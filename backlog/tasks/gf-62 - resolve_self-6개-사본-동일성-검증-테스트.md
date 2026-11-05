---
id: GF-62
title: resolve_self() 6개 사본 동일성 검증 테스트
status: Done
assignee: []
created_date: '2026-08-27 20:29'
updated_date: '2026-08-27 20:57'
labels: []
dependencies: []
ordinal: 60000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
commit-msg/pre-commit/pre-push/post-commit/checks/cpp.sh/checks/sql.sh 6개 파일에 resolve_self() 함수가 글자 단위로 동일하게 복붙돼 있다(의도된 설계 - 로직은 공유하지 않음). 이 6곳이 실제로 동일한지 자동 검증하는 테스트가 없어, 한 곳만 버그를 고치고 나머지를 빠뜨려도(GF-16류) 아무도 바로 눈치채지 못한다. 함수 본문을 추출해 6개 파일 간 diff로 비교하는 테스트를 추가한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 6개 파일에서 resolve_self 함수 본문만 추출해 서로 동일한지 확인하는 테스트가 추가된다
- [x] #2 일부러 한 파일의 resolve_self를 다르게 바꿨을 때 테스트가 실패하는 것을 확인한다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
tests/consistency.bats에 6개 파일(commit-msg/pre-commit/pre-push/post-commit/checks/cpp.sh/checks/sql.sh)의 resolve_self() 함수 본문을 awk로 추출해 서로 바이트 단위로 동일한지 비교하는 케이스를 추가. 일부러 sql.sh의 resolve_self 한 줄을 바꿨을 때 테스트가 실패하는 것, 원복하면 통과하는 것을 실제로 확인. bats 전체 63/63 통과, shellcheck 전체 파일 경고 없음.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
resolve_self() 6개 사본이 글자 그대로 동일한지 검증하는 bats 테스트를 tests/consistency.bats에 추가했다. 로직 공유 없이 테스트로만 drift를 잡는 방식(decision-9 원칙 유지). 네거티브 케이스 실증, bats+shellcheck 전체 통과.
<!-- SECTION:FINAL_SUMMARY:END -->
