---
id: doc-3
title: AI 귀속 트레일러 레퍼런스
type: guide
created_date: '2026-09-19 05:27'
updated_date: '2026-10-03 07:30'
---
## 🤖 AI 귀속 footer

> decision-5

AI 코딩 에이전트가 커밋했다면 아래 트레일러가 자동으로 붙습니다. 신뢰 수준이 트레일러마다
다르다는 걸 알아두는 게 중요합니다.

| 트레일러                     | 값 출처                                                                                                                                                                                                                          | 신뢰 수준                                                                           |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `AI-Tool`, `AI-Tool-Version` | `AI_AGENT` 환경변수(Claude Code 프로세스가 하위 프로세스에 주입)                                                                                                                                                                 | 강제 — LLM이 스스로 만든 값이 아님                                                  |
| `AI-Model`                   | **Claude Code**: 세션 트랜스크립트(`~/.claude/projects/<slug>/<session>.jsonl`)의 `message.model` — Anthropic API 응답을 그대로 기록한 값. **그 외 도구**: `git config gitformat.aiModel`(commit-msg가 존재/화이트리스트를 강제) | Claude Code는 서버 발급 사실 / 그 외는 존재+형식만 강제, 진실성은 검증 불가         |
| `Tokens-Used`                | AI-Tool이 감지된 모든 커밋에 붙습니다. **Claude Code**: `in=<입력> out=<출력>` — 세션·서브에이전트 트랜스크립트에서 **이 커밋이 바꾼 파일을 건드린 응답**의 `message.usage` 합(커밋당 귀속, 델타 아님, decision-27). `in`은 input+cache_creation+cache_read, `out`은 output. 귀속된 응답이 없으면 `in=0 out=0 (no-attributed-turn)`. **그 외 도구/실패 시**: `unavailable (사유)` (아래 참고) | 서버 발급 사실(자가신고 아님, Claude Code 한정) / 귀속 판정은 경로 문자열 대조라 근사 / 그 외는 실측 채널 없음 |
| `Tool-Calls`                 | 귀속된 응답의 `tool_use` 블록 중 이 커밋이 바꾼 파일을 실제로 건드린 것의 개수. 귀속된 응답이 없으면 `0 (no-attributed-turn)` — 출처/한계는 `Tokens-Used`와 동일 | 서버 발급 사실(자가신고 아님, Claude Code 한정) / 그 외는 실측 채널 없음            |
| `Co-Authored-By`             | `AI-Tool`이 `claude-code`일 때만 자동 삽입                                                                                                                                                                                       | 자동                                                                                |
| `Hooks-Commit`               | 이 git-format 클론 자체의 `git rev-parse --short HEAD`                                                                                                                                                                           | 완전 자동, 모든 커밋에 적용(AI 여부 무관)                                           |
| `Signed-off-by`              | 커미터 정보(`git log -1 --format='%cn <%ce>'`)                                                                                                                                                                                   | 완전 자동, 모든 커밋에 적용(AI 여부 무관, `git commit -s`와 동일 방식, decision-10) |

`CLAUDE_CODE_SESSION_ID`는 `AI-Model`/`Tokens-Used`/`Tool-Calls` 조회를 위해 트랜스크립트
파일 경로를 찾는 데만 내부적으로 쓰이고, 값 자체가 커밋 footer에 남지는 않습니다 — 세션
식별자를 공개 저장소 히스토리에 영구히 남기지 않기 위함입니다.

`Tokens-Used`/`Tool-Calls`는 **이 커밋에 든 양**입니다(decision-27). 세션 트랜스크립트와
서브에이전트 트랜스크립트(`<세션 ID>/subagents/*.jsonl`) 전체에서, 도구 호출이 이 커밋이 바꾼
파일(`git diff-tree … HEAD`)을 건드린 응답만 골라 더합니다. `file_path`/`notebook_path`는
저장소 상대경로로 정규화해 완전 일치, Bash는 명령에 저장소 상대경로가 들어 있는지로
판정합니다(파일명만으로는 매칭하지 않음). 응답 하나는 한 커밋에만 들어가도록, 귀속한 응답
키를 `<대상 저장소>/.git/.gitformat-token-attributed`에 기억합니다(세션이 바뀌면 새로 시작).
어느 커밋 파일도 건드리지 않은 응답(탐색·대화)은 어디에도 들어가지 않습니다. 상세는 doc-16.

측정에 실패하면 `unavailable (사유 슬러그)`로 명시 기록합니다(사유:
`no-session-id`/`transcript-not-found`/`transcript-unreadable`/
`transcript-parse-failed`/`no-usage-channel`). 기록 파일은 실측 성공 시에만 갱신합니다.
귀속된 응답의 usage가 정말 0이면 `in=0 out=0`으로, 귀속된 응답이 아예 없으면
`in=0 out=0 (no-attributed-turn)`으로 구별해 남깁니다(생략하지 않음).

GF-129 이전 커밋의 `Tokens-Used`는 단일 숫자로, "직전 커밋 이후 세션에서 소비된 토큰"(델타,
`.gitformat-token-cursor`)이었습니다. 형식이 달라 구별되며 고치지 않습니다.
