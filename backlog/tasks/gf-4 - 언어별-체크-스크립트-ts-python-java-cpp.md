---
id: GF-4
title: 언어별 체크 스크립트 (ts/python/java/cpp)
status: Done
assignee: []
created_date: '2026-08-24 03:12'
updated_date: '2026-08-24 03:34'
labels: []
dependencies:
  - GF-3
type: task
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
hooks/checks/{ts,python,java,cpp}.sh 각각 lint/타입체크 실행
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 각 언어 마커 파일이 있을 때만 해당 스크립트가 실행된다
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/checks/{ts,python,java,cpp}.sh 작성. 각각 필요한 도구가 없거나 대상 파일/설정이 없으면 조용히 건너뛰고, pre-commit 단계는 lint/컴파일/포맷 검사까지만 하고 빌드·테스트는 pre-push로 미루는 원칙으로 구현. sh -n으로 4개 스크립트 문법 검증 완료.
<!-- SECTION:FINAL_SUMMARY:END -->
