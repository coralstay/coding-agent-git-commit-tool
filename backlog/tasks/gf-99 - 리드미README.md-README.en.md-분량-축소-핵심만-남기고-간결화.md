---
id: GF-99
title: 리드미(README.md) 3섹션 재구성 - 왜/무엇을/훅 생애주기 + README.en.md 삭제
status: Done
assignee:
  - '@coralstay'
created_date: '2026-09-19 04:46'
updated_date: '2026-09-19 05:26'
labels: []
dependencies: []
type: docs
ordinal: 96000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
README.md가 394줄/23개 섹션으로 늘어나 있다. 사용자가 정보 압축이 아니라 재구성을 요청했다: README.en.md(영어판, GF-75)를 삭제하고, README.md를 정확히 세 개의 최상위 섹션 - 왜 만들었는가 / 무엇을 만들었는가 / 훅 생애주기마다 어떤 훅이 동작하는가 - 로 재편한다. 나머지 기존 독립 섹션(설치/사용법/저장소가 바꾸는 것/커밋규칙/훅목록/Task-Id/no-verify탐지/AI귀속/커스터마이즈/저장소구조/주의점/한계/라이선스)은 독립 헤더로 남기지 않고, 꼭 필요한 조각(설치 명령, 라이선스 한 줄)만 세 섹션 안에 흡수한다. 섹션이 3개뿐이라 목차(📖 목차)도 제거한다.

"왜 만들었는가" 섹션은 다음을 핵심 결론으로 명시해야 한다: 이 git 포맷을 강제하는 궁극적 이유는 (a) 에이전트가 여러 커밋을 남겼을 때 나중에 분석 가능하게 하는 것과 (b) 그 기록을 사람이 이해할 수 있는지 확인하는 것이다.

"훅 생애주기" 섹션은 pre-commit→commit-msg→(커밋 생성)→post-commit 순서와 각 훅이 하는 일(형식/길이/Task-Id 검증, 언어별 lint, --no-verify 우회 탐지, AI 귀속/토큰 트레일러 자동 삽입 - 사유 슬러그 포함)을 표로 담는다.

GF-99에서 빠지는 세부 내용(설치 상세, 커밋규칙 전문, AI귀속 표 전체, 커스터마이즈, 저장소구조, 주의점/한계 전문, 실사용 예시)은 정보 손실 없이 후속 태스크(GF-100, backlog/docs)로 이관한다 - GF-99 자체에서는 삭제만 하면 되고 이관 작업은 GF-100 몫이다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 README.en.md가 삭제되고 README.md의 언어 전환 링크와 📖 목차 섹션도 제거된다
- [x] #2 README.md가 정확히 세 개의 최상위 섹션(왜 만들었는가/무엇을 만들었는가/훅 생애주기마다 어떤 훅이 동작하는가)만 갖는다 - 기존 독립 헤더 13개는 더 이상 존재하지 않는다
- [x] #3 "왜 만들었는가" 섹션이 에이전트의 다중 커밋 분석 가능성과 사람의 이해 가능성을 핵심 결론으로 명시한다
- [x] #4 "무엇을 만들었는가" 섹션에 실제 설치 명령(기존 저장소 적용 + --global)이 남아있다
- [x] #5 "훅 생애주기" 섹션이 pre-commit/commit-msg/post-commit 순서와 각 훅의 역할, AI 귀속/토큰 트레일러(사유 슬러그 포함)를 표로 담는다
- [x] #6 반복되던 예시 블록(git log -1 등)이 1~2개로 줄어든다
- [x] #7 README.md 안의 decision-N/GF-N 참조 링크가 삭제/오손되지 않는다
- [x] #8 shellcheck -s sh 전체와 bats tests/ 전체가 통과한다
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. README.en.md 삭제 + 언어전환 링크/목차 제거
2. README.md를 3섹션(왜/무엇을/훅생애주기)으로 재작성 - 왜: AI 다중커밋 분석가능성+사람 이해가능성을 핵심결론으로 명시. 무엇을: 3 POSIX sh 훅+conf+install.sh, git-native, 설치 명령(단일+--global) 유지, 라이선스 한줄 흡수. 훅생애주기: pre-commit->commit-msg->(커밋생성)->post-commit 표 + AI귀속/토큰 트레일러 사유슬러그 포함
3. 예시 블록 1~2개로 축소, decision-N/GF-N 참조 살아있는 문장만 유지
4. shellcheck+bats 통과 확인, README.en 잔여 참조 확인(backlog/ 제외)
5. AC 8개 검증 후 Done
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
검증: shellcheck -s sh hooks/commit-msg hooks/pre-commit hooks/post-commit hooks/checks/*.sh install.sh 경고 없음(exit 0). bats tests/ 전체 103개 통과(exit 0, 회귀 없음). grep -rn README.en . 결과 backlog/tasks·backlog/decisions(과거 기록)만 남고 그 외 잔여 참조 없음. grep -o decision-N README.md로 추출한 7개(3,4,5,6,10,12,14) 모두 backlog/decisions/에 실재. 커밋 3개: [chore][backlog] GF-99 재정의+GF-100 생성 / [docs][readme] 3섹션 재구성(README.en.md 삭제 포함).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
README.md를 왜 만들었는가/무엇을 만들었는가/훅 생애주기마다 어떤 훅이 동작하는가 3개 최상위 섹션으로 재구성하고 README.en.md를 삭제했다(언어전환 링크·목차 제거). '왜' 섹션은 AI 에이전트의 다중 커밋 분석 가능성과 사람의 이해 가능성을 핵심 결론으로 명시했고, '무엇을' 섹션에 단일 저장소/--global 설치 명령과 라이선스 한 줄을 남겼고, '훅 생애주기' 섹션에 pre-commit→commit-msg→(커밋생성)→post-commit 순서와 AI 귀속/토큰 트레일러(사유 슬러그 6개 포함) 표를 담았다. git log -1 예시는 1개로 축소, decision-3/4/5/6/10/12/14 참조는 살아있는 문장 안에서 보존했다. 빠진 세부 내용(설치 상세/커밋규칙 전문/AI귀속 표 전체/커스터마이즈/저장소구조/주의점·한계/실사용 예시)은 GF-100에서 backlog/docs로 이관 예정. 검증: shellcheck -s sh 전체 clean, bats tests/ 103/103 통과, README.en 잔여 참조는 backlog/tasks·decisions 과거 기록에만 존재.
<!-- SECTION:FINAL_SUMMARY:END -->
