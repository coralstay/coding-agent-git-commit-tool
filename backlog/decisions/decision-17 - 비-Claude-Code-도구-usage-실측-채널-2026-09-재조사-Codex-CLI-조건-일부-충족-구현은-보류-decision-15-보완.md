---
id: decision-17
title: >-
  비-Claude-Code 도구 usage 실측 채널 2026-09 재조사: Codex CLI 조건 일부 충족, 구현은 보류
  (decision-15 보완)
date: '2026-09-25 02:41'
status: accepted
---
## Context

GF-97은 `trailer_tokens_used()`를 `AI_TOOL_ID` 분기 디스패처로 만들면서 claude-code가
아닌 도구는 전부 `unavailable (no-usage-channel)`로 처리하게 했다. GF-114는 "그 판단이
아직 유효한가"를 다시 확인하기 위한 태스크이고, 이 문서는 2026-09-25 재조사 결과다.

git-format이 usage 값을 실측으로 인정하는 조건은 decision-5/decision-15와 같은 두 개다.

1. **세션 상관관계 채널** — AI 도구 프로세스가 하위 프로세스(git 훅 포함)에 "지금 이
   커밋을 만든 세션이 어느 것인지" 프로그래밍적으로 특정할 수 있는 값을 주입한다.
2. **서버가 확정한 usage 값** — 그 세션 기록에 남는 토큰 수가 사용자가 로컬에서 고쳐
   쓸 수 있는 설정값이 아니라 API 응답이 확정해 되돌려준 사실이다.

decision-15는 같은 8개 도구를 2026-09 초에 조사해 어느 것도 두 조건을 동시에
만족하지 않는다고 결론지었다. 이번 재조사에서 **조건 1의 상태가 실제로 바뀐 도구가
하나 나왔다**.

| 도구 | 조건 1 (상관관계 채널) | 조건 2 (서버 확정 usage) | decision-15 대비 |
|---|---|---|---|
| OpenAI Codex CLI | **충족** — `CODEX_THREAD_ID`가 셸 툴 실행 시 하위 프로세스에 노출됨(0.125.0에서 확인) | **불충분** — rollout jsonl에 `token_count`/`token_usage_record`로 usage가 남지만 현재 과소계상이 문서화돼 있다 | **변화 있음** |
| Google Gemini CLI | 미충족 — 셸 서브프로세스에는 `GEMINI_CLI=1` 불리언만 주입된다. `session_id`는 Gemini CLI 자체 hook 컨텍스트에만 전달되고, git 훅은 그 페이로드를 받지 못한다 | 부분 — 세션 히스토리에 토큰 통계가 저장되지만 경로가 `~/.gemini/tmp/<project_hash>/chats/`로 프로젝트 단위라 세션 특정이 안 된다 | 조건 2만 진전 |
| Cursor | 미충족 — 여전히 세션/대화 ID env var이 없다(공개 기능요청 상태). `CURSOR_INVOKED_AS`는 호출 방식 표시용 문자열이다 | 미확인 | 변화 없음 |
| GitHub Copilot CLI | 미충족 — 문서화된 세션 ID env var 없음. `COPILOT_MODEL` 등은 사용자가 설정하는 입력값이다 | 미확인 | 변화 없음 |
| Aider / Cline / Windsurf / Amazon Q Developer CLI | 미충족 | 미확인 | 변화 근거를 찾지 못함 |

Codex CLI를 더 본 결과는 이렇다.

- 조건 1은 확실히 충족된다. `CODEX_THREAD_ID`가 셸 툴 실행 환경에 실제로 들어오는
  것이 openai/codex#19937에서 재현 예시와 함께 확인된다(그 이슈가 "not planned"로
  닫힌 것은 **stdio MCP 서버**에도 같은 값을 넘겨달라는 별개 요청이고, 셸 툴 쪽
  노출은 이미 동작하는 동작으로 전제돼 있다).
- rollout 파일은 `~/.codex/sessions/YYYY/MM/DD/rollout-*-<thread-id>.jsonl` 형태라
  `CODEX_THREAD_ID`만 있으면 경로를 특정할 수 있다 — 구조적으로는 Claude Code와
  같은 모양이다.
- 그런데 조건 2가 지금은 성립하지 않는다. openai/codex#47003(2026-09-21, open)이
  auto-compaction 요청의 usage가 rollout 집계에 **전혀 반영되지 않음**을
  기록한다: 0.154/0.155에서는 `token_usage_record`는 써지지만 다음 `token_count`의
  `total_token_usage`가 변하지 않고, 0.147에서는 레코드 자체가 안 써진다. 감사한
  compaction 요청 68건 중 68건이 누적치에 0을 기여했다. openai/codex#42025는
  `token_count` 레코드 이후 로컬 히스토리 프로젝션이 멈추는 별개 버그다.
- 모델 이름 쪽은 decision-15의 결론이 그대로 유지된다. openai/codex#47779(2026-09-24,
  open)이 rollout의 model 필드가 서버가 실제로 서비스한 모델이 아니라 요청값의
  메아리임을 확인한다 — 존재하지 않는 `gpt-9.9-does-not-exist`도 그대로 되돌아온다.

## Decision

**Codex CLI용 usage 실측을 지금 구현하지 않는다.** `trailer_tokens_used()`의 분기와
`no-usage-channel` 처리를 그대로 둔다. hooks/*에 스텁이나 미리 준비된 함수도 두지
않는다.

이유는 "채널이 없다"가 아니라 **"채널의 값이 지금 틀렸다"**로 바뀌었다. 과소계상이
문서화된 수치로 `Tokens-Used` 트레일러를 채우면, git-format이 실측이라고 표시한 값이
실제보다 작다는 뜻이 된다 — 자가신고를 거부한 이유(값의 신뢰성)와 같은 이유로 이
수치도 받을 수 없다. 사유 슬러그를 하나 더 만들어 구분하는 방법도 택하지 않는다:
현재 rollout usage 스키마 자체가 버전마다 흔들리고 있어(0.147 vs 0.154/0.155)
지금 무엇을 코드로 고정해도 곧 어긋난다.

decision-15는 철회하지 않는다. 이 문서는 조사 시점과 대상 범위를 갱신하는 보완이며,
`AI-Model`에 대한 decision-15의 결론(비-Claude-Code 도구는 자가신고 유지)은
openai/codex#47779로 오히려 재확인됐다.

## Consequences

- 코드·문서상 동작 변화는 없다. `Tokens-Used`/`Tool-Calls`는 계속 claude-code에서만
  실측되고 나머지는 `unavailable (no-usage-channel)`이다.
- **재검토 트리거**(이 중 하나라도 성립하면 GF-114를 다시 연다):
  - openai/codex#47003이 닫히고, compaction 요청 usage가 rollout의
    `total_token_usage`에 반영되는 버전이 안정 릴리스로 나온다.
  - Codex CLI가 rollout의 usage 레코드 스키마를 문서화된 인터페이스로 약속한다
    (버전 간 변동이 멈춘다).
  - Gemini CLI가 셸 서브프로세스에 세션 ID를 주입하기 시작한다 — 그러면 이미 있는
    세션 토큰 통계와 합쳐져 두 조건이 동시에 충족된다.
  - 다른 도구가 위 두 조건을 만족하는 로컬 채널을 새로 노출한다.
- 트리거가 성립해 구현하게 되면 작업 모양은 decision-15 시점 예상과 같다:
  `trailer_tokens_used()`의 분기에 `measure_claude_code_token_usage()`와 같은 패턴의
  도구별 실측 함수를 하나 추가하고, 실패 사유 슬러그와 커서 파일 규약을 재사용한다.
- 조사 근거 URL은 GF-114 태스크 노트에 남겼다.
