"""브랜치명·커밋 메시지에 섞인 셸 메타문자가 실행되지 않는지 본다(구 robustness-injection.bats).

GF-27, decision-8: 표준 인증이 아니라 훅이 브랜치명/커밋 메시지를 항상 인자 배열로
다루고 셸을 거치지 않는다는 실제 코드 특성을 실증하는 네거티브 테스트.

커밋 메시지에 섞인 메타문자는 test_message_format_enforced.py가 이미 다루므로,
여기서는 브랜치명에 집중하고 커밋 메시지 쪽은 개행+메타문자 조합/non-UTF8/매우 긴
라인처럼 더 공격적인 조합만 본다 — 트레일러가 실제로 붙는 경로(Task-Id 브랜치)에서
interpret-trailers 삽입이 깨지지 않는지 함께 확인한다.

주의: git 브랜치명은 공백을 허용하지 않는다(check-ref-format). 그래서 아래 페이로드는
공백 없는 형태(예: $IFS로 공백을 대신)를 쓴다 — 셸 인젝션 페이로드에서 흔히 쓰이는
공백 우회 기법이라 오히려 더 현실적인 공격 벡터다.
"""

import unittest

from isolated_repo import IsolatedRepoTestCase


class ShellMetacharactersSafeTest(IsolatedRepoTestCase):
    def assertNotCreated(self, *names):
        for name in names:
            self.assertFalse((self.repo / name).exists(), f"{name}이 생성됐다")

    def stage_one_file(self):
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")

    # ── git이 애초에 거부하는 브랜치명 ──────────────────────────────

    def test_공백이_섞인_브랜치명은_git_자체가_거부한다(self):
        """[브랜치명] 공백이 섞인 브랜치명은 git 자체가 생성을 거부한다"""
        self.assertRejected(self.git("checkout", "-q", "-b", "GF-1 with space"))

    # ── git은 허용하지만 셸엔 위험한 브랜치명 ───────────────────────

    def test_서브셸_패턴이_섞여도_실행되지_않는다(self):
        """[브랜치명] $()+$IFS 서브셸 패턴이 섞여도 실행되지 않고 커밋이 안전하게 처리된다"""
        self.git_ok("checkout", "-q", "-b", "GF-1-$(touch${IFS}pwned-a)")
        self.stage_one_file()
        self.assertAccepted(self.commit("[feat] subshell in branch name"))
        self.assertNotCreated("pwned-a")
        self.assertTrailerCount(self.head_message(), "Task-Id: GF-1", 1)

    def test_백틱_패턴이_섞여도_실행되지_않는다(self):
        """[브랜치명] 백틱+$IFS 서브셸 패턴이 섞여도 실행되지 않는다"""
        self.git_ok("checkout", "-q", "-b", "GF-1-`touch${IFS}pwned-b`")
        self.stage_one_file()
        self.assertAccepted(self.commit("[feat] backtick in branch name"))
        self.assertNotCreated("pwned-b")

    def test_셸_연산자가_섞여도_실행되지_않는다(self):
        """[브랜치명] 세미콜론/파이프/&&가 섞여도 실행되지 않는다"""
        self.git_ok(
            "checkout",
            "-q",
            "-b",
            "GF-1-;touch-pwned-c|touch-pwned-d&&touch-pwned-e",
        )
        self.stage_one_file()
        self.assertAccepted(self.commit("[feat] shell operators in branch name"))
        self.assertNotCreated("pwned-c", "pwned-d", "pwned-e")

    # ── 커밋 메시지: 개행+메타문자 / non-UTF8 / 매우 긴 라인 ─────────

    def test_개행과_메타문자가_섞여도_트레일러_삽입이_깨지지_않는다(self):
        """[커밋메시지] 개행과 셸 메타문자가 뒤섞여도 트레일러 삽입이 깨지지 않는다"""
        self.git_ok("checkout", "-q", "-b", "GF-2-injection")
        self.stage_one_file()
        self.assertAccepted(
            self.commit(
                "[feat] 복합 페이로드\n\n$(touch pwned-f)\n`touch pwned-g`\n"
                "; touch pwned-h | touch pwned-i"
            )
        )
        self.assertNotCreated("pwned-f", "pwned-g", "pwned-h", "pwned-i")
        self.assertTrailerCount(self.head_message(), "Task-Id: GF-2", 1)

    def test_non_UTF8_바이트가_섞여도_트레일러_삽입이_깨지지_않는다(self):
        """[커밋메시지] non-UTF8 바이트가 섞여도 트레일러 삽입이 깨지지 않는다"""
        self.git_ok("checkout", "-q", "-b", "GF-3-nonutf8")
        self.stage_one_file()
        bad_msg = self.temp_dir() / "bad-message"
        bad_msg.write_bytes(b"[feat] broken \xff\xfe bytes\n")
        self.assertAccepted(self.git("commit", "-F", bad_msg))
        self.assertTrailerCount(self.head_message(), "Task-Id: GF-3", 1)

    def test_매우_긴_라인이_섞여도_트레일러_삽입이_깨지지_않는다(self):
        """[커밋메시지] 매우 긴 라인이 섞여도 트레일러 삽입이 깨지지 않는다"""
        # 이 테스트의 목적은 interpret-trailers 삽입(GF-128부터
        # prepare-commit-msg)이 매우 긴 라인 앞에서 깨지지 않는지 확인하는 것이지, GF-83의 본문 줄 길이(72자) 검증
        # 자체를 테스트하는 게 아니다. 예전에는 20000자 본문 줄을 --no-verify로
        # commit-msg를 건너뛰어 통과시켰지만, GF-127에서 검증이 --no-verify로도
        # 건너뛸 수 없는 prepare-commit-msg로 옮겨와 그 우회가 닫혔다. 그래서 72자
        # 예외를 받는 등록된 트레일러 토큰 줄(BREAKING CHANGE)로 긴 라인을 넣는다.
        self.git_ok("checkout", "-q", "-b", "GF-4-longline")
        self.stage_one_file()
        long_body = "BREAKING CHANGE: " + "y" * 20000
        self.assertAccepted(self.commit(f"[feat] 긴 본문\n\n{long_body}"))
        message = self.head_message()
        self.assertTrailerCount(message, "Task-Id: GF-4", 1)
        self.assertIn(long_body, message)


if __name__ == "__main__":
    unittest.main()
