---
id: GF-23
title: commit-msg 견고성 테스트 (동등분할/경계값/결정테이블/구문테스트)
status: Done
assignee: []
created_date: '2026-08-24 04:48'
updated_date: '2026-08-27 06:42'
labels: []
dependencies:
  - GF-21
type: task
ordinal: 23000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
type/scope 형식, Task-Id 브랜치 패턴, AI-Model 게이트를 다음 테스트 기법으로 커버: 동등분할, 경계값분석, 결정테이블, 구문테스트
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 동등분할: 유효/무효 type, scope 유무, BREAKING CHANGE(!/footer) 각 클래스 대표값 테스트
- [x] #2 경계값분석: 빈 description, 매우 긴 subject/branch명, task 번호 0/매우 큰 수
- [x] #3 결정테이블: AI_AGENT유무 x tool=claude-code유무 x gitformat.aiModel설정유무 x 화이트리스트일치 조합 전부
- [x] #4 구문테스트: 개행/셸 메타문자가 포함된 커밋 메시지가 정상적으로 거부/처리되는지
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. tests/robustness-commit-msg.bats 신규 작성 (load helpers/git-format)
2. 동등분할: 유효/무효 type, scope 유무, BREAKING CHANGE(!/footer) 대표값 테스트
3. 경계값분석: 빈 description 거부, 매우 긴 subject 통과, Task-Id 0/매우 큰 수/매우 긴 브랜치명 통과, Task-Id 없는 non-exempt 브랜치 거부
4. 결정테이블: AI_AGENT 미설정/claude-code/비-claude-code x aiModel 설정여부 x 화이트리스트 일치여부 5개 대표 행
5. 구문테스트: 셸 메타문자(subject) 무해 처리, 개행 포함 body 통과, 제어문자(탭) 시작 거부
6. bats tests/robustness-commit-msg.bats 로컬 실행 후 acceptance criteria 체크
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
tests/robustness-commit-msg.bats 신규 작성, bats 로컬 실행 결과 19/19 통과. 동등분할 5건, 경계값분석 6건, 결정테이블 5건, 구문테스트 3건.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
created: 2026-08-24 13:18
---
세션 일시정지 지점(2026-08-24). GF-23~28은 ISO/IEC 25010+29119 견고성 테스트 계획(decision-7)의 나머지. 사용자가 범위를 아직 확정 안 함 — 다음 세션 시작 시 'GF-23~26(형식적 커버리지 확장) 뺄지, GF-27(보안/인젝션)·GF-28(Actions 견고성)만 먼저 할지, 아니면 6개 다 순차로 할지'부터 다시 물어볼 것. GF-1~22, 29~40은 전부 완료·머지·푸시됨(main 클린, 원격과 동기화).
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/commit-msg를 표준 인용 없이 실무 근거(decision-8)로 커버하는 bats 테스트 19건 작성. tests/robustness-commit-msg.bats, 로컬 bats 실행 19/19 통과로 검증.
<!-- SECTION:FINAL_SUMMARY:END -->
