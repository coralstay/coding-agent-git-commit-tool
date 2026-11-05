---
id: GF-57
title: hooks 포맷 정리 전체 검증 + decision 기록
status: Done
assignee: []
created_date: '2026-08-27 14:41'
updated_date: '2026-08-27 20:02'
labels: []
dependencies:
  - GF-51
  - GF-52
  - GF-53
  - GF-54
  - GF-55
  - GF-56
ordinal: 55000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GF-51~56(hooks/install.sh/checks 포맷 정리) 완료 후 전체 bats+shellcheck 재검증. decision 문서로 'hooks는 POSIX sh 유지, 포맷/네이밍 관례만 참고해 적용, 문법은 POSIX만 사용' 정책을 기록한다(외부 문서 URL은 인용하지 않음).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 bats tests/ 전체가 통과한다
- [x] #2 shellcheck -s sh hooks/commit-msg hooks/pre-commit hooks/pre-push hooks/post-commit hooks/checks/*.sh install.sh 가 경고 없이 통과한다
- [x] #3 decision 문서가 생성되어 이번 정책이 기록된다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
GF-51~56(commit-msg/pre-commit/pre-push/post-commit/checks 5개/install.sh) 완료 후 bats tests/ 전체 60/60 통과, shellcheck -s sh 전체 파일 경고 0건 확인. decision-9 작성 완료(외부 문서 URL 인용 없이 정책만 서술).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/install.sh/checks 포맷 정리(GF-51~56) 통합 검증 완료 - bats 60/60, shellcheck 0건. decision-9로 'POSIX 문법 유지 + 표기 관례만 참고' 정책을 기록.
<!-- SECTION:FINAL_SUMMARY:END -->
