---
id: GF-127
title: 커밋 메시지 검증을 prepare-commit-msg로 이전
status: In Progress
assignee:
  - '@claude'
created_date: '2026-09-25 19:33'
updated_date: '2026-10-04 01:49'
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
구현(0d9df83, a57d038):
- commit-msg의 검증 함수(형식·길이·빈 줄·Fixes·브랜치 Task-Id·AI-Model 게이트, type 목록 비면 중단)를 동작 그대로 prepare-commit-msg로 옮기고 같은 커밋에서 hooks/commit-msg를 삭제했다(AC #9). 오류 메시지 접두어만 prepare-commit-msg:로 바뀌었다.
- 실행 순서: 재생·병합 면제 → 스테일 마커 무효화 → 에디터 경로 거부 → validate_message() → 마커 기록. 무효화를 거부 경로보다 앞에 두어 거부·예외로 끝나면 마커가 남지 않는다(GF-31의 commit-msg finally 정리를 대체).
- 메시지 파일은 주석 제거 전 원문이다. commit-msg와 같게 열 0의 '#' 줄만 빼고 commit.cleanup/core.commentChar는 보지 않는다(-m/-F 경로에서 이 훅과 구 commit-msg가 보는 내용은 같다).
- revert 제목 예외(유저 결정 b): 'Revert "..."'와 'Reapply "..."'를 fullmatch로 인정. git 2.54.0 실측으로 revert의 revert는 'Reapply "<제목>"'이 되므로 함께 넣었다. 중첩은 바깥 따옴표만 보므로 통과한다. 이 제목은 50자 제한에서도 뺀다(git이 원래 제목에 접두어를 붙여 50자 제목의 revert는 60자). 본문 72자·빈 줄 규칙은 그대로 적용.
- --amend 모호성(source=commit)은 알려진 한계로 validate_message() 주석에 남겼다.
- AC #8: 트레일러는 아직 post-commit이 커밋 뒤에 붙이므로 검증이 먼저 돈다. GF-128에서 삽입을 validate_message() 뒤에 둬야 한다고 주석에 적었다.
- 테스트: --no-verify 우회 불가(형식·길이·브랜치), clean revert --no-edit 통과, 60자 revert 제목 통과, Reapply·그 revert 통과, revert 비슷한 손글씨 제목 거부, 거부 시 스테일 마커 제거를 추가. commit-msg 전용 케이스(conf 가드, python3 부재)는 삭제하고, --no-verify로 검증을 피하던 테스트 2개와 Task-Id 없는 브랜치에서 준비 커밋을 만들던 replay 테스트를 고쳤다. install 테스트는 commit-msg 링크가 정리되는지 확인하도록 바꿨다(install.sh 변경 없음).
- 결과: python3 -m unittest discover -s tests → Ran 113 tests OK, ruff check . 통과. 이 저장소의 커밋 0d9df83이 새 훅으로 생성됐고, --no-verify로 형식 틀린 커밋은 거부됐다.
<!-- SECTION:NOTES:END -->

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
