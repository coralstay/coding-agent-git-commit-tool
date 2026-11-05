---
id: GF-30
title: commit-msg 병합 커밋 예외 로직이 실제로는 절대 작동 안 함
status: Done
assignee: []
created_date: '2026-08-24 08:13'
updated_date: '2026-08-24 08:17'
labels: []
dependencies: []
priority: high
type: bug
ordinal: 30000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
commit-msg 훅은 인자를 1개(메시지 파일 경로)만 받는데, source($2)가 'merge'인지 확인하는 코드는 prepare-commit-msg 훅의 인자 규약과 착각한 것. 실측: git merge --no-ff 시 SOURCE는 항상 비어있어 병합 커밋도 Conventional Commits 정규식 검사를 받아 거부된다. 이 저장소를 쓰는 모든 프로젝트에서 일반적인 non-fast-forward 머지가 전부 막히는 심각한 버그.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
.git/MERGE_HEAD 존재로 병합 여부 판단하도록 수정(기존엔 존재하지도 않는 $2 인자로 검사해 절대 작동 안 했음). 실제 non-ff merge로 검증.
<!-- SECTION:FINAL_SUMMARY:END -->
