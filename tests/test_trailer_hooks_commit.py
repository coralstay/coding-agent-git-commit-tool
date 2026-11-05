"""Hooks-Commit과 Signed-off-by를 본다.

구 robustness-post-commit.bats(GF-25, GF-82)의 해당 케이스에서 출발했다. Hooks-Commit은
AI 여부와 무관하게 항상 붙는다. Signed-off-by는 decision-30부터 AI 도구가 감지되지 않은
커밋(사람 커밋)에만 붙는다 — DCO에서 이 트레일러는 사람의 인증이기 때문이다.

GF-128 전에는 post-commit이 `git commit --amend`로 트레일러를 붙였고 그 amend가
post-commit을 다시 발동시켜, 재귀 가드(_GITFORMAT_AMEND_GUARD)가 유한 시간 안에
끝내는지도 여기서 봤다. 삽입이 prepare-commit-msg의 메시지 파일 쓰기로 바뀌어 amend도
재귀도 없어졌으므로 그 케이스는 사라졌다.
"""

import unittest

from isolated_repo import HOOKS_DIR, SIGNED_OFF_BY, IsolatedRepoTestCase


class UnconditionalTrailerTest(IsolatedRepoTestCase):
    def setUp(self):
        super().setUp()
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")

    def test_사람_커밋에는_Signed_off_by가_커미터_정보로_붙는다(self):
        """[GF-82/decision-30] AI_AGENT가 없는 커밋에 Signed-off-by가 커미터 정보로 한 번 붙는다"""
        self.assertAccepted(self.commit("[feat] signed off commit"))
        message = self.head_message()
        self.assertTrailerCount(message, f"Signed-off-by: {SIGNED_OFF_BY}", 1)
        self.assertTrailerCount(message, "Signed-off-by:", 1)

    def test_에이전트_커밋에는_Signed_off_by가_붙지_않는다(self):
        """[decision-30] AI_AGENT=claude-code_... 커밋에는 Signed-off-by가 붙지 않는다"""
        home = self.fake_home()
        self.assertAccepted(
            self.commit("[feat] agent commit", env=self.claude_env(home))
        )
        message = self.head_message()
        self.assertTrailerKeyAbsent(message, "Signed-off-by")
        # 같은 신호로 AI-Agent가 붙었는지까지 봐야 "에이전트 커밋으로 판정됐다"가 증명된다.
        self.assertTrailerCount(message, "AI-Agent:", 1)

    def test_에이전트_커밋에_사람이_쓴_Signed_off_by는_그대로_남는다(self):
        """[decision-30] 운영자가 메시지에 직접 쓴 Signed-off-by는 에이전트 커밋에서도 보존된다"""
        home = self.fake_home()
        self.assertAccepted(
            self.commit(
                "[feat] agent commit signed by human\n\nSigned-off-by: Jane <j@e.com>",
                env=self.claude_env(home),
            )
        )
        message = self.head_message()
        self.assertTrailerCount(message, "Signed-off-by:", 1)
        self.assertTrailerCount(message, "Signed-off-by: Jane <j@e.com>", 1)

    def test_Hooks_Commit이_훅_저장소의_HEAD로_한_번_붙는다(self):
        """Hooks-Commit이 이 커밋을 검증한 훅 코드의 커밋 해시로 정확히 한 번 붙는다 (decision-5)"""
        expected = self.git_ok(
            "-C", HOOKS_DIR, "rev-parse", "--short", "HEAD"
        ).stdout.strip()
        self.assertAccepted(self.commit("[feat] hooks commit trailer"))
        self.assertTrailerCount(self.head_message(), f"Hooks-Commit: {expected}", 1)


if __name__ == "__main__":
    unittest.main()
