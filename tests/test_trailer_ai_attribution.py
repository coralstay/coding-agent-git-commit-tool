"""AI 도구 귀속 트레일러(AI-Tool/AI-Tool-Version/AI-Model)를 본다(decision-5).

구 robustness-post-commit.bats(GF-25, GF-97, GF-98)의 결함주입·슬러그 케이스.
AI-Model은 Claude Code 세션 트랜스크립트에서 읽으므로, 트랜스크립트를 못 읽는
상황(JSON 손상, HOME 이상값)에서 커밋을 막지 않고 그 트레일러만 생략하는
fail-open이 의도된 동작이다.
"""

import unittest

from isolated_repo import IsolatedRepoTestCase


class TrailerAiAttributionTest(IsolatedRepoTestCase):
    def test_트랜스크립트_JSON이_깨져도_AI_Model만_생략된다(self):
        """[결함주입] Claude Code 트랜스크립트 JSON이 깨져도 AI-Model만 생략되고 커밋은 막히지 않는다"""
        home = self.fake_home()
        self.write_transcript(
            home, ["this is not valid json at all", "{ also not valid"]
        )
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")
        self.assertAccepted(
            self.commit("[feat] broken transcript", env=self.claude_env(home))
        )
        message = self.head_message()
        self.assertTrailerKeyAbsent(message, "AI-Model")
        self.assertTrailerCount(message, "AI-Tool: claude-code", 1)

    def test_HOME이_존재하지_않아도_커밋은_막히지_않는다(self):
        """[결함주입] HOME이 존재하지 않는 경로여도 커밋은 막히지 않는다"""
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")
        missing_home = self.repo / "nonexistent-gitformat-home"
        self.assertAccepted(
            self.commit("[feat] broken HOME", env=self.claude_env(missing_home))
        )

    def test_사람_커밋에는_AI_트레일러가_전혀_붙지_않는다(self):
        """[GF-97] 사람 커밋(AI 도구 미감지)에는 Tokens-Used/Tool-Calls가 전혀 붙지 않는다"""
        # AI_AGENT/CLAUDE_CODE_SESSION_ID는 헬퍼가 자식 환경에서 기본적으로 지운다 —
        # 이 스위트를 Claude Code로 돌리면 셸 환경에 이미 노출돼 있어(GF-97 검증 중
        # 실제로 발견) 지우지 않으면 "사람 커밋"이 조용히 AI 커밋이 된다.
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")
        self.assertAccepted(self.commit("[feat] human commit no ai"))
        message = self.head_message()
        self.assertTrailerKeyAbsent(message, "AI-Tool")
        self.assertTrailerKeyAbsent(message, "Tokens-Used")
        self.assertTrailerKeyAbsent(message, "Tool-Calls")

    def test_밑줄과_점이_든_경로에서도_트랜스크립트를_찾는다(self):
        """[GF-98] 저장소 경로에 밑줄/점이 있어도 Claude Code 실제 슬러그 규칙으로 트랜스크립트를 찾아 AI-Model/Tokens-Used/Tool-Calls가 채워진다"""
        # Claude Code의 실제 규칙은 "영숫자가 아닌 모든 문자를 하이픈으로 치환"이다.
        # GF-98 이전에는 훅도 테스트도 `/`만 치환해 둘 다 틀렸으니 우연히 일치하며
        # 버그를 못 잡았다. 저장소 최상위 디렉터리 이름 자체에 밑줄/점을 넣어(하위
        # 디렉터리에 넣어도 소용없다 - git 훅은 항상 worktree 최상위를 PWD로 실행된다)
        # 두 알고리즘이 반드시 갈리는 상황을 재현한다.
        nested = self.repo / "repo_with.dot_and_underscore"
        self.make_repo(path=nested)

        home = self.fake_home()
        self.write_transcript(
            home,
            [
                {
                    "type": "assistant",
                    "message": {
                        "model": "claude-slug-fix-test",
                        "usage": {"input_tokens": 10, "output_tokens": 5},
                        # 커밋할 a.txt를 건드린 응답이라야 Tokens-Used에 귀속된다(GF-129).
                        "content": [
                            {
                                "type": "tool_use",
                                "name": "Edit",
                                "input": {"file_path": "a.txt"},
                            }
                        ],
                    },
                }
            ],
            cwd=nested,
        )

        self.write("a.txt", "hi\n", cwd=nested)
        self.git_ok("add", "a.txt", cwd=nested)
        self.assertAccepted(
            self.commit(
                "[feat] underscore dot path slug",
                cwd=nested,
                env=self.claude_env(home),
            )
        )
        message = self.head_message(cwd=nested)
        self.assertTrailerCount(message, "AI-Model: claude-slug-fix-test", 1)
        self.assertTrailerCount(message, "Tokens-Used: in=10 out=5", 1)
        self.assertTrailerCount(message, "Tool-Calls: 1", 1)


if __name__ == "__main__":
    unittest.main()
