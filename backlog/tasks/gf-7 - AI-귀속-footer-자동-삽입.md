---
id: GF-7
title: AI 귀속 footer 자동 삽입
status: Done
assignee: []
created_date: '2026-08-24 03:12'
updated_date: '2026-08-24 03:43'
labels: []
dependencies:
  - GF-6
type: task
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
AI-Tool/AI-Tool-Version(AI_AGENT 파싱), AI-Session-Id(CLAUDE_CODE_SESSION_ID), AI-Model(세션 트랜스크립트 message.model 읽기, 비-Claude Code는 gitformat.aiModel 존재+화이트리스트+벤더 검증), Co-Authored-By 자동, Hooks-Commit(git-format 자체 커밋 해시)(decision-5)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Claude Code 환경에서 AI-Model이 세션 트랜스크립트의 실제 model 값과 일치한다
- [x] #2 AI 환경이 감지되지 않으면(사람 커밋) 아무 트레일러도 추가되지 않는다
- [x] #3 트랜스크립트 파싱 실패 시 커밋을 막지 않고 AI-Model만 조용히 생략한다
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
post-commit에 AI-Tool/AI-Tool-Version(AI_AGENT 파싱), Co-Authored-By(claude-code 한정), AI-Session-Id(CLAUDE_CODE_SESSION_ID), AI-Model(Claude Code는 세션 트랜스크립트 message.model, 그 외는 gitformat.aiModel), Hooks-Commit(git-format 자체 HEAD)을 추가. commit-msg에 non-claude-code AI-Model 존재+화이트리스트 게이트 추가. 구현 중 git interpret-trailers --if-exists doNothing이 접두어 키를 삭제하는 버그와 Co-Authored-By 오귀속 버그를 발견해 수정. 가짜 트랜스크립트/여러 AI 도구/인간 커밋 시나리오를 격리 저장소에서 검증.
<!-- SECTION:FINAL_SUMMARY:END -->
