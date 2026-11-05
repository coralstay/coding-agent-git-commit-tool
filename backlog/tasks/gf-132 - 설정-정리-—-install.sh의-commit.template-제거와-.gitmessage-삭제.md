---
id: GF-132
title: 설정 정리 — install.sh의 commit.template 제거와 .gitmessage 삭제
status: To Do
assignee: []
created_date: '2026-09-25 19:34'
updated_date: '2026-09-25 21:43'
labels:
  - hooks
  - install
dependencies:
  - GF-128
references:
  - decision-18
  - decision-19
documentation:
  - backlog/docs/doc-13 - git-format-재설계-계획-—-커밋-규칙을-prepare-commit-msg로-통합.md
  - backlog/docs/doc-14 - 용어-정리-—-턴-트랜스크립트-귀속-마커-구분.md
  - backlog/docs/doc-18 - 재설계-작업-순서와-의존성.md
modified_files:
  - install.sh
  - .gitmessage
priority: high
type: chore
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
구 훅 3개 삭제는 각 기능을 옮기는 태스크(DRAFT-20~22)에서 함께 처리하므로 이 태스크에는 남지 않는다. 여기서는 훅과 무관하게 남는 설정 정리만 한다.

commit.template 제거가 핵심이다. 이 설정은 에디터에 뜨는 작성 안내가 목적인데, 새 설계는 에디터 경로를 거부하므로(decision-18) 영구히 쓰이지 않는다. 같은 이유로 .gitmessage 파일도 필요 없어진다 — 다만 그 안의 원자적 커밋 규칙 문장은 README로 옮겨야 한다(DRAFT-29).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 install.sh에서 로컬과 전역의 commit.template 설정을 제거한다
- [ ] #2 install.sh의 commit.template 관련 안내 출력도 함께 제거한다
- [ ] #3 .gitmessage 파일을 삭제한다
- [ ] #4 install.sh가 훅 파일 목록을 글롭으로 다루므로 훅 추가 삭제에 스크립트 수정이 필요 없음을 확인한다
- [ ] #5 shellcheck -s sh install.sh가 통과한다
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 python3 -m unittest 스위트 전체 통과 (이관 전이면 bats tests/ 통과)
- [ ] #2 ruff check 통과
- [ ] #3 이 저장소 자신의 커밋이 새 훅으로 정상 생성되는지 확인
<!-- DOD:END -->
