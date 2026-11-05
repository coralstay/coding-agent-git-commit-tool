---
id: GF-81
title: checks/cpp.sh 확장자 목록이 루트 파일명으로 글롭 확장돼 하위 디렉터리 파일이 검사에서 누락됨
status: Done
assignee:
  - '@coralstay'
created_date: '2026-08-28 14:54'
updated_date: '2026-08-28 14:59'
labels: []
dependencies: []
ordinal: 79000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`hooks/checks/cpp.sh`는 `gitformat.conf`의 다중값 `gitformat.cpp.ext`(`*.c *.cc *.cpp *.cxx *.h *.hpp *.hh`)를
따옴표 없이 `$(git config ... --get-all gitformat.cpp.ext)`로 펼쳐 `git diff --cached -- ...`에 넘긴다(주석 의도:
"다중값 확장자 목록을 그대로 인자로 펼친다", `shellcheck disable=SC2046`).

문제는 이 명령 치환이 word splitting 뒤에 pathname expansion(실제 파일시스템 글롭)까지 같이 겪는다는 점이다.
cpp.sh는 그 시점에 이미 `cd "$REPO_ROOT"` 상태이므로, 저장소 루트에 그 확장자와 매치되는 파일이 하나라도 있으면
해당 글롭 토큰이 "그 파일명 하나"로 셸에 의해 먼저 치환돼버린다. 그 결과 git에 전달되는 pathspec이
"트리 전체의 `*.cpp`"가 아니라 "루트의 특정 파일 하나"로 좁아져, 하위 디렉터리에 있는 같은 확장자 파일은
스테이징돼 있어도 clang-format 검사 대상에서 통째로 빠진다.

실측 재현: 루트에 정상 포맷 `root.cpp`, `src/deep.cpp`에 clang-format 위반 코드를 만들어 같이 스테이징 후 실제
훅으로 커밋 → exit 0으로 통과함(FILELIST에 `root.cpp`만 담기고 `src/deep.cpp`는 아예 안 잡힘). 기존
`tests/checks-cpp.bats` 픽스처는 항상 루트에 파일이 하나뿐이라 우연히 이 문제를 피해가서 지금까지 안 걸렸다.

`sql.sh`는 확장자가 하나뿐이라 `'*.sql'`을 따옴표로 감싸 써서 이 문제가 없다(`SC2046` disable은 코드
전체에서 cpp.sh 이 한 곳뿐).

영향 범위: 로컬 pre-commit뿐 아니라 opt-in GitHub Actions 백스톱(`verify.yml`)도 내부적으로 동일한
`hooks/pre-commit` → `checks/cpp.sh` 경로를 그대로 재사용하므로 서버사이드 백스톱도 동일하게 뚫린다. 루트에
`main.cpp`나 헤더 파일 하나만 있어도(흔한 CMake 프로젝트 레이아웃) 하위 디렉터리 C/C++ 파일의 포맷 검사가
조용히 무력화된다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 루트와 하위 디렉터리에 동시에 스테이징된 C/C++ 파일이 있을 때, 하위 디렉터리 파일의 clang-format 위반도 정상적으로 커밋을 차단한다
- [x] #2 gitformat.cpp.ext 값이 git diff pathspec으로 전달될 때 셸의 pathname expansion(파일시스템 글롭)을 겪지 않는다
- [x] #3 기존 GF-36(공백 파일명)/GF-37(rename 파일) 동작은 회귀 없이 그대로 유지된다
- [x] #4 tests/checks-cpp.bats에 루트+하위 디렉터리 동시 스테이징 케이스에 대한 회귀 테스트가 추가된다
- [x] #5 shellcheck -s sh 게이트를 통과한다
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. hooks/checks/cpp.sh의 46-54행을 수정: gitformat.cpp.ext 값을 개행 단위로 읽어 `set --`로 위치 인자에 하나씩 누적(post-commit의 트레일러 누적 패턴과 동일 기법)한 뒤, git diff --cached에는 "$@"로 따옴표 유지한 채 전달한다. 이렇게 하면 word splitting은 되지만 각 토큰이 개별 인자로 quoting된 상태로 남아 pathname expansion(파일시스템 글롭)을 겪지 않는다.
2. SC2046 shellcheck disable 주석은 더 이상 필요 없으므로 제거한다 - 수정 후에는 unquoted glob expansion이 없으므로 SC2046이 발생하지 않아야 한다(shellcheck로 확인).
3. tests/checks-cpp.bats에 회귀 테스트 추가: 루트에 정상 포맷 cpp 파일 + src/ 하위 디렉터리에 clang-format 위반 cpp 파일을 함께 스테이징 후 커밋이 차단되는지 확인(GF-81).
4. 기존 GF-36(공백 파일명)/GF-37(rename) 테스트가 회귀 없이 통과하는지 재확인.
5. shellcheck -s sh hooks/checks/cpp.sh 통과 확인.
6. bats tests/ 전체 재실행(88+1개) 통과 확인.
7. GF-81 브랜치(예: GF-81-cpp-ext-glob-fix)를 만들어 커밋 → main으로 fast-forward 병합(레포 관례: git log상 과거 GF-* 수정 커밋들이 전부 Task-Id 트레일러를 갖고 있어 브랜치명에 Task-Id 패턴이 있어야 commit-msg 훅과 post-commit 트레일러 삽입이 정상 동작함을 확인함).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
수정: hooks/checks/cpp.sh의 git diff pathspec 인자 구성을 $(...) 직접 펼치기에서 set -- 누적(POSIX sh 배열 흉내, post-commit 트레일러 누적과 동일 기법)으로 교체 - word splitting은 유지하되 pathname expansion(파일시스템 글롭)은 겪지 않게 함.
검증: (1) 수동 재현 - 수정 전에는 루트 root.cpp + src/deep.cpp(포맷 위반) 동시 스테이징 시 exit 0으로 통과(버그 확인), 수정 후 동일 시나리오에서 실제 clang-format이 src/deep.cpp를 잡아 exit 1로 정상 차단됨을 실제 커밋으로 확인.
(2) tests/checks-cpp.bats에 회귀 테스트 추가(루트+하위 디렉터리 동시 스테이징) - bats tests/checks-cpp.bats 6/6 통과.
(3) bats tests/ 전체 89/89 통과(회귀 없음, GF-36/GF-37 케이스 포함).
(4) shellcheck -s sh hooks/commit-msg hooks/pre-commit hooks/pre-push hooks/post-commit hooks/checks/*.sh install.sh 통과(exit 0) - SC2046 disable 주석 제거됨(더 이상 unquoted glob 확장이 없어 불필요).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
checks/cpp.sh가 gitformat.cpp.ext 다중값 확장자 목록을 $(...)로 따옴표 없이 펼기던 부분을, set --로 값을 하나씩 따옴표 유지한 채 누적하는 방식으로 교체했다. 기존 코드는 word splitting과 함께 셸의 pathname expansion까지 겪어, 저장소 루트에 그 확장자와 매치되는 파일이 있으면 git diff pathspec이 "트리 전체 *.cpp"가 아니라 "루트의 그 파일 하나"로 좁아져 하위 디렉터리 C/C++ 파일이 clang-format 검사에서 조용히 누락됐다(로컬 pre-commit과 opt-in GitHub Actions 백스톱 verify.yml 둘 다 영향). 수동 재현으로 버그와 수정 모두 확인했고, tests/checks-cpp.bats에 회귀 테스트를 추가했다. bats 89/89, shellcheck -s sh 전부 통과.
<!-- SECTION:FINAL_SUMMARY:END -->
