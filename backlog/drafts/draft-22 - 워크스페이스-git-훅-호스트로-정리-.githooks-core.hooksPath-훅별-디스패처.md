---
id: DRAFT-22
title: '워크스페이스 git 훅 호스트로 정리: .githooks + core.hooksPath + 훅별 디스패처'
status: Draft
assignee: []
created_date: '2026-10-30T19:04:00Z'
updated_date: '2026-10-30T19:35:00Z'
labels:
  - hooks
  - workspace
dependencies: []
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## 배경
유저 결정(2026-10-31): 앞으로 생성하는 모든 프로젝트의 git 훅은 `git config core.hooksPath .githooks` 방식으로 관리한다.
core.hooksPath는 저장소당 디렉터리 하나만 가리키므로, 지금처럼 이 도구가 hooksPath를 자기 클론 경로(hooks/)로 잡으면
다른 도구(예: dev-tools/source-header의 pre-commit)와 공존할 수 없다. 그래서 이 저장소를 워크스페이스 git 훅 호스트로 정리한다.

## 목표 구조
<프로젝트>/.githooks/            (커밋됨, core.hooksPath=.githooks)
  pre-commit                     공용 디스패처(POSIX sh): pre-commit.d/* 를 이름순으로 실행, 하나라도 실패하면 중단
  pre-commit.d/20-source-header  한 줄: exec source-header hook pre-commit
  prepare-commit-msg             공용 디스패처
  prepare-commit-msg.d/10-commit-format  한 줄: 이 도구의 커밋 형식·트레일러 로직 호출

- 실제 로직은 ~/githubs/bin 의 명령에 있고 .githooks에는 한 줄짜리 연결만 둔다
- 명령이 PATH에 없으면(다른 머신 등) 경고 후 건너뛴다. 강제는 CI가 맡는다
- 설치 명령: 대상 저장소에 .githooks 템플릿 생성 + core.hooksPath=.githooks 설정. 링크가 아닌 기존 훅/다른 hooksPath가 있으면 덮지 않고 중단
- 기존 설치(hooksPath=클론 경로) 저장소의 이전 경로를 제공한다

## 관련
- dev-tools/source-header TASK-1 (도구 핵심). source-header는 `source-header hook pre-commit` 진입점만 제공하고 연결은 이 저장소가 맡는다
- 계획: ~/.claude/plans/giggly-kindling-snowglobe.md
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 공용 디스패처(POSIX sh)가 .githooks/<hook>.d/*를 이름순으로 실행하고, 하나라도 실패하면 그 exit 코드로 중단한다. 플러그인이 부르는 명령이 PATH에 없으면 경고 후 건너뛴다
- [ ] #2 커밋 형식·트레일러 로직이 prepare-commit-msg.d/10-commit-format 플러그인으로 동작하고, 기존 tests/ 전체가 통과한다
- [ ] #3 install이 대상 저장소에 .githooks 템플릿(pre-commit, prepare-commit-msg 디스패처 + 기본 플러그인)을 만들고 core.hooksPath=.githooks를 설정한다. 다른 hooksPath나 링크가 아닌 기존 훅이 있으면 덮지 않고 중단한다
- [ ] #4 pre-commit.d/20-source-header 플러그인이 source-header hook pre-commit을 부른다(source-header가 없으면 건너뜀)
- [ ] #5 hooksPath가 클론 경로인 기존 설치 저장소를 .githooks로 옮기는 migrate 명령이 있다
- [ ] #6 README·hooks/readme.md를 갱신하고, templateDir(decision-2)을 어떻게 바꾸는지 decision 기록을 남긴다
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests/ 전체 통과(기존 + 디스패처·install·migrate 신규), 로그를 Implementation Notes에 첨부
- [ ] #2 임시 저장소에서 install → 커밋 형식 검사와 source-header 검사가 둘 다 실제로 동작함을 실측
- [ ] #3 README·hooks/readme.md·decision 갱신
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
### Subjective
유저 결정(2026-10-31): 앞으로 만드는 프로젝트의 git 훅은 `git config core.hooksPath .githooks`(저장소에 커밋된 디렉터리)로 모두 관리하고, 이 저장소를 그 호스트로 정리한다. source-header의 pre-commit도 같은 디렉터리에서 돌아야 한다.

### Objective
- 지금 install.sh는 core.hooksPath를 이 클론의 hooks/로 잡는다(로컬). 전역 옵션은 init.templateDir로 새 저장소의 .git/hooks에 링크를 심는다(decision-2).
- 훅은 prepare-commit-msg 하나다. --no-verify로도 건너뛸 수 없다는 점 때문에 규칙 강제가 이 훅에 모여 있다(decision-18).
- core.hooksPath는 저장소당 디렉터리 하나만 가리킨다.

### Assessment
.githooks/<hook>은 공용 디스패처로 두고 <hook>.d/* 플러그인을 이름순으로 실행한다. 이 도구의 커밋 형식 로직은 prepare-commit-msg.d/10-commit-format이 기존 hooks/prepare-commit-msg를 호출하는 형태로 옮긴다(로직 자체는 그대로). 플러그인은 한 줄로 bin 명령을 부르고, 명령이 없으면 경고 후 건너뛴다. 기존 설치 방식과 decision-2(templateDir)를 어떻게 바꿀지는 decision 기록으로 남긴다.

### Plan
1. 디스패처 + 템플릿(.githooks/) 테스트 먼저 → 구현
2. install: 대상 저장소에 .githooks 생성 + core.hooksPath=.githooks, 기존 hooksPath·훅이 있으면 중단
3. 기존 설치(클론 경로) 저장소 이전 명령
4. README·hooks/readme.md·decision 갱신
<!-- SECTION:PLAN:END -->
