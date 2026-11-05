# GF-148: install이 대상 저장소에 .githooks를 만들고 core.hooksPath=.githooks를 설정
"""install.sh(= git-commit-tool)의 .githooks 설치를 본다(decision-32).

설치는 대상 저장소에 githooks/ 템플릿(디스패처 + 기본 플러그인)을 .githooks/로 복사하고
`core.hooksPath=.githooks`를 설정한다. 이미 다른 hooksPath가 있거나 .git/hooks/에 링크가
아닌 훅이 있으면 아무것도 쓰지 않고 멈춘다 — hooksPath를 바꾸면 그 훅들이 조용히
무시되기 때문이다. 두 번 실행해도 결과가 같다.

전역 git 설정은 건드리지 않는다 — child_env가 GIT_CONFIG_GLOBAL을 빈 파일로 돌린다.
"""

import os
import unittest

from isolated_repo import (
    GITHOOKS_TEMPLATE,
    GITMESSAGE,
    HOOKS_DIR,
    INSTALL_SH,
    IsolatedRepoTestCase,
)

TEMPLATE_FILES = sorted(
    str(p.relative_to(GITHOOKS_TEMPLATE))
    for p in GITHOOKS_TEMPLATE.rglob("*")
    if p.is_file()
)


class InstallGithooksTest(IsolatedRepoTestCase):
    def setUp(self):
        self.repo = self.make_repo(hooks_path=None)

    def install(self, *args):
        return self.run_cmd([INSTALL_SH, *args, self.repo], stdin=b"")

    def config(self, key):
        return self.git("config", "--get", key).stdout.strip()

    def installed_files(self):
        root = self.repo / ".githooks"
        if not root.exists():
            return []
        return sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file())

    # == AC/DoD ==

    def test_githooks_템플릿을_만들고_hooksPath를_설정한다(self):
        """GF-148#3 디스패처와 기본 플러그인을 실행 가능한 파일로 만들고 core.hooksPath=.githooks"""
        self.assertAccepted(self.install())
        self.assertEqual(
            [
                "pre-commit",
                "pre-commit.d/20-source-header",
                "prepare-commit-msg",
                "prepare-commit-msg.d/10-commit-format",
            ],
            TEMPLATE_FILES,
        )
        self.assertEqual(TEMPLATE_FILES, self.installed_files())
        for rel in TEMPLATE_FILES:
            installed = self.repo / ".githooks" / rel
            self.assertEqual((GITHOOKS_TEMPLATE / rel).read_bytes(), installed.read_bytes())
            self.assertTrue(os.access(installed, os.X_OK), f"{rel}에 실행 권한이 없다")
        self.assertEqual(".githooks", self.config("core.hooksPath"))
        self.assertEqual(str(GITMESSAGE), self.config("commit.template"))

    def test_두_번_실행해도_결과가_같다(self):
        """GF-148#3 멱등: 두 번째 실행도 성공하고 파일·설정이 그대로다"""
        self.assertAccepted(self.install())
        first = {r: (self.repo / ".githooks" / r).read_bytes() for r in TEMPLATE_FILES}
        self.assertAccepted(self.install())
        second = {r: (self.repo / ".githooks" / r).read_bytes() for r in TEMPLATE_FILES}
        self.assertEqual(first, second)
        self.assertEqual(".githooks", self.config("core.hooksPath"))

    def test_다른_hooksPath가_있으면_덮지_않고_멈춘다(self):
        """GF-148#3 다른 core.hooksPath가 있으면 아무것도 쓰지 않고 실패한다"""
        self.git_ok("config", "core.hooksPath", ".husky")
        result = self.install()
        self.assertRejected(result)
        self.assertIn(".husky", result.output)
        self.assertEqual(".husky", self.config("core.hooksPath"))
        self.assertEqual([], self.installed_files())

    def test_링크가_아닌_기존_훅이_있으면_덮지_않고_멈춘다(self):
        """GF-148#3 .git/hooks/에 링크가 아닌 훅이 있으면 아무것도 쓰지 않고 실패한다"""
        own_hook = self.git_dir_file("hooks/pre-commit")
        own_hook.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        own_hook.chmod(0o755)
        result = self.install()
        self.assertRejected(result)
        self.assertIn("pre-commit", result.output)
        self.assertEqual("#!/bin/sh\nexit 0\n", own_hook.read_text(encoding="utf-8"))
        self.assertEqual("", self.config("core.hooksPath"))
        self.assertEqual([], self.installed_files())

    # == Coverage ==

    def test_옛_방식_설치면_migrate를_안내하고_멈춘다(self):
        """hooksPath가 이 도구의 hooks/(옛 방식)면 install은 멈추고 migrate를 안내한다"""
        self.git_ok("config", "core.hooksPath", HOOKS_DIR)
        result = self.install()
        self.assertRejected(result)
        self.assertIn("migrate", result.output)
        self.assertEqual(str(HOOKS_DIR), self.config("core.hooksPath"))

    def test_샘플과_심볼릭_링크_훅은_막지_않는다(self):
        """.git/hooks/의 *.sample과 심볼릭 링크(옛 templateDir이 심은 링크 등)는 설치를 막지 않는다"""
        hooks = self.git_dir_file("hooks")
        (hooks / "pre-commit.sample").write_text("#!/bin/sh\n", encoding="utf-8")
        (hooks / "prepare-commit-msg").symlink_to(HOOKS_DIR / "prepare-commit-msg")
        self.assertAccepted(self.install())
        self.assertEqual(".githooks", self.config("core.hooksPath"))

    def test_직접_고친_파일은_덮지_않고_빠진_파일만_채운다(self):
        """.githooks의 고친 파일은 그대로 두고, 없는 템플릿 파일만 새로 만든다"""
        custom = self.write(".githooks/pre-commit", "#!/bin/sh\n# custom\n")
        self.assertAccepted(self.install())
        self.assertEqual("#!/bin/sh\n# custom\n", custom.read_text(encoding="utf-8"))
        self.assertEqual(TEMPLATE_FILES, self.installed_files())

    def test_설치_뒤_커밋이_실제로_검사된다(self):
        """설치한 저장소에서 형식 위반 커밋은 거부되고 맞는 커밋은 통과한다"""
        self.assertAccepted(self.install())
        env = {"PATH": self.path_with_tools(git_commit_tool=INSTALL_SH)}
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")
        self.assertRejected(self.commit("이상한 메시지", env=env))
        self.assertAccepted(self.commit("[feat] after install", env=env))
        self.assertTrailerCount(self.head_message(), "Hooks-Commit:", 1)

    def test_global_옵션은_없앴다고_알리고_멈춘다(self):
        """--global은 decision-32로 없어졌다 — 전역 설정을 건드리지 않고 실패한다"""
        result = self.install("--global")
        self.assertRejected(result)
        self.assertIn("decision-32", result.output)
        self.assertEqual("", self.config("core.hooksPath"))


if __name__ == "__main__":
    unittest.main()
