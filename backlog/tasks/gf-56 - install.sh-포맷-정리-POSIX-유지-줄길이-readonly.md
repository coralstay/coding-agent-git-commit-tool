---
id: GF-56
title: 'install.sh 포맷 정리 (POSIX 유지, 줄길이/readonly)'
status: Done
assignee: []
created_date: '2026-08-27 14:40'
updated_date: '2026-08-27 19:58'
labels: []
dependencies: []
ordinal: 54000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
install.sh의 100자 초과 줄을 줄바꿈하고 단일 대입 상수성 변수에 readonly를 추가한다. 문법은 POSIX만 사용. 동작 변경 없음.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 100자를 초과하는 줄이 없다
- [x] #2 단일 대입 상수성 변수에 readonly가 적용된다
- [x] #3 tests/robustness-install.bats가 동일하게 통과하고 shellcheck -s sh 경고가 없다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
100자 초과 줄 없음(이미 준수). 단일 대입 상수성 변수(SELF_DIR/HOOKS_DIR/GITMESSAGE/TEMPLATE_DIR, TARGET은 최종 확정 후)에 readonly 추가. GLOBAL_MODE는 재대입되는 변수라 제외. bats 4/4 통과, shellcheck -s sh 경고 없음.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
install.sh에 단일 대입 상수성 변수 readonly를 추가(줄길이는 이미 준수 상태). 동작 변경 없음을 bats+shellcheck로 확인.
<!-- SECTION:FINAL_SUMMARY:END -->
