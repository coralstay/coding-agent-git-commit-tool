---
id: GF-149
title: 'install에 플러그인 선택 옵션 추가: source-header만 설치'
status: In Progress
assignee: []
created_date: '2026-10-31T11:07:00Z'
updated_date: '2026-11-12T02:55:00Z'
labels:
  - hooks
  - install
dependencies: []
documentation:
  - ~/.claude/plans/giggly-kindling-snowglobe.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## 배경
유저 결정(2026-10-31): 기존 저장소에 .githooks를 설치할 때는 source-header 검사(20-source-header)만 우선 켜고, 커밋 형식 검사(10-commit-format)는 저장소마다 규칙 차이를 본 뒤 따로 진행한다. 지금 install은 기본 플러그인 두 개를 항상 함께 만든다(GF-148).

## 범위
install(과 migrate)에 플러그인 선택 옵션을 추가한다. 예: `git-commit-tool --plugins source-header [대상]`. 옵션이 없으면 지금처럼 둘 다 설치한다(새 프로젝트 기본값 유지).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 --plugins <이름,...> 옵션으로 설치할 플러그인을 고를 수 있고(commit-format, source-header), 옵션이 없으면 둘 다 설치한다. 모르는 이름이면 아무것도 쓰지 않고 exit 1
- [x] #2 migrate도 같은 옵션을 받는다
- [x] #3 README에 기존 저장소용 예시(git-commit-tool --plugins source-header)를 적는다
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 tests/ 전체 통과(일반·.githooks 경유 두 모드)
- [x] #2 임시 저장소에서 --plugins source-header 설치 후 커밋 형식이 강제되지 않고 source-header 검사만 도는 것을 실측
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
### Subjective
기존 저장소에는 source-header 플러그인만 먼저 설치하기로 유저가 정했다(2026-10-31).

### Objective
GF-148 install은 템플릿(.githooks)의 모든 파일을 없는 것만 복사한다. 플러그인은 prepare-commit-msg.d/10-commit-format, pre-commit.d/20-source-header 두 개다.

### Assessment
템플릿 복사 단계에서 플러그인 이름 목록으로 거르는 옵션 하나면 충분하다. 디스패처는 항상 설치한다(빈 .d는 아무것도 안 함).

### Plan
1. 테스트 먼저(--plugins source-header면 10-commit-format이 생기지 않음, 옵션 없으면 둘 다, 모르는 이름이면 오류)
2. install.sh 옵션 파싱 + 복사 필터
3. README 사용법
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-11-12 구현·검증 기록 (브랜치 task/GF-149, 커밋 7834cb5 11f1bcc 9476186, 푸시 전)
- AC #1: install에 --plugins <이름,...> (--plugins a,b 와 --plugins=a,b). 옵션이 없으면 둘 다 설치. 모르는 이름이면 아무것도 쓰지 않고 오류. 테스트 5개(test_install_githooks.py)가 구현 전 14개 중 4개 실패(알 수 없는 옵션)했다가 통과(서브에이전트 보고).
- AC #2: migrate도 같은 옵션을 받는다. 선택한 플러그인만 복사하고 기존 파일은 지우지 않는다. 테스트 3개(test_migrate_githooks.py). 먼저 실패하는 증거는 없다 — install과 같은 옵션 파서를 쓰므로 처음부터 통과했고 증거를 꾸미지 않았다.
- AC #3: README 설치 절에 기존 저장소용 예시(git-commit-tool --plugins source-header)와 migrate --plugins 언급.
- DoD #1(직접 실행): python3 -m unittest discover -s tests → 152 tests OK(54초). sh -n, shellcheck -s sh 통과. .githooks 경유 두 번째 모드(GITFORMAT_TEST_VIA_GITHOOKS=1)도 152개 통과했다는 것은 서브에이전트 보고이며 제가 다시 돌리지는 않았다.
- DoD #2(직접 측정, mktemp 저장소, 전역 git 설정 무력화): --plugins nope → 오류 메시지, 저장소에 .git과 a.c만 남음(아무것도 쓰지 않음). --plugins source-header 설치 → .githooks/pre-commit, prepare-commit-msg, pre-commit.d/20-source-header 3개만 생기고 prepare-commit-msg.d/10-commit-format 없음. 엉터리 메시지 커밋 성공(형식 미강제). .source-header.json을 켜고 헤더 없는 b.c를 커밋하면 'b.c:1: error: source header is missing (H001)'로 차단되고 커밋 수 그대로.
<!-- SECTION:NOTES:END -->
