---
id: GF-18
title: pre-push에 SQL 전체 lint 추가
status: Done
assignee: []
created_date: '2026-08-24 04:29'
updated_date: '2026-08-24 04:31'
labels: []
dependencies:
  - GF-17
type: task
ordinal: 18000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
pre-push에 저장소 전체 sqlfluff lint 추가 (pre-commit은 스테이징 파일만, pre-push는 전체)
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
pre-push에 .sqlfluff/추적된 .sql 파일 감지 후 sqlfluff lint . 실행하는 블록 추가. 가짜 sqlfluff로 스킵/통과/실패 검증.
<!-- SECTION:FINAL_SUMMARY:END -->
