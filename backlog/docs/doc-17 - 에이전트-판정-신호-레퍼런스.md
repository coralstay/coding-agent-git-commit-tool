---
id: doc-17
title: 에이전트 판정 신호 레퍼런스
type: specification
created_date: '2026-09-25 19:34'
updated_date: '2026-09-25 19:46'
---
# 에이전트 판정 신호 레퍼런스

커밋을 만든 주체가 AI 에이전트인지 판정할 때 쓰는 환경변수와, 각각을 **검증할 수 있는지**.
결정 근거는 decision-20.

## 실측한 신호 (Claude Code가 하위 프로세스에 주입)

| 환경변수 | 예시 값 | 역할 | 판정에 쓰나 |
| --- | --- | --- | --- |
| `CLAUDE_CODE_SESSION_ID` | UUID | 트랜스크립트 경로 `~/.claude/projects/<슬러그>/<UUID>.jsonl`를 만든다 → 모델·토큰 값의 출처 | **예 — 파일 실재로 확인** |
| `CLAUDE_PID` | `57115` | Claude Code 프로세스 PID | **예 — `ps -p <pid> -o comm=`이 `claude`인지 확인** |
| `AI_AGENT` | `claude-code_2-1-267_agent` | `도구_버전_역할`. `AI-Agent` 트레일러의 도구·버전 **값 출처**. 주입값이라 LLM 자가신고가 아니다 | 값으로만 — 존재 여부는 검증 불가 |
| `CLAUDE_CODE_EXECPATH` | `/opt/homebrew/Caskroom/claude-code/2.1.267/claude` | 실행 파일 경로. **경로에 버전이 들어 있다** | 보조 — `AI_AGENT`가 없을 때 버전 보강 |
| `CLAUDE_CODE_CHILD_SESSION` | `1` | 하위 세션(서브에이전트 등) 표시 | 보조 |
| `CLAUDECODE` | `1` | "Claude Code 안에서 실행 중"이라는 단순 플래그 | 아니오 — 위조·누락이 쉽고 검증 불가 |
| `CLAUDE_CODE_ENTRYPOINT` | `cli` | 실행 경로(cli/vscode 등) | 아니오 — 진단용 |
| `CLAUDE_EFFORT` | `high` | 추론 강도 설정 | 아니오 — 귀속과 무관 |
| `CLAUDE_CODE_MESSAGING_SOCKET` | (경로) | IPC 소켓 | 아니오 |
| `CLAUDE_CODE_MESSAGING_TOKEN` | (토큰) | 그 채널의 **인증 토큰** | 아니오 — **비밀값** |

## 판정 규칙

`CLAUDE_CODE_SESSION_ID`가 **실재하는 트랜스크립트 파일**을 가리키거나, `CLAUDE_PID`가
**살아 있는 `claude` 프로세스**를 가리키면 에이전트 커밋이다.

이 둘만이 파일시스템·프로세스 테이블과 **대조해 확인**되는 신호다. 나머지는 "있다/없다"뿐이라
판정 근거로 쓰지 않는다 — `CLAUDECODE=1` 하나로 판정하면 위조와 누락에 모두 취약하다.

## 값 조립

`AI-Agent: <도구>/<버전> (<모델>)`

- 도구·버전: `AI_AGENT`를 `_`로 분리(`claude-code_2-1-267_agent` → 도구 `claude-code`,
  버전 `2.1.267`). 없으면 `CLAUDE_CODE_EXECPATH` 경로에서 버전을 보강한다.
- 모델: 세션 트랜스크립트의 `message.model`. Anthropic API 응답을 애플리케이션이 그대로
  기록한 값이라 자가신고가 아니다.
- **구성요소를 못 구해도 줄은 반드시 남긴다**: `version-unavailable`, `model-unavailable`.
  조용한 생략이 곧 잘못된 귀속이다.

## 비밀값 취급

`CLAUDE_CODE_MESSAGING_TOKEN`과 `CLAUDE_CODE_MESSAGING_SOCKET`은 IPC 채널의 인증 정보다.
**커밋 메시지·로그·에러 출력에 절대 남기지 않는다.** 환경변수를 일괄 덤프하는 디버그 코드를
훅에 넣지 말 것.

`CLAUDE_CODE_SESSION_ID`는 비밀값은 아니지만 커밋 이력에 영구히 남길 이유가 없어
트레일러로 쓰지 않는다 — 트랜스크립트를 찾는 데만 쓴다.

## 다른 AI 도구

동등한 검증 채널(주입된 세션 상관자 + 서버가 확인한 모델 값)을 가진 도구가 없어
`AI-Agent`가 붙지 않는다. 기존 조사 결론(decision-15, decision-17)을 유지한다.
