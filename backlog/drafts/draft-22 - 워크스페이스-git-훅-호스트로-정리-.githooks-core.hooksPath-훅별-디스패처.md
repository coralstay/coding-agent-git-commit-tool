---
id: DRAFT-22
title: '워크스페이스 git 훅 호스트로 정리: .githooks + core.hooksPath + 훅별 디스패처'
status: Draft
assignee: []
created_date: '2026-10-30T19:04:00Z'
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
