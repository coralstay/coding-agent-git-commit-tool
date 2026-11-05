# GF-148: hooksPath가 이 도구의 클론 경로인 옛 설치를 .githooks로 옮기는 migrate
"""`git-commit-tool migrate`를 본다(decision-32).

옛 설치(decision-2)는 대상 저장소의 core.hooksPath가 이 클론의 hooks/를 직접 가리킨다.
migrate는 그런 저장소에 .githooks/를 만들고 hooksPath를 .githooks로 바꾼다. 옛 방식이
아닌 저장소(설정 없음, 다른 hooksPath)는 건드리지 않고 멈추고, 이미 옮긴 저장소에서는
아무 일 없이 성공한다.
"""

import shutil
import unittest

from isolated_repo import (
    GITHOOKS_TEMPLATE,
    HOOKS_DIR,
    INSTALL_SH,
    IsolatedRepoTestCase,
)


class MigrateGithooksTest(IsolatedRepoTestCase):
    def setUp(self):
        self.repo = self.make_repo(hooks_path=None)

    def migrate(self):
        return self.run_cmd([INSTALL_SH, "migrate", self.repo], stdin=b"")

    def config(self, key):
        return self.git("config", "--get", key).stdout.strip()

    # == AC/DoD ==

    def test_클론_경로_hooksPath를_githooks로_옮긴다(self):
        """GF-148#5 hooksPath=이 클론의 hooks/인 저장소를 .githooks로 옮긴다"""
        self.git_ok("config", "core.hooksPath", HOOKS_DIR)
        result = self.migrate()
        self.assertAccepted(result)
        self.assertEqual(".githooks", self.config("core.hooksPath"))
        for name in ("pre-commit", "prepare-commit-msg"):
            self.assertEqual(
                (GITHOOKS_TEMPLATE / name).read_bytes(),
                (self.repo / ".githooks" / name).read_bytes(),
            )
        self.assertTrue(
            (self.repo / ".githooks/prepare-commit-msg.d/10-commit-format").exists()
        )

    def test_옮긴_뒤에도_커밋이_검사된다(self):
        """GF-148#5 migrate 뒤 커밋이 .githooks 플러그인 경로로 검사된다"""
        self.git_ok("config", "core.hooksPath", HOOKS_DIR)
        self.assertAccepted(self.migrate())
        env = {"PATH": self.path_with_tools(git_commit_tool=INSTALL_SH)}
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")
        self.assertRejected(self.commit("이상한 메시지", env=env))
        self.assertAccepted(self.commit("[feat] after migrate", env=env))
        self.assertTrailerCount(self.head_message(), "Hooks-Commit:", 1)

    def test_옛_설치가_아니면_건드리지_않고_멈춘다(self):
        """GF-148#5 hooksPath가 없거나 다른 경로면 아무것도 바꾸지 않고 실패한다"""
        result = self.migrate()
        self.assertRejected(result)
        self.assertIn("install", result.output)
        self.assertEqual("", self.config("core.hooksPath"))

        self.git_ok("config", "core.hooksPath", ".husky")
        self.assertRejected(self.migrate())
        self.assertEqual(".husky", self.config("core.hooksPath"))
        self.assertFalse((self.repo / ".githooks").exists())

    # == Coverage ==

    def test_이미_옮긴_저장소에서는_그대로_성공한다(self):
        """멱등: 두 번째 migrate는 아무것도 바꾸지 않고 성공한다"""
        self.git_ok("config", "core.hooksPath", HOOKS_DIR)
        self.assertAccepted(self.migrate())
        self.assertAccepted(self.migrate())
        self.assertEqual(".githooks", self.config("core.hooksPath"))

    def test_다른_클론의_hooks도_옛_설치로_알아본다(self):
        """hooksPath가 이 도구의 다른 클론 hooks/여도 옛 설치로 보고 옮긴다"""
        other = self.temp_dir(prefix="gitformat-otherclone-") / "hooks"
        shutil.copytree(HOOKS_DIR, other)
        self.git_ok("config", "core.hooksPath", other)
        self.assertAccepted(self.migrate())
        self.assertEqual(".githooks", self.config("core.hooksPath"))

    def test_무시되던_git_hooks는_막지_않고_알린다(self):
        """옛 설치에서도 무시되던 .git/hooks의 훅은 막지 않고 목록만 알린다"""
        own_hook = self.git_dir_file("hooks/pre-commit")
        own_hook.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        self.git_ok("config", "core.hooksPath", HOOKS_DIR)
        result = self.migrate()
        self.assertAccepted(result)
        self.assertIn(str(own_hook.name), result.output)
        self.assertEqual("#!/bin/sh\nexit 0\n", own_hook.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
