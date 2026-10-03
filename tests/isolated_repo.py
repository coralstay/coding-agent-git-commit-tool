"""격리된 임시 git 저장소 헬퍼(GF-124). 기존 tests/helpers/git-format.bash 대체.

이 저장소의 테스트는 훅을 import하지 않는다 — 임시 저장소에서 실제 `git commit`을
태워 훅을 서브프로세스로 실행하고 종료 코드·출력·커밋 메시지만 본다(블랙박스).
bats 판과 같은 방식이며, 달라진 것은 프레임워크뿐이다.

제공하는 것:
  * IsolatedRepoTestCase — 테스트마다 훅이 연결된 임시 저장소를 새로 만든다.
    저장소·섀도 PATH·훅 사본 같은 임시 자원은 전부 addCleanup으로 정리되므로
    테스트끼리 상태를 공유하지 않고 어떤 순서로도 돌 수 있다.
  * 자식 프로세스 환경 조립(child_env) — 러너 자신의 환경은 건드리지 않는다.
  * path_without() — 특정 실행파일 하나만 없는 PATH를 만든다.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

GITFORMAT_ROOT = Path(__file__).resolve().parent.parent
HOOKS_DIR = GITFORMAT_ROOT / "hooks"
CONF_FILE = HOOKS_DIR / "gitformat.conf"
INSTALL_SH = GITFORMAT_ROOT / "install.sh"
GITMESSAGE = GITFORMAT_ROOT / ".gitmessage"

USER_NAME = "gitformat-tests"
USER_EMAIL = "tests@example.com"
SIGNED_OFF_BY = f"{USER_NAME} <{USER_EMAIL}>"

CONF_GUARD_MESSAGE = "gitformat: gitformat.conf를 읽을 수 없습니다"
BROKEN_CONF = "this is not valid git-config syntax [[[\n"

# 자식 프로세스 환경에서 항상 지우는 변수.
#
# AI_AGENT/CLAUDE_CODE_SESSION_ID: 이 스위트를 Claude Code로 돌리면 셸 환경에 이미
# 노출돼 있어(GF-97 검증 중 실제로 발견) "사람 커밋" 시나리오가 조용히 AI 커밋이
# 된다. bats 판은 그 케이스에서만 `env -u`로 지웠지만, 여기서는 기본값으로 지워
# 모든 테스트가 실행 환경과 무관하게 같은 결과를 내게 한다 — AI 경로를 검증하는
# 테스트는 필요한 값을 명시적으로 넘긴다.
# _GITFORMAT_AMEND_GUARD: 값이 새어들어오면 post-commit이 즉시 빠져나가 트레일러가
# 하나도 붙지 않는다.
# GIT_*: 러너가 훅/래퍼 안에서 실행될 때 새어들어오면 임시 저장소가 아니라 이
# 저장소의 인덱스를 건드린다.
_STRIPPED_ENV = (
    "AI_AGENT",
    "CLAUDE_CODE_SESSION_ID",
    "_GITFORMAT_AMEND_GUARD",
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_COMMON_DIR",
    "GIT_PREFIX",
    "GIT_AUTHOR_DATE",
    "GIT_COMMITTER_DATE",
)

_ASDF_PIN = None


def asdf_pins():
    """asdf로 런타임을 관리하는 로컬 환경에서 셈이 버전을 찾게 하는 환경변수.

    훅이 Python이 된 뒤(GF-108/GF-109), HOME을 가짜 경로로 바꾸는 테스트들은 셈이
    .tool-versions를 못 찾아 훅이 아예 실행되지 않는다(훅과 무관한 로컬 환경 이슈).
    asdf가 없는 환경(CI 등)에서는 빈 dict를 돌려주므로 아무 영향이 없다.

    "system"을 쓰면 안 된다 — path_without()이 만드는 섀도 PATH의 python3는 asdf
    셈을 가리키는 심볼릭 링크라, "셈이 아닌 python3를 찾아라"라는 뜻의 system이 그
    링크를 다시 집어 무한 재귀로 멈춘다(실측 확인). 그래서 지금 해석된 구체 버전을
    고정한다. 버전 해석 자체가 진짜 HOME 아래의 .tool-versions를 읽으므로, 가짜
    HOME을 덮어쓰기 *전에* 계산해야 한다 — 모듈 수준에서 한 번 계산해 캐시한다.
    """
    global _ASDF_PIN
    if _ASDF_PIN is None:
        _ASDF_PIN = {}
        if shutil.which("asdf"):
            # asdf 자체가 없는 환경에서는 조용히 넘어간다.
            result = subprocess.run(
                ["asdf", "current", "python"],
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            lines = result.stdout.splitlines()
            fields = lines[1].split() if len(lines) > 1 else []
            if len(fields) > 1:
                _ASDF_PIN["ASDF_PYTHON_VERSION"] = fields[1]
            # node는 버전 해석 없이 lts로 충분하다(ts 체크가 npm/npx/tsc를 쓴다).
            _ASDF_PIN["ASDF_NODEJS_VERSION"] = "lts"
    return dict(_ASDF_PIN)


def transcript_slug(path):
    """Claude Code가 ~/.claude/projects/ 아래 세션 디렉터리에 쓰는 실제 슬러그 규칙.

    "영숫자가 아닌 모든 문자를 하이픈으로 치환"이다(GF-98). 훅의 계산을 그대로
    베끼지 않고 이 규칙을 독립적으로 구현해 둔다 — bats 판이 한때 훅과 똑같이
    잘못 계산해(둘 다 `/`만 치환) 우연히 일치하며 버그를 놓쳤다.
    """
    return re.sub(r"[^A-Za-z0-9]", "-", str(path))


def path_without(tool):
    """`tool` 하나만 찾을 수 없는 PATH 값을 만들어 그 디렉터리 경로를 돌려준다.

    "도구가 없으면 어떻게 되나" 시나리오에서 PATH="/usr/bin:/bin"처럼 하드코딩하면
    플랫폼마다 도구 설치 위치가 달라 깨진다(GF-32에서 실측: macOS/Homebrew는
    /opt/homebrew/bin이지만 ubuntu-latest는 같은 도구가 /usr/bin에 있었다 — 당시
    대상은 GF-135에서 제거된 언어별 검사 도구였고, 지금 남은 대상은 python3다).
    그 도구가 있는 디렉터리만 PATH에서 빼는 방법도 안 된다 — git도 같은 디렉터리에
    있어 git 자체가 사라진다.

    그래서 PATH에서 찾을 수 있는 모든 실행파일을 지정한 도구 하나만 빼고 임시
    디렉터리에 심볼릭 링크로 모은다. git/sh/grep 등은 전부 정상 동작하면서 그
    도구만 정확히 못 찾게 된다.
    """
    shadow = Path(tempfile.mkdtemp(prefix="gitformat-shadow-"))
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        if not directory or not os.path.isdir(directory):
            continue
        try:
            entries = list(os.scandir(directory))
        except OSError:
            continue
        for entry in entries:
            if entry.name == tool:
                continue
            link = shadow / entry.name
            if link.exists() or link.is_symlink():
                continue
            try:
                if not os.access(entry.path, os.X_OK):
                    continue
                link.symlink_to(entry.path)
            except OSError:
                continue
    return shadow


class Result:
    """서브프로세스 실행 결과. bats의 $status/$output에 대응한다."""

    def __init__(self, argv, returncode, stdout, stderr):
        self.argv = argv
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    @property
    def output(self):
        """bats의 $output과 같게 stdout과 stderr를 합친 것."""
        return self.stdout + self.stderr

    def __str__(self):
        return f"$ {' '.join(self.argv)}\n[exit {self.returncode}]\n{self.output}"


class IsolatedRepoTestCase(unittest.TestCase):
    """훅이 연결된 임시 git 저장소 하나를 갖는 테스트 케이스."""

    def setUp(self):
        self.repo = self.make_repo()

    # ── 임시 자원 ────────────────────────────────────────────────

    def temp_dir(self, prefix="gitformat-test-"):
        path = Path(tempfile.mkdtemp(prefix=prefix))
        # macOS의 /var는 /private/var 심볼릭 링크라, 해석하지 않으면 훅이 계산하는
        # 물리 경로와 테스트가 계산하는 경로가 갈려 트랜스크립트 슬러그가 어긋난다.
        path = path.resolve()
        self.addCleanup(shutil.rmtree, path, ignore_errors=True)
        return path

    def make_repo(self, *, hooks_path=HOOKS_DIR, path=None, env=None):
        """임시 git 저장소를 만들고 이 클론의 훅을 연결한다."""
        repo = self.temp_dir() if path is None else Path(path)
        repo.mkdir(parents=True, exist_ok=True)
        self.run_cmd_ok(["git", "init", "-q"], cwd=repo, env=env)
        # 서명은 끄고(에이전트 없는 환경에서 멈추지 않게) 커미터는 고정한다 —
        # Signed-off-by 단언이 이 값을 본다.
        self.run_cmd_ok(["git", "config", "commit.gpgsign", "false"], cwd=repo, env=env)
        self.run_cmd_ok(["git", "config", "user.email", USER_EMAIL], cwd=repo, env=env)
        self.run_cmd_ok(["git", "config", "user.name", USER_NAME], cwd=repo, env=env)
        if hooks_path is not None:
            self.run_cmd_ok(
                ["git", "config", "core.hooksPath", str(hooks_path)], cwd=repo, env=env
            )
        return repo

    def copy_hooks(self, *omit):
        """hooks/ 사본을 임시 디렉터리에 만들고 지정한 파일을 지운다.

        진짜 저장소의 hooks/는 절대 건드리지 않는다. git은 앞선 훅이 실패하면 뒤의
        훅을 아예 실행하지 않으므로, 특정 훅만 검증 대상으로 만들려면 앞의 훅을
        사본에서 지워야 한다.
        """
        copy = self.temp_dir(prefix="gitformat-hooks-")
        shutil.copytree(HOOKS_DIR, copy, dirs_exist_ok=True)
        for name in omit:
            (copy / name).unlink(missing_ok=True)
        return copy

    def break_conf(self, hooks_copy):
        (Path(hooks_copy) / "gitformat.conf").write_text(BROKEN_CONF, encoding="utf-8")

    def path_without(self, tool):
        shadow = path_without(tool)
        self.addCleanup(shutil.rmtree, shadow, ignore_errors=True)
        self.assertFalse(
            (shadow / tool).exists(),
            f"섀도 PATH에 {tool}이 남아 있으면 이 테스트는 아무것도 검증하지 못한다",
        )
        # 섀도 PATH가 그 도구만 정확히 가렸는지 고정한다. 이 단언이 없으면 PATH가
        # 통째로 망가져 git 자체가 죽는 경우에도 테스트가 똑같이 통과한다.
        probe = self.run_cmd(["git", "--version"], env={"PATH": str(shadow)})
        self.assertEqual(0, probe.returncode, str(probe))
        return shadow

    def fake_home(self):
        return self.temp_dir(prefix="gitformat-home-")

    def empty_global_config(self):
        """child_env가 GIT_CONFIG_GLOBAL로 넘길 빈 설정 파일.

        setUp을 재정의하고 super()를 부르지 않는 하위 클래스가 있으므로 초기화에
        의존하지 않고 getattr로 지연 생성한다.
        """
        path = getattr(self, "_empty_global_config", None)
        if path is None:
            path = self.temp_dir(prefix="gitformat-gitconfig-") / "gitconfig"
            path.write_text("", encoding="utf-8")
            self._empty_global_config = path
        return path

    # ── 자식 프로세스 실행 ───────────────────────────────────────

    def child_env(self, cwd, overrides):
        """자식 프로세스에 넘길 환경변수. 러너 자신의 os.environ은 바꾸지 않는다."""
        env = {k: v for k, v in os.environ.items() if k not in _STRIPPED_ENV}
        env.update(asdf_pins())
        # 시스템 git config는 항상 차단한다 - 기계마다 다른 값이 테스트 결과를 바꾼다.
        env["GIT_CONFIG_SYSTEM"] = os.devnull
        # 훅의 shell_pwd()는 POSIX 셸과 같이 환경변수 PWD가 현재 디렉터리를 가리킬
        # 때 그 값을 쓴다. 셸을 거치지 않고 실행하면 PWD가 러너의 것으로 남으므로
        # 명시적으로 맞춰준다.
        env["PWD"] = str(cwd)
        for key, value in (overrides or {}).items():
            if value is None:
                env.pop(key, None)
            else:
                env[key] = str(value)
        # 실행하는 사람의 전역 git config(~/.gitconfig)가 격리 저장소로 새어 들어오지
        # 않게 빈 파일로 돌린다. 이게 없으면 결과가 러너 환경에 따라 달라진다 - 실제로
        # 개발 기계에는 install.sh --global이 심은 commit.template이 있어서 에디터
        # 커밋이 source=template으로 왔는데, 그 설정이 없는 CI에서는 git이 source
        # 인자를 아예 넘기지 않아 훅의 에디터 거부가 통과해버렸다(GF-125).
        #
        # HOME은 바꾸지 않는다 - 원래 이유는 CI가 pip install로 언어별 검사 도구를
        # 실제 HOME 아래 사용자 site-packages에 깔았기 때문인데, 그 검사는 GF-135에서
        # 사라졌다. 그래도 그대로 둔다 - 러너 환경을 필요 없이 바꾸지 않는다.
        #
        # HOME을 명시적으로 넘긴 테스트는 건드리지 않는다. install.sh --global은
        # 가짜 HOME의 .gitconfig에 쓰고 테스트가 그 파일을 읽어 확인하므로,
        # GIT_CONFIG_GLOBAL을 씌우면 그 경로가 어긋난다(GIT_CONFIG_GLOBAL이 HOME보다
        # 우선한다).
        if "HOME" not in (overrides or {}):
            env["GIT_CONFIG_GLOBAL"] = str(self.empty_global_config())
        return env

    def run_cmd(self, argv, *, cwd=None, env=None, timeout=None, stdin=None):
        argv = [str(a) for a in argv]
        cwd = Path(cwd) if cwd is not None else self.repo
        completed = subprocess.run(
            argv,
            cwd=str(cwd),
            env=self.child_env(cwd, env),
            capture_output=True,
            input=stdin,
            timeout=timeout,
            check=False,
        )
        # 출력은 항상 바이트로 받아 UTF-8로 디코드한다 — 로케일을 깨뜨린 채 훅을
        # 돌리는 테스트(GF-116)도 훅이 출력 인코딩을 UTF-8로 고정하므로 이게 맞다.
        return Result(
            argv,
            completed.returncode,
            completed.stdout.decode("utf-8", errors="replace"),
            completed.stderr.decode("utf-8", errors="replace"),
        )

    def run_cmd_ok(self, argv, **kwargs):
        result = self.run_cmd(argv, **kwargs)
        self.assertEqual(0, result.returncode, str(result))
        return result

    def git(self, *args, **kwargs):
        return self.run_cmd(["git", *args], **kwargs)

    def git_ok(self, *args, **kwargs):
        """테스트 준비 단계의 git 호출. 실패하면 즉시 드러나야 한다."""
        return self.run_cmd_ok(["git", *args], **kwargs)

    def python(self, script, *args, **kwargs):
        """훅/체크 스크립트를 직접 실행한다. 러너와 같은 python3를 쓴다."""
        return self.run_cmd([sys.executable, str(script), *args], **kwargs)

    # ── 저장소 조작 ──────────────────────────────────────────────

    def write(self, relpath, content, *, cwd=None):
        target = (Path(cwd) if cwd is not None else self.repo) / relpath
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def commit(self, message, *extra_args, **kwargs):
        return self.git("commit", *extra_args, "-m", message, **kwargs)

    def commit_ok(self, message, *extra_args, **kwargs):
        result = self.commit(message, *extra_args, **kwargs)
        self.assertEqual(0, result.returncode, str(result))
        return result

    def head_message(self, **kwargs):
        return self.git_ok("log", "-1", "--pretty=%B", **kwargs).stdout.rstrip("\n")

    def head_subject(self, **kwargs):
        return self.git_ok("log", "-1", "--pretty=%s", **kwargs).stdout.rstrip("\n")

    def head_hash(self, **kwargs):
        return self.git_ok("rev-parse", "HEAD", **kwargs).stdout.strip()

    def commit_count(self, **kwargs):
        return int(self.git_ok("rev-list", "--count", "HEAD", **kwargs).stdout.strip())

    def git_dir_file(self, name, *, cwd=None):
        return (Path(cwd) if cwd is not None else self.repo) / ".git" / name

    def write_transcript(self, home, records, *, session_id="fake-session", cwd=None):
        """가짜 HOME 아래에 Claude Code 세션 트랜스크립트(JSONL)를 만든다.

        records의 문자열은 그대로(깨진 JSON 재현용), dict는 json.dumps해서 쓴다.
        """
        repo_path = Path(cwd) if cwd is not None else self.repo
        directory = Path(home) / ".claude" / "projects" / transcript_slug(repo_path)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{session_id}.jsonl"
        lines = [r if isinstance(r, str) else json.dumps(r) for r in records]
        with path.open("a", encoding="utf-8") as handle:
            for line in lines:
                handle.write(line + "\n")
        return path

    def write_subagent_transcript(
        self, home, records, *, agent="agent-1", session_id="fake-session", cwd=None
    ):
        """서브에이전트 트랜스크립트(<세션 디렉터리>/<세션 ID>/subagents/<agent>.jsonl).

        Claude Code는 서브에이전트의 대화를 부모 세션 트랜스크립트 옆 이 경로에 같은
        JSONL 형식으로 남긴다(GF-129). 형식 규칙은 write_transcript와 같다.
        """
        repo_path = Path(cwd) if cwd is not None else self.repo
        directory = (
            Path(home)
            / ".claude"
            / "projects"
            / transcript_slug(repo_path)
            / session_id
            / "subagents"
        )
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{agent}.jsonl"
        lines = [r if isinstance(r, str) else json.dumps(r) for r in records]
        with path.open("a", encoding="utf-8") as handle:
            for line in lines:
                handle.write(line + "\n")
        return path

    def claude_env(self, home, *, session_id="fake-session", version="2-1-0"):
        return {
            "HOME": str(home),
            "AI_AGENT": f"claude-code_{version}",
            "CLAUDE_CODE_SESSION_ID": session_id,
        }

    # ── 단언 ─────────────────────────────────────────────────────

    def assertAccepted(self, result):
        self.assertEqual(0, result.returncode, str(result))

    def assertRejected(self, result):
        self.assertNotEqual(0, result.returncode, str(result))

    def assertTrailerCount(self, message, trailer, expected=1):
        """트레일러가 정확히 몇 번 들어 있는지 본다.

        부분 일치(`in`)로만 보면 같은 트레일러가 두 번 붙는 회귀(GF-33류)를 놓친다.
        """
        self.assertEqual(
            expected,
            message.count(trailer),
            f"'{trailer}'가 {expected}번이어야 하는데 "
            f"{message.count(trailer)}번이다:\n{message}",
        )

    def assertTrailerKeyAbsent(self, message, key):
        self.assertEqual(0, message.count(f"{key}:"), f"{key}가 붙었다:\n{message}")
