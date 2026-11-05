---
id: GF-107
title: 'hooks Python 전환 거버넌스: decision 기록 + install.sh python3 가드'
status: Done
assignee:
  - '@claude'
created_date: '2026-09-24 09:23'
updated_date: '2026-09-24 10:24'
labels:
  - python-migration
  - governance
milestone: m-4
dependencies: []
documentation:
  - doc-9
  - doc-10
modified_files:
  - install.sh
priority: high
type: chore
ordinal: 1
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## 왜

hooks/*를 Python으로 옮기려면 decision-9(hooks/*, install.sh, hooks/checks/*.sh를 POSIX sh로 유지)를 먼저 재검토해야 한다 - decision-9의 Consequences 절이 "이탈하려면 이 결정을 먼저 재검토해야 한다"고 명시하고 있다. 또한 GF-88이 과거 Python 전환을 기각했는데, 그 기각 사유는 "컴파일된 네이티브 바이너리 배포"가 README의 감사 가능성 약속과 충돌한다는 것이었다. 이번 전환은 해석되는 Python 소스를 그대로 배포하는 다른 모델이라 그 사유가 적용되지 않는다는 점을 명시적으로 기록해야 한다.

## 무엇을

1. decision-13이 decision-9의 vendoring 조항만 부분 대체한 선례와 같은 구조로, decision-9를 hooks/pre-commit, hooks/commit-msg, hooks/post-commit, hooks/checks/*.py 범위에서만 대체하는 새 decision을 기록한다. install.sh는 계속 decision-9 적용(POSIX sh 유지).
2. install.sh에 python3 존재 확인 가드를 추가한다(기존 gitformat.conf 읽기 가드 바로 다음, 같은 스타일).

## 선행/병렬

다른 모든 태스크보다 먼저 진행한다. decision 기록은 이 저장소 관례상 코드 변경보다 먼저 커밋돼야 하고, install.sh 가드도 마일스톤 1의 파일 포팅이 시작되기 전에 있어야 python3 부재로 인한 원인 파악 지연을 막을 수 있다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 decision-9를 hooks/pre-commit·commit-msg·post-commit·hooks/checks/*.py 범위에서 대체하는 새 decision이 decision-13과 같은 구조(Context/Decision/Consequences)로 기록된다
- [x] #2 새 decision에 GF-88의 기각 사유(컴파일 바이너리의 감사 가능성 충돌)가 이번 배포 모델(해석되는 Python 소스)에는 적용되지 않는 이유가 명시된다
- [x] #3 새 decision의 Consequences에 python3 런타임 의존성 신설과 README 문구 갱신 필요가 기록되고, install.sh는 계속 POSIX sh를 유지한다는 점이 명시된다
- [x] #4 install.sh에 command -v python3 가드가 기존 gitformat.conf 읽기 가드 바로 다음 자리, 같은 스타일로 추가된다
- [x] #5 python3이 없을 때 install.sh가 명확한 한국어 에러 메시지와 함께 exit 1로 중단된다
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 해당 AC 범위의 bats 서브셋이 통과한다
- [x] #2 CI(shellcheck + ruff)가 초록이다
- [x] #3 변경 파일이 AC 범위를 벗어나지 않는다 - 범위 밖 작업 발견 시 유저에게 먼저 확인한다
- [x] #4 커밋이 [type][subsystem] 규칙과 Task-Id 트레일러를 만족한다
- [x] #5 Done 전환 전 final summary에 객관적 검증 증거(테스트 통과 로그 등)를 남긴다
- [x] #6 새 코드에 불필요한 주석을 넣지 않는다 - WHY가 비자명한 경우(GF-33/34/35/76/80 회귀 방지 패턴, 의도적 fail-open, 의도적 중복 유지 등)에만 한 줄 주석을 남긴다
- [x] #7 PR은 rebase-merge로만 머지하고(squash/merge-commit 금지), push·PR 생성·머지 각 단계 전에 git fetch로 원격 상태를 먼저 확인한다(트렁크 방식이 아니라 로컬/리모트가 어긋날 수 있음)
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. `backlog decision create "hooks Python 전환: decision-9의 POSIX 정책을 hooks/*, hooks/checks/*.sh 범위에서 대체" -s accepted`로 decision 생성
2. 생성된 decision 파일에 Context/Decision/Consequences 작성 - decision-13(decision-9의 vendoring 조항만 부분 대체)의 구조를 그대로 따른다. decision CLI에는 본문을 채우는 명령이 없어 파일을 직접 작성해야 하는 예외 케이스다(GF-103의 readme.md와 동일한 상황)
3. install.sh의 gitformat.conf 읽기 가드(현재 24~27행) 바로 다음에 `command -v python3` 가드 블록 추가
4. install.sh 상단 설명 주석 갱신 - 현재 "core.hooksPath와 commit.template을 설정한다"는 문구가 python3 확인 책임을 반영하지 못함
5. `shellcheck -s sh install.sh` 통과 확인
6. 이 태스크가 Done이 된 뒤에야 m-3(리팩토링)의 파일 포팅을 시작한다
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
검증(2026-09-24, 재실행): core.hooksPath가 존재하지 않는 tmp 경로로 덮여 있어 최초 두 커밋에 Task-Id 등 트레일러가 붙지 않았다. install.sh --no-global .로 복구한 뒤 같은 트리를 그대로 두 커밋으로 재작성해 트레일러를 정상화했다(git diff fab82a4 HEAD 결과 없음). bats tests/ 103/103 통과, CI와 동일한 shellcheck -s sh hooks/commit-msg hooks/pre-commit hooks/post-commit hooks/checks/*.sh install.sh 통과, python3을 뺀 PATH에서 install.sh가 한국어 메시지와 함께 exit 1.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
decision-9의 POSIX 문법 조항을 hooks/pre-commit·commit-msg·post-commit과 hooks/checks/*.py 8개 파일 범위에서만 대체하는 decision-16을 기록하고(GF-88의 기각 사유가 컴파일 바이너리 배포에만 해당함을 본문에 명시), install.sh에는 gitformat.conf 읽기 가드 바로 다음에 command -v python3 가드를 같은 스타일로 추가했다. install.sh 자체는 POSIX sh를 유지한다. 검증: bats tests/ 103/103 통과, CI와 동일한 shellcheck -s sh 전체 대상 통과, python3이 없는 PATH에서 install.sh가 'python3을 찾을 수 없습니다' 메시지와 함께 exit 1.
<!-- SECTION:FINAL_SUMMARY:END -->
