---
id: GF-137
title: 'append-only 이력 정책 결정과 문서화, 원격 강제 적용'
status: Done
assignee:
  - '@claude'
created_date: '2026-09-26 13:24'
updated_date: '2026-10-03 03:31'
labels:
  - policy
  - docs
dependencies: []
references:
  - decision-24
documentation:
  - backlog/docs/doc-19 - 이력을-바꾸는-git-연산별-훅-판별-방법-실측.md
  - backlog/docs/doc-20 - GitHub-원격-강제-설정-관리-—-rulesets와-저장소-설정.md
priority: high
type: docs
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
이력 재작성에 대한 정책이 없었고, 오히려 PR을 rebase-merge로 병합하는 관행이 있었다. 그 관행이 실제로 기록을 거짓으로 만들고 있었다 — 실측: main의 커밋들이 Signed-off-by: cpu-once를 달고 있는데 실제 committer는 coralstay이고 %G?가 전부 N이다.

이 태스크는 정책을 결정하고 문서화하고, 원격 쪽 강제를 적용한다. 훅 구현은 DRAFT-18이 맡는다.

전제는 README에 적힌 "에이전트가 프로그래밍하고 git이 그 작업의 로그로 동작한다"다. 로그라면 append-only가 맞다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 append-only 이력 정책을 decision으로 기록한다 — 연산별 허용/거부와 금지선(공개된 이력)
- [x] #2 이력을 바꾸는 git 연산별 훅 판별 방법을 실측해 문서로 남긴다
- [x] #3 우회 경로를 전수 조사해 문서에 남긴다 — 훅이 없는 경로, 판별 불가 경로, 로컬이 닿지 않는 경로, 오탐
- [x] #4 GitHub 원격 강제를 적용한다 — 병합 방식을 머지 커밋만 남기고 force push와 브랜치 삭제를 막는다
- [x] #5 원격 설정 관리 문서를 만든다 — 현재 상태, 켜면 안 되는 규칙, 확인·변경 명령, 함정
- [x] #6 claude-rails의 fast-forward 전용 강제 훅이 정책과 충돌하는 점을 그쪽 저장소에 기록한다
- [x] #7 후속 작업을 드래프트로 남긴다 — 로컬 훅 강제, CI 트레일러 정합성 검사, 원격 보호 범위 확대
- [x] #8 기존 rebase-merge 지시가 폐기됐음을 메모리에 반영한다
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 실제로 머지 커밋으로 병합이 되는지 확인
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
마무리 검증(2026-10-03): #1 decision-24 파일 존재·accepted. #2·#3 doc-19의 '결론 표'와 '우회 경로 전수 조사' 절. #4 gh api: allow_merge_commit=true, rebase=false, squash=false, ruleset 23313297 active(deletion, non_fast_forward). #5 doc-20(현재 상태·켜면 안 되는 규칙·확인/변경 방법·함정 절). #6 claude-rails 저장소 decision-10·decision-11, task-24(pre_merge_check.py 제거). #7 DRAFT-18·19·20 존재. #8 메모리 feedback_rebase_merge.md에 2026-09-26 정책 뒤집힘 기록. DoD: 이 태스크의 커밋이 들어간 PR #39가 머지 커밋 0e6cf0c(부모 2개)로 병합됨.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
append-only 이력 정책을 decision-24로 정하고, 연산별 판별 방법과 우회 경로를 doc-19, 원격 강제 설정을 doc-20에 정리했다. GitHub에 머지 커밋 전용 병합과 force push·삭제 금지 ruleset을 적용했고, 후속 작업은 DRAFT-18·19·20으로 남겼다. claude-rails 쪽 충돌은 그 저장소 decision-10·11과 task-24에 기록됐다. gh api 결과와 PR #39의 머지 커밋(부모 2개)으로 확인했다.
<!-- SECTION:FINAL_SUMMARY:END -->
