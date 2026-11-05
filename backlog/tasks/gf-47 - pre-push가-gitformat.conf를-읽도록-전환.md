---
id: GF-47
title: pre-push가 gitformat.conf를 읽도록 전환
status: Done
assignee: []
created_date: '2026-08-27 09:38'
updated_date: '2026-08-27 14:10'
labels: []
dependencies:
  - GF-44
ordinal: 45000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
hooks/pre-push의 언어 감지 마커 5종과 sqlfluff 기본 dialect('ansi') 인라인 리터럴을 hooks/gitformat.conf에서 읽도록 바꾼다. pre-commit과 이제 진짜로 같은 소스를 참조하게 되어 마커 목록 drift가 구조적으로 불가능해진다. has_npm_script 등 함수 로직은 그대로 유지한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 언어 감지 마커 5종과 sqlfluff 기본 dialect가 인라인 리터럴 대신 hooks/gitformat.conf에서 읽힌다
- [x] #2 동작 변경 없음 — tests/robustness-dispatch.bats, tests/smoke.bats가 리팩토링 전후 동일하게 통과한다
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. resolve_self()를 pre-push에 새로 추가(다른 훅과 동일 코드, 독립적으로)
2. HOOK_DIR/CONF 계산 추가
3. 언어 감지 마커 5종+sql glob, sqlfluff 기본 dialect를 CONF에서 읽어 변수화
4. if 조건문/sqlfluff 호출부를 그 변수로 교체
5. bats tests/robustness-dispatch.bats tests/smoke.bats + shellcheck
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
hooks/pre-push에 resolve_self()를 새로 추가(다른 훅에 이미 있던 것과 동일 코드, 독립적으로)해 gitformat.conf 경로를 찾도록 함. 언어 감지 마커 5종+sql glob, sqlfluff 기본 dialect(sqlDialectDefault)를 CONF에서 읽음. java gradle 글롭은 SC2086 의도적 예외(if 앞에 disable, elif 앞엔 지시자를 못 둬서 if로 옮김). bats 9/9 통과(dispatch/smoke), shellcheck 경고 없음.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/pre-push의 언어 감지 마커 5종과 sqlfluff 기본 dialect를 hooks/gitformat.conf에서 읽도록 전환. pre-commit과 이제 같은 소스를 참조해 마커 목록 drift가 구조적으로 불가능해짐. has_npm_script 로직은 그대로 유지. 9개 bats + shellcheck로 동작 무변경 확인.
<!-- SECTION:FINAL_SUMMARY:END -->
