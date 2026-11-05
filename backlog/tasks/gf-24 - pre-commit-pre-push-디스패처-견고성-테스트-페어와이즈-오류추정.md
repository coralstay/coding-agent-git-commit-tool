---
id: GF-24
title: pre-commit/pre-push 디스패처 견고성 테스트 (페어와이즈/오류추정)
status: Done
assignee: []
created_date: '2026-08-24 04:48'
updated_date: '2026-08-27 08:57'
labels: []
dependencies:
  - GF-21
type: task
ordinal: 24000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
다중 언어 동시 존재, 도구 부재, 손상된 매니페스트 파일, 심볼릭 링크 설치 경로(GF-16 재확인)를 커버
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 페어와이즈: ts+python+sql처럼 2개 이상 언어가 한 저장소에 동시에 있을 때 전부 개별 실행되는지
- [x] #2 오류추정: package.json이 손상된 JSON일 때, CMakeLists.txt가 있지만 cmake 없을 때 등
- [x] #3 template/(심볼릭 링크) 경로로 설치된 저장소에서 checks/가 정확히 resolve되는지 회귀 테스트로 고정
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. tests/robustness-dispatch.bats 신규 작성
2. 페어와이즈: ts+python+sql 동시 존재 시 (a) 전부 클린이면 셋 다 실행되고 통과 (b) python만 깨지면 sql 도달 전 커밋이 막힘(디스패치 순서 확인) (c) python 클린+sql만 깨지면 sql이 막음
3. 오류추정: package.json이 손상된 JSON이어도 pre-push의 has_npm_script가 안전하게 건너뜀, CMakeLists.txt는 있지만 cmake가 PATH에 없으면 pre-push가 조용히 건너뜀
4. GF-16 회귀: 실제 install.sh --global을 격리된 HOME(mktemp)으로 실행해 template/ symlink 경유로 새 저장소를 init하고, pre-commit이 checks/를 정확히 resolve하는지(ruff가 실제로 실행되어 커밋을 막는지)로 검증
5. bats tests/robustness-dispatch.bats 실행 후 acceptance criteria 체크
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
tests/robustness-dispatch.bats 신규 작성, bats 로컬 실행 6/6 통과. 페어와이즈 3건(다중언어 동시 클린/python실패/sql실패), 오류추정 2건(손상된 package.json, cmake 없이 CMakeLists.txt), GF-16 회귀 1건(격리 HOME으로 실제 install.sh --global 실행 후 symlink 경유 신규 저장소에서 ruff가 실제로 실행됨을 확인).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/pre-commit·pre-push 디스패처를 페어와이즈/오류추정 기법으로 커버하는 bats 테스트 6건 작성. tests/robustness-dispatch.bats, 로컬 bats 실행 6/6 통과로 검증. GF-16(심볼릭 링크 경로 resolve) 회귀도 실제 install.sh --global(격리 HOME)로 재현해 고정.
<!-- SECTION:FINAL_SUMMARY:END -->
