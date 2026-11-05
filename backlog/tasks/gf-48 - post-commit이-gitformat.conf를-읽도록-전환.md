---
id: GF-48
title: post-commit이 gitformat.conf를 읽도록 전환
status: Done
assignee: []
created_date: '2026-08-27 09:38'
updated_date: '2026-08-27 14:12'
labels: []
dependencies:
  - GF-44
ordinal: 46000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
hooks/post-commit의 trailer 키 7종(Verify-Bypassed/Task-Id/AI-Tool/AI-Tool-Version/Co-Authored-By/AI-Model/Hooks-Commit), claude-code 식별자, Co-Authored-By 값 인라인 리터럴을 hooks/gitformat.conf에서 읽도록 바꾼다. 같은 파일 안에서 trailer_exists 호출부와 --trailer 삽입부가 같은 변수를 참조하게 되어 GF-33류 오타 불일치가 구조적으로 불가능해진다. trailer_exists/resolve_self 함수 로직은 그대로 유지한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 trailer 키 7종·claude-code 식별자·Co-Authored-By 값이 인라인 리터럴 대신 hooks/gitformat.conf에서 읽히고, 존재확인부와 삽입부가 동일 변수를 참조한다
- [x] #2 동작 변경 없음 — tests/robustness-post-commit.bats, tests/robustness-injection.bats, tests/smoke.bats가 리팩토링 전후 동일하게 통과한다
- [x] #3 심볼릭 링크(template/) 설치 환경에서도 conf 파일 경로를 정확히 찾는다(GF-16 회귀 없음)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. HOOK_DIR/CONF 계산을 파일 앞부분으로 이동(현재는 뒤쪽 Hooks-Commit 계산부에만 있음)
2. trailer 키 7종을 CONF에서 읽어 변수화, trailer_exists 호출부와 --trailer 삽입부 양쪽 다 그 변수 참조
3. claude-code 식별자, Co-Authored-By 값을 CONF에서 읽어 변수화
4. bats tests/robustness-post-commit.bats tests/robustness-injection.bats tests/smoke.bats + shellcheck
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
hooks/post-commit의 resolve_self/HOOK_DIR 계산을 파일 앞부분으로 이동(기존엔 Hooks-Commit 계산부에만 있었음)해 CONF 경로를 일찍 확보. trailer 키 7종을 CONF에서 읽어 변수화하고 trailer_exists 호출부와 --trailer 삽입부 양쪽 다 동일 변수를 참조하도록 통일(GF-33류 오타 불일치가 이제 구조적으로 불가능). claude-code 식별자, Co-Authored-By 값도 CONF에서 읽음. 마커 파일명도 commit-msg/pre-commit과 일관되게 CONF에서 읽도록 전환. bats 16/16 통과(post-commit/injection/smoke), shellcheck 경고 없음. 실제 AI_AGENT=claude-code_2-1-0 커밋으로 트레일러 4종(AI-Tool/AI-Tool-Version/Co-Authored-By/Hooks-Commit) 값이 리팩토링 전과 정확히 동일함을 수동 검증.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/post-commit의 trailer 키 7종·AI 도구 식별자·Co-Authored-By 값·마커 파일명을 hooks/gitformat.conf에서 읽도록 전환. 존재확인부(trailer_exists)와 삽입부(--trailer)가 항상 같은 변수를 참조하게 되어 GF-33류 버그가 구조적으로 재발 불가능해짐. trailer_exists 등 로직은 그대로 유지. 16개 bats + shellcheck + 실제 커밋 수동검증으로 동작 무변경 확인.
<!-- SECTION:FINAL_SUMMARY:END -->
