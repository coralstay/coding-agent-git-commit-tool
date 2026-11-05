---
id: GF-59
title: README에 gitformat.conf 반영 (구조도 + 커스터마이즈)
status: Done
assignee: []
created_date: '2026-08-27 20:29'
updated_date: '2026-08-27 20:59'
labels: []
dependencies: []
ordinal: 57000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GF-44에서 hooks/gitformat.conf가 신설됐지만 README의 저장소 구조 트리와 커스터마이즈 섹션에는 반영되지 않았다. 구조 트리에 hooks/gitformat.conf를 추가하고, 커스터마이즈 섹션에 '내부 기본값은 이 파일에서 관리되며 컨슈머가 직접 건드릴 일은 없다'는 설명을 한 단락 추가한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 README 저장소 구조 트리에 hooks/gitformat.conf가 표시된다
- [x] #2 README 커스터마이즈 섹션에 gitformat.conf의 역할과 gitformat.taskPrefix 등 컨슈머 오버라이드와의 관계가 설명된다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
저장소 구조 트리에 hooks/gitformat.conf 추가. 커스터마이즈 섹션에 gitformat.conf의 역할(내부 기본값 통합 파일, 컨슈머의 git config 오버라이드와 레이어가 다름)을 설명하는 문단 추가. 겸사겸사 tests/ 항목의 decision-7 인용을 decision-8(현재 유효한 결정)로 정정.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
README 저장소 구조 트리와 커스터마이즈 섹션에 hooks/gitformat.conf를 반영했다. tests/ 항목의 오래된 decision-7 인용도 decision-8로 정정.
<!-- SECTION:FINAL_SUMMARY:END -->
