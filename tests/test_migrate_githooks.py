# ---
# title: test_migrate_githooks
# description: 옛 hooksPath 설치를 .githooks로 옮기는 migrate의 동작과 건드리지 않는 경우를 검증하는 테스트
# authors: [coralstay]
# license: AGPL-3.0-only
# status: draft
# created_date: '2026-11-06'
# updated_date: '2026-11-06'
# ---
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
        self.git_ok("config", "core.hooksPath", HOOKS_DIR)  # ---- 1
        result = self.migrate()
        self.assertAccepted(result)
        self.assertEqual(".githooks", self.config("core.hooksPath"))  # ---- 2
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

    def test_plugins_옵션으로_고른_플러그인만_옮긴다(self):
        """GF-149#2 migrate --plugins source-header면 10-commit-format 없이 디스패처와 20-source-header만 만든다"""
        self.git_ok("config", "core.hooksPath", HOOKS_DIR)
        self.assertAccepted(
            self.run_cmd(
                [INSTALL_SH, "migrate", "--plugins", "source-header", self.repo],
                stdin=b"",
            )
        )
        self.assertEqual(".githooks", self.config("core.hooksPath"))
        root = self.repo / ".githooks"
        self.assertEqual(
            ["pre-commit", "pre-commit.d/20-source-header", "prepare-commit-msg"],
            sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()),
        )

    def test_이미_옮긴_저장소에도_plugins를_적용하고_있는_플러그인은_지우지_않는다(self):
        """GF-149#2 이미 .githooks인 저장소에서 migrate --plugins는 고른 것만 채우고 기존 파일은 남긴다"""
        self.git_ok("config", "core.hooksPath", HOOKS_DIR)
        self.assertAccepted(self.migrate())
        (self.repo / ".githooks/pre-commit.d/20-source-header").unlink()
        self.assertAccepted(
            self.run_cmd(
                [INSTALL_SH, "migrate", "--plugins=source-header", self.repo],
                stdin=b"",
            )
        )
        self.assertTrue((self.repo / ".githooks/pre-commit.d/20-source-header").exists())
        self.assertTrue(
            (self.repo / ".githooks/prepare-commit-msg.d/10-commit-format").exists()
        )

    def test_migrate에_모르는_플러그인_이름이면_아무것도_바꾸지_않고_실패한다(self):
        """GF-149#2 migrate --plugins nope는 hooksPath도 .githooks도 건드리지 않고 exit 1"""
        self.git_ok("config", "core.hooksPath", HOOKS_DIR)
        result = self.run_cmd(
            [INSTALL_SH, "migrate", "--plugins", "nope", self.repo], stdin=b""
        )
        self.assertEqual(1, result.returncode, str(result))
        self.assertIn("nope", result.output)
        self.assertEqual(str(HOOKS_DIR), self.config("core.hooksPath"))
        self.assertFalse((self.repo / ".githooks").exists())

    def test_옛_설치가_아니면_건드리지_않고_멈춘다(self):
        """GF-148#5 hooksPath가 없거나 다른 경로면 아무것도 바꾸지 않고 실패한다"""
        result = self.migrate()
        self.assertRejected(result)
        self.assertIn("install", result.output)
        self.assertEqual("", self.config("core.hooksPath"))  # ---- 3

        self.git_ok("config", "core.hooksPath", ".husky")
        self.assertRejected(self.migrate())
        self.assertEqual(".husky", self.config("core.hooksPath"))
        self.assertFalse((self.repo / ".githooks").exists())  # ---- 4

    # == Coverage ==

    def test_이미_옮긴_저장소에서는_그대로_성공한다(self):
        """멱등: 두 번째 migrate는 아무것도 바꾸지 않고 성공한다"""
        self.git_ok("config", "core.hooksPath", HOOKS_DIR)
        self.assertAccepted(self.migrate())
        self.assertAccepted(self.migrate())  # ---- 5
        self.assertEqual(".githooks", self.config("core.hooksPath"))

    def test_다른_클론의_hooks도_옛_설치로_알아본다(self):
        """hooksPath가 이 도구의 다른 클론 hooks/여도 옛 설치로 보고 옮긴다"""
        other = self.temp_dir(prefix="gitformat-otherclone-") / "hooks"
        shutil.copytree(HOOKS_DIR, other)
        self.git_ok("config", "core.hooksPath", other)  # ---- 6
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
        self.assertEqual("#!/bin/sh\nexit 0\n", own_hook.read_text(encoding="utf-8"))  # ---- 7


if __name__ == "__main__":
    unittest.main()


# ======== 노트 ========
# 1 옛 설치 = hooksPath가 이 클론의 hooks/
#   설명: 옛 설치(decision-2)는 대상 저장소의 core.hooksPath가 이 클론의 hooks/를 직접 가리킨다. migrate는 그런 저장소만
#   .githooks로 옮긴다.
#   관련: decision-2, decision-32
# 2 hooksPath가 .githooks로 바뀜
#   설명: 옮긴 뒤 hooksPath는 클론 경로가 아니라 저장소 안의 상대 경로 .githooks다. 그래야 다른 클론·CI에서도 같은 훅이 동작한다.
#   관련: GF-148#5
# 3 옛 설치가 아니면 건드리지 않고 멈춤
#   설명: hooksPath가 없거나 다른 경로(.husky 등)면 아무것도 바꾸지 않고 실패하며 install을 안내한다.
#   관련: GF-148#5
#   개념: fail-closed
# 4 다른 hooksPath 저장소에는 .githooks도 만들지 않음
#   설명: 실패했을 때 설정뿐 아니라 파일도 쓰이지 않았음을 확인한다.
# 5 두 번째 migrate는 아무것도 바꾸지 않고 성공
#   설명: 이미 .githooks로 옮긴 저장소에서 다시 불러도 성공하고 설정이 그대로여야 한다.
#   관련: GF-148#5
#   개념: 멱등(idempotent)
# 6 다른 클론의 hooks/도 옛 설치로 인식
#   설명: hooksPath가 이 도구의 다른 클론 hooks/여도 옛 설치로 보고 옮긴다. install.sh는 경로가 이 클론의 hooks/이거나, 아니면 그
#   디렉터리에 prepare-commit-msg와 gitformat.conf가 모두 있을 때 이 도구의 hooks/로 본다.
#   관련: install.sh(migrate)
# 7 .git/hooks의 직접 만든 훅은 막지 않고 알린다
#   설명: 옛 설치에서도 hooksPath 때문에 이미 무시되던 훅이므로 migrate를 막지 않고 목록만 알린다. 내용은 그대로 둔다.
#   관련: tests/test_install_githooks.py
