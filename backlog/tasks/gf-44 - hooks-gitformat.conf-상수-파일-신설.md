---
id: GF-44
title: hooks/gitformat.conf 상수 파일 신설
status: Done
assignee: []
created_date: '2026-08-27 09:37'
updated_date: '2026-08-27 09:40'
labels: []
dependencies: []
ordinal: 42000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
hooks/commit-msg, hooks/pre-commit, hooks/pre-push, hooks/post-commit, hooks/checks/cpp.sh, hooks/checks/sql.sh에 흩어진 하드코딩 리터럴(마커 파일명 .gitformat-verified, TASK_PREFIX/EXEMPT 기본값, trailer 키 7종, AI 도구 식별자 claude-code, Co-Authored-By 값, 언어 감지 마커 5종, sqlfluff 기본 dialect, cpp 확장자 목록, known-models.txt 경로, .gitformat-build 디렉터리명)을 hooks/gitformat.conf(git config 포맷) 한 곳에 모은다. 이 시점에는 conf 파일과 값만 만들고 각 훅 코드는 건드리지 않는다 — 이후 태스크들이 이 파일의 키 이름에 의존하므로 먼저 완료돼야 한다. 스키마는 backlog 문서(plan)에 초안이 있다: [gitformat] markerFile/taskPrefixDefault/branchExempt(다중값)/aiToolClaudeCode/coAuthoredBy/knownModelsFile/sqlDialectDefault/buildDir, [gitformat "trailer"] verifyBypassed/taskId/aiTool/aiToolVersion/coAuthoredBy/aiModel/hooksCommit, [gitformat "marker"] ts/python(다중값)/java/javaGradle/cpp/cppMake/sql, [gitformat "cpp"] ext(다중값).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 hooks/gitformat.conf가 git config 포맷으로 유효하다(git config --file hooks/gitformat.conf --list로 파싱 가능)
- [x] #2 스키마의 모든 키 값이 현재 각 훅에 하드코딩된 값과 정확히 일치한다(값 자체는 안 바뀜, 새 파일만 추가)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. 각 훅 파일을 다시 정독해 정확한 리터럴 값을 확인
2. hooks/gitformat.conf를 git config 포맷으로 작성 (git config --file로 set)
3. git config --file hooks/gitformat.conf --list 로 파싱 검증
4. 각 값이 현재 하드코딩된 값과 정확히 일치하는지 grep으로 재대조
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
hooks/gitformat.conf를 git config --file 명령으로 생성(직접 손으로 문법 작성 대신 git 자체 명령으로 값을 넣어 포맷 오류 방지). git config --file hooks/gitformat.conf --list로 27개 키/값 전부 파싱 확인, --get-all로 다중값(branchExempt 4개, marker.python 2개, cpp.ext 7개) 정상 조회 확인. 현재 하드코딩된 값과 grep으로 재대조해 정확히 일치함을 확인.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/gitformat.conf(git config 포맷) 신설 완료. 마커 파일명, TASK_PREFIX/EXEMPT 기본값, trailer 키 7종, AI 도구 식별자, Co-Authored-By 값, 언어 감지 마커 5종+glob, sqlfluff dialect, cpp 확장자 7종, known-models 경로, build 디렉터리명을 한 곳에 정리. git config --file --list로 파싱 검증 완료. 아직 어떤 훅 코드도 이 파일을 읽지 않음(다음 태스크 GF-45~49에서 전환).
<!-- SECTION:FINAL_SUMMARY:END -->
