---
id: GF-25
title: post-commit 상태전이/동시성 견고성 테스트 (상태전이/결함주입)
status: Done
assignee: []
created_date: '2026-08-24 04:48'
updated_date: '2026-08-27 08:59'
labels: []
dependencies:
  - GF-21
type: task
ordinal: 25000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
마커 파일 생명주기, --no-verify, 반복 amend, 트랜스크립트 손상·누락, 재귀가드를 커버
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 상태전이: 마커없음->pre-commit성공->마커있음->post-commit->마커삭제 전이 전부 테스트
- [x] #2 결함주입: 트랜스크립트 JSON이 깨졌을 때 AI-Model만 조용히 생략되고 커밋은 막히지 않는지
- [x] #3 결함주입: jq가 없을 때, HOME이 이상한 값일 때도 커밋이 막히지 않는지
- [x] #4 재귀가드가 실제로 무한루프를 막는지 타임아웃 기반으로 확인
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. tests/robustness-post-commit.bats 신규 작성
2. 상태전이: pre-commit 통과 후 마커 생성 -> post-commit이 읽고 지움(정상 커밋 후 마커 없음), --no-verify로 마커 없이 커밋 -> Verify-Bypassed:true 트레일러 확인
3. 결함주입: 가짜 CLAUDE_CODE_SESSION_ID + 깨진 트랜스크립트 JSON -> AI-Model 트레일러만 생략되고 커밋은 안 막힘 (jq 있을 때만 실행, 없으면 skip)
4. 결함주입: jq를 PATH에서 제거해도 커밋이 안 막힘, HOME이 존재하지 않는 경로여도 안 막힘
5. 재귀가드: timeout 기반으로 커밋이 유한 시간 내 끝나는지 확인 (_GITFORMAT_AMEND_GUARD)
6. bats tests/robustness-post-commit.bats 실행 후 acceptance criteria 체크
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
tests/robustness-post-commit.bats 신규 작성, bats 로컬 실행 6/6 통과. 상태전이 2건(정상커밋/--no-verify), 결함주입 3건(깨진 트랜스크립트/jq 없음/HOME 이상값), 재귀가드 1건(timeout 10초 내 완료 확인).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/post-commit의 마커 생명주기, --no-verify 탐지, AI-Model 결함내성, 재귀가드를 상태전이/결함주입 기법으로 커버하는 bats 테스트 6건 작성. tests/robustness-post-commit.bats, 로컬 bats 실행 6/6 통과로 검증.
<!-- SECTION:FINAL_SUMMARY:END -->
