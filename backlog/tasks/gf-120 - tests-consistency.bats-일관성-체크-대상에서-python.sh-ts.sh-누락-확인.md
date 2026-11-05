---
id: GF-120
title: tests/consistency.bats 일관성 체크 대상에서 python.sh/ts.sh 누락 확인
status: Done
assignee: []
created_date: '2026-09-19 15:46'
updated_date: '2026-09-24 14:19'
labels: []
dependencies: []
documentation:
  - doc-12
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
tests/consistency.bats의 특정 일관성 체크(예: gitformat.conf 읽기 가드 동일성 체크, GF-76 관련)가 대상 파일 목록에 cpp.sh/sql.sh/java.sh만 나열하고 python.sh/ts.sh는 빠져 있다. 전체 커밋 플로우 테스트로 간접 커버는 되지만, 이 특정 체크 범위에서는 두 파일이 제외돼 있어 의도적인지 누락인지 확인 필요.

발견 경위: 2026-09-20 '이 프로젝트의 부족한점?' 조사(backlog/docs 조사 agent, tests/consistency.bats)
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
무효 종료(GF-122). 이 태스크는 tests/consistency.bats의 conf 읽기 가드 동일성 검사(GF-76) 대상 목록에 python.sh/ts.sh가 빠진 것이 의도인지 누락인지 확인하는 건이었다. GF-108에서 그 검사 자체가 삭제돼 확인할 대상 목록이 존재하지 않는다.

배경: 유저 결정으로 '기능 테스트, 즉 행위 검증만 남기고 구현 언어 종속 테스트는 삭제한다'는 방침이 정해졌고, 소스 텍스트를 사본끼리 비교하던 검사 3건이 함께 제거됐다. conf 읽기 가드의 경우 GF-77에서 이미 tests/conf-guard.bats가 런타임 검증(conf를 실제로 깨뜨려 각 파일을 실행)을 하고 있었고, 그쪽은 대상 누락 없이 7건이 유지된다 - 즉 이 태스크가 우려한 커버리지 공백은 더 강한 검사 쪽에 애초에 없었다.

경위와 대체 행위 검증의 위치는 doc-12에 정리했다.
<!-- SECTION:FINAL_SUMMARY:END -->
