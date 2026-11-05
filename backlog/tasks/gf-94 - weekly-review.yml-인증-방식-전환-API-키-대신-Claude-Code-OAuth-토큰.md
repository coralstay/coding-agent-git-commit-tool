---
id: GF-94
title: 종합 리뷰 GitHub Actions 자동화 제거 - weekly-review.yml 및 관련 문서 삭제
status: Done
assignee: []
created_date: '2026-09-04 04:08'
updated_date: '2026-09-04 04:13'
labels: []
dependencies: []
ordinal: 91000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
인증 방식(API 키 vs OAuth 토큰) 트레이드오프와 시크릿 유출 보안 리스크를 논의한 뒤, 사용자가 무인 CI 자동화 자체를 하지 않기로 결정했다. GF-93에서 추가한 .github/workflows/weekly-review.yml(및 이를 지원하던 docs/reviews/, README 언급)을 전부 제거한다. 대화형 세션용 /review-full 슬래시 커맨드(.claude/commands/, gitignore 대상이라 원래도 저장소에 없음)는 유지 - 시크릿을 저장소에 등록할 필요가 없고 보안 우려도 없기 때문.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 .github/workflows/weekly-review.yml이 삭제된다
- [x] #2 docs/reviews/ 디렉터리(README.md 포함)가 삭제된다
- [x] #3 README.md/README.en.md의 저장소 구조 트리에서 docs/reviews/, weekly-review.yml 언급이 제거되고 실제 상태와 일치한다
- [x] #4 .github/workflows/test.yml(기존 dev CI)과 .claude/commands/review-full.md(대화형 슬래시 커맨드)는 그대로 유지된다
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
인증 방식(API 키 vs OAuth 토큰)과 시크릿 유출 보안 리스크를 논의하던 중, 무인 CI 자동화 자체를 하지 않기로 결정이 바뀌었다. GF-93에서 만든 .github/workflows/weekly-review.yml과 이를 지원하던 docs/reviews/(README.md 포함)를 삭제했다. README.md/README.en.md의 저장소 구조 트리에서 관련 언급을 제거해 실제 상태와 일치시켰다. .github/workflows/test.yml(기존 dev CI)과 .claude/commands/review-full.md(대화형 /review-full 슬래시 커맨드 - 시크릿 불필요, 로컬 전용)는 그대로 유지했다. 검증: shellcheck -s sh 전체 통과, bats tests/ 전체 95개 통과(회귀 없음).
<!-- SECTION:FINAL_SUMMARY:END -->
