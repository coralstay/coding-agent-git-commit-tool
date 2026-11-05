---
id: GF-85
title: >-
  서버사이드 검증 GitHub Actions(verify.yml/self-verify.yml/caller 예시) 제거 - 클라이언트측 전용으로
  범위 축소
status: Done
assignee: []
created_date: '2026-09-03 06:55'
updated_date: '2026-09-03 07:01'
labels: []
dependencies: []
references:
  - >-
    backlog/decisions/decision-3 -
    post-commit-트레일러로-no-verify-우회-탐지-push는-한계-서버사이드-백스톱-필요.md
documentation:
  - README.md
  - README.en.md
  - install.sh
ordinal: 83000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
사용자 결정: git-format은 클라이언트측 git 훅 프로그래밍만 다루고, 서버사이드/CI 기반 검증(push 단계 백스톱)은 이 프로젝트 범위 밖이다 - 필요하면 별도 프로젝트에서 다룬다. 컨슈머 대상 서버사이드 검증 제품인 .github/workflows/verify.yml, 그걸 dogfooding하는 self-verify.yml, 컨슈머가 복사해 쓰는 docs/examples/github-actions-caller.yml을 제거한다. 이 저장소 자체의 개발용 CI인 .github/workflows/test.yml(shellcheck+bats)은 '컨슈머에게 제공하는 서버사이드 검증 제품'이 아니라 이 프로젝트 자신의 코드 품질 게이트이므로 남긴다. decision-3의 5번 항목(git-format이 opt-in 재사용 워크플로를 제공한다는 부분)만 대체하는 새 decision을 기록한다 - decision-3의 나머지(Verify-Bypassed 트레일러 메커니즘)는 그대로 유효하다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 .github/workflows/verify.yml, .github/workflows/self-verify.yml, docs/examples/github-actions-caller.yml이 삭제된다
- [x] #2 .github/workflows/test.yml은 그대로 남고 정상 동작한다(shellcheck -s sh + bats tests/ 통과)
- [x] #3 README.md/README.en.md에서 opt-in GitHub Actions 백스톱 섹션, 저장소 구조 트리의 verify.yml/self-verify.yml/docs/examples 언급, 한계 섹션의 관련 문구가 실제 상태와 일치하도록 갱신된다
- [x] #4 install.sh가 출력하는 안내 메시지가 더 이상 존재하지 않는 docs/examples/github-actions-caller.yml을 가리키지 않는다
- [x] #5 decision-3의 5번 항목(서버사이드 백스톱을 git-format이 제공한다는 부분)만 대체하는 새 decision이 기록되고, decision-3 파일 자체와 decision-3의 나머지 항목은 수정하지 않는다
- [x] #6 삭제 후에도 tests/ 전체 bats 스위트와 shellcheck -s sh가 통과한다
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
verify.yml/self-verify.yml/docs/examples/github-actions-caller.yml을 삭제해 서버사이드 검증(컨슈머 대상)을 이 프로젝트 범위에서 제외했다. .github/workflows/test.yml(이 저장소 자신의 dev CI)은 컨슈머 제품이 아니므로 남겼다. decision-11을 생성해 decision-3의 5번 항목(git-format이 opt-in 재사용 워크플로를 제공한다는 부분)만 대체했다 - decision-3의 1~4번(Verify-Bypassed 트레일러 메커니즘)과 파일 자체는 미수정. README.md/README.en.md의 관련 섹션·저장소 구조 트리·한계 섹션, install.sh의 안내 메시지를 실제 상태에 맞게 갱신했다. 검증: 삭제/변경 후 bats tests/ 전체 통과(exit 0), shellcheck -s sh 전부 통과(exit 0) - 사전에 grep으로 확인한 대로 어느 테스트도 삭제된 파일을 참조하지 않았다.
<!-- SECTION:FINAL_SUMMARY:END -->
