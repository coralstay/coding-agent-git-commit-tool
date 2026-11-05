---
id: GF-83
title: commit-msg가 subject 길이 / 본문 줄바꿈 폭을 실제로 검증하도록 만들기
status: Done
assignee: []
created_date: '2026-09-03 01:25'
updated_date: '2026-09-03 22:34'
labels: []
dependencies:
  - GF-82
documentation:
  - .gitmessage
  - hooks/commit-msg
ordinal: 81000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
README '한계 및 향후 검토 과제' 항목: .gitmessage는 subject 50자 이내 권장, 본문 72자 줄바꿈 권장이라고 안내하지만, commit-msg 훅은 실제로 길이를 재지 않아 안내가 강제력이 없다. GF-82(커밋 스타일을 [type][subsystem] 프리픽스 + 리누스 토발즈 방식으로 전환)가 서브젝트 형식 자체를 바꾸는 중이므로, 이 작업은 GF-82 완료 후 새 형식을 기준으로 진행한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 subject 길이 초과, 본문 줄 길이 초과 상황에 대한 commit-msg의 동작(거부/경고)이 명확히 정의되고 테스트로 커버된다
- [x] #2 정의된 동작이 .gitmessage와 README 커밋 메시지 규칙 섹션에 정확히 반영된다
- [x] #3 README '한계 및 향후 검토 과제'에서 '실제로 길이를 재지 않는다'는 문구가 제거되거나 실제 동작으로 갱신된다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
구현: hooks/commit-msg에 validate_length() 추가(validate_format 다음, validate_fixes_trailer 이전 순서로 호출). subject 50자/본문 줄 72자 초과 시 거부(exit 1) - 이 훅의 기존 정책(형식/빈줄/Task-Id/AI-Model 전부 거부)과의 일관성 위해 경고가 아닌 거부로 판단. 글자 수는 바이트가 아니라 유니코드 문자 수로 계산(printf | LC_ALL=C.UTF-8 wc -m, 그 호출 시점에만 로케일 override, 스크립트 전역 LC_ALL=C(GF-80)는 유지) - 이 저장소 커밋 이력이 한글 위주라 바이트 기준이면 '50자' 안내와 실제 기준이 크게 어긋남(실측: 한글 48자 제목=66바이트). 본문 줄 검증은 gitformat.conf [gitformat "trailer"]에 등록된 토큰(Task-Id/Fixes/BREAKING CHANGE 등)으로 시작하는 줄을 72자 제한에서 예외 처리 - 이를 위해 기존에 빠져있던 breakingChange = BREAKING CHANGE 항목을 gitformat.conf에 추가(다른 코드/문서는 BREAKING CHANGE를 트레일러로 취급하면서도 중앙 설정에는 없던 gap, 부수적으로 정리). gitformat.conf에 subjectMaxLength=50, bodyLineMaxLength=72 추가(타입 목록과 동일하게 컨슈머 오버레이 없이 CONF 고정값으로 관리 - taskPrefix 같은 로컬 override 레이어는 이 태스크 범위 밖으로 판단). 검증: shellcheck -s sh hooks/commit-msg hooks/pre-commit hooks/post-commit hooks/checks/*.sh install.sh 통과, bats tests/ 전체 94개 통과(1차 시도에서 회귀 2건 발견 후 수정: robustness-commit-msg.bats의 셸메타문자 테스트가 51자 넘는 페이로드라 길이 검증에 먼저 걸려 짧은 파일명으로 수정, robustness-injection.bats의 '매우 긴 라인' 테스트는 목적이 post-commit interpret-trailers 견고성 확인이라 --no-verify로 commit-msg 길이 검증을 우회하도록 수정).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
commit-msg에 validate_length() 함수를 추가해 subject 50자 / 본문 줄 72자 제한을 실제로 검증하고 위반 시 거부(exit 1)하도록 했다 - 이 훅의 다른 모든 규칙(형식/빈줄/Task-Id/AI-Model)이 전부 거부 방식이라 일관성을 위해 경고가 아닌 거부를 선택했다. 글자 수는 바이트가 아니라 유니코드 문자 수 기준(한글 위주인 이 저장소 커밋 관행과 '50자' 안내의 실제 의미에 맞춤). footer 트레일러 줄(gitformat.conf에 등록된 토큰)은 72자 제한에서 예외. .gitmessage/README.md/README.en.md를 갱신해 새 강제 동작을 반영했고, README의 '한계 및 향후 검토 과제'에서 관련 문구를 제거했다. 검증: shellcheck -s sh(전체 훅 대상) 통과, bats tests/ 94개 전체 통과(subject/본문 길이 경계값·유니코드 문자 수·트레일러 예외를 다루는 신규 테스트 7개 포함, 길이 검증 도입으로 목적이 어긋난 기존 테스트 2개 수정).
<!-- SECTION:FINAL_SUMMARY:END -->
