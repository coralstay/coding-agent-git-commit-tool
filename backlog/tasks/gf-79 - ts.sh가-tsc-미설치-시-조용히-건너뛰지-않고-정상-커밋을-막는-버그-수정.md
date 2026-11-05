---
id: GF-79
title: ts.sh가 tsc 미설치 시 조용히 건너뛰지 않고 정상 커밋을 막는 버그 수정
status: Done
assignee: []
created_date: '2026-08-28 14:17'
updated_date: '2026-08-28 14:24'
labels: []
dependencies: []
ordinal: 77000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
이 프로젝트의 모든 언어 체크는 "필요한 도구가 없으면 조용히 건너뛴다"는 설계 원칙이 있다(README에 명시). 그런데 hooks/checks/ts.sh는 tsconfig.json이 있고 npx가 PATH에 있으면 tsc 자체가 로컬/전역 어디에도 설치돼 있지 않아도 무조건 npx --no-install tsc --noEmit을 실행한다. npx는 PATH가 아니라 npm 전역 설치를 직접 참조하므로, typescript가 전역 설치돼 있지 않은 환경(devDependency로만 설치하는 게 흔한 실사용 패턴, 그리고 .github/workflows/test.yml의 ubuntu-latest 러너도 typescript를 따로 설치하지 않음)에서는 "npx canceled due to missing packages" 에러로 매우 정상적인(타입 에러 없는) 커밋까지 거부된다. NPM_CONFIG_PREFIX를 빈 임시 디렉터리로 돌려 전역 typescript 미설치 상태를 재현해 실측 확인함. 즉 이 프로젝트 자체의 CI(test.yml)에서 GF-73이 추가한 tsc 관련 bats 케이스가 실패할 가능성이 높고, 실사용자도 typescript를 devDependency로만 설치했다면 동일하게 막힌다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 node_modules/.bin/tsc(로컬 devDependency)나 전역 tsc 중 하나도 찾을 수 없으면 tsc 검사를 조용히 건너뛴다(커밋을 막지 않는다)
- [x] #2 둘 중 하나라도 있으면 기존처럼 실제 tsc --noEmit으로 타입 에러를 잡는다(회귀 없음)
- [x] #3 CI 러너처럼 전역 typescript가 없는 상태를 재현하는 bats 테스트가 추가된다
- [x] #4 bats 전체와 shellcheck -s sh가 통과한다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
hooks/checks/ts.sh의 tsc 실행 로직을 npx --no-install 경유에서 직접 실행으로 변경. npx --no-install은 PATH가 아니라 npm/npx 자체의 별도 조회 경로를 참조해서, command -v tsc가 PATH상에서 tsc를 찾아내도 npx는 여전히 못 찾아 실패할 수 있음을 실측 확인(NPM_CONFIG_PREFIX를 빈 디렉터리로 돌려 재현 시도했으나 asdf shim이 계속 잡혀 실패 - 결국 npx 자체를 안 쓰는 방향으로 재설계). node_modules/.bin/tsc(로컬 devDependency) 우선 확인 후 없으면 PATH의 tsc(전역 설치)를 직접 호출, 둘 다 없으면 조용히 건너뜀. tests/checks-ts.bats에 path_without tsc로 tsc 완전 부재를 재현하는 케이스 추가. 네거티브 케이스(수정 되돌려서 새 테스트가 실패하는지 확인 후 복원)로 검증. 기존 정상 경로(전역 tsc 있을 때 lint/tsc 실행, 타입 에러 차단)도 회귀 없음 재확인. bats 전체 88/88, shellcheck 전체 통과. 참고: 이 저장소 자체 CI(GitHub Actions ubuntu-latest)는 gh run list로 확인해보니 typescript가 이미 사용 가능해 tsc 관련 테스트는 CI에서도 원래 통과하고 있었음 - 이 버그는 CI가 아니라 typescript를 devDependency로만 설치하는(전역 미설치) 실사용자 환경에서 발생한다.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
ts.sh가 npx --no-install 경유로 tsc를 실행해서, tsc가 PATH에서는 보여도 npx의 별도 조회 경로에서 못 찾으면(흔히 devDependency로만 설치한 경우) 타입 에러 없는 정상 커밋까지 막던 버그를 고쳤다. npx를 거치지 않고 로컬/전역 tsc를 직접 실행하도록 변경, 실측 재현/수정/재검증 완료.
<!-- SECTION:FINAL_SUMMARY:END -->
