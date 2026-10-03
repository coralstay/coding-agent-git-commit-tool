---
id: GF-128
title: 트레일러 삽입을 prepare-commit-msg로 이전하고 키 단위 중복을 차단
status: To Do
assignee: []
created_date: '2026-09-25 19:33'
updated_date: '2026-10-03 12:48'
labels:
  - hooks
  - trailers
dependencies:
  - GF-127
references:
  - decision-19
  - decision-18
  - decision-25
  - decision-28
documentation:
  - backlog/docs/doc-13 - git-format-재설계-계획-—-커밋-규칙을-prepare-commit-msg로-통합.md
  - backlog/docs/doc-14 - 용어-정리-—-턴-트랜스크립트-귀속-마커-구분.md
  - backlog/docs/doc-18 - 재설계-작업-순서와-의존성.md
modified_files:
  - hooks/prepare-commit-msg
  - hooks/post-commit
  - hooks/gitformat.conf
priority: high
type: feature
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
트레일러가 두 줄씩 붙는 문제가 있다. 실측으로 최근 40커밋 중 Co-Authored-By가 40/40, Task-Id가 12/40 중복이다. 원인은 중복 판정을 git interpret-trailers --parse 출력으로 하는 것인데, 이 명령은 메시지 맨 끝의 연속된 트레일러 블록만 인식해서 빈 줄로 분리된 앞 문단의 트레일러를 보지 못한다. Co-Authored-By는 별도 원인으로, 판정이 키와 값의 완전 일치라서 메시지의 값과 설정의 정규 값이 다르면 새로 추가된다.

메시지 파일에 직접 쓰면 --amend가 사라져 재귀 가드와 rebase 중 실패가 함께 해소된다. 판정 기준도 '키가 있으면 생략'으로 바꿔 사람이 쓴 값을 훅이 덮어쓰지 않게 한다.

트레일러 집합도 이 태스크에서 확정한다 — AI-Tool/AI-Tool-Version/AI-Model을 AI-Agent 한 줄로 합치고, Signed-off-by(커미터 정보는 커밋 객체에 이미 있다)와 Verify-Bypassed(우회가 불가능해져 탐지 대상이 없다)를 없앤다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 트레일러를 git interpret-trailers --in-place로 커밋 메시지 파일에 직접 쓴다 (git commit --amend를 사용하지 않는다)
- [ ] #2 중복 판정은 메시지 원문을 줄 단위로 읽어 해당 키로 시작하는 줄이 있으면 그 키를 건너뛴다
- [ ] #3 메시지에 빈 줄로 분리된 Task-Id 문단이 먼저 있어도 Task-Id가 한 줄만 남는다
- [ ] #4 메시지에 다른 값의 Co-Authored-By가 있으면 훅이 추가하지 않고 원래 값이 보존된다
- [ ] #5 AI-Tool/AI-Tool-Version/AI-Model을 AI-Agent 한 줄(<도구>/<버전> (<모델>))로 합친다
- [ ] #6 AI-Agent는 구성요소를 못 구해도 줄을 남긴다 (version-unavailable / model-unavailable)
- [ ] #7 재귀 가드가 필요 없어져 제거된다
- [ ] #8 git rebase로 커밋을 재생해도 트레일러가 추가되지 않고 훅이 실패하지도 않는다
- [ ] #9 같은 커밋에서 hooks/post-commit을 삭제한다 — 남겨두면 prepare가 넣은 트레일러에 post-commit이 Signed-off-by와 Verify-Bypassed를 또 붙여 이 저장소의 실제 이력에 잘못된 footer가 남는다
- [ ] #10 Verify-Bypassed 트레일러를 더 이상 삽입하지 않는다. Signed-off-by는 계속 삽입한다(decision-25가 decision-19의 제거 조항을 대체)
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 python3 -m unittest 스위트 전체 통과 (이관 전이면 bats tests/ 통과)
- [ ] #2 ruff check 통과
- [ ] #3 이 저장소 자신의 커밋이 새 훅으로 정상 생성되는지 확인
<!-- DOD:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-10-03 03:14
---
2026-10-03: decision-25가 decision-19의 Signed-off-by 제거 조항을 대체했다(더 최근 문서인 decision-24·DRAFT-19가 Signed-off-by를 전제로 한다). 예전 AC#7(Signed-off-by와 Verify-Bypassed 미삽입)을 지우고 Signed-off-by는 유지하는 AC로 다시 적었다. 설명 본문의 'Signed-off-by를 없앤다'는 이 코멘트로 대체된다.
---
<!-- COMMENTS:END -->
