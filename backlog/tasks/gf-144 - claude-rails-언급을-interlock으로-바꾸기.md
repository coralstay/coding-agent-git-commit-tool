---
id: GF-144
title: claude-rails 언급을 interlock으로 바꾸기
status: Done
assignee: []
created_date: '2026-10-05 07:49'
updated_date: '2026-10-05 08:08'
labels:
  - rename
dependencies: []
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
claude-rails 저장소가 interlock(coralstay/interlock)으로 이름이 바뀐다. 계획: ~/.claude/plans/typed-chasing-conway.md

수용 기준(승격 시 AC로 등록):
1. .claude-rails.json을 .interlock.json으로 바꾼다 (interlock이 옛 이름도 읽으므로 순서 무관)
2. README·레퍼런스 문서·코드 주석의 claude-rails 이름과 링크를 interlock / coralstay/interlock으로 바꾼다. 완료 태스크·decision 기록은 그대로 둔다
3. 테스트 게이트 통과
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 .claude-rails.json을 .interlock.json으로 바꾼다
- [x] #2 README·레퍼런스 문서·코드 주석의 claude-rails 이름과 링크를 interlock / coralstay/interlock으로 바꾼다. 완료 태스크·decision 기록은 그대로
- [x] #3 테스트 게이트 통과
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
살아 있는 레퍼런스 문서 backlog/readme.md·doc-20(가이드)·doc-21(개념 지도)의 claude-rails를 interlock으로 바꿨다(9e6ba79). AC#1: 이 저장소에는 .claude-rails.json이 원래 없어(doc-13 참고) 옮길 파일이 없었고, .gitignore에도 .claude-rails/ 항목이 없었다 — 새 .interlock.json은 만들지 않았다. README·hooks·install.sh·CI·tests에는 claude-rails 언급이 없었다. 남긴 것: 기록 문서 doc-11(GF-107 우회 기록)·doc-13(재설계 계획)·doc-19(실측), decision-24, draft-18·20, 다른 태스크 기록. 검증: python3 -m unittest discover -s tests → Ran 106 tests OK, ruff check hooks/ tests/ → All checks passed (bats 스위트는 decision-21로 unittest에 이관돼 없음).
<!-- SECTION:FINAL_SUMMARY:END -->
