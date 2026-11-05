---
id: GF-131
title: applypatch-msg 훅 신설 — git am 차단
status: To Do
assignee: []
created_date: '2026-09-25 19:34'
updated_date: '2026-09-25 21:43'
labels:
  - hooks
dependencies:
  - GF-125
references:
  - decision-18
documentation:
  - backlog/docs/doc-13 - git-format-재설계-계획-—-커밋-규칙을-prepare-commit-msg로-통합.md
  - backlog/docs/doc-15 - 훅-실행-경로-실측-git-2.54.0.md
  - backlog/docs/doc-18 - 재설계-작업-순서와-의존성.md
modified_files:
  - hooks/applypatch-msg
priority: medium
type: feature
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
실측으로 git am은 prepare-commit-msg를 실행하지 않는다 — applypatch-msg, pre-applypatch, post-applypatch만 돈다. 따라서 검사·검증·트레일러를 prepare-commit-msg로 모아도 git am으로 적용한 패치는 규칙 밖에 남는다.

패치 적용 경로를 지원하는 대신 거부한다. 이 저장소의 작업 방식은 rebase와 cherry-pick이고, 그 둘은 prepare-commit-msg를 타므로 대안이 이미 있다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 git am으로 패치를 적용하면 applypatch-msg가 거부해 커밋이 만들어지지 않는다
- [ ] #2 거부 메시지가 rebase 또는 cherry-pick을 쓰라고 안내한다
- [ ] #3 설정 파일을 읽지 않으므로 설정 읽기 가드가 없다 (의존이 없다는 뜻)
- [ ] #4 표준 라이브러리만 사용하고 stdout/stderr 인코딩을 UTF-8로 고정한다
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 python3 -m unittest 스위트 전체 통과 (이관 전이면 bats tests/ 통과)
- [ ] #2 ruff check 통과
- [ ] #3 이 저장소 자신의 커밋이 새 훅으로 정상 생성되는지 확인
<!-- DOD:END -->
