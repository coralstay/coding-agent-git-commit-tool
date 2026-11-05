---
id: GF-82
title: 'commit-msg 서브젝트를 [type][subsystem] 프리픽스로 전환 + 토발즈 스타일 트레일러/빈줄 규칙 도입'
status: Done
assignee: []
created_date: '2026-09-03 01:13'
updated_date: '2026-09-03 06:46'
labels: []
dependencies: []
references:
  - backlog/decisions/decision-1 - Conventional-Commits-채택.md
documentation:
  - .gitmessage
  - README.md
  - README.en.md
  - hooks/commit-msg
  - hooks/post-commit
ordinal: 80000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Conventional Commits의 `type(scope)!:` 서브젝트 형식을 `[type][subsystem]` 대괄호 프리픽스로 바꾸고, BREAKING CHANGE `!` 마커를 제거한다. 본문이 있으면 제목-본문 사이 빈 줄을 훅에서 강제한다. post-commit이 모든 커밋에 Signed-off-by 트레일러를 커미터 정보로 자동 삽입한다(git commit -s와 동일한 방식, DCO 스타일). Fixes: <hash> 트레일러는 강제하지 않되, 존재하면 참조 해시가 실제 커밋인지 검증한다. decision-1(Conventional Commits 채택)을 대체하는 새 decision을 기록한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 commit-msg가 [type][subsystem] description 형식(subsystem 대괄호는 선택)을 검증하고, 기존 type(scope): 콜론 형식과 ! breaking-change 마커는 더 이상 허용하지 않는다
- [x] #2 본문(3번째 이후 내용)이 있는데 2번째 줄이 빈 줄이 아니면 commit-msg가 거부한다
- [x] #3 Fixes: 트레일러가 있으면 참조 해시가 저장소에 실재하는 커밋인지 검증하고, 존재하지 않으면 거부한다 - 트레일러 자체는 강제하지 않는다
- [x] #4 post-commit이 모든 커밋에 Signed-off-by 트레일러를 커미터 정보(git log -1 --format='%cn <%ce>')로 자동 삽입한다(이미 있으면 건너뜀)
- [x] #5 .gitmessage, README.md, README.en.md가 새 서브젝트 형식/Fixes/Signed-off-by 규칙을 반영한다
- [x] #6 decision-1을 대체하는 새 decision이 기록되고 decision-1 파일 자체는 직접 수정하지 않는다
- [x] #7 tests/robustness-commit-msg.bats, tests/consistency.bats가 새 형식에 맞게 갱신되고 전체 bats 스위트와 shellcheck -s sh가 통과한다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
구현: hooks/commit-msg 서브젝트 정규식을 [type][subsystem] 형식으로 교체(! 마커 제거), 빈 줄 강제(2번째 non-comment 줄이 비어있지 않으면 거부), Fixes: 트레일러 해시를 git rev-parse --verify로 검증. hooks/post-commit이 모든 커밋에 Signed-off-by를 커미터 정보로 자동 삽입(git commit -s 방식). gitformat.conf에 trailer.signedOffBy/trailer.fixes 키 추가. .gitmessage/README.md/README.en.md를 새 형식으로 갱신, Conventional Commits 배지 제거. decision-10을 생성해 decision-1을 대체(파일 자체는 미수정). 검증: bats tests/ 95/95 통과, shellcheck -s sh 전부 통과(둘 다 최종 커밋 상태에서 재확인). 커밋 5개로 분리: gitformat.conf 키 추가 / commit-msg+post-commit+전체 테스트 스위트 갱신 / .gitmessage+README 갱신 / decision-10 기록 / (범위 밖) GF-83·GF-84 백로깅. 서브젝트 형식은 새 규칙 자체를 적용해 커밋함(dogfooding).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
커밋 메시지 서브젝트를 Conventional Commits(type(scope)!:)에서 리누스 토발즈 스타일 [type][subsystem] 프리픽스로 전환했다. 빈 줄 강제, Fixes: 해시 검증, post-commit의 Signed-off-by 자동삽입을 hooks/commit-msg·hooks/post-commit에 추가했고, .gitmessage/README.md/README.en.md를 새 형식으로 갱신했다. decision-10을 생성해 decision-1(Conventional Commits 채택)을 대체했다(원본 파일은 미수정, 프로젝트 관례대로 과거 기록으로 보존). 검증: bats tests/ 95/95 통과(신규 회귀 테스트 8개 포함: 빈 줄 강제 2개, Fixes 검증 3개, Signed-off-by 자동삽입 1개, ! 마커 거부 1개, 목록 갱신 등), shellcheck -s sh 전부 통과. 이 태스크 자체의 커밋 5개도 새 [type][subsystem] 형식을 그대로 적용해 작성했다.
<!-- SECTION:FINAL_SUMMARY:END -->
