---
id: GF-13
title: AI-Session-Id 트레일러 제거
status: Done
assignee: []
created_date: '2026-08-24 04:14'
updated_date: '2026-08-24 04:16'
labels: []
dependencies: []
type: task
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
post-commit이 커밋 footer에 AI-Session-Id를 삽입하던 부분을 제거한다. AI-Model 추출을 위해 CLAUDE_CODE_SESSION_ID로 트랜스크립트 파일을 찾는 내부 로직은 유지하되, 그 값 자체를 커밋 이력에 영구히 남기지 않는다.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/post-commit에서 AI-Session-Id 트레일러 삽입 코드 제거(CLAUDE_CODE_SESSION_ID는 AI-Model 조회용 트랜스크립트 경로 계산에만 내부 사용, 커밋에는 남기지 않음). README/docs/decision-5 갱신(decision-5는 삭제 대신 amendment로 이력 보존). 가짜 트랜스크립트로 AI-Model은 정상 동작하고 AI-Session-Id는 더 이상 안 붙는 것 재검증.
<!-- SECTION:FINAL_SUMMARY:END -->
