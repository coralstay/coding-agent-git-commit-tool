---
id: decision-28
title: Signed-off-by 유지는 유저가 직접 확정했다 (decision-25 보완)
date: '2026-10-03 12:48'
status: accepted
---
## Context

decision-19(2026-09-25)가 `Signed-off-by` 제거를 정했지만, 그 실행을 맡은 GF-128이 아직
To Do라 `post-commit`은 계속 이 트레일러를 붙여 왔다. 그 사이 decision-25(2026-10-03)가
"문서끼리 충돌하면 최근 문서를 우선한다"는 규칙을 적용해 제거 조항을 대체하고 유지로
정했다. 근거는 decision-24·DRAFT-19가 `Signed-off-by`와 실제 커미터의 불일치를 이력
재작성의 증거로 쓴다는 것이었다.

그 유지 판단은 날짜 규칙을 기계적으로 적용한 결과였고, 유저에게 `Signed-off-by` 자체를
묻고 정한 것은 아니었다. 2026-10-03 유저가 "지웠는데 왜 남아 있나"라고 물어 경위를
설명했고, 유저가 직접 유지를 골랐다.

## Decision

**`Signed-off-by`는 유지한다 — 유저가 직접 확정했다.** decision-25의 유지 조항과 근거는
그대로이고, 이 decision은 그 판단이 유저 확인을 거쳤다는 사실만 보탠다.

## Consequences

- GF-128 AC #10("Signed-off-by는 계속 삽입한다")이 그대로 유효하다. 설명 본문의
  "Signed-off-by를 없앤다"는 GF-128 코멘트 #1과 이 decision으로 대체된다.
- 이 트레일러를 실제로 대조하는 코드는 아직 없다(DRAFT-19가 draft 상태). 그 전까지는
  사람이 `git log`로 커미터와 비교할 때만 쓰인다.
- 나중에 같은 질문이 나오면 decision-19가 아니라 이 decision을 본다.

