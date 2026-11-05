---
id: decision-20
title: 에이전트 판정은 검증 가능한 신호만 쓴다 — SESSION_ID와 PID
date: '2026-09-25 19:34'
status: accepted
---
## Context

현재 `post-commit`의 `trailer_ai_tool()`은 `AI_AGENT` 환경변수 **하나만** 보고, 비어 있으면
AI 관련 트레일러를 **조용히 전부 생략**한다. 환경변수 하나가 빠지면 에이전트가 만든 커밋이
사람 커밋과 구별되지 않는다. git-format의 목적이 "AI가 남긴 작업 이력을 나중에 분석할 수
있게 만드는 것"이므로 이건 목적을 직접 훼손한다.

실측으로 Claude Code가 하위 프로세스에 주입하는 신호를 조사했다(전체 표는 doc-17).
핵심은 **검증 가능성**의 차이다.

- `CLAUDE_CODE_SESSION_ID` → 트랜스크립트 파일 경로를 만든다. **파일 실재로 확인 가능.**
- `CLAUDE_PID` → `ps -p <pid> -o comm=`이 `claude`를 반환하는지 **프로세스 테이블로 확인 가능.**
- `CLAUDECODE=1`, `CLAUDE_CODE_ENTRYPOINT` 등 → 값의 존재 여부뿐. 위조도 누락도 쉽다.

## Decision

**에이전트 판정은 검증 가능한 두 신호로만 한다.** `CLAUDE_CODE_SESSION_ID`가 실재하는
트랜스크립트 파일을 가리키거나, `CLAUDE_PID`가 살아 있는 `claude` 프로세스를 가리키면
에이전트 커밋이다.

- `AI_AGENT`는 **도구와 버전의 값 출처로만** 쓴다. 존재 여부를 판정 근거로 쓰지 않는다.
- `AI_AGENT`가 없으면 `CLAUDE_CODE_EXECPATH`의 경로에서 버전을 보강한다(경로에 버전이 들어
  있다).
- 플래그성 변수(`CLAUDECODE` 등)는 판정에 쓰지 않는다.
- **구성요소를 못 구해도 트레일러 줄은 반드시 남긴다** — `version-unavailable`,
  `model-unavailable`. 조용한 생략이 곧 잘못된 귀속이다.
- 세션 ID는 트랜스크립트를 찾는 데만 쓰고 커밋에 남기지 않는다(decision-5 amendment 유지).
- `CLAUDE_CODE_MESSAGING_SOCKET`/`_TOKEN`은 **인증 정보**다. 커밋 메시지에 절대 남기지 않는다.

## Consequences

- 환경변수 하나가 빠져도 에이전트 커밋이 사람 커밋으로 위장되지 않는다.
- 판정이 파일시스템·프로세스 상태에 의존하므로, 훅이 도는 시점에 세션이 살아 있어야 한다.
  세션이 끝난 뒤 별도로 커밋하면(예: 나중에 셸에서 직접) 에이전트로 판정되지 않는다 —
  실제로 그때는 사람이 커밋한 것이므로 옳은 동작이다.
- 판정 기준이 Claude Code에 특화돼 있다. 다른 AI 도구는 동등한 검증 채널이 없어
  `AI-Agent`가 붙지 않는다(기존 decision-15·17의 결론을 유지).
- 컨슈머 저장소가 Claude Code 프로젝트가 아니면 AI 트레일러가 아예 붙지 않는다 — 의도된
  동작이다.
