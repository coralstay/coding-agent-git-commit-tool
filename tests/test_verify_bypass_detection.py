"""검증 마커와 --no-verify의 관계를 본다(decision-3, GF-31, GF-126, GF-135).

구 robustness-post-commit.bats의 상태전이 케이스. 마커를 쓰는 훅은 시작 시점에 남은
마커를 지우고 끝에 다시 쓰고, post-commit은 그 마커의 존재만 보고 판정한 뒤 항상
지운다 — 그래야 다음 커밋으로 스테일 마커가 새지 않는다.

**GF-126이 이 관계를 바꿨다.** 마커 기록이 pre-commit에서 prepare-commit-msg로
옮겨왔고, prepare-commit-msg는 --no-verify로도 건너뛸 수 없다(doc-15). 그래서 마커는
--no-verify 커밋에서도 항상 써지고, 마커의 부재로 우회를 판정하는 Verify-Bypassed는
**사실상 도달 불가능**해졌다.

**GF-135는 그 마커가 무엇을 뜻하는지를 바꿨다.** 언어별 lint가 제거되며 마커가 gate할
대상이 없어져, 이제 마커는 "검사를 통과했다"가 아니라 "prepare-commit-msg가 돌았다"만
뜻한다. 그래도 조건 없이 계속 써야 한다 — 안 쓰면 아직 살아 있는 post-commit이 모든
커밋에 Verify-Bypassed를 붙인다. 아래 두 테스트가 그 가교를 고정한다. 마커와 이 테스트
파일은 post-commit과 함께 GF-128에서 사라진다.

"사실상"인 이유는 재생 커밋 경로다(GF-126 실측). 면제가 먼저 걸려 마커가 없으니
post-commit은 그 경로에서 Verify-Bypassed를 여전히 큐에 넣는데, 재생 중에는 amend 자체가
실패해(archive DRAFT-18) 트레일러가 커밋에 남지 않는다 — 그 경로를 단언으로 고정하지
않는 것은 지금 동작이 의도된 설계가 아니라 구 post-commit의 미해결 결함이기 때문이다.

GF-126 시점에는 --no-verify가 아직 commit-msg를 건너뛰어 '메시지 검증 우회'가 기록 없이
가능했다. GF-127이 검증을 prepare-commit-msg로 옮기고 commit-msg를 삭제해 그 과도기를
닫았다 — --no-verify로 형식이 틀린 메시지를 넣을 수 없다는 사실은
test_message_format_enforced.py가 고정한다.
"""

import unittest

from isolated_repo import IsolatedRepoTestCase

MARKER_NAME = ".gitformat-verified"


class VerifyBypassDetectionTest(IsolatedRepoTestCase):
    def test_정상_커밋은_마커가_남지_않고_Verify_Bypassed도_없다(self):
        """[상태전이] 정상 커밋은 마커가 결과적으로 남지 않고 Verify-Bypassed가 안 붙는다"""
        marker = self.git_dir_file(MARKER_NAME)
        self.assertFalse(marker.exists())
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")
        self.assertAccepted(self.commit("[feat] normal commit"))
        self.assertFalse(marker.exists(), "post-commit이 마커를 지우지 않았다")
        self.assertTrailerKeyAbsent(self.head_message(), "Verify-Bypassed")

    def test_no_verify_커밋에도_Verify_Bypassed가_붙지_않는다(self):
        """[상태전이] --no-verify로 커밋해도 마커가 써져 Verify-Bypassed가 붙지 않는다

        GF-126까지는 반대였다 — pre-commit이 --no-verify로 스킵돼 마커가 없었고,
        post-commit이 그 부재를 우회 증거로 읽어 Verify-Bypassed: true를 붙였다. 마커
        기록이 --no-verify로 건너뛸 수 없는 prepare-commit-msg로 옮겨온 뒤에는 마커가
        항상 써지므로 이 트레일러는 도달 불가능하다. post-commit과 함께 GF-128에서
        사라질 신호다.
        """
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")
        self.assertAccepted(self.commit("[feat] bypass verification", "--no-verify"))
        # post-commit이 판정 후 항상 지우므로 마커 자체는 남지 않는다.
        self.assertFalse(self.git_dir_file(MARKER_NAME).exists())
        self.assertTrailerKeyAbsent(self.head_message(), "Verify-Bypassed")


if __name__ == "__main__":
    unittest.main()
