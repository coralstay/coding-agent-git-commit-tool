---
id: DRAFT-22
title: Signed-off-by 자동 삽입을 재검토한다 — DCO 의미 충돌
status: Draft
assignee: []
created_date: '2026-10-04 01:43'
updated_date: '2026-10-04 01:43'
labels:
  - trailers
  - policy
dependencies: []
references:
  - decision-25
  - decision-19
documentation:
  - backlog/docs/doc-22 - 유사-프로젝트-조사-—-AI-커밋-출처-기록-도구-비교.md
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
post-commit은 모든 커밋에 커미터 정보로 Signed-off-by를 자동으로 붙인다(decision-25가 decision-19의 제거 조항을 대체해 유지). 그런데 Signed-off-by는 관례상 사람이 DCO를 인증한다는 서명이다.

- Linux 커널 정책: "AI agents MUST NOT add Signed-off-by tags. Only humans can legally certify the DCO."
- ai-attribution-hooks와 crashoverride 가이드는 Signed-off-by를 AI 커밋에 대한 사람의 책임 인정으로 쓰고, AI 트레일러가 있으면 이를 요구한다.

이 훅이 에이전트 커밋에도 자동으로 붙이면, DCO를 요구하는 저장소에 설치했을 때 사람이 인증하지 않은 커밋이 인증된 것처럼 보인다. 조사 근거는 doc-22.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Signed-off-by를 유지·제거·사람 커밋에만 붙임 중 하나로 정하고 decision으로 기록한다
- [ ] #2 결정에 맞게 GF-128 AC #10을 갱신한다
- [ ] #3 DCO를 요구하는 저장소에 설치할 때의 동작이 README에 적혀 있다
<!-- AC:END -->
