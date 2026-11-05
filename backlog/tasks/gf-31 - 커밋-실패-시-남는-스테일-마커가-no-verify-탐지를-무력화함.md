---
id: GF-31
title: 커밋 실패 시 남는 스테일 마커가 --no-verify 탐지를 무력화함
status: Done
assignee: []
created_date: '2026-08-24 08:13'
updated_date: '2026-08-24 08:17'
labels: []
dependencies: []
priority: high
type: bug
ordinal: 31000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
pre-commit이 통과해 마커를 쓴 뒤 commit-msg가 메시지를 거부하면 커밋 자체가 안 생성돼 post-commit이 안 돌고 마커가 안 지워진다. 이후 관련없는 --no-verify 커밋이 그 스테일 마커를 소비해 Verify-Bypassed가 안 붙는다. commit-msg가 거부할 때 마커를 같이 지워야 한다.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
commit-msg에 EXIT trap 추가해 0이 아닌 종료 시 검증마커를 항상 삭제. pre-commit통과->commit-msg거부->--no-verify커밋 시나리오로 재현 후 수정 확인.
<!-- SECTION:FINAL_SUMMARY:END -->
