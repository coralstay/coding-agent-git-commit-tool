---
id: decision-15
title: '비-Claude-Code AI 도구 AI-Model 검증 불가 확인: 자가신고 유지 (decision-5 보완)'
date: '2026-09-03 22:21'
status: accepted
---
## Context

decision-5는 Claude Code의 `AI-Model` 트레일러가 신뢰할 수 있는 이유를 두 가지로
설명한다: (1) Claude Code 프로세스가 하위 프로세스(git hook 포함)에
`CLAUDE_CODE_SESSION_ID`를 직접 주입해 `post-commit`이 "지금 커밋을 만든
세션이 어느 파일인지" 프로그래밍적으로 특정할 수 있고, (2) 그 세션
트랜스크립트(`~/.claude/projects/<slug>/<session>.jsonl`)의 `message.model`이
Anthropic API 응답을 그대로 옮겨 적은 값이라 사용자가 로컬에서 임의로 바꿔
쓸 수 있는 값이 아니다(서버 발급 사실). 반면 그 외 AI 도구는 사용자가
`gitformat.aiModel`에 입력한 값을 존재/화이트리스트 여부만 확인하고 그대로
믿는다(README "한계" 항목).

GF-84는 "Claude Code 말고 다른 주요 AI 코딩 도구도 이 두 조건을 동시에
만족하는 로컬 채널을 갖고 있는가"를 실제로 조사했다(주요 검색 엔진 기준
2026-09 시점 최신 문서/이슈 확인). 조사 대상: Cursor, GitHub Copilot CLI,
Aider, Cline, Windsurf/Cascade, OpenAI Codex CLI, Google Gemini CLI, Amazon Q
Developer CLI. 상세 조사 근거는 GF-84 태스크 노트에 기록돼 있다. 요약:

| 도구 | 로컬 세션 로그 | 서브프로세스에 세션 상관용 env var 주입 | model 필드 출처 |
|---|---|---|---|
| Cursor | `~/.cursor/.../agent-transcripts/*.jsonl` + `store.db` | 없음(`CURSOR_AGENT=1` 불리언뿐, 세션ID 노출은 미해결 기능요청) | 로컬 "model hint"(설정값) |
| GitHub Copilot CLI | `~/.copilot/session-state/<id>/events.jsonl` | 문서화된 세션ID env var 없음 | `COPILOT_MODEL`은 사용자가 직접 설정하는 입력값 |
| Aider | `.aider.chat.history.md`(마크다운) | 없음 | `AIDER_MODEL` env var/설정 — 사용자가 직접 지정 |
| Cline | `globalStorage/tasks/<id>/api_conversation_history.json`(API 요청/응답 원문) | 없음(`CLINE_ACTIVE=true`는 아직 오픈 기능제안, 미배포) | 원문 API 응답이라 성격은 가장 유사하나 상관관계 채널 부재 |
| Windsurf/Cascade | 대화 자체를 영속 저장하지 않음(단기 Memories만) | 해당 없음 | 해당 없음 |
| OpenAI Codex CLI | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`(`session_meta`/`turn_context.model`) | **있음** — `CODEX_THREAD_ID`가 셸 툴 실행 시 서브프로세스에 노출됨(openai/codex#19937) | `turn_context.model`은 `timestamp`/`cwd`/`cli_version`과 함께 턴 시작 시점에 기록되는 로컬 설정값으로 보이며, API 응답이 사후에 확정한 모델을 되돌려 쓰는 필드라는 근거를 찾지 못함 |
| Google Gemini CLI | 세션 트랜스크립트 존재 | 없음(`GEMINI_CLI=1` 불리언뿐) | 확인 불가 |
| Amazon Q Developer CLI | `~/.aws/amazonq/history/chat-history-[id].json` | 문서화된 세션ID env var 없음 | 모델이 AWS 백엔드가 관리하는 값이라 "자가신고" 개념 자체가 약함 |

## Decision

**비-Claude-Code AI 도구에 대한 트랜스크립트 기반 `AI-Model` 검증을 구현하지
않는다.** decision-5가 정한 "그 외 도구는 `gitformat.aiModel` 존재/화이트리스트
검증까지만 강제하고 진실성은 검증하지 않는다"는 정책을 그대로 유지한다 —
decision-5의 표를 대체하지 않고, "왜 그 외 도구까지 확대하지 않았는지"를
보완 설명하는 문서로 decision-5 옆에 남긴다.

판단 근거:

- 조사한 8개 도구 중 어느 것도 Claude Code와 동시에 두 조건(① 훅이 커밋
  시점에 정확한 세션 파일을 찾을 수 있는, 애플리케이션이 직접 주입하는 세션
  상관관계 채널, ② 그 파일 안에서 API 응답이 사후 확정한 model 값)을
  만족하지 않는다.
- 가장 근접한 후보인 **OpenAI Codex CLI**는 `CODEX_THREAD_ID`로 조건 ①은
  만족하지만, 세션 로그의 `model` 필드가 로컬 CLI 설정(요청 전에 이미 정해진
  값)을 그대로 옮겨 적은 것으로 보여 조건 ②를 만족하지 못한다 — 이 필드를
  파싱해도 지금의 `gitformat.aiModel` 자가신고보다 신뢰 수준이 높아지지
  않는다. 오히려 Codex CLI가 언제든 바꿀 수 있는 비공개/버전별 내부 JSONL
  스키마에 의존하게 돼, "신뢰 수준은 그대로인데 유지보수 비용과 깨질 위험만
  늘어나는" 교환이 된다.
- **Cline**의 `api_conversation_history.json`은 원문 API 응답을 담고 있어
  성격상 Claude Code의 `message.model`에 가장 가깝지만, 훅이 커밋 시점에
  "어느 task 폴더가 지금 이 커밋을 만들었는지" 특정할 상관관계 채널(세션ID
  env var)이 아직 없다 — 채널이 없으면 어떤 파일을 읽어야 할지 알 수 없으므로
  구현 불가능하다.
- 이 프로젝트는 외부 서비스/새 런타임 의존을 늘리지 않는 방향(decision-11,
  decision-14)을 반복 확인해왔다. 신뢰 수준을 실질적으로 높이지 못하는
  파싱 로직을 굳이 추가하는 것은 이 미니멀리즘과도 어긋난다.

## Consequences

- README "한계 및 향후 검토 과제"의 "비-Claude-Code AI 도구의 `AI-Model` 값은
  자가신고 수준입니다" 문구는 그대로 유지하되, 이 decision을 근거로 링크해
  "조사했지만 검증 가능한 채널을 찾지 못했다"는 사실을 명시한다(GF-84).
- 이후 이 도구들(특히 Codex CLI, Cline)이 세션 ID를 서브프로세스에 공식
  노출하거나 API 응답 기반 model 필드를 문서화하면, 이 decision을 재검토해야
  한다 — 지금의 "불가능" 판단은 2026-09 시점 조사 결과에 근거한 것이지
  영구적인 결론이 아니다.
- `hooks/post-commit`/`hooks/commit-msg`의 로직 변경은 없다 — `trailer_ai_model()`,
  `enforce_ai_model_gate()`는 이번 태스크로 수정되지 않는다.

