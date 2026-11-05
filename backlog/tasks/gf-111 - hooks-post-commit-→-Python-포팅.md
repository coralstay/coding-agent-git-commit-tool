---
id: GF-111
title: hooks/post-commit → Python 포팅
status: Done
assignee:
  - '@claude'
created_date: '2026-09-24 09:24'
updated_date: '2026-09-24 18:15'
labels:
  - python-migration
  - hooks
milestone: m-3
dependencies:
  - GF-110
documentation:
  - doc-9
  - doc-10
modified_files:
  - hooks/post-commit
  - .github/workflows/test.yml
type: enhancement
ordinal: 5
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## 왜

post-commit은 423줄로 전환 대상 중 가장 크고, 트레일러 삽입/우회 탐지/AI 귀속 측정이 얽혀 있어 마지막에 포팅한다. pre-commit이 쓰는 .gitformat-verified 마커를 읽는 역할이라 코드 의존은 없지만(마커는 포맷 기반 계약이라 sh/Python 상관없이 상호운용됨) 마커를 쓰는 쪽을 먼저 포팅한 뒤 읽는 쪽을 포팅하는 순서가 원인 추적에 유리하다.

## 무엇을

hooks/post-commit을 #!/usr/bin/env python3 단일 파일로 포팅한다.

그대로 유지해야 하는 것(단순화 금지 대상):
- amend 재귀 방지 가드(_GITFORMAT_AMEND_GUARD 환경변수 확인)가 반드시 맨 먼저 실행돼야 한다. post-commit이 git commit --amend로 트레일러를 삽입하므로 이 가드가 없거나 늦으면 무한 재귀한다
- git interpret-trailers --if-exists는 키를 정확 일치가 아니라 접두어로 매칭한다(GF-33) - 이 때문에 지금 코드는 --if-exists에 기대지 않고 "key: value" 줄을 직접 파싱한다. Python으로 옮길 때 interpret-trailers를 믿고 단순화하면 안 된다
- Verify-Bypassed(마커 부재 = --no-verify 우회), Task-Id, AI-Tool/AI-Tool-Version/AI-Model, Co-Authored-By, Tokens-Used/Tool-Calls, Hooks-Commit, Signed-off-by 트레일러 삽입 로직 전부
- TASK_PREFIX/BRANCH 계산은 commit-msg와 동일 유지(파일별 독립 중복)

정당한 개선: jq 서브프로세스 호출을 json.loads()로 대체한다 - Claude Code 트랜스크립트 파싱에 쓰던 jq 의존성이 사라진다. 단 현재의 fail-open 단위를 바꾸면 안 된다: 지금은 jq -s로 한 줄이라도 파싱 실패하면 배치 전체가 실패해 MEASUREMENT_REASON="transcript-parse-failed"로 기록된다. 개별 불량 줄만 조용히 건너뛰는 식으로 바꾸면 동작 변경이다.

의도적 예외 유지: AI-Model 트랜스크립트 조회는 실패 시 조용히 트레일러를 생략하는 fail-open이 의도된 동작이다(decision-5). 이 한 곳만 좁은 try/except로 감싸고, 나머지 subprocess 호출은 실패 시 예외를 던지게 한다(GF-76의 조용한 실패 전파 방지).

CI: 같은 커밋에서 test.yml shellcheck 대상에서 hooks/post-commit 제거 - 이 시점에 install.sh만 남는다.

## 선행/병렬

코드 의존은 없다(마커는 포맷 기반 계약이라 pre-commit이 sh든 Python이든 상호운용된다). 다만 마커를 쓰는 쪽(pre-commit, GF-110)을 먼저 포팅한 뒤 읽는 쪽을 포팅하는 순서가 문제 발생 시 원인 추적에 유리하므로 GF-110 이후를 권장한다(강제 아님).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 hooks/post-commit이 #!/usr/bin/env python3 셔뱅의 단일 Python 파일로 포팅되고, amend 재귀 방지 가드가 다른 어떤 작업보다 먼저 실행된다
- [x] #2 Verify-Bypassed(마커 부재 = --no-verify 우회), Task-Id, AI-Tool/AI-Tool-Version/AI-Model, Co-Authored-By, Tokens-Used/Tool-Calls, Hooks-Commit, Signed-off-by 트레일러 삽입이 sh 버전과 동일하게 동작한다
- [x] #3 git interpret-trailers --if-exists의 접두어 매칭 문제(GF-33)를 피하기 위해 기존처럼 'key: value' 줄을 직접 파싱하는 방식이 유지된다(interpret-trailers를 믿고 단순화하지 않음)
- [x] #4 jq 서브프로세스 호출이 json.loads()로 대체되어 jq 의존성이 제거되되, 한 줄이라도 파싱 실패 시 배치 전체를 실패 처리해 MEASUREMENT_REASON=transcript-parse-failed로 기록하는 현재의 fail-open 단위가 그대로 유지된다
- [x] #5 AI-Model 트랜스크립트 조회만 좁은 try/except로 감싸 실패 시 트레일러를 생략하는 의도된 fail-open(decision-5)을 유지하고, 나머지 subprocess 호출은 실패 시 예외를 던진다(GF-76 조용한 실패 전파 방지)
- [x] #6 TASK_PREFIX/BRANCH 계산 블록이 commit-msg와 동일하게 유지되고(파일별 독립 중복), 모든 subprocess.run에 encoding=utf-8이 명시된다
- [x] #7 같은 커밋에서 test.yml shellcheck 대상에서 hooks/post-commit이 제거되어 install.sh만 남는다
- [x] #8 bats tests/robustness-post-commit.bats 통과 후 bats tests/ 전체를 1회 재실행해 교차 파일 정합성을 확인한다
- [x] #9 범위 추가(앞선 포팅 태스크들과 같은 성격): tests/conf-guard.bats의 post-commit 실행을 python3로 교체하고, jq 제거로 존재하지 않게 된 동작을 검증하던 테스트 2건을 삭제한다(unavailable (jq-not-installed) 검증, jq 부재 시 커밋 비차단). 함께 있던 'jq가 없으면 skip' 가드 5개도 제거해 해당 케이스들이 모든 환경에서 실제로 돌게 한다. 근거는 doc-12의 '메커니즘이 사라진 테스트는 삭제, 행위 검증은 유지' 방침
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
1. hooks/post-commit(sh, 423줄)을 읽고 트레일러별 로직을 분해한다
2. amend 재귀 방지 가드를 main() 최상단에 배치 - 환경변수 확인 후 즉시 종료. post-commit이 git commit --amend를 호출하므로 이 가드가 늦으면 무한 재귀한다
3. 트레일러 존재 확인은 git interpret-trailers --parse 출력을 "key: value"로 직접 파싱(--if-exists의 접두어 매칭에 의존 금지 - GF-33)
4. 트랜스크립트 파싱을 jq에서 json.loads()로 전환하되, jq -s의 all-or-nothing 실패 단위를 유지한다(한 줄이라도 실패하면 전체를 transcript-parse-failed로 기록)
5. AI-Model 조회만 좁은 try/except로 감싸고(decision-5의 의도된 fail-open), 나머지 subprocess는 실패 시 예외를 던지게 한다
6. TASK_PREFIX/BRANCH 블록은 GF-109의 commit-msg와 동일하게 유지
7. 같은 커밋에서 shellcheck 대상에서 hooks/post-commit 제거 → install.sh만 남는다
8. bats tests/robustness-post-commit.bats 실행 후 bats tests/ 전체를 1회 더 실행
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
검증(2026-09-25, 부모 세션이 직접 재확인):
- bats tests/ 99/99 통과, 실패 0, skip 0. 총계가 101에서 99로 준 것은 jq 제거로 무의미해진 케이스 2건을 지웠기 때문이다(AC #9).
- core.hooksPath 전체 스위트 전후 동일
- ruff: hooks/ + 셔뱅 탐색 8개 파일 All checks passed
- shellcheck 대상이 install.sh 하나만 남았다 - decision-16이 예고한 최종 상태다. hooks/ 3개 파일 모두 첫 줄이 #!/usr/bin/env python3인 것을 확인했다.
- AC #4(파싱 실패 단위)를 직접 손으로 재확인: 격리 저장소 + 가짜 트랜스크립트로 1차 커밋 Tokens-Used 150/Tool-Calls 1/커서 1, 이후 유효한 줄(2010토큰)과 불량 줄을 함께 추가하고 2차 커밋 → unavailable (transcript-parse-failed), 커서 1 그대로. 유효한 줄이 부분 집계되지 않았고 커서가 갱신되지 않아 다음 커밋이 같은 지점부터 재시도한다. 커밋 수 2로 amend 재귀도 없다.

sh와 의도적으로 달라진 곳 세 가지:
1. Task-Id 번호 추출. sh는 grep -oE '[0-9]+' | head -1이라 매치 문자열 안의 첫 숫자 덩어리를 집는다 - taskPrefix에 숫자가 있으면(예: GF2, 브랜치 GF2-14) 접두어의 '2'를 번호로 오인해 Task-Id: GF2-2가 된다. 정규식 그룹으로 접두어 뒤 숫자만 집도록 바꿨다. 기본 접두어 GF에는 숫자가 없어 실사용 차이는 없지만 잠재 버그를 이식하지 않기로 판단했다.
2. PROJECT_SLUG의 기준 경로. sh는 $PWD를 쓰는데 os.getcwd()는 심볼릭 링크를 해석한 물리 경로를 돌려준다(macOS에서 /var vs /private/var). 그대로 쓰면 Claude Code가 실제로 만든 세션 디렉터리 슬러그와 어긋나 트랜스크립트를 영영 못 찾는다. POSIX 셸의 PWD 초기화와 동일하게, 환경변수 PWD가 현재 디렉터리를 가리키는 절대경로일 때만 그 값을 쓰고 아니면 getcwd()로 폴백한다.
3. 커밋 메시지 디코딩에 errors='replace'가 아니라 'surrogateescape'를 썼다. commit-msg는 메시지를 읽기만 하지만 post-commit은 amend로 다시 쓰므로, replace를 쓰면 디코딩 불가 바이트가 U+FFFD로 조용히 치환돼 유저의 커밋 메시지가 변조된다. surrogateescape는 원래 바이트로 되돌아가 왕복이 무손실이고 예외도 나지 않는다.

이번 작업에서 발견했으나 범위 밖이라 손대지 않은 것:
- transcript-parse-failed를 검증하는 bats 케이스가 없다. AC #4가 고정하는 동작인데 스위트가 보호하지 않는다. 손으로만 확인했다. GF-112(전체 검증)에서 채우는 것이 적절하다.
- README.md:126과 backlog/docs/doc-3의 사유 슬러그 목록에 이제 발생하지 않는 jq-not-installed가 남아 있다. 문서 갱신은 GF-112/GF-113 소관이다.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/post-commit(423줄, 전환 대상 중 가장 큼)을 표준 라이브러리만 쓰는 단일 Python 파일로 포팅했다. 이로써 hooks/ 8개 파일이 전부 Python이 되고 shellcheck 대상은 install.sh 하나만 남았다(decision-16의 최종 상태).

단순화하지 않고 그대로 지킨 것:
- amend 재귀 가드가 파일에서 가장 먼저 실행된다. 이 훅이 git commit --amend로 트레일러를 넣고 그 amend가 post-commit을 재발동시키므로, 늦으면 재귀가 깊어지고 빠지면 무한 재귀가 된다.
- git interpret-trailers --if-exists의 접두어 매칭에 기대지 않고 'key: value' 줄을 직접 정확 일치로 비교한다(GF-33). Python으로 옮기며 표준 도구를 믿는 쪽으로 단순화했다면 그 버그가 되살아났을 자리다.
- jq를 json.loads()로 대체하되 파싱 실패 단위를 바꾸지 않았다. jq -s는 전체를 한 번에 슬러프해 한 줄이라도 깨지면 배치 전체가 실패하는데, 불량 줄만 건너뛰게 만들면 조용한 동작 변경이다. 손으로 직접 재확인했다.
- AI-Model 조회와 Hooks-Commit 조회만 좁은 fail-open으로 두고 나머지 subprocess 실패는 예외를 던진다(GF-76).

의도적으로 sh와 달라진 곳: Task-Id 번호 추출이 접두어 속 숫자를 오인하던 잠재 버그를 이식하지 않았고, PROJECT_SLUG 기준 경로를 셸의 PWD 의미론으로 맞췄으며(getcwd()는 심볼릭 링크를 해석해 슬러그가 어긋난다), 커밋 메시지 디코딩에 surrogateescape를 써서 amend 왕복이 무손실이 되게 했다.

jq 제거로 unavailable (jq-not-installed) 사유가 사라져, 그것을 검증하던 테스트 2건을 doc-12 방침에 따라 삭제했다(101 → 99). 함께 있던 'jq 없으면 skip' 가드 5개도 제거해 해당 케이스들이 모든 환경에서 실제로 돈다.

검증: bats tests/ 99/99 통과(실패 0, skip 0), ruff 8개 파일 All checks passed, shellcheck install.sh 클린, core.hooksPath 스위트 전후 동일, 파싱 실패 단위/커서 델타/재귀 가드를 격리 저장소에서 직접 확인.
<!-- SECTION:FINAL_SUMMARY:END -->
