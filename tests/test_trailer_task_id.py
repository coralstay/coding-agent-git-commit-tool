# ---
# title: test_trailer_task_id
# description: 브랜치명에서 Task-Id 트레일러가 정확히 한 번 붙는지 검증하는 테스트
# authors: [coralstay]
# license: AGPL-3.0-only
# status: draft
# created_date: '2026-11-06'
# updated_date: '2026-11-06'
# ---
"""prepare-commit-msg가 브랜치명에서 Task-Id 트레일러를 만들어 붙이는지 본다(decision-4).

prepare-commit-msg가 이미 브랜치명의 <prefix>-<번호> 패턴을 강제했으므로(없으면 예외
브랜치가 아닌 한 커밋 자체가 거부된다 - test_branch_task_id_required.py), 여기서는
같은 패턴이 트레일러로 정확히 한 번 남는지, 예외 브랜치에서는 아예 붙지 않는지를
본다. bats 판은 부분 문자열 존재만 봤고 개수를 세지 않았다.
"""

import unittest

from isolated_repo import IsolatedRepoTestCase


class TrailerTaskIdTest(IsolatedRepoTestCase):
    def test_브랜치명의_Task_Id가_정확히_한_번_붙는다(self):
        """Task-Id 트레일러가 브랜치명에서 정확히 한 번 삽입된다"""
        self.git_ok("checkout", "-q", "-b", "GF-7-trailer")
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")
        self.assertAccepted(self.commit("[feat] task id trailer"))
        message = self.head_message()
        self.assertTrailerCount(message, "Task-Id: GF-7", 1)  # ---- 1
        self.assertTrailerCount(message, "Task-Id:", 1)

    def test_예외_브랜치에는_Task_Id가_붙지_않는다(self):
        """예외 브랜치(main)에는 Task-Id 트레일러가 붙지 않는다"""
        self.git_ok("checkout", "-q", "-B", "main")
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")
        self.assertAccepted(self.commit("[feat] exempt branch commit"))
        self.assertTrailerKeyAbsent(self.head_message(), "Task-Id")  # ---- 2


if __name__ == "__main__":
    unittest.main()


# ======== 노트 ========
# 1 Task-Id는 브랜치명에서 정확히 한 번
#   설명: 브랜치명 GF-7-trailer에서 만든 Task-Id: GF-7이 정확히 한 번 있어야 한다. bats 판은 부분 문자열 존재만 봤고 개수를 세지 않았다.
#   관련: decision-4, tests/test_branch_task_id_required.py
#   개념: 트레일러 개수 단언
# 2 예외 브랜치에는 Task-Id가 붙지 않는다
#   설명: 예외 브랜치(main)는 패턴 강제를 받지 않으므로 Task-Id 트레일러도 만들지 않는다.
#   관련: decision-4
