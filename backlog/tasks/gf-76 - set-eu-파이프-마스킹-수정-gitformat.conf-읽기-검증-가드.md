---
id: GF-76
title: set -eu 파이프 마스킹 수정 + gitformat.conf 읽기 검증 가드
status: Done
assignee: []
created_date: '2026-08-28 10:07'
updated_date: '2026-08-28 10:12'
labels: []
dependencies: []
ordinal: 74000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
commit-msg의 TYPES 계산이 파이프(git config --get-all | tr)로 되어 있어, git config가 실패해도 마지막 명령(tr)이 항상 성공해 set -e가 못 잡는다. 캐치-후-변환으로 분리한다. 계기로, gitformat.conf를 읽는 8개 파일(hooks 6개 + checks/cpp.sh,java.sh,sql.sh + install.sh) 전부에 CONF 읽기 자체가 실패하면 명확한 에러로 즉시 중단하는 공통 가드를 추가하고, 이 가드가 파일마다 어긋나지 않도록 consistency.bats로 동일성을 보장한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 hooks/commit-msg의 TYPES가 git config 실패 시 set -e로 즉시 중단된다(파이프에 숨지 않는다)
- [x] #2 CONF를 읽는 8개 파일 모두에 gitformat.conf 읽기 실패를 감지하는 동일한 가드 블록이 있다
- [x] #3 tests/consistency.bats에 이 가드 블록이 8개 파일에서 byte-identical한지 검증하는 테스트가 추가된다
- [x] #4 bats 전체와 shellcheck -s sh가 통과한다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
commit-msg의 TYPES 계산을 캐치-후-변환(RAW_TYPES 별도 변수)으로 분리해 git config 실패가 set -e로 즉시 드러나게 함. CONF를 읽는 8개 파일(commit-msg/pre-commit/pre-push/post-commit/checks/{cpp,java,sql}.sh/install.sh) 전부에 'git config --file $CONF --list'로 conf 파일 자체를 검증하는 byte-identical 가드 추가(파일 없음/문법 깨짐 시 exit 128임을 실측 확인). tests/consistency.bats에 8개 파일 동일성 테스트 추가, 네거티브 케이스(pre-push 문구 하나만 바꿔서 테스트 실패 확인 후 원복)로 실제 drift 감지 검증. 격리된 저장소에 문법이 깨진 gitformat.conf를 심어 실제 커밋을 시도, 새 가드가 명확한 에러 메시지로 즉시 막는 것을 실측 확인. CLAUDE.md에 '파이프 왼쪽 명령의 실패를 흘려보내지 말 것' 관례 문서화(이번 TYPES 버그를 근거로). bats 76/76, shellcheck 전체 통과.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
commit-msg TYPES의 파이프 마스킹 버그를 캐치-후-변환으로 고치고, CONF를 읽는 8개 파일 전부에 동일한 조기 진단 가드를 추가했다. consistency.bats로 동일성을 보장하고, 실제 커밋 시나리오로 동작을 실측 검증했다. CLAUDE.md에 재발 방지 관례를 남겼다.
<!-- SECTION:FINAL_SUMMARY:END -->
