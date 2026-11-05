---
id: GF-72
title: checks/java.sh가 gitformat.conf의 marker.java/marker.javaGradle을 읽도록 전환
status: Done
assignee: []
created_date: '2026-08-28 04:37'
updated_date: '2026-08-28 04:41'
labels: []
dependencies: []
ordinal: 70000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
hooks/checks/java.sh가 mvn/gradle 중 어느 빌드 도구를 쓸지 판단하려고 pom.xml/build.gradle*를 자체적으로 하드코딩해 재확인한다. pre-commit/pre-push는 이미 gitformat.conf의 gitformat.marker.java/marker.javaGradle에서 이 값을 읽는데(GF-46/47), java.sh만 GF-49(cpp.sh/sql.sh 전환) 때 빠뜨려서 값이 두 곳에 따로 존재한다. java.sh도 gitformat.conf에서 읽도록 전환한다(resolve_self를 독립적으로 추가해야 함, cpp.sh/sql.sh와 동일 패턴).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 hooks/checks/java.sh가 pom.xml/build.gradle* 리터럴 대신 gitformat.conf에서 marker.java/marker.javaGradle을 읽는다
- [x] #2 동작 변경 없음 - tests/checks-java.bats가 전과 동일하게 통과하고 shellcheck -s sh 경고가 없다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
hooks/checks/java.sh에 resolve_self()를 독립적으로 추가(cpp.sh/sql.sh와 동일 패턴)해 gitformat.conf 경로를 찾도록 함. pom.xml/build.gradle* 하드코딩을 marker.java/marker.javaGradle 조회로 대체. build.gradle* 글롭은 SC2086 의도적 예외 처리(pre-commit과 동일). bats 3/3(checks-java) + 전체 69/69 통과, shellcheck 전체 통과.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/checks/java.sh가 pom.xml/build.gradle* 하드코딩 대신 gitformat.conf의 marker.java/marker.javaGradle을 읽도록 전환했다(GF-49에서 빠뜨렸던 파일). 동작 변경 없음을 bats+shellcheck로 확인.
<!-- SECTION:FINAL_SUMMARY:END -->
