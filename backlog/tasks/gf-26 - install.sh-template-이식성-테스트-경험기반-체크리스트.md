---
id: GF-26
title: install.sh/template 이식성 테스트 (경험기반 체크리스트)
status: Done
assignee: []
created_date: '2026-08-24 04:48'
updated_date: '2026-08-27 09:00'
labels: []
dependencies:
  - GF-21
type: task
ordinal: 26000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
비대화형/대화형 환경, --global 반복 실행 멱등성, GNU/BSD 도구 차이를 커버
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 비대화형(파이프)에서 프롬프트 없이 안전하게 기본 동작하는지
- [x] #2 --global을 여러 번 실행해도 template/hooks 심볼릭 링크가 깨지지 않는지(멱등성)
- [x] #3 존재하지 않는 대상 디렉터리, git 저장소가 아닌 디렉터리 등 잘못된 인자에 대한 에러 메시지가 명확한지
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. tests/robustness-install.bats 신규 작성
2. 비대화형: stdin을 /dev/null로 리다이렉트하고 install.sh를 인자 없이 실행 -> 프롬프트 없이 전역 설정 건너뛰고 로컬 설정만 적용
3. 멱등성: 격리된 HOME에서 install.sh --global을 두 번 연속 실행해도 template/hooks 심볼릭 링크가 정상 상태 유지
4. 에러 메시지: 존재하지 않는 대상 디렉터리, git 저장소가 아닌 디렉터리를 인자로 줬을 때 0이 아닌 종료 + 명확한 stderr 메시지
5. bats tests/robustness-install.bats 실행 후 acceptance criteria 체크
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
tests/robustness-install.bats 신규 작성, bats 로컬 실행 4/4 통과. 비대화형 1건, --global 멱등성 1건(격리 HOME, 실제 전역 설정 미접촉 확인), 에러 처리 2건(존재하지 않는 대상/비-git 디렉터리). 부가 확인: install.sh/hooks/checks/*.sh에 readlink -f, sed -i, stat -c/-f 등 GNU 전용 플래그 없음(grep으로 확인) — GNU/BSD 차이로 깨질 지점 없음.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
install.sh의 비대화형 동작, --global 반복 실행 멱등성, 잘못된 인자 에러 처리를 경험기반 체크리스트로 커버하는 bats 테스트 4건 작성. tests/robustness-install.bats, 로컬 bats 실행 4/4 통과로 검증. 모든 테스트는 격리된 HOME을 사용해 실제 전역 git 설정을 건드리지 않음을 확인.
<!-- SECTION:FINAL_SUMMARY:END -->
