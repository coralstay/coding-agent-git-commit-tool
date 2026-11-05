---
id: decision-31
title: 커밋 포맷 전용 — 토큰 측정은 별도 컴포넌트로 분리 (decision-5·19·27의 측정 조항 대체)
date: '2026-10-12 09:54'
status: accepted
---
## Context

coding-agent-git-commit-tool은 커밋 메시지 형식 강제와 함께, AI 도구가 감지된 커밋에
`Tokens-Used`/`Tool-Calls` 트레일러를 붙여 왔다(decision-5 GF-97 amendment, decision-19,
decision-27). 값을 구하려고 `prepare-commit-msg`가 Claude Code 세션 트랜스크립트 전체와
서브에이전트 트랜스크립트를 읽어 응답을 커밋에 귀속하고, 그 귀속 기록을
`.git/.gitformat-token-attributed`에 커밋 사이 상태로 남겼다(GF-129, doc-16).

2026-10-12 유저 결정: **이 도구는 깃 커밋 포맷만 맞춘다.** 토큰 측정을 커밋 훅에 두면
깃과 측정이 강결합된다.

- 측정의 단위와 시점이 커밋에 묶인다. 커밋을 만들지 않은 작업, 커밋 뒤에 git이 커밋을
  포기한 경우(서명 실패 등), `--amend`의 경계 같은 깃 쪽 사정이 측정값을 흔든다.
- 측정 로직(귀속 판정, 서브에이전트, 세션 상태 파일)이 포맷 훅의 크기를 대부분 차지해
  감사 가능성(decision-16)을 떨어뜨린다.
- 측정 방식이 바뀔 때마다 커밋 이력의 트레일러 의미가 바뀐다(decision-19 → decision-27).

## Decision

**커밋 훅은 토큰·툴콜을 측정하지 않는다. 측정은 별도 컴포넌트(이름 미정)로 옮긴다.**

- `Tokens-Used`/`Tool-Calls` 트레일러를 붙이지 않고, 귀속 기록 파일
  (`.gitformat-token-attributed`, `.gitformat-token-cursor`)을 만들거나 읽지 않는다.
  `gitformat.conf`의 `trailer.tokensUsed`/`trailer.toolCalls` 키도 지운다(GF-146).
- 사람이나 에이전트가 메시지에 직접 쓴 `Tokens-Used`/`Tool-Calls` 줄은 지우지도 값을
  검증하지도 않는다. 등록 트레일러가 아니므로 평범한 본문 줄이고, 본문 72자 제한을
  받는다 — 측정 줄만을 위한 예외를 남기면 그 자체가 측정과의 결합이다.
- **남기는 것**: `AI-Agent`의 모델 판정(트랜스크립트의 `message.model` 읽기)은 측정이
  아니라 출처 기록이라 그대로다. `Task-Id`, `Co-Authored-By`, `Hooks-Commit`,
  `Signed-off-by`(decision-30)도 바뀌지 않는다.

이 decision이 대체하는 조항:

- decision-5의 Amendment(2026-09-19, GF-97) 전체 — `Tokens-Used`/`Tool-Calls`의 사유 명시,
  범위, 0과 unavailable 구분
- decision-19 표의 `Tokens-Used`/`Tool-Calls` 두 행
- decision-27 전체 — 커밋당 토큰량과 귀속 규칙

과거 decision 파일은 이력이므로 고치지 않는다.

## Consequences

- 커밋 footer가 에이전트 커밋 기준 4줄(`Task-Id`, `AI-Agent`, `Co-Authored-By`,
  `Hooks-Commit`)로 줄어든다.
- GF-146 이전 커밋의 `Tokens-Used`/`Tool-Calls`는 고치지 않는다. 재생 커밋(cherry-pick ·
  rebase)은 면제라 그 줄을 그대로 옮기고, `--amend --no-edit`으로 들고 온 줄도 남는다.
- 측정 컴포넌트는 깃 훅에 기대지 않는 쪽으로 따로 설계한다. 그 컴포넌트가 커밋 메시지에
  측정값을 남기기로 한다면, 이 도구에 키를 다시 등록하는 대신 72자 안에 들어가는 형식을
  쓰는 게 결합을 만들지 않는다.
- 마일스톤 m-2(AI 커밋 토큰 측정), DRAFT-23, GF-114는 새 컴포넌트로 옮긴다는 사유로
  보관한다. doc-16(측정 방법과 한계)은 폐기 표시를 하고 지우지 않는다.
