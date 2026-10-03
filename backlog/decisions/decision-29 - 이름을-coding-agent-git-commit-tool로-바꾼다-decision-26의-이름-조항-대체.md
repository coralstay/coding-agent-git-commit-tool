---
id: decision-29
title: 이름을 coding-agent-git-commit-tool로 바꾼다 (decision-26의 이름 조항 대체)
date: '2026-10-03 13:11'
status: accepted
---
## Context

decision-26(2026-10-03)이 이름을 git-trail로 정했다. 같은 날 유저가 "와닿지 않는다"고 했고,
이름을 다시 고르기 전에 이 프로젝트가 무엇을 하는지부터 다시 정리했다. 실제로 쓰면서
체감하는 일은 두 가지다.

- 커밋 메시지 규칙을 검사해 어기면 커밋을 거부한다(`prepare-commit-msg`, `commit-msg`).
- 커밋마다 작성자·AI 도구·모델·태스크·토큰을 트레일러로 자동 기록한다(`post-commit`).

trail·logbook·ledger·hallmark처럼 "지울 수 없는 기록"에 기댄 이름은, 이력 불변 기둥이 아직
코드로 구현되지 않은 상태(DRAFT-18·19)에서 이 두 가지를 떠올리게 하지 못했다.

후보로 git-claude도 나왔지만, 유저는 범위를 Claude 전용으로 좁히지 않고 여러 AI 도구를
계속 지원하기로 했다. 이어서 agent-commit을 검토했으나 "에이전트가 커밋을 대신 만들어
주는 도구"로 읽힐 수 있었다. 유저가 "헷갈리지 않게" 하는 일을 그대로 적은 이름을 골랐다.

## Decision

**이름을 coding-agent-git-commit-tool로 바꾼다.** 코딩 에이전트가 만드는 git 커밋을 다루는
도구라는 뜻이다. decision-26의 이름 조항만 대체하고, decision-25의 목적 세 기둥과 decision-26의
용어 설명(doc-21 개념 지도)은 그대로 유효하다.

**범위는 범용으로 유지한다.** Claude Code 이외의 AI 도구 지원(`gitformat.knownModel`의 다른
모델, `AI-Model` 게이트, decision-15·17)은 이름 때문에 버리지 않는다.

로컬 폴더, GitHub 저장소, 문서를 모두 새 이름으로 바꾼다(유저 지시). GitHub 저장소는
coralstay/git-trail → coralstay/coding-agent-git-commit-tool로 rename하고, 예전 이름 세 개는
GitHub이 리다이렉트한다.

## Consequences

- 표시 이름만 바뀐다. 설정 키·파일명(`gitformat.*`)은 GF-133, 태스크 접두어 GF와 지난 기록
  본문은 decision-25·26과 같은 이유로 그대로 둔다.
- 로컬 폴더가 옮겨지면 Claude Code의 프로젝트 경로가 바뀐다. 트랜스크립트와 메모리 위치가
  경로에서 파생되므로, 이동은 병합 뒤 마지막에 하고 메모리는 새 경로로 복사한다.
  `core.hooksPath`를 이 폴더로 둔 저장소(이 저장소, agent-orchestartor)는 다시 설치해야 한다.
- 이름이 길다. 명령 예시에서는 클론 위치를 짧게 잡아도 된다고 README에 안내한다.

