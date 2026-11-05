---
id: GF-17
title: hooks/checks/sql.sh 언어 체크 추가 (pre-commit lint)
status: Done
assignee: []
created_date: '2026-08-24 04:29'
updated_date: '2026-08-24 04:30'
labels: []
dependencies: []
type: task
ordinal: 17000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
pre-commit 디스패처에 SQL 감지(.sqlfluff 설정 또는 추적된 .sql 파일) 추가, 스테이징된 .sql 파일에 sqlfluff lint 실행
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 sqlfluff 없으면 조용히 건너뜀
- [x] #2 .sql 파일도 .sqlfluff도 없으면 건너뜀
- [x] #3 스테이징된 .sql만 대상으로 lint, 실패 시 커밋 차단
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/checks/sql.sh 추가, pre-commit 디스패처에 .sqlfluff/추적된 .sql 파일 감지 추가. sqlfluff 미설치/스테이징 .sql 없음/.sql 자체 없음 모두 조용히 건너뜀 확인, 가짜 sqlfluff로 lint 통과·실패(커밋 차단)까지 검증.
<!-- SECTION:FINAL_SUMMARY:END -->
