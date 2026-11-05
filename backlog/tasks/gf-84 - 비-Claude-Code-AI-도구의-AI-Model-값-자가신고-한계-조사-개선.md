---
id: GF-84
title: 비-Claude-Code AI 도구의 AI-Model 값 자가신고 한계 조사/개선
status: Done
assignee: []
created_date: '2026-09-03 01:26'
updated_date: '2026-09-03 22:30'
labels: []
dependencies: []
references:
  - backlog/decisions/decision-5 - AI-귀속-footer-정책-트랜스크립트-기반-AI-Model-포함.md
  - decision-15
documentation:
  - hooks/commit-msg
  - hooks/post-commit
  - hooks/gitformat.conf
ordinal: 82000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
decision-5에 따라 Claude Code는 세션 트랜스크립트(message.model)로 AI-Model을 검증하지만, 그 외 AI 도구는 사용자가 gitformat.aiModel에 설정한 값을 존재/화이트리스트 여부만 확인하고 그대로 신뢰한다(자가신고 수준). README '한계 및 향후 검토 과제'에 명시된 항목. 다른 주요 AI 코딩 도구들이 로컬에 검증 가능한 세션 로그/트랜스크립트를 남기는지 조사하고, 가능하면 Claude Code와 유사한 방식으로 검증을 강화하거나, 불가능하면 그 근거를 decision-5를 갱신하는 새 decision으로 명시적으로 남긴다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 비-Claude-Code AI 도구(예: 주요 AI 코딩 CLI/에이전트) 중 로컬에서 검증 가능한 세션 로그/트랜스크립트를 남기는 도구가 있는지 조사 결과가 태스크 노트에 기록된다
- [ ] #2 검증 가능한 도구가 있으면 해당 도구에 대해 트랜스크립트 기반 AI-Model 검증이 구현되고 테스트로 커버된다
- [x] #3 검증이 불가능하다는 결론이면 그 근거가 decision-5를 대체하거나 보완하는 새 decision으로 기록된다(decision-5 파일 자체는 직접 수정하지 않는다)
- [x] #4 README '한계 및 향후 검토 과제' 문구가 조사/구현 결과에 맞게 갱신된다
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. 주요 비-Claude-Code AI 코딩 도구(Cursor, GitHub Copilot CLI, Aider, Cline, Windsurf/Cascade, OpenAI Codex CLI, Google Gemini CLI, Amazon Q Developer CLI) 리서치: 로컬 세션 로그 존재 여부, 세션 상관관계용 서브프로세스 env var 존재 여부, model 필드가 API 응답 기반인지 로컬 설정 기반인지 조사\n2. 결론에 따라 decision-5를 보완하는 새 decision 생성 (검증 불가 판단 시) 또는 훅 구현 (검증 가능한 도구 발견 시)\n3. README.md/README.en.md 한계 섹션 갱신\n4. shellcheck/bats 통과 확인 후 커밋, task-finalization
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
리서치 결과(AC #1): 8개 비-Claude-Code AI 코딩 도구 조사. 판단 기준 2가지 — (a) 훅이 커밋 시점에 올바른 세션 파일을 찾아낼 수 있도록 도구가 서브프로세스에 세션 식별자 env var를 주입하는가(Claude Code의 AI_AGENT/CLAUDE_CODE_SESSION_ID처럼 앱이 직접 주입, LLM 자가 export 아님), (b) 그 세션 파일의 model 필드가 실제 API 응답값을 그대로 기록한 것인가(로컬 설정/CLI 인자를 그대로 되돌려쓴 것이 아님, decision-5가 Claude Code에서 확인한 message.model과 동일 성격).

- Cursor: ~/.cursor/projects/.../agent-transcripts/<id>/<id>.jsonl + store.db에 세션 기록. 단 model은 'model hint'(로컬 선택값) 성격. 서브프로세스에 세션ID env var 없음(CURSOR_AGENT=1 플래그뿐, 세션ID 노출은 미해결 기능요청 상태, 2026-09 기준).
- GitHub Copilot CLI: ~/.copilot/session-state/<id>/events.jsonl에 model 변경 이벤트 기록. 그러나 COPILOT_MODEL은 사용자가 직접 지정하는 입력값(env var)이고, 서브프로세스에 세션ID를 노출하는 env var는 문서화돼 있지 않음(copilot help environment 기준).
- Aider: .aider.chat.history.md(마크다운)에 대화 기록. 모델은 AIDER_MODEL env var/설정 파일로 사용자가 직접 지정 — 자가신고와 동일한 성격. 세션 상관관계용 env var 없음.
- Cline(VS Code 확장): globalStorage/tasks/<id>/api_conversation_history.json에 실제 API 요청/응답 원문을 저장 — 8개 중 Claude Code의 message.model과 가장 유사한 후보. 그러나 서브프로세스(터미널)에 세션 식별 env var를 주입하는 기능은 아직 오픈 기능제안(CLINE_ACTIVE=true) 단계이고 실제 배포되지 않음 — 훅이 커밋과 세션을 상관시킬 방법이 없음.
- Windsurf/Cascade: 대화 내용 자체를 디스크에 영속 저장하지 않음(단기 'Memories' 요약만 저장) — 애초에 조회할 트랜스크립트가 없음.
- OpenAI Codex CLI: 8개 중 가장 유력한 후보. CODEX_THREAD_ID가 셸 툴 실행 시 서브프로세스에 실제로 노출됨(openai/codex#19937에서 'Codex CLI 0.125.0 exposes CODEX_THREAD_ID in shell tool executions' 확인). 세션 로그는 ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl(session_meta/turn_context에 model 필드 포함). 그러나 이 model 필드는 턴 시작 시점에 로컬 CLI 설정(config.toml의 model 값)을 그대로 기록하는 것으로 보이며(reverse-engineering 자료 기준 session_meta/turn_context는 timestamp/cwd/cli_version과 같은 '로컬 컨텍스트' 필드들과 함께 기록됨), API 응답이 실제로 확정한 모델을 사후에 되돌려 쓰는 필드라는 근거를 찾지 못함 — 즉 gitformat.aiModel 자가신고와 신뢰 수준이 동일하고, 검증되지 않은 내부 포맷(버전업 시 깨지기 쉬움)을 파싱하는 비용만 추가됨.
- Google Gemini CLI: 세션 트랜스크립트는 있으나(~/.gemini 또는 Antigravity의 transcript.jsonl), 서브프로세스에 노출되는 건 GEMINI_CLI=1 불리언 플래그뿐 — 세션 상관관계 불가.
- Amazon Q Developer CLI: ~/.aws/amazonq/history/chat-history-[id].json 존재하나 서브프로세스 세션ID env var 문서 없음. Q의 모델은 AWS가 관리하는 백엔드 선택이라 사용자가 임의 모델명을 설정하는 개념 자체가 약함.

결론: 8개 도구 전부 Claude Code 수준(앱이 강제 주입하는 세션 식별자 + API 응답 그대로 기록된 model 필드)의 검증 채널을 제공하지 않는다. 가장 근접한 Codex CLI도 model 필드가 사실상 로컬 설정 재기록이라 자가신고와 신뢰 수준이 같다. → AC #3 경로(decision 기록, 미구현)로 진행.

검증(shellcheck/bats): 'shellcheck -s sh hooks/commit-msg hooks/pre-commit hooks/post-commit hooks/checks/*.sh install.sh' 통과(SHELLCHECK_OK). 'bats tests/' 87개 전체 ok(not ok 없음) — 이번 작업은 hooks/*.sh 로직을 건드리지 않았으므로(README/decision 문서만 변경) 기존 회귀 스위트가 그대로 통과함을 확인. AC #2는 조사 결과 검증 가능한 도구가 없어(결론 참고) 조건 불충족으로 체크하지 않음 — 해당 경로는 decision-15 생성(AC #3)으로 대체.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
8개 비-Claude-Code AI 코딩 도구(Cursor, GitHub Copilot CLI, Aider, Cline, Windsurf/Cascade, OpenAI Codex CLI, Google Gemini CLI, Amazon Q Developer CLI)를 조사한 결과, Claude Code 수준(앱이 직접 주입하는 세션 상관관계 채널 + API 응답이 확정한 model 값)을 동시에 만족하는 도구를 찾지 못했다. 가장 근접한 OpenAI Codex CLI(CODEX_THREAD_ID 서브프로세스 노출)도 세션 로그의 model 필드가 로컬 설정값 재기록으로 보여 자가신고와 신뢰 수준이 같았다. 조사 근거는 태스크 노트에 기록했고(AC #1), decision-15를 새로 만들어 decision-5를 보완하며 자가신고 방식을 유지하는 근거를 남겼다(AC #3, decision-5 파일은 직접 수정하지 않음). README.md/README.en.md의 '한계 및 향후 검토 과제' 문구를 조사 결과에 맞게 갱신했다(AC #4). AC #2는 검증 가능한 도구가 없어 조건 불충족으로 구현하지 않았다(의도적 미해당). shellcheck(hooks/*, install.sh) 통과, bats tests/ 87개 전체 통과로 회귀 없음을 확인했다.
<!-- SECTION:FINAL_SUMMARY:END -->
