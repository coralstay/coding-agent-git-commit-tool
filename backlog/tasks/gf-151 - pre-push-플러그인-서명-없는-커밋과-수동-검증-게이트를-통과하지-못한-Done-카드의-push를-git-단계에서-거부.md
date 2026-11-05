---
id: GF-151
title: 'pre-push 플러그인: 서명 없는 커밋과 수동 검증 게이트를 통과하지 못한 Done 카드의 push를 git 단계에서 거부'
status: To Do
assignee: []
created_date: '2026-11-05T18:56:00Z'
updated_date: '2026-11-05T20:28:00Z'
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
## 비즈니스 규칙
- B1 (AC #1) pre-push 디스패처는 git이 준 stdin(ref 목록)을 한 번 읽어 두고 플러그인마다 같은 내용을 넘긴다
- B2 (AC #2) push되는 커밋(원격에 없는 범위) 중 서명 상태가 N인 커밋이 하나라도 있으면 거부하고 해시 · 제목을 나열한다
- B3 (AC #3) 그 범위에서 status가 Done으로 바뀐 backlog 카드마다 card_gate.py를 실행해, 하나라도 통과하지 못하면 거부한다
- B4 (AC #4) card_gate.py를 찾을 수 없으면 카드 검사는 경고만 하고 넘어간다(디스패처의 127 규칙과 같음). 서명 검사는 card_gate.py와 무관하게 언제나 한다
- B5 (AC #3) 삭제 push(로컬 sha가 0)는 검사하지 않는다
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 pre-push 디스패처가 stdin을 버퍼링해 플러그인마다 같은 ref 목록을 넘긴다(pre-commit · prepare-commit-msg 동작은 그대로)
- [ ] #2 card-gates 플러그인이 push 범위의 서명 없는(N) 커밋을 거부하고 나열한다
- [ ] #3 push 범위에서 Done으로 바뀐 카드가 card_gate.py를 통과하지 못하면 거부하고, 삭제 push는 검사하지 않는다
- [ ] #4 card_gate.py가 없으면 카드 검사만 경고 후 건너뛰고 서명 검사는 한다
- [ ] #5 install의 플러그인 선택(GF-149 --plugins)으로 card-gates를 고를 수 있다
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests/ 전체 통과(격리 저장소 isolated_repo.py 사용, 전역 서명 설정에 의존하지 않음)
- [ ] #2 [수동 검증] README · githooks 설명에 pre-push.d와 card-gates를 반영한다
- [ ] #3 [수동 검증] Claude 밖 터미널에서 서명 없는 커밋 push와 Manual-Verified 없는 Done 카드 push가 거부됨을 확인한다
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
### Subjective
유저가 2026-11-06 Claude 훅 밖의 우회(D1 간접 실행 · 카드 직접 수정, D2 Antigravity)를 git 단계에서 막기로 했다(계획 ~/.claude/plans/giggly-kindling-snowglobe.md 3절). Antigravity의 서명 없는 커밋(ebpf 5b1f0fc · 7acc271)이 계기다.

### Objective
- githooks/pre-commit · prepare-commit-msg는 같은 디스패처로, $0 이름의 .d/ 플러그인을 이름순으로 실행하고 127은 경고 후 계속한다. stdin은 나눠 주지 않는다고 적혀 있다(pre-push는 stdin으로 ref 목록을 받는다).
- 플러그인은 한 줄로 PATH의 명령을 exec한다(pre-commit.d/20-source-header).
- tests/에 isolated_repo.py · test_githooks_dispatcher.py가 있다.
- 판정 로직(card_gate.py)은 agile-hooks TASK-73이 만든다. 이 저장소는 호출만 한다.

### Assessment
디스패처에 stdin 버퍼링을 넣되 pre-push일 때만 적용해 기존 두 훅의 동작을 바꾸지 않는다. 서명 검사는 git만으로 할 수 있으니 플러그인 안에서 직접 하고(%G? = N), 카드 검사는 card_gate.py에 맡겨 로직을 복제하지 않는다. 서명 없는 커밋 거부는 GF-130(에이전트 판정)과 독립적으로 동작한다. --no-verify는 막을 수 없으므로 최종 방어는 upkeep CI다.

### Plan
1. AC #1: 디스패처 테스트 먼저(pre-push에서 두 플러그인이 같은 stdin을 받음, 기존 훅 불변) → 구현, githooks/pre-push 추가.
2. AC #2 · #4: card-gates 플러그인 서명 검사 테스트 → 구현.
3. AC #3: Done 카드 검사 테스트(card_gate.py 대역으로 통과 · 거부, 삭제 push) → 구현. TASK-73 card_gate.py가 나오면 실제 연동 확인.
4. AC #5: GF-149 --plugins 연동, README.
<!-- SECTION:PLAN:END -->
