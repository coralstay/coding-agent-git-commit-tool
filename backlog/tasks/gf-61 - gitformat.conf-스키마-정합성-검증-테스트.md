---
id: GF-61
title: gitformat.conf 스키마 정합성 검증 테스트
status: Done
assignee: []
created_date: '2026-08-27 20:29'
updated_date: '2026-08-27 20:53'
labels: []
dependencies: []
ordinal: 59000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
각 훅이 참조하는 gitformat.conf 키(marker.*, trailer.*, aiToolClaudeCode, coAuthoredBy, sqlDialectDefault, cpp.ext, taskPrefixDefault, markerFile, knownModelsFile 등)가 실제로 conf 파일에 존재하고 값이 비어있지 않은지 검증하는 테스트를 추가한다. 키 오타나 누락이 나면 각 훅이 개별적으로 조용히 오동작하는 걸 방지한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 gitformat.conf의 모든 필수 키가 존재하고 비어있지 않은지 검증하는 bats 케이스(또는 셸 스크립트 기반 체크)가 추가된다
- [x] #2 일부러 키를 빠뜨리거나 값을 비웠을 때 테스트가 실패로 잡아내는 것을 실제로 확인한다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
tests/consistency.bats에 gitformat.conf의 24개 키(hooks/*, checks/*.sh가 실제 참조하는 키를 grep으로 전수 조사) 전부가 존재하고 값이 비어있지 않은지 검증하는 케이스를 추가. 키를 일부러 unset했을 때 테스트가 실패하는 것, 복원하면 다시 통과하는 것을 실제로 확인. bats 전체 62/62 통과, shellcheck 전체 파일 경고 없음. 한계: 키 목록이 자동 추출이 아니라 테스트 파일에 수동으로 나열돼 있어, 새 키를 추가하면서 이 목록 갱신을 깜빡할 수 있음 - 주석으로 명시해둠.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
gitformat.conf의 필수 키 24개가 전부 존재하고 비어있지 않은지 검증하는 bats 테스트를 tests/consistency.bats에 추가했다. 네거티브 케이스(키 제거 시 실패)를 실제로 확인. bats+shellcheck 전체 통과로 회귀 없음 확인.
<!-- SECTION:FINAL_SUMMARY:END -->
