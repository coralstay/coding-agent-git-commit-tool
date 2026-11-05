---
id: GF-46
title: pre-commit이 gitformat.conf를 읽도록 전환
status: Done
assignee: []
created_date: '2026-08-27 09:38'
updated_date: '2026-08-27 14:07'
labels: []
dependencies:
  - GF-44
ordinal: 44000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
hooks/pre-commit의 언어 감지 마커 5종(package.json 등) 인라인 리터럴을 hooks/gitformat.conf에서 읽도록 바꾼다. resolve_self/run_check 함수 로직은 그대로 유지한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 언어 감지 마커 5종이 인라인 리터럴 대신 hooks/gitformat.conf에서 읽힌다
- [x] #2 동작 변경 없음 — tests/robustness-dispatch.bats, tests/checks-*.bats, tests/smoke.bats가 리팩토링 전후 동일하게 통과한다
- [x] #3 심볼릭 링크(template/) 설치 환경에서도 conf 파일 경로를 정확히 찾는다(GF-16 회귀 없음)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. CONF 경로를 기존 HOOK_DIR 계산에 이어 붙임
2. 언어 감지 마커 5종(ts/python(다중)/java/javaGradle/cpp/cppMake/sql/sqlGlob)을 CONF에서 읽어 변수화
3. if 조건문들을 그 변수 참조로 교체 (python은 다중값이라 순회)
4. bats tests/robustness-dispatch.bats tests/checks-*.bats tests/smoke.bats + shellcheck
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
hooks/pre-commit을 hooks/gitformat.conf 소비로 전환: 마커 파일명(markerFile)과 언어 감지 마커 5종+glob(marker.ts/python(다중값)/java/javaGradle/cpp/cppMake/sql/sqlGlob)을 CONF에서 읽음. 계획엔 없었지만 일관성을 위해 MARKER도 commit-msg와 동일하게 CONF에서 읽도록 함께 전환(안 그러면 마커 파일명이 파일별로 다시 갈라질 위험). java의 build.gradle* 글롭은 SC2086 의도적 예외로 인라인 disable 추가. bats 24/24 통과(dispatch/checks-cpp/java/python/sql/smoke), shellcheck 경고 없음.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/pre-commit의 마커 파일명과 언어 감지 마커 5종을 hooks/gitformat.conf에서 읽도록 전환. resolve_self/run_check 로직은 그대로 유지. 24개 bats + shellcheck로 동작 무변경 확인.
<!-- SECTION:FINAL_SUMMARY:END -->
