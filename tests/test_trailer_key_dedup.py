"""트레일러 중복 판정이 키 단위로 이뤄지는지 본다(GF-128 AC #1~#4, decision-19).

GF-128 전에는 post-commit이 `git interpret-trailers --parse` 출력에서 "키: 값"이 정확히
같은 줄을 찾아 중복을 판정했다. --parse는 메시지 맨 끝의 연속된 트레일러 블록만 보므로
빈 줄로 분리된 앞 문단의 Task-Id를 못 봤고, 값까지 비교하니 다른 값의 Co-Authored-By
옆에 정규 값이 또 붙었다(실측: 최근 40커밋 중 Co-Authored-By 40/40, Task-Id 12/40 중복).
지금은 메시지 원문의 모든 줄에서 "<키>:"로 시작하는 줄을 찾고(대소문자 무시), 있으면 그
키를 건너뛴다.
"""

import unittest

from isolated_repo import IsolatedRepoTestCase

CANONICAL_CO_AUTHOR = "Co-Authored-By: Claude <noreply@anthropic.com>"


class TrailerKeyDedupTest(IsolatedRepoTestCase):
    def setUp(self):
        super().setUp()
        self.git_ok("checkout", "-q", "-b", "GF-7-dedup")
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")

    def count_lines_with_key(self, message, key):
        prefix = f"{key.lower()}:"
        return sum(1 for line in message.split("\n") if line.lower().startswith(prefix))

    def test_빈_줄로_분리된_앞_문단의_Task_Id가_있으면_한_줄만_남는다(self):
        """[AC #3] 메시지에 빈 줄로 분리된 Task-Id 문단이 먼저 있어도 Task-Id가 한 줄만 남는다"""
        self.commit_ok(
            "[feat] 앞 문단 Task-Id\n\nTask-Id: GF-7\n\n그 뒤에 이어지는 본문 문단"
        )
        message = self.head_message()
        self.assertEqual(1, self.count_lines_with_key(message, "Task-Id"), message)
        # 다른 트레일러는 정상으로 붙는다 — 훅이 아예 안 돈 것이 아니다.
        self.assertTrailerCount(message, "Hooks-Commit:", 1)

    def test_다른_값의_Co_Authored_By는_보존되고_추가되지_않는다(self):
        """[AC #4] 메시지에 다른 값의 Co-Authored-By가 있으면 원래 값만 남는다"""
        home = self.fake_home()
        self.commit_ok(
            "[feat] 다른 공동저자\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>",
            env=self.claude_env(home),
        )
        message = self.head_message()
        self.assertEqual(
            1, self.count_lines_with_key(message, "Co-Authored-By"), message
        )
        self.assertIn(
            "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>", message
        )
        self.assertNotIn(CANONICAL_CO_AUTHOR, message)

    def test_키는_대소문자를_구분하지_않는다(self):
        """[AC #2] Co-authored-by처럼 대소문자만 다른 키도 같은 키로 보고 건너뛴다"""
        home = self.fake_home()
        self.commit_ok(
            "[feat] 소문자 키\n\nCo-authored-by: Someone <s@example.com>",
            env=self.claude_env(home),
        )
        message = self.head_message()
        self.assertEqual(
            1, self.count_lines_with_key(message, "Co-Authored-By"), message
        )
        self.assertIn("Co-authored-by: Someone <s@example.com>", message)

    def test_사람이_쓴_트레일러_값을_덮어쓰지_않는다(self):
        """[AC #2] 키가 있으면 값이 달라도 훅이 고치거나 옆에 붙이지 않는다"""
        self.commit_ok("[feat] 직접 쓴 값\n\nHooks-Commit: deadbee")
        message = self.head_message()
        self.assertEqual(1, self.count_lines_with_key(message, "Hooks-Commit"), message)
        self.assertIn("Hooks-Commit: deadbee", message)

    def test_amend_no_edit은_트레일러를_늘리지_않는다(self):
        """[AC #1/doc-13 #7] --amend --no-edit을 반복해도 트레일러가 늘어나지 않는다"""
        home = self.fake_home()
        env = self.claude_env(home)
        self.commit_ok("[feat] amend 대상", env=env)
        before = self.head_message()
        for _ in range(2):
            self.write("a.txt", "changed\n")
            self.git_ok("add", "a.txt")
            self.assertAccepted(self.git("commit", "--amend", "--no-edit", env=env))
        self.assertEqual(before, self.head_message())
        self.assertEqual(1, self.commit_count())

    def test_메시지_파일에_직접_써서_reflog에_amend가_남지_않는다(self):
        """[AC #1] 트레일러를 붙이려고 커밋을 다시 쓰지 않는다 — 커밋 하나에 reflog 한 줄이다"""
        self.commit_ok("[feat] 한 번에 최종 메시지")
        reflog = self.git_ok("reflog", "--format=%gs").stdout.splitlines()
        self.assertEqual(1, len(reflog), reflog)
        self.assertNotIn("amend", reflog[0])
        self.assertTrailerCount(self.head_message(), "Task-Id: GF-7", 1)


if __name__ == "__main__":
    unittest.main()
