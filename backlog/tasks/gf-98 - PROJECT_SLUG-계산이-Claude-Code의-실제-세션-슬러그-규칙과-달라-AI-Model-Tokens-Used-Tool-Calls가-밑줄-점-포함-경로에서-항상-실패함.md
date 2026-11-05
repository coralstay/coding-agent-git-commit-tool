---
id: GF-98
title: >-
  PROJECT_SLUG 계산이 Claude Code의 실제 세션 슬러그 규칙과 달라
  AI-Model/Tokens-Used/Tool-Calls가 밑줄/점 포함 경로에서 항상 실패함
status: Done
assignee: []
created_date: '2026-09-18 16:21'
updated_date: '2026-09-19 01:45'
labels: []
milestone: m-2
dependencies: []
references:
  - GF-97
type: bug
ordinal: 95000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
hooks/post-commit의 trailer_ai_model()과 trailer_tokens_used()(각각 독립 사본, decision-9 관례)가 세션 트랜스크립트 경로를 PROJECT_SLUG="$(printf '%s' "$PWD" | tr '/' '-')"로 계산한다 - 슬래시만 하이픈으로 치환.

그런데 Claude Code가 실제로 ~/.claude/projects/ 아래 세션 디렉터리를 만들 때 쓰는 규칙은 "영숫자가 아닌 모든 문자를 하이픈으로 치환"이다(직접 재현: printf '%s' "$PWD" | tr -c 'A-Za-z0-9' '-' 가 실제 디렉터리명과 정확히 일치함을 확인). $HOME이나 작업 경로에 밑줄/점 등이 들어가면(예: 이 저장소를 쓰는 사용자의 $HOME=/Users/me, 밑줄 포함) 훅이 계산한 슬러그가 실제 디렉터리와 어긋나 트랜스크립트를 영영 찾지 못한다.

실제로 git log로 확인한 결과 이 저장소 자체의 GF-96 관련 커밋들(0cd8aff/3cbb904/a5ec61f/568af76)은 전부 AI-Model/Tokens-Used/Tool-Calls가 붙지 않았다 - "조회 실패 시 조용히 생략"으로 설계돼 있어 지금까지 에러 없이 숨어 있던 버그다.

GF-97(같은 함수를 다루는 unavailable+사유 명시 기능)과 밀접하게 관련되지만, 사용자 확인 결과 별도 버그로 분리해 처리한다. 같은 코드를 건드리므로 실행 순서/충돌에 주의(먼저 병합되는 쪽 기준으로 나머지를 rebase).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 trailer_ai_model()과 (GF-97 반영 이후) measure_claude_code_token_usage() 양쪽의 PROJECT_SLUG 계산이 Claude Code의 실제 규칙(영숫자가 아닌 모든 문자를 하이픈으로 치환, 예: tr -c A-Za-z0-9 -)과 일치하도록 수정된다
- [x] #2 밑줄/점이 포함된 경로(FAKE_HOME)에서도 트랜스크립트 파일을 정확히 찾아낸다는 것을 검증하는 bats 테스트가 tests/robustness-post-commit.bats에 추가된다
- [x] #3 이 저장소 자신에서 실커밋을 하나 만들어 AI-Model/Tokens-Used/Tool-Calls가 실제로 채워지는지 수동 확인하고 구현 노트에 근거를 남긴다
- [x] #4 shellcheck -s sh hooks/post-commit 와 bats tests/ 전체가 경고/실패 없이 통과한다
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. tests/robustness-post-commit.bats에 실패하는 테스트 추가: 저장소 최상위 디렉터리 이름 자체에 밑줄/점을 포함시켜(하위 디렉터리는 훅 PWD에 영향 없음 - 훅은 항상 worktree root에서 실행됨을 실측 확인) tr -c A-Za-z0-9 - 로 계산한 SLUG로 FAKE_HOME 트랜스크립트를 배치하고 AI-Model/Tokens-Used/Tool-Calls가 실값으로 채워지는지 검증. bats로 RED 확인.
2. hooks/post-commit의 trailer_ai_model()과 measure_claude_code_token_usage() 두 PROJECT_SLUG 라인을 tr -c A-Za-z0-9 - 로 수정.
3. 같은 테스트 재실행해 GREEN 확인, bats tests/ 전체 재실행해 회귀 없는지 확인.
4. 이 저장소 자신에서 실커밋 하나 만들어 AI-Model/Tokens-Used/Tool-Calls가 실제로 채워지는지 수동 확인, 근거를 구현 노트에 남김.
5. shellcheck -s sh hooks/post-commit 클린 확인.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
AC3 근거: (1) 실제 머신에서 tr -c 'A-Za-z0-9' '-' 를 $HOME=/Users/my_user 를 포함한 실제 프로젝트 경로(~/githubs/git-format)에 적용한 결과가 Claude Code가 실제로 만든 ~/.claude/projects/ 디렉터리명(-Users-my-user-githubs-git-format)과 정확히 일치함을 확인. 반면 수정 전 알고리즘(tr '/' '-')은 -Users-my_user-githubs-git-format(밑줄 보존)를 만들어 실제 디렉터리와 어긋남 - 버그와 수정 둘 다 실측 재현. (2) gf-98-worktree에서 FAKE_HOME + 수정된 알고리즘으로 계산한 SLUG 위치에 트랜스크립트를 배치하고 실제 git commit(HOME 오버라이드, bats 아님)을 만들어 AI-Model: claude-manual-verify / Tokens-Used: 168 / Tool-Calls: 2 트레일러가 크래프팅한 값과 정확히 일치함을 확인 - 검증 후 해당 임시 커밋은 git reset --hard로 되돌림(히스토리에는 남기지 않음, 근거는 이 노트에 기록).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/post-commit의 trailer_ai_model()과 measure_claude_code_token_usage() 두 곳 모두 PROJECT_SLUG 계산을 tr '/' '-' 에서 tr -c 'A-Za-z0-9' '-' 로 교정해 Claude Code의 실제 세션 슬러그 규칙과 일치시켰다. TDD로 진행: 저장소 최상위 디렉터리 이름에 밑줄/점을 넣어 두 알고리즘이 반드시 갈리게 만드는 bats 케이스를 tests/robustness-post-commit.bats에 먼저 추가해 RED(AI-Model 미검출)를 확인한 뒤 코드를 수정해 GREEN으로 전환했다(같은 버그를 흉내내던 기존 GF-96/GF-97 테스트 5곳의 SLUG 계산도 정확한 알고리즘으로 함께 갱신). 검증: (1) 실제 머신의 $HOME=/Users/my_user 경로에 새 알고리즘을 적용한 결과가 Claude Code가 실제로 만든 ~/.claude/projects/ 디렉터리명과 정확히 일치하고 구 알고리즘은 불일치함을 실측 확인, (2) FAKE_HOME 기반 실제 git commit(bats 아님)에서 AI-Model/Tokens-Used/Tool-Calls가 크래프팅한 값과 정확히 일치함을 확인 후 되돌림, (3) bats tests/ 103개 전체 통과(exit 0), (4) shellcheck -s sh hooks/post-commit 경고 없음. 커밋 3개(chore/test/fix) + 구현노트 chore 1개, push/PR 없음.
<!-- SECTION:FINAL_SUMMARY:END -->
