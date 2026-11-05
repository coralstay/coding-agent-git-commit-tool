---
id: GF-78
title: gitformat.branchExempt --add가 기본 예외 브랜치를 덮어써버리는 버그 수정
status: Done
assignee: []
created_date: '2026-08-28 14:12'
updated_date: '2026-08-28 14:17'
labels: []
dependencies: []
ordinal: 76000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
README가 안내하는 대로 git config --add gitformat.branchExempt "hotfix/*"를 실행하면, 이후 그 저장소에서는 main/master/develop/release/*조차 더 이상 예외 브랜치로 인식되지 않아 커밋이 거부된다. hooks/commit-msg의 EXEMPT 계산이 "로컬 오버라이드가 있으면 그것만 쓰고, 없으면 gitformat.conf 기본값만 쓴다"는 폴백(||) 구조라서, 로컬에 하나라도 값이 추가되는 순간 내장 기본값 4개가 통째로 사라진다. 실제로 재현 확인함(격리된 저장소에서 add 전엔 main 통과, add 후엔 동일 main이 "브랜치명에 GF-<번호> 패턴이 없습니다"로 거부됨 - 에러 메시지 자체가 "main은 예외"라고 말하는데 실제로는 거부되는 자기모순 상태). taskPrefix(단일값, override 의미)와 달리 branchExempt는 README에서 --add로 안내하므로 로컬 값과 내장 기본값을 합쳐야(union) 의도에 맞다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 로컬에 gitformat.branchExempt를 --add한 뒤에도 main/master/develop/release/*가 여전히 예외 브랜치로 동작한다
- [x] #2 로컬에 추가한 패턴도 함께 예외로 동작한다(둘 다 살아있음, union)
- [x] #3 로컬 오버라이드가 전혀 없는 기존 동작(기본 4개 예외)은 그대로 유지된다
- [x] #4 이 시나리오를 검증하는 bats 테스트가 추가된다
- [x] #5 bats 전체와 shellcheck -s sh가 통과한다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
hooks/commit-msg의 EXEMPT 계산을 폴백(||, 로컬값 있으면 그것만/없으면 conf 기본값만)에서 병합(로컬값 + conf 기본값을 항상 둘 다 포함)으로 변경. git config --get-all이 값 없을 때 exit 1을 내는데, set -eu 하의 서브셸에서 여러 명령을 순차 실행할 때 첫 명령 실패가 서브셸 자체를 조기 종료시켜 둘째 명령이 안 돌 수 있어 || true로 보호. 실제 재현(격리 저장소에서 --add 전엔 main 통과, --add 후엔 동일 main이 거부되는 자기모순 확인) 후 수정, 재현 시나리오 그대로 재검증(add 후에도 main 통과 + 추가한 hotfix/* 도 통과 + 관계없는 브랜치는 여전히 거부). tests/robustness-commit-msg.bats에 3개 케이스 추가, 네거티브 케이스(수정 되돌려서 테스트가 실패하는지 확인 후 복원)로 실제 회귀 감지 검증. bats 87/87, shellcheck 전체 통과.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
README가 안내하는 git config --add gitformat.branchExempt 사용법을 그대로 따르면 main/master/develop/release/*조차 예외 브랜치에서 빠져 커밋이 거부되던 버그를 고쳤다. 로컬 오버라이드와 내장 기본값을 합치도록(union) 변경, 실제 재현/수정/재검증 완료.
<!-- SECTION:FINAL_SUMMARY:END -->
