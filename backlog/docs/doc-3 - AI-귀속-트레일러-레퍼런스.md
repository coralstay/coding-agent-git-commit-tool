---
id: doc-3
title: AI 귀속 트레일러 레퍼런스
type: guide
created_date: '2026-09-19 05:27'
updated_date: '2026-10-12 10:00'
---
## 🤖 AI 귀속 footer

> decision-5 · decision-19 · decision-30 · decision-31

AI 코딩 에이전트가 커밋했다면 `prepare-commit-msg`가 커밋 객체를 만들기 전에 아래 트레일러를
메시지 파일에 붙입니다. 신뢰 수준이 트레일러마다 다르다는 걸 알아두는 게 중요합니다. 메시지에
같은 키의 줄이 이미 있으면(대소문자 무시) 그 키는 붙이지 않습니다(decision-19).

| 트레일러         | 값 출처                                                                                                                                                                                                                                                                                             | 신뢰 수준                                                                                     |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `AI-Agent`       | `<도구>/<버전> (<모델>)` 한 줄. 도구 · 버전은 `AI_AGENT` 환경변수(Claude Code 프로세스가 하위 프로세스에 주입). 모델은 **Claude Code**면 세션 트랜스크립트(`~/.claude/projects/<slug>/<session>.jsonl`)의 마지막 assistant `message.model`, **그 외 도구**면 `git config gitformat.aiModel`(훅이 존재 · 화이트리스트를 강제) | 도구 · 버전은 프로세스 주입값 / 모델은 Claude Code면 서버 발급 사실, 그 외는 존재+형식만 강제 |
| `Co-Authored-By` | 도구가 `claude-code`일 때만 `Claude <noreply@anthropic.com>`                                                                                                                                                                                                                                       | 자동                                                                                          |
| `Hooks-Commit`   | 이 coding-agent-git-commit-tool 클론 자체의 `git rev-parse --short HEAD`                                                                                                                                                                                                                            | 완전 자동, 모든 커밋(AI 여부 무관)                                                            |
| `Signed-off-by`  | 커미터 ident(`git var GIT_COMMITTER_IDENT`). **AI 도구가 감지되지 않은 커밋에만** 붙습니다(decision-30)                                                                                                                                                                                             | 자동. 사람의 DCO 인증이라 에이전트 커밋에는 붙이지 않습니다                                   |

버전이나 모델을 못 구하면 줄을 생략하지 않고 `version-unavailable`/`model-unavailable`로
남깁니다 — 조용한 생략은 "AI가 관여하지 않았다"로 읽혀 잘못된 귀속이 됩니다. 트랜스크립트
조회는 어떤 이유로 실패해도 커밋을 막지 않습니다.

`CLAUDE_CODE_SESSION_ID`는 `AI-Agent`의 모델을 찾으려고 트랜스크립트 파일 경로를 계산하는 데만
내부적으로 쓰이고, 값 자체가 커밋 footer에 남지는 않습니다 — 세션 식별자를 공개 저장소
히스토리에 영구히 남기지 않기 위함입니다. 트랜스크립트에서는 `message.model`만 읽습니다.

## 측정 트레일러는 범위 밖입니다

`Tokens-Used`/`Tool-Calls`는 더 붙지 않습니다(decision-31, GF-146). 토큰 · 툴콜 측정을 커밋 훅에
두면 깃과 측정이 강결합되므로 별도 컴포넌트(이름 미정)로 옮겼습니다. 훅은
`.git/.gitformat-token-attributed`/`.gitformat-token-cursor`를 만들거나 읽지 않습니다.

- 메시지에 직접 쓴 `Tokens-Used`/`Tool-Calls` 줄은 지우거나 값을 검증하지 않습니다. 등록 트레일러가
  아니므로 평범한 본문 줄이고, 본문 72자 제한을 받습니다.
- GF-146 이전 커밋의 두 트레일러는 고치지 않습니다. 형식과 의미의 변천(델타 → 커밋당 귀속)은
  doc-16에 남아 있습니다.

## 예전 트레일러

- `AI-Tool`/`AI-Tool-Version`/`AI-Model`은 `AI-Agent` 한 줄로 합쳤습니다(decision-19, GF-128).
- `Verify-Bypassed`는 없앴습니다 — 검증하는 훅을 `--no-verify`로 건너뛸 수 없어 기록할 우회가
  없습니다(decision-18).
