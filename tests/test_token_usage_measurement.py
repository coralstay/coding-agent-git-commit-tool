"""Tokens-Used/Tool-Calls 측정을 본다(decision-5 확장, GF-96/GF-97/GF-112/GF-139/GF-129).

구 robustness-post-commit.bats의 토큰 측정 케이스에서 출발했다. 값은 Claude Code 세션
트랜스크립트(JSONL)와 서브에이전트 트랜스크립트에서 얻는다. 측정할 수 없는 경우에도
조용히 생략하지 않고 unavailable (사유)로 명시하는 것이 GF-97이 고정한 동작이다.

GF-129(decision-27)에서 의미가 바뀌었다. 예전에는 .git/.gitformat-token-cursor에 "이미
읽은 줄 수"를 두고 직전 커밋 이후 구간 전체(델타)를 더했다. 지금은 세션 전체에서 이
커밋이 바꾼 파일을 건드린 응답만 골라(귀속) 그 usage를 `in=<입력> out=<출력>`으로 남기고,
귀속한 응답 키를 .git/.gitformat-token-attributed에 적어 한 응답이 두 커밋에 들어가지
않게 한다. 델타·커서를 전제로 하던 GF-96/GF-139 테스트는 같은 관심사(중복 계상 방지,
세션 변경)를 새 의미로 다시 쓴 것이다.

GF-111에서 트랜스크립트 파싱이 jq 서브프로세스에서 json.loads()로 바뀌어 jq 의존성이
사라졌다 — "jq가 없으면 skip"하던 가드가 없으므로 이 케이스들은 모든 환경에서 실제로
실행된다.
"""

import os
import unittest

from isolated_repo import IsolatedRepoTestCase

RECORD_NAME = ".gitformat-token-attributed"
OLD_CURSOR_NAME = ".gitformat-token-cursor"
NO_ATTRIBUTED_TOKENS = "Tokens-Used: in=0 out=0 (no-attributed-turn)"
NO_ATTRIBUTED_CALLS = "Tool-Calls: 0 (no-attributed-turn)"


def tool_use(name, **tool_input):
    return {"type": "tool_use", "name": name, "input": tool_input}


def edit(path):
    return tool_use("Edit", file_path=str(path))


def bash(command):
    return tool_use("Bash", command=command)


TEXT_BLOCK = {"type": "text", "text": "hi"}


def response(
    request_id,
    message_id,
    blocks,
    input_tokens=0,
    output_tokens=0,
    cache_creation=0,
    cache_read=0,
):
    """API 응답 하나를 실제 트랜스크립트 모양(content 블록마다 한 줄)으로 만든다.

    같은 응답의 줄들은 최상위 requestId와 message.id를 공유하고 usage도 똑같이
    반복하며, content만 블록별로 다르다(GF-139 실측). 줄 목록을 돌려준다.
    """
    usage = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cache_creation_input_tokens": cache_creation,
        "cache_read_input_tokens": cache_read,
    }
    lines = []
    for block in blocks:
        line = {
            "type": "assistant",
            "message": {"usage": dict(usage), "content": [block]},
        }
        if request_id is not None:
            line["requestId"] = request_id
        if message_id is not None:
            line["message"]["id"] = message_id
        lines.append(line)
    return lines


class TokenUsageMeasurementTest(IsolatedRepoTestCase):
    def record_lines(self):
        return self.git_dir_file(RECORD_NAME).read_text(encoding="utf-8").splitlines()

    def stage(self, *relpaths):
        for relpath in relpaths:
            self.write(relpath, f"{relpath}\n")
        self.git_ok("add", *relpaths)

    def commit_ai(self, message, home, **kwargs):
        self.assertAccepted(self.commit(message, env=self.claude_env(home, **kwargs)))
        return self.head_message()

    # ── 귀속 판정 ────────────────────────────────────────────────

    def test_커밋한_파일을_건드린_응답만_합산한다(self):
        """[GF-129] 커밋한 파일을 건드린 응답의 usage만 더하고, 다른 파일만 건드린 응답은 뺀다"""
        home = self.fake_home()
        self.write_transcript(
            home,
            response("req-1", "msg-1", [edit(self.repo / "a.txt")], 10, 5)
            + response(
                "req-2", "msg-2", [tool_use("Read", file_path="other.txt")], 1000, 500
            )
            + response("req-3", "msg-3", [TEXT_BLOCK], 2000, 900)
            + [{"type": "user", "message": {"content": "hello"}}],
        )
        self.stage("a.txt")
        message = self.commit_ai("[feat] attribute edited file", home)
        self.assertTrailerCount(message, "Tokens-Used: in=10 out=5", 1)
        self.assertTrailerCount(message, "Tool-Calls: 1", 1)
        self.assertEqual(["fake-session", "req-1 msg-1"], self.record_lines())

    def test_in은_입력과_캐시_토큰의_합이고_out은_출력이다(self):
        """[GF-129] in=input+cache_creation+cache_read, out=output_tokens 형식으로 남긴다"""
        home = self.fake_home()
        self.write_transcript(
            home,
            response(
                "req-1",
                "msg-1",
                [edit("a.txt")],
                input_tokens=3,
                output_tokens=7,
                cache_creation=100,
                cache_read=2000,
            ),
        )
        self.stage("a.txt")
        message = self.commit_ai("[feat] in out format", home)
        self.assertTrailerCount(message, "Tokens-Used: in=2103 out=7", 1)
        self.assertNotIn("delta", message)

    def test_같은_응답의_여러_줄은_usage를_한_번만_더하고_tool_use는_모두_모은다(self):
        """[GF-139/GF-129] 같은 (requestId, message.id) 줄들은 usage를 한 번만 더하고, 귀속 판정과 Tool-Calls는 모든 줄의 tool_use를 본다"""
        home = self.fake_home()
        # 귀속 근거(Edit a.txt)가 첫 줄이 아니라 셋째 줄에 있다 — 첫 줄만 보면 놓친다.
        self.write_transcript(
            home,
            response(
                "req-1",
                "msg-1",
                [TEXT_BLOCK, bash("ls"), edit("a.txt"), bash("cat a.txt")],
                100,
                10,
            ),
        )
        self.stage("a.txt")
        message = self.commit_ai("[feat] dedup response lines", home)
        self.assertTrailerCount(message, "Tokens-Used: in=100 out=10", 1)
        # 대상 경로를 건드린 블록(Edit a.txt, Bash cat a.txt)만 센다 - ls는 빠진다.
        self.assertTrailerCount(message, "Tool-Calls: 2", 1)

    def test_실측_0은_no_attributed_turn과_구별된다(self):
        """[GF-97/GF-129] 귀속된 응답의 usage가 정말 0이면 사유 없이 in=0 out=0으로 남긴다"""
        home = self.fake_home()
        self.write_transcript(home, response("req-1", "msg-1", [edit("a.txt")], 0, 0))
        self.stage("a.txt")
        message = self.commit_ai("[feat] genuine zero tokens", home)
        self.assertTrailerCount(message, "Tokens-Used: in=0 out=0", 1)
        self.assertTrailerCount(message, "Tool-Calls: 1", 1)
        self.assertNotIn("no-attributed-turn", message)
        self.assertNotIn("unavailable", message)

    def test_귀속된_응답이_없으면_no_attributed_turn을_남긴다(self):
        """[GF-129] 어떤 응답도 커밋 파일을 건드리지 않았으면 in=0 out=0 (no-attributed-turn)이다"""
        home = self.fake_home()
        self.write_transcript(
            home,
            response("req-1", "msg-1", [tool_use("Read", file_path="other.txt")], 50, 5)
            + response("req-2", "msg-2", [TEXT_BLOCK], 60, 6),
        )
        self.stage("a.txt")
        message = self.commit_ai("[feat] nothing attributed", home)
        self.assertTrailerCount(message, NO_ATTRIBUTED_TOKENS, 1)
        self.assertTrailerCount(message, NO_ATTRIBUTED_CALLS, 1)
        self.assertEqual(["fake-session"], self.record_lines())

    # ── 경로 정규화 ──────────────────────────────────────────────

    def test_절대경로와_심볼릭_링크_경로를_저장소_상대경로로_정규화한다(self):
        """[GF-129] file_path가 절대경로이거나 심볼릭 링크(/tmp→/private/tmp 같은)를 거쳐도 저장소 상대경로로 정규화해 일치시킨다"""
        home = self.fake_home()
        link_parent = self.temp_dir(prefix="gitformat-link-")
        link = link_parent / "repo-link"
        os.symlink(self.repo, link)
        self.write_transcript(
            home,
            response("req-1", "msg-1", [edit(self.repo / "sub" / "a.txt")], 1, 1)
            + response("req-2", "msg-2", [edit(link / "sub" / "b.txt")], 10, 10)
            + response(
                "req-3",
                "msg-3",
                [tool_use("NotebookEdit", notebook_path="sub/c.ipynb")],
                100,
                100,
            )
            # 이름만 같은 다른 위치의 파일은 귀속되지 않는다.
            + response(
                "req-4", "msg-4", [edit(link_parent / "sub" / "a.txt")], 1000, 1000
            ),
        )
        self.stage("sub/a.txt", "sub/b.txt", "sub/c.ipynb")
        message = self.commit_ai("[feat] normalize paths", home)
        self.assertTrailerCount(message, "Tokens-Used: in=111 out=111", 1)
        self.assertTrailerCount(message, "Tool-Calls: 3", 1)

    def test_Bash는_저장소_상대경로가_든_명령만_귀속한다(self):
        """[GF-129] Bash 명령은 저장소 상대경로(또는 절대경로)를 담을 때만 귀속하고, 하위 경로 파일의 파일명만으로는 매칭하지 않는다"""
        home = self.fake_home()
        self.write_transcript(
            home,
            response("req-1", "msg-1", [bash("ruff check hooks/post-commit")], 1, 1)
            + response(
                "req-2", "msg-2", [bash(f"cat {self.repo}/hooks/post-commit")], 10, 10
            )
            # 파일명만: cd 후 상대 이름으로 접근해도 귀속하지 않는다(AC#4).
            + response(
                "req-3", "msg-3", [bash("cd hooks && cat post-commit")], 100, 100
            )
            # 앞뒤로 다른 글자가 붙은 경로는 다른 파일이다.
            + response(
                "req-4",
                "msg-4",
                [bash("cat myhooks/post-commit hooks/post-commit-old")],
                1000,
                1000,
            ),
        )
        self.stage("hooks/post-commit")
        message = self.commit_ai("[feat] bash path matching", home)
        self.assertTrailerCount(message, "Tokens-Used: in=11 out=11", 1)
        self.assertTrailerCount(message, "Tool-Calls: 2", 1)

    def test_저장소_최상위_파일은_경계로_구분된_파일명으로_매칭한다(self):
        """[GF-129] 최상위 파일은 경로가 곧 파일명이라 경계로 구분된 이름을 받되, 하위 디렉터리의 같은 이름이나 더 긴 이름은 받지 않는다"""
        home = self.fake_home()
        self.write_transcript(
            home,
            response("req-1", "msg-1", [bash("echo hi > a.txt")], 1, 1)
            + response(
                "req-2", "msg-2", [bash("sed -i '' 's/x/y/' \"./a.txt\"")], 10, 10
            )
            + response("req-3", "msg-3", [bash("cat sub/a.txt")], 100, 100)
            + response("req-4", "msg-4", [bash("cat a.txt.bak ba.txt")], 1000, 1000),
        )
        self.stage("a.txt")
        message = self.commit_ai("[feat] root file matching", home)
        self.assertTrailerCount(message, "Tokens-Used: in=11 out=11", 1)
        self.assertTrailerCount(message, "Tool-Calls: 2", 1)

    # ── 한 응답은 한 커밋에만 ─────────────────────────────────────

    def test_한_응답은_두_커밋에_중복_계상되지_않는다(self):
        """[GF-129] 두 파일을 건드린 응답은 먼저 커밋된 쪽에만 귀속되고 다음 커밋에서 다시 세지 않는다"""
        home = self.fake_home()
        self.write_transcript(
            home, response("req-1", "msg-1", [edit("a.txt"), edit("b.txt")], 100, 10)
        )
        self.stage("a.txt")
        message = self.commit_ai("[feat] first of two files", home)
        self.assertTrailerCount(message, "Tokens-Used: in=100 out=10", 1)

        self.stage("b.txt")
        message = self.commit_ai("[feat] second of two files", home)
        self.assertTrailerCount(message, NO_ATTRIBUTED_TOKENS, 1)
        self.assertTrailerCount(message, NO_ATTRIBUTED_CALLS, 1)

    def test_커밋_뒤에_이어_기록된_같은_응답의_줄도_다시_세지_않는다(self):
        """[GF-139/GF-129] 응답 하나의 줄이 커밋 앞뒤로 나뉘어 기록돼도 응답 키로 기억해 다음 커밋에 다시 넣지 않는다"""
        home = self.fake_home()
        self.write_transcript(
            home, response("req-1", "msg-1", [edit("a.txt")], 100, 10)
        )
        self.stage("a.txt")
        self.commit_ai("[feat] straddle commit one", home)

        self.write_transcript(
            home,
            response("req-1", "msg-1", [edit("b.txt")], 100, 10)
            + response("req-2", "msg-2", [edit("b.txt")], 5, 1),
        )
        self.stage("b.txt")
        message = self.commit_ai("[feat] straddle commit two", home)
        self.assertTrailerCount(message, "Tokens-Used: in=5 out=1", 1)
        self.assertTrailerCount(message, "Tool-Calls: 1", 1)
        self.assertEqual(
            ["fake-session", "req-1 msg-1", "req-2 msg-2"], self.record_lines()
        )

    def test_a를_고치고_b를_먼저_커밋해도_a의_응답은_뒤_커밋에_귀속된다(self):
        """[GF-129] a 수정 → b 커밋 → a 커밋 순서에서도 a를 고친 응답이 a 커밋에 들어간다(구간이 아니라 세션 전체를 본다)"""
        home = self.fake_home()
        self.write_transcript(
            home,
            response("req-a", "msg-a", [edit("a.txt")], 300, 30)
            + response("req-b", "msg-b", [edit("b.txt")], 20, 2),
        )
        self.stage("b.txt")
        message = self.commit_ai("[feat] commit b first", home)
        self.assertTrailerCount(message, "Tokens-Used: in=20 out=2", 1)

        self.stage("a.txt")
        message = self.commit_ai("[feat] commit a later", home)
        self.assertTrailerCount(message, "Tokens-Used: in=300 out=30", 1)
        self.assertTrailerCount(message, "Tool-Calls: 1", 1)

    def test_서브에이전트_트랜스크립트의_응답도_귀속한다(self):
        """[GF-129] <세션>/subagents/*.jsonl의 응답도 같은 규칙으로 귀속해 더한다"""
        home = self.fake_home()
        self.write_transcript(home, response("req-1", "msg-1", [edit("a.txt")], 10, 1))
        self.write_subagent_transcript(
            home,
            response("req-s1", "msg-s1", [edit("a.txt"), bash("cat a.txt")], 200, 20)
            + response("req-s2", "msg-s2", [edit("other.txt")], 9000, 900),
        )
        self.stage("a.txt")
        message = self.commit_ai("[feat] subagent attribution", home)
        self.assertTrailerCount(message, "Tokens-Used: in=210 out=21", 1)
        self.assertTrailerCount(message, "Tool-Calls: 3", 1)

    def test_세션이_바뀌면_귀속_기록을_새로_시작한다(self):
        """[GF-139/GF-129] 기록 파일의 세션 ID가 지금 세션과 다르면 이전 기록을 버리고 새로 시작한다"""
        home = self.fake_home()
        self.write_transcript(
            home, response("req-1", "msg-1", [edit("a.txt")], 10, 1), session_id="old"
        )
        self.stage("a.txt")
        self.commit_ai("[feat] old session commit", home, session_id="old")
        self.assertEqual(["old", "req-1 msg-1"], self.record_lines())

        # 같은 응답 키가 새 세션에 다시 나와도(키는 세션 사이에 보장된 유일값이 아니다)
        # 이전 세션의 기록 때문에 빠지면 안 된다.
        self.write_transcript(
            home, response("req-1", "msg-1", [edit("b.txt")], 7, 3), session_id="new"
        )
        self.stage("b.txt")
        message = self.commit_ai("[feat] new session commit", home, session_id="new")
        self.assertTrailerCount(message, "Tokens-Used: in=7 out=3", 1)
        self.assertEqual(["new", "req-1 msg-1"], self.record_lines())

    def test_id가_없는_줄은_각자_하나의_응답이고_파일명과_줄_번호로_기억한다(self):
        """[GF-139/GF-129] requestId나 message.id가 없는 줄은 줄마다 별개 응답으로 세고, '<파일>:<줄 번호>' 키로 기록해 다시 세지 않는다"""
        home = self.fake_home()
        self.write_transcript(
            home,
            response(None, "msg-1", [edit("a.txt")], 7, 3)
            + response("req-1", None, [edit("a.txt")], 7, 3)
            + response(None, None, [edit("a.txt")], 7, 3),
        )
        self.stage("a.txt")
        message = self.commit_ai("[feat] lines without ids", home)
        self.assertTrailerCount(message, "Tokens-Used: in=21 out=9", 1)
        self.assertEqual(
            [
                "fake-session",
                "fake-session.jsonl:1",
                "fake-session.jsonl:2",
                "fake-session.jsonl:3",
            ],
            self.record_lines(),
        )

        self.write("a.txt", "changed\n")
        self.git_ok("add", "a.txt")
        message = self.commit_ai("[feat] lines without ids again", home)
        self.assertTrailerCount(message, NO_ATTRIBUTED_TOKENS, 1)

    # ── 실패 경로 ────────────────────────────────────────────────

    def test_깨진_줄이_있으면_배치_전체가_실패하고_기록은_그대로다(self):
        """[GF-112/GF-129] 트랜스크립트에 깨진 줄이 하나라도 있으면 unavailable (transcript-parse-failed)이고 귀속 기록은 바뀌지 않는다"""
        home = self.fake_home()
        self.write_transcript(home, response("req-1", "msg-1", [edit("a.txt")], 10, 5))
        self.stage("a.txt")
        self.commit_ai("[feat] parse failure baseline commit", home)
        before = self.record_lines()

        # 정상 응답과 깨진 줄을 함께 넣는다 — 깨진 줄만 건너뛰고 나머지를 집계하면
        # "일부만 집계된 값"이 정상값인 척 기록되므로 배치 전체가 실패해야 한다
        # (GF-111 AC #4가 고정한 동작).
        self.write_transcript(
            home,
            response("req-2", "msg-2", [edit("b.txt")], 7, 3)
            + ["{ this line is not valid json"],
        )
        self.stage("b.txt")
        message = self.commit_ai("[feat] parse failure commit", home)
        self.assertTrailerCount(
            message, "Tokens-Used: unavailable (transcript-parse-failed)", 1
        )
        self.assertTrailerCount(
            message, "Tool-Calls: unavailable (transcript-parse-failed)", 1
        )
        self.assertEqual(before, self.record_lines())

    def test_서브에이전트_트랜스크립트가_깨져도_배치_전체가_실패한다(self):
        """[GF-129] 서브에이전트 트랜스크립트의 깨진 줄도 transcript-parse-failed로 배치 전체를 실패시킨다"""
        home = self.fake_home()
        self.write_transcript(home, response("req-1", "msg-1", [edit("a.txt")], 10, 5))
        self.write_subagent_transcript(home, ["{ broken"])
        self.stage("a.txt")
        message = self.commit_ai("[feat] broken subagent transcript", home)
        self.assertTrailerCount(
            message, "Tokens-Used: unavailable (transcript-parse-failed)", 1
        )
        self.assertFalse(self.git_dir_file(RECORD_NAME).exists())

    def test_트랜스크립트_파일이_없으면_사유가_명시된다(self):
        """[GF-97] 트랜스크립트 파일이 없으면 Tokens-Used/Tool-Calls가 unavailable (transcript-not-found)로 명시된다"""
        home = self.fake_home()
        self.stage("a.txt")
        message = self.commit_ai(
            "[feat] no transcript file", home, session_id="nonexistent-session"
        )
        self.assertTrailerCount(
            message, "Tokens-Used: unavailable (transcript-not-found)", 1
        )
        self.assertTrailerCount(
            message, "Tool-Calls: unavailable (transcript-not-found)", 1
        )
        self.assertFalse(self.git_dir_file(RECORD_NAME).exists())

    def test_claude_code_외_도구는_no_usage_channel로_명시된다(self):
        """[GF-97] claude-code 외 AI 도구가 감지되면 unavailable (no-usage-channel)로 명시된다"""
        self.stage("a.txt")
        # prepare-commit-msg의 AI-Model 게이트(decision-5)는 claude-code 외 AI 도구가 감지되면
        # gitformat.aiModel이 설정돼 있을 것을 요구한다 — 이 테스트의 관심사는 그
        # 게이트 통과 이후 post-commit의 분기이므로 먼저 채워둔다.
        self.git_ok("config", "gitformat.aiModel", "gpt-5")
        self.assertAccepted(
            self.commit("[feat] other ai tool", env={"AI_AGENT": "other-tool_1-0"})
        )
        message = self.head_message()
        self.assertTrailerCount(message, "AI-Tool: other-tool", 1)
        self.assertTrailerCount(
            message, "Tokens-Used: unavailable (no-usage-channel)", 1
        )
        self.assertTrailerCount(
            message, "Tool-Calls: unavailable (no-usage-channel)", 1
        )

    def test_예전_델타_커서_파일은_쓰지_않고_지운다(self):
        """[GF-129] 예전 .gitformat-token-cursor는 값에 영향을 주지 않고, 측정에 성공하면 지워진다"""
        home = self.fake_home()
        self.write_transcript(home, response("req-1", "msg-1", [edit("a.txt")], 10, 5))
        # 예전 커서가 "이미 1줄 읽었음"이라고 해도 그 응답은 아직 귀속된 적이 없다.
        self.git_dir_file(OLD_CURSOR_NAME).write_text(
            "fake-session 1", encoding="utf-8"
        )
        self.stage("a.txt")
        message = self.commit_ai("[feat] legacy cursor ignored", home)
        self.assertTrailerCount(message, "Tokens-Used: in=10 out=5", 1)
        self.assertFalse(self.git_dir_file(OLD_CURSOR_NAME).exists())


if __name__ == "__main__":
    unittest.main()
