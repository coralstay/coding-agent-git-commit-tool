---
id: GF-21
title: bats-core 테스트 하네스 구축 + shellcheck CI 편입
status: Done
assignee: []
created_date: '2026-08-24 04:48'
updated_date: '2026-08-24 07:48'
labels: []
dependencies: []
type: task
ordinal: 21000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
brew로 bats-core 설치, tests/ 디렉터리 구조 구축(hooks별 .bats 파일), self-verify.yml에 bats 실행과 shellcheck 정적분석 스텝 추가. hooks/commit-msg의 SC2254 경고는 의도된 글롭 매칭이라 인라인 disable 처리(decision-7)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 bats tests/ 로 최소 1개 이상의 smoke 테스트가 통과한다
- [x] #2 shellcheck -s sh로 hooks/ 전체 검사 시 경고 0건(문서화된 예외 제외)
- [x] #3 CI(self-verify.yml)에서 bats+shellcheck가 실행된다
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
tests/helpers/git-format.bash + tests/smoke.bats(3 케이스, 전부 통과) 추가. hooks/commit-msg SC2254 인라인 disable로 shellcheck 경고 0건. .github/workflows/test.yml 신설(shellcheck+bats, 컨슈머용 verify.yml과 분리).
<!-- SECTION:FINAL_SUMMARY:END -->
