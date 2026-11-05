---
id: GF-110
title: hooks/pre-commit → Python 포팅
status: Done
assignee:
  - '@claude'
created_date: '2026-09-24 09:23'
updated_date: '2026-09-24 16:17'
labels:
  - python-migration
  - hooks
milestone: m-3
dependencies:
  - GF-108
documentation:
  - doc-9
  - doc-10
modified_files:
  - hooks/pre-commit
  - .github/workflows/test.yml
type: enhancement
ordinal: 4
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## 왜

pre-commit은 git이 직접 실행하는 3개 진입점 중 하나이자, 언어 감지 후 checks 스크립트를 호출하는 디스패처다. checks/*.py가 먼저 존재해야 디스패치 경로를 갱신할 수 있으므로 GF-108 완료가 선행 조건이다.

## 무엇을

hooks/pre-commit을 #!/usr/bin/env python3 셔뱅을 가진 단일 Python 파일로 포팅한다(sh 런처 없음 - python3을 필요조건으로 받아들이는 결정에 따름).
- template/hooks/*가 심볼릭 링크라 자기 실제 위치를 알아야 하는데, sh의 수동 resolve_self() 루프 대신 os.path.realpath(__file__)로 대체(심볼릭 링크 체인을 기본으로 따라감 - 정당한 단순화)
- 마커 파일 기반 언어 감지 로직 이식(마커 목록은 기존대로 gitformat.conf에서 git config --file 셸아웃으로 읽음 - ini 파서 직접 구현하지 않음)
- 5개 체크 스크립트를 sys.executable로 호출(이미 확보된 인터프리터 경로 재사용)
- 성공 시 .gitformat-verified 마커 기록(post-commit이 --no-verify 우회 탐지에 쓰는 포맷 계약이므로 형식 불변)

중요: CI의 shellcheck 대상이 글롭이 아니라 파일명 직접 지정이라, 이 파일이 Python이 되는 커밋에서 .github/workflows/test.yml의 대상 목록에서 hooks/pre-commit을 같이 빼야 한다. 미루면 그 사이 커밋들에서 CI가 Python 파일을 sh로 린트하려다 깨진다.

## 선행/병렬

GF-108(checks 5개) 완료가 선행 조건. GF-109(commit-msg)과는 코드 의존이 없어 병렬 가능하다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 hooks/pre-commit이 #!/usr/bin/env python3 셔뱅의 단일 Python 파일로 포팅되고 실행 권한이 유지된다
- [x] #2 os.path.realpath(__file__)로 자기 실제 위치를 찾아 template/hooks/의 심볼릭 링크를 경유해 실행돼도 hooks/ 경로를 올바르게 해석한다(sh의 수동 resolve_self 루프 대체)
- [x] #3 마커 파일 기반 언어 감지가 sh 버전과 동일하게 동작하고 마커 목록은 기존대로 git config --file로 gitformat.conf에서 읽는다(ini 파서 직접 구현 금지)
- [x] #4 감지된 언어의 체크 스크립트를 sys.executable로 호출하고, 체크 실패 시 해당 종료 코드로 커밋을 막는다
- [x] #5 성공 시 .gitformat-verified 마커를 post-commit이 읽는 기존 형식 그대로 기록한다
- [x] #6 같은 커밋에서 .github/workflows/test.yml의 shellcheck 대상 목록에서 hooks/pre-commit이 제거된다(파일명 직접 지정이라 미루면 CI가 Python 파일을 sh로 린트하려다 깨짐)
- [x] #7 bats tests/robustness-dispatch.bats tests/smoke.bats tests/conf-guard.bats가 전부 통과한다
- [x] #8 범위 추가(GF-108 AC #10, GF-109 AC #9와 같은 성격): 구 sh 호출부인 tests/conf-guard.bats와 tests/smoke.bats의 pre-commit 실행을 python3로 교체한다 - 안 고치면 포팅과 동시에 반드시 깨진다
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 해당 AC 범위의 bats 서브셋이 통과한다
- [ ] #2 CI(shellcheck + ruff)가 초록이다
- [ ] #3 변경 파일이 AC 범위를 벗어나지 않는다 - 범위 밖 작업 발견 시 유저에게 먼저 확인한다
- [x] #4 커밋이 [type][subsystem] 규칙과 Task-Id 트레일러를 만족한다
- [x] #5 Done 전환 전 final summary에 객관적 검증 증거(테스트 통과 로그 등)를 남긴다
- [x] #6 새 코드에 불필요한 주석을 넣지 않는다 - WHY가 비자명한 경우(GF-33/34/35/76/80 회귀 방지 패턴, 의도적 fail-open, 의도적 중복 유지 등)에만 한 줄 주석을 남긴다
- [ ] #7 PR은 rebase-merge로만 머지하고(squash/merge-commit 금지), push·PR 생성·머지 각 단계 전에 git fetch로 원격 상태를 먼저 확인한다(트렁크 방식이 아니라 로컬/리모트가 어긋날 수 있음)
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. 현재 hooks/pre-commit(sh, 100줄)을 읽고 로직 블록을 분해한다: resolve_self, gitformat.conf 읽기 가드, 마커 기반 언어 감지, 체크 스크립트 호출, 검증 마커 기록
2. Python으로 재작성 - HOOK_DIR은 os.path.realpath(__file__) 기반, conf는 git config --file 셸아웃, 체크 호출은 sys.executable 사용
3. 실행 권한 확인(chmod +x) - git은 실행 가능한 파일만 훅으로 실행한다
4. 같은 커밋에서 .github/workflows/test.yml의 shellcheck 대상 목록에서 hooks/pre-commit 제거
5. bats tests/robustness-dispatch.bats tests/smoke.bats tests/conf-guard.bats 실행
6. 스크래치 저장소에서 install.sh --global로 template/hooks/ 심볼릭 링크 경로를 만들고, 그 경로로 실행됐을 때도 realpath 해석이 올바른지 수동 확인(bats가 검증하지 못하는 경로)
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
검증(2026-09-25, 부모 세션이 직접 재확인):
- bats tests/ 101/101 통과, 실패 0
- core.hooksPath 전체 스위트 전후 모두 ~/githubs/git-format/hooks (GF-123 수정이 유지됨)
- ruff: hooks/ + 셔뱅 탐색 7개 파일 All checks passed (pre-commit이 수정 없이 자동 포함)
- shellcheck -s sh hooks/post-commit install.sh 클린 - shellcheck 대상이 이제 2개만 남았다
- 마커 형식 직접 확인: 격리 저장소에서 훅을 실행해 od -c로 '1790266612 48079\n' 확인, 정규식 ^[0-9]+ [0-9]+\n$ 매치. post-commit(아직 sh)과의 포맷 계약이 깨지지 않았다.
- AC #2(심볼릭 링크 경유 해석)는 robustness-dispatch.bats의 [GF-16 회귀] 케이스가 template/hooks 심볼릭 링크로 설치된 새 저장소에서 실제 커밋을 태워 검증하며 통과한다.

설계 판단 하나: 체크 스크립트 호출이 sys.executable 방식이 되면서 기존 [ -x $script ] 가드가 의미를 잃었다(실행 비트가 더 이상 실행 가능 여부를 결정하지 않음). os.path.isfile로 바꿨다 - -x를 유지하면 모드 비트만 잃은 멀쩡한 체크 스크립트가 조용히 건너뛰어지는 GF-32류 no-op이 된다. 없는 스크립트를 조용히 건너뛰는 기존 동작은 그대로다.

sh와 달라진 곳: ls ${MARKER_JAVA_GRADLE}는 값이 비면 CWD를 나열하며 성공해 java 체크가 모든 저장소에서 발동했을 것이다. glob.glob('')는 빈 리스트라 발동하지 않는다. 현재 conf 값(build.gradle*)에서는 두 동작이 동일하고, Python 쪽이 의도한 의미론이다.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/pre-commit을 표준 라이브러리만 쓰는 단일 Python 파일로 포팅했다(decision-16). resolve_self() 수동 루프는 os.path.realpath(__file__)로 대체했고, 체크 스크립트는 sys.executable로 호출해 pre-commit을 실행 중인 인터프리터를 그대로 재사용한다.

가장 조심한 것은 검증마커 형식이다. post-commit(아직 sh, GF-111)이 이 파일을 읽어 --no-verify 우회를 탐지하므로(decision-3, GF-31) '<epoch> <pid>' 한 줄 형식이 계약이다. 격리 저장소에서 od -c로 바이트 단위 확인했다.

sys.executable 호출로 바뀌면서 기존 [ -x ] 가드를 os.path.isfile로 교체했다 - 실행 비트가 더 이상 실행 가능 여부를 결정하지 않으므로, -x를 남기면 모드 비트만 잃은 스크립트가 조용히 건너뛰어지는 GF-32류 no-op이 된다.

호출부는 같은 커밋에서 고쳤다: test.yml의 shellcheck 대상에서 pre-commit 제거(이제 post-commit과 install.sh 둘만 남음), conf-guard.bats와 smoke.bats의 sh 실행을 python3로 교체. ruff는 GF-122의 셔뱅 탐색 덕에 수정 없이 자동으로 포함됐다.

검증: bats tests/ 101/101 통과(실패 0), core.hooksPath 스위트 전후 동일, ruff 7개 파일 All checks passed, shellcheck 클린, 마커 형식 바이트 확인, AC #2는 robustness-dispatch.bats의 GF-16 심볼릭 링크 케이스가 통과로 검증.
<!-- SECTION:FINAL_SUMMARY:END -->
