---
id: GF-22
title: 언어별 체크 실도구 재검증 (sqlfluff/ruff/clang-format/maven)
status: Done
assignee: []
created_date: '2026-08-24 04:48'
updated_date: '2026-08-24 07:56'
labels: []
dependencies:
  - GF-21
type: task
ordinal: 22000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
brew로 sqlfluff/ruff/clang-format/maven 설치 후, GF-17/18(SQL)과 GF-4/10(python/cpp/java) 계열 테스트를 PATH 셔밍 대신 실제 도구로 재작성한 bats 테스트로 대체
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 sql.sh가 실제 sqlfluff로 통과/실패 케이스를 검증한다
- [x] #2 python.sh가 실제 ruff로 통과/실패 케이스를 검증한다
- [x] #3 cpp.sh가 실제 clang-format으로 통과/실패 케이스를 검증한다
- [x] #4 java.sh가 실제 mvn(pom.xml 프로젝트)으로도 검증한다(기존엔 gradle만 실도구였음)
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
실도구(sqlfluff/ruff/clang-format/mvn) 기반 bats 테스트 4개 파일(총 13케이스) 추가. 실도구 검증 중 심각한 버그 2건 발견/수정: (1) sqlfluff는 dialect 미지정 시 무조건 사용법에러(exit 2) -> .sqlfluff 없을 때 --dialect ansi 폴백 추가. (2) mvn -o(오프라인)는 플러그인 캐시 없는 첫 실행에서 항상 실패 -> -o 제거. 둘 다 PATH 셔밍 테스트로는 못 잡던 결함. 전체 16개 bats + shellcheck 통과.
<!-- SECTION:FINAL_SUMMARY:END -->
