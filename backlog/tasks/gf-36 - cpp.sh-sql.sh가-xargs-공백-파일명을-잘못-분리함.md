---
id: GF-36
title: cpp.sh/sql.sh가 xargs 공백 파일명을 잘못 분리함
status: Done
assignee: []
created_date: '2026-08-24 08:13'
updated_date: '2026-08-24 12:48'
labels: []
dependencies: []
type: bug
ordinal: 36000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
git diff --cached --name-only 결과를 echo | xargs로 넘기면 공백 포함 파일명이 여러 인자로 쪼개진다. -z/-0으로 NUL 구분해야 함.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
cpp.sh/sql.sh: git diff -z + xargs -0로 NUL 구분(공백 파일명 안전), 임시파일 경유(셸 변수는 NUL 못담음). 공백 파일명 시나리오 bats로 회귀 고정.
<!-- SECTION:FINAL_SUMMARY:END -->
