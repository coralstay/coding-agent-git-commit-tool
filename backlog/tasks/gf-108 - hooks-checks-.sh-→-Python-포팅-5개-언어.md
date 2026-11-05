---
id: GF-108
title: hooks/checks/*.sh → Python 포팅 (5개 언어)
status: Done
assignee:
  - '@claude'
created_date: '2026-09-24 09:23'
updated_date: '2026-09-24 13:42'
labels:
  - python-migration
  - hooks
  - checks
milestone: m-3
dependencies: []
references:
  - DRAFT-16
documentation:
  - doc-9
  - doc-10
modified_files:
  - hooks/checks/python.py
  - hooks/checks/ts.py
  - hooks/checks/java.py
  - hooks/checks/cpp.py
  - hooks/checks/sql.py
  - .gitignore
  - hooks/pre-commit
  - tests/checks-python.bats
  - tests/checks-ts.bats
  - tests/checks-java.bats
  - tests/checks-cpp.bats
  - tests/checks-sql.bats
type: enhancement
ordinal: 2
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## 왜

언어별 체크 스크립트 5개는 서로 코드를 공유하지 않아 독립적으로 포팅 가능하고, 가장 작아서(python.sh는 18줄) 전체 전환의 패턴을 먼저 검증하기 좋다. git이 직접 실행하는 파일이 아니라 pre-commit이 호출하는 스크립트라 인터프리터 PATH 탐색 문제도 없다 - pre-commit이 sys.executable로 자신을 실행 중인 인터프리터 경로를 그대로 넘겨 호출한다.

## 무엇을

hooks/checks/{python,ts,java,cpp,sql}.sh를 각각 .py로 포팅한다. sh 시절의 우회 기법 중 Python에서 불필요해지는 것은 정당하게 단순화한다:
- ts: package.json의 scripts.lint 확인을 node -e 셸아웃 대신 json.load()로 직접 파싱. 단 tsc 우선순위(로컬 node_modules/.bin/tsc > PATH, npx 금지 - GF-79)는 그대로 유지
- cpp/sql: git diff --cached -z 출력을 \0로 split. mktemp + xargs -0 우회가 필요 없어진다
- 모든 subprocess.run에 encoding="utf-8" 명시(로케일 의존 디코딩으로 GF-80 성격의 버그가 재현되는 것 방지)
- git config --get이 빈 값도 성공 취급하는 문제(GF-35)는 빈 문자열 명시 체크로 이식

## 선행/병렬

선행 조건 없음. 5개 체크 스크립트는 서로 코드를 공유하지 않아 완전히 병렬로 진행 가능하다. 이 태스크의 완료가 GF-110(pre-commit)의 선행 조건이다 - pre-commit 디스패처가 .py 파일명을 직접 참조하기 때문.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 hooks/checks/python.py가 ruff check . 우선, 없으면 flake8 . 폴백, 둘 다 없으면 조용히 스킵하는 기존 동작 그대로 포팅되고 bats tests/checks-python.bats가 통과한다
- [x] #2 hooks/checks/ts.py가 package.json의 scripts.lint를 json.load()로 직접 파싱하고(node -e 셸아웃 제거), 로컬 node_modules/.bin/tsc를 PATH보다 우선하며 npx를 쓰지 않는다(GF-79). bats tests/checks-ts.bats 통과
- [x] #3 hooks/checks/java.py가 pom.xml이면 mvn -q compile, build.gradle*이면 ./gradlew -q compileJava를 실행하는 기존 동작으로 포팅되고 bats tests/checks-java.bats가 통과한다
- [x] #4 hooks/checks/cpp.py가 git diff --cached -z 출력을 NUL로 split해 공백 포함 파일명을 안전하게 처리하고(mktemp/xargs -0 우회 제거), 확장자 목록을 gitformat.conf에서 읽으며 bats tests/checks-cpp.bats가 통과한다
- [x] #5 hooks/checks/sql.py가 동일한 NUL-split 방식으로 스테이징된 .sql 파일을 sqlfluff lint에 넘기고 .sqlfluff 부재 시에만 --dialect를 붙이며 bats tests/checks-sql.bats가 통과한다
- [x] #6 5개 파일 전부 모든 subprocess.run 호출에 encoding=utf-8이 명시되고, git config --get의 빈 값 성공 취급(GF-35)에 대한 빈 문자열 명시 체크가 이식된다
- [x] #7 tests/checks-*.bats 내부에 hooks/checks/*.sh 경로 하드코딩이 있는지 파일을 직접 열어 확인하고 .py로 갱신한다
- [x] #8 .gitignore에 __pycache__/ 와 *.pyc가 추가된다
- [x] #9 구 .sh 체크 스크립트를 삭제하기 전에 아직 sh인 hooks/pre-commit의 디스패치 경로를 .py로 갱신해, 어느 중간 커밋에서도 훅 체인이 깨지지 않는다
- [x] #10 구 .sh 삭제로 깨지는 AC 밖 3개 파일을 최소 수정으로 함께 고친다(유저 승인, 2026-09-24): .github/workflows/test.yml의 shellcheck 대상에서 hooks/checks/*.sh 제거, tests/conf-guard.bats의 checks 3건을 python3 .py 호출로 교체, tests/consistency.bats의 resolve_self/conf가드 파일 목록에서 checks 항목 제거(파이썬 쪽 동일성 검사 설계는 GF-112 소관)
- [x] #11 추가 승인 범위(유저 승인, 2026-09-24): tests/robustness-dispatch.bats의 GF-16 케이스에 asdf python 버전 지정을 추가해(checks-ts.bats의 ASDF_NODEJS_VERSION과 동일 방식) 이 테스트만 HOME을 바꾸는 탓에 로컬에서 python3 셈이 해석되지 않던 문제를 없앤다
- [x] #12 추가 승인 범위(유저 승인, 2026-09-24): 훅 소스를 텍스트로 떠서 사본끼리 비교하던 구현 언어 종속 검사 3건(consistency.bats의 resolve_self·TASK_PREFIX/BRANCH·conf 읽기 가드 동일성)을 삭제하고 행위 검증 테스트만 남긴다. AC #10의 'consistency.bats 목록에서 checks 항목만 제거' 방침을 대체하며, GF-112가 예정했던 Python 쪽 동일성 검사 설계도 함께 불필요해진다
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 해당 AC 범위의 bats 서브셋이 통과한다
- [ ] #2 CI(shellcheck + ruff)가 초록이다
- [x] #3 변경 파일이 AC 범위를 벗어나지 않는다 - 범위 밖 작업 발견 시 유저에게 먼저 확인한다
- [x] #4 커밋이 [type][subsystem] 규칙과 Task-Id 트레일러를 만족한다
- [x] #5 Done 전환 전 final summary에 객관적 검증 증거(테스트 통과 로그 등)를 남긴다
- [x] #6 새 코드에 불필요한 주석을 넣지 않는다 - WHY가 비자명한 경우(GF-33/34/35/76/80 회귀 방지 패턴, 의도적 fail-open, 의도적 중복 유지 등)에만 한 줄 주석을 남긴다
- [x] #7 PR은 rebase-merge로만 머지하고(squash/merge-commit 금지), push·PR 생성·머지 각 단계 전에 git fetch로 원격 상태를 먼저 확인한다(트렁크 방식이 아니라 로컬/리모트가 어긋날 수 있음)
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
5개 파일은 서로 독립이라 순서는 자유지만, 가장 단순한 python.py로 공통 패턴을 먼저 확정한 뒤 나머지에 적용한다.

1. hooks/checks/python.py: 원본 18줄 이식(ruff → flake8 폴백 → 조용한 스킵). shutil.which로 도구 존재 확인, subprocess.run(..., encoding="utf-8"). 이 파일에서 나머지 4개에 공통 적용할 패턴(인자 처리, 종료 코드 전달, conf 읽기 방식)을 확정한다
2. hooks/checks/ts.py: json.load()로 package.json의 scripts.lint 확인. tsc는 node_modules/.bin/tsc → shutil.which("tsc") 순서, npx 금지(GF-79)
3. hooks/checks/java.py: pom.xml이면 mvn -q compile, build.gradle* glob이면 ./gradlew -q compileJava
4. hooks/checks/cpp.py: `git diff --cached -z` 출력을 split("\0"), 확장자 목록은 git config --file --get-all로 gitformat.conf에서 읽음
5. hooks/checks/sql.py: 동일한 NUL-split, .sqlfluff 부재 시에만 --dialect 부여
6. 각 파일 작성 직후 대응 bats 실행(checks-python/ts/java/cpp/sql.bats)
7. tests/checks-*.bats를 직접 열어 .sh 경로 하드코딩을 확인하고 .py로 갱신
8. **구 .sh 삭제 전에 아직 sh인 hooks/pre-commit의 디스패치 경로를 .py로 갱신한다** - 이 순서를 지키지 않으면 GF-110이 끝나기 전까지 중간 커밋들에서 훅 체인이 깨진다
9. .gitignore에 __pycache__/ 와 *.pyc 추가
10. 구 hooks/checks/*.sh 5개 삭제(내용이 전부 바뀌므로 git mv가 아니라 신규 작성 후 삭제)

11. (유저 승인 범위 확장) .github/workflows/test.yml shellcheck 인자에서 hooks/checks/*.sh 제거 - 글롭이 매치 0개가 되면 shellcheck가 실패한다
12. tests/conf-guard.bats의 checks/{cpp,java,sql}.sh 실행 3건을 python3 checks/*.py 실행으로 교체
13. tests/consistency.bats의 resolve_self 6개 사본 목록과 conf 가드 7개 파일 목록에서 checks의 .sh 3개를 제거(Python은 realpath를 쓰므로 resolve_self 자체가 없음)
14. 전체 bats 스위트와 ruff로 검증
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
진행 상태(세션 중단 대비, 2026-09-24): 브랜치 task/GF-108, 작업트리 클린, 구현 미착수. 서브에이전트에 5개 .sh → .py 포팅 + 호출부 수정(pre-commit 디스패치, conf-guard.bats 3건, consistency.bats 목록/제목 카운트, test.yml shellcheck 인자, .gitignore, 구 .sh 삭제) 위임함. 세션이 한도로 끊기면: git status로 서브에이전트가 남긴 커밋/변경을 먼저 확인하고, 남은 부분부터 이어서 진행할 것. 결정사항 - checks/*.py는 셔뱅+실행비트를 갖고 아직 sh인 pre-commit이 직접 실행한다(sys.executable 전환은 GF-110 소관).

구현 완료(65f52e9). 검증 증거:
- bats checks-python/cpp/sql + conf-guard + consistency: 25/25 통과
- bats checks-ts: 7/7 통과 (실제 npm/tsc)
- bats checks-java: 3/3 통과 (실제 mvn, 온라인)
- bats smoke/robustness-dispatch/injection/install: 19건 중 18 통과
- ruff check hooks/checks/: All checks passed
- shellcheck -s sh hooks/commit-msg hooks/pre-commit hooks/post-commit install.sh: 클린

남은 실패 1건(AC 밖, 유저 확인 대기): tests/robustness-dispatch.bats의
'[GF-16 회귀] template/ 심볼릭 링크...'. 이 테스트만 HOME을 가짜 임시
디렉터리로 바꾸는데, 로컬 python3가 asdf shim이라 .tool-versions를 못 찾아
'No version is set for command python3'로 죽는다. 훅 코드 문제가 아니라
tests/checks-ts.bats가 ASDF_NODEJS_VERSION으로 이미 우회해 둔 것과 같은
종류의 로컬 테스트 환경 이슈다(CI의 ubuntu-latest는 /usr/bin/python3라 무관).

포팅 중 판단한 것:
- checks/*.py는 셔뱅+실행비트를 갖고 아직 sh인 pre-commit이 직접 실행한다.
  sys.executable 전달은 pre-commit이 Python이 되는 GF-110 소관.
- cpp/sql의 git diff -z 읽기에 AC #6대로 encoding=utf-8을 명시했다. 이러면
  subprocess가 텍스트 모드가 되어 universal newlines 변환이 걸리므로,
  파일명에 CR이 들어있으면 LF로 바뀐다(구 sh는 바이트 그대로 넘겼다).
  UTF-8이 아닌 파일명은 디코딩 에러가 된다. 둘 다 병적인 경우라 AC를
  그대로 따랐다.
- xargs -0를 없애면서 clang-format/sqlfluff 호출이 한 번의 exec이 됐다.
  파일 수가 아주 많으면 ARG_MAX에 걸릴 수 있다(xargs는 배치로 나눠줬다).

최종 검증(전체 스위트, 2026-09-24):
- bats tests/ : 100/100 통과, 실패 0 (언어 종속 검사 3건 삭제 전에는 103/103)
- ruff check hooks/checks/ : All checks passed
- shellcheck -s sh hooks/commit-msg hooks/pre-commit hooks/post-commit install.sh : 클린
- AC #6 기계 검증: hooks/checks/*.py의 subprocess.run 16개 전부에 encoding=utf-8이
  붙어 있음을 파싱 스크립트로 확인(누락 0)

AC #12(언어 종속 테스트 삭제)로 지운 3건은 모두 행위 검증 쪽에 대응이 있다:
resolve_self는 robustness-dispatch.bats의 GF-16 케이스, conf 읽기 가드는
conf-guard.bats 7건, TASK_PREFIX/BRANCH는 robustness-injection.bats가
브랜치별 Task-Id 트레일러로 확인한다. 이 때문에 GF-112에 남아 있던
'consistency.bats에 Python 쪽 동일성 검사 설계' 항목은 더 이상 필요 없다 -
GF-112 착수 전에 그 범위를 조정해야 한다.

테스트 스위트 재설계 방침은 DRAFT-16에 연결했다(상호 --add-ref). GF-108에서 확정된 '기능 테스트, 즉 행위 검증만 남기고 구현 언어 종속 테스트는 삭제한다'는 결정과, 그에 따라 DRAFT-16의 착수 순서 5번이 이미 해결됐다는 것, GF-112 범위 조정이 필요하다는 것을 draft 본문에 옮겨 적었다.

머지 완료(2026-09-24): PR #19를 rebase-merge로 머지. CI는 24caddc에서 static-analysis/bats 둘 다 통과했고, 머지 후 origin/main은 8a13b61이다(rebase라 SHA가 재작성됨). 로컬 main도 fast-forward로 맞췄다.

DoD #2는 절반만 만족한다: shellcheck는 CI에서 초록이지만 ruff는 아직 CI 스텝이 없어 로컬 실행(All checks passed)으로만 확인했다. 즉 지금 hooks/checks/*.py는 CI에서 린트되지 않는다 - ruff 스텝 추가는 GF-112 소관(doc-10은 첫 .py가 생긴 뒤 아무 때나 병렬 추가 가능하다고 적고 있다).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/checks/{python,ts,java,cpp,sql}.sh를 표준 라이브러리만 쓰는 Python으로 포팅하고(decision-16), 구 .sh를 지우면 함께 깨지는 호출부를 같은 커밋에서 고쳤다 - 아직 sh인 pre-commit의 디스패치 경로, test.yml의 shellcheck 대상, conf-guard.bats의 실행 3건, consistency.bats의 파일 목록.

sh 시절 우회 기법 중 Python에서 불필요해진 것만 걷어냈다: ts는 node -e 셸아웃 대신 json.load()로 scripts.lint를 직접 파싱하고, cpp/sql은 git diff -z 출력을 NUL로 split해 mktemp+xargs -0가 사라졌으며, resolve_self()는 os.path.realpath로 대체됐다. 회귀 방지 장치는 그대로 이식했다 - 모든 subprocess.run에 encoding=utf-8(GF-80), git config --get 빈 값 명시 체크(GF-35), 확장자 pathspec이 셸 글롭으로 먼저 펼쳐지지 않음(GF-81), tsc 로컬 우선·npx 금지(GF-79).

유저 승인을 받아 범위를 두 번 넓혔다(AC #10~#12): 구 .sh 삭제로 깨지는 AC 밖 3개 파일, GF-16 테스트의 asdf python 셈 해석 보정, 그리고 훅 소스를 텍스트로 떠서 비교하던 구현 언어 종속 검사 3건 삭제(행위 검증으로 대체됨을 확인).

검증: bats tests/ 100/100 통과(실패 0), ruff check hooks/checks/ All checks passed, shellcheck -s sh(남은 sh 4개) 클린, subprocess.run 16개 전부 encoding=utf-8 파싱 확인.
<!-- SECTION:FINAL_SUMMARY:END -->
