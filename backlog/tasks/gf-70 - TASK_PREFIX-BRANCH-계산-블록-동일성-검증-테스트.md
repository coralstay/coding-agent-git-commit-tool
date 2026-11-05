---
id: GF-70
title: TASK_PREFIX/BRANCH 계산 블록 동일성 검증 테스트
status: Done
assignee: []
created_date: '2026-08-28 04:25'
updated_date: '2026-08-28 04:30'
labels: []
dependencies: []
ordinal: 68000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
commit-msg와 post-commit 양쪽에 TASK_PREFIX_DEFAULT 조회, TASK_PREFIX 폴백(GF-35 로직 포함), BRANCH 계산이 거의 동일한 8~9줄짜리 블록으로 복붙돼 있다(resolve_self처럼 의도된 독립 설계). resolve_self()는 GF-62에서 6개 사본 동일성 테스트로 이미 보호되지만, 이 TASK_PREFIX/BRANCH 블록은 아직 그런 drift 테스트가 없다. tests/consistency.bats에 두 파일에서 이 블록을 추출해 비교하는 케이스를 추가한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 commit-msg와 post-commit의 TASK_PREFIX/BRANCH 계산 블록을 추출해 동일한지 확인하는 bats 케이스가 tests/consistency.bats에 추가된다
- [x] #2 일부러 한쪽만 다르게 바꿨을 때 테스트가 실패하는 것을 확인한다
- [x] #3 동작 변경 없음 - 전체 bats 스위트가 전과 동일하게 통과하고 shellcheck -s sh 경고가 없다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
tests/consistency.bats에 TASK_PREFIX_DEFAULT부터 readonly BRANCH까지 블록을 awk로 추출해 비교하는 케이스 추가. 처음 실행에서 실제로 실패했는데, 진짜 로직 차이가 아니라 post-commit에 GF-35 설명 주석이 누락돼 있던 것 - 이 자체가 이 테스트의 가치를 보여주는 사례. post-commit에 동일 주석을 추가해 완전히 일치시킴. bats 전체 68/68 통과, shellcheck 전체 통과.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
commit-msg/post-commit의 TASK_PREFIX/BRANCH 계산 블록 동일성을 검증하는 테스트를 추가했다. 실행 중 실제로 문서화 누락(GF-35 주석)을 잡아내 post-commit에 보강했다.
<!-- SECTION:FINAL_SUMMARY:END -->
