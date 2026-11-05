---
id: GF-74
title: 문서 정합성 감사 (backlog/README vs 실제 코드)
status: Done
assignee: []
created_date: '2026-08-28 09:29'
updated_date: '2026-08-28 09:32'
labels: []
dependencies: []
ordinal: 72000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
이 세션에서 gitformat.conf 중앙화, 트레일러 로직 변경, 훅 재구조화 등 코드가 많이 바뀌었다. backlog/decisions와 backlog/tasks, README.md가 지금 코드의 실제 동작과 다르게 말하는 부분이 없는지 확인한다. 문장이 어색하거나 과장된 부분도 함께 다듬는다(윤문). 코드 변경 없이 문서만 대상으로 한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 주요 문서(README.md, backlog/decisions/*)에서 언급하는 파일 경로, 설정 키, 트레일러 이름, 훅 동작 설명이 hooks/*, hooks/checks/*.sh, hooks/gitformat.conf의 실제 내용과 일치한다
- [x] #2 불일치나 오래된 서술을 찾으면 고치고, 무엇을 왜 고쳤는지 구현노트에 남긴다
- [x] #3 과장되거나 수사적인 표현(예: 거창한 단어 사용)을 발견하면 간결한 표현으로 바꾼다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
README.md/decision-1~9/task 파일 등 전체를 코드(hooks/*, gitformat.conf, install.sh)와 대조. README 본문 내용은 실제 동작과 모두 일치함을 확인(타입 목록, 트레일러 이름, 마커 파일, Task-Id 파싱, AI-Model 신뢰수준, GitHub Actions 백스톱 등). 발견한 불일치 2건: (1) docs/references/pro-git/VENDORING.md가 'decision-1~7'로 decision 개수를 하드코딩해 9개로 늘어난 지금 상태와 어긋남 - 번호 범위 대신 backlog/decisions/ 링크로 수정. (2) README 저장소 구조 트리에 docs/examples/, .github/workflows/가 빠져있어 본문에서 언급하는 파일(github-actions-caller.yml, verify.yml)의 위치를 트리에서 확인할 수 없었음 - 추가함. 별도로 decision-5/gf-7 태스크가 언급하는 '도구-벤더 일관성 검사'는 commit-msg에 실제로 구현돼 있지 않음(존재+화이트리스트 검사만 있음) - 다만 README는 이 주장을 반복하지 않고, decision/task 파일은 CLAUDE.md 규칙상 CLI로 수정할 수 없는 항목이라 코드를 고치지 않고 기록만 남김.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
README.md와 backlog 문서를 코드와 대조해 불일치 2건(VENDORING.md의 decision 번호 범위, README 구조 트리의 누락 경로)을 수정했다. 나머지 서술은 실제 동작과 일치함을 확인.
<!-- SECTION:FINAL_SUMMARY:END -->
