---
id: GF-93
title: '종합 리뷰 리포트 자동화: /review-full 슬래시 커맨드 + 주간 GitHub Actions'
status: Done
assignee: []
created_date: '2026-09-03 23:02'
updated_date: '2026-09-03 23:07'
labels: []
dependencies: []
ordinal: 90000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
이번 세션에서 만든 종합 리뷰 리포트(기능/비기능/아키텍처/데이터흐름/decision 계보/테스트커버리지/발견사항/권고 구조)를 반복 생성할 수 있게 만든다. (1) 대화형 세션에서 원할 때 바로 실행하는 /review-full 슬래시 커맨드(.claude/commands/, 이 저장소 .gitignore의 .claude/ 규칙에 따라 로컬 전용/gitignore 대상 - 저장소에 커밋되지 않는 개인 도구). (2) 매주 자동으로 같은 리뷰를 생성해 저장소에 Markdown으로 커밋하는 GitHub Actions 워크플로(anthropics/claude-code-action 사용, ANTHROPIC_API_KEY 시크릿 필요 - 시크릿 등록은 GitHub 웹 UI에서 사용자가 직접 해야 하며 이 태스크 범위 밖).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 .claude/commands/review-full.md가 생성되어, 이번 세션 결과물과 동일한 9개 섹션 구조(개요/기능상세/비기능요구사항/아키텍처/데이터흐름/decision역사/테스트커버리지/발견사항/권고사항)로 코드베이스를 다시 읽고 HTML Artifact로 발행하는 절차를 담는다
- [x] #2 .github/workflows/weekly-review.yml이 생성되어 매주 1회 cron으로 트리거되고(+ workflow_dispatch로 수동 실행도 가능), anthropics/claude-code-action으로 동일한 리뷰를 생성해 docs/reviews/weekly-<날짜>.md로 커밋한다
- [x] #3 워크플로 파일 자체 또는 README에 ANTHROPIC_API_KEY 시크릿을 어디서 어떻게 등록해야 하는지 안내가 있다
- [x] #4 기존 shellcheck/bats 검증에 회귀가 없다(새로 추가되는 파일은 POSIX sh 대상이 아니므로 영향 없음을 확인)
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
이번 세션에서 만든 종합 리뷰 리포트를 반복 생성할 수 있게 두 가지를 만들었다. (1) .claude/commands/review-full.md - 대화형 세션에서 /review-full로 실행하면 저장소 전체를 다시 읽어 9개 섹션 구조로 리포트를 작성하고, 매번 새 Artifact를 만들지 않고 이번에 발행한 기존 Artifact(https://claude.ai/code/artifact/34f4da7c-60f7-42e4-bbdd-3f0b2ce89acf)를 갱신하도록 URL을 명시해뒀다. .gitignore의 .claude/ 규칙에 따라 저장소에는 커밋되지 않는 로컬 전용 도구다. (2) .github/workflows/weekly-review.yml - 매주 월요일 00:00 UTC cron(+ workflow_dispatch 수동 실행)으로 anthropics/claude-code-action을 실행해 같은 9개 섹션 구조의 리뷰를 생성하고 docs/reviews/weekly-<날짜>.md로 커밋한다. 무인 실행에서는 claude.ai Artifact를 발행할 수 없어(대화형 세션 전용 기능) Markdown 파일 커밋 방식을 택했다. ANTHROPIC_API_KEY 시크릿 설정 방법을 워크플로 상단 주석과 docs/reviews/README.md에 안내했고, GitHub Actions schedule 트리거가 60일 비활성 시 자동 비활성화되는 알려진 제약도 함께 문서화했다. README.md/README.en.md의 저장소 구조 트리에 docs/reviews/, weekly-review.yml을 반영했다. 검증: shellcheck -s sh 전체 통과, bats tests/ 전체 94개 통과(회귀 없음 - 새 파일들은 POSIX sh 대상이 아님), .github/workflows/weekly-review.yml의 YAML 문법을 python yaml로 파싱 확인.
<!-- SECTION:FINAL_SUMMARY:END -->
