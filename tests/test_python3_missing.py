"""훅이 실행되는 시점의 PATH에 python3이 없을 때의 동작을 본다(구 robustness-python-path.bats).

GF-113, decision-16: sh 시절에는 없던 실패 모드라 "sh/Python 동일성 재검증"이 아니라
신규 동작 검증이다. 훅마다 결과가 비대칭이라는 README의 서술(커밋 객체를 만들기 전에
도는 훅은 커밋 차단, post-commit은 트레일러 조용한 누락)이 실제로 그런지 확인하는 것이
목적이다.

python3은 **자식 프로세스의 환경변수에서만** 지운다 — 러너 자신은 계속 자기 python3로
돌아간다(GF-124 AC #7). bats 판은 PATH를 셸 변수로 다뤄 같은 효과를 냈지만, 러너와
피험체가 같은 셸 상태를 공유해 실수로 새어나갈 여지가 있었다.
"""

import unittest

from isolated_repo import IsolatedRepoTestCase


class Python3MissingTest(IsolatedRepoTestCase):
    def setUp(self):
        super().setUp()
        # path_without()이 "python3만 정확히 가려졌고 git은 살아 있다"를 이미 단언한다.
        self.shadow_path = self.path_without("python3")
        self.no_python = {"PATH": str(self.shadow_path)}

    def use_hooks_without(self, *hooks):
        """특정 훅만 남긴 hooks/ 사본으로 core.hooksPath를 돌린다.

        git은 앞선 훅이 실패하면 뒤의 훅을 아예 실행하지 않으므로, 검증하려는 훅보다
        앞서 도는 훅을 전부 지워야 그 훅이 실제 검증 대상이 된다. 실행 순서는
        prepare-commit-msg → post-commit이다 — GF-126에서 pre-commit이 삭제돼 맨 앞이
        prepare-commit-msg가 됐고, GF-127에서 commit-msg가 삭제됐다.
        """
        trimmed = self.copy_hooks(*hooks)
        self.git_ok("config", "core.hooksPath", trimmed)
        return trimmed

    def baseline_commit(self):
        self.write("base.txt", "base\n")
        self.git_ok("add", "base.txt")
        self.commit_ok("[feat] baseline commit")
        return self.head_hash()

    # ── prepare-commit-msg: 커밋이 실제로 막힌다 ──────────────────────

    def test_prepare_commit_msg가_실패해_커밋_객체가_안_만들어진다(self):
        """[GF-113] python3이 없으면 prepare-commit-msg가 실패해 커밋 객체가 만들어지지 않는다

        GF-126까지는 이 자리에서 pre-commit이 먼저 실패했다. pre-commit이 삭제돼
        맨 앞 훅이 prepare-commit-msg로 바뀌었을 뿐, "커밋 객체가 만들어지지 않는다"는
        단언은 그대로다.
        """
        before = self.baseline_commit()

        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")
        result = self.commit("[feat] blocked by missing python3", env=self.no_python)
        self.assertRejected(result)
        self.assertIn("python3", result.output)

        # 종료 코드만 보면 안 된다 — 커밋 객체가 정말 안 생겼는지까지 확인한다.
        self.assertEqual(before, self.head_hash())
        self.assertEqual(1, self.commit_count())

    # ── post-commit: 커밋은 남고 트레일러만 조용히 빠진다 ────────────

    def test_post_commit만_실패해_트레일러가_누락된다(self):
        """[GF-113] python3이 없으면 post-commit만 실패해 커밋은 남고 트레일러가 누락된다"""
        self.use_hooks_without("prepare-commit-msg")

        # 같은 설정에서 python3이 보이면 트레일러가 붙는다는 것부터 확인한다 — 이게
        # 없으면 아래 누락이 python3 부재 때문인지 훅 연결이 애초에 안 된 탓인지
        # 구분할 수 없다.
        self.baseline_commit()
        self.assertTrailerCount(self.head_message(), "Signed-off-by:", 1)

        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")
        result = self.commit("[feat] trailerless commit", env=self.no_python)

        # --no-verify도 아니고 에러도 아니다 — 커밋은 평범하게 성공한 것처럼 보인다.
        self.assertAccepted(result)
        self.assertEqual(2, self.commit_count())
        self.assertEqual("[feat] trailerless commit", self.head_subject())

        message = self.head_message()
        self.assertTrailerKeyAbsent(message, "Signed-off-by")
        self.assertTrailerKeyAbsent(message, "Hooks-Commit")
        self.assertTrailerKeyAbsent(message, "Task-Id")


if __name__ == "__main__":
    unittest.main()
