# ---
# title: test_githooks_commit_format
# description: .githooks의 10-commit-format 플러그인 경로로 커밋 형식 검사가 동작하는지 검증하는 테스트
# authors: [coralstay]
# license: AGPL-3.0-only
# status: draft
# created_date: '2026-11-06'
# updated_date: '2026-11-06'
# ---
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
        self.repo = self.make_repo(hooks_path=None)  # ---- 1
        self.githooks = self.githooks_copy()
        self.git_ok("config", "core.hooksPath", self.githooks)
        self.with_tool = {"PATH": self.path_with_tools(git_commit_tool=INSTALL_SH)}  # ---- 2
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
        self.assertTrailerCount(message, f"Hooks-Commit: {expected}", 1)  # ---- 3
        self.assertTrailerCount(message, f"Signed-off-by: {SIGNED_OFF_BY}", 1)

    def test_형식에_안_맞는_커밋은_거부된다(self):
        """GF-148#2 플러그인 경로에서도 형식 위반 커밋이 거부되고 커밋 객체가 안 생긴다"""
        result = self.commit("이상한 메시지", env=self.with_tool)
        self.assertRejected(result)
        self.assertIn("prepare-commit-msg", result.output)
        self.assertRejected(self.git("rev-parse", "--verify", "HEAD"))  # ---- 4

    def test_no_verify로도_건너뛸_수_없다(self):
        """GF-148#2 디스패처를 거쳐도 prepare-commit-msg는 --no-verify로 건너뛸 수 없다(decision-18)"""
        result = self.commit("이상한 메시지", "--no-verify", env=self.with_tool)  # ---- 5
        self.assertRejected(result)

    # == Coverage ==

    def test_git_commit_tool이_없으면_경고하고_검사를_건너뛴다(self):
        """git-commit-tool이 PATH에 없는 머신에서는 경고만 내고 커밋을 막지 않는다"""
        shadow = self.path_without("git-commit-tool")
        result = self.commit("이상한 메시지", env={"PATH": str(shadow)})  # ---- 6
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


# ======== 노트 ========
# 1 hooksPath 없이 만든 뒤 githooks 사본을 연결
#   설명: make_repo가 기본 훅 연결을 하지 않게 하고 githooks/ 사본(대상 저장소의 .githooks/ 원본)을 직접 연결한다. 이 파일은 플러그인 경로
#   자체를 시험한다.
#   관련: decision-32, tests/isolated_repo.py(githooks_copy)
# 2 PATH에 git-commit-tool을 세운다
#   설명: 플러그인은 PATH의 git-commit-tool을 부른다. 이 클론의 install.sh로 가는 링크를 PATH 앞에 세워 테스트 대상 클론이 실행되게
#   한다.
#   관련: install.sh
# 3 트레일러는 대상 저장소가 아니라 클론 기준
#   설명: 대상 저장소의 .githooks/에는 conf도 클론도 없다. 훅이 자기 클론을 기준으로 gitformat.conf와 Hooks-Commit(클론의
#   HEAD)을 찾는지가 핵심이다.
#   관련: GF-148#2, hooks/prepare-commit-msg
#   개념: 클론 기준 경로
# 4 거부된 커밋은 객체가 생기지 않는다
#   설명: 형식 위반이 거부되었을 뿐 아니라 HEAD가 만들어지지 않았음을 rev-parse로 확인한다.
# 5 --no-verify로 건너뛸 수 없다
#   설명: 디스패처를 거쳐도 prepare-commit-msg는 --no-verify로 건너뛸 수 없다. 검증이 그 훅으로 모인 이유다.
#   관련: decision-18
#   개념: fail-closed
# 6 도구가 없는 머신에서는 경고만 내고 건너뜀
#   설명: 다른 머신에서 도구가 없다고 커밋이 막히면 안 되고 강제는 CI가 맡는다. 경고에 플러그인 이름(10-commit-format)이 나와야 원인을 알 수 있다.
#   관련: tests/test_githooks_dispatcher.py
#   개념: fail-open(의도된)
