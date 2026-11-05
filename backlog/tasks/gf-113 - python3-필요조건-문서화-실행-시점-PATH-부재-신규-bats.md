---
id: GF-113
title: python3 필요조건 문서화 + 실행 시점 PATH 부재 신규 bats
status: Done
assignee:
  - '@claude'
created_date: '2026-09-24 09:25'
updated_date: '2026-09-24 19:09'
labels:
  - python-migration
  - docs
  - tests
milestone: m-4
dependencies:
  - GF-107
  - GF-109
  - GF-110
  - GF-111
documentation:
  - doc-9
  - doc-6
  - doc-10
modified_files:
  - README.md
  - hooks/readme.md
  - tests/robustness-install.bats
type: enhancement
ordinal: 7
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## 왜

이번 전환의 유일한 실질적 트레이드오프는 python3 의존성이다. 그런데 "설치돼 있음"만으로는 부족하고 훅이 실행되는 시점의 PATH에도 잡혀야 한다. GUI git 클라이언트(SourceTree, GitHub Desktop, IDE 내장 git 패널)는 셸 프로파일(.zshrc 등)을 거치지 않고 OS 최소 PATH(macOS는 launchd가 물려주는 /usr/bin:/bin:/usr/sbin:/sbin 수준)만 물려받는 경우가 흔해, Homebrew/pyenv로만 설치된 python3(/opt/homebrew/bin/python3 등)을 못 찾을 수 있다. 최신 macOS는 /usr/bin/python3를 기본 내장하지도 않는다.

이 문제를 코드로 우회하지 않고(sh 런처 + git config로 경로를 저장하는 방식을 검토했으나 채택하지 않음) 명시적 필요조건으로 고지하기로 했으므로, 고지 자체가 제품의 일부다. 그리고 sh에는 없던 이 새 실패 모드가 문서에 적은 대로 실제로 동작하는지 객관적으로 검증해야 한다 - 문서만 써두고 검증하지 않으면 안 된다.

## 무엇을

1. README.md: "Runtime deps: none" 문구를 명시적 필요조건 섹션으로 교체한다. "Requirements: git, python3 (PATH에서 실행 가능해야 함)"을 설치 안내보다 먼저 보이는 자리에 둔다. 그 아래에 GUI 클라이언트 PATH 한계를 세부 설명으로 붙이되, 훅별 영향이 비대칭이라는 점을 강조한다:
   - pre-commit/commit-msg: python3을 못 찾으면 훅이 실패하고 git이 커밋을 막는다(눈에 띄는 안전한 실패)
   - post-commit: 이미 커밋이 완료된 뒤라 git이 신경 쓰지 않는다 - Task-Id/AI-Model/Signed-off-by 트레일러가 조용히 누락된 채 커밋은 성공한 것처럼 보인다(가장 날카로운 지점)
   - install.sh의 확인은 설치 시점(터미널, 풍부한 PATH)만 검증하므로 실제 커밋 시점(GUI, 좁은 PATH) 동작을 보장하지 못한다

2. hooks/readme.md에도 이 python3 PATH 요구사항을 한 줄 반영한다.

3. tests/robustness-install.bats: python3이 없는 설치 환경 케이스를 추가한다(기존 path_without() 헬퍼 재사용). GF-107에서 만든 install.sh 가드가 명확한 에러로 설치를 막는지 확인.

4. 신규 bats: 훅 실행 시점(설치 시점 아님) PATH에 python3이 없을 때의 동작을 검증한다. path_without()으로 python3을 숨긴 환경에서 (a) pre-commit/commit-msg가 nonzero로 실패해 커밋이 실제로 막히는지, (b) post-commit이 실패해도 커밋 자체는 유지되고 트레일러만 누락되는지 직접 확인한다. 이건 sh 버전에 없던 동작이라 "동일성 재검증"이 아니라 "신규 동작 검증"이다.

## 선행/병렬

항목마다 다르다. README 필요조건 문구는 코드 상태와 무관해 아무 때나(마일스톤 1을 기다리지 않고) 쓸 수 있다. install.sh 부재 케이스 bats는 GF-107 완료 후면 언제든 가능하다. 실행 시점 PATH 부재 bats는 해당 훅이 실제로 Python으로 포팅된 뒤에만 의미가 있으므로, GF-110/11/12가 하나씩 끝날 때마다 그 훅의 케이스부터 병렬로 추가하면 된다(전부 기다릴 필요 없음).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 README.md의 'Runtime deps: none' 문구가 설치 안내보다 먼저 보이는 명시적 필요조건 섹션(Requirements: git, python3 - PATH에서 실행 가능해야 함)으로 교체된다
- [x] #2 README에 GUI git 클라이언트 최소 PATH 한계가 문서화되고, 훅별 영향 비대칭(pre-commit/commit-msg는 커밋 차단이라 눈에 띄는 실패 / post-commit은 트레일러가 조용히 누락된 채 커밋이 성공한 것처럼 보임)이 명시된다
- [x] #3 README에 install.sh의 python3 확인이 설치 시점(터미널, 풍부한 PATH)만 검증하므로 실제 커밋 시점(GUI, 좁은 PATH) 동작을 보장하지 못한다는 점이 명시된다
- [x] #4 hooks/readme.md에도 python3 PATH 요구사항이 반영된다
- [x] #5 tests/robustness-install.bats에 python3 없는 설치 환경 케이스가 path_without() 헬퍼를 재사용해 추가되고, install.sh 가드가 명확한 에러로 설치를 막는 것이 확인된다
- [x] #6 신규 bats로 훅 실행 시점 PATH에 python3이 없을 때 pre-commit/commit-msg가 nonzero로 실패해 커밋이 실제로 막히는 것이 확인된다
- [x] #7 신규 bats로 같은 조건에서 post-commit이 실패해도 커밋 자체는 유지되고 트레일러만 누락되는 것이 확인된다(README에 문서화한 비대칭 동작의 객관적 증거)
- [x] #8 AC #1의 'Runtime deps: none'과 같은 주장이 README 안에 여러 형태로 반복된다 - 배지 두 개(Shell: POSIX sh, Runtime deps: none), 상단 소개의 'npm/pip 같은 별도 런타임 없이', 'POSIX sh 훅 3개' 문구, '별도 런타임 의존성은 두지 않았습니다' 문장. python3 의존이 생긴 이상 전부 사실이 아니므로 한 곳만 고치지 말고 같이 바로잡는다
- [x] #9 GF-112에서 이월: backlog/docs/doc-5(저장소 구조)가 hooks/checks/*.sh를 나열하고 있어 낡았고, GF-112가 신설한 hooks/readme.md와 hooks/checks/readme.md도 반영돼 있지 않다. 전환 후 실제 구조에 맞춘다
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
1. README.md에서 "Runtime deps: none" 문구의 현재 위치를 확인하고, 설치 안내보다 앞서는 Requirements 섹션으로 교체한다
2. 그 아래에 GUI 클라이언트 PATH 한계, 훅별 비대칭 영향(pre-commit/commit-msg는 커밋 차단 / post-commit은 트레일러 조용한 누락), install.sh 검증의 시점 한계를 하위 항목으로 작성
3. hooks/readme.md에 python3 PATH 요구사항 한 줄 반영
4. tests/robustness-install.bats에 python3 부재 설치 케이스 추가 - 기존 path_without() 헬퍼 재사용
5. 신규 bats 파일 작성 - 실행 시점 PATH 부재 시나리오. pre-commit/commit-msg는 커밋이 실제로 막히는지, post-commit은 커밋이 유지되고 트레일러만 빠지는지를 각각 단언한다
6. 실측 동작이 README에 쓴 문구와 다르면 **README를 실측에 맞춰 고친다** - 문서가 아니라 실제 동작이 기준이다
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
GF-108 진행 중 발견(2026-09-24): README.md:99의 `hooks/checks/<lang>.sh` 표기가 .py 포팅 후 죽은 경로가 된다. GF-108 범위 밖이라 손대지 않았으니 이 태스크의 README 갱신 때 같이 고칠 것(README.en.md에 대응 문구가 있으면 함께).

검증(2026-09-25, 부모 세션이 직접 재확인):
- bats tests/ 104/104 통과, 실패 0 (GF-112에서 100이었고 신규 4건 추가 - install 시점 1건, 실행 시점 3건)
- core.hooksPath 전체 스위트 전후 동일. 신규 install 케이스가 타깃을 명시해 GF-123 버그를 재현하지 않는다.
- ruff 8개 파일 All checks passed, shellcheck -s sh install.sh 클린
- README 거짓 문구 잔존 여부를 정규식으로 재확인: Runtime deps: none / runtime%20deps-none / npm~pip 같은 별도 런타임 / POSIX sh 훅 / 별도 런타임 의존성은 두지 / checks/<lang>.sh / Shell: POSIX sh 전부 0건
- 필요조건 섹션이 146행, 설치 안내가 170행으로 AC #1의 '설치 안내보다 먼저' 조건을 만족한다

AC #4는 이미 충족돼 있었다. GF-112가 만든 hooks/readme.md에 python3 실행 시점 PATH 요구사항과 훅별 비대칭이 이미 들어 있어, 중복해서 쓰지 않고 그대로 뒀다.

AC #7(비대칭의 객관적 증거)이 이 태스크의 핵심이라 테스트 설계를 직접 확인했다. 거짓 통과를 막는 가드가 세 겹이다:
1. setup()이 섀도 PATH에 python3이 없고 git은 여전히 동작하는지 먼저 단언한다 - 이게 없으면 PATH가 통째로 망가져 git이 죽는 경우에도 똑같이 통과한다.
2. git은 앞선 훅이 실패하면 뒤의 훅을 실행하지 않으므로, commit-msg/post-commit 케이스는 앞 훅을 제거한 hooks/ 사본으로 돌려 검증 대상 훅이 실제로 실행되게 한다.
3. 각 케이스가 같은 hooks 사본으로 정상 PATH에서 기준 커밋을 먼저 만들어 트레일러가 붙는 것을 확인한다 - 이게 없으면 트레일러 누락이 python3 부재 때문인지 훅 연결이 안 된 탓인지 구분할 수 없다.
차단 케이스는 종료 코드뿐 아니라 HEAD 불변과 커밋 수 불변까지 본다. 비대칭 케이스는 반대로 커밋이 존재하고(개수 2, 제목 일치) 트레일러만 없음을 본다.

범위 밖이라 남긴 것: doc-9(전환 계획)과 doc-8이 낡은 표현을 담고 있으나 둘 다 '그때 무엇을 계획/결정했는가'의 기록이라 고치면 이력이 왜곡된다. 의도적으로 두었다.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Python 전환의 유일한 실질적 트레이드오프인 python3 의존성을 문서화하고, sh 시절에는 없던 새 실패 모드를 테스트로 고정했다.

README에서 '런타임 의존성 없음' 주장은 한 곳이 아니라 다섯 형태로 반복되고 있었다 - 배지 두 개(Shell: POSIX sh, Runtime deps: none), 상단 소개 문구, 'POSIX sh 훅 3개', '별도 런타임 의존성은 두지 않았습니다'. 한 곳만 고치면 나머지가 계속 거짓말을 하므로 전부 바로잡고, 설치 안내보다 앞에 필요조건 섹션을 새로 넣었다. GF-108이 이 태스크로 넘겨둔 checks/<lang>.sh 잔여 참조도 함께 고쳤다.

문서의 핵심은 훅별 실패 비대칭이다. pre-commit/commit-msg는 python3을 못 찾으면 커밋이 막혀 바로 드러나지만, post-commit은 커밋이 이미 만들어진 뒤라 git이 실패를 반영하지 않는다 - 커밋은 성공한 것처럼 보이고 Task-Id/AI-Model/Signed-off-by만 조용히 사라진다. GUI git 클라이언트가 셸 프로파일 없이 OS 최소 PATH만 물려받는다는 점, 최신 macOS에 /usr/bin/python3가 없다는 점, install.sh의 확인이 설치 시점만 보장한다는 점을 함께 적었다.

그 서술이 실제로 맞는지 신규 bats 3건으로 증명했다. 종료 코드만 보는 테스트는 여기서 아무것도 증명하지 못하므로, 차단 케이스는 HEAD와 커밋 수가 그대로인지까지 보고 비대칭 케이스는 반대로 커밋이 존재하면서 트레일러만 없음을 본다. 거짓 통과를 막기 위해 섀도 PATH가 python3만 정확히 가렸는지, 같은 hooks 사본으로 정상 PATH에서는 트레일러가 붙는지를 각각 먼저 단언한다.

AC #4는 GF-112가 만든 hooks/readme.md에 이미 들어 있어 중복하지 않고 그대로 뒀다. GF-112에서 이월한 doc-5(저장소 구조)도 전환 후 상태로 갱신했다.

검증: bats tests/ 104/104 통과(실패 0), ruff 8개 파일 All checks passed, shellcheck -s sh install.sh 클린, core.hooksPath 스위트 전후 동일, README 거짓 문구 잔존 0건.
<!-- SECTION:FINAL_SUMMARY:END -->
