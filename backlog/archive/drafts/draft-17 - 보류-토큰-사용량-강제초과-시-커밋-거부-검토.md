---
id: DRAFT-17
title: '[보류] 토큰 사용량 강제(초과 시 커밋 거부) 검토'
status: Draft
assignee: []
created_date: '2026-09-24 09:28'
updated_date: '2026-09-25 19:55'
labels:
  - parked
  - post-migration
dependencies: []
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## 배경

현재 post-commit은 Tokens-Used/Tool-Calls 트레일러를 세션 트랜스크립트에서 측정해 기록만 한다(GF-96/GF-97). 유저가 "기능 추가할 때 토큰 사용량을 강제한다면 프로젝트를 어떻게 만드는 게 맞나"를 물어 구조적 제약을 먼저 기록해둔다.

## 핵심 구조 제약

post-commit은 커밋을 막을 수 없다. 이 훅이 실행되는 시점엔 커밋 객체가 이미 생성된 뒤라 종료 코드를 무엇으로 반환하든 git이 커밋을 되돌리지 않는다(지금은 git commit --amend로 트레일러를 소급 삽입하는 용도로만 쓴다).

따라서 "토큰 사용량 초과 시 커밋 거부" 같은 강제 기능은 반드시 pre-commit이나 commit-msg(둘 다 커밋 생성 전에 실행되고 실제로 막을 수 있음) 쪽에 있어야 한다. 그러려면 지금 post-commit에만 있는 트랜스크립트 측정 로직을 커밋 생성 전 시점에서도 쓸 수 있게 재설계해야 한다.

## 보류 사유

Python 전환 중에 이런 신규 기능을 끼워 넣으면 "동작 동일성 검증"이라는 이번 전환의 최우선 목표와 충돌한다. 스텁 코드도 미리 넣지 않는다.

## 재개 조건

Python 전환 완료 후. 착수 전에 정할 것: 측정 대상(어떤 AI 도구까지), 임계값 설정 위치(gitformat.conf), 초과 시 동작(거부 vs 경고), 자가신고 값의 신뢰도 문제(GF-84에서 이미 한계가 확인됨).
<!-- SECTION:DESCRIPTION:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
보류 상태이므로 구현 계획이 아니라 재개 시 착수 순서를 기록한다.

1. Python 전환(DRAFT-8~14) 완료를 확인한다
2. 현재 post-commit 전용인 트랜스크립트 측정 로직을 커밋 생성 전 시점에서도 호출 가능한지 조사한다(측정 대상 데이터가 커밋 전에 존재하는지가 관건)
3. 임계값 설정 위치와 키 이름을 gitformat.conf에 설계한다
4. 초과 시 동작을 결정한다 - 거부 vs 경고. 거부라면 pre-commit과 commit-msg 중 어디에 둘지
5. 자가신고 값의 신뢰도 한계(GF-84에서 이미 확인됨)를 재검토해 강제의 근거로 쓸 수 있는 수준인지 판단한다
<!-- SECTION:PLAN:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: claude
created: 2026-09-25 19:55
---
2026-09-26 재설계로 이 드래프트의 핵심 구조 제약이 해소된다. 여기 적힌 "post-commit은 커밋을 막을 수 없으니 측정 로직을 커밋 생성 전 시점에서도 쓸 수 있게 재설계해야 한다"가 DRAFT-19~24(prepare-commit-msg 통합, decision-18)에서 실제로 이뤄진다 — 측정이 커밋 전에 돌고 exit 1로 커밋을 막을 수 있는 훅으로 옮겨간다. 재개 조건을 "Python 전환 완료 후"에서 "DRAFT-23(토큰 측정 재작성) 완료 후"로 갱신한다. 착수 시 전제가 달라진 점: Tokens-Used 형식이 in/out/delta 세 값으로 바뀌므로(decision-19) 임계값도 어느 값 기준인지 정해야 한다.
---
<!-- COMMENTS:END -->
