---
id: DRAFT-23
title: 토큰 측정을 편집 시점 체크포인트와 git notes로 옮길지 검토한다
status: Draft
assignee: []
created_date: '2026-10-04 01:43'
updated_date: '2026-10-04 01:43'
labels:
  - measurement
  - spike
dependencies: []
references:
  - decision-27
  - decision-24
documentation:
  - backlog/docs/doc-22 - 유사-프로젝트-조사-—-AI-커밋-출처-기록-도구-비교.md
  - backlog/docs/doc-16 - 토큰·툴콜-측정-방법과-한계.md
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Tokens-Used/Tool-Calls는 커밋 시점에 Claude Code 트랜스크립트를 거슬러 읽어 이 커밋의 파일을 건드린 응답을 재구성한다(decision-27, doc-16). 측정 방법론은 아직 실험 단계이고 Claude Code에만 된다.

git-ai는 다르게 한다(doc-22).
- 에이전트가 파일을 고칠 때마다 체크포인트를 남기고, 커밋할 때 합친다 — 사후 재구성이 없다. Claude Code에서는 PostToolUse 훅으로 같은 일을 할 수 있다.
- 결과를 커밋 메시지가 아니라 git notes(refs/notes/ai)에 둔다. 메시지를 다시 쓰지 않아 append-only(decision-24)와 맞고, rebase·cherry-pick 뒤에도 notes를 옮겨 붙인다. 대신 git log만으로 안 보이고 notes를 따로 push·fetch해야 한다.

두 가지(체크포인트 수집, notes 저장)는 독립적으로 채택할 수 있다. 어느 쪽이 지금 방식보다 나은지 판단할 근거가 필요하다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 같은 세션을 지금 방식과 체크포인트 방식으로 측정해 결과 차이를 비교한다
- [ ] #2 notes 저장 시 push·fetch·rebase에서 기록이 살아남는지 실측한다
- [ ] #3 채택·기각 여부를 decision으로 기록한다
<!-- AC:END -->
