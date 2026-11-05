---
id: GF-65
title: install.sh가 C/C++ 프로젝트의 .gitignore에 .gitformat-build 자동 반영 검토
status: Done
assignee: []
created_date: '2026-08-27 20:29'
updated_date: '2026-08-27 21:10'
labels: []
dependencies: []
ordinal: 63000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
현재 README 주의점에 '.gitformat-build/는 커밋하지 말고 컨슈머가 직접 .gitignore에 추가하라'고만 안내돼 있어 수동이다. install.sh가 대상 저장소에 CMakeLists.txt/Makefile이 있을 때 .gitignore에 .gitformat-build/ 항목이 없으면 자동으로 추가(또는 추가할지 물어보는)할지 검토하고, 하기로 하면 구현한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 .gitformat-build 자동 처리 여부와 방식(자동 추가/대화형 확인/미실시)이 결정되고 근거가 기록된다
- [x] #2 구현하기로 했다면 install.sh 변경 후 tests/robustness-install.bats에 해당 케이스가 추가되고 통과한다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
결정: 자동 추가(대화형 확인 없이) - 이미 추적 중인 .gitignore에 한 줄 추가하는 것뿐이라 리스크가 낮고, 되돌리기도 쉬워서 --global 설정처럼 물어볼 필요는 없다고 판단. install.sh가 gitformat.conf의 marker.cpp/marker.cppMake/buildDir 값을 읽어(하드코딩 대신 기존 값 재사용) CMakeLists.txt/Makefile이 있으면 .gitignore에 .gitformat-build/를 추가(이미 있으면 건너뜀, 멱등적). tests/robustness-install.bats에 케이스 4개 추가(자동추가/Makefile만 있어도 동작/중복방지/마커 없으면 미동작). bats 전체 67/67 통과, shellcheck 통과.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
install.sh가 C/C++ 프로젝트에 .gitformat-build/를 .gitignore에 자동 추가하도록 구현(대화형 확인 없이 자동, 저위험 판단). gitformat.conf의 기존 마커 값을 재사용해 일관성 유지. bats 4건 추가, 전체 67/67 통과.
<!-- SECTION:FINAL_SUMMARY:END -->
