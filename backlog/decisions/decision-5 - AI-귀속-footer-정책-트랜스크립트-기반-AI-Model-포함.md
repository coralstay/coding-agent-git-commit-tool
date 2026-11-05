---
id: decision-5
title: 'AI 귀속 footer 정책: 트랜스크립트 기반 AI-Model 포함'
date: '2026-08-24 03:09'
status: accepted
---
## Context

AI 에이전트가 만든 커밋에 "어떤 도구/모델이 작업했는지"를 남기고 싶다. 최초 요구사항은
"자가신고 방식 말고 강제할 방법"이었다. 조사 결과:

- Claude Code는 하위 프로세스(git hook 포함)에 `AI_AGENT`(도구+버전), `CLAUDE_CODE_SESSION_ID`,
  `CLAUDE_EFFORT`, `CLAUDECODE` 환경변수를 **애플리케이션이 직접 주입**한다 — LLM이 스스로
  export하는 값이 아니므로 사실상 강제 가능.
- 반면 정확한 모델명(예: claude-sonnet-5)은 이 환경변수들에 없다. Claude Code의 자체 훅
  페이로드(`PreToolUse`/`PostToolUse`)에도 모델 필드가 없음을 claude-code-guide 조사로 확인.
- **단, 세션 트랜스크립트 로그(`~/.claude/projects/<slug>/<session-id>.jsonl`)의 각
  assistant 턴에는 `message.model` 필드가 있고, 이는 Anthropic API 응답을 Claude Code가
  그대로 기록한 값이다(서버 발급 사실, 자가신고 아님)** — 실제로 이 세션에서
  `"message.model":"claude-sonnet-5"` 를 직접 확인함. 파일 경로는
  `$CLAUDE_CODE_SESSION_ID` + `$PWD`를 `tr '/' '-'` 한 슬러그로 프로그래밍적으로 유도 가능.

## Decision

`post-commit` 훅이 AI 관련 footer 트레일러를 자동 삽입한다(모두 `Verify-Bypassed`와 같은
amend 메커니즘 사용, `--no-verify` 재귀가드 공유):

| 트레일러 | 값 출처 | 강제 수준 |
|---|---|---|
| `AI-Tool` / `AI-Tool-Version` | `AI_AGENT` 환경변수 파싱 | 강제 (프로세스 주입) |
| `AI-Model` | **Claude Code**: 세션 트랜스크립트 JSONL에서 `git commit`을 실행한 시점에 가장 가까운 assistant 턴의 `message.model` 추출. **그 외 AI 툴**: 트랜스크립트 채널이 없으므로 `git config gitformat.aiModel` 값 사용, 단 `CLAUDECODE`/`AI_AGENT` 감지 시 미설정이면 커밋 거부(존재 강제) + 알려진 모델 ID 화이트리스트 검증 + 도구-벤더 일관성 검사 | Claude Code: 강제급(서버 발급 사실) / 그 외: 존재+형식 강제, 진실성 검증 불가 |
| `Co-Authored-By` | AI 환경 감지 시 `Claude <noreply@anthropic.com>` 형태로 자동 삽입 | 자동 |
| `Hooks-Commit` | git-format 저장소 자체의 `git rev-parse --short HEAD` (수동 버전 문자열 대신) | 완전 자동 |

트랜스크립트 조회 시 훅은 `message.model` 필드 하나만 추출하고, 대화 내용 자체는 절대
로그하거나 복제하지 않는다(프라이버시).

## Consequences

- Claude Code에서 만든 커밋은 실제 API가 응답한 모델명이 정확히 남는다 — 이후 어떤 모델이
  어떤 작업을 했는지 `git log`만으로 추적 가능(비용 분석, 회고에도 활용 가능).
- 트랜스크립트 파일 포맷이 Claude Code 업데이트로 바뀌면 파싱 로직이 깨질 수 있음 — 실패
  시 조용히 `AI-Model` 트레일러를 생략하도록 방어적으로 구현(커밋 자체를 막지는 않음).
- 서브에이전트(fork)가 커밋을 실행하는 경우 세션 파일이 다를 수 있어 부정확할 수 있음 —
  1차 구현에서는 알려진 한계로 문서화하고, 필요시 `tool_use`가 `git commit`을 포함하는
  가장 최근 항목을 찾는 방식으로 정밀도를 높인다.
- Claude Code 외 툴 사용자는 상대적으로 약한 보장(존재 강제)만 받는다는 점을 README에
  명시해 기대치를 관리한다.

## Amendment (2026-08-24, GF-13)

`AI-Session-Id`(`CLAUDE_CODE_SESSION_ID`) 트레일러를 제거했다. 세션 식별자를 공개
저장소의 커밋 이력에 영구히 남기는 게 프라이버시/추적 관점에서 바람직하지 않다는
판단. `CLAUDE_CODE_SESSION_ID` 자체는 `AI-Model` 조회를 위해 세션 트랜스크립트 파일
경로를 찾는 데 여전히 내부적으로만 쓰고, 그 값을 커밋에 남기지는 않는다.

## Amendment (2026-09-19, GF-97)

GF-96이 추가한 `Tokens-Used`/`Tool-Calls`(세션 트랜스크립트 `message.usage` 델타
합산)는 원래 측정 조건(jq/트랜스크립트/세션ID) 중 하나라도 실패하면 `AI-Model`과
동일하게 두 트레일러를 조용히 생략했다. 실사용 중 "AI 커밋인데 토큰을 안 남겼다"와
"측정 자체가 불가능했다"를 구분할 수 없다는 문제, 그리고 게이트가
`AI_TOOL_ID = claude-code`로 앞단에서 막혀 다른 AI 도구의 커밋은 애초에 트레일러를
전혀 받지 못한다는 문제가 확인돼, 다음과 같이 정책을 보완한다.

- **조용한 생략 → 사유 명시**: 측정에 실패하면 트레일러 값 자체를
  `unavailable (사유 슬러그)`로 명시 기록한다. 사유 슬러그: `no-session-id` /
  `jq-not-installed` / `transcript-not-found` / `transcript-unreadable` /
  `transcript-parse-failed`. 새 트레일러 키는 만들지 않고 기존 두 트레일러 값 안에
  괄호로 붙인다. 커밋을 막지는 않는다(best-effort 유지).
- **범위 확대**: `AI_TOOL_ID`가 비어있지 않은 모든 커밋(=AI 도구가 감지된 모든
  커밋)에 두 트레일러를 붙인다. 다만 decision-15가 이미 "Claude Code 외에는 신뢰
  가능한 로컬 토큰 채널이 없다"고 결론지었으므로, claude-code 외 도구는 실측을
  구현하지 않고 항상 `unavailable (no-usage-channel)`을 남긴다 — `AI-Tool` 케이스
  분기 관례를 따라 나중에 새 채널이 생기면 분기 하나만 추가하면 되는 구조로
  준비해둔다.
- **0과 unavailable 구분**: 실제로 트랜스크립트를 읽어 합산한 값이 0이어도
  `unavailable`이 아니라 `Tokens-Used: 0`/`Tool-Calls: 0`으로 그대로 기록한다(기존
  `-gt 0` 가드 제거). 커서 파일은 실측 성공 시에만 갱신한다.
- **델타-근사치 한계 명문화**: 이 값들은 "이 커밋을 만드는 데 정확히 필요했던
  토큰"이 아니라 "직전 커밋 이후 이 세션에서 소비된 토큰"의 근사치일 뿐이다 — 그
  구간에 이 커밋과 무관한 대화/탐색이 섞이면 과대평가될 수 있다. 이는 위
  Consequences의 "서브에이전트가 커밋을 실행하는 경우 세션 파일이 다를 수 있어
  부정확할 수 있음" 캐비어트와 같은 결의 한계이며, 더 정확한 귀속 방법(예: 특정
  `tool_use`가 `git commit`을 포함하는 지점까지만 잘라서 집계하는 방식 등)은 아직
  찾지 못했다 — README에도 실험적 상태임을 정직하게 명시한다.
- **범위 밖**: `AI-Model`/`trailer_ai_model()`은 이번 변경 대상이 아니다(여전히
  조용한 생략 유지). 검증 중 발견한 `PROJECT_SLUG` 계산 버그(밑줄 등 비-슬래시
  특수문자가 든 `$HOME` 경로에서 트랜스크립트를 영영 못 찾음 - `AI-Model`도 동일
  영향)는 별도 버그 태스크(GF-98)로 분리했고, 이번 변경에서는 그 버그가 있는 채로
  로직을 그대로 이식했다.
