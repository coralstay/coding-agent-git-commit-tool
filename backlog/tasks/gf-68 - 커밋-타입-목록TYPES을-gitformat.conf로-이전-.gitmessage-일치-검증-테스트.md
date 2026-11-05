---
id: GF-68
title: 커밋 타입 목록(TYPES)을 gitformat.conf로 이전 + .gitmessage 일치 검증 테스트
status: Done
assignee: []
created_date: '2026-08-27 20:35'
updated_date: '2026-08-27 20:48'
labels: []
dependencies: []
ordinal: 66000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
hooks/commit-msg의 TYPES 변수(feat/fix/docs/style/refactor/perf/test/build/ci/chore/revert)와 .gitmessage의 사람이 읽는 타입 설명이 서로 다른 파일에 독립적으로 중복돼 있다(gitformat.conf 신설 때 놓친 항목). TYPES를 gitformat.conf로 옮겨 commit-msg가 거기서 정규식을 조립하게 하고, .gitmessage는 계속 사람이 직접 관리하는 정적 파일로 두되 gitformat.conf의 타입 목록과 .gitmessage에 적힌 목록이 정확히 일치하는지 검증하는 bats 테스트를 추가한다(resolve_self 6종 동일성 검증과 같은 패턴, GF-62 참고). 런타임 결합(설치 시 자동 생성)은 하지 않는다 - 누락되면 테스트가 즉시 잡는 방식을 택함.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 hooks/commit-msg가 TYPES를 gitformat.conf(다중값 키)에서 읽어 정규식을 조립한다
- [x] #2 gitformat.conf의 타입 목록과 .gitmessage에 적힌 타입 목록이 정확히 일치하는지 검증하는 bats 테스트가 추가된다
- [x] #3 일부러 한쪽 목록에만 타입을 추가/삭제했을 때 테스트가 실패하는 것을 확인한다
- [x] #4 동작 변경 없음 - tests/robustness-commit-msg.bats, tests/smoke.bats가 전과 동일하게 통과하고 shellcheck -s sh 경고가 없다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
gitformat.conf에 gitformat.type 다중값 키(11개) 추가. hooks/commit-msg가 여기서 읽어 파이프(|)로 이어붙여 정규식을 조립하도록 전환. tests/consistency.bats 신설(GF-62의 향후 유사 테스트도 여기 모을 예정) - gitformat.conf와 .gitmessage의 타입 목록이 정확히 일치하는지 검증. 일부러 conf에만 타입을 추가했을 때 테스트가 실패하는 것, 되돌리면 다시 통과하는 것을 실제로 확인. bats 22/22(commit-msg) + 1/1(consistency) 통과, shellcheck -s sh 경고 없음.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
커밋 타입 목록을 gitformat.conf(gitformat.type 다중값)로 이전하고, .gitmessage와의 일치 여부를 검증하는 tests/consistency.bats를 신설했다. 런타임 결합 없이 테스트로만 drift를 방지한다. bats+shellcheck로 동작 무변경 확인, 네거티브 케이스도 실증.
<!-- SECTION:FINAL_SUMMARY:END -->
