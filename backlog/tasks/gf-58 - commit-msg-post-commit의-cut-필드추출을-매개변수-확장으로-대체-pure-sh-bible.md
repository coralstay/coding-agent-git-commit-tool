---
id: GF-58
title: commit-msg/post-commit의 cut 필드추출을 매개변수 확장으로 대체 (pure-sh-bible)
status: Done
assignee: []
created_date: '2026-08-27 20:10'
updated_date: '2026-08-27 20:13'
labels: []
dependencies: []
ordinal: 56000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
hooks/commit-msg의 AI_TOOL_GATE, hooks/post-commit의 AI_TOOL_ID/AI_TOOL_VERSION이 cut -d_ -f1/-f2로 AI_AGENT를 필드분리한다. POSIX 매개변수 확장(${var%%_*}, ${var#*_})으로 외부 프로세스(cut) 없이 동일하게 처리한다. tr '-' '.'(AI_TOOL_VERSION 후처리)과 tr '/' '-'(PROJECT_SLUG)는 POSIX에 전역 치환 매개변수 확장이 없어 순수 셸로 바꾸면 루프+패턴 인용이 필요해 이식성 이득 없이 버그 위험만 커진다 — tr은 POSIX 표준 유틸리티라 이미 완전히 이식성 있으므로 그대로 둔다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 AI_TOOL_GATE, AI_TOOL_ID, AI_TOOL_VERSION의 필드 추출이 cut 대신 매개변수 확장으로 처리된다
- [x] #2 cut -d_ -f1/-f2와 동일한 결과를 내는지 기존 값(claude-code_2-1-227_agent, other-tool_1-0, 빈 문자열)으로 확인된다
- [x] #3 동작 변경 없음 - tests/robustness-commit-msg.bats, tests/robustness-post-commit.bats, tests/smoke.bats가 동일하게 통과하고 shellcheck -s sh 경고가 없다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
AI_TOOL_GATE(commit-msg), AI_TOOL_ID/AI_TOOL_VERSION(post-commit)의 cut -d_ -f1/-f2를 ${var%%_*}/${var#*_} 매개변수 확장으로 대체. tr '-' '.'(AI_TOOL_VERSION)과 tr '/' '-'(PROJECT_SLUG)는 POSIX에 전역 치환이 없어 그대로 유지(이식성 손해 없음, 순수 셸 전환 시 위험만 증가). bats 35/35 통과, shellcheck -s sh 경고 없음. 실제 AI_AGENT=claude-code_2-1-227_agent 커밋으로 AI-Tool-Version: 2.1.227이 정확히 나옴을 수동 검증(cut -d_ -f2와 동일).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
cut -d_ -f1/-f2 필드추출 3곳을 POSIX 매개변수 확장으로 대체해 외부 프로세스(cut) 호출을 제거. tr은 POSIX 표준이라 이식성 손해가 없어 그대로 유지. bats+shellcheck+실제 커밋 수동검증으로 동작 무변경 확인.
<!-- SECTION:FINAL_SUMMARY:END -->
