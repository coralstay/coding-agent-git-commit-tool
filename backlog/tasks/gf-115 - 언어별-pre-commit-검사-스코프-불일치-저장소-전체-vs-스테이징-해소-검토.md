---
id: GF-115
title: 언어별 pre-commit 검사 스코프 불일치 (저장소 전체 vs 스테이징) 해소 검토
status: Done
assignee: []
created_date: '2026-09-19 15:46'
updated_date: '2026-09-25 02:58'
labels: []
dependencies: []
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
checks/ts.sh, checks/python.sh, checks/java.sh는 저장소 전체를 검사하고, checks/cpp.sh, checks/sql.sh는 git diff --cached로 스테이징된 파일만 검사한다. TS/Python/Java 프로젝트는 이번 커밋과 무관한 기존 lint/컴파일 에러 때문에도 커밋이 막힐 수 있다(false blocking) — 언어 간 검사 스코프를 일관되게 맞출지, 아니면 스코프 차이를 의도된 것으로 문서화만 할지 검토 필요.

발견 경위: 2026-09-20 '이 프로젝트의 부족한점?' 조사(Explore agent, hooks/checks/ts.sh:25, python.sh:12, java.sh:48/51 vs cpp.sh:70, sql.sh:50)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 python.py가 스테이징된 .py/.pyi 파일만 ruff/flake8으로 검사하고, 스테이징된 Python 파일이 없으면 그 검사를 건너뛴다
- [x] #2 ts.py의 tsc 단계가 tsconfig.json을 extends하는 임시 프로젝트 파일(files=스테이징 파일, include=[])로 스테이징 범위만 검사하고, 실행 후 임시 파일이 남지 않는다
- [x] #3 스테이징되지 않은 파일이나 이미 커밋된 파일의 기존 린트/타입 에러가 무관한 커밋을 막지 않는다(python/ts 양쪽 회귀 테스트)
- [x] #4 스테이징된 파일의 린트/타입 에러는 여전히 커밋을 막고, tsconfig의 strict에서만 잡히는 타입 에러도 계속 잡힌다
- [x] #5 java.py의 mvn/gradle 컴파일과 ts.py의 npm run lint은 프로젝트/저장소 전체 범위로 남고, 그 이유가 코드 주석에 적혀 있다
- [x] #6 검사 스코프 규칙이 hooks/checks/readme.md, README.md, doc-6에 문서화된다
- [x] #7 bats tests/ 전체와 ruff check . 가 통과한다
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. python.py: ruff/flake8을 스테이징된 *.py/*.pyi에만 실행, 없으면 조용히 건너뜀(cpp.py/sql.py와 같은 git diff --cached fail-open 블록 중복 유지 - decision-16 감사 가능성).
2. ts.py: npm run lint은 저장소 전체 유지(사용자 package.json 스크립트의 인자 계약 불명), tsc는 임시 tsconfig({extends: ./tsconfig.json, files: [스테이징 .ts/.tsx], include: []})를 프로젝트 tsconfig 옆에 써서 tsc -p <temp> --noEmit으로 스테이징 범위만 검사 + finally로 임시 파일 정리. tsc <file> 형식은 tsconfig를 무시해 strict 에러를 놓치므로 금지.
3. java.py: mvn/gradle에 파일 단위 컴파일 모드가 없어 프로젝트 전체 유지 - 이유를 주석으로 명시.
4. 문서: hooks/checks/readme.md에 스코프 규칙(파일 단위 린터=스테이징, 프로젝트 단위 컴파일러/타입체커=전체) 반영, hooks/readme.md·README.md 스테일 문장 점검, backlog doc으로 규칙 기록.
5. 테스트: tests/checks-python.bats·checks-ts.bats에 (a) 비스테이징 파일의 기존 에러는 커밋을 막지 않음, (b) 스테이징 파일의 에러는 여전히 막음, (c) ts는 strict 전용 타입 에러가 여전히 잡힘 회귀 테스트 추가.
6. 검증: bats tests/ 전체 + ruff check .
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## 결정과 근거 (GF-115)

- **스코프 규칙**: 도구가 파일 목록/프로젝트 파일로 대상을 지정할 수 있으면 스테이징
  범위로 좁히고, 그럴 수 없는 프로젝트 단위 도구만 전체 범위로 남긴다.
  - 좁힘: `python.py`(ruff/flake8에 파일 목록 전달), `ts.py`의 tsc(임시 프로젝트 파일).
  - 유지: `java.py`의 `mvn -q compile`/`./gradlew -q compileJava` — 파일 단위 컴파일
    모드가 없다(자바 컴파일은 같은 소스 트리의 다른 클래스를 참조해야 성립).
    `ts.py`의 `npm run lint` — 컨슈머가 직접 쓴 스크립트라 파일 인자를 덧붙였을 때의
    계약을 알 수 없다(`eslint .`은 안 좁혀지고, 인자를 예상하지 않는 스크립트는 깨진다).
- **tsc를 좁히는 방법**: `tsc --noEmit <파일>`은 쓰지 않았다. 파일 인자를 주면 tsc가
  tsconfig.json을 통째로 무시한다(실측: strict 전용 에러가 있는 파일이 파일 인자로는
  exit 0, `tsc --noEmit`으로는 exit 2). 대신 저장소 루트에
  `tsconfig.gitformat-<pid>.json`을 써서 `{extends: ./tsconfig.json, files: [스테이징
  파일], include: []}`로 두고 `tsc -p <그 파일> --noEmit`을 돌리고 finally에서 지운다.
  `include: []`가 필수다 — extends는 같은 이름의 키만 덮으므로 원본의 `include`가
  남으면 스테이징되지 않은 파일이 다시 끌려온다(실측으로 확인: include를 덮지 않은
  임시 파일은 비스테이징 파일 에러 3건을 함께 보고했고, 덮은 쪽은 스테이징 파일 1건만
  보고했다).
- **공유 모듈로 빼지 않은 이유**: `git diff --cached`로 스테이징 파일을 뽑는 블록은
  cpp.py/sql.py와 같은 형태로 python.py/ts.py에 중복 유지했다 — 훅 파일 하나만 읽으면
  그 훅의 동작을 전부 알 수 있어야 한다는 감사 가능성 요구사항(decision-16, pre-commit
  주석)이 공유 모듈보다 우선한다. `git diff` 실패는 "검사할 파일 없음"으로 흘리는
  fail-open도 기존 두 파일과 동일하게 맞췄다.
- **확장자 목록을 gitformat.conf에 넣지 않은 이유**: python `*.py`/`*.pyi`,
  ts `*.ts`/`*.tsx`/`*.mts`/`*.cts`는 각각 한 파일에서만 쓰는 값이고, conf를 읽게 하면
  두 파일에 conf 읽기 가드 블록까지 복제해야 한다. sql.py가 `*.sql`을 인라인으로 두는
  선례를 따랐다. `.js`/`.jsx`는 일부러 제외했다 — allowJs가 아닌 프로젝트에서 .js를
  files에 넣으면 타입 에러와 무관한 사용법 에러로 커밋이 막힌다.

## 검증 증거

- `bats tests/`: 114개 전부 통과, 실패 0 (exit 0). main 기준선 104개에 checks-python.bats
  4개 + checks-ts.bats 6개를 더한 수다(`git grep -c "^@test"` 합계로 확인).
- `ruff check .`: All checks passed!
- 새 회귀 테스트가 실제로 회귀를 잡는지 역검증: HEAD의 옛 python.py/ts.py를 임시로
  되돌려 같은 테스트를 돌렸다.
  - 옛 python.py: checks-python.bats #4/#5/#6 실패(비스테이징 에러, 커밋된 에러,
    Python 파일 미스테이징 케이스), 나머지 통과.
  - 옛 ts.py: checks-ts.bats #9/#10/#11/#12 실패, strict 테스트(#8)는 통과 — 옛 코드는
    저장소 전체를 보므로 strict 에러는 잡되 스코프만 넓었다는 뜻이다.
- strict 회귀 감시탑 실측: strict 전용 에러(TS7006)가 있는 파일에 대해
  `tsc --noEmit <파일>` = exit 0, `tsc -p <임시 프로젝트 파일> --noEmit` = exit 2.
- `tests/robustness-dispatch.bats`의 `"python: ruff check ."` 기대값 3곳은 명령 이름까지만
  비교하도록 좁혀 갱신했다(디스패치 사실만 확인하는 테스트다).

## GF-115 범위 밖에서 발견한 것 (고치지 않음)

- `backlog/docs/doc-6`의 한계 항목에 "훅이 POSIX sh로 작성돼 있어 WSL이나 Git Bash 같은
  POSIX 호환 셸이 필요합니다"가 남아 있다 — 훅은 GF-108/109에서 Python으로 전환됐다
  (decision-16). 스코프와 무관한 스테일 문장이라 그대로 뒀다.
- `backlog/docs/doc-7`의 "pre-commit이 스테이징된 파일로 언어를 감지해"도 같은 종류의
  부정확한 표현이다(감지는 저장소 루트의 마커 파일로 한다). README.md 쪽은 이번에
  스코프 문장을 다시 쓰면서 함께 고쳤지만 doc-7은 손대지 않았다.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
언어별 pre-commit 검사 스코프를 '도구가 허용하는 한 스테이징 범위'로 통일했다. python.py는 ruff/flake8을 스테이징된 .py/.pyi 파일 목록에만 돌리고, ts.py의 tsc는 tsconfig.json을 extends하면서 files를 스테이징 파일로, include를 []로 덮은 임시 프로젝트 파일(tsc -p, finally에서 삭제)로 좁혔다 - tsconfig를 무시하는 'tsc --noEmit <파일>' 형태는 쓰지 않는다. 파일 단위 모드가 없는 mvn/gradle 컴파일과 인자 계약을 알 수 없는 npm run lint은 전체 범위로 남기고 그 이유를 주석·문서에 남겼다. 검증: bats tests/ 114개 전부 통과(실패 0, main 기준선 104개 + 새 회귀 테스트 10개), ruff check . 통과. 새 회귀 테스트는 HEAD의 옛 체크 스크립트로 되돌려 돌렸을 때 python 3건·ts 4건이 실패하는 것으로 회귀 탐지력을 역검증했고, strict 전용 타입 에러(TS7006)가 파일 인자 방식에서는 exit 0, 임시 프로젝트 파일 방식에서는 exit 2인 것도 실측했다.
<!-- SECTION:FINAL_SUMMARY:END -->
