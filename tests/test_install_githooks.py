# ---
# title: test_install_githooks
# description: install이 대상 저장소에 .githooks를 만들고 hooksPath를 설정하며 멱등인지 검증하는 테스트
# authors: [coralstay]
# license: AGPL-3.0-only
# status: draft
# created_date: '2026-11-06'
# updated_date: '2026-11-06'
# ---
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
        return self.run_cmd([INSTALL_SH, *args, self.repo], stdin=b"")  # ---- 1

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
            self.assertEqual((GITHOOKS_TEMPLATE / rel).read_bytes(), installed.read_bytes())  # ---- 2
            self.assertTrue(os.access(installed, os.X_OK), f"{rel}에 실행 권한이 없다")
        self.assertEqual(".githooks", self.config("core.hooksPath"))
        self.assertEqual(str(GITMESSAGE), self.config("commit.template"))

    def test_두_번_실행해도_결과가_같다(self):
        """GF-148#3 멱등: 두 번째 실행도 성공하고 파일·설정이 그대로다"""
        self.assertAccepted(self.install())
        first = {r: (self.repo / ".githooks" / r).read_bytes() for r in TEMPLATE_FILES}
        self.assertAccepted(self.install())
        second = {r: (self.repo / ".githooks" / r).read_bytes() for r in TEMPLATE_FILES}
        self.assertEqual(first, second)  # ---- 3
        self.assertEqual(".githooks", self.config("core.hooksPath"))

    def test_다른_hooksPath가_있으면_덮지_않고_멈춘다(self):
        """GF-148#3 다른 core.hooksPath가 있으면 아무것도 쓰지 않고 실패한다"""
        self.git_ok("config", "core.hooksPath", ".husky")
        result = self.install()
        self.assertRejected(result)
        self.assertIn(".husky", result.output)
        self.assertEqual(".husky", self.config("core.hooksPath"))
        self.assertEqual([], self.installed_files())  # ---- 4

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
        self.assertEqual([], self.installed_files())  # ---- 5

    def test_plugins_옵션이_고른_플러그인만_설치한다(self):
        """GF-149#1 --plugins source-header면 10-commit-format 없이 디스패처와 20-source-header만 만든다"""
        self.assertAccepted(self.install("--plugins", "source-header"))
        self.assertEqual(
            [
                "pre-commit",
                "pre-commit.d/20-source-header",
                "prepare-commit-msg",
            ],
            self.installed_files(),
        )
        self.assertEqual(".githooks", self.config("core.hooksPath"))

    def test_plugins_옵션은_등호_쉼표_목록_install_서브커맨드를_받는다(self):
        """GF-149#1 --plugins=이름, 쉼표 목록, `install --plugins ... 대상`도 같은 결과"""
        self.assertAccepted(self.install("--plugins=commit-format"))
        self.assertEqual(
            [
                "pre-commit",
                "prepare-commit-msg",
                "prepare-commit-msg.d/10-commit-format",
            ],
            self.installed_files(),
        )
        self.assertAccepted(self.install("--plugins", "source-header,commit-format"))
        self.assertEqual(TEMPLATE_FILES, self.installed_files())
        self.repo = self.make_repo(hooks_path=None)
        self.assertAccepted(
            self.run_cmd(
                [INSTALL_SH, "install", "--plugins", "source-header", self.repo],
                stdin=b"",
            )
        )
        self.assertNotIn(
            "prepare-commit-msg.d/10-commit-format", self.installed_files()
        )

    def test_plugins_옵션이_없으면_둘_다_설치한다(self):
        """GF-149#1 옵션이 없으면 지금처럼 commit-format과 source-header를 둘 다 설치한다"""
        self.assertAccepted(self.install())
        self.assertEqual(TEMPLATE_FILES, self.installed_files())

    def test_모르는_플러그인_이름이면_아무것도_쓰지_않고_실패한다(self):
        """GF-149#1 모르는 이름(다른 이름과 섞여도)이면 아무것도 쓰지 않고 exit 1, 알려진 이름을 안내"""
        for value in ("nope", "source-header,nope", ""):
            result = self.install("--plugins", value)
            self.assertEqual(1, result.returncode, str(result))
            if value:
                self.assertIn("nope", result.output)
            self.assertIn("source-header", result.output)
            self.assertEqual("", self.config("core.hooksPath"))
            self.assertEqual([], self.installed_files())
        result = self.run_cmd([INSTALL_SH, self.repo, "--plugins"], stdin=b"")
        self.assertEqual(1, result.returncode, str(result))
        self.assertEqual([], self.installed_files())

    def test_source_header만_설치하면_커밋_형식은_강제되지_않는다(self):
        """GF-149#1 --plugins source-header 뒤에는 형식에 안 맞는 메시지도 커밋되고 트레일러가 붙지 않는다"""
        self.assertAccepted(self.install("--plugins", "source-header"))
        env = {"PATH": self.path_with_tools(git_commit_tool=INSTALL_SH)}
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")
        self.assertAccepted(self.commit("이상한 메시지", env=env))
        self.assertTrailerCount(self.head_message(), "Hooks-Commit:", 0)

    # == Coverage ==

    def test_옛_방식_설치면_migrate를_안내하고_멈춘다(self):
        """hooksPath가 이 도구의 hooks/(옛 방식)면 install은 멈추고 migrate를 안내한다"""
        self.git_ok("config", "core.hooksPath", HOOKS_DIR)
        result = self.install()
        self.assertRejected(result)
        self.assertIn("migrate", result.output)
        self.assertEqual(str(HOOKS_DIR), self.config("core.hooksPath"))  # ---- 6

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
        self.assertEqual("#!/bin/sh\n# custom\n", custom.read_text(encoding="utf-8"))  # ---- 7
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
        self.assertEqual("", self.config("core.hooksPath"))  # ---- 8


if __name__ == "__main__":
    unittest.main()


# ======== 노트 ========
# 1 install은 비대화형(stdin 비움)으로 실행
#   설명: 설치 스크립트가 질문으로 멈추지 않는지 보려고 stdin을 빈 바이트로 닫고 대상 저장소를 마지막 인자로 넘긴다.
#   관련: install.sh
# 2 설치본은 템플릿과 바이트 단위로 같다
#   설명: githooks/ 템플릿을 대상 저장소의 .githooks/로 그대로 복사한다. 실행 권한까지 보존돼야 git이 훅으로 실행한다.
#   관련: decision-32, githooks/
# 3 두 번 실행해도 결과가 같다(멱등)
#   설명: 두 번째 실행도 성공하고 파일 내용과 core.hooksPath가 그대로여야 한다.
#   관련: GF-148#3
#   개념: 멱등(idempotent)
# 4 다른 hooksPath가 있으면 아무것도 쓰지 않고 멈춤
#   설명: hooksPath를 바꾸면 기존 훅(.husky 등)이 조용히 무시되므로 덮지 않고 실패한다. 설정도 원래 값 그대로, .githooks/도 만들어지지 않아야
#   한다.
#   관련: GF-148#3, decision-32
#   개념: fail-closed
# 5 링크가 아닌 기존 .git/hooks 훅도 보호
#   설명: 사용자가 직접 둔 훅은 내용도 hooksPath도 그대로 두고 설치를 멈춘다. 실행 가능한 파일이 있다는 사실이 곧 사용자의 자산이다.
#   관련: GF-148#3
#   개념: fail-closed
# 6 옛 방식 설치면 migrate를 안내하고 멈춤
#   설명: hooksPath가 이 도구의 hooks/를 직접 가리키는 옛 설치는 install이 덮지 않고 migrate를 안내한다. 값도 바꾸지 않는다.
#   관련: tests/test_migrate_githooks.py, decision-2, decision-32
# 7 직접 고친 파일은 덮지 않고 빠진 파일만 채움
#   설명: 사용자가 .githooks/에서 고친 파일은 그대로 두고 템플릿에만 있는 파일만 새로 만든다. 재설치가 사용자 수정을 지우면 안 된다.
#   관련: GF-148#3
#   개념: 멱등(idempotent)
# 8 --global은 없어졌다고 알리고 멈춤
#   설명: --global(init.templateDir)은 decision-32로 폐지됐다. 전역 설정을 건드리지 않고 실패하며, 출력에 결정 번호를 알린다.
#   관련: decision-32
