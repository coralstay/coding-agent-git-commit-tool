"""훅이 실행되는 시점의 PATH에 python3이 없을 때의 동작을 본다(구 robustness-python-path.bats).

GF-113, decision-16: sh 시절에는 없던 실패 모드라 "sh/Python 동일성 재검증"이 아니라
신규 동작 검증이다. 커밋 객체를 만들기 전에 도는 훅은 python3이 없으면 커밋을 막는다는
것을 확인한다. GF-128 전에는 post-commit이 실패해 커밋은 남고 트레일러만 조용히 빠지는
비대칭 경로도 여기서 고정했지만, post-commit이 삭제되고 트레일러 삽입이
prepare-commit-msg로 옮겨와 그 경로가 없어졌다 — 이제 python3 부재는 언제나 드러나는
실패다(decision-18 "대가와 한계").

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


if __name__ == "__main__":
    unittest.main()
