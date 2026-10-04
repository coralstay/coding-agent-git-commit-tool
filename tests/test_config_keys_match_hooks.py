"""값은 같아야 하지만 로직/문서는 공유하지 않는 항목들이 실제로 일치하는지 본다.

구 consistency.bats. 런타임 결합 없이 테스트로만 drift를 잡는다는 게 이 프로젝트의
설계 원칙이다(decision-8).

bats 판은 "훅이 참조하는 키 목록"을 손으로 나열해 두고 대조했다 — 목록 자체가 drift의
원천이었다(실제로 GF-83에서 들어온 gitformat.subjectMaxLength/bodyLineMaxLength가
끝까지 목록에 추가되지 않았다). 여기서는 훅 소스에서 conf 읽기 호출을 직접 뽑아내고,
설정 파일도 `--get-regexp`로 동적으로 읽어 대조한다(GF-124 AC #6).
"""

import re
import subprocess
import unittest

from isolated_repo import CONF_FILE, GITFORMAT_ROOT, HOOKS_DIR

GITMESSAGE = GITFORMAT_ROOT / ".gitmessage"

# gitformat.conf를 키 단위로 읽는 파일들. install.sh는 `--list`로 읽기 가능 여부만
# 보고 개별 키는 읽지 않으므로 여기 없다. post-commit은 GF-128에서 삭제됐다.
CONF_READERS = (HOOKS_DIR / "prepare-commit-msg",)

# 훅이 실제로 쓰는 conf 읽기 형태를 그대로 뽑는다: conf_get("...") /
# conf_get_all("...") 헬퍼 호출이다. GF-135까지는 `--file CONF ... --get`를 인라인으로
# 쓰는 두 번째 형태도 뽑았는데, 그 형태를 쓰던 파일은 checks/cpp.py와 checks/sql.py
# 뿐이라 checks/가 삭제되며 함께 사라졌다. 훅이 다시 인라인 형태를 쓰기 시작하면 아래
# "한 파일에서 아무 키도 못 뽑았다" 단언이 그 사실을 소리 내어 알려준다.
CONF_GET_HELPER_RE = re.compile(r'conf_get(?:_all)?\(\s*"(gitformat\.[^"]+)"')


def git_config_conf(*args):
    return subprocess.run(
        ["git", "config", "--file", str(CONF_FILE), *args],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    ).stdout


def conf_keys_referenced_by(path):
    source = path.read_text(encoding="utf-8")
    return set(CONF_GET_HELPER_RE.findall(source))


class ConfigKeysMatchHooksTest(unittest.TestCase):
    def test_커밋_타입_목록이_gitmessage와_일치한다(self):
        """gitformat.conf의 커밋 타입 목록과 .gitmessage에 적힌 타입 목록이 일치한다 (GF-68)"""
        conf_types = sorted(git_config_conf("--get-all", "gitformat.type").split())

        message_types = []
        collecting = False
        for line in GITMESSAGE.read_text(encoding="utf-8").splitlines():
            if "type 목록" in line:
                collecting = True
                continue
            if "subsystem (선택)" in line:
                break
            if collecting and re.match(r"^#   [a-z]+", line):
                message_types.append(line.split()[1])
        message_types.sort()

        self.assertTrue(conf_types, "gitformat.conf에서 타입 목록을 읽지 못했다")
        self.assertTrue(message_types, ".gitmessage에서 타입 목록을 읽지 못했다")
        self.assertEqual(conf_types, message_types)

    def test_훅이_참조하는_conf_키가_전부_존재하고_값이_있다(self):
        """gitformat.conf에 각 훅이 참조하는 키가 전부 존재하고 값이 비어있지 않다 (GF-61)"""
        referenced = {}
        for path in CONF_READERS:
            keys = conf_keys_referenced_by(path)
            # 한 파일에서 아무 키도 못 뽑았다면 추출 정규식이 코드 형태 변화를
            # 따라가지 못한 것이다 — 검사가 아무것도 안 하고 통과하는 것(GF-32
            # 유형)을 막기 위해 조용히 넘기지 않는다.
            self.assertTrue(keys, f"{path.name}에서 conf 읽기 호출을 뽑지 못했다")
            for key in keys:
                referenced.setdefault(key, []).append(path.name)

        for key, sources in sorted(referenced.items()):
            value = git_config_conf("--get-all", key).strip()
            self.assertTrue(
                value, f"누락되거나 빈 값: {key} (참조: {', '.join(sources)})"
            )

        # 트레일러 키는 섹션 전체를 동적으로 읽어 대조한다. prepare-commit-msg는 본문 줄
        # 길이 예외 판정에 이 섹션을 통째로(--get-regexp) 쓰므로, 이름으로 참조되지
        # 않는 키(예: trailer.breakingChange)도 실제로 쓰인다 — 그래서 "훅이 이름으로
        # 참조하는 트레일러 키 ⊆ 섹션"만 요구하고, 섹션의 모든 값이 비어있지 않은지는
        # 따로 본다.
        # git은 --get-regexp 출력의 변수명을 소문자로 정규화한다(변수명은
        # 대소문자를 구분하지 않는다) — 양쪽을 소문자로 맞춰 비교한다.
        section = {}
        for line in git_config_conf(
            "--get-regexp", r"^gitformat\.trailer\."
        ).splitlines():
            key, _, value = line.partition(" ")
            section[key.lower()] = value
        self.assertTrue(section, "gitformat.conf에서 트레일러 섹션을 읽지 못했다")
        for key, value in sorted(section.items()):
            self.assertTrue(value.strip(), f"트레일러 키에 값이 없다: {key}")

        referenced_trailers = {
            key.lower() for key in referenced if key.startswith("gitformat.trailer.")
        }
        self.assertTrue(referenced_trailers, "트레일러 키 참조를 하나도 못 뽑았다")
        self.assertEqual(
            set(),
            referenced_trailers - set(section),
            "훅이 참조하는데 gitformat.conf의 트레일러 섹션에 없는 키가 있다",
        )


if __name__ == "__main__":
    unittest.main()
