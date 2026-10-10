---
id: GF-145
title: Sigkill Foundry 형식 설계 문서 세우기
status: Done
assignee: []
created_date: '2026-10-05 11:52'
updated_date: '2026-10-10 22:38'
labels:
  - docs
dependencies: []
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
최상위 Sigkill Foundry 설계 문서와 같은 5문서 세트(design/: 0 문서 정보, 1 제안서 ~ 5 구현 결과 보고서, 부록)를 이 저장소에 세우고, Claude 앱 문서를 편집 원본으로 둔다. 이 저장소의 README·backlog 레퍼런스 문서·decision에서 1.01 배경과 문제, 1.02 원칙, 3.01 시스템 구성을 채우고 나머지 장은 골격으로 둔다(원천은 기존 문서). 진척 서술 금지.

수용 기준(승격 시 AC로 등록):
1. design/ 구조·장 형식이 최상위 Sigkill Foundry와 같다
2. 1.01 · 1.02 · 3.01을 기존 문서 근거로 채우고 나머지는 골격으로 둔다
3. Claude 앱에 장별 문서와 목차 문서를 만들고 design/README.md에 링크한다
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 design/ 구조·장 형식이 최상위 Sigkill Foundry와 같다
- [x] #2 1.01 · 1.02 · 3.01을 기존 문서 근거로 채우고 나머지는 골격으로 둔다
- [x] #3 설계 문서의 원본은 design/ 하나다 — Claude 앱 편집 원본 문구 · 링크 칸을 두지 않고, 목차 상태는 실제 파일 기준
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
최상위 Sigkill Foundry와 같은 5문서 설계 세트(design/)를 세웠다. 장 파일 구성은 최상위와 일치.
- 0 문서 정보: 최상위 TRL · NFR 번호를 같은 ID · 같은 뜻으로 이어받음(로컬 번호 대역 없음).
- 1.01 배경과 문제(계측 컴포넌트, 검사와 기록, 문제-대응 7행, 세 기둥), 1.02 원칙 P1~P12(대체 관계 표 포함), 3.01 시스템 구성(구성 요소 8개, 커밋 생애주기 DOT 흐름도, 트레일러 11종 표, TRL ↔ 훅 함수 대응). 나머지는 골격.
- 3.01은 현재 코드 기준(훅 3개) — decision-18·19의 통합 구조와의 차이는 3.05 · 4.03에서 다룸.
- 원본은 design/ 하나(Claude 앱 편집 원본 규칙 없음).
- 검증: python3 -m unittest discover -s tests → 106 OK.
<!-- SECTION:FINAL_SUMMARY:END -->
