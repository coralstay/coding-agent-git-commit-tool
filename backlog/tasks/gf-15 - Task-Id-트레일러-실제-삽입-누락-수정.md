---
id: GF-15
title: Task-Id 트레일러 실제 삽입 누락 수정
status: Done
assignee: []
created_date: '2026-08-24 04:23'
updated_date: '2026-08-24 04:24'
labels: []
dependencies: []
type: bug
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
decision-4는 브랜치명이 Task-Id 패턴에 매치되면 post-commit이 Task-Id: GF-N 트레일러를 자동 삽입한다고 설계했지만, 실제로는 commit-msg의 거부(reject) 로직만 구현되고 삽입 코드가 빠져있었다. 실제 GitHub에서 fresh clone한 저장소로 리얼 테스트하다가 발견함.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
post-commit에 브랜치명에서 <prefix>-<번호>를 찾아 Task-Id 트레일러를 삽입하는 로직 추가(commit-msg와 동일한 패턴 재사용). exempt 브랜치는 없음, GF-42/커스텀 prefix PROJ-7 모두 정상 삽입 검증. GitHub fresh clone 기반 실사용 테스트 중 발견된 구현 누락 버그.
<!-- SECTION:FINAL_SUMMARY:END -->
