---
id: GF-5
title: pre-push 훅 (빌드/테스트)
status: Done
assignee: []
created_date: '2026-08-24 03:12'
updated_date: '2026-08-24 03:35'
labels: []
dependencies:
  - GF-4
type: task
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
push 직전 언어별 무거운 빌드/테스트 실행
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/pre-push 작성: TS(npm test/build), Python(pytest), Java(mvn verify/gradle check), C++(cmake build+ctest)를 언어 감지 후 순차 실행. pre-commit보다 무거운 검증(테스트/전체빌드)을 담당. 도구/스크립트 없으면 조용히 건너뜀. sh -n 및 실행 테스트 완료.
<!-- SECTION:FINAL_SUMMARY:END -->
