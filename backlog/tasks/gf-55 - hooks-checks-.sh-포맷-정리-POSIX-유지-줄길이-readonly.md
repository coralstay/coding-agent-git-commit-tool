---
id: GF-55
title: 'hooks/checks/*.sh 포맷 정리 (POSIX 유지, 줄길이/readonly)'
status: Done
assignee: []
created_date: '2026-08-27 14:40'
updated_date: '2026-08-27 19:55'
labels: []
dependencies: []
ordinal: 53000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
hooks/checks/ts.sh, python.sh, java.sh, cpp.sh, sql.sh의 100자 초과 줄을 줄바꿈하고 단일 대입 상수성 변수에 readonly를 추가한다. 문법은 POSIX만 사용. 동작 변경 없음.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 5개 파일 모두 100자를 초과하는 줄이 없다
- [x] #2 단일 대입 상수성 변수에 readonly가 적용된다
- [x] #3 tests/checks-*.bats가 동일하게 통과하고 shellcheck -s sh 경고가 없다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
5개 파일 모두 100자 초과 줄 없음(이미 준수). 단일 대입 상수성 변수(각 파일의 REPO_ROOT, cpp.sh/sql.sh는 추가로 HOOK_DIR/CONF/FILELIST/SQL_DIALECT_DEFAULT)에 readonly 추가. bats 15/15 통과(checks-cpp/java/python/sql), shellcheck -s sh 경고 없음.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/checks/*.sh 5개 파일에 단일 대입 상수성 변수 readonly를 전면 추가(줄길이는 이미 준수 상태). 동작 변경 없음을 bats+shellcheck로 확인.
<!-- SECTION:FINAL_SUMMARY:END -->
