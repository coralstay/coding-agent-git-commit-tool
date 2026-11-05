---
id: GF-73
title: checks-ts.bats 신설 (ts.sh 테스트 커버리지 공백)
status: Done
assignee: []
created_date: '2026-08-28 04:59'
updated_date: '2026-08-28 09:11'
labels: []
dependencies: []
ordinal: 71000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
hooks/checks/ts.sh(TypeScript/JavaScript 체크)만 다른 언어(cpp/java/python/sql)와 달리 전용 테스트 파일이 없다. tests/robustness-dispatch.bats가 package.json 감지/오류추정 케이스를 간접적으로만 다루고, ts.sh 자체의 핵심 로직(npm run lint 성공/실패, lint 스크립트 없을 때 건너뜀, npm 없을 때 건너뜀, tsconfig.json+npx tsc --noEmit 실행)은 어디서도 직접 검증되지 않는다. 다른 checks-*.bats와 같은 패턴으로 tests/checks-ts.bats를 신설한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 lint 스크립트 성공/실패, lint 스크립트 없음, npm 없음, tsconfig.json+tsc 실행 케이스를 다루는 tests/checks-ts.bats가 추가된다
- [x] #2 가능한 한 실제 도구(npm, tsc)로 검증한다(GF-22 실도구 재검증 원칙과 동일)
- [x] #3 전체 bats 스위트가 통과하고 shellcheck -s sh 경고가 없다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
tests/checks-ts.bats 신설, 6개 케이스(lint 성공/실패, lint 스크립트 없음, npm 없음, tsc 통과, tsc 타입에러 차단). npm run lint는 eslint 등 설치 없이 package.json 스크립트 자체(exit 0/1)로 검증, tsc는 로컬에 실제 설치된 버전으로 검증(GF-22 원칙과 동일). 디버깅 중 로컬 asdf 버전매니저가 격리된 임시 디렉터리에서 node/tsc 버전을 못 찾는 이슈를 발견 - ts.sh 버그가 아니라 로컬 환경 이슈라 테스트 setup()에서만 ASDF_NODEJS_VERSION을 지정해 해결(asdf 없는 환경에서는 조건부로 무시됨). bats 전체 75/75 통과, shellcheck 전체 통과.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
ts.sh 전용 테스트 파일이 없던 공백을 tests/checks-ts.bats(6개 케이스)로 메웠다. 실제 npm/tsc로 검증. 로컬 asdf 환경 이슈도 함께 발견/해결.
<!-- SECTION:FINAL_SUMMARY:END -->
