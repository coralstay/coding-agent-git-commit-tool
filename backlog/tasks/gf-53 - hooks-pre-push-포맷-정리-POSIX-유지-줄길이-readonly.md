---
id: GF-53
title: 'hooks/pre-push 포맷 정리 (POSIX 유지, 줄길이/readonly)'
status: Done
assignee: []
created_date: '2026-08-27 14:40'
updated_date: '2026-08-27 19:47'
labels: []
dependencies: []
ordinal: 51000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
hooks/pre-push의 100자 초과 줄을 줄바꿈하고 단일 대입 상수성 변수에 readonly를 추가한다. 문법은 POSIX만 사용. 동작 변경 없음.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 100자를 초과하는 줄이 없다
- [x] #2 단일 대입 상수성 변수에 readonly가 적용된다
- [x] #3 tests/robustness-dispatch.bats, tests/smoke.bats가 동일하게 통과하고 shellcheck -s sh 경고가 없다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
92번 줄(sqlfluff 감지 조건)이 100자를 초과해 줄바꿈. 단일 대입 상수성 변수 11개(HOOK_DIR/CONF/MARKER_TS/MARKER_JAVA/MARKER_JAVA_GRADLE/MARKER_CPP/MARKER_CPP_MAKE/MARKER_SQL/MARKER_SQL_GLOB/SQL_DIALECT_DEFAULT/REPO_ROOT/BUILD_DIR)에 readonly 추가. bats 9/9 통과, shellcheck -s sh 경고 없음.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/pre-push의 100자 초과 줄 1곳을 줄바꿈하고 단일 대입 상수성 변수에 readonly를 추가. 동작 변경 없음을 bats+shellcheck로 확인.
<!-- SECTION:FINAL_SUMMARY:END -->
