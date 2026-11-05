---
id: GF-117
title: 'README 지원 언어 문구 ''등'' 정정 (5종 고정, 확장 계획 없음)'
status: Done
assignee: []
created_date: '2026-09-19 15:46'
updated_date: '2026-09-25 02:25'
labels: []
dependencies: []
documentation:
  - backlog/docs/doc-6 - 주의점과-한계.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
README.md:25의 'TS, C/C++, Java, Python, SQL 등' 표현이 향후 확장 가능성을 암시하지만, backlog/docs/doc-6에는 5종 고정이며 확장 계획이 없다고 명시돼 있다. README 문구를 '5종 고정'으로 명확히 정정할지 검토.

발견 경위: 2026-09-20 '이 프로젝트의 부족한점?' 조사(backlog/docs 조사 agent, README.md:25 vs backlog/docs/doc-6)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 README.md의 지원 언어 나열에서 '등'이 제거되고 5종(TS, C/C++, Java, Python, SQL) 고정임이 드러나는 문구로 바뀐다
- [x] #2 README 전체에서 지원 언어 확장 가능성을 암시하는 다른 표현이 남아 있지 않다
- [x] #3 doc-6:32의 '5종으로 고정' 서술과 README 문구가 서로 모순되지 않는다
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. README에서 지원 언어를 나열하거나 확장을 암시하는 모든 지점을 찾는다
2. README.md:27 'TS, C/C++, Java, Python, SQL 등' → '등' 제거로 닫힌 목록으로 만든다
3. doc-6:32와 같은 표현으로 '5종 고정 + 확대 계획 없음'을 README 본문에도 한 문장 추가한다
4. README 전체 재확인 후 bats 전체 스위트로 회귀 없음을 확인한다
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
README.md 두 곳을 수정했다. (1) :27 동기 설명의 '(TS, C/C++, Java, Python, SQL 등)'에서 '등'을 제거해 닫힌 목록으로 만들었다. (2) :53에 '지원 언어는 TS/Python/Java/C·C++/SQL 5종으로 고정돼 있고 확대 계획은 없습니다.'를 추가했다 — doc-6:32와 같은 표현을 써서 두 문서가 문자열 수준에서 대조 가능하게 했다. README에는 별도 '한계' 섹션이 없고 :195에서 backlog doc으로 넘기므로, 언어 고정 사실은 기존 lint 도구 설명 단락에 붙였다.

같은 단락의 'lint 도구(npm/ruff/clang-format/mvn/sqlfluff 등)'의 '등'은 의도적으로 남겼다 — 나열이 실제로 부분집합이라(flake8, gradle 누락) 여기서는 '등'이 정확한 서술이다. 언어 목록과 달리 확장 가능성을 암시하는 오류가 아니다.

검증 증거: (1) grep으로 README.md:27이 '(TS, C/C++, Java, Python, SQL)'로 바뀐 것 확인. (2) grep -nE '(TS|Python|Java|SQL|C\+\+)[^)]*등\)' 결과 0건 — 언어 나열에 붙은 '등'이 남아 있지 않음. (3) grep '5종으로 고정'이 README.md:53과 doc-6:32 양쪽에서 같은 언어 나열로 일치. 회귀 검증: bats tests/ 104/104 통과(실패 0).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
README.md:27의 '(TS, C/C++, Java, Python, SQL 등)'에서 '등'을 제거해 지원 언어를 닫힌 목록으로 만들고, :53에 doc-6:32와 동일한 표현으로 'TS/Python/Java/C·C++/SQL 5종 고정, 확대 계획 없음'을 명시했다. 같은 단락의 lint 도구 나열은 실제로 부분집합이라 '등'을 의도적으로 남겼다. grep으로 세 AC를 각각 확인했고 bats 전체 104/104 통과로 회귀가 없음을 확인했다.
<!-- SECTION:FINAL_SUMMARY:END -->
