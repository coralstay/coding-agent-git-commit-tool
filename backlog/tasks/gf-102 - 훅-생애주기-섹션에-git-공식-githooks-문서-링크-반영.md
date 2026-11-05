---
id: GF-102
title: 훅 생애주기 섹션에 git 공식 githooks 문서 링크 반영
status: Done
assignee: []
created_date: '2026-09-19 13:06'
updated_date: '2026-09-19 14:32'
labels: []
dependencies: []
type: docs
ordinal: 99000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
사용자가 README의 "훅 생애주기" 섹션이 git 공식 문서(githooks)를 근거로 삼고, 그 문서 주소를 README에 직접 삽입하라고 요청했다.

공식 문서(https://git-scm.com/docs/githooks) 확인 결과, git-format README가 이미 서술한 내용(pre-commit/commit-msg는 --no-verify로 건너뛰지만 post-commit은 항상 실행되고 exit code가 커밋 결과에 영향을 주지 못한다는 것, commit-msg는 커밋 메시지 파일 경로 하나를 인자로 받는다는 것)이 공식 문서와 정확히 일치함을 확인했다 - 내용 수정은 필요 없고, 근거 링크만 삽입하면 된다.

"훅 생애주기" 섹션 상단에 공식 문서 링크를 추가하고, post-commit이 --no-verify로도 건너뛸 수 없다는 핵심 주장(decision-3의 근거) 옆에도 같은 링크를 인용으로 붙인다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 README.md의 "훅 생애주기" 섹션에 https://git-scm.com/docs/githooks 링크가 최소 1곳 이상 삽입된다
- [x] #2 post-commit이 --no-verify로 건너뛸 수 없고 실행이 보장된다는 문장 옆에 공식 문서 인용이 붙는다
- [x] #3 기존 섹션 내용(핵심 두 문장, 훅 순서, AI 귀속 표)은 변경되지 않는다 - 링크만 추가
- [x] #4 shellcheck -s sh 전체와 bats tests/ 전체가 통과한다
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
훅 생애주기 섹션 상단에 githooks 공식문서 링크 추가, post-commit 항상 실행 문장 옆에 같은 링크 인용 추가. 내용 자체는 이미 공식문서와 일치하므로 수정 없음.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
검증: (1) grep git-scm.com/docs/githooks README.md -> 2건(섹션 상단 + post-commit 설명). (2) post-commit 문장 옆에 공식 문서 인용 확인. (3) diff로 핵심 두 문장/훅 순서/AI귀속 표는 변경 없음, 링크 2줄만 추가됨을 확인. (4) shellcheck -s sh 전체 clean, bats tests/ 103/103 통과. 공식문서(https://git-scm.com/docs/githooks) WebFetch로 직접 대조해 pre-commit/commit-msg는 --no-verify로 스킵되지만 post-commit은 항상 실행되고 exit code가 결과에 영향 없다는 기존 서술이 정확함을 재확인.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
README "훅 생애주기" 섹션에 git 공식 githooks 문서(https://git-scm.com/docs/githooks) 링크를 두 곳(섹션 상단, post-commit 항상 실행 설명 옆)에 추가했다. 공식 문서를 직접 대조해 기존 서술(pre-commit/commit-msg는 --no-verify로 건너뛰지만 post-commit은 항상 실행되고 exit code가 커밋 결과에 영향을 못 준다)이 정확함을 확인했으므로 내용 자체는 바꾸지 않고 근거 링크만 추가했다.

검증: shellcheck -s sh 전체 clean, bats tests/ 103/103 통과.
<!-- SECTION:FINAL_SUMMARY:END -->
