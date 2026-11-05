---
id: decision-30
title: Signed-off-by는 사람이 만든 커밋에만 붙인다 (decision-25·28의 유지 조항 대체)
date: '2026-10-04 01:58'
status: accepted
---
## Context

`post-commit`은 모든 커밋에 커미터 정보로 `Signed-off-by`를 붙여 왔다(decision-25, 유저 확정은
decision-28). 2026-10-04 유사 프로젝트 조사(doc-22)에서 이 트레일러가 업계에서 쓰이는 의미와
충돌한다는 게 드러났다.

- Linux 커널 정책: "AI agents MUST NOT add Signed-off-by tags. Only humans can legally certify
  the DCO."
- ai-attribution-hooks, crashoverride 가이드: `Signed-off-by`를 AI 커밋에 대한 사람의 책임
  인정으로 쓴다.

에이전트 커밋에 훅이 자동으로 붙이면, DCO를 요구하는 저장소에서 사람이 인증하지 않은 커밋이
인증된 것처럼 보인다(DRAFT-22).

## Decision

**`Signed-off-by`는 사람이 만든 커밋에만 붙인다** — 유저 결정(2026-10-04).

- "사람이 만든 커밋"은 훅이 AI 도구를 감지하지 못한 커밋이다. 판정은 `AI-Agent`를 붙일지
  정하는 신호와 같은 것을 쓴다(지금은 `AI_AGENT` 환경변수, GF-130에서 재작성 예정).
- 에이전트 커밋에는 붙이지 않는다. 사람이 메시지에 직접 쓴 `Signed-off-by`는 키 단위 중복
  판정(GF-128)에 따라 그대로 둔다 — 운영자가 스스로 서명하는 것은 막지 않는다.

decision-25의 `Signed-off-by` 유지 조항과 decision-28을 이 decision이 대체한다.

## Consequences

- GF-128 AC #10을 이 decision에 맞게 고친다.
- DRAFT-19가 `Signed-off-by`와 실제 커미터의 불일치를 이력 재작성의 증거로 쓰려던 검사는
  사람 커밋에만 적용된다. 에이전트 커밋은 다른 증거(예: `Hooks-Commit`, 커밋 객체의
  committer)로 봐야 한다.
- 판정이 에이전트 감지에 기대므로, 감지가 틀리면(에이전트인데 신호가 없으면) 에이전트
  커밋에 `Signed-off-by`가 붙는다. 감지의 정확도는 GF-130의 몫이다.
- DRAFT-22는 이 decision과 GF-128로 처리되어 보관한다.
