---
id: DRAFT-16
title: '[보류] bats 테스트 스위트 재설계'
status: Draft
assignee: []
created_date: '2026-09-24 09:28'
updated_date: '2026-09-24 14:18'
labels:
  - parked
  - post-migration
  - tests
dependencies: []
references:
  - GF-108
documentation:
  - doc-12
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## 배경

현재 테스트는 bats-core 기반 13개 파일 100개 케이스다(GF-108에서 103 → 100). 이 테스트들은 훅을 블랙박스(서브프로세스)로 호출해 종료 코드/출력/결과 트레일러만 확인하므로 훅이 sh든 Python이든 언어에 무관하게 동작한다 - 그래서 Python 전환의 안전망으로 그대로 재사용할 수 있다.

유저가 "추후에 bats 테스트도 다시 짤 생각이 있다"고 밝혔으나, 전환 작업 중에 테스트까지 바꾸면 안전망 자체가 흔들려 동작 동일성을 보장할 수 없다.

## 보류 사유

이번 전환에서는 기존 케이스를 그대로 쓰고, 언어 변경에 따라 꼭 필요한 경로 수정(hooks/checks/*.sh → *.py 하드코딩 등)만 반영한다. 스위트 자체의 재설계는 범위 밖.

## GF-108에서 이미 결정된 것 (재개 시 전제)

아래 착수 순서 5번("consistency.bats의 바이트 동일성 검사를 유지할지")은 GF-108에서 유저 결정으로 이미 답이 났다. **기능 테스트, 즉 행위 검증만 남기고 구현 언어에 종속된 테스트는 삭제한다**는 방침이다.

그에 따라 consistency.bats에서 훅 소스를 awk로 떠서 사본끼리 텍스트 비교하던 3건(resolve_self 동일성, TASK_PREFIX/BRANCH 블록 동일성, conf 읽기 가드 동일성)을 삭제했다. 셋 다 행위 검증 쪽에 대응이 있음을 확인한 뒤 지웠다 - 각각 robustness-dispatch.bats의 GF-16 케이스, conf-guard.bats 7건, robustness-injection.bats의 브랜치별 Task-Id 트레일러.

남은 consistency.bats 2건(GF-68 커밋 타입 목록 일치, GF-61 conf 키 존재)은 구현 언어와 무관한 설정/문서 값 일치 검사라 유지한다.

파급: GF-112에 있던 "consistency.bats에 Python 쪽 동일성 검사를 설계한다" 항목은 불필요해졌다. GF-112 착수 전에 그 범위를 조정해야 한다.

## 재개 조건

Python 전환 완료 후. 검토할 선택지: bats 유지 vs pytest 전환(훅이 Python이 되므로 내부 함수 단위 테스트가 가능해짐), 블랙박스/화이트박스 비중 재조정.

단 위의 "행위 검증만 남긴다" 방침을 고려하면 화이트박스/단위 테스트를 늘리는 방향은 방침과 충돌할 수 있다 - 재개 시 먼저 유저와 정리할 것.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
보류 상태이므로 구현 계획이 아니라 재개 시 착수 순서를 기록한다.

1. Python 전환(GF-108~113) 완료를 확인한다
2. 현재 100개 케이스를 성격별로 분류한다 - 블랙박스 커밋 플로우 / 단위 검증 / 파일 간 일관성 검사
3. pytest 전환 시 이득이 큰 것만 선별한다. 훅이 Python이 되면 내부 함수 단위 테스트가 가능해지므로 단위 검증 성격의 케이스가 후보. 단 GF-108의 '행위 검증만 남긴다' 방침과 충돌하는지 먼저 확인할 것
4. bats를 남길 범위를 결정한다 - 실제 git commit을 태우는 end-to-end 검증은 bats가 여전히 적합하다
5. (해결됨, GF-108) consistency.bats의 바이트 동일성 검사는 유지하지 않기로 했고 해당 3건은 이미 삭제됐다
<!-- SECTION:PLAN:END -->
