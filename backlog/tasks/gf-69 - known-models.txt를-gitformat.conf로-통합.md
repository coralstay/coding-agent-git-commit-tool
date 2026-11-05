---
id: GF-69
title: known-models.txt를 gitformat.conf로 통합
status: Done
assignee: []
created_date: '2026-08-27 20:41'
updated_date: '2026-08-27 20:44'
labels: []
dependencies: []
priority: high
ordinal: 67000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
hooks/checks/known-models.txt(AI-Model 트레일러 화이트리스트)가 gitformat.conf 밖의 별도 파일로 남아 있다. 이 프로젝트의 핵심 목적(커밋 이력을 반정형 데이터로 구조화, 설정을 한 곳에 모으는 gitformat.conf 원칙)에 맞춰 이 화이트리스트도 gitformat.conf의 다중값 키(예: gitformat.knownModel)로 옮긴다. hooks/commit-msg가 known-models.txt 파일을 별도로 읽던 로직을 gitformat.conf --get-all 조회로 바꾼다. 조직이 자체 모델 ID를 추가하고 싶을 때도 gitformat.conf 한 파일만 건드리면 되게 한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 AI-Model 화이트리스트 값 8개(claude-opus-5 등)가 gitformat.conf의 다중값 키로 존재한다
- [x] #2 hooks/commit-msg가 known-models.txt 대신 gitformat.conf에서 화이트리스트를 읽는다
- [x] #3 hooks/checks/known-models.txt 파일은 제거하거나, 더 이상 읽히지 않는다는 점을 명시한 안내로 대체한다
- [x] #4 동작 변경 없음 - tests/robustness-commit-msg.bats, tests/smoke.bats가 전과 동일하게 통과하고 shellcheck -s sh 경고가 없다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
gitformat.conf에 gitformat.knownModel 다중값 키(8개)를 추가하고 knownModelsFile 키는 제거. hooks/commit-msg가 known-models.txt 파일 대신 gitformat.conf --get-all로 화이트리스트를 조회하도록 전환(파일 존재 여부 대신 값 존재 여부로 폴백 판단, 동일 의미). hooks/checks/known-models.txt 파일 삭제. README의 관련 언급 2곳(커스터마이즈 섹션, 저장소 구조 트리) 갱신. bats 22/22 통과, shellcheck -s sh 경고 없음.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
AI-Model 화이트리스트를 별도 파일(known-models.txt)에서 gitformat.conf(gitformat.knownModel 다중값)로 통합해 설정을 한 곳에 모았다. hooks/commit-msg 전환, 파일 삭제, README 갱신 완료. bats+shellcheck로 동작 무변경 확인.
<!-- SECTION:FINAL_SUMMARY:END -->
