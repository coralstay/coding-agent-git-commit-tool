---
id: GF-28
title: GitHub Actions 워크플로 견고성 (오류추정)
status: Done
assignee: []
created_date: '2026-08-24 04:48'
updated_date: '2026-08-27 09:06'
labels: []
dependencies:
  - GF-21
type: task
ordinal: 28000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
얕은 클론(fetch-depth 기본값)일 때 PR 커밋 범위 검증이 어떻게 동작하는지, 권한 최소화 검토
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 fetch-depth를 지정 안 한 캐ller 워크플로에서도 verify.yml이 명확하게 실패하거나 우회하는지(현재 fetch-depth:0 전제라 미지정 시 동작 확인 필요)
- [x] #2 GITHUB_TOKEN 권한이 최소한(contents:read 등)으로 충분한지 점검
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
AC1: 로컬 실행(bats/act) 대신 실제 GH Actions 실행 로그를 증거로 삼음 — self-verify.yml(caller, fetch-depth 미지정)이 트리거한 verify.yml 실행(https://github.com/coralstay/git-format/actions/runs/32730711526, PR #2, GF-32 검증, 2026-08-24, 결과 success)의 'Checkout repository' 스텝이 fetch-depth:0으로 실행됐고, 'Conventional Commits 형식 검증' 스텝의 git rev-list BASE..HEAD가 커밋 5개를 정상 순회함을 로그로 직접 확인. verify.yml 자신의 체크아웃이 fetch-depth:0으로 고정돼 있어 caller가 fetch-depth를 지정하든 안 하든 영향이 없음이 실측으로 확인됨 — 코드 수정 불필요.
AC2: verify.yml/test.yml/self-verify.yml/docs/examples/github-actions-caller.yml 4개 파일 모두에 permissions: contents: read를 워크플로 레벨로 추가(기존엔 permissions 블록 자체가 없어 저장소 기본 권한을 그대로 상속했음). 4개 파일 모두 python3 yaml.safe_load로 파싱 검증 통과.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
AC1은 실제 GH Actions 실행 로그(PR #2, run 32730711526)로 caller의 fetch-depth 미지정이 verify.yml의 하드코딩된 fetch-depth:0에 영향 없음을 실측 확인(코드 변경 없음). AC2는 4개 워크플로/예시 파일에 permissions: contents: read를 명시적으로 추가해 권한을 최소화(YAML 파싱 검증 통과).
<!-- SECTION:FINAL_SUMMARY:END -->
