---
id: GF-63
title: CI에 POSIX 준수 게이트 명시화
status: Done
assignee: []
created_date: '2026-08-27 20:29'
updated_date: '2026-08-27 21:03'
labels: []
dependencies: []
ordinal: 61000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
test.yml의 shellcheck -s sh 스텝이 사실상 POSIX 준수(decision-9) 게이트 역할을 하고 있지만 스텝 이름/코멘트에 이 의도가 명시돼 있지 않다. 향후 기여자가 의도를 오해하고 스텝을 지우거나 -s sh를 -s bash로 바꾸는 걸 막기 위해 스텝 이름과 코멘트에 'POSIX 준수 게이트(decision-9)'임을 명확히 표시한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 test.yml의 shellcheck 스텝 이름/코멘트에 decision-9 POSIX 정책 강제 목적이 명시된다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
test.yml의 ShellCheck 스텝 이름을 'ShellCheck (POSIX 준수 게이트, decision-9)'로 바꾸고, -s sh를 지우거나 -s bash로 바꾸면 안 되는 이유를 코멘트로 명시. 워크플로 상단 코멘트의 오래된 decision-7 인용도 decision-8로 정정. YAML 파싱 검증 통과.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
test.yml의 ShellCheck 스텝이 사실은 POSIX 준수(decision-9) 게이트라는 걸 스텝 이름과 코멘트에 명시했다. 오래된 decision-7 인용도 정정.
<!-- SECTION:FINAL_SUMMARY:END -->
