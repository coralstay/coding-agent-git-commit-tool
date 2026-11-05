---
id: GF-92
title: >-
  GF-86 잔여 정리: test.yml shellcheck 커맨드 + install.sh sync_template 심볼릭 링크 정리 누락
  수정
status: Done
assignee: []
created_date: '2026-09-03 23:02'
updated_date: '2026-09-04 03:31'
labels: []
dependencies: []
references:
  - decision-12
ordinal: 89000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GF-86(decision-12)에서 hooks/pre-push를 완전히 삭제했지만 두 곳이 따라가지 못해 깨진 상태로 남아있다. (1) .github/workflows/test.yml의 static-analysis 잡 ShellCheck 스텝이 존재하지 않는 hooks/pre-push를 인자로 넘겨 로컬 재현 시 exit 2로 실패한다. (2) install.sh의 sync_template()은 hooks/*에 현재 존재하는 파일에 대해서만 심볼릭 링크를 만들고, hooks/에서 삭제된 파일에 대응하는 template/hooks/의 예전 심볼릭 링크는 정리하지 않는다 - 실측으로 이 저장소 자신의 template/hooks/pre-push가 지금 대상 없는 깨진 심볼릭 링크로 남아있다. install.sh --global을 이미 실행해둔 컨슈머가 업데이트해도 문제가 남는다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 test.yml의 ShellCheck 스텝 커맨드에서 hooks/pre-push 토큰을 제거하고, 그 커맨드를 로컬에서 재실행하면 exit 0이 된다 (파일 내 다른 pre-push 언급도 점검해 실제와 다르면 갱신)
- [x] #2 install.sh의 sync_template()이 실행되면 template/hooks/ 안에서 hooks/에 더 이상 대응 파일이 없는 심볼릭 링크(예: template/hooks/pre-push)를 삭제한다 (POSIX sh, decision-9 준수: 배열/local/[[ ]]/=~ 금지)
- [x] #3 tests/robustness-install.bats에 격리된 GITFORMAT_ROOT 사본에서 hooks/ 파일 하나를 삭제 후 install.sh --global을 재실행하면 template/hooks/의 대응 심볼릭 링크도 삭제되는지 검증하는 케이스가 추가된다
- [x] #4 shellcheck -s sh hooks/commit-msg hooks/pre-commit hooks/post-commit hooks/checks/*.sh install.sh 통과 및 bats tests/ 전체(기존 94개+신규) 통과
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
test.yml ShellCheck 커맨드에서 hooks/pre-push 토큰 제거 (AC1) - shellcheck exit 0 확인, 커밋 2adb908. install.sh sync_template()에 template/hooks/의 대상 없는 심볼릭 링크 정리 루프 추가 (AC2) - POSIX sh(배열/local/[[ ]] 미사용). tests/robustness-install.bats에 격리된 FAKE_ROOT 사본 기반 정리 테스트 추가 (AC3) - 개별 실행 통과 확인. 전체 bats tests/ 실행 중(백그라운드).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
GF-86에서 hooks/pre-push 삭제 후 반영이 안 됐던 두 곳을 고쳤다. (1) .github/workflows/test.yml의 shellcheck 스텝에서 hooks/pre-push 토큰 제거 - 로컬 재현으로 exit 2 -> exit 0 확인. (2) install.sh의 sync_template()에 정리 루프 추가 - template/hooks/의 심볼릭 링크 중 hooks/에 대응 파일이 없는 것을 삭제한다(POSIX sh, decision-9 준수). tests/robustness-install.bats에 격리된 사본 기반 검증 케이스 추가(훅 파일 삭제 후 --global 재실행 시 대응 심볼릭 링크만 정확히 사라지고 나머지는 유지되는지). 검증: shellcheck -s sh 전체 통과, bats tests/ 전체 95개 통과(기존 94 + 신규 1).
<!-- SECTION:FINAL_SUMMARY:END -->
