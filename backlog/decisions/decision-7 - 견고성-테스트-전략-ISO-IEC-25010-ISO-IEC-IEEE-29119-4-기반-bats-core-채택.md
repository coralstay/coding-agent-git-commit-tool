---
id: decision-7
title: '견고성 테스트 전략: ISO/IEC 25010 + ISO/IEC/IEEE 29119-4 기반, bats-core 채택'
date: '2026-08-24 04:47'
status: accepted
---
## Context

GF-1~20의 검증은 전부 애드혹 수동 테스트였다(격리 저장소를 매번 손으로 만들어
시나리오를 실행). 실제 PR 테스트(GF-20)에서 설계엔 있었지만 구현이 빠진 버그
(GF-15)와 심볼릭 링크 환경에서만 발생하는 버그(GF-16)를 뒤늦게 발견한 전례가
있어, 반복 가능하고 체계적인 테스트 전략이 필요했다. SQL 체크(GF-17/18)도
sqlfluff 미설치로 PATH 셔밍(가짜 실행파일)으로만 검증한 상태였다.

## Decision

- **품질 프레임**: ISO/IEC 25010 SQuaRE 품질모델의 Reliability > Fault
  Tolerance(결함 허용성, "robustness"의 공식 대응 용어) 및 Recoverability,
  Security, Portability, Compatibility 특성을 견고성 테스트의 기준으로 삼는다.
  출처: https://www.iso.org/standard/35733.html ,
  https://iso25000.com/index.php/en/iso-25000-standards/iso-25010/62-reliability
- **테스트 기법**: ISO/IEC/IEEE 29119-4의 black-box(동등분할/경계값분석/
  결정테이블/상태전이/페어와이즈/구문테스트)와 experience-based(오류추정/
  결함주입) 기법을 채택해 각 backlog 태스크의 acceptance criteria에 기법명을
  명시한다. 실무 참고서로 ISTQB Foundation Level Syllabus v4.0(비유료)을 곁들인다.
  출처: https://www.iso.org/standard/60245.html ,
  https://xbosoft.com/blog/iso-29119-summary-notes/ ,
  https://astqb.org/assets/documents/ISTQB_CTFL_Syllabus-v4.0.pdf
- **"Robustness Testing"/"Negative Testing"**: ISTQB 용어집상 별도 표제어로,
  위 기법들을 *적용해 달성하는 목적*으로 취급한다.
  출처: https://istqb-glossary.page/robustness-testing/
- **테스트 하네스**: bats-core(https://github.com/bats-core/bats-core) 채택.
  하네스 자체는 Bash가 필요하지만 `run sh ./hook.sh`로 배포용 POSIX sh 스크립트를
  그대로 구동·검증할 수 있어, hooks/*는 여전히 순수 POSIX sh로 유지하면서 테스트만
  dev 전용으로 bash를 쓸 수 있다. POSIX-순수 대안 shUnit2
  (https://github.com/kward/shunit2), 커버리지·모킹까지 지원하는 ShellSpec
  (https://github.com/shellspec/shellspec)도 검토했으나 생태계·CI 예제가 가장
  풍부한 bats-core를 최종 채택했다.
- **정적 분석**: 이미 로컬에 설치된 ShellCheck(v0.11.0, https://www.shellcheck.net/)를
  ISO 29119의 "정적 테스트"로 CI에 편입한다. 현재 hooks/ 전체 검사 결과 경고
  1건(`hooks/commit-msg`의 `case "$BRANCH" in $pattern)` — SC2254, `$pattern`을
  글롭으로 매칭하려는 의도적 설계라 오탐)만 발견됐고 인라인 disable로 처리한다.
- **실도구 재검증**: sqlfluff/ruff/clang-format/maven을 brew로 실제 설치해
  기존 PATH 셔밍 기반 테스트를 실도구 기반으로 대체한다(GF-22).

## Consequences

- 테스트 하네스(bats-core)가 Bash에 의존하므로 로컬 개발 환경에 Bash가 있어야
  테스트를 돌릴 수 있다 — 배포 대상(hooks/*)의 POSIX 순수성과는 무관.
- 실도구 5종 설치로 로컬 brew 환경에 패키지가 늘어난다(가역적).
- ISO 25010/29119-4는 원문이 유료라 ISTQB 무료 자료와 2차 요약을 근거로 인용한다
  — 표준 문서 자체를 직접 인용하지 않고 있다는 한계를 문서에 명시해둔다.
