---
id: GF-71
title: python_marker_found 루프 블록 동일성 검증 테스트 (pre-commit/pre-push)
status: Done
assignee: []
created_date: '2026-08-28 04:32'
updated_date: '2026-08-28 04:35'
labels: []
dependencies: []
ordinal: 69000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
hooks/pre-commit과 hooks/pre-push 양쪽에 gitformat.conf의 다중값 marker.python을 순회해 python_marker_found를 세팅하는 4줄짜리 루프 블록이 동일하게 복붙돼 있다(resolve_self/TASK_PREFIX-BRANCH와 같은 패턴, 의도된 독립 설계). 아직 이 블록에 대한 drift 테스트가 없다. tests/consistency.bats에 두 파일에서 이 블록을 추출해 비교하는 케이스를 추가한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 pre-commit과 pre-push의 python_marker_found 루프 블록을 추출해 동일한지 확인하는 bats 케이스가 tests/consistency.bats에 추가된다
- [x] #2 일부러 한쪽만 다르게 바꿨을 때 테스트가 실패하는 것을 확인한다
- [x] #3 동작 변경 없음 - 전체 bats 스위트가 전과 동일하게 통과하고 shellcheck -s sh 경고가 없다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
tests/consistency.bats에 python_marker_found=false부터 done까지 루프 블록을 awk로 추출해 pre-commit/pre-push 간 비교하는 케이스 추가. 첫 실행부터 통과(실제로 완전 동일했음). bats 전체 69/69 통과, shellcheck 전체 통과.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
pre-commit/pre-push의 python_marker_found 루프 블록 동일성을 검증하는 테스트를 tests/consistency.bats에 추가했다.
<!-- SECTION:FINAL_SUMMARY:END -->
