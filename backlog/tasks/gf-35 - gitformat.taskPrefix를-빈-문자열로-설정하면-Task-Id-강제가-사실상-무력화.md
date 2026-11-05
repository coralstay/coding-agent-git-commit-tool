---
id: GF-35
title: gitformat.taskPrefix를 빈 문자열로 설정하면 Task-Id 강제가 사실상 무력화
status: Done
assignee: []
created_date: '2026-08-24 08:13'
updated_date: '2026-08-24 08:17'
labels: []
dependencies: []
type: bug
ordinal: 35000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
git config --get은 빈 문자열도 성공(exit 0)으로 취급해 기본값 폴백이 안 걸림. TASK_PREFIX가 빈 문자열이 되면 정규식이 -[0-9]+로 축소돼 거의 모든 브랜치가 통과한다.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
TASK_PREFIX가 빈 문자열이면 명시적으로 GF 폴백(commit-msg, post-commit 둘 다). 빈 prefix 재현 후 수정 확인.
<!-- SECTION:FINAL_SUMMARY:END -->
