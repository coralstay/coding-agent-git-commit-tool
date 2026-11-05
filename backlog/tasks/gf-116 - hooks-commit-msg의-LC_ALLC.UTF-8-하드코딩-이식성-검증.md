---
id: GF-116
title: hooks/commit-msg의 LC_ALL=C.UTF-8 하드코딩 이식성 검증
status: Done
assignee: []
created_date: '2026-09-19 15:46'
updated_date: '2026-09-25 16:47'
labels: []
dependencies: []
references:
  - decision-16
documentation:
  - backlog/docs/doc-6 - 주의점과-한계.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
hooks/commit-msg:139에서 문자 수 계산에 LC_ALL=C.UTF-8을 사용한다. macOS/glibc 환경에서는 관대하게 동작함이 확인됐지만, musl/Alpine 같은 제한된 환경에는 이 로케일이 없을 수 있어 조용히 깨질 위험이 있다(미검증). 컨테이너/CI 환경 등에서 실측 검증하거나, 로케일 부재 시 안전한 폴백을 추가할지 검토 필요.

발견 경위: 2026-09-20 '이 프로젝트의 부족한점?' 조사(Explore agent, hooks/commit-msg:139)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 GF-116이 지적한 LC_ALL=C.UTF-8 하드코딩이 현재 코드에 존재하지 않음이 확인되고, 어떤 변경으로 사라졌는지 근거가 기록된다
- [x] #2 로케일이 없는 환경에서 훅이 한국어 메시지를 출력하다 UnicodeEncodeError로 죽지 않도록 폴백이 추가된다 (hooks/* 및 hooks/checks/* 전부)
- [x] #3 stdout/stderr 인코딩이 ASCII로 떨어지는 조건을 재현해 폴백 전에는 죽고 폴백 후에는 죽지 않음이 실측으로 확인된다
- [x] #4 로케일 부재 상황을 고정하는 bats 회귀 테스트가 추가되고 통과한다
- [x] #5 doc-6의 '훅이 POSIX sh로 작성돼 있어' 서술이 Python 3 기준으로 정정된다
- [x] #6 doc-7의 'pre-commit이 스테이징된 파일로 언어를 감지해' 서술이 실제 동작(루트 마커 파일로 감지)에 맞게 정정된다
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. LC_ALL=C.UTF-8이 현재 코드에 남아 있는지 확인하고, 없으면 어떤 변경으로 사라졌는지 근거를 찾는다
2. 같은 위험(로케일 부재)이 다른 형태로 남아 있는지 실측한다 — Python의 출력 인코딩
3. 실제 git commit에서 재현해 무엇이 죽고 무엇이 깨지는지 정확히 가른다
4. hooks/* 및 hooks/checks/* 전부에 stdout/stderr UTF-8 고정 폴백을 넣는다
5. tests/robustness-locale.bats로 회귀 고정하고, 폴백을 되돌려 테스트가 실제로 무는지 확인한다
6. doc-6의 'POSIX sh로 작성돼' 서술을 정정한다(사용자 승인 범위)
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
LC_ALL=C.UTF-8은 이미 없다. GF-109(commit-msg Python 포팅)가 커밋 메시지를 read_bytes().decode('utf-8', errors='replace')로 읽게 바꾸면서 sh 시절 로케일 우회 두 개를 모두 제거했다 — GF-80의 export LC_ALL=C와 길이 계산용 LC_ALL=C.UTF-8 + wc -m. len(str)이 곧 코드포인트 수라 한글 제목 길이가 안내와 어긋나지 않는다. grep -rn LC_ALL hooks/ install.sh 결과 0건.

그런데 GF-116이 경고한 위험 자체는 사라지지 않고 옮겨왔다. Python은 로케일이 UTF-8을 제공하지 않으면 출력 인코딩이 ascii로 떨어지고, 이 저장소의 모든 훅 메시지는 한국어다.

실측으로 정확히 갈랐다(LC_ALL=C + PYTHONCOERCECLOCALE=0 + PYTHONUTF8=0으로 C.UTF-8 부재 환경을 재현):
- stdout 경로는 죽는다. 기본 errors='strict'라서다. 실제 git commit에서 checks/python.py의 '[git-format] python: ruff/flake8을 찾을 수 없어 건너뜀' — 무해해야 하는 스킵 경로! — 에서 UnicodeEncodeError 트레이스백이 나고 커밋 객체가 만들어지지 않았다.
- stderr 경로는 죽지 않는다. 기본 errors='backslashreplace'라 commit-msg의 거부 메시지가 '\ucee4\ubc0b \uba54\uc2dc\uc9c0...'로 나왔다. 거부 판정 자체는 정상이었지만 사람이 읽을 수 없는 출력이었다.

폴백: hooks/{commit-msg,pre-commit,post-commit}과 hooks/checks/*.py 8개 파일 전부에서 import 직후 sys.stdout/sys.stderr을 encoding='utf-8', errors='replace'로 reconfigure한다. 예외는 (AttributeError, ValueError, OSError)로 삼킨다 — 스트림이 TextIOWrapper가 아닌 경우에도 훅이 죽지 않아야 한다.

터미널이 UTF-8을 못 읽으면 글자가 깨져 보이는 트레이드오프를 택했다. 메시지가 UTF-8로 작성돼 있으므로 출력도 UTF-8로 내보내는 게 맞고, 무엇보다 '깨져 보이는 것'이 '죽어서 모든 커밋을 막는 것'보다 낫다. 이 트레이드오프는 doc-6에 명시했다.

컨테이너 실측은 하지 않았다 — Docker/Alpine이 로컬에 없어 musl 환경을 직접 돌리지 못했고, 대신 PEP 538/540을 끈 조건으로 '로케일이 UTF-8을 못 주는 상태'를 재현했다. 실패 모드(ascii stdout)는 같지만 musl 환경에서의 직접 확인은 아니다.

검증 증거: (AC1) grep -rn LC_ALL hooks/ install.sh → 0건. 제거 주체는 GF-109(태스크 노트에 read_bytes().decode로 로케일 우회 2개 제거가 명시돼 있음). (AC2) git show --stat으로 hooks/{commit-msg,pre-commit,post-commit} + hooks/checks/{cpp,java,python,sql,ts}.py 8개 파일 전부에 폴백이 들어간 것 확인. (AC3) 실제 git commit으로 전후 비교: 폴백 전에는 'UnicodeEncodeError: ascii codec can not encode character' 트레이스백 + 커밋 객체 미생성, 폴백 후에는 '[git-format] python: ruff/flake8을 찾을 수 없어 건너뜀'이 정상 출력되고 커밋 성공. commit-msg 거부 메시지도 이스케이프에서 '커밋 메시지가 [type][subsystem] 형식이 아닙니다'로 바뀜. (AC4) bats tests/robustness-locale.bats 4/4 통과. 테스트가 실제로 무는지 확인: python.py의 폴백만 제거하면 #1이 실패하고, commit-msg의 폴백만 제거하면 #2와 #4가 실패한다. (AC5) grep 'POSIX sh로 작성' → 0건, Windows 항목이 install.sh/POSIX 전제 기준으로 재작성됨. 회귀: bats tests/ 114/114 통과(실패 0), ruff check . 통과.

GF-115 머지 후 rebase 재검증: hooks/checks/ts.py에서 충돌이 났고(GF-115의 EXTENSIONS 블록 vs 이 태스크의 인코딩 폴백) 폴백이 먼저 오도록 순차 배치해 해소했다 — 폴백은 이후 어떤 print보다 앞서야 효과가 있다. doc-6은 frontmatter updated_date만 충돌. 합쳐진 상태에서 bats tests/ 124/124 통과(실패 0), ruff check . 통과. 단독 브랜치 시점의 114/114는 GF-115의 신규 10건이 빠진 수치였다.

추가 범위(사용자 승인, 2026-09-25): doc-7:35의 'pre-commit이 스테이징된 파일로 언어를 감지해'를 '저장소 루트의 마커 파일로 언어를 감지해'로 정정했다. GF-115가 같은 오류를 README에서만 고쳤고 doc-7에 남아 있던 것이다. 검증: grep '스테이징된 파일로 언어를 감지' → backlog/docs/, README.md, hooks/ 전체에서 0건.

같은 세션에서 발견한 별건(DRAFT-18로 분리): git rebase 중 post-commit이 cherry-pick 도중 amend를 시도해 'fatal: You are in the middle of a cherry-pick -- cannot amend'(git exit 128)로 실패하고 트레이스백을 낸다. 재현 절차와 원인 연쇄를 DRAFT-18에 기록했다.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
GF-116이 지적한 LC_ALL=C.UTF-8 하드코딩은 이미 없었다 — GF-109가 커밋 메시지를 read_bytes().decode('utf-8', errors='replace')로 읽게 바꾸며 로케일 우회 두 개를 모두 제거했다. 그러나 경고했던 위험 자체는 사라지지 않고 Python의 출력 인코딩으로 옮겨와 있었다. C.UTF-8이 없는 환경을 재현해 실측한 결과, stdout은 기본 errors=strict라 checks/python.py의 '도구가 없어 건너뜀'이라는 무해한 경로에서 UnicodeEncodeError로 죽고 커밋이 트레이스백과 함께 막혔다(stderr은 backslashreplace라 죽지 않지만 한국어가 이스케이프로 깨졌다). 훅 8개 전부에서 stdout/stderr을 UTF-8(errors=replace)로 reconfigure하는 폴백을 넣어 양쪽 모두 해결했고, tests/robustness-locale.bats 4개로 고정했다 — 폴백을 되돌리면 해당 테스트가 실패하는 것까지 확인했다. 사용자 승인 범위로 doc-6의 '훅이 POSIX sh로 작성돼' 서술도 정정했다. 컨테이너 실측은 하지 못했다(Docker/Alpine 부재) — PEP 538/540을 끈 조건으로 같은 실패 모드를 재현한 것이며 musl 환경 직접 확인은 아니다. bats 114/114, ruff 통과.
<!-- SECTION:FINAL_SUMMARY:END -->
