---
id: decision-11
title: '서버사이드 검증 범위 제외: git-format은 클라이언트측 훅만 다룬다 (decision-3의 5번 항목 대체)'
date: '2026-09-03 06:58'
status: accepted
---
## Context

decision-3의 5번 항목("push까지 강제하려면 ... GitHub Actions에서 동일 검사를
재실행하는 서버사이드 백스톱을 두어야 하며, 이는 git-format이 제공하는
선택적(opt-in) 재사용 워크플로로 제공한다")에 따라 `.github/workflows/verify.yml`
(재사용 워크플로), `self-verify.yml`(이 저장소 자신의 dogfooding),
`docs/examples/github-actions-caller.yml`(컨슈머용 caller 예시)을 만들어
제공해왔다.

사용자가 이 방향을 재검토했다: git-format의 정체성은 "npm/pip 같은 런타임
없이 git 자체 기능만으로" 동작하는 클라이언트측 훅 도구인데, 유일한
서버사이드 백스톱을 GitHub Actions라는 특정 CI 벤더에 의존해 제공하는 건
이 정체성과 어긋난다. pre-receive 훅처럼 순수 git 기능으로 서버사이드를
푸는 대안도 검토했으나(GitHub.com은 pre-receive 훅에 대한 사용자 접근을
열어주지 않아 실효성이 제한적), 최종적으로는 "서버사이드/CI 기반 검증
자체를 이 프로젝트 범위에서 제외하고, 필요하면 별도 프로젝트에서 다룬다"는
방향으로 정리했다. 즉 특정 CI 벤더로 갈아타는 게 아니라, CI/서버사이드
검증이라는 카테고리 자체를 git-format의 스코프 밖으로 뺀다.

## Decision

- `.github/workflows/verify.yml`, `.github/workflows/self-verify.yml`,
  `docs/examples/github-actions-caller.yml`을 저장소에서 제거한다.
- `.github/workflows/test.yml`(이 저장소 자신의 shellcheck+bats 개발용 CI)은
  남긴다 — 이건 "컨슈머에게 제공하는 서버사이드 검증 제품"이 아니라 이
  프로젝트 자신의 코드 품질 게이트이므로 이번 스코프 축소와 무관하다.
  (구분 기준: 이 워크플로가 검증하는 대상이 "컨슈머의 커밋/PR"인가,
  "git-format 자신의 훅 코드"인가.)
- git-format이 제공하는 것은 여전히 `hooks/commit-msg`,
  `hooks/pre-commit`, `hooks/pre-push` 같은 순수 POSIX sh 스크립트뿐이다.
  이 스크립트들은 CI 환경 여부와 무관하게 그대로 호출 가능하도록 설계돼
  있으므로(실제로 옛 verify.yml도 로직 재구현 없이 이 스크립트들을 그대로
  호출했었다), 서버사이드 검증이 필요한 컨슈머는 자신의 CI/서버
  pre-receive 훅에서 이 스크립트들을 직접 호출해 구성하면 된다 — 다만 그
  구성 자체는 git-format이 만들어 배포하지 않는다.
- decision-3의 1~4번(pre-commit 검증마커 → post-commit이 `--no-verify`를
  감지해 `Verify-Bypassed: true` 트레일러를 프로그래밍적으로 삽입하는
  메커니즘)은 이 decision과 무관하게 그대로 유효하다. 대체되는 건 5번의
  "git-format이 opt-in 재사용 워크플로를 제공한다"는 부분뿐이다 — 5번
  앞부분의 사실 설명("push 단계는 로컬 훅으로 탐지 불가능하다는 git
  구조상의 한계")도 그대로 유효하다.

## Consequences

- git-format을 설치하는 컨슈머는 더 이상 `docs/examples/github-actions-caller.yml`을
  복사해 쓸 수 없다 — push 단계 백스톱이 필요하면 직접 만들어야 한다.
- decision-8이 test 범위로 나열했던 "GitHub Actions 워크플로(GF-28)"는 그
  대상(verify.yml/self-verify.yml)이 이제 존재하지 않아 의미를 잃는다.
  decision-8 파일 자체와 GF-28/GF-32/GF-64/GF-20/GF-12/GF-66 같은 관련
  과거 태스크는 이미 완료된 작업의 역사적 기록이므로 소급 수정하지 않는다.
- README/`install.sh`의 관련 안내 문구, 저장소 구조 트리, 한계 섹션을 이
  decision에 맞게 갱신한다(GF-85).
- 이 프로젝트의 유일한 "우회 흔적 남기기" 보장은 이제 로컬 커밋 이력에
  남는 `Verify-Bypassed: true` 트레일러뿐이며, push 단계까지의 강제는
  전적으로 컨슈머의 몫이라는 점을 README가 명확히 해야 한다.

