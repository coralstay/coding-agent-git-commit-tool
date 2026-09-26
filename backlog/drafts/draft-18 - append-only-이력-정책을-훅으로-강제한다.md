---
id: DRAFT-18
title: append-only 이력 정책을 훅으로 강제한다
status: Draft
assignee: []
created_date: '2026-09-26 08:30'
updated_date: '2026-09-26 08:30'
labels:
  - hooks
  - policy
dependencies: []
references:
  - decision-24
documentation:
  - backlog/docs/doc-19 - 이력을-바꾸는-git-연산별-훅-판별-방법-실측.md
  - backlog/docs/doc-13 - git-format-재설계-계획-—-커밋-규칙을-prepare-commit-msg로-통합.md
  - backlog/docs/doc-15 - 훅-실행-경로-실측-git-2.54.0.md
priority: high
type: feature
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
decision-24로 이력 정책을 append-only로 정했다. 커밋이 만들어진 뒤에는 그 객체를 다시 만들지 않는다 — 금지선은 커널 문서와 같이 push된 이력에 둔다.

이 태스크는 그 정책을 훅으로 강제한다. 판별 방법은 doc-19에 실측으로 정리돼 있다.

가장 조심할 점: cherry-pick과 rebase는 훅 인자로 구분되지 않는다. source도 상태 파일도 같고 $GIT_DIR/rebase-merge/ 디렉터리 하나만 다르다. 상태 파일만 보고 거부하면 허용해야 할 로컬 rebase까지 막힌다.

부수 효과: merge와 revert는 git이 메시지를 지어주므로(Merge branch ..., Revert "...") [type][subsystem] 규칙에 맞지 않는다. 둘 다 새 커밋이라 트레일러는 붙여야 하고 제목 형식 검사만 예외로 둬야 한다. 이 예외는 검증을 prepare-commit-msg로 옮기는 GF-127에서 함께 구현해야 한다 — 지금은 revert/merge에서 commit-msg가 돌지 않아 드러나지 않는다.

기존 정책과 충돌한다: 로컬 claude-rails 훅이 git merge를 --ff-only 없이 거부하고 있다. 그 훅도 갱신해야 한다(claude-rails 저장소).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 cherry-pick을 거부한다 — CHERRY_PICK_HEAD가 있고 rebase-merge/와 rebase-apply/가 둘 다 없을 때만
- [ ] #2 로컬 rebase 재생은 통과한다 (rebase-merge/ 디렉터리가 있으면 면제) — cherry-pick 차단이 rebase를 막지 않는지 테스트로 고정
- [ ] #3 git commit --amend를 거부한다 (source=commit). post-commit이 내부적으로 쓰는 amend는 _GITFORMAT_AMEND_GUARD로 구분되어 통과한다
- [ ] #4 squash를 거부한다 (source=squash 또는 SQUASH_MSG)
- [ ] #5 hooks/pre-rebase를 신설해 이미 push된 커밋을 다시 쓰는 rebase를 거부한다 — git rev-list <upstream>..HEAD의 커밋 중 하나라도 git branch -r --contains에 걸리면 거부
- [ ] #6 push되지 않은 로컬 rebase는 pre-rebase를 통과한다
- [ ] #7 revert는 통과하고 트레일러가 붙는다 — append-only의 되돌리기 수단이다
- [ ] #8 merge 커밋은 통과하고 트레일러가 붙는다
- [ ] #9 거부 메시지가 왜 막혔는지와 대신 무엇을 쓰라는지 안내한다 (cherry-pick 대신 merge, amend 대신 새 커밋)
- [ ] #10 README에 append-only 정책과 연산별 허용/거부를 표로 적는다
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 python3 -m unittest 스위트 전체 통과
- [ ] #2 ruff check 통과
- [ ] #3 이 저장소 자신의 커밋이 정상 생성되는지 확인
- [ ] #4 claude-rails의 --ff-only 강제 훅을 갱신해야 한다는 점을 그쪽 저장소에 드래프트로 남긴다
<!-- DOD:END -->
