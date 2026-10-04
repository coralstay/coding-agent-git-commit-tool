"""재생·병합 커밋에서 새 훅이 아무 것도 하지 않는지 본다(GF-125 AC #1, decision-18).

재생 커밋은 이미 검증된 커밋의 복제다 — 다시 도장을 찍는 것도, 다시 재는 것도 틀렸다.
구 post-commit이 cherry-pick 도중 `--amend`를 시도해 트레이스백을 냈던 문제(archive
DRAFT-18)를 원인 단계에서 없애는 장치이므로, 재생 경로에서 훅이 조용히 통과하는지를
고정해 둔다.

**남은 구 훅은 사본에서 지운 뒤 검증한다.** 구 post-commit이 cherry-pick 중에 내는
DRAFT-18 트레이스백이 아직 그대로 살아 있어, 그걸 같이 태우면 이 파일이 새 훅을 검증하는
게 아니라 아직 고치지 않은 구 훅을 검증하게 된다. GF-126에서 pre-commit이, GF-127에서
commit-msg가 삭제돼 지울 대상은 post-commit 하나만 남았고, post-commit도 삭제되는
GF-128 이후에는 이 사본 구성이 곧 실제 구성이 된다.

source 값과 진행 상태 파일은 git 2.54.0에서 실측했다(2026-09-26). cherry-pick과
rebase 재생은 `source=message`라 CHERRY_PICK_HEAD 같은 진행 상태 파일로만 잡히고,
에디터로 여는 revert와 병합 커밋은 `source=merge`로 온다 — 훅이 둘을 OR로 보는 이유다.
"""

import unittest

from isolated_repo import IsolatedRepoTestCase

# AC #1이 규정하는 진행 상태 파일. 훅은 존재 여부만 보므로 내용은 무엇이든 된다.
PROGRESS_FILES = ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REBASE_HEAD", "REVERT_HEAD")


class ReplayCommitsUntouchedTest(IsolatedRepoTestCase):
    def setUp(self):
        self.hooks_copy = self.copy_hooks("post-commit")
        self.repo = self.make_repo(hooks_path=self.hooks_copy)
        self.hook = self.hooks_copy / "prepare-commit-msg"
        self.write("base.txt", "base\n")
        self.git_ok("add", "base.txt")
        self.commit_ok("[feat] 기준 커밋")

    def current_branch(self):
        return self.git_ok("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()

    def make_editor(self, subject):
        """실제 에디터처럼 기존 내용을 보존하며 제목만 끼워넣는 GIT_EDITOR 스크립트.

        doc-15: 메시지 파일을 `>`로 덮어쓰면 훅이 넣어둔 내용이 사라져 오판하게 된다.
        """
        editor = self.temp_dir(prefix="gitformat-editor-") / "editor.sh"
        editor.write_text(
            "#!/bin/sh\n"
            'tmp="$(mktemp)"\n'
            # 제목 뒤에 빈 줄을 넣는다 — 안 넣으면 git이 원래 있던 다음 줄까지
            # 제목으로 이어 붙여 읽어(실측) 단언이 제목만 보지 못한다.
            f'printf "{subject}\\n\\n" > "$tmp"\n'
            'cat "$1" >> "$tmp"\n'
            'mv "$tmp" "$1"\n',
            encoding="utf-8",
        )
        editor.chmod(0o755)
        return editor

    def assertHookSilent(self, result):
        """재생 경로에서는 거부도, 트레이스백도, 어떤 출력도 없어야 한다."""
        self.assertAccepted(result)
        self.assertNotIn("Traceback", result.output)
        self.assertNotIn("prepare-commit-msg", result.output)

    # ── 실제 git 명령으로 재생·병합 커밋을 만든다 ────────────────────

    def test_cherry_pick이_거부되지_않는다(self):
        """[GF-125] cherry-pick 재생 커밋은 훅의 거부나 트레이스백 없이 완료된다"""
        base_branch = self.current_branch()
        # GF-127 이후 메시지 검증(브랜치 Task-Id 강제 포함)이 prepare-commit-msg에서
        # 돌므로, 준비 단계의 일반 커밋도 Task-Id가 있는 브랜치에서 만들어야 한다.
        self.git_ok("checkout", "-q", "-b", "GF-1-side")
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")
        self.commit_ok("[feat] 재생할 커밋")
        replayed = self.head_hash()
        self.git_ok("checkout", "-q", base_branch)

        self.assertHookSilent(self.git("cherry-pick", replayed))

        self.assertEqual(2, self.commit_count())
        self.assertEqual("[feat] 재생할 커밋", self.head_subject())

    def test_revert가_거부되지_않는다(self):
        """[GF-125] git revert --no-edit은 훅의 거부나 트레이스백 없이 완료된다"""
        self.assertHookSilent(self.git("revert", "--no-edit", "HEAD"))

        self.assertEqual(2, self.commit_count())
        # 충돌 없는 revert는 REVERT_HEAD가 없어 면제에 걸리지 않는다(source=message).
        # git이 만드는 이 제목은 [type][subsystem] 형식이 아니지만 GF-127에서 형식
        # 규칙의 예외로 인정했으므로 검증을 거치고도 조용히 통과한다.
        self.assertEqual('Revert "[feat] 기준 커밋"', self.head_subject())

    def test_에디터로_여는_revert도_거부되지_않는다(self):
        """[GF-125] git revert --edit은 에디터가 열려도 거부되지 않는다(source=merge)"""
        editor = self.make_editor("[revert] 에디터에서 고친 제목")

        result = self.git("revert", "--edit", "HEAD", env={"GIT_EDITOR": editor})

        # source=template이 아니라 merge로 오므로(실측) 면제가 먼저 걸린다. 에디터가
        # 관여하는데도 통과하는 유일한 경로다.
        self.assertHookSilent(result)
        self.assertEqual(2, self.commit_count())
        self.assertEqual("[revert] 에디터에서 고친 제목", self.head_subject())

    def test_병합_커밋이_거부되지_않는다(self):
        """[GF-125] 병합 커밋(source=merge, MERGE_HEAD 존재)은 거부되지 않는다"""
        base_branch = self.current_branch()
        self.git_ok("checkout", "-q", "-b", "GF-2-feature")
        self.write("feature.txt", "feature\n")
        self.git_ok("add", "feature.txt")
        self.commit_ok("[feat] 병합될 커밋")
        self.git_ok("checkout", "-q", base_branch)
        # 양쪽을 분기시켜 fast-forward가 아닌 실제 병합 커밋이 만들어지게 한다.
        self.write("main.txt", "main\n")
        self.git_ok("add", "main.txt")
        self.commit_ok("[feat] 병합하는 쪽 커밋")

        self.assertHookSilent(self.git("merge", "--no-ff", "--no-edit", "GF-2-feature"))

        # 부모가 2개인지까지 봐야 진짜 병합 커밋이 만들어진 것이 증명된다.
        parents = self.git_ok("log", "-1", "--format=%p").stdout.split()
        self.assertEqual(2, len(parents), f"병합 커밋이 아니다: {parents}")

    # ── 훅을 직접 호출해 면제 조건 하나씩 고정한다 ──────────────────

    def test_진행_상태_파일이_있으면_에디터_경로도_통과한다(self):
        """[GF-125] 면제가 거부보다 먼저 온다 — 진행 상태 파일이 있으면 template도 통과"""
        message_file = self.write("msgfile", "[feat] 재생 중 메시지\n")
        for name in PROGRESS_FILES:
            with self.subTest(progress_file=name):
                progress = self.git_dir_file(name)
                progress.write_text(self.head_hash() + "\n", encoding="utf-8")
                try:
                    # source=template은 원래 거부 대상이다. 그래도 통과해야 한다 —
                    # 실행 순서가 뒤바뀌면(거부가 면제보다 먼저) 이 단언이 깨진다.
                    result = self.python(self.hook, message_file, "template")
                finally:
                    progress.unlink()
                self.assertAccepted(result)
                self.assertEqual("", result.output, str(result))

    def test_source가_merge나_squash면_통과한다(self):
        """[GF-125] 진행 상태 파일이 없어도 source가 merge/squash면 통과한다"""
        message_file = self.write("msgfile", "Merge branch 'feature'\n")
        for source in ("merge", "squash"):
            with self.subTest(source=source):
                result = self.python(self.hook, message_file, source)
                self.assertAccepted(result)
                self.assertEqual("", result.output, str(result))


if __name__ == "__main__":
    unittest.main()
