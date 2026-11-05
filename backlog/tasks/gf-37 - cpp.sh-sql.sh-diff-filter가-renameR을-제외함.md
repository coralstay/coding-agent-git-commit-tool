---
id: GF-37
title: cpp.sh/sql.sh diff-filter가 rename(R)을 제외함
status: Done
assignee: []
created_date: '2026-08-24 08:13'
updated_date: '2026-08-24 12:48'
labels: []
dependencies: []
type: bug
ordinal: 37000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
--diff-filter=ACM은 rename 상태(R)를 포함 안 함. 파일을 리네임하면서 동시에 수정한 경우 clang-format/sqlfluff 체크를 건너뛴다. ACMR로 바꿔야 함.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
cpp.sh/sql.sh diff-filter를 ACM->ACMR로 확장해 rename 상태 파일도 검사. 리네임+수정 시나리오 bats로 회귀 고정.
<!-- SECTION:FINAL_SUMMARY:END -->
