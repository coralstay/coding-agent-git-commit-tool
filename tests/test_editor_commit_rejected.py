"""에디터로 커밋하려는 경로가 거부되는지 본다(GF-125 AC #2, decision-18).

prepare-commit-msg는 에디터가 열리기 **전에** 실행된다(doc-15 실측). 그래서 이 훅은
사람이 앞으로 타이핑할 최종 메시지를 볼 수 없고, 메시지 검증이 원리적으로 불가능하다.
decision-18은 그 경로를 아예 거부해 "통과한 커밋은 모두 검증을 거쳤다"가 성립하게
한다 — 이 파일은 그 게이트가 실제로 닫히는지, 그리고 `-m`/`-F` 경로는 열려 있는지를
본다.

에디터 시뮬레이션 주의(doc-15에 기록된 실수): GIT_EDITOR 스크립트가 메시지 파일을
`>`로 덮어쓰면 훅이 넣어둔 내용이 사라져 "훅이 동작하지 않았다"고 오판하게 된다.
실제 에디터는 파일을 열어 고치므로 시뮬레이션도 기존 내용을 보존해야 한다. 여기서는
그 위에 "에디터가 실제로 열렸는지"를 마커 파일로 남긴다 — 거부가 에디터보다 앞에서
일어났다는 것까지 확인할 수 있어야 이 테스트가 훅의 실행 시점을 검증한 셈이 된다.
"""

import unittest

from isolated_repo import IsolatedRepoTestCase


class EditorCommitRejectedTest(IsolatedRepoTestCase):
    def make_editor(self):
        """실제 에디터처럼 기존 내용을 보존하며 제목만 끼워넣는 GIT_EDITOR 스크립트.

        실행되면 마커 파일을 남긴다. 반환값은 (스크립트 경로, 마커 경로)다.
        """
        directory = self.temp_dir(prefix="gitformat-editor-")
        marker = directory / "editor-ran"
        editor = directory / "editor.sh"
        editor.write_text(
            "#!/bin/sh\n"
            f'printf "ran\\n" > "{marker}"\n'
            'tmp="$(mktemp)"\n'
            'printf "[feat] 사람이 에디터에서 타이핑한 제목\\n" > "$tmp"\n'
            "# 기존 내용(훅이 넣은 것, 주석 안내)을 보존한다 — 덮어쓰면 오판한다.\n"
            'cat "$1" >> "$tmp"\n'
            'mv "$tmp" "$1"\n',
            encoding="utf-8",
        )
        editor.chmod(0o755)
        return editor, marker

    def baseline_commit(self):
        self.write("base.txt", "base\n")
        self.git_ok("add", "base.txt")
        self.commit_ok("[feat] 기준 커밋")
        return self.head_hash()

    def test_에디터_경로_커밋은_거부된다(self):
        """[GF-125] -m 없이 커밋하면 훅이 거부하고 -m을 안내한다 (commit.template 없음)"""
        editor, marker = self.make_editor()
        before = self.baseline_commit()

        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")
        result = self.git("commit", env={"GIT_EDITOR": editor})

        self.assertRejected(result)
        self.assertIn("git commit -m", result.output)
        self.assertNotIn("Traceback", result.output)
        # 거부가 에디터보다 먼저 일어났는지까지 본다 — 에디터가 열린 뒤에 막았다면
        # 사람이 타이핑한 내용을 훅이 볼 수 있다는 뜻이고 decision-18의 전제가 틀린
        # 것이 된다.
        self.assertFalse(
            marker.exists(),
            f"에디터가 열렸다 — 훅이 그보다 먼저 막지 못했다:\n{result}",
        )
        # 종료 코드만 보면 안 된다 — 커밋 객체가 정말 안 생겼는지까지 확인한다.
        self.assertEqual(before, self.head_hash())
        self.assertEqual(1, self.commit_count())

    def test_commit_template이_설정돼_있어도_거부된다(self):
        """[GF-125 회귀] commit.template 설정 여부와 무관하게 에디터 경로가 거부된다

        source($2)로 판정하면 이 두 경우가 갈린다 - commit.template이 설정된
        저장소에서만 git이 source=template을 넘기고, 설정이 없으면 source 인자를
        아예 안 넘긴다. 그래서 source 기반 판정은 개발 기계(전역에
        commit.template이 있음)에서는 통과하고 CI에서는 실패했다. 이 테스트가
        두 조건을 모두 고정한다.
        """
        template = self.temp_dir(prefix="gitformat-tmpl-") / "template.txt"
        template.write_text("# 템플릿 안내 주석\n", encoding="utf-8")
        self.git_ok("config", "commit.template", str(template))

        editor, marker = self.make_editor()
        before = self.baseline_commit()

        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")
        result = self.git("commit", env={"GIT_EDITOR": editor})

        self.assertRejected(result)
        self.assertIn("git commit -m", result.output)
        self.assertFalse(marker.exists(), f"에디터가 열렸다:\n{result}")
        self.assertEqual(before, self.head_hash())

    def test_amend_no_edit는_통과한다(self):
        """[GF-125] --amend --no-edit은 직전 메시지가 들어 있어 통과한다"""
        self.baseline_commit()
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")

        result = self.git("commit", "--amend", "--no-edit")

        self.assertAccepted(result)
        self.assertEqual("[feat] 기준 커밋", self.head_subject())

    def test_m_옵션_커밋은_통과한다(self):
        """[GF-125] git commit -m은 그대로 통과한다(source=message)"""
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")

        result = self.commit("[feat] -m 경로는 통과한다")

        self.assertAccepted(result)
        self.assertEqual(1, self.commit_count())
        self.assertEqual("[feat] -m 경로는 통과한다", self.head_subject())

    def test_F_옵션_커밋은_통과한다(self):
        """[GF-125] git commit -F <파일>도 통과한다(source=message)"""
        message_file = self.temp_dir(prefix="gitformat-msg-") / "message.txt"
        message_file.write_text("[feat] -F 경로는 통과한다\n", encoding="utf-8")

        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")
        result = self.git("commit", "-F", message_file)

        self.assertAccepted(result)
        self.assertEqual(1, self.commit_count())
        self.assertEqual("[feat] -F 경로는 통과한다", self.head_subject())


if __name__ == "__main__":
    unittest.main()
