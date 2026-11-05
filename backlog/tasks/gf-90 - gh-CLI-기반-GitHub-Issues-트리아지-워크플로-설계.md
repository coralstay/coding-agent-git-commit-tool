---
id: GF-90
title: gh CLI 기반 GitHub Issues 트리아지 워크플로 설계
status: Done
assignee: []
created_date: '2026-09-03 11:40'
updated_date: '2026-09-03 11:41'
labels: []
milestone: m-1
dependencies: []
ordinal: 88000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GitHub Issues(공개 사용자 리포트)와 backlog.md(내부 태스크 관리, GF-<번호>)가 지금은 완전히 분리돼 있다. gh CLI로 이슈를 조회·라벨링·응답·종료하는 흐름을 정하고, 이슈가 실제 작업으로 이어질 때 backlog task와 어떻게 연결(예: 이슈 URL을 backlog task의 --ref로 남기는 식)할지 정한다. Claude와 함께 이 트리아지를 굴릴 방법(예: 반복 트리아지용 슬래시 커맨드/스킬)도 함께 설계한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 gh CLI로 오픈 이슈를 조회·필터링(라벨/상태별)하는 표준 명령 세트가 정리된다
- [ ] #2 이슈 → backlog task 전환 규칙이 정해진다 (어떤 이슈가 task로 승격되는지, 승격 시 이슈 URL을 backlog task에 어떻게 연결하는지)
- [ ] #3 이슈에 라벨/댓글/종료를 다는 책임과 절차(사람이 직접 vs Claude가 gh CLI로 대신 수행)가 정리된다
- [ ] #4 Claude와 함께 반복적으로 트리아지를 돌릴 방법(스킬/슬래시 커맨드 등)이 프로토타입되거나, 프로토타입 없이 수동 워크플로만으로 시작할지 결정된다
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
사용자 결정: gh CLI 기반 GitHub Issues 트리아지 도입을 하지 않기로 함. 이유는 대화에서 별도로 설명되지 않았고, 사용자가 '도입은 하지 않는걸로'라고만 확정함. 워크플로 설계/프로토타입 없이 결정으로 종료하며, AC 1~4는 객관적 검증 증거가 없어 미체크 상태로 남긴다.
<!-- SECTION:FINAL_SUMMARY:END -->
