"""install.sh와 template/ 이식성을 본다(구 robustness-install.bats).

GF-26, decision-8: 표준 인증이 아니라 install.sh의 실제 분기(비대화형/--global/에러
처리)에 근거한 실용적 테스트. 실제 전역 git 설정(~/.gitconfig)은 절대 건드리지 않고
HOME을 매 테스트마다 임시 디렉터리로 격리한다 — 격리는 자식 환경에만 적용되므로 러너
자신의 HOME은 그대로다.
"""

import shutil
import unittest

from isolated_repo import (
    GITFORMAT_ROOT,
    GITMESSAGE,
    HOOKS_DIR,
    INSTALL_SH,
    IsolatedRepoTestCase,
)

TEMPLATE_DIR = GITFORMAT_ROOT / "template"


class InstallScriptTest(IsolatedRepoTestCase):
    def setUp(self):
        # 커밋을 만들지 않으므로 커미터 설정도 훅 연결도 필요 없다 - 빈 저장소면 된다.
        self.repo = self.temp_dir(prefix="gitformat-target-")
        self.run_cmd_ok(["git", "init", "-q"], cwd=self.repo)

    def fake_root(self):
        """install.sh와 hooks/만 들어 있는 coding-agent-git-commit-tool 클론 사본.

        실제 hooks/ 파일을 지우는 테스트는 이 저장소 자신이 아니라 이 사본에서 한다.
        """
        root = self.temp_dir(prefix="gitformat-root-")
        shutil.copytree(HOOKS_DIR, root / "hooks")
        (root / "install.sh").write_bytes(INSTALL_SH.read_bytes())
        shutil.copymode(INSTALL_SH, root / "install.sh")
        (root / ".gitmessage").write_bytes(GITMESSAGE.read_bytes())
        return root

    def git_config_file(self, path, key):
        return self.run_cmd(
            ["git", "config", "--file", path, "--get", key]
        )

    # ── 비대화형 환경 ───────────────────────────────────────────────

    def test_비대화형이면_전역_설정을_건너뛴다(self):
        """[비대화형] stdin이 tty가 아니면 프롬프트 없이 로컬 설정만 적용하고 전역은 건너뛴다"""
        home = self.fake_home()
        # stdin을 닫은 파이프로 넘겨 `[ -t 0 ]`이 거짓이 되게 한다(</dev/null과 동등).
        result = self.run_cmd(
            [INSTALL_SH, self.repo], env={"HOME": str(home)}, stdin=b""
        )
        self.assertAccepted(result)
        self.assertIn("비대화형 환경이라 전역 설정은 건너뜁니다", result.output)

        # 로컬 설정은 정상 적용됐어야 한다.
        self.assertEqual(
            str(HOOKS_DIR),
            self.git_ok("-C", self.repo, "config", "--get", "core.hooksPath").stdout.strip(),
        )
        self.assertEqual(
            str(GITMESSAGE),
            self.git_ok(
                "-C", self.repo, "config", "--get", "commit.template"
            ).stdout.strip(),
        )

        # 전역(가짜 HOME) 설정은 안 건드렸어야 한다.
        self.assertRejected(
            self.git_config_file(home / ".gitconfig", "init.templateDir")
        )

    # ── 멱등성: --global 반복 실행 ───────────────────────────────────

    def test_global을_두_번_실행해도_심볼릭_링크가_유지된다(self):
        """[멱등성] --global을 격리된 HOME에서 두 번 연속 실행해도 template/hooks 심볼릭 링크가 정상 유지된다"""
        home = self.fake_home()
        env = {"HOME": str(home)}
        # --global은 전역 설정만 하는 플래그가 아니다 - install.sh는 타깃(기본값 CWD)에
        # 대한 로컬 설치도 함께 수행한다. 타깃을 생략하면 이 저장소 자신이 대상이
        # 되므로 반드시 격리된 타깃을 넘긴다(GF-123).
        self.run_cmd_ok([INSTALL_SH, "--global", self.repo], env=env)
        first = (TEMPLATE_DIR / "hooks" / "prepare-commit-msg").readlink()

        self.run_cmd_ok([INSTALL_SH, "--global", self.repo], env=env)
        second = (TEMPLATE_DIR / "hooks" / "prepare-commit-msg").readlink()

        self.assertEqual(first, second)
        self.assertEqual(HOOKS_DIR / "prepare-commit-msg", first)
        self.assertTrue((TEMPLATE_DIR / "hooks" / "post-commit").is_symlink())
        # GF-127에서 삭제된 훅의 링크는 남지 않는다.
        self.assertFalse((TEMPLATE_DIR / "hooks" / "commit-msg").is_symlink())

        # 실제 전역 git 설정이 아니라 가짜 HOME 쪽에 반영됐는지를 직접 확인한다.
        self.assertEqual(
            str(TEMPLATE_DIR),
            self.git_config_file(home / ".gitconfig", "init.templateDir").stdout.strip(),
        )

    # ── 정리: 삭제된 훅의 template/hooks 심볼릭 링크 정리 (GF-92) ────

    def test_삭제된_훅의_심볼릭_링크도_정리된다(self):
        """[정리] hooks/에서 파일이 삭제된 뒤 --global을 재실행하면 template/hooks의 대응 심볼릭 링크도 삭제된다"""
        # GF-86(decision-12)에서 hooks/pre-push를 삭제했지만 template/hooks/pre-push
        # 심볼릭 링크는 지워지지 않고 대상 없는 채로 남았다(sync_template()이 새로
        # 생기는 파일만 링크하고, 없어진 파일의 예전 링크는 정리하지 않았기 때문).
        home = self.fake_home()
        env = {"HOME": str(home)}
        root = self.fake_root()

        self.run_cmd_ok([root / "install.sh", "--global", self.repo], env=env)
        self.assertTrue(
            (root / "template" / "hooks" / "prepare-commit-msg").is_symlink()
        )
        self.assertTrue((root / "template" / "hooks" / "post-commit").is_symlink())

        # hooks/에서 파일 하나를 지운다 (GF-86의 hooks/pre-push 삭제 상황 재현).
        (root / "hooks" / "prepare-commit-msg").unlink()

        self.run_cmd_ok([root / "install.sh", "--global", self.repo], env=env)

        # 삭제된 파일의 심볼릭 링크는 사라져야 한다(깨진 링크로도 남으면 안 된다).
        stale = root / "template" / "hooks" / "prepare-commit-msg"
        self.assertFalse(stale.exists())
        self.assertFalse(stale.is_symlink())

        # 여전히 존재하는 훅의 심볼릭 링크는 그대로 유지된다.
        self.assertTrue((root / "template" / "hooks" / "post-commit").is_symlink())
        self.assertTrue((root / "template" / "hooks" / "gitformat.conf").is_symlink())

    # ── 회귀: 테스트가 이 저장소 자신의 설정을 오염시키지 않는다 ─────

    def test_global_실행이_이_저장소의_hooksPath를_바꾸지_않는다(self):
        """[GF-123 회귀] --global 실행이 이 저장소 자신의 core.hooksPath를 바꾸지 않는다"""
        # --global 케이스들이 타깃 인자를 생략해, install.sh의 기본 타깃인 CWD(=이
        # 저장소)에 로컬 설치가 함께 일어났다. 그 결과 스위트를 한 번 돌릴 때마다 이
        # 저장소의 core.hooksPath가 곧 삭제될 임시 경로를 가리키게 되고, 이후 모든
        # 커밋에서 훅이 조용히 실행되지 않았다(에러 없이 트레일러만 사라짐).
        home = self.fake_home()
        root = self.fake_root()

        before = self.git(
            "-C", GITFORMAT_ROOT, "config", "--get", "core.hooksPath"
        ).stdout
        self.run_cmd_ok(
            [root / "install.sh", "--global", self.repo], env={"HOME": str(home)}
        )
        after = self.git(
            "-C", GITFORMAT_ROOT, "config", "--get", "core.hooksPath"
        ).stdout
        self.assertEqual(before, after)

        # 타깃 쪽에는 정상적으로 설치됐어야 한다(설치 자체가 안 된 것으로 통과하면 안 된다).
        self.assertEqual(
            str(root / "hooks"),
            self.git_ok(
                "-C", self.repo, "config", "--get", "core.hooksPath"
            ).stdout.strip(),
        )

    # ── 필요조건: python3 부재 (GF-113, decision-16) ─────────────────

    def test_python3이_없으면_설치를_막는다(self):
        """[필요조건] PATH에 python3이 없으면 install.sh가 명확한 에러로 설치를 막는다"""
        # 이 가드는 설치 시점만 본다 - 훅이 실제로 실행되는 시점의 PATH는 보장하지
        # 못하고, 그쪽 동작은 test_python3_missing.py가 따로 검증한다(GF-107).
        shadow = self.path_without("python3")
        result = self.run_cmd(
            [INSTALL_SH, self.repo], env={"PATH": str(shadow)}, stdin=b""
        )
        self.assertRejected(result)
        self.assertIn("python3을 찾을 수 없습니다", result.output)

        # 가드가 설정보다 먼저 걸렸어야 한다 - 에러만 찍고 설치는 다 해버리면 안 된다.
        self.assertRejected(
            self.git("-C", self.repo, "config", "--get", "core.hooksPath")
        )

    # ── 에러 메시지: 잘못된 인자 ────────────────────────────────────

    def test_존재하지_않는_대상_디렉터리는_실패한다(self):
        """[에러처리] 존재하지 않는 대상 디렉터리는 0이 아닌 상태로 실패한다"""
        missing = self.repo / "no-such-gitformat-target-dir"
        result = self.run_cmd([INSTALL_SH, missing], stdin=b"")
        self.assertRejected(result)
        self.assertNotEqual("", result.output.strip(), "에러 출력이 비어 있다")

    def test_git_저장소가_아니면_명확한_에러로_실패한다(self):
        """[에러처리] git 저장소가 아닌 디렉터리는 명확한 에러 메시지와 함께 실패한다"""
        not_a_repo = self.temp_dir(prefix="gitformat-plain-")
        result = self.run_cmd([INSTALL_SH, not_a_repo], stdin=b"")
        self.assertRejected(result)
        self.assertIn("git 저장소가 아닙니다", result.output)


if __name__ == "__main__":
    unittest.main()
