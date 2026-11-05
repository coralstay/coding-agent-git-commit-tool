---
id: GF-42
title: 훅 리터럴 지역화 + 계약 문서화 (독립성 우선 리팩토링)
status: To Do
assignee: []
created_date: '2026-08-27 09:11'
updated_date: '2026-08-27 09:25'
labels: []
dependencies: []
type: task
ordinal: 42000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
이전 계획(공용 lib으로 resolve_self/TASK_PREFIX/BRANCH/AI_TOOL_ID 추출)은 방향을 바꿨다. 목적은 (1) 버그 수정을 쉽게 하기 위해 각 훅 파일이 자기 안에서 완결되게 하는 것, (2) 특정 훅 하나만 다른 셸/언어로 갈아끼울 수 있게 하는 것이다. 공용 lib을 여러 파일이 source하면 이 두 목적과 반대로 간다. 그래서 함수/변수 중복(resolve_self 등)은 그대로 두고, 대신 각 파일에 하드코딩된 리터럴(마커 파일명, 언어 감지 마커, trailer 키 이름, AI 도구 식별자 등)을 파일 상단의 지역 변수로 추출한다 — 다른 파일과 공유하지 않고 파일마다 독립적으로. 여러 파일이 반드시 같은 값을 써야 맞물려 동작하는 계약 성격 리터럴(마커 파일명, Task-Id 정규식 등)은 공유 파일 없이 각자 하드코딩하되, backlog 문서화 + bats 테스트로 드리프트를 감지한다. 이 태스크는 하위 서브태스크(파일별 리터럴 지역화)들의 부모 역할만 한다.
<!-- SECTION:DESCRIPTION:END -->

## Comments

<!-- COMMENTS:BEGIN -->
created: 2026-08-27 09:25
---
방향 전환(2026-08-27): 공용 lib 추출(중복 제거)은 '버그 수정 용이성'과 '훅별 셸 교체 가능성'이라는 목적과 상충해 폐기. 대신 파일별 리터럴 지역화(독립성 유지)로 재설계 — 하위 서브태스크는 -p GF-42로 생성됨. GF-43(cpp.sh/sql.sh 공용 함수화)도 같은 이유로 은퇴, 대체 작업은 이 태스크의 서브태스크로 이관.
---
<!-- COMMENTS:END -->
