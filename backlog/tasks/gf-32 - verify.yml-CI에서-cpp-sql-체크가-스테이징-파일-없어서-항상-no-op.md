---
id: GF-32
title: verify.yml CI에서 cpp/sql 체크가 스테이징 파일 없어서 항상 no-op
status: Done
assignee: []
created_date: '2026-08-24 08:13'
updated_date: '2026-08-24 13:13'
labels: []
dependencies: []
priority: high
type: bug
ordinal: 32000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
verify.yml은 컨슈머 저장소를 체크아웃만 하고 git add를 안 해서, git diff --cached 기반인 cpp.sh/sql.sh가 항상 빈 목록을 보고 조용히 건너뛴다. PR에 깨진 C++/SQL이 있어도 CI 백스톱이 절대 못 잡는다.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
verify.yml에 git reset --soft $BASE_SHA 추가 -> git diff --cached가 PR 전체 변경분을 노출해 cpp.sh/sql.sh가 실제로 검사하게 됨(git add -A는 이미 커밋된 파일엔 효과 없어서 안 통했음). 실제 PR(#2)로 검증: 깨진 main.cpp를 verify/verify가 실제로 잡는 것 확인. 검증 과정에서 부가로 발견된 CI 전용 이슈(shellcheck 버전차 SC2317, test.yml 실도구 미설치, path_without의 플랫폼별 경로 취약성)도 모두 같은 PR에서 수정, 최종 CI 전부 green 확인 후 머지.
<!-- SECTION:FINAL_SUMMARY:END -->
