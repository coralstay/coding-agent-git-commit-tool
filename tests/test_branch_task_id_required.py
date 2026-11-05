"""prepare-commit-msg가 브랜치명의 Task-Id 패턴을 강제하는지 본다(decision-4).

구 robustness-commit-msg.bats(GF-23)의 브랜치 관련 케이스. <prefix>-<번호> 패턴이
없으면 예외 브랜치가 아닌 한 커밋을 거부한다. 예외 목록은 로컬 오버라이드와 내장
기본값의 합집합이어야 한다(GF-78).
"""

import unittest

from isolated_repo import IsolatedRepoTestCase


class BranchTaskIdTest(IsolatedRepoTestCase):
    def setUp(self):
        super().setUp()
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")

    # ── 경계값분석: task 번호 0·거대값, 매우 긴 브랜치명 ────────────

    def test_번호가_0이어도_통과한다(self):
        """[경계값] Task-Id 번호가 0이어도 브랜치 패턴은 통과한다"""
        self.git_ok("checkout", "-q", "-b", "GF-0-zero")
        self.assertAccepted(self.commit("[feat] zero task id"))

    def test_번호가_매우_커도_통과한다(self):
        """[경계값] Task-Id 번호가 매우 커도 브랜치 패턴은 통과한다"""
        self.git_ok("checkout", "-q", "-b", "GF-99999999999999999999-huge")
        self.assertAccepted(self.commit("[feat] huge task id"))

    def test_매우_긴_브랜치명도_패턴만_있으면_통과한다(self):
        """[경계값] 매우 긴 브랜치명도 Task-Id 패턴만 있으면 통과한다"""
        self.git_ok("checkout", "-q", "-b", "GF-1-" + "x" * 200)
        self.assertAccepted(self.commit("[feat] long branch"))

    def test_Task_Id_없는_non_exempt_브랜치는_거부된다(self):
        """[경계값] Task-Id 없는 non-exempt 브랜치는 거부된다"""
        self.git_ok("checkout", "-q", "-b", "no-task-id-here")
        self.assertRejected(self.commit("[feat] missing task id"))

    # ── branchExempt --add 시 기본 예외 유실 회귀 방지 (GF-78) ──────

    def test_add해도_기본_예외_브랜치는_유지된다(self):
        """[GF-78] branchExempt를 --add해도 기본 예외 브랜치(main)는 유지된다"""
        self.git_ok("config", "--add", "gitformat.branchExempt", "hotfix/*")
        # -B: 이미 main 브랜치일 수도(git init 기본값에 따라 다름) 있어 -b 대신
        # 강제 생성/전환으로 환경에 상관없이 동작하게 한다.
        self.git_ok("checkout", "-q", "-B", "main")
        self.assertAccepted(self.commit("[feat] main after add"))

    def test_add한_패턴도_예외로_동작한다(self):
        """[GF-78] branchExempt로 --add한 패턴도 예외로 동작한다"""
        self.git_ok("config", "--add", "gitformat.branchExempt", "hotfix/*")
        self.git_ok("checkout", "-q", "-b", "hotfix/urgent")
        self.assertAccepted(self.commit("[feat] added exempt pattern"))

    def test_add해도_Task_Id_없는_다른_브랜치는_거부된다(self):
        """[GF-78] branchExempt를 --add해도 Task-Id 없는 다른 브랜치는 여전히 거부된다"""
        self.git_ok("config", "--add", "gitformat.branchExempt", "hotfix/*")
        self.git_ok("checkout", "-q", "-b", "unrelated-branch")
        self.assertRejected(self.commit("[feat] still rejected"))


if __name__ == "__main__":
    unittest.main()
