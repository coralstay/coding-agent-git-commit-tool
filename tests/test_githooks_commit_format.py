# GF-148: 커밋 형식·트레일러 로직이 .githooks 플러그인(10-commit-format)으로 동작
"""prepare-commit-msg.d/10-commit-format 플러그인 경로로 실제 커밋을 태운다(decision-32).

플러그인은 한 줄로 `git-commit-tool hook prepare-commit-msg "$@"`를 부르고,
`git-commit-tool`(= 이 클론의 install.sh로 가는 심볼릭 링크)이 hooks/prepare-commit-msg를
exec한다. 훅 로직은 그대로이고, 이 경로에서도 훅이 자기 클론을 기준으로 gitformat.conf와
Hooks-Commit을 찾는지가 핵심이다 — 대상 저장소의 .githooks/에는 conf도 클론도 없다.

기존 tests/ 전체를 이 경로로 다시 돌리는 모드는 isolated_repo의
GITFORMAT_TEST_VIA_GITHOOKS=1이 맡는다(CI의 두 번째 테스트 스텝).
"""

import unittest

from isolated_repo import (
    CONF_GUARD_MESSAGE,
    HOOKS_DIR,
    INSTALL_SH,
    SIGNED_OFF_BY,
    IsolatedRepoTestCase,
)


class GithooksCommitFormatTest(IsolatedRepoTestCase):
    def setUp(self):
        self.repo = self.make_repo(hooks_path=None)
        self.githooks = self.githooks_copy()
        self.git_ok("config", "core.hooksPath", self.githooks)
        self.with_tool = {"PATH": self.path_with_tools(git_commit_tool=INSTALL_SH)}
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")

    # == AC/DoD ==

    def test_형식에_맞는_커밋에_클론_기준_트레일러가_붙는다(self):
        """GF-148#2 플러그인 경로에서도 훅이 클론의 conf와 HEAD로 트레일러를 붙인다"""
        expected = self.git_ok(
            "-C", HOOKS_DIR, "rev-parse", "--short", "HEAD"
        ).stdout.strip()
        result = self.commit("[feat] via githooks plugin", env=self.with_tool)
        self.assertAccepted(result)
        self.assertNotIn(CONF_GUARD_MESSAGE, result.output)
        message = self.head_message()
        self.assertTrailerCount(message, f"Hooks-Commit: {expected}", 1)
        self.assertTrailerCount(message, f"Signed-off-by: {SIGNED_OFF_BY}", 1)

    def test_형식에_안_맞는_커밋은_거부된다(self):
        """GF-148#2 플러그인 경로에서도 형식 위반 커밋이 거부되고 커밋 객체가 안 생긴다"""
        result = self.commit("이상한 메시지", env=self.with_tool)
        self.assertRejected(result)
        self.assertIn("prepare-commit-msg", result.output)
        self.assertRejected(self.git("rev-parse", "--verify", "HEAD"))

    def test_no_verify로도_건너뛸_수_없다(self):
        """GF-148#2 디스패처를 거쳐도 prepare-commit-msg는 --no-verify로 건너뛸 수 없다(decision-18)"""
        result = self.commit("이상한 메시지", "--no-verify", env=self.with_tool)
        self.assertRejected(result)

    # == Coverage ==

    def test_git_commit_tool이_없으면_경고하고_검사를_건너뛴다(self):
        """git-commit-tool이 PATH에 없는 머신에서는 경고만 내고 커밋을 막지 않는다"""
        shadow = self.path_without("git-commit-tool")
        result = self.commit("이상한 메시지", env={"PATH": str(shadow)})
        self.assertAccepted(result)
        self.assertIn("10-commit-format", result.output)
        self.assertIn("건너뜁니다", result.output)

    def test_hook_하위_명령은_모르는_훅을_거부한다(self):
        """git-commit-tool hook <모르는 훅>은 0이 아닌 코드로 끝난다"""
        result = self.run_cmd([INSTALL_SH, "hook", "pre-push"])
        self.assertRejected(result)
        self.assertIn("pre-push", result.output)


if __name__ == "__main__":
    unittest.main()
