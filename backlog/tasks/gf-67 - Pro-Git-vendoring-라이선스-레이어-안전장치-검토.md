---
id: GF-67
title: Pro Git vendoring 라이선스 레이어 안전장치 검토
status: Done
assignee: []
created_date: '2026-08-27 20:29'
updated_date: '2026-08-27 21:17'
labels: []
dependencies: []
ordinal: 65000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
docs/references/pro-git/는 CC BY-NC-SA(비영리) 라이선스라 저장소 전체 MIT 라이선스와 레이어가 다르다. README에 명시는 돼 있지만, 실수로 저장소 전체를 상업적으로 재배포하면서 이 디렉터리 라이선스 차이를 놓칠 구조적 위험이 남아있다. VENDORING.md 안내가 충분한지, 최상위 LICENSE 파일이나 docs/references/pro-git/ 자체에 더 눈에 띄는 경고가 필요한지 검토한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 라이선스 레이어 차이에 대한 안내가 충분한지 재검토하고, 부족하면 보강한다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
실제 Pro Git .asc 원문 내용은 읽지도 수정하지도 않고, 라이선스 고지 체계만 점검했다. 재검토 결과 최상위 LICENSE 파일에는 이 예외가 전혀 언급돼 있지 않아 라이선스 스캐너나 사람이 루트 LICENSE만 보면 저장소 전체를 MIT로 오해할 구조적 위험을 확인. LICENSE 파일 끝에 docs/references/pro-git/ 예외 고지를 추가하고, README '📄 라이선스' 섹션에도 짧은 경고를 추가해 총 3곳(README 주의점 - 기존, README 라이선스 섹션 - 신규, LICENSE 파일 - 신규)에서 확인 가능하게 함. bats 67/67 통과, shellcheck 전체 통과(문서/라이선스 변경이라 코드 영향 없음, 회귀 없음 확인 차원).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
최상위 LICENSE 파일에 docs/references/pro-git/의 CC BY-NC-SA 3.0 예외를 명시하는 고지를 추가하고, README 라이선스 섹션에도 같은 경고를 추가했다. 기존엔 이 사실이 README 주의점 한 곳에만 있어 루트 LICENSE만 보는 경우 놓칠 위험이 있었다.
<!-- SECTION:FINAL_SUMMARY:END -->
