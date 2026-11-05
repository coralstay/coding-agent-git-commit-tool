---
id: DRAFT-22
title: 'pre-push 플러그인: 서명 없는 커밋과 수동 검증 게이트를 통과하지 못한 Done 카드의 push를 git 단계에서 거부'
status: Draft
assignee: []
created_date: '2026-11-05T18:56:00Z'
labels:
  - security
dependencies: []
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## 배경
유저 결정(2026-11-06, 계획 ~/.claude/plans/giggly-kindling-snowglobe.md 3절). Claude 훅은 Claude Code 안에서만 걸린다. Antigravity는 commit.gpgsign을 우회해 서명 없는 커밋을 만들었고(ebpf 5b1f0fc · 7acc271, handcrafted-python), bash -c · 스크립트 · 카드 파일 직접 수정으로 -s Done을 하면 훅이 보지 못한다. git 단계(.githooks)에서 한 번 더 막는다. --no-verify는 막을 수 없어 upkeep CI가 최종 방어선이다.
선행: agile-hooks DRAFT-10(사람 서명 지문 고정) · DRAFT-11(수동 검증 Done 게이트, scripts/card_gate.py).

## 제안
- githooks/pre-push.d/ 디스패처(pre-commit.d와 같은 방식)와 card-gates 플러그인
- push되는 ref 범위의 커밋 중 서명 없음(%G? = N)이 있으면 거부(GF-130과 연결)
- 그 범위에서 status가 Done으로 바뀐 backlog 카드마다 설치된 card_gate.py를 실행해 실패하면 거부
- card_gate.py가 없으면 경고만(backlog 프로젝트가 아닌 저장소 영향 없음)

## AC 후보
1. 서명 없는 커밋이 든 push를 거부하고 해당 커밋을 나열한다
2. Done으로 바뀐 카드가 card_gate.py를 통과하지 못하면 거부한다
3. Claude 밖 터미널(Antigravity · 직접 실행)에서도 걸린다
4. 설치 옵션(--plugins)으로 고를 수 있고 README에 반영한다
<!-- SECTION:DESCRIPTION:END -->
