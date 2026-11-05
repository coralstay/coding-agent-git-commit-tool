---
id: GF-103
title: backlog/ 및 하위 7개 폴더에 readme.md 추가 (claude-rails 관례 참고)
status: Done
assignee: []
created_date: '2026-09-19 14:49'
updated_date: '2026-09-19 14:54'
labels: []
dependencies: []
type: docs
ordinal: 100000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
여러 프로젝트(git-format, claude-rails 등)를 backlog.md CLI로 관리하는데 프로젝트마다 구조 파악이 안 돼 헷갈린다는 피드백. claude-rails의 backlog/ 디렉토리를 직접 확인해보니 디렉토리 이름 자체(tasks/drafts/docs/decisions/milestones/completed/archive)는 git-format과 거의 동일하고, 실제 차이는 (1) task_prefix가 GF vs task라는 것(backlog.md CLI가 초기화 후 변경을 명시적으로 거부하므로 이건 못 바꿈), (2) claude-rails는 backlog/ 및 각 하위 폴더마다 "무엇인가/언제 쓰나/관련 명령" 3단 구성의 readme.md를 두고 있는데 git-format에는 이게 하나도 없다는 것. 구조 파악 어려움의 실제 원인은 후자로 보인다.

claude-rails의 readme.md들은 backlog CLI가 관리하는 엔티티(task-N/doc-N/decision-N 등)가 아니라 순수 정적 마크다운 파일이라 CLI를 거치지 않고 직접 작성/배치한다(CLAUDE.md의 "CLI로만 수정" 원칙은 task/draft/doc/decision/milestone 마크다운에 적용되는 것이지 이런 폴더 안내문에는 해당 안 됨).

각 readme.md는 claude-rails 형식을 참고하되 git-format 자신의 실제 내용(GF 접두어, decision 15개+대체 체인, milestone m-0/m-2, gitformat.taskPrefix 브랜치 강제 등)으로 채운다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 backlog/readme.md와 tasks/drafts/docs/decisions/milestones/completed/archive 7개 하위 폴더 readme.md, 총 8개 파일이 생성된다
- [x] #2 각 readme.md가 "무엇인가/언제 쓰나/관련 명령" 3단 구성을 따르고 git-format의 실제 수치(태스크 개수, decision 개수, milestone 이름 등)와 관례(GF 접두어, decision 대체 체인은 파일 본문 확인 필요, gitformat.taskPrefix 브랜치 강제 등)를 정확히 반영한다
- [x] #3 decisions/readme.md가 decision update/delete 명령 부재 및 CLAUDE.md의 "직접 수정 금지 원칙과 충돌" 지점을 명시한다(claude-rails와 동일하게 이 저장소도 겪는 실제 제약)
- [x] #4 archive/readme.md와 completed/readme.md가 각각 실제 보관된 항목(GF-42+서브태스크 6개/m-1, GF-43)과 그 경위를 정확히 설명한다
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
claude-rails backlog/ readme.md 8개(최상위+7개 하위폴더) 형식을 참고해 git-format 실제 내용으로 채운 readme.md 8개를 직접 작성(backlog CLI 비관리 파일이라 Write로 직접 생성).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
검증: (1) backlog/readme.md + 7개 하위 폴더(tasks/drafts/docs/decisions/milestones/completed/archive) readme.md 총 8개 파일 생성 확인(ls). (2) 각 파일이 무엇인가/언제 쓰나/관련 명령 3단 구성을 따르고 실제 수치(태스크 99개, decision 15개, milestone m-0/m-2, doc 8개)를 반영. (3) decisions/readme.md에 decision update/delete 명령 부재 및 CLAUDE.md 직접수정금지 원칙과의 충돌 지점을 명시. (4) archive/readme.md에 GF-42+서브태스크 6개(공용로직 추출 시도 후 decision-9 방향으로 폐기) 및 m-1(GitHub 이슈 관리 에픽 보류) 경위, completed/readme.md에 GF-43 및 cleanup 기준 설명. (5) backlog doctor 클린, backlog task list/doc list 정상 동작 확인(새 readme.md들이 CLI 엔티티 인식에 영향 없음). shellcheck -s sh 전체 clean, bats tests/ 103/103 통과.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
여러 backlog.md 프로젝트(git-format, claude-rails)를 오갈 때 디렉토리 구조 파악이 안 된다는 피드백에 따라, claude-rails가 이미 쓰고 있는 관례(각 폴더에 "무엇인가/언제 쓰나/관련 명령" 3단 구성 readme.md)를 그대로 가져와 backlog/ + 하위 7개 폴더(tasks/drafts/docs/decisions/milestones/completed/archive)에 이 저장소 실제 내용으로 채운 readme.md 8개를 추가했다. decisions/readme.md는 decision update/delete 명령이 없어 CLAUDE.md의 "CLI로만 수정" 원칙과 충돌하는 지점을 명시했고, archive/completed readme.md는 실제 보관된 항목(GF-42+서브태스크, m-1 / GF-43)과 그 경위를 설명한다. 이 readme.md들은 backlog CLI가 관리하는 엔티티가 아니라 순수 정적 파일이라 CLI를 거치지 않고 직접 작성했다.

검증: backlog doctor 클린, shellcheck -s sh 전체 clean, bats tests/ 103/103 통과.
<!-- SECTION:FINAL_SUMMARY:END -->
