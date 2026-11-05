---
id: GF-49
title: checks/cpp.sh·sql.sh가 gitformat.conf를 읽도록 전환
status: Done
assignee: []
created_date: '2026-08-27 09:38'
updated_date: '2026-08-27 14:14'
labels: []
dependencies:
  - GF-44
ordinal: 47000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
hooks/checks/cpp.sh의 C/C++ 확장자 목록과 hooks/checks/sql.sh의 기본 dialect('ansi') 인라인 리터럴을 hooks/gitformat.conf에서 읽도록 바꾼다. 두 파일 간 mktemp+trap 파일목록 수집 로직은 공유하지 않고 지금처럼 각자 독립적으로 유지한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 cpp.sh의 확장자 목록과 sql.sh의 기본 dialect가 인라인 리터럴 대신 hooks/gitformat.conf에서 읽힌다(두 파일 간 함수 공유는 없음)
- [x] #2 동작 변경 없음 — tests/checks-cpp.bats, tests/checks-sql.bats가 리팩토링 전후 동일하게 통과한다
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. cpp.sh, sql.sh 각각에 resolve_self()를 독립적으로 추가(공유 안 함)
2. HOOK_DIR(hooks/checks -> 상위 hooks/)/CONF 계산 추가
3. cpp.sh: 확장자 목록을 CONF의 gitformat.cpp.ext(다중값)에서 읽어 git diff 인자로 전개
4. sql.sh: 기본 dialect를 CONF의 gitformat.sqlDialectDefault에서 읽음
5. bats tests/checks-cpp.bats tests/checks-sql.bats + shellcheck
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
hooks/checks/cpp.sh, hooks/checks/sql.sh 각각에 resolve_self()를 독립적으로 추가(서로 공유 안 함)해 checks/의 상위(hooks/)에 있는 gitformat.conf를 찾도록 함. cpp.sh는 C/C++ 확장자 목록(gitformat.cpp.ext, 다중값)을 git diff 인자로 전개(SC2046 의도적 예외 처리), sql.sh는 기본 dialect(gitformat.sqlDialectDefault)를 --dialect 인자로 사용. mktemp+trap 파일목록 수집 로직은 두 파일 모두 그대로 유지(공유 함수화하지 않음 — GF-43 방향 전환 유지). bats 9/9 통과(checks-cpp/checks-sql, GF-36 공백 파일명·GF-37 rename 케이스 포함), shellcheck 경고 없음.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/checks/cpp.sh의 확장자 목록과 hooks/checks/sql.sh의 기본 dialect를 hooks/gitformat.conf에서 읽도록 전환. 두 파일 간 함수/변수 공유는 전혀 없음(각자 독립적으로 resolve_self 보유). 9개 bats + shellcheck로 동작 무변경 확인.
<!-- SECTION:FINAL_SUMMARY:END -->
