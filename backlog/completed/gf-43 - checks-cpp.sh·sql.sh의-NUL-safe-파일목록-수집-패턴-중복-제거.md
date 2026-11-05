---
id: GF-43
title: checks/cpp.sh·sql.sh의 NUL-safe 파일목록 수집 패턴 중복 제거
status: Done
assignee: []
created_date: '2026-08-27 09:11'
updated_date: '2026-08-27 09:25'
labels: []
dependencies: []
type: task
ordinal: 43000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
cpp.sh와 sql.sh가 거의 동일한 mktemp+trap+git diff --cached -z 파일목록 수집 로직(GF-36 공백 파일명, GF-37 rename 대응 코드)을 각자 갖고 있다. 새 언어 체크를 추가할 때마다 이 패턴을 복사-붙여넣기 하게 되므로 공용 함수로 추출한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 파일목록 수집 로직이 한 곳에만 정의되고 cpp.sh/sql.sh가 재사용한다
- [ ] #2 리팩토링 후에도 tests/checks-cpp.bats, tests/checks-sql.bats가 그대로 통과한다(GF-36 공백 파일명, GF-37 rename 케이스 포함)
<!-- AC:END -->

## Comments

<!-- COMMENTS:BEGIN -->
created: 2026-08-27 09:25
---
독립성 우선 원칙(버그 수정 용이성 + 훅별 셸 교체 가능성)에 따라 cpp.sh/sql.sh 공용 함수화 계획을 폐기. 대체 작업(각 파일 독립적으로 리터럴만 지역화)은 GF-42의 서브태스크로 이관됨.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
공용화 대신 파일별 독립 리터럴 지역화로 방향 전환 — 실제 구현은 GF-42 서브태스크(checks/cpp.sh·sql.sh 리터럴 지역화)에서 진행.
<!-- SECTION:FINAL_SUMMARY:END -->
