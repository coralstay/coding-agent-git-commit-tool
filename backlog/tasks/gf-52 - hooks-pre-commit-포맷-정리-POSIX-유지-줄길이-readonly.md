---
id: GF-52
title: 'hooks/pre-commit 포맷 정리 (POSIX 유지, 줄길이/readonly)'
status: Done
assignee: []
created_date: '2026-08-27 14:40'
updated_date: '2026-08-27 14:47'
labels: []
dependencies: []
ordinal: 50000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
hooks/pre-commit의 100자 초과 줄을 줄바꿈하고 단일 대입 상수성 변수에 readonly를 추가한다. 문법은 POSIX만 사용. 동작 변경 없음.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 100자를 초과하는 줄이 없다
- [x] #2 단일 대입 상수성 변수에 readonly가 적용된다
- [x] #3 tests/robustness-dispatch.bats, tests/checks-*.bats, tests/smoke.bats가 동일하게 통과하고 shellcheck -s sh 경고가 없다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
100자 초과 줄 없음(이미 준수). 단일 대입 상수성 변수 12개(REPO_ROOT/GIT_DIR/HOOK_DIR/CHECKS_DIR/CONF/MARKER/MARKER_TS/MARKER_JAVA/MARKER_JAVA_GRADLE/MARKER_CPP/MARKER_CPP_MAKE/MARKER_SQL/MARKER_SQL_GLOB)에 readonly 추가. bats 24/24 통과, shellcheck -s sh 경고 없음.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/pre-commit에 단일 대입 상수성 변수 readonly를 전면 추가(줄길이는 이미 100자 이내로 준수 상태). 동작 변경 없음을 bats+shellcheck로 확인.
<!-- SECTION:FINAL_SUMMARY:END -->
