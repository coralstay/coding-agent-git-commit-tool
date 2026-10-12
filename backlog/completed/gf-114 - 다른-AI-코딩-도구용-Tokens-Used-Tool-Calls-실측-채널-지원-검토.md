---
id: GF-114
title: 다른 AI 코딩 도구용 Tokens-Used/Tool-Calls 실측 채널 지원 검토
status: Done
assignee: []
created_date: '2026-09-19 01:21'
updated_date: '2026-10-12 10:02'
labels: []
dependencies: []
references:
  - decision-15
  - decision-17
documentation:
  - backlog/docs/doc-8 - decision-이력-지도.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GF-97에서 trailer_tokens_used()를 AI_TOOL_ID 케이스 분기 디스패처로 만들면서, claude-code가 아닌 감지된 AI 도구는 전부 "unavailable (no-usage-channel)"로 처리하도록 했다. decision-15(2026-09)는 당시 조사한 8개 도구(Cursor/Copilot CLI/Aider/Cline/Windsurf/Codex CLI/Gemini CLI/Amazon Q) 중 어느 것도 (1) 하위 프로세스에 주입되는 세션 상관관계 채널과 (2) 그 세션 안에서 서버가 확정한 usage 값을 동시에 제공하지 않는다고 결론지었다.

이후 어떤 도구가 이 두 조건을 만족하는 로컬 채널을 새로 노출하면, trailer_tokens_used()의 case 분기에 그 도구용 실측 함수(measure_claude_code_token_usage()와 같은 패턴)를 하나 추가하는 정도의 작업이 될 것으로 예상된다.

지금은 코드에 스텁이나 미리 준비된 함수를 두지 않는다 - 실제로 그런 도구가 나타나기 전까지는 이 draft로만 아이디어를 남겨둔다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 decision-15 조사 대상 8개 도구에 대해 2026-09-25 시점 재조사가 이뤄지고, GF-114가 요구하는 두 조건(하위 프로세스에 주입되는 세션 상관관계 채널 + 그 세션 안에서 서버가 확정한 usage 값) 각각의 충족 여부가 1차 출처와 함께 기록된다
- [x] #2 조건 충족 여부가 decision-15 시점과 달라진 도구가 있으면 무엇이 어떻게 달라졌는지, 그럼에도 지금 구현하지 않는(또는 하는) 이유가 명시된다
- [x] #3 다시 검토해야 할 시점을 판단할 수 있는 구체적 트리거가 남는다
- [x] #4 GF-114의 방침대로 hooks/*에 스텁이나 미리 준비된 함수를 추가하지 않는다
- [x] #5 doc-8(decision 이력 지도)에 decision-16과 decision-17이 등록되고 마지막 집계 목록의 개수가 실제 decision 수와 일치한다
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. decision-15의 8개 도구 목록과 두 조건 정의를 다시 읽고, 가장 근접했던 OpenAI Codex CLI부터 재조사한다
2. 조건 (1) 세션 상관관계 채널: CODEX_THREAD_ID가 실제로 하위 프로세스에 주입되는지 1차 출처로 확인한다
3. 조건 (2) 서버 확정 usage: rollout jsonl의 token_count/total_token_usage가 서버 발급 값인지, 신뢰할 만한 완전성을 갖는지 확인한다
4. 나머지 도구에 변화가 있는지 확인한다(특히 GitHub Copilot CLI)
5. 결과를 decision으로 남기고 doc-6/doc-3 서술을 필요한 만큼만 갱신한다 — hooks/*에는 아무 코드도 추가하지 않는다
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
재조사 결론: decision-15 시점과 달라진 도구가 하나 있다 — OpenAI Codex CLI가 조건 1(하위 프로세스에 주입되는 세션 상관관계 채널)을 이제 충족한다. 그러나 조건 2(서버가 확정한 usage 값)가 성립하지 않아 구현은 보류했다. 상세는 decision-17.

핵심 근거(1차 출처):
- openai/codex#19937 (closed as not planned, 2026-04-28) — 'Codex CLI 0.125.0 exposes CODEX_THREAD_ID in shell tool executions'를 재현 예시와 함께 확인. 이슈가 닫힌 이유는 stdio MCP 서버에도 같은 값을 넘겨달라는 별개 요청이 거절된 것이고, 셸 툴 노출 자체는 동작하는 전제다. rollout 경로가 ~/.codex/sessions/YYYY/MM/DD/rollout-*-<thread-id>.jsonl이라 이 값만 있으면 경로 특정이 된다.
- openai/codex#47003 (open, 2026-09-21) — auto-compaction 요청 usage가 rollout 집계에 반영되지 않는다. 0.154/0.155는 token_usage_record는 쓰지만 다음 token_count의 total_token_usage가 변하지 않고, 0.147은 레코드 자체를 안 쓴다. 감사 대상 compaction 요청 68건 중 68건이 누적치에 0 기여. → 이 수치로 Tokens-Used를 채우면 실측이라 표시한 값이 실제보다 작아진다.
- openai/codex#42025 — token_count 레코드 이후 로컬 히스토리 프로젝션이 멈추는 별개 버그(스키마 불안정성 근거).
- openai/codex#47779 (open, 2026-09-24) — rollout의 model 필드가 서버가 서비스한 모델이 아니라 요청값의 메아리임을 확인('every model-bearing field echoes the request', 존재하지 않는 gpt-9.9-does-not-exist도 그대로 되돌아옴). → decision-15의 AI-Model 결론은 오히려 재확인됐다.
- Google Gemini CLI — 셸 서브프로세스에는 GEMINI_CLI=1 불리언만 주입된다(session_id는 Gemini CLI 자체 hook 컨텍스트 전용이고 git 훅은 그 페이로드를 못 받는다). 토큰 통계는 ~/.gemini/tmp/<project_hash>/chats/에 저장되지만 경로가 프로젝트 단위라 세션 특정 불가. 조건 2만 진전.
- Cursor — 세션/대화 ID env var 여전히 없음(공개 기능요청 상태), CURSOR_INVOKED_AS는 호출 방식 표시 문자열.
- GitHub Copilot CLI — 문서화된 세션 ID env var 없음. 세션은 ~/.copilot/session-state/에 저장되고 COPILOT_MODEL은 사용자 입력값.
- Aider / Cline / Windsurf / Amazon Q Developer CLI — 변화 근거를 찾지 못했다(decision-15 시점 결론 유지). 이 4개는 Codex/Gemini/Cursor/Copilot만큼 깊이 파지 않았고 '변화 없음 확인'이 아니라 '변화 근거 미발견'이다.

조사 범위의 정직한 한계: 웹 검색 + GitHub 이슈 본문 확인까지만 했고, Codex CLI를 실제로 설치해 rollout 파일을 직접 만들어 보지는 않았다.

검증 증거: (AC1) decision-17 Context의 표에 8개 도구 각각의 조건 1/2 충족 여부와 decision-15 대비 변화를 기록했고, 근거 URL은 위 노트에 1차 출처(openai/codex#19937/#47003/#42025/#47779 및 각 도구 문서)로 남겼다. (AC2) Codex CLI의 변화(조건 1 충족)와 보류 이유(조건 2의 과소계상 + 스키마 불안정)를 decision-17 Decision 절에 명시했다. (AC3) decision-17 Consequences에 재검토 트리거 4개를 구체적으로 남겼다(#47003 수정 안정 릴리스 / rollout usage 스키마 문서화 / Gemini CLI의 셸 서브프로세스 세션 ID 주입 / 그 외 도구의 신규 채널). (AC4) git status로 이 브랜치의 변경이 backlog/ 3개 파일뿐이고 hooks/ 변경이 0건임을 확인했다. (AC5) ls로 실제 decision 파일이 17개임을 확인하고, doc-8의 '17개 decision 전부 계정' 목록에 decision-16·17이 포함되며 서론의 '17개 decision 중 7개 주제' 및 '대체 체인이 있는 7개 주제' 표제와 개수가 일치함을 grep으로 확인했다. ruff check . 통과.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
created: 2026-10-12 10:02
---
보관: 토큰 측정은 별도 컴포넌트로 이관(GF-146). coding-agent-git-commit-tool은 커밋 포맷만 맞춘다(decision-31).
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
decision-15의 8개 도구를 2026-09-25 시점으로 재조사해 decision-17로 기록했다. 결론이 하나 바뀌었다: OpenAI Codex CLI는 CODEX_THREAD_ID를 셸 툴 하위 프로세스에 노출하므로 조건 1(세션 상관관계 채널)을 이제 충족하고, rollout 경로도 thread ID로 특정 가능하다. 그러나 조건 2(서버 확정 usage)가 성립하지 않는다 — openai/codex#47003이 auto-compaction 요청 usage가 rollout 집계에 전혀 반영되지 않음을 기록하고(감사 68건 중 68건이 0 기여), 스키마도 버전마다 흔들린다. 과소계상된 수치로 Tokens-Used를 채우면 '실측'이라 표시한 값이 실제보다 작아지므로 구현을 보류하고, 재검토 트리거 4개를 남겼다. AI-Model 쪽은 openai/codex#47779(rollout의 model이 요청값의 메아리)로 decision-15 결론이 재확인됐다. 방침대로 hooks/*에는 스텁을 추가하지 않았다(git status로 확인). 사용자 승인을 받아 doc-8에 누락돼 있던 decision-16까지 함께 등록했다.
<!-- SECTION:FINAL_SUMMARY:END -->
