---
id: GF-119
title: post-commit PROJECT_SLUG의 Claude Code 내부 경로 규칙 암묵 결합 문서화/완화
status: Done
assignee: []
created_date: '2026-09-19 15:46'
updated_date: '2026-09-25 02:37'
labels: []
dependencies: []
documentation:
  - backlog/docs/doc-6 - 주의점과-한계.md
  - backlog/docs/doc-3 - AI-귀속-트레일러-레퍼런스.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
hooks/post-commit:225의 PROJECT_SLUG=$(printf '%s' "$PWD" | tr -c 'A-Za-z0-9' '-')가 Claude Code 트랜스크립트 경로를 재구성하는 데 쓰이는데, 이는 Claude Code 내부 slug 알고리즘과 암묵적으로 결합돼 있다. Claude Code가 알고리즘을 바꾸면 AI-Model/Tokens-Used 측정이 에러 없이 조용히 실패한다. 이 결합 지점을 코드 주석/문서로 명시하거나, 실패를 감지 가능하게 만들지 검토.

발견 경위: 2026-09-20 '이 프로젝트의 부족한점?' 조사(Explore agent, hooks/post-commit:225)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 hooks/post-commit의 슬러그 계산 지점 주석에 '이것은 Claude Code의 문서화되지 않은 내부 규칙에 의존하는 외부 계약이며, 상대가 규칙을 바꾸면 이쪽이 조용히 어긋난다'는 성격이 명시된다
- [x] #2 슬러그가 어긋났을 때 사용자가 관측할 수 있는 신호(Tokens-Used/Tool-Calls의 unavailable (transcript-not-found))와 AI-Model은 신호 없이 누락된다는 비대칭이 문서에 기록된다
- [x] #3 결합이 깨졌을 때의 진단 절차가 문서에 남는다
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. claude_transcript_path()의 현재 상태와 실패 경로를 읽어, 결합이 깨졌을 때 실제로 어떤 신호가 남는지 확인한다
2. post-commit 주석에 이 지점이 '외부 계약 의존'이라는 성격과 트레일러별 신호 비대칭을 명시한다
3. doc-6 '한계'에 같은 내용 + 실행 가능한 진단 절차(실제 디렉터리명 vs 훅이 계산하는 슬러그 비교)를 추가한다
4. 진단 절차를 직접 실행해 동작을 확인하고 ruff/bats로 회귀가 없음을 확인한다
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
코드 변경은 주석뿐이고 동작은 바꾸지 않았다 — 조사 결과 '실패를 감지 가능하게 만드는' 부분은 이미 구현돼 있었기 때문이다. measure_claude_code_token_usage()가 트랜스크립트 부재를 MEASUREMENT_REASON='transcript-not-found'로 남기고, 그 값이 Tokens-Used/Tool-Calls 트레일러에 'unavailable (transcript-not-found)'로 찍힌다(tests/robustness-post-commit.bats의 GF-97 테스트가 이 동작을 이미 고정). 반면 trailer_ai_model()은 decision-5의 의도된 fail-open이라 신호 없이 트레일러만 생략한다. 그래서 남은 실제 결함은 '이 비대칭과 진단 방법이 어디에도 안 적혀 있다'는 문서 공백이었고, 그것만 메웠다.

AI-Model도 사유를 남기도록 바꾸는 선택지는 택하지 않았다 — decision-5가 '트랜스크립트 조회 실패는 어떤 이유든 커밋을 막지 않고 조용히 생략'을 명시적으로 결정했고, 이를 뒤집는 건 GF-119의 범위('문서화/완화')를 넘는 정책 변경이다.

검증 증거: (AC1) hooks/post-commit:165-175 주석에 '이 저장소에서 외부 계약에 의존하는 유일한 지점', '우리가 지킬 수 있는 약속이 아니다', '상대가 규칙을 바꾸면 예외 없이 없는 경로를 반환하고 측정은 조용히 어긋난다'가 들어갔다. (AC2) doc-6 '한계'의 신규 항목에 Tokens-Used/Tool-Calls는 'unavailable (transcript-not-found)'로 사유가 남고 AI-Model은 decision-5 fail-open으로 신호 없이 누락된다는 비대칭이 기록됐다 — 이 동작은 bats 'GF-97 트랜스크립트 파일이 없으면 ... transcript-not-found로 명시된다'가 이미 고정하고 있다. (AC3) doc-6에 적은 진단 절차를 실제로 실행했다: python3 -c로 계산한 슬러그가 '-Users-my-user-githubs-git-format'이고 ls ~/.claude/projects/에 동일한 디렉터리가 존재해 일치를 확인했다 — 절차가 현재 규칙에서 참을 반환한다는 것과 불일치 시 감지가 가능하다는 것이 함께 확인된다. 회귀: ruff check . 통과, bats tests/ 104/104 통과(실패 0).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/post-commit의 claude_transcript_path() 슬러그 계산이 Claude Code의 문서화되지 않은 내부 규칙에 의존한다는 사실을 주석으로 명시하고, doc-6 '한계'에 트레일러별 신호 비대칭과 실행 가능한 진단 절차를 추가했다. 동작 변경은 없다 — 조사 결과 '실패 감지' 부분은 이미 MEASUREMENT_REASON='transcript-not-found'로 구현돼 bats가 고정하고 있었고, AI-Model의 무신호 누락은 decision-5가 의도한 fail-open이어서 뒤집지 않았다. 남아 있던 실제 결함은 이 비대칭과 진단 방법이 어디에도 없다는 문서 공백이었다. 진단 절차는 직접 실행해 슬러그 일치를 확인했고, ruff 통과 + bats 104/104로 회귀가 없음을 확인했다.
<!-- SECTION:FINAL_SUMMARY:END -->
