---
id: GF-64
title: verify.yml fetch-depth 안전성의 반복 가능한 테스트화
status: Done
assignee: []
created_date: '2026-08-27 20:29'
updated_date: '2026-08-27 21:05'
labels: []
dependencies: []
ordinal: 62000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GF-28에서 verify.yml이 caller의 fetch-depth 설정과 무관하게 안전한지(자체 체크아웃이 fetch-depth:0으로 고정돼 있어서) 확인했지만, 검증 근거가 과거 1회 실제 PR CI 로그 관찰이었지 반복 가능한 테스트로 고정되지는 않았다. 나중에 verify.yml을 수정하다 실수로 이 안전장치가 깨져도 자동으로 잡아줄 방법이 없다. act 같은 로컬 GitHub Actions 실행기를 쓰거나, 최소한 caller가 fetch-depth를 명시하지 않는 시나리오를 흉내 내는 반복 가능한 검증 방법을 마련한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 caller가 fetch-depth를 지정하지 않아도 verify.yml의 Conventional Commits 검증(git rev-list 기반)이 정상 동작함을 반복 실행 가능한 방식으로 검증한다(로컬 act 또는 실제 CI 워크플로 케이스)
- [x] #2 검증 방법과 한계(예: act 미설치 환경에서는 스킵됨 등)가 문서화된다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
act 등 로컬 GH Actions 실행기를 새로 설치하는 대신(새 의존성 도입 회피), verify.yml 자체에 체크아웃 직후 'git rev-parse --is-shallow-repository'로 얕은 클론이 아님을 확인하는 스텝을 추가했다. 이러면 이 워크플로가 실행될 때마다(=self-verify.yml을 통해 모든 PR마다) fetch-depth:0 전제가 매번 반복적으로 재검증된다 - 과거 1회 로그 관찰이 아니라 상시 CI 게이트가 됐다. 한계: 로컬에서 오프라인으로 재현 가능한 테스트는 아니고, 실제 GitHub Actions 실행 시에만 검증된다(act 미설치 환경에서는 이 방식 자체가 필요 없음 - 애초에 act에 의존하지 않는 접근이라 해당 없음). YAML 파싱 검증 통과.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
verify.yml에 fetch-depth:0 전제를 매 실행마다 재검증하는 얕은클론 확인 스텝을 추가해, 과거 1회 관찰이었던 안전성 확인을 상시 반복 가능한 CI 게이트로 전환했다. act 같은 새 의존성 도입 없이 git 자체 명령(rev-parse --is-shallow-repository)만 사용.
<!-- SECTION:FINAL_SUMMARY:END -->
