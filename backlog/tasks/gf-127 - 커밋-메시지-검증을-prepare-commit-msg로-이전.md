---
id: GF-127
title: 커밋 메시지 검증을 prepare-commit-msg로 이전
status: In Progress
assignee:
  - '@claude'
created_date: '2026-09-25 19:33'
updated_date: '2026-10-04 01:39'
labels:
  - hooks
  - validation
dependencies:
  - GF-126
references:
  - decision-18
documentation:
  - backlog/docs/doc-13 - git-format-재설계-계획-—-커밋-규칙을-prepare-commit-msg로-통합.md
  - backlog/docs/doc-14 - 용어-정리-—-턴-트랜스크립트-귀속-마커-구분.md
  - backlog/docs/doc-18 - 재설계-작업-순서와-의존성.md
modified_files:
  - hooks/prepare-commit-msg
  - hooks/commit-msg
priority: high
type: feature
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
메시지 형식 검증은 지금 commit-msg가 담당하고, --no-verify로 건너뛸 수 있다. prepare-commit-msg로 옮기면 우회가 불가능해진다.

검증은 트레일러 삽입보다 먼저 돌아야 한다 — 사람이 쓴 부분만 검증하고 훅이 만든 트레일러는 검증 대상이 아니다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 제목이 [type][subsystem] <설명> 형식인지 검증한다 (subsystem은 생략 가능)
- [ ] #2 제목이 50자를 넘으면 거부한다 (바이트가 아니라 유니코드 코드포인트 기준)
- [ ] #3 본문 줄이 72자를 넘으면 거부하되, 등록된 트레일러 토큰으로 시작하는 줄은 예외로 둔다
- [ ] #4 본문이나 트레일러가 있으면 제목과의 사이에 빈 줄을 요구한다
- [ ] #5 Fixes 트레일러가 있으면 참조 해시가 저장소에 실재하는 커밋인지 검증한다
- [ ] #6 브랜치명에 <prefix>-<번호> 패턴이 없으면 거부하되 예외 브랜치와 detached HEAD는 면제한다
- [ ] #7 커밋 타입 목록을 설정 파일에서 읽으며, 목록이 비면 조용히 통과하지 않고 원인을 밝히며 중단한다
- [ ] #8 검증이 트레일러 삽입보다 먼저 실행된다
- [ ] #9 같은 커밋에서 hooks/commit-msg를 삭제한다 — 기능을 옮기고 구 훅을 남기면 검증이 두 번 실행된다
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 python3 -m unittest 스위트 전체 통과 (이관 전이면 bats tests/ 통과)
- [ ] #2 ruff check 통과
- [ ] #3 이 저장소 자신의 커밋이 새 훅으로 정상 생성되는지 확인
<!-- DOD:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: claude
created: 2026-09-26 02:35
---
GF-125에서 발견한 위험 — 이 태스크 착수 전에 방침을 정해야 한다 (2026-09-26 실측, doc-15 정정 반영).

clean `git revert --no-edit`은 면제 조건에 걸리지 않는다:
- source가 `message`다 (`merge`/`squash` 아님)
- `REVERT_HEAD`가 **없다** — 이 파일은 revert가 충돌로 멈췄을 때만 생긴다
- `MERGE_MSG`만 존재한다

실측 로그: `source=[message] MERGE_MSG msg=[Revert "[feat] base commit"]`

즉 prepare-commit-msg의 재생 커밋 면제(GF-125 AC #1)를 통과해 일반 경로로 흘러간다.
그런데 git이 만드는 메시지 `Revert "[feat] base commit"`은 제목 규칙
`[type][subsystem] <설명>`에 맞지 않는다.

**지금은 revert 경로에서 commit-msg가 돌지 않아 드러나지 않는다.** 이 태스크가 검증을
prepare-commit-msg로 옮기는 순간 clean revert가 전부 거부된다. 기존 동작과 달라지는
회귀이므로 의도적으로 결정해야 한다.

선택지:
(a) MERGE_MSG 존재를 면제 조건에 추가한다 — 다만 MERGE_MSG는 cherry-pick에도 있어
    면제 범위가 넓어진다
(b) `Revert "..."` 형식을 제목 규칙의 예외로 인정한다 — conf의 type 목록에 이미
    revert가 있으나 git 자동 메시지는 대괄호 형식이 아니다
(c) revert 시 사용자가 `-m`으로 규칙에 맞는 메시지를 직접 주도록 요구한다

함께 결정할 것: 같은 태스크에 걸린 --amend 모호성(GF-125 코멘트 #1) — source=commit이
--amend --no-edit(최종 메시지)과 --amend(뒤에 에디터 열림)를 구분하지 못한다.
---

author: @claude
created: 2026-10-04 01:39
---
2026-10-04 유저 결정: clean revert 문제는 (b)로 간다 — git이 만드는 'Revert "..."' 제목을 제목 규칙의 예외로 인정한다. 면제(a)는 cherry-pick까지 넓어지고, (c)는 git 기본 동작을 막는다. --amend 모호성(source=commit)은 이 태스크에서 해결하지 않고 알려진 한계로 남긴다.
---
<!-- COMMENTS:END -->
