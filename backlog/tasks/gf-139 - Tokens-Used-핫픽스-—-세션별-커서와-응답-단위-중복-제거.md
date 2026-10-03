---
id: GF-139
title: Tokens-Used 핫픽스 — 세션별 커서와 응답 단위 중복 제거
status: In Progress
assignee:
  - '@claude'
created_date: '2026-10-03 03:30'
updated_date: '2026-10-03 03:39'
labels:
  - hooks
  - bug
dependencies: []
references:
  - decision-5
  - decision-19
documentation:
  - backlog/docs/doc-16 - 토큰·툴콜-측정-방법과-한계.md
priority: high
type: bug
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Tokens-Used 값이 두 방향으로 틀리고 있다(2026-10-03 실측).

첫째, 세션이 바뀌면 첫 커밋이 0으로 찍힌다. post-commit은 트랜스크립트에서 이미 읽은 줄 수를 저장소에 커서 하나(.git/.gitformat-token-cursor)로만 저장하는데, 트랜스크립트는 세션마다 새 파일이다. 새 세션의 짧은 파일을 이전 세션의 줄 수(927)로 읽으면 새 줄이 없다고 판단해 0이 된다. 커밋 7fef01e가 이렇게 0으로 남았다. GF-129에 없는 버그다.

둘째, 0이 아닐 때는 2~3배 부풀려진다. 트랜스크립트는 API 응답 하나를 content 블록마다 한 줄씩 기록하고, 각 줄이 같은 usage를 반복해서 들고 있다. 지금 구현은 줄마다 더한다. 이번 세션 실측으로 assistant 215줄이 응답 109개였다. 이건 GF-129 AC#1과 같은 문제다.

GF-129는 GF-127→GF-128 재설계 뒤로 묶여 있어서, 값이 틀린 채로 커밋이 계속 쌓인다. 그래서 지금 post-commit에서 두 버그만 먼저 고친다. Tokens-Used 형식 변경(in/out/delta)과 커밋 귀속은 GF-129에 그대로 남긴다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 커서 파일에 세션 ID와 줄 수를 함께 저장하고, 세션 ID가 다르면 트랜스크립트 0줄부터 집계한다
- [ ] #2 예전 형식(숫자만) 커서는 세션 불일치로 취급해 0줄부터 집계한다
- [ ] #3 (requestId, message.id)가 같은 assistant 줄은 usage를 한 번만 더한다
- [ ] #4 requestId나 message.id가 없는 줄은 지금처럼 줄 단위로 더한다
- [ ] #5 Tool-Calls는 지금처럼 모든 줄의 tool_use 블록을 센다
- [ ] #6 새 세션 첫 커밋, 중복 줄, 예전 커서 형식을 다루는 테스트를 추가하고 기존 테스트의 커서 기대값을 새 형식에 맞춘다
- [ ] #7 doc-16에 세션별 커서와 응답 단위 계상을 반영하고, GF-129 AC#1이 이 핫픽스로 선반영됐다고 코멘트를 남긴다
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 python3 -m unittest discover -s tests 전체 통과
- [ ] #2 ruff check 통과
- [ ] #3 실제 커밋의 Tokens-Used가 트랜스크립트를 응답 단위로 따로 합산한 값과 일치하는지 확인
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. 테스트 먼저(TDD): 새 세션 첫 커밋, 같은 (requestId, message.id) 줄 1회 계상, 키 없는 줄 줄 단위, 예전 숫자 커서, 커서 경계를 걸친 응답 중복 방지
2. hooks/post-commit의 measure_claude_code_token_usage()/aggregate_usage() 수정 — 커서 형식 '<session_id> <줄 수>'
3. 기존 테스트의 커서 기대값 갱신
4. doc-16 갱신, GF-129 코멘트
5. 실제 커밋으로 값 대조 (구현은 서브에이전트, 검토·커밋 확인은 메인)
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
구현(서브에이전트, TDD):
- 테스트 먼저(a096f1d): 새 세션 첫 커밋 / 예전 숫자 커서 / 같은 (requestId, message.id) 줄 1회 계상 / id 없는 줄 줄 단위 / 커서 경계를 걸친 응답 중복 방지 5건 추가, 기존 커서 기대값을 'fake-session <N>'으로 갱신. 구현 전 실행 시 11건 중 8건 실패 확인.
- 구현(482fd24): hooks/post-commit의 aggregate_usage(lines, seen_keys)와 measure_claude_code_token_usage()만 수정. 커서 형식 '<세션 ID> <줄 수>'(개행 없음), 마지막 공백 기준 rsplit로 파싱. 세션 불일치·숫자만·손상 → 0줄부터. 같은 세션이면 커서 앞 구간을 aggregate_usage로 돌려 응답 키만 모으고(합산은 버림) 새 구간에서 그 키의 usage를 건너뜀. 앞 구간 파싱 실패도 transcript-parse-failed로 배치 실패 처리. 같은 응답의 usage는 첫 줄 값을 씀.
- 결과: python3 -m unittest discover -s tests → Ran 98 tests, OK. ruff check hooks/ tests/ + python 훅 → All checks passed.
- 실커밋 482fd24의 커서: '<세션 UUID> 1353' 형식으로 기록됨(Tokens-Used: 25915492, 이 값은 이번 세션의 첫 커밋 이후 구간 전체 합). DoD#3(응답 단위 별도 합산과 대조)은 메인에서 확인 필요.
- doc-16에 '현재 post-commit 구현 (GF-139 핫픽스)' 절 추가, GF-129에 선반영 코멘트 남김.
- 범위 밖 발견: doc-1 설치 가이드 표의 .gitformat-token-cursor 설명이 '(누적 줄 수)'로 남아 있음 — 손대지 않음.
<!-- SECTION:NOTES:END -->
