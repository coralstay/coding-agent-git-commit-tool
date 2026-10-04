"""prepare-commit-msg가 커밋 메시지 형식·길이·Fixes·AI 모델 게이트를 강제하는지 본다.

구 robustness-commit-msg.bats(GF-23)에서 브랜치 Task-Id 강제를 뺀 나머지.
브랜치 쪽은 test_branch_task_id_required.py가 맡는다. GF-127에서 검증이 commit-msg에서
prepare-commit-msg로 옮겨오고 commit-msg는 삭제됐다 — 아래 케이스는 전부 실제
`git commit`을 태우는 블랙박스 테스트라 그대로 새 경로를 검증한다. 옮겨오며 생긴
동작(--no-verify로 우회 불가, git revert 제목 예외, 거부 시 마커 없음)은 맨 아래에 있다.

decision-8: 표준 인증이 아니라 실제 버그 이력(GF-30, GF-34, GF-35)에 근거한 실용적
테스트. GF-82에서 서브젝트가 [type][subsystem] 프리픽스로 바뀌었고, GF-83에서 제목
50자·본문 줄 72자 길이 검증이 들어왔다.
"""

import unittest

from isolated_repo import IsolatedRepoTestCase


class MessageFormatTest(IsolatedRepoTestCase):
    def setUp(self):
        super().setUp()
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")

    # ── 동등분할: type/subsystem/BREAKING CHANGE 대표값 ──────────────

    def test_유효한_type과_subsystem_없음은_통과한다(self):
        """[동등분할] 유효한 type + subsystem 없음은 통과한다"""
        self.assertAccepted(self.commit("[fix] 버그 수정"))

    def test_유효한_type과_subsystem_있음은_통과한다(self):
        """[동등분할] 유효한 type + subsystem 있음은 통과한다"""
        self.assertAccepted(self.commit("[fix][parser] 버그 수정"))

    def test_목록에_없는_type은_거부된다(self):
        """[동등분할] 목록에 없는 type은 거부된다"""
        self.assertRejected(self.commit("[wip] 진행중"))

    def test_subject의_느낌표는_더_이상_지원하지_않는다(self):
        """[동등분할] BREAKING CHANGE(subject의 !)는 더 이상 지원하지 않아 거부된다 (GF-82)"""
        self.assertRejected(self.commit("[feat!] 하위호환 깨는 변경"))

    def test_footer의_BREAKING_CHANGE는_통과한다(self):
        """[동등분할] BREAKING CHANGE(footer)는 통과한다"""
        self.assertAccepted(
            self.commit("[feat] 변경\n\nBREAKING CHANGE: 하위호환 깨짐")
        )

    # ── 경계값분석: 빈 description / 매우 긴 값 ──────────────────────

    def test_description이_비면_거부된다(self):
        """[경계값] description이 빈 문자열이면 거부된다"""
        self.assertRejected(self.commit("[feat] "))

    def test_매우_긴_subject는_길이_제한으로_거부된다(self):
        """[GF-83] 매우 긴 subject는 형식이 맞아도 길이 제한(50자)으로 거부된다"""
        self.assertRejected(self.commit("[feat] " + "x" * 5000))

    # ── 결정테이블: AI_AGENT유무 x claude-code여부 x aiModel x 화이트리스트 ──

    def test_AI_AGENT_미설정이면_게이트를_건너뛴다(self):
        """[결정테이블] AI_AGENT 미설정이면 AI-Model 게이트를 건너뛴다"""
        self.assertAccepted(self.commit("[feat] no ai agent", env={"AI_AGENT": ""}))

    def test_claude_code면_aiModel_없이도_통과한다(self):
        """[결정테이블] AI_AGENT=claude-code면 aiModel 미설정이어도 통과한다"""
        self.assertAccepted(
            self.commit("[feat] claude code agent", env={"AI_AGENT": "claude-code_2-1-0"})
        )

    def test_비_claude_도구에_aiModel_미설정이면_거부된다(self):
        """[결정테이블] 비-claude-code 도구 + aiModel 미설정이면 거부된다"""
        self.assertRejected(
            self.commit("[feat] other tool no model", env={"AI_AGENT": "other-tool_1-0"})
        )

    def test_화이트리스트에_없는_aiModel은_거부된다(self):
        """[결정테이블] 비-claude-code 도구 + aiModel 설정했지만 화이트리스트에 없으면 거부된다"""
        self.git_ok("config", "gitformat.aiModel", "not-a-real-model")
        self.assertRejected(
            self.commit("[feat] unknown model", env={"AI_AGENT": "other-tool_1-0"})
        )

    def test_화이트리스트에_있는_aiModel은_통과한다(self):
        """[결정테이블] 비-claude-code 도구 + aiModel이 화이트리스트에 있으면 통과한다"""
        self.git_ok("config", "gitformat.aiModel", "gpt-5")
        self.assertAccepted(
            self.commit("[feat] known model", env={"AI_AGENT": "other-tool_1-0"})
        )

    # ── 구문테스트: 셸 메타문자 / 개행 / 제어문자 ───────────────────

    def test_셸_메타문자가_있어도_실행되지_않는다(self):
        """[구문테스트] 커밋 메시지에 셸 메타문자가 있어도 실행되지 않고 안전하게 처리된다"""
        # subject 길이 제한(GF-83, 50자)에 걸리지 않도록 짧은 파일명을 쓴다 —
        # 이 테스트의 목적은 셸 인젝션 방지 확인이지 길이 검증이 아니다.
        self.assertAccepted(
            self.commit("[feat] $(touch p1) `touch p2`;touch p3|touch p4")
        )
        for name in ("p1", "p2", "p3", "p4"):
            self.assertFalse((self.repo / name).exists(), f"{name}이 생성됐다")

    def test_본문에_개행이_있어도_정상_처리된다(self):
        """[구문테스트] 커밋 메시지 본문에 개행이 있어도 정상 처리된다"""
        self.assertAccepted(
            self.commit("[feat] 여러줄\n\n첫 줄\n둘째 줄\n\nFooter: value")
        )

    def test_type_앞에_제어문자가_섞이면_거부된다(self):
        """[구문테스트] type 앞에 제어문자(탭)가 섞이면 거부된다"""
        self.assertRejected(self.commit("\t[feat] 탭으로 시작"))

    # ── 빈 줄 강제 / Fixes: 검증 (GF-82, 리누스 스타일) ─────────────

    def test_제목과_본문_사이에_빈_줄이_없으면_거부된다(self):
        """[GF-82] 본문이 있는데 제목과의 사이에 빈 줄이 없으면 거부된다"""
        self.assertRejected(self.commit("[feat] 제목\n본문이 빈 줄 없이 바로 이어짐"))

    def test_빈_줄로_구분된_본문은_통과한다(self):
        """[GF-82] 본문이 있고 빈 줄로 구분돼 있으면 통과한다"""
        self.assertAccepted(self.commit("[feat] 제목\n\n본문"))

    def test_Fixes가_실재하는_커밋을_가리키면_통과한다(self):
        """[GF-82] Fixes: 트레일러가 실재하는 커밋을 가리키면 통과한다"""
        self.commit_ok("[fix] baseline", "-q")
        first_hash = self.head_hash()
        self.write("a.txt", "hi\nmore\n")
        self.git_ok("add", "a.txt")
        self.assertAccepted(self.commit(f"[fix] 후속 수정\n\nFixes: {first_hash}"))

    def test_Fixes가_없는_해시를_가리키면_거부된다(self):
        """[GF-82] Fixes: 트레일러가 존재하지 않는 해시를 가리키면 거부된다"""
        self.commit_ok("[fix] baseline", "-q")
        self.write("a.txt", "hi\nmore\n")
        self.git_ok("add", "a.txt")
        self.assertRejected(
            self.commit(
                "[fix] 후속 수정\n\nFixes: 0000000000000000000000000000000000dead"
            )
        )

    def test_Fixes가_없어도_통과한다(self):
        """[GF-82] Fixes: 트레일러가 없어도 통과한다 (강제 아님)"""
        self.assertAccepted(self.commit("[fix] no fixes trailer"))

    # ── subject 길이 / 본문 줄 길이 검증 (GF-83) ────────────────────

    def test_subject가_정확히_50자면_통과한다(self):
        """[GF-83] subject가 정확히 50자면 통과한다 (경계값)"""
        self.assertAccepted(self.commit("[feat] " + "x" * 43))

    def test_subject가_51자면_거부된다(self):
        """[GF-83] subject가 51자면 거부된다 (경계값)"""
        self.assertRejected(self.commit("[feat] " + "x" * 44))

    def test_글자_수는_바이트가_아니라_코드포인트로_센다(self):
        """[GF-83] 글자 수는 바이트가 아니라 유니코드 문자 단위로 센다 - 한글 27자(67바이트)는 통과한다"""
        self.assertAccepted(self.commit("[feat] " + "가" * 20))

    def test_한글이어도_50자를_넘으면_거부된다(self):
        """[GF-83] 한글이어도 문자 수 자체가 50자를 넘으면 거부된다 (52자)"""
        self.assertRejected(self.commit("[feat] " + "가" * 45))

    def test_본문_줄이_정확히_72자면_통과한다(self):
        """[GF-83] 본문 줄이 정확히 72자면 통과한다 (경계값)"""
        self.assertAccepted(self.commit("[feat] 제목\n\n" + "x" * 72))

    def test_본문_줄이_73자면_거부된다(self):
        """[GF-83] 본문 줄이 73자면 거부된다 (경계값)"""
        self.assertRejected(self.commit("[feat] 제목\n\n" + "x" * 73))

    def test_등록된_트레일러_토큰_줄은_72자를_넘어도_통과한다(self):
        """[GF-83] 등록된 트레일러 토큰으로 시작하는 줄은 72자를 넘어도 통과한다"""
        self.assertAccepted(
            self.commit("[feat] 제목\n\nBREAKING CHANGE: " + "y" * 70)
        )


    # ── --no-verify로 우회할 수 없다 (GF-127, decision-18) ───────────

    def test_no_verify로도_형식_검증을_건너뛸_수_없다(self):
        """[GF-127] --no-verify를 줘도 형식이 틀린 메시지는 거부된다"""
        result = self.commit("형식 없는 제목", "--no-verify")
        self.assertRejected(result)
        self.assertIn("커밋 메시지가 [type][subsystem] 형식이 아닙니다", result.output)
        self.assertRejected(self.git("log", "-1"))

    def test_no_verify로도_길이_검증을_건너뛸_수_없다(self):
        """[GF-127] --no-verify를 줘도 본문 줄 72자 초과는 거부된다"""
        self.assertRejected(self.commit("[feat] 제목\n\n" + "x" * 73, "--no-verify"))

    def test_no_verify로도_브랜치_Task_Id_강제를_건너뛸_수_없다(self):
        """[GF-127] --no-verify를 줘도 Task-Id 없는 non-exempt 브랜치는 거부된다"""
        self.git_ok("checkout", "-q", "-b", "no-task-id-here")
        self.assertRejected(self.commit("[feat] missing task id", "--no-verify"))

    # ── git revert가 만드는 제목 예외 (GF-127, 유저 결정 (b)) ─────────

    def test_clean_revert_no_edit은_통과한다(self):
        """[GF-127] 충돌 없는 git revert --no-edit은 Revert "..." 제목으로 통과한다"""
        self.commit_ok("[feat] 되돌릴 커밋")
        result = self.git("revert", "--no-edit", "HEAD")
        self.assertAccepted(result)
        self.assertEqual(2, self.commit_count())
        self.assertEqual('Revert "[feat] 되돌릴 커밋"', self.head_subject())

    def test_50자_제목을_revert해도_길이_제한에_걸리지_않는다(self):
        """[GF-127] git이 만든 revert 제목은 50자를 넘어도 통과한다 (60자)"""
        subject = "[feat] " + "x" * 43
        self.commit_ok(subject)
        self.assertAccepted(self.git("revert", "--no-edit", "HEAD"))
        self.assertEqual(f'Revert "{subject}"', self.head_subject())
        self.assertGreater(len(self.head_subject()), 50)

    def test_revert를_revert한_Reapply도_통과한다(self):
        """[GF-127] revert의 revert(git 2.43+의 Reapply "...")와 그 revert도 통과한다"""
        self.commit_ok("[feat] 되돌릴 커밋")
        self.assertAccepted(self.git("revert", "--no-edit", "HEAD"))
        self.assertAccepted(self.git("revert", "--no-edit", "HEAD"))
        reapply = self.head_subject()
        # git 버전에 따라 Reapply "..." 또는 Revert "Revert "..."" 둘 중 하나다.
        self.assertIn(
            reapply,
            ('Reapply "[feat] 되돌릴 커밋"', 'Revert "Revert "[feat] 되돌릴 커밋""'),
        )
        self.assertAccepted(self.git("revert", "--no-edit", "HEAD"))
        self.assertEqual(f'Revert "{reapply}"', self.head_subject())
        self.assertEqual(4, self.commit_count())

    def test_revert_비슷한_손글씨_제목은_거부된다(self):
        """[GF-127] 따옴표 없는 Revert 제목이나 다른 git 자동 제목은 예외가 아니다"""
        for subject in ("Revert 되돌림", 'revert "소문자"', 'Revert ""', "fixup! [feat] x"):
            with self.subTest(subject=subject):
                self.assertRejected(self.commit(subject))

    def test_revert_제목도_본문_빈_줄_규칙은_지킨다(self):
        """[GF-127] revert 제목 예외는 제목 형식·길이만이다 — 빈 줄 규칙은 그대로다"""
        self.assertRejected(self.commit('Revert "[feat] x"\n바로 이어진 본문'))

    # ── 거부하면 검증 마커가 남지 않는다 (GF-31 → GF-127) ────────────

    def test_거부되면_스테일_마커도_남지_않는다(self):
        """[GF-31] 이전 실행의 마커가 남아 있어도 검증에서 거부되면 마커가 지워진다"""
        marker = self.git_dir_file(".gitformat-verified")
        marker.write_text("0 0\n", encoding="utf-8")
        self.assertRejected(self.commit("형식 없는 제목"))
        self.assertFalse(marker.exists(), "거부된 커밋 뒤에 마커가 남았다")


if __name__ == "__main__":
    unittest.main()
