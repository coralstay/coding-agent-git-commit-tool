---
id: GF-86
title: 'pre-push 훅(테스트/전체 빌드 실행) 제거 - 무거운 검사는 프로젝트 범위 밖, README 반영'
status: Done
assignee: []
created_date: '2026-09-03 11:10'
updated_date: '2026-09-03 12:05'
labels: []
dependencies: []
references:
  - decision-12
  - decision-11
documentation:
  - README.md
  - README.en.md
ordinal: 84000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
사용자 판단: pre-push가 하던 테스트/전체 빌드 실행(npm test/build, pytest, mvn verify, cmake+ctest, sqlfluff 전체 lint)은 git-format의 스코프에 맞지 않는다. decision-11은 서버사이드(GitHub Actions) 백스톱만 범위에서 뺐고 hooks/pre-push 자체는 '여전히 제공하는 것'이라 명시했었는데, 이번 결정은 그 판단을 대체해 pre-push 훅 자체를 완전히 제거한다. git-format은 이제 commit-msg/pre-commit/post-commit(커밋 단계)까지만 다루고 push 단계는 전혀 훅하지 않는다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 hooks/pre-push 파일이 삭제된다
- [x] #2 hooks/gitformat.conf의 buildDir 키(pre-push 전용)가 제거된다
- [x] #3 install.sh의 .gitformat-build/ 자동 .gitignore 추가 로직(pre-push 산출물 보호용)이 제거된다
- [x] #4 README.md/README.en.md가 pre-push 제거 상태와 일치하도록 갱신된다 (실제 사용법의 push 워크플로 섹션, 훅이 하는 일 표, SQL 섹션의 전체-lint 문구, 저장소 구조 트리, 한계 섹션의 --no-verify/push 서술, 왜 만들었나 섹션의 커밋/푸시 전 검사 문구)
- [x] #5 decision-12(Context/Decision/Consequences)가 작성되어 decision-11의 'pre-push는 여전히 제공한다' 판단을 이 결정이 대체함을 명시한다
- [x] #6 삭제/변경 후 tests/ 전체 bats 스위트와 shellcheck -s sh가 통과한다 (pre-push를 참조하는 conf-guard.bats/robustness-dispatch.bats/consistency.bats/robustness-install.bats의 관련 테스트 삭제·수정 포함)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. hooks/pre-push 삭제
2. hooks/gitformat.conf에서 buildDir 키 제거
3. install.sh에서 .gitformat-build/ 자동 .gitignore 추가 블록(MARKER_CPP/MARKER_CPP_MAKE/BUILD_DIR_NAME 관련) 제거
4. decision-12 본문(Context/Decision/Consequences) 작성 - decision-11의 'pre-push는 여전히 제공' 판단을 대체함을 명시
5. README.md/README.en.md 갱신: 실제 사용법 push 섹션, 훅 표, SQL 섹션, .gitformat-build 관련 행/문구, 저장소 구조 트리, 한계 섹션, 왜 만들었나 섹션
6. tests/conf-guard.bats: pre-push 테스트 삭제
7. tests/robustness-dispatch.bats: pre-push 테스트 2개 + 헤더 주석 수정
8. tests/consistency.bats: resolve_self 파일목록/CONF가드 파일목록에서 pre-push 제거, python_marker_found pre-commit/pre-push 비교 테스트 전체 삭제
9. tests/robustness-install.bats: template/hooks/pre-push 심볼릭링크 검증 삭제, .gitformat-build 자동 gitignore 테스트 블록 전체 삭제
10. bats tests/ 전체 + shellcheck -s sh 통과 확인
11. AC별로 커밋
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/pre-push를 삭제하고 gitformat.conf의 buildDir 키, install.sh의 .gitformat-build 자동 .gitignore 블록을 제거했다. decision-12에 Context/Decision/Consequences를 작성해 decision-11의 'pre-push는 여전히 제공' 판단을 대체함을 명시했다. README.md/README.en.md의 실제 사용법(push 섹션 제거), 훅 표, SQL 섹션, .gitformat-build 관련 행/문구, 저장소 구조 트리, 한계 섹션, 왜 만들었나 섹션을 갱신했다. tests/conf-guard.bats·robustness-dispatch.bats·consistency.bats·robustness-install.bats에서 pre-push/.gitformat-build 관련 테스트를 삭제·수정했고, checks/java.sh·cpp.sh의 pre-push 참조 주석도 갱신했다. 검증: shellcheck -s sh 전체 통과(exit 0), bats tests/ 전체 87개 테스트 통과(exit 0).
<!-- SECTION:FINAL_SUMMARY:END -->
