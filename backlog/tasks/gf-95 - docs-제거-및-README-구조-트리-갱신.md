---
id: GF-95
title: docs/ 제거 및 README 구조 트리 갱신
status: Done
assignee: []
created_date: '2026-09-10 08:40'
updated_date: '2026-09-10 08:41'
labels: []
dependencies: []
ordinal: 92000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
docs/references/conventional-commits-ko.md를 포함해 docs/ 디렉토리 전체를 제거하고, README.md/README.en.md의 저장소 구조 트리에서 docs/ 항목을 삭제한다. Pro Git 원서는 이미 decision-14로 vendoring 금지된 상태라 이 레포에 다시 넣지 않는다(개인 Books/ 라이브러리에만 별도로 받음).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 docs/ 디렉토리가 저장소에서 완전히 삭제됨
- [x] #2 README.md, README.en.md의 구조 트리에 docs/ 항목이 더 이상 없음
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
docs/ 디렉토리(conventional-commits-ko.md + pro-git 빈 폴더 잔재)를 완전히 삭제하고 README.md/README.en.md 구조 트리에서 docs/ 항목 제거. Pro Git 원문은 decision-14 정책대로 레포에 다시 넣지 않음(개인 Books/ 라이브러리에 별도로만 받음).
<!-- SECTION:FINAL_SUMMARY:END -->
