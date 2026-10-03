---
id: GF-141
title: 훅 주석에 남은 pre-commit·bats 언급 정리
status: In Progress
assignee:
  - '@claude'
created_date: '2026-10-03 08:11'
updated_date: '2026-10-03 12:16'
labels:
  - docs
  - hooks
dependencies: []
references:
  - decision-16
  - decision-21
  - decision-23
  - GF-127
  - GF-128
documentation:
  - backlog/docs/doc-12 - consistency.bats-바이트-동일성-검사-폐지-경위와-대체-행위-검증.md
  - 'https://claude.ai/artifact/6rCLn6LHGfXNpZKSstZR4W'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
훅 해부 아티팩트를 코드와 대조하다(2026-10-03) 훅 주석 일부가 이미 사라진 구조를 설명하고 있는 걸 발견했다. 파일 하나만 읽고 동작을 파악하는 게 이 저장소의 감사 가능성 원칙(decision-16)이라, 주석이 틀리면 그 원칙이 깨진다.

발견한 곳:
- hooks/prepare-commit-msg 첫머리: "지금 하는 일은 두 가지"라고 하지만 실제로는 검증마커 기록까지 세 가지다.
- hooks/commit-msg validate_format(): 타입 목록 일치를 tests/robustness-commit-msg.bats가 검증한다고 적었는데 bats는 decision-21로 사라졌다(지금은 tests/test_config_keys_match_hooks.py).
- hooks/commit-msg 끝의 finally 주석, hooks/post-commit detect_verify_bypass() 주석: pre-commit이 마커를 남긴다고 적었지만 pre-commit 훅은 없고 prepare-commit-msg가 쓴다.

범위: GF-127/GF-128이 commit-msg·post-commit의 로직을 prepare-commit-msg로 옮기며 두 파일을 정리할 예정이라 AC 3·4는 그때 다시 바뀔 수 있다. 승격 시점(2026-10-03)에 유저가 그 겹침을 알고도 AC 전체를 이대로 진행하기로 했다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 prepare-commit-msg 첫머리 주석이 실제 동작(재생 면제·에디터 거부·마커 기록)과 일치한다
- [ ] #2 commit-msg 주석이 가리키는 테스트 파일이 실제로 존재한다
- [ ] #3 commit-msg finally 주석이 마커 작성 주체를 prepare-commit-msg로 적는다
- [ ] #4 post-commit detect_verify_bypass() 주석이 마커 작성 주체를 prepare-commit-msg로 적는다
- [ ] #5 동작 변경 없음 — 기존 테스트 전부 통과
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
AC1~4 주석 정정 완료(da3bae4, 889a100, a89e37e). 매 커밋 전 python3 -m unittest discover -s tests 106건 OK, ruff check 통과.

AC 밖 발견: hooks/post-commit 첫머리(6행) "pre-commit은 시작 시점에 마커를 지우고, 통과하면 끝에 다시 쓴다" — pre-commit은 없고 prepare-commit-msg는 마커를 조건 없이 쓴다. 범위 확장 여부를 유저에게 확인 중.
<!-- SECTION:NOTES:END -->
