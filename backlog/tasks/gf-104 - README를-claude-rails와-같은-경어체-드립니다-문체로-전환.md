---
id: GF-104
title: README를 claude-rails와 같은 경어체(-드립니다) 문체로 전환
status: Done
assignee: []
created_date: '2026-09-19 14:57'
updated_date: '2026-09-19 15:02'
labels: []
dependencies: []
type: docs
ordinal: 101000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
사용자가 claude-rails README 전문을 직접 붙여넣고, 같은 훅 계열 저장소이니 문체(경어/존대, "왜 필요했는지 말씀드립니다"류 -드립니다체)까지 그대로 참고해서 만들라고 명시했다. 대제목(상단 소개 문단)부터 손보라는 지시도 있었다.

GF-99/101/102에서 확정한 5개 섹션 구조(왜/무엇을/훅 생애주기/설치/더 자세한 내용)와 실제 정보(핵심 두 문장, 훅 순서, AI귀속 표, githooks 공식문서 링크 2곳, backlog 포인터)는 그대로 유지하고, 섹션 제목과 본문 문장 끝을 claude-rails 스타일("~말씀드립니다", "~해 드립니다", "~습니다")로 전환한다. 상단 소개 문단도 claude-rails의 "~하기 위해 만들어 사용하고 있는 ~입니다" 패턴으로 다시 쓴다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 5개 섹션 제목이 각각 "왜 만들었는지 말씀드립니다/무엇을 만들었는지 말씀드립니다/훅을 생애주기별로 정리해 드립니다/설치 방법을 안내해 드립니다/더 자세한 내용이 궁금하시다면" 패턴으로 바뀐다
- [x] #2 상단 소개 문단이 claude-rails와 같은 "~만들어 사용하고 있는 ~입니다" 톤으로 바뀐다
- [x] #3 본문 문장 끝이 전반적으로 -습니다/-드립니다 경어체로 통일된다(기존 반말/명령형 어미 없음)
- [x] #4 GF-99/101/102가 확정한 정보(핵심 두 문장, 훅 순서, AI귀속 표, githooks 링크 2곳, backlog 포인터 4개, install 명령)는 내용 손실 없이 그대로 유지된다
- [x] #5 shellcheck -s sh 전체와 bats tests/ 전체가 통과한다
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
5개 섹션 제목을 claude-rails 스타일 -드립니다체로 변경, 본문 문장 끝을 전반적으로 경어체로 통일, 상단 소개 문단도 같은 톤으로 재작성. 기존 확정 정보(표/링크/명령)는 그대로 유지.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
검증: (1) grep "^## " README.md -> 5개 섹션 제목 모두 "-말씀드립니다/-해 드립니다" 패턴으로 확인. (2) 상단 소개 문단이 "공유할 수 있게 만들어 사용하고 있는 도구입니다"로 claude-rails 패턴 반영. (3) 본문 전체를 훑어 반말/명령형 어미(-하세요 등) 없음, "-습니다/-드립니다"로 통일 확인. (4) diff로 핵심 두 문장/훅 순서/AI귀속 표/githooks 링크 2곳/backlog 포인터 4개/install 명령 전부 내용 그대로 유지, 문장 끝만 바뀜을 확인. (5) shellcheck -s sh 전체 clean, bats tests/ 103/103 통과.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
README를 같은 훅 계열 저장소 coralstay/claude-rails의 경어체(섹션 제목 "~말씀드립니다"/"~해 드립니다", 본문 "-습니다")로 전환했다. 5개 섹션 제목(왜/무엇을/훅생애주기/설치/더 자세한 내용)을 claude-rails 패턴으로 바꾸고, 상단 소개 문단과 본문 문장 끝을 전반적으로 경어체로 통일했다. GF-99/101/102가 확정한 정보(핵심 두 문장, 훅 순서, AI귀속 표, githooks 공식문서 링크 2곳, backlog 포인터, install 명령)는 내용 손실 없이 그대로 유지했다.

검증: shellcheck -s sh 전체 clean, bats tests/ 103/103 통과.
<!-- SECTION:FINAL_SUMMARY:END -->
