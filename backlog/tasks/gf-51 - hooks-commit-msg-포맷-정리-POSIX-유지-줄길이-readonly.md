---
id: GF-51
title: 'hooks/commit-msg 포맷 정리 (POSIX 유지, 줄길이/readonly)'
status: Done
assignee: []
created_date: '2026-08-27 14:40'
updated_date: '2026-08-27 14:44'
labels: []
dependencies: []
ordinal: 49000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
hooks/commit-msg의 100자 초과 줄(대부분 한글 주석)을 줄바꿈하고, 한 번만 대입되는 상수성 변수(HOOK_DIR, CONF, MARKER, TASK_PREFIX_DEFAULT, AI_TOOL_CLAUDE_CODE 등 — 조건부 재대입되는 TASK_PREFIX 자체는 제외)에 readonly를 추가한다. 문법은 POSIX만 사용, bashism 도입 안 함. 동작 변경 없음(순수 포맷팅).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 100자를 초과하는 줄이 없다
- [x] #2 단일 대입 상수성 변수에 readonly가 적용된다(재대입되는 변수는 제외)
- [x] #3 tests/robustness-commit-msg.bats, tests/smoke.bats가 리팩토링 전후 동일하게 통과하고 shellcheck -s sh 경고가 없다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
72/77번 줄(TASK_PREFIX/EXEMPT 폴백)이 100자를 초과해 줄바꿈. 단일 대입 상수성 변수 12개(MSG_FILE/GIT_DIR/HOOK_DIR/CONF/MARKER/TYPES/SUBJECT_LINE/TASK_PREFIX_DEFAULT/TASK_PREFIX(폴백 확정 후)/BRANCH/EXEMPT/AI_TOOL_CLAUDE_CODE/AI_TOOL_GATE/CONFIGURED_MODEL/KNOWN_MODELS_FILE)에 readonly 추가. bats 22/22 통과, shellcheck -s sh 경고 없음.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/commit-msg의 100자 초과 줄 2곳을 줄바꿈하고 단일 대입 상수성 변수 다수에 readonly를 추가(POSIX 표준 builtin, 문법 변경 없음). 동작 변경 없음을 bats+shellcheck로 확인.
<!-- SECTION:FINAL_SUMMARY:END -->
