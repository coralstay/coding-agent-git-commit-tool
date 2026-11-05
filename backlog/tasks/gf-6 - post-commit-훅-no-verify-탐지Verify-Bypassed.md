---
id: GF-6
title: 'post-commit 훅: --no-verify 탐지(Verify-Bypassed)'
status: Done
assignee: []
created_date: '2026-08-24 03:12'
updated_date: '2026-08-24 03:38'
labels: []
dependencies:
  - GF-3
type: task
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
검증마커 유무로 --no-verify 판단, amend로 Verify-Bypassed 트레일러 삽입, 재귀가드+멱등성(decision-3)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 --no-verify로 커밋해도 무한루프 없이 Verify-Bypassed: true가 삽입된다
- [x] #2 정상 커밋에는 트레일러가 붙지 않는다
- [x] #3 --amend를 반복해도 트레일러가 중복되지 않는다
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/post-commit 작성: pre-commit 마커 존재 여부로 --no-verify 판단, git interpret-trailers --if-exists doNothing으로 Verify-Bypassed 트레일러 멱등 삽입, _GITFORMAT_AMEND_GUARD로 재귀 방지, 확인 직후 마커 항상 삭제로 스테일 마커 방지. 격리 테스트 저장소에서 정상/--no-verify/반복amend/연속정상 4개 시나리오 실제 커밋으로 검증 완료.
<!-- SECTION:FINAL_SUMMARY:END -->
