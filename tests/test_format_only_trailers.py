"""커밋 포맷 전용 — 훅이 토큰·툴콜을 측정하지 않는다(GF-146, decision-31).

GF-146 전에는 AI 도구가 감지된 커밋에 Tokens-Used/Tool-Calls를 붙이려고 세션
트랜스크립트의 usage를 읽어 커밋에 귀속하고, 그 귀속 기록을 .git/ 아래 상태 파일로
남겼다. 측정을 커밋 훅에 두면 깃과 측정이 강결합되므로 측정은 별도 컴포넌트로 옮기기로
했다(2026-10-12 유저 결정). 이 파일은 그 뒤에 남는 동작을 본다:

- 측정 트레일러를 붙이지 않는다(GF-146#B1)
- 사람이나 에이전트가 직접 쓴 측정 줄은 그대로 둔다(GF-146#B2)
- 귀속 기록 파일을 만들거나 읽지 않는다(GF-146#B3)
- 나머지 트레일러 삽입은 그대로다(GF-146#B4)

AI-Agent의 모델 판정(트랜스크립트의 message.model 읽기)은 측정이 아니라 출처 기록이라
남는다 — 그 동작은 test_trailer_ai_attribution.py가 본다.
"""

import unittest

from isolated_repo import SIGNED_OFF_BY, IsolatedRepoTestCase

ATTRIBUTED_RECORD = ".gitformat-token-attributed"
LEGACY_CURSOR = ".gitformat-token-cursor"


def assistant_turn_editing(path, *, model="claude-test-model"):
    """커밋할 파일을 Edit한 assistant 응답 한 줄. GF-146 전이라면 측정·귀속 대상이었다."""
    return {
        "type": "assistant",
        "requestId": "req-1",
        "message": {
            "id": "msg-1",
            "model": model,
            "usage": {"input_tokens": 10, "output_tokens": 5},
            "content": [
                {"type": "tool_use", "name": "Edit", "input": {"file_path": path}}
            ],
        },
    }


class FormatOnlyTrailersTest(IsolatedRepoTestCase):
    def setUp(self):
        super().setUp()
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")

    def trailer_keys(self):
        """HEAD 커밋의 트레일러 키를 나온 순서대로 돌려준다."""
        raw = self.git_ok(
            "log", "-1", "--format=%(trailers:only,unfold,keyonly)"
        ).stdout
        return [line.strip() for line in raw.splitlines() if line.strip()]

    # ── AC #1: 측정 코드 삭제 ──────────────────────────────────────

    def test_GF_146_1_B1_claude_code_커밋에_측정_트레일러가_붙지_않는다(self):
        """[GF-146#1/GF-146#B1] usage가 든 트랜스크립트가 있어도 Tokens-Used/Tool-Calls가 붙지 않고, AI-Agent의 모델은 여전히 채워진다"""
        home = self.fake_home()
        self.write_transcript(home, [assistant_turn_editing("a.txt")])
        self.assertAccepted(
            self.commit("[feat] no measurement", env=self.claude_env(home))
        )
        message = self.head_message()
        self.assertTrailerKeyAbsent(message, "Tokens-Used")
        self.assertTrailerKeyAbsent(message, "Tool-Calls")
        # 모델 판정은 남는다 — 트랜스크립트를 읽는 경로 자체가 사라진 게 아니다.
        self.assertTrailerCount(
            message, "AI-Agent: claude-code/2.1.0 (claude-test-model)", 1
        )

    def test_GF_146_1_B1_claude_code_외_도구에도_측정_트레일러가_붙지_않는다(self):
        """[GF-146#1/GF-146#B1] claude-code 외 AI 도구 커밋에도 unavailable (no-usage-channel) 같은 측정 줄이 붙지 않는다"""
        self.git_ok("config", "gitformat.aiModel", "gpt-5")
        self.assertAccepted(
            self.commit("[feat] other tool", env={"AI_AGENT": "other-tool_1-2-3_agent"})
        )
        message = self.head_message()
        self.assertTrailerKeyAbsent(message, "Tokens-Used")
        self.assertTrailerKeyAbsent(message, "Tool-Calls")
        self.assertTrailerCount(message, "AI-Agent: other-tool/1.2.3 (gpt-5)", 1)

    def test_GF_146_1_B2_직접_쓴_측정_줄은_그대로_남는다(self):
        """[GF-146#1/GF-146#B2] 메시지에 직접 쓴 Tokens-Used/Tool-Calls 줄은 지우지도 바꾸지도 않는다(AI 커밋·사람 커밋 모두)"""
        body = "Tokens-Used: in=123 out=45\nTool-Calls: 7"
        home = self.fake_home()
        self.write_transcript(home, [assistant_turn_editing("a.txt")])
        self.assertAccepted(
            self.commit(f"[feat] agent wrote it\n\n{body}", env=self.claude_env(home))
        )
        message = self.head_message()
        self.assertTrailerCount(message, "Tokens-Used: in=123 out=45", 1)
        self.assertTrailerCount(message, "Tokens-Used:", 1)
        self.assertTrailerCount(message, "Tool-Calls: 7", 1)
        self.assertTrailerCount(message, "Tool-Calls:", 1)

        self.write("b.txt", "hi\n")
        self.git_ok("add", "b.txt")
        self.assertAccepted(self.commit(f"[feat] human wrote it\n\n{body}"))
        message = self.head_message()
        self.assertTrailerCount(message, "Tokens-Used: in=123 out=45", 1)
        self.assertTrailerCount(message, "Tool-Calls: 7", 1)

    def test_GF_146_1_B3_귀속_기록_파일을_만들지_않는다(self):
        """[GF-146#1/GF-146#B3] 귀속될 응답이 있는 claude-code 커밋 뒤에도 .git/.gitformat-token-attributed가 생기지 않는다"""
        home = self.fake_home()
        self.write_transcript(home, [assistant_turn_editing("a.txt")])
        self.assertAccepted(
            self.commit("[feat] no record file", env=self.claude_env(home))
        )
        self.assertFalse(self.git_dir_file(ATTRIBUTED_RECORD).exists())
        self.assertFalse(self.git_dir_file(LEGACY_CURSOR).exists())

    def test_GF_146_1_B3_남아_있는_상태_파일을_건드리지_않는다(self):
        """[GF-146#1/GF-146#B3] GF-146 전에 생긴 귀속 기록·델타 커서 파일은 읽지도 고치지도 지우지도 않는다"""
        record = self.git_dir_file(ATTRIBUTED_RECORD)
        cursor = self.git_dir_file(LEGACY_CURSOR)
        record.write_text("fake-session\nstale-key\n", encoding="utf-8")
        cursor.write_text("fake-session 3\n", encoding="utf-8")
        home = self.fake_home()
        self.write_transcript(home, [assistant_turn_editing("a.txt")])
        self.assertAccepted(
            self.commit("[feat] leave state files", env=self.claude_env(home))
        )
        self.assertEqual("fake-session\nstale-key\n", record.read_text(encoding="utf-8"))
        self.assertEqual("fake-session 3\n", cursor.read_text(encoding="utf-8"))

    # ── AC #2: 남은 트레일러 삽입은 그대로 ───────────────────────────

    def test_GF_146_2_B4_에이전트_커밋의_트레일러_구성이_그대로다(self):
        """[GF-146#2/GF-146#B4] Task-Id 브랜치의 claude-code 커밋에는 Task-Id · AI-Agent · Co-Authored-By · Hooks-Commit만 이 순서로 붙는다"""
        self.git_ok("checkout", "-q", "-b", "GF-7-format-only")
        home = self.fake_home()
        self.write_transcript(home, [assistant_turn_editing("a.txt")])
        self.assertAccepted(
            self.commit("[feat] agent trailers", env=self.claude_env(home))
        )
        self.assertEqual(
            ["Task-Id", "AI-Agent", "Co-Authored-By", "Hooks-Commit"],
            self.trailer_keys(),
        )
        message = self.head_message()
        self.assertTrailerCount(message, "Task-Id: GF-7", 1)
        self.assertTrailerCount(
            message, "Co-Authored-By: Claude <noreply@anthropic.com>", 1
        )

    def test_GF_146_2_B4_사람_커밋의_트레일러_구성이_그대로다(self):
        """[GF-146#2/GF-146#B4] Task-Id 브랜치의 사람 커밋에는 Task-Id · Hooks-Commit · Signed-off-by만 이 순서로 붙는다"""
        self.git_ok("checkout", "-q", "-b", "GF-7-format-only")
        self.assertAccepted(self.commit("[feat] human trailers"))
        self.assertEqual(
            ["Task-Id", "Hooks-Commit", "Signed-off-by"], self.trailer_keys()
        )
        self.assertTrailerCount(
            self.head_message(), f"Signed-off-by: {SIGNED_OFF_BY}", 1
        )


if __name__ == "__main__":
    unittest.main()
