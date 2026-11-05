---
id: GF-45
title: commit-msg가 gitformat.conf를 읽도록 전환
status: Done
assignee: []
created_date: '2026-08-27 09:38'
updated_date: '2026-08-27 14:04'
labels: []
dependencies:
  - GF-44
ordinal: 43000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
hooks/commit-msg의 마커 파일명(.gitformat-verified), TASK_PREFIX/EXEMPT 기본값, AI 도구 식별자(claude-code) 인라인 리터럴을 hooks/gitformat.conf(git config --file)에서 읽도록 바꾼다. resolve_self/cleanup_marker_on_reject 등 함수 로직은 그대로 유지한다(합치지 않음). 컨슈머 저장소의 gitformat.taskPrefix/gitformat.branchExempt 오버라이드 우선순위(설정 있으면 그 값, 없으면 conf의 기본값)는 유지한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 마커 파일명·TASK_PREFIX/EXEMPT 기본값·claude-code 식별자가 인라인 리터럴 대신 hooks/gitformat.conf에서 읽힌다
- [x] #2 동작 변경 없음 — tests/robustness-commit-msg.bats, tests/smoke.bats가 리팩토링 전후 동일하게 통과한다
- [x] #3 심볼릭 링크(template/) 설치 환경에서도 conf 파일 경로를 정확히 찾는다(GF-16 회귀 없음)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. resolve_self()를 파일 앞부분으로 옮기고 HOOK_DIR/CONF(hooks/gitformat.conf)를 계산
2. 마커 파일명을 CONF의 gitformat.markerFile에서 읽어 MARKER 변수로 사용(cleanup_marker_on_reject에서 사용)
3. TASK_PREFIX 기본값 폴백을 CONF의 gitformat.taskPrefixDefault로 대체(GF-35 로직은 유지)
4. EXEMPT 기본값 폴백을 CONF의 gitformat.branchExempt(--get-all)로 대체
5. AI 도구 식별자 claude-code를 CONF의 gitformat.aiToolClaudeCode로 대체
6. known-models.txt 경로를 CONF의 gitformat.knownModelsFile + HOOK_DIR로 조합
7. bats tests/robustness-commit-msg.bats tests/smoke.bats 실행, shellcheck 실행
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
hooks/commit-msg를 hooks/gitformat.conf 소비로 전환: 마커 파일명(gitformat.markerFile), TASK_PREFIX/EXEMPT 기본값(taskPrefixDefault/branchExempt), AI 도구 식별자(aiToolClaudeCode), known-models 경로(knownModelsFile)를 CONF에서 읽음. resolve_self를 파일 앞부분으로 옮겨 HOOK_DIR/CONF 계산에 재사용(기존에 AI 게이트 블록 안에만 있던 중복 정의 제거 — 같은 파일 내부 중복이라 스코프 내). bats tests/robustness-commit-msg.bats+smoke.bats 22/22 통과, shellcheck 경고 없음. install.sh --global(격리 HOME)로 실제 symlink 설치 시나리오 수동 검증 — known-models.txt 경로가 정확히 resolve됨(GF-16 회귀 없음).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/commit-msg의 마커 파일명/TASK_PREFIX·EXEMPT 기본값/claude-code 식별자/known-models 경로를 hooks/gitformat.conf에서 읽도록 전환. 컨슈머의 gitformat.taskPrefix/branchExempt 오버라이드 우선순위는 그대로 유지. 22개 bats 테스트 + shellcheck + symlink 설치 수동검증으로 동작 무변경 확인.
<!-- SECTION:FINAL_SUMMARY:END -->
