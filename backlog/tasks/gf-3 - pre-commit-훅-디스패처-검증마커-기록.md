---
id: GF-3
title: pre-commit 훅 디스패처 + 검증마커 기록
status: Done
assignee: []
created_date: '2026-08-24 03:12'
updated_date: '2026-08-24 03:32'
labels: []
dependencies:
  - GF-2
type: task
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
package.json/pyproject.toml/pom.xml/CMakeLists.txt 등으로 언어 감지 후 해당 체크 실행, 통과 시 검증마커 기록(decision-3)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 마커 없는 언어는 아무 것도 안 하고 통과한다
- [x] #2 체크 통과 시 .gitformat-verified 마커가 기록된다
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/pre-commit 작성: package.json/pyproject.toml|requirements.txt/pom.xml|build.gradle*/CMakeLists.txt|Makefile로 언어 감지 후 hooks/checks/<lang>.sh 실행, 전부 통과 시 .gitformat-verified 마커 기록. 언어 미감지·체크스크립트 부재 시 무해 통과, 체크 실패 시 마커 미기록을 수동 테스트로 확인.
<!-- SECTION:FINAL_SUMMARY:END -->
