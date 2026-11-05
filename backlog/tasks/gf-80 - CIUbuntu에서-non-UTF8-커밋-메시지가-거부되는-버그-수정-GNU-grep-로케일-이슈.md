---
id: GF-80
title: CI(Ubuntu)에서 non-UTF8 커밋 메시지가 거부되는 버그 수정 - GNU grep 로케일 이슈
status: Done
assignee: []
created_date: '2026-08-28 14:23'
updated_date: '2026-08-28 14:31'
labels: []
dependencies: []
ordinal: 78000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
gh run list로 확인한 결과 이 저장소의 test.yml CI가 GF-28(2026-08-27) 이후 커밋 전부에서 계속 실패 중이었다(macOS 로컬 bats는 항상 통과해서 아무도 눈치채지 못함). 실패 원인: tests/robustness-injection.bats의 "non-UTF8 바이트가 섞여도 트레일러 삽입이 깨지지 않는다" 테스트가 Ubuntu 러너에서 실패. hooks/commit-msg가 커밋 메시지 원문(SUBJECT_LINE)에 grep -qE/-v를 로케일 지정 없이 실행하는데, GNU grep(Linux)은 UTF-8 로케일에서 잘못된 멀티바이트 시퀀스를 만나면 매칭에 실패해 정상적인 type(예: feat:)이 붙은 메시지도 "형식이 아닙니다"로 거부한다. macOS의 BSD grep은 이런 경우에 관대해서 로컬에서는 재현되지 않았다(LC_ALL=C로도 로컬에서 재현 안 됨 - BSD/GNU grep 구현 차이). Docker/Linux 환경이 로컬에 없어 실제 GNU grep 동작을 직접 재현하지 못했고, 이 문제는 커밋 메시지/브랜치명 원문을 grep으로 처리하는 모든 지점에 잠재한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 commit-msg/post-commit에서 커밋 메시지 원문·브랜치명을 처리하는 grep 호출이 로케일에 의존하지 않도록(LC_ALL=C) 고정된다
- [x] #2 수정 후 실제 GitHub Actions CI(gh run list)에서 test 워크플로가 성공한다 - 로컬에 Linux 환경이 없어 이것이 유일한 실측 검증 수단이다
- [x] #3 기존 bats 테스트(로컬 macOS)가 회귀 없이 통과한다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
commit-msg/post-commit 상단(set -eu 직후)에 export LC_ALL=C 추가. GNU grep(Linux)이 UTF-8 로케일에서 잘못된 멀티바이트 시퀀스를 만나면 매칭에 실패하는 문제를, type 목록/정규식이 전부 ASCII라 바이트 단위(C 로케일) 매칭으로도 의미가 같다는 점을 이용해 로케일 자체를 고정하는 방식으로 해결. Docker/Linux가 로컬에 없어 실제 GNU grep 동작을 직접 재현하지 못했다 - gh run list/gh run view로 GF-28(2026-08-27)부터 현재까지 CI의 test 워크플로가 전부 동일한 테스트(non-UTF8 트레일러) 하나로만 실패하고 있었음을 먼저 확인해 문제를 정확히 좁혔다. 로컬 macOS bats 88/88 회귀 없음, shellcheck 통과. AC #2(CI 실제 성공)는 푸시 후 gh run list/view로 확인 예정.

푸시 후 gh run view 33180258469으로 실제 CI 확인: bats 3m38s 성공, static-analysis 7s 성공. GF-28(2026-08-27) 이후 처음으로 test 워크플로 전체 성공.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/commit-msg·post-commit 상단에 export LC_ALL=C를 추가해, GNU grep(Linux)이 UTF-8 로케일에서 잘못된 멀티바이트 시퀀스를 만나면 매칭에 실패하던 문제를 고쳤다. GF-28부터 계속 실패하던 실제 GitHub Actions CI가 이 수정으로 다시 통과함을 gh run view로 확인했다.
<!-- SECTION:FINAL_SUMMARY:END -->
