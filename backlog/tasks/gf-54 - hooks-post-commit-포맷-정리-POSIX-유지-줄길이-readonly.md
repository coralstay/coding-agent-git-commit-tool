---
id: GF-54
title: 'hooks/post-commit 포맷 정리 (POSIX 유지, 줄길이/readonly)'
status: Done
assignee: []
created_date: '2026-08-27 14:40'
updated_date: '2026-08-27 19:51'
labels: []
dependencies: []
ordinal: 52000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
hooks/post-commit의 100자 초과 줄을 줄바꿈하고 trailer 키 변수 등 단일 대입 상수성 변수에 readonly를 추가한다. 문법은 POSIX만 사용. 동작 변경 없음.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 100자를 초과하는 줄이 없다
- [x] #2 단일 대입 상수성 변수에 readonly가 적용된다
- [x] #3 tests/robustness-post-commit.bats, tests/robustness-injection.bats, tests/smoke.bats가 동일하게 통과하고 shellcheck -s sh 경고가 없다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
7개 줄(65/81/85/105/113/125/145)이 100자를 초과해 줄바꿈. 단일 대입 상수성 변수 다수(GIT_DIR/HOOK_DIR/CONF/MARKER/TRAILER_* 7종/AI_TOOL_CLAUDE_CODE/CO_AUTHORED_BY_VALUE/CURRENT_MSG/EXISTING_TRAILERS/TASK_PREFIX_DEFAULT/TASK_PREFIX/BRANCH/TASK_NUM/AI_TOOL_ID/AI_TOOL_VERSION)에 readonly 추가. bats 16/16 통과, shellcheck -s sh 경고 없음.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/post-commit의 100자 초과 줄 7곳을 줄바꿈하고 단일 대입 상수성 변수 다수에 readonly를 추가. 동작 변경 없음을 bats+shellcheck로 확인.
<!-- SECTION:FINAL_SUMMARY:END -->
