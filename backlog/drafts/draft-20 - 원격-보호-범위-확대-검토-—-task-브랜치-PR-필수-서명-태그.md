---
id: DRAFT-20
title: '원격 보호 범위 확대 검토 — task 브랜치, PR 필수, 서명, 태그'
status: Draft
assignee: []
created_date: '2026-09-26 13:22'
updated_date: '2026-09-26 13:22'
labels:
  - policy
dependencies: []
references:
  - decision-24
documentation:
  - backlog/docs/doc-20 - GitHub-원격-강제-설정-관리-—-rulesets와-저장소-설정.md
priority: medium
type: spike
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
현재 ruleset(main-protection)은 `~DEFAULT_BRANCH`만 보호한다. 원격 쪽에 남은 구멍을 정리하고 각각 켤지 판단한다.

## 남은 구멍

**task 브랜치가 보호되지 않는다.** force push로 다시 쓸 수 있다. 그 상태로 merge되면 main 자체는 append-only지만 **에이전트 작업 기록은 이미 위조된 상태**로 들어온다. 대상을 `~ALL`로 넓히면 "push된 이력은 불변"이 완전해지는데, 대신 PR 도중 main 변경을 따라잡을 때 rebase 후 force push를 못 하게 된다 — merge로 따라잡아야 한다(append-only와 일관되지만 운영 부담을 판단해야 한다).

**main에 직접 push가 원격에서 막히지 않는다.** 지금은 로컬 claude-rails 훅만 막는다. 그 훅이 없는 환경이나 웹 UI에서는 그대로 들어간다. ruleset의 `pull_request` 규칙을 켜면 원격이 막는다.

**저장소 설정 자체를 되돌릴 수 있다.** `allow_rebase_merge`를 다시 켜는 것을 막을 장치가 없다 — ruleset은 브랜치를 보호하지 저장소 설정을 보호하지 않는다. 조직 레벨 규칙이 필요한 영역이다.

**서명이 강제되지 않는다.** 누가/무엇이 만든 커밋인지 암호학적으로 확인되지 않는다. 다만 현재 이 저장소 커밋은 `%G?`가 `N`으로 나오므로 켜면 자기 push가 막힌다 — 서명 설정 정리가 선행이다.

**태그는 별도 target이다.** 브랜치 ruleset이 태그 삭제·이동을 커버하지 않는다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 ruleset 대상을 ~ALL로 넓힐지 결정하고 근거를 기록한다 — PR 중 main을 따라잡을 때의 운영 부담을 함께 평가
- [ ] #2 pull_request 규칙(PR 필수)을 켤지 결정한다
- [ ] #3 required_signatures를 켤 조건을 정한다 — 현재 %G?가 N인 원인부터 해소
- [ ] #4 태그 ruleset이 필요한지 판단한다
- [ ] #5 저장소 설정이 되돌려지는 것을 감지할 방법이 있는지 조사한다 (조직 규칙 또는 주기적 확인)
- [ ] #6 결정 결과를 doc-20에 반영한다
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 각 항목에 대해 켠다/안 켠다와 그 근거가 기록됐다
<!-- DOD:END -->
