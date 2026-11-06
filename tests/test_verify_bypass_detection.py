# ---
# title: test_verify_bypass_detection
# description: 폐지된 Verify-Bypassed 트레일러가 다시 나타나지 않음을 고정하는 테스트
# authors: [coralstay]
# license: AGPL-3.0-only
# status: draft
# created_date: '2026-11-06'
# updated_date: '2026-11-06'
# ---
"""Verify-Bypassed 트레일러가 더 이상 붙지 않는지 본다(GF-128 AC #10, decision-18).

decision-3 시절 post-commit은 검증 마커가 없으면 --no-verify 우회로 보고
Verify-Bypassed: true를 붙였다. GF-126·GF-127에서 검증이 --no-verify로 건너뛸 수 없는
prepare-commit-msg로 모이면서 탐지할 우회가 없어졌고, GF-128에서 post-commit과 함께 이
트레일러를 없앴다. 파일 이름은 그 경위를 찾기 쉽게 그대로 둔다 — 지금 이 파일이 고정하는
것은 "탐지"가 아니라 "그 트레일러가 다시 나타나지 않는다"는 사실이다.

Verify-Bypassed의 판정 근거였던 검증마커($GIT_DIR/.gitformat-verified)도 GF-128에서
함께 없앴다 — 그 마커를 읽던 것은 post-commit뿐이었다.

--no-verify로 형식이 틀린 메시지를 넣을 수 없다는 사실은 test_message_format_enforced.py가
고정한다.
"""

import unittest

from isolated_repo import IsolatedRepoTestCase


class VerifyBypassedRemovedTest(IsolatedRepoTestCase):
    def setUp(self):
        super().setUp()
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")

    def test_정상_커밋에_Verify_Bypassed가_없다(self):
        """[GF-128] 정상 커밋에 Verify-Bypassed가 붙지 않는다"""
        self.assertAccepted(self.commit("[feat] normal commit"))
        self.assertTrailerKeyAbsent(self.head_message(), "Verify-Bypassed")

    def test_no_verify_커밋에도_Verify_Bypassed가_없다(self):
        """[GF-128] --no-verify로 커밋해도 Verify-Bypassed가 붙지 않고 트레일러는 정상으로 붙는다"""
        self.assertAccepted(self.commit("[feat] bypass verification", "--no-verify"))
        message = self.head_message()
        self.assertTrailerKeyAbsent(message, "Verify-Bypassed")  # ---- 1
        self.assertTrailerCount(message, "Hooks-Commit:", 1)  # ---- 2

    def test_검증마커를_더_이상_쓰지_않는다(self):
        """[GF-128] 커밋 뒤 $GIT_DIR에 검증마커 파일이 생기지 않는다"""
        self.assertAccepted(self.commit("[feat] no marker"))
        self.assertFalse(self.git_dir_file(".gitformat-verified").exists())  # ---- 3


if __name__ == "__main__":
    unittest.main()


# ======== 노트 ========
# 1 Verify-Bypassed 트레일러는 더 이상 붙지 않는다
#   설명: decision-3 시절 post-commit은 검증 마커가 없으면 --no-verify 우회로 보고 Verify-Bypassed: true를 붙였다.
#   GF-126·GF-127에서 검증이 --no-verify로 건너뛸 수 없는 prepare-commit-msg로 모이면서 탐지할 우회가 없어졌고 GF-128에서
#   post-commit과 함께 이 트레일러를 없앴다. 파일 이름은 그 경위를 찾기 쉽게 그대로 둔다. 지금 이 파일이 고정하는 것은 탐지가 아니라 그 트레일러가 다시
#   나타나지 않는다는 사실이다.
#   관련: GF-126, GF-127, GF-128, decision-3, decision-18
#   개념: 회귀 고정(폐지된 기능)
# 2 --no-verify가 prepare-commit-msg를 건너뛰지 못함
#   설명: 트레일러 삽입도 이 훅이 하므로 Hooks-Commit이 붙었으면 훅이 돈 것이다. --no-verify로 형식이 틀린 메시지를 넣을 수 없다는 사실은
#   test_message_format_enforced.py가 고정한다.
#   관련: tests/test_message_format_enforced.py
# 3 검증마커 파일도 사라졌다
#   설명: Verify-Bypassed의 판정 근거였던 검증마커($GIT_DIR/.gitformat-verified)도 GF-128에서 함께 없앴다. 그 마커를 읽던
#   것은 post-commit뿐이었다.
#   관련: GF-128
