"""install.sh의 공통 분기를 본다(구 robustness-install.bats).

GF-26, decision-8: 표준 인증이 아니라 install.sh의 실제 분기(비대화형/에러 처리)에
근거한 실용적 테스트. 실제 전역 git 설정(~/.gitconfig)은 절대 건드리지 않고
HOME을 매 테스트마다 임시 디렉터리로 격리한다 — 격리는 자식 환경에만 적용되므로 러너
자신의 HOME은 그대로다. --global(init.templateDir)과 template/ 동기화 케이스는
GF-148(decision-32)에서 그 기능과 함께 사라졌고, .githooks 설치 자체는
test_install_githooks.py가 본다.
"""

import shutil
import unittest

from isolated_repo import (
    GITFORMAT_ROOT,
    GITHOOKS_TEMPLATE,
    GITMESSAGE,
    HOOKS_DIR,
    INSTALL_SH,
    IsolatedRepoTestCase,
)


class InstallScriptTest(IsolatedRepoTestCase):
    def setUp(self):
        # 커밋을 만들지 않으므로 커미터 설정도 훅 연결도 필요 없다 - 빈 저장소면 된다.
        self.repo = self.temp_dir(prefix="gitformat-target-")
        self.run_cmd_ok(["git", "init", "-q"], cwd=self.repo)

    def fake_root(self):
        """install.sh와 hooks/·githooks/만 들어 있는 coding-agent-git-commit-tool 클론 사본.

        실제 hooks/ 파일을 지우는 테스트는 이 저장소 자신이 아니라 이 사본에서 한다.
        """
        root = self.temp_dir(prefix="gitformat-root-")
        shutil.copytree(HOOKS_DIR, root / "hooks")
        shutil.copytree(GITHOOKS_TEMPLATE, root / "githooks")
        (root / "install.sh").write_bytes(INSTALL_SH.read_bytes())
        shutil.copymode(INSTALL_SH, root / "install.sh")
        (root / ".gitmessage").write_bytes(GITMESSAGE.read_bytes())
        return root

    def git_config_file(self, path, key):
        return self.run_cmd(
            ["git", "config", "--file", path, "--get", key]
        )

    # ── 비대화형 환경 ───────────────────────────────────────────────

    def test_비대화형에서도_프롬프트_없이_설치된다(self):
        """[비대화형] stdin이 tty가 아니어도 묻지 않고 .githooks 설치를 끝낸다"""
        # GF-148(decision-32) 전에는 여기서 전역(init.templateDir) 설정을 물었고,
        # 비대화형이면 건너뛰었다. 전역 설치가 없어져 묻는 것 자체가 없다.
        home = self.fake_home()
        result = self.run_cmd(
            [INSTALL_SH, self.repo], env={"HOME": str(home)}, stdin=b""
        )
        self.assertAccepted(result)
        self.assertEqual(
            ".githooks",
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

    def test_no_global은_호환용으로_받아_준다(self):
        """[호환] 예전 스크립트가 넘기던 --no-global은 오류 없이 무시한다"""
        home = self.fake_home()
        self.assertAccepted(
            self.run_cmd(
                [INSTALL_SH, "--no-global", self.repo],
                env={"HOME": str(home)},
                stdin=b"",
            )
        )

    # ── 회귀: 테스트가 이 저장소 자신의 설정을 오염시키지 않는다 ─────

    def test_설치가_이_저장소의_hooksPath를_바꾸지_않는다(self):
        """[GF-123 회귀] 다른 클론 사본의 설치가 이 저장소 자신의 core.hooksPath를 바꾸지 않는다"""
        # 타깃 인자를 생략하면 install.sh의 기본 타깃인 CWD(=이 저장소)에 설치가
        # 일어난다. 예전에는 그 결과 이 저장소의 core.hooksPath가 곧 삭제될 임시
        # 경로를 가리켜 이후 모든 커밋에서 훅이 조용히 실행되지 않았다.
        home = self.fake_home()
        root = self.fake_root()

        before = self.git(
            "-C", GITFORMAT_ROOT, "config", "--get", "core.hooksPath"
        ).stdout
        self.run_cmd_ok(
            [root / "install.sh", self.repo], env={"HOME": str(home)}, stdin=b""
        )
        after = self.git(
            "-C", GITFORMAT_ROOT, "config", "--get", "core.hooksPath"
        ).stdout
        self.assertEqual(before, after)

        # 타깃 쪽에는 정상적으로 설치됐어야 한다(설치 자체가 안 된 것으로 통과하면 안 된다).
        self.assertEqual(
            ".githooks",
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
