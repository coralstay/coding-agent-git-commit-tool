---
id: GF-109
title: hooks/commit-msg → Python 포팅
status: Done
assignee:
  - '@claude'
created_date: '2026-09-24 09:24'
updated_date: '2026-09-24 15:44'
labels:
  - python-migration
  - hooks
milestone: m-3
dependencies: []
documentation:
  - doc-9
  - doc-10
modified_files:
  - hooks/commit-msg
  - .github/workflows/test.yml
type: enhancement
ordinal: 3
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## 왜

commit-msg는 커밋 메시지 형식을 검증해 위반 시 커밋 자체를 거부하는 훅이다. pre-commit이나 checks 스크립트를 호출하지 않는 독립 로직이라 다른 포팅 작업과 코드 의존이 없고 병렬 진행이 가능하다.

## 무엇을

hooks/commit-msg를 #!/usr/bin/env python3 단일 파일로 포팅한다(305줄, 전환 대상 중 두 번째로 큼).

정당한 단순화: 커밋 메시지를 Path(msg_file).read_bytes().decode("utf-8", errors="replace")로 읽으면 sh 시절의 두 가지 로케일 우회가 모두 필요 없어진다 - (1) GNU grep이 리눅스에서 invalid UTF-8을 잘못 처리하는 문제를 피하려던 export LC_ALL=C(GF-80), (2) 한글이 바이트 단위로 과소 계산되지 않게 하려던 LC_ALL=C.UTF-8 + wc -m. Python의 str/len()은 코드포인트 단위라 기본적으로 유니코드를 올바르게 센다. errors="replace"는 invalid UTF-8 커밋 메시지에서 훅이 UnicodeDecodeError로 죽지 않게 하는 의도적 선택이다.

그대로 유지해야 하는 것:
- Task-Id 앵커링 정규식(GF-34) - (^|[^a-zA-Z0-9])PREFIX-[0-9]+ 형태를 유지해 부분 문자열 오매치를 막는다
- subject 50자 / body 72자 길이 검증, blank-line-after-subject 규칙
- [type][subsystem] 프리픽스 검증, 타입 목록은 gitformat.conf에서 읽음
- Fixes: 트레일러의 해시 존재 검증, AI-Model 화이트리스트 게이트
- TASK_PREFIX/BRANCH 계산 블록은 post-commit과 동일하게 유지(공유 모듈 없이 파일별 독립 중복 - 이번 전환의 확정 사항)
- 거부 시 마커 정리(sh의 trap EXIT)는 try/finally로 이식
- 모든 subprocess.run에 encoding="utf-8" 명시

CI: 같은 커밋에서 test.yml shellcheck 대상 목록에서 hooks/commit-msg를 제거한다(파일명 직접 지정이라 미루면 CI가 깨짐).

## 선행/병렬

선행 조건 없음. commit-msg는 pre-commit이나 checks 스크립트를 호출하지 않는 독립 로직이라 GF-108, GF-110과 병렬로 진행 가능하다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 hooks/commit-msg가 #!/usr/bin/env python3 셔뱅의 단일 Python 파일로 포팅되고 os.path.realpath(__file__) 기반 위치 해석이 적용된다
- [x] #2 커밋 메시지를 read_bytes().decode('utf-8', errors='replace')로 읽어 LC_ALL=C(GF-80)와 LC_ALL=C.UTF-8+wc -m 우회가 모두 제거되고, invalid UTF-8 메시지에서도 훅이 예외로 죽지 않는다
- [x] #3 subject 50자/body 72자 길이 검증이 한글 등 멀티바이트 문자에서 코드포인트 단위로 sh 버전과 동일하게 동작한다
- [x] #4 [type][subsystem] 프리픽스 검증, blank-line-after-subject 규칙, Fixes: 트레일러 해시 존재 검증, AI-Model 화이트리스트 게이트가 전부 동등하게 이식된다(타입 목록은 gitformat.conf에서 읽음)
- [x] #5 Task-Id 앵커링 정규식이 (^|[^a-zA-Z0-9])PREFIX-[0-9]+ 형태로 이식돼 부분 문자열 오매치(GF-34)가 재발하지 않고, TASK_PREFIX/BRANCH 계산 블록이 post-commit과 동일하게 유지된다
- [x] #6 거부 시 마커 정리(sh의 trap EXIT)가 try/finally로 이식되고, 모든 subprocess.run에 encoding=utf-8이 명시된다
- [x] #7 같은 커밋에서 test.yml shellcheck 대상 목록에서 hooks/commit-msg가 제거된다
- [x] #8 bats tests/robustness-commit-msg.bats tests/robustness-injection.bats가 전부 통과한다
- [x] #9 범위 추가(GF-108 AC #10/#11과 같은 성격): 구 sh 호출부인 tests/conf-guard.bats의 commit-msg 실행을 python3로 교체한다 - 안 고치면 포팅과 동시에 반드시 깨진다
- [x] #10 범위 추가(같은 성격): HOME을 가짜 경로로 바꾸는 테스트들이 로컬 asdf 환경에서 python3 셈을 해석하지 못해 훅이 실행되지 않던 문제를 helpers/git-format.bash의 asdf_pin_python()으로 통일해 해결한다. ASDF_PYTHON_VERSION=system은 path_without()의 섀도 PATH에서 무한 재귀로 멈추므로 쓰지 않고, asdf가 해석한 구체 버전을 고정한다(이 PC는 asdf로 python을 관리한다)
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
1. hooks/commit-msg(sh, 305줄)를 읽고 검증 규칙을 목록화한다: [type][subsystem] 프리픽스, subject 50자, body 72자, blank-line-after-subject, Fixes: 해시 존재, Task-Id 브랜치 강제, AI-Model 화이트리스트
2. Python으로 재작성 - 메시지는 read_bytes().decode("utf-8", errors="replace"), 길이 검증은 len(str)로 코드포인트 단위
3. Task-Id 정규식은 re.escape(prefix)로 조립하고 (^|[^a-zA-Z0-9]) 앵커를 유지(GF-34 재발 방지)
4. TASK_PREFIX/BRANCH 계산 블록은 GF-111에서 그대로 복제할 수 있는 형태로 작성한다(공유 모듈은 만들지 않기로 확정됨 - 파일별 독립 중복 유지)
5. 거부 시 마커 정리는 try/finally로 이식(sh의 trap EXIT 대체)
6. 같은 커밋에서 shellcheck 대상 목록에서 hooks/commit-msg 제거
7. bats tests/robustness-commit-msg.bats tests/robustness-injection.bats 실행 - 한글 메시지의 길이 경계값과 invalid UTF-8 입력을 특히 확인한다
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
검증(2026-09-25):
- bats tests/ 100/100 통과, 실패 0
- bats tests/robustness-commit-msg.bats 34/34, robustness-injection.bats 7/7, conf-guard.bats 7/7
- ruff: hooks/ + 셔뱅 탐색 6개 파일 All checks passed (commit-msg가 자동으로 포함됨)
- shellcheck -s sh hooks/pre-commit hooks/post-commit install.sh 클린, test.yml 대상에서 commit-msg 제거 확인

AC #5 단서: 'TASK_PREFIX/BRANCH 블록이 post-commit과 동일' 조건은 post-commit이 아직 sh라(GF-111) 텍스트 동일성으로는 성립할 수 없다. 동작 동등성(같은 conf 키, GF-35 빈 값 폴백, symbolic-ref → HEAD 폴백, 앵커링된 대소문자 무시 패턴)으로 이식했고, GF-111이 그대로 옮길 수 있게 배치했다. 텍스트 동일성 검사는 GF-108에서 폐지됐고(doc-12) 행위 검증은 robustness-injection.bats가 맡는다.

이번에 발견한 것 두 가지(GF-109 범위 밖, 별도 처리 필요):

1. tests/robustness-install.bats:72가 install.sh 사본을 타깃 인자 없이 --global로 실행한다. 타깃 기본값이 CWD(실제 저장소)이고 SELF_DIR이 임시 디렉터리라, 테스트를 돌릴 때마다 실제 저장소의 core.hooksPath가 곧 삭제될 임시 경로로 덮어써진다. 그러면 이후 모든 커밋에서 훅이 조용히 죽는다. 이 세션의 커밋 4c1ea01에 트레일러가 없는 것이 그 결과다. 테스트 주석은 '격리된 사본에서 진행한다'고 적고 있으나 훅 소스만 격리했고 설치 대상은 격리하지 못했다.

2. 위 1번의 여파로 cbfa564의 Tokens-Used: 55890695가 실제 델타가 아니다. 훅이 죽어 있던 기간만큼 커서가 밀려 누적된 값이다. 지금 재계산해도 '그 커밋의 올바른 값'은 복원되지 않으므로(현재 커서 기준의 다른 값이 나올 뿐) 숫자를 바꾸지 않고 경위만 남긴다.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/commit-msg(305줄)를 표준 라이브러리만 쓰는 단일 Python 파일로 포팅했다(decision-16).

정당한 단순화: 커밋 메시지를 read_bytes().decode('utf-8', errors='replace')로 읽어 sh 시절 로케일 우회 두 개(GF-80의 LC_ALL=C, 길이 계산용 LC_ALL=C.UTF-8 + wc -m)를 모두 제거했다. len(str)이 곧 코드포인트 수라 한글 제목 길이가 안내와 어긋나지 않는다. resolve_self()는 os.path.realpath로 대체했다.

회귀 방지 장치는 전부 이식했다 - MERGE_HEAD 기반 병합 예외(GF-30), 거부 시 마커 정리(GF-31, trap EXIT → try/finally로 예기치 못한 예외 경로까지 커버), Task-Id 앵커링(GF-34), taskPrefix 빈 값 폴백(GF-35), branchExempt union(GF-78), 그리고 type 목록이 비면 조용히 모든 커밋을 거부하지 않고 원인을 밝히며 멈춘다(GF-76 형태 방지).

conf에서 읽은 값을 정규식에 넣을 때 re.escape를 적용했다 - 현재 conf 값에는 메타문자가 없어 동작 변화는 없지만, sh 버전에 있던 conf→정규식 주입 여지를 없앴다.

호출부는 같은 커밋에서 고쳤다: test.yml의 shellcheck 대상에서 commit-msg 제거, conf-guard.bats의 sh 실행을 python3로 교체. ruff는 GF-122의 셔뱅 탐색 덕에 수정 없이 자동으로 포함됐다.

검증: bats tests/ 100/100 통과(실패 0), ruff 6개 파일 All checks passed, shellcheck 클린.
<!-- SECTION:FINAL_SUMMARY:END -->
