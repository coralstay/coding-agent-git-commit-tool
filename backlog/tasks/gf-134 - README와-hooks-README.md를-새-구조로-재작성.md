---
id: GF-134
title: README와 hooks/README.md를 새 구조로 재작성
status: To Do
assignee: []
created_date: '2026-09-25 19:34'
updated_date: '2026-09-25 21:43'
labels:
  - docs
dependencies:
  - GF-133
references:
  - decision-18
  - decision-19
  - decision-22
documentation:
  - backlog/docs/doc-13 - git-format-재설계-계획-—-커밋-규칙을-prepare-commit-msg로-통합.md
  - backlog/docs/doc-14 - 용어-정리-—-턴-트랜스크립트-귀속-마커-구분.md
  - backlog/docs/doc-15 - 훅-실행-경로-실측-git-2.54.0.md
  - backlog/docs/doc-16 - 토큰·툴콜-측정-방법과-한계.md
  - backlog/docs/doc-17 - 에이전트-판정-신호-레퍼런스.md
  - backlog/docs/doc-18 - 재설계-작업-순서와-의존성.md
modified_files:
  - README.md
  - hooks/README.md
priority: medium
type: docs
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
훅이 3개에서 2개로 줄고 생애주기가 완전히 바뀌므로 문서가 전부 어긋난다. 코드와 문서가 갈라지지 않게 재설계 마무리로 함께 고친다.

.gitmessage를 삭제하므로 그 안에 있던 원자적 커밋 규칙 문장을 README로 옮기면서 '커밋 하나 = 논리적 변경 하나 = 함수 하나 수준'으로 구체화한다. 이 규칙은 이 프로젝트가 만드는 모든 저장소에 적용되는 정책이다.

python3 부재 시 실패 양상도 달라졌다 — 이전에는 트레일러만 조용히 누락됐지만 이제 커밋이 막힌다. 조용한 실패에서 드러나는 실패로 바뀐 것이므로 그대로 적는다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 README의 훅 생애주기 설명이 prepare-commit-msg와 applypatch-msg 2개 구조로 바뀐다
- [ ] #2 README의 트레일러 표가 새 집합(Task-Id, AI-Agent, Co-Authored-By, Tokens-Used, Tool-Calls, Hooks-Commit)을 반영한다
- [ ] #3 README의 예시 커밋이 새 footer 형식을 보여준다
- [ ] #4 README 설치 안내에서 commit.template 언급이 제거된다
- [ ] #5 커밋 하나 = 논리적 변경 하나 = 함수 하나 수준 규칙이 README에 명시된다
- [ ] #6 python3 부재 시 커밋이 막힌다는 사실이 반영된다
- [ ] #7 에디터로는 커밋할 수 없고 -m을 써야 한다는 점이 명시된다
- [ ] #8 git am이 거부된다는 점과 plumbing은 훅이 없다는 한계가 명시된다
- [ ] #9 hooks/README.md가 새 2개 훅 구조로 재작성된다
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 python3 -m unittest 스위트 전체 통과 (이관 전이면 bats tests/ 통과)
- [ ] #2 ruff check 통과
- [ ] #3 이 저장소 자신의 커밋이 새 훅으로 정상 생성되는지 확인
<!-- DOD:END -->
