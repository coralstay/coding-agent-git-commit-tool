---
id: GF-12
title: (opt-in) GitHub Actions 백스톱 워크플로
status: Done
assignee: []
created_date: '2026-08-24 03:12'
updated_date: '2026-08-24 03:53'
labels: []
dependencies:
  - GF-10
type: task
ordinal: 12000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
push 단계 --no-verify 우회에 대한 서버사이드 백스톱, 브랜치 보호 필수 status check용 재사용 워크플로(decision-3)
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
.github/workflows/verify.yml(workflow_call 재사용 워크플로): 컨슈머 저장소+git-format을 함께 체크아웃해 PR 범위 커밋 전체에 hooks/commit-msg, 작업트리에 hooks/pre-commit·pre-push를 그대로 실행 — 로컬과 동일 로직 재사용. docs/examples/github-actions-caller.yml로 호출 예시 제공, README에 브랜치 보호 필수 status check 지정 필요성 안내. PyYAML로 두 워크플로 파일 문법 유효성 검증(실제 Actions 러너 실행은 미검증, README에도 명시).
<!-- SECTION:FINAL_SUMMARY:END -->
