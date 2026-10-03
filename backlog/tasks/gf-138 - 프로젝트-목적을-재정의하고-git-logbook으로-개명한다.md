---
id: GF-138
title: 프로젝트 목적을 재정의하고 git-logbook으로 개명한다
status: Done
assignee:
  - '@claude'
created_date: '2026-10-03 02:57'
updated_date: '2026-10-03 03:18'
labels:
  - docs
  - naming
dependencies: []
references:
  - decision-11
  - decision-12
  - decision-24
documentation:
  - backlog/docs/doc-20 - GitHub-원격-강제-설정-관리-—-rulesets와-저장소-설정.md
priority: high
type: docs
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
README와 도구 이름은 이 프로젝트를 '커밋 메시지 형식을 정하는 도구'로 소개한다. 그런데 실제 설계는 그보다 넓다 — append-only 이력 정책과 GitHub 원격 강제(decision-24, DRAFT-18/19/20), Tokens-Used·AI-Model 같은 출처 측정 트레일러와 게이트, Task-Id 브랜치 강제, 에디터 커밋 금지. 2026-10-03 범위 점검에서 이 어긋남이 드러났고, 유저가 판단했다: 이것들까지 포함하는 것이 이 프로젝트의 목적이다.

그래서 목적을 세 기둥으로 다시 적는다 — 형식(제목·본문 규칙), 출처 기록(트레일러 자동 기록과 관련 게이트), 이력 불변(append-only를 로컬 훅과 원격으로 강제). 이 목적은 decision-11(서버측·CI 검증은 범위 밖)과 decision-12(push 단계는 다루지 않음)의 범위 제외 조항과 충돌하므로, 새 decision이 그 조항을 대체한다고 명시해야 한다.

이름도 목적에 맞춘다. git-format은 첫 번째 기둥만 말한다. git-logbook(항해일지 — 정해진 양식으로 순서대로 쓰고 지난 장은 고치지 않는다)이 세 기둥을 함께 담는다. GitHub 저장소는 새로 만들지 않고 coralstay/git-format을 rename한다 — 이력·PR·rulesets가 그대로 남고 예전 URL은 GitHub이 리다이렉트한다.

이번에 바꾸지 않는 것과 이유:
- 설정 키·파일명(gitformat.*, gitformat.conf, .gitformat-verified, _GITFORMAT_AMEND_GUARD): 컨슈머의 git config를 깨는 호환성 변경이라 별건이다. gitformat.conf 개칭을 이미 다루는 GF-133으로 넘긴다.
- 태스크 접두어 GF: 바꾸면 기존 태스크·브랜치·커밋의 Task-Id와 어긋난다. 지난 기록을 다시 쓰는 것은 append-only와 반대다.
- backlog의 지난 decision·doc·task 본문: 당시의 기록이다.
- 로컬 클론 디렉터리 이름: 각자의 환경 문제다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 프로젝트 목적(형식·출처 기록·이력 불변)을 decision-25로 기록하고, decision-11/12의 범위 제외 조항을 대체한다고 명시한다
- [x] #2 decision-25가 decision-24, DRAFT-18/19/20, decision-22, 토큰 측정, AI-Model 게이트, Task-Id 강제, 에디터 금지를 목적 안의 것으로 명시한다
- [x] #3 README의 제목·소개·다루는 범위 섹션이 새 목적과 git-logbook 이름으로 바뀐다
- [x] #4 README의 clone URL이 실제 원격 coralstay/git-logbook을 가리킨다
- [x] #5 install.sh 출력·주석, hooks 주석, .gitmessage, CI 주석, tests의 표시 이름 git-format이 git-logbook으로 바뀐다 (설정 키·파일명 gitformat.*은 제외)
- [x] #6 backlog/config.yml의 project_name이 git-logbook으로 바뀐다
- [x] #7 GF-133에 gitformat.* 설정 키와 마커 파일명을 새 이름으로 옮기는 AC가 추가된다
- [ ] #8 PR을 머지 커밋으로 병합한 뒤 GitHub 저장소를 coralstay/git-logbook으로 rename하고 로컬 origin URL을 갱신한다
- [x] #9 backlog 문서를 decision-25에 맞춘다 — doc-6·doc-7의 'push·서버측 범위 밖' 서술, doc-8 decision 지도(decision-23~25 추가와 decision-11·12·19 상태), doc-1·doc-5·doc-20의 예전 이름·URL
- [x] #10 decision-19의 Signed-off-by 제거 조항이 더 최근 문서(decision-24, DRAFT-19)에 의해 대체됐음을 decision-25에 기록하고, 이를 구현할 GF-128의 AC와 README를 맞춘다
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 python3 -m unittest discover -s tests 전체 통과
- [x] #2 ruff check 통과
- [x] #3 git grep -i git-format -- ':!backlog' 결과에 의도한 예외만 남는다
- [ ] #4 rename 뒤 git ls-remote origin 성공, 예전 URL 리다이렉트 확인
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. decision-25 기록 (AC#1,#2) → 커밋
2. README 제목·소개·범위·clone URL 재작성 (AC#3,#4) → 커밋
3. 나머지 표시 이름 치환: install.sh, hooks 주석, .gitmessage, CI, tests, backlog/config.yml (AC#5,#6) → 테스트 → 커밋
4. GF-133에 설정 키 이전 AC 추가 (AC#7) → 커밋
5. 서브에이전트로 diff 독립 검토
6. PR → CI → 머지 커밋 병합 → gh repo rename → origin URL 갱신 (AC#8)
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
검증: python3 -m unittest 93개 통과, ruff·shellcheck 통과. git grep -i git-format -- ':!backlog'는 README 개명 안내 줄과 tests/isolated_repo.py:1(예전 파일명 언급) 두 곳만 남음 — 둘 다 의도한 예외. 서브에이전트 독립 리뷰 지적 중 AC 범위 안은 반영(decision-25의 pre-rebase 서술 정정, README 원격 보호 범위 과장 정정, install.sh 문구). 유저 지시로 backlog 문서 정리(AC#9)와 Signed-off-by 유지(AC#10, '최근 문서 우선')를 범위에 추가. doc-7의 '[git-format] ts' 출력은 개명 전에 이미 사라진 기능의 실제 출력이라 그대로 둠.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
프로젝트 목적을 형식·출처 기록·이력 불변의 세 기둥으로 재정의(decision-25, decision-11·12의 범위 제외 조항과 decision-19의 Signed-off-by 제거 조항 대체)하고 표시 이름을 git-logbook으로 바꿨다. README·install.sh·훅 주석·테스트·CI·backlog config와 문서 6개를 맞추고, 설정 키 이전은 GF-133, Signed-off-by 유지는 GF-128 AC로 넘겼다. unittest 93개·ruff·shellcheck 통과. AC#8(GitHub 저장소 rename)과 DoD#4는 PR 머지 후에만 가능해 미체크 상태로 Done 처리 — rename 직후 검증하고 체크한다.
<!-- SECTION:FINAL_SUMMARY:END -->
