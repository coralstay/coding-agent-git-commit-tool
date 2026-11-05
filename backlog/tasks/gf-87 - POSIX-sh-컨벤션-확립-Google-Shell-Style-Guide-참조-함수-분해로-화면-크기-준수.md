---
id: GF-87
title: 'POSIX sh 컨벤션 확립: commit-msg/post-commit 함수 분해로 화면 크기 준수'
status: Done
assignee: []
created_date: '2026-09-03 11:25'
updated_date: '2026-09-03 12:26'
labels: []
milestone: m-0
dependencies: []
references:
  - decision-14
ordinal: 85000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
훅 파일은 유지하되(훅 1개 = 파일 1개, decision-9의 '훅 간 로직 비공유' 원칙 유지) 화면 크기를 넘는 commit-msg(211줄)/post-commit(224줄)을 함수 단위로 분해해 리뷰어가 한 화면 안에서 각 검증/트레일러 단위를 이해할 수 있게 한다. 외부 스타일 가이드는 저장소에 vendoring하지 않는다(decision-14, decision-9 원칙 복귀) — 컨벤션 판단은 필요할 때마다 참고만 하고 규칙만 적용한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 hooks/commit-msg가 validate_format/validate_fixes_trailer/enforce_task_id_branch/enforce_ai_model_gate 등 이름 있는 함수로 분해되고, 각 함수가 한 화면(약 50줄) 안에 들어온다
- [x] #2 hooks/post-commit이 detect_verify_bypass/trailer_task_id/trailer_ai_attribution/trailer_signed_off_by 등 이름 있는 함수로 분해되고, 각 함수가 한 화면 안에 들어온다
- [x] #3 리팩터 후에도 파일당 정확히 1개 훅이라는 배포 단위는 그대로 유지된다(멀티파일 분리 없음)
- [x] #4 리팩터 후 tests/ 전체 bats 스위트와 shellcheck -s sh가 통과한다
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. hooks/commit-msg를 validate_format/validate_fixes_trailer/enforce_task_id_branch/
   enforce_ai_model_gate 함수로 분해. resolve_self/CONF 가드/TASK_PREFIX-BRANCH 블록은
   post-commit과 텍스트 동일성이 tests/consistency.bats로 보장되므로 함수로 감싸더라도
   들여쓰기까지 정확히 동일하게 유지. (완료)
2. hooks/post-commit을 detect_verify_bypass/trailer_task_id/trailer_ai_attribution/
   trailer_signed_off_by 함수로 분해. 같은 이유로 TASK_PREFIX-BRANCH 블록 들여쓰기를
   commit-msg와 동일하게.
3. tests/consistency.bats의 TASK_PREFIX/BRANCH 블록 추출 awk 패턴을 새 들여쓰기에 맞게 조정
   (텍스트 동일성이라는 불변조건 자체는 유지, 추출 방식만 갱신).
4. shellcheck -s sh + bats tests/ 전체 통과 확인.
5. AC별 커밋.

참고: 초기 계획엔 Google Shell Style Guide vendoring이 있었으나, 라이선스
레이어 리스크 때문에 decision-14로 전면 취소(pro-git 포함 기존 vendoring도
함께 제거). 함수 분해 자체는 vendoring과 무관하게 그대로 진행.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/commit-msg를 validate_format/validate_fixes_trailer/enforce_task_id_branch/enforce_ai_model_gate 4개 함수로, hooks/post-commit을 detect_verify_bypass/trailer_task_id/trailer_ai_tool/trailer_ai_model/trailer_hooks_commit/trailer_signed_off_by 6개 함수로 분해했다(원래 trailer_ai_attribution 하나로 계획했으나 65줄이라 화면 크기 기준을 넘어 trailer_ai_tool/trailer_ai_model 둘로 나눔). 각 함수는 3~44줄로 전부 화면 크기 안에 들어온다. 리팩터 중 POSIX sh 함정을 하나 발견해 고쳤다: 함수 안에서 'set -- "$@" --trailer ...'로 위치 매개변수를 누적하면 함수가 끝날 때 호출자에게 전달되지 않고 원상복구된다 - 그래서 트레일러 누적을 위치 매개변수 대신 전역 변수 TRAILER_QUEUE(queue_trailer 헬퍼)로 바꾸고, 최종 조립(set --)은 함수 밖 톱레벨에서 heredoc(파이프 아님, 서브셸 방지)으로 한 번만 하도록 재설계했다. resolve_self()/CONF 읽기 가드는 두 파일 다 top-level로 남겨 기존 동일성 테스트(tests/consistency.bats)에 영향 없음. TASK_PREFIX/BRANCH 블록은 함수 안으로 들어가며 2칸 들여쓰기가 붙어 tests/consistency.bats의 awk 추출 패턴을 그에 맞게 갱신했다(불변조건 자체는 유지). 훅 파일 수는 그대로(훅 1개=파일 1개 유지, 멀티파일 분리 없음). 검증: shellcheck -s sh 전체 통과, bats tests/ 전체 87개 테스트 통과(trailer 관련 상태전이/결함주입 테스트 포함 - 위 버그가 있었다면 여기서 잡혔을 것).
<!-- SECTION:FINAL_SUMMARY:END -->
