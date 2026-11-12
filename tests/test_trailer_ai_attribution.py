# ---
# title: test_trailer_ai_attribution
# description: AI 도구 귀속 트레일러 AI-Agent의 생성과 fail-open 동작을 검증하는 테스트
# authors: [coralstay]
# license: AGPL-3.0-only
# status: draft
# created_date: '2026-11-06'
# updated_date: '2026-11-06'
# ---
"""AI 도구 귀속 트레일러 AI-Agent를 본다(decision-5, decision-19, GF-128).

구 robustness-post-commit.bats(GF-25, GF-97, GF-98)의 결함주입·슬러그 케이스에서
출발했다. GF-128에서 AI-Tool/AI-Tool-Version/AI-Model이 `AI-Agent: <도구>/<버전>
(<모델>)` 한 줄로 합쳐졌다. 모델은 Claude Code 세션 트랜스크립트에서 읽으므로,
트랜스크립트를 못 읽는 상황(JSON 손상, HOME 이상값)에서도 커밋을 막지 않는 fail-open이
의도된 동작이다 — 다만 예전처럼 줄을 생략하지 않고 model-unavailable로 남긴다(AC #6).
"""

import unittest

from isolated_repo import IsolatedRepoTestCase


class TrailerAiAttributionTest(IsolatedRepoTestCase):
    def test_트랜스크립트_JSON이_깨지면_모델이_model_unavailable이다(self):
        """[결함주입/AC #6] 트랜스크립트 JSON이 깨져도 커밋은 막히지 않고 AI-Agent의 모델 자리가 model-unavailable이 된다"""
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
        self.assertTrailerCount(
            message, "AI-Agent: claude-code/2.1.0 (model-unavailable)", 1  # ---- 1
        )
        self.assertTrailerCount(message, "AI-Agent:", 1)

    def test_HOME이_존재하지_않아도_커밋은_막히지_않는다(self):
        """[결함주입] HOME이 존재하지 않는 경로여도 커밋은 막히지 않는다"""
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")
        missing_home = self.repo / "nonexistent-gitformat-home"
        self.assertAccepted(
            self.commit("[feat] broken HOME", env=self.claude_env(missing_home))  # ---- 2
        )

    def test_사람_커밋에는_AI_트레일러가_전혀_붙지_않는다(self):
        """[GF-97] 사람 커밋(AI 도구 미감지)에는 AI-Agent가 붙지 않는다(Tokens-Used/Tool-Calls는 GF-146#3 이후 어떤 커밋에도 붙지 않는다)"""
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")
        self.assertAccepted(self.commit("[feat] human commit no ai"))  # ---- 3
        message = self.head_message()
        self.assertTrailerKeyAbsent(message, "AI-Agent")
        self.assertTrailerKeyAbsent(message, "Tokens-Used")
        self.assertTrailerKeyAbsent(message, "Tool-Calls")

    def test_밑줄과_점이_든_경로에서도_트랜스크립트를_찾는다(self):
        """[GF-98/GF-146#3] 저장소 경로에 밑줄/점이 있어도 Claude Code 실제 슬러그 규칙으로 트랜스크립트를 찾아 AI-Agent의 모델이 채워지고, Tokens-Used/Tool-Calls는 붙지 않는다"""
        nested = self.repo / "repo_with.dot_and_underscore"  # ---- 4
        self.make_repo(path=nested)

        home = self.fake_home()
        self.write_transcript(
            home,
            [
                {
                    "type": "assistant",
                    "message": {
                        "model": "claude-slug-fix-test",
                        "usage": {"input_tokens": 10, "output_tokens": 5},  # ---- 5
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
        self.assertTrailerCount(
            message, "AI-Agent: claude-code/2.1.0 (claude-slug-fix-test)", 1
        )
        self.assertTrailerKeyAbsent(message, "Tokens-Used")  # ---- 6
        self.assertTrailerKeyAbsent(message, "Tool-Calls")

    # ── AI-Agent 조립과 축약(AC #5, #6) ─────────────────────────────

    def test_예전_AI_트레일러_세_종류는_붙지_않는다(self):
        """[GF-128 AC #5] AI-Tool/AI-Tool-Version/AI-Model은 더 이상 붙지 않는다"""
        home = self.fake_home()
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")
        self.assertAccepted(self.commit("[feat] merged agent line", env=self.claude_env(home)))
        message = self.head_message()
        for key in ("AI-Tool", "AI-Tool-Version", "AI-Model"):
            self.assertTrailerKeyAbsent(message, key)
        self.assertTrailerCount(message, "AI-Agent:", 1)

    def test_버전이_없으면_version_unavailable로_남긴다(self):
        """[GF-128 AC #6] AI_AGENT에 버전 필드가 없어도 AI-Agent 줄은 version-unavailable로 남는다"""
        home = self.fake_home()
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")
        env = {"HOME": str(home), "AI_AGENT": "claude-code"}
        self.assertAccepted(self.commit("[feat] no version field", env=env))
        self.assertTrailerCount(  # ---- 7
            self.head_message(),
            "AI-Agent: claude-code/version-unavailable (model-unavailable)",
            1,
        )

    def test_claude_code_외_도구는_gitformat_aiModel을_모델로_쓴다(self):
        """[GF-128 AC #5] claude-code 외 도구는 게이트가 검증한 gitformat.aiModel이 모델 자리에 들어간다"""
        self.git_ok("config", "gitformat.aiModel", "gpt-5")
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")
        self.assertAccepted(
            self.commit("[feat] other agent", env={"AI_AGENT": "other-tool_1-2-3_agent"})
        )
        message = self.head_message()
        self.assertTrailerCount(message, "AI-Agent: other-tool/1.2.3 (gpt-5)", 1)
        self.assertTrailerKeyAbsent(message, "Co-Authored-By")  # ---- 8


if __name__ == "__main__":
    unittest.main()


# ======== 노트 ========
# 1 트랜스크립트가 깨져도 model-unavailable로 남김
#   설명: 모델은 Claude Code 세션 트랜스크립트에서 읽는다. 트랜스크립트를 못 읽는 상황(JSON 손상, HOME 이상값)에서도 커밋을 막지 않는
#   fail-open이 의도된 동작이다. 다만 예전처럼 줄을 생략하지 않고 model-unavailable로 남긴다.
#   관련: decision-5, decision-19, GF-128 AC #6
#   개념: fail-open(의도된)
# 2 HOME이 없어도 커밋은 막히지 않음
#   설명: HOME이 존재하지 않는 경로여도 AI 귀속 때문에 커밋이 막히면 안 된다. 결함을 주입해 fail-open을 고정한다.
#   관련: GF-25
#   개념: 결함 주입
# 3 사람 커밋에는 AI 트레일러가 전혀 붙지 않음
#   설명: AI_AGENT/CLAUDE_CODE_SESSION_ID는 헬퍼가 자식 환경에서 기본적으로 지운다. 이 스위트를 Claude Code로 돌리면 셸 환경에 이미
#   노출돼 있어(GF-97 검증 중 실제로 발견) 지우지 않으면 사람 커밋이 조용히 AI 커밋이 된다.
#   관련: GF-97, tests/isolated_repo.py(_STRIPPED_ENV)
#   개념: 환경 격리
# 4 저장소 최상위 이름에 밑줄/점을 넣는다
#   설명: Claude Code의 실제 규칙은 영숫자가 아닌 모든 문자를 하이픈으로 치환하는 것이다. GF-98 이전에는 훅도 테스트도 /만 치환해 둘 다 틀렸으니
#   우연히 일치하며 버그를 못 잡았다. 하위 디렉터리에 넣어도 소용없다 - git 훅은 항상 worktree 최상위를 PWD로 실행된다 - 그래서 최상위 이름 자체에
#   밑줄/점을 넣어 두 알고리즘이 반드시 갈리는 상황을 재현한다.
#   관련: GF-98, tests/isolated_repo.py(transcript_slug)
#   개념: 트랜스크립트 슬러그
# 5 usage는 있어도 모델만 읽는다
#   설명: GF-146 전이라면 측정·귀속됐을 usage다. 지금은 모델만 읽는다.
#   관련: GF-146
# 6 측정은 별도 컴포넌트로 옮겼다
#   설명: GF-146#3: 측정은 별도 컴포넌트로 옮겼으므로 Tokens-Used/Tool-Calls는 붙지 않는다.
#   관련: GF-146#3, decision-31, tests/test_format_only_trailers.py
# 7 버전·세션 ID가 없어도 줄은 남는다
#   설명: 세션 ID도 없으므로 모델도 못 구한다. 두 자리가 모두 비어도 AI-Agent 줄은 version-unavailable (model-unavailable)로
#   남는다.
#   관련: GF-128 AC #6
#   개념: 생략하지 않고 자리표시값으로 남김
# 8 Co-Authored-By는 claude-code일 때만
#   설명: claude-code 외 도구는 gitformat.aiModel이 모델 자리에 들어가지만 Co-Authored-By 트레일러는 붙지 않는다.
#   관련: GF-128 AC #5
