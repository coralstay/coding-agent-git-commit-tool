"""AI 여부와 무관하게 항상 붙는 트레일러(Hooks-Commit, Signed-off-by)를 본다.

구 robustness-post-commit.bats(GF-25, GF-82)의 해당 케이스. 트레일러 삽입은
`git commit --amend`로 이뤄지고 그 amend가 post-commit을 다시 발동시키므로,
_GITFORMAT_AMEND_GUARD가 재귀를 끊는지도 여기서 본다.
"""

import subprocess
import unittest

from isolated_repo import HOOKS_DIR, SIGNED_OFF_BY, IsolatedRepoTestCase


class UnconditionalTrailerTest(IsolatedRepoTestCase):
    def test_Signed_off_by가_커미터_정보로_삽입된다(self):
        """[GF-82] 정상 커밋에 Signed-off-by가 커미터 정보로 자동 삽입된다"""
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")
        self.assertAccepted(self.commit("[feat] signed off commit"))
        self.assertTrailerCount(
            self.head_message(), f"Signed-off-by: {SIGNED_OFF_BY}", 1
        )

    def test_Hooks_Commit이_훅_저장소의_HEAD로_한_번_붙는다(self):
        """Hooks-Commit이 이 커밋을 검증한 훅 코드의 커밋 해시로 정확히 한 번 붙는다 (decision-5)"""
        # bats 판은 Hooks-Commit의 부재만 확인했고(python3 부재 케이스) 값이 맞는지는
        # 본 적이 없다. 개수까지 보는 단언으로 값을 직접 고정한다.
        expected = self.git_ok(
            "-C", HOOKS_DIR, "rev-parse", "--short", "HEAD"
        ).stdout.strip()
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")
        self.assertAccepted(self.commit("[feat] hooks commit trailer"))
        message = self.head_message()
        self.assertTrailerCount(message, f"Hooks-Commit: {expected}", 1)

    def test_재귀_가드가_유한_시간_안에_끝낸다(self):
        """[재귀가드] --no-verify + AI 트레일러가 붙는 커밋도 유한 시간 안에 끝난다"""
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")
        # GF-97 이후 이 커밋에는 AI-Tool: other-tool과 함께 Tokens-Used/Tool-Calls:
        # unavailable (no-usage-channel)이 붙지만, 이 테스트의 관심사는 재귀 가드가
        # 유한 시간 안에 끝나는지이지 트레일러 값 자체가 아니다.
        # GF-127 전에는 --no-verify가 commit-msg의 AI-Model 게이트까지 건너뛰었지만,
        # 그 게이트가 --no-verify로 건너뛸 수 없는 prepare-commit-msg로 옮겨왔으므로
        # 게이트를 통과할 모델을 먼저 설정한다.
        self.git_ok("config", "gitformat.aiModel", "gpt-5")
        try:
            result = self.commit(
                "[feat] recursion guard check",
                "--no-verify",
                env={"AI_AGENT": "other-tool_1-0"},
                timeout=10,
            )
        except subprocess.TimeoutExpired:
            self.fail("post-commit이 10초 안에 끝나지 않았다 - 재귀 가드가 깨졌다")
        self.assertAccepted(result)


if __name__ == "__main__":
    unittest.main()
