---
id: GF-33
title: AI-Tool-Version cut 버그 + interpret-trailers 접두어 충돌로 트레일러 소실
status: Done
assignee: []
created_date: '2026-08-24 08:13'
updated_date: '2026-08-24 13:15'
labels: []
dependencies: []
priority: high
type: bug
ordinal: 33000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
AI_AGENT에 밑줄이 없으면 cut -d_ -f2가 전체 문자열을 그대로 반환해 AI_TOOL_VERSION=AI_TOOL_ID가 됨. 이 상태에서 addIfDifferent가 AI-Tool과 AI-Tool-Version을 같은 트레일러로 오인(접두어 매칭)해 값이 같으면 AI-Tool-Version을 아예 안 붙인다. GF-7에서 doNothing->addIfDifferent로 바꾼 것만으론 이 접두어 충돌을 완전히 못 피함 - 자체 정확 일치 검사로 바꿔야 함.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
AI_AGENT에 밑줄 없으면 AI-Tool-Version 생략(값 모름). git interpret-trailers 접두어매칭 대신 자체 정확일치 검사(trailer_exists)+--if-exists add로 전체 트레일러 로직 재작성 - 어떤 키 쌍도 접두어 충돌 안 남. 밑줄없음/정상/반복amend 멱등성 재검증.
<!-- SECTION:FINAL_SUMMARY:END -->
