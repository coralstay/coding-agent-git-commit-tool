---
id: GF-39
title: package.json 스크립트 존재 확인이 grep이라 scripts 밖의 동명 키와 혼동됨
status: Done
assignee: []
created_date: '2026-08-24 08:13'
updated_date: '2026-08-24 12:51'
labels: []
dependencies: []
type: bug
ordinal: 39000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
grep -q 패턴은 scripts 객체 밖에 있는 동명의 키(예: devDependencies의 'test'라는 패키지명)도 매치해 npm run이 실제로 없는 스크립트를 실행하려다 실패한다. node -e로 실제 scripts 객체를 확인해야 함.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
ts.sh/pre-push의 grep 기반 스크립트 존재 확인을 node -e 기반 has_npm_script()로 교체(scripts 객체만 정확히 확인). devDependencies 동명키 오탐 방지 + 실제 스크립트 정상실행 재검증(로컬 asdf nodejs 핀 깨짐 발견, ASDF_NODEJS_VERSION=lts로 우회해 검증).
<!-- SECTION:FINAL_SUMMARY:END -->
