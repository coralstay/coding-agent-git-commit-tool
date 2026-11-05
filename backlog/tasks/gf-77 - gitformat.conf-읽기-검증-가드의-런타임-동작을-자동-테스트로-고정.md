---
id: GF-77
title: gitformat.conf 읽기 검증 가드의 런타임 동작을 자동 테스트로 고정
status: Done
assignee: []
created_date: '2026-08-28 10:19'
updated_date: '2026-08-28 10:23'
labels: []
dependencies: []
ordinal: 75000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GF-76에서 CONF를 읽는 8개 파일(commit-msg/pre-commit/pre-push/post-commit/checks/{cpp,java,sql}.sh/install.sh)에 gitformat.conf 읽기 검증 가드를 추가했다. tests/consistency.bats는 이 가드 블록이 8개 파일에서 텍스트로 동일한지만 검증하고, 실제로 conf가 깨졌을 때 각 파일이 정말 그 에러로 즉시 멈추는지는 수동으로 1회 확인했을 뿐 자동 테스트가 없다. 8개 파일 각각에 대해 gitformat.conf를 깨뜨린 상태로 직접 실행해 exit 1과 에러 메시지를 확인하는 bats 테스트를 추가한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 8개 파일 각각에 대해, gitformat.conf가 깨진 상태에서 실행하면 exit 0이 아니고 "gitformat: gitformat.conf를 읽을 수 없습니다" 메시지가 출력되는 테스트가 있다
- [x] #2 테스트는 진짜 저장소의 hooks/gitformat.conf를 건드리지 않고 격리된 사본에서만 conf를 깨뜨린다
- [x] #3 bats 전체와 shellcheck -s sh가 통과한다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
tests/conf-guard.bats 신설, 8개 케이스(commit-msg/pre-commit/pre-push/post-commit/checks/{cpp,java,sql}.sh/install.sh). 매 테스트마다 hooks/를 mktemp 임시 디렉터리로 복사해 그 사본의 gitformat.conf만 깨뜨리고, 각 스크립트를 직접 실행해(git commit 전체 흐름이 아니라 sh <스크립트> 직접 호출) exit 0이 아니고 'gitformat: gitformat.conf를 읽을 수 없습니다' 메시지가 나오는지 확인. install.sh는 hooks/+install.sh를 함께 복사해 별도 clone 구조로 테스트. 네거티브 케이스(checks/sql.sh의 가드 블록을 일시적으로 제거해 테스트가 실패하는지 확인 후 원복)로 실제 회귀 감지를 검증. 진짜 저장소의 hooks/gitformat.conf는 git status로 매번 clean 확인. bats 전체 84/84, shellcheck 전체 통과.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
GF-76의 gitformat.conf 읽기 검증 가드가 실제로 conf 파일이 깨졌을 때 8개 파일 모두에서 정말 동작하는지 런타임 bats 테스트(tests/conf-guard.bats)로 고정했다. 이전엔 텍스트 동일성만 테스트되고 실제 동작은 수동 확인 1회뿐이었다.
<!-- SECTION:FINAL_SUMMARY:END -->
