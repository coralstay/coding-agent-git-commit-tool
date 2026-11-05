---
id: GF-89
title: '코드 품질 도구 리서치: SonarQube/CodeQL 등 정적 분석·보안 스캔 도구 적용 검토'
status: Done
assignee: []
created_date: '2026-09-03 11:31'
updated_date: '2026-09-03 12:31'
labels: []
milestone: m-0
dependencies: []
ordinal: 87000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
지금은 shellcheck(-s sh)와 bats-core 테스트(decision-8)만으로 코드 품질을 관리하고 있다. SonarQube, CodeQL 같은 정적 분석/보안 스캔 도구를 추가로 도입할 가치가 있는지 조사한다. 참고: CodeQL은 공식적으로 Bash/POSIX sh를 지원하지 않는다(C/C++, C#, Go, Java/Kotlin, JS/TS, Python, Ruby, Swift만 지원) - 이 프로젝트가 셸을 유지하기로 한 결정(GF-88 종료 사유)과 맞물려 실제 적용 가능 여부부터 확인해야 한다. SonarQube는 커뮤니티 셸 분석 플러그인이 있는지, 있다면 shellcheck 대비 추가 가치가 있는지를 본다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 SonarQube가 POSIX sh/bash를 실제로 분석할 수 있는지(공식 지원 여부, 플러그인 필요 여부) 확인된다
- [x] #2 CodeQL의 언어 지원 범위와 이 프로젝트(POSIX sh 훅)에 적용 가능한지 여부가 확인된다
- [x] #3 두 도구가 이미 쓰고 있는 shellcheck -s sh 대비 실제로 추가 가치(잡아내는 이슈 종류, 오탐률 등)가 있는지 비교된다
- [x] #4 무료/오픈소스 사용 범위에서 이 공개 저장소에 CI로 통합 가능한지(비용, rate limit, 설정 난이도) 확인된다
- [x] #5 도입 여부에 대한 권고가 정리되고, 도입한다면 어떤 도구를 어느 워크플로(.github/workflows/test.yml)에 추가할지 방안이 나온다
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. CodeQL 언어 지원 범위를 웹 검색으로 확인 (AC #2)
2. SonarQube의 Shell(bash/POSIX) 분석 지원 여부를 웹 검색/공식 문서로 확인 (AC #1)
3. SonarQube Shell 분석기의 규칙 카테고리(버그/취약점/코드스멜/보안 핫스팟)와
   shellcheck 대비 차별점 확인 (AC #3)
4. SonarQube Cloud의 공개 저장소 무료 티어, 설정 난이도(계정/토큰 필요 여부) 확인 (AC #4)
5. 위 근거를 종합해 도입 여부 권고 정리 (AC #5)

코드 변경 없는 순수 리서치 태스크라 구현 단계는 없음. 근거는 implementation
notes에 출처 링크와 함께 기록한다.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
[AC #1] SonarQube는 Bash/POSIX Shell 분석을 공식 지원한다 - 단, 2026년 기준
SonarQube Cloud에서 "beta"로 막 출시된 상태다(SonarSource 커뮤니티 확인:
"Yes, we have just released the analyzer"). ksh/zsh 등 다른 셸 방언은 부분
지원만 된다. 출처: https://docs.sonarsource.com/sonarqube-cloud/analyzing-source-code/languages/shell , https://community.sonarsource.com/t/support-for-shell-sh-bash-is-available-in-beta-on-sonarqube-cloud/149807

[AC #2] CodeQL은 C/C++/C#/Go/Java/Kotlin/JS/TS/Python/Ruby/Swift/Rust만
지원하고 Bash/Shell은 지원 언어 목록에 없다 - git-format 훅(전부 POSIX sh)에
적용 불가능. 출처: https://codeql.github.com/docs/codeql-overview/supported-languages-and-frameworks/

[AC #3] SonarQube Shell 분석기는 버그/취약점/코드 스멜/보안 핫스팟 4개
카테고리로 규칙을 분류한다 - shellcheck은 이런 보안 중심 분류 없이 이식성/
정확성 린팅에 집중한다는 점에서 카테고리 자체는 다르다. 다만 이 저장소
훅은 이미 shellcheck -s sh를 전체 통과하고 있고(GF-86/87 검증 포함), 개별
규칙 단위 비교(예: 구체적으로 어떤 취약점 패턴을 SonarQube만 잡는지)는
베타 분석기 특성상 문서에 상세 목록이 공개돼 있지 않아 실제로 설치해봐야
확인 가능 - 이 리서치 범위에서는 실측하지 않음.

[AC #4] SonarQube Cloud는 공개 오픈소스 저장소에 대해 무료(LOC 무제한 명시,
50k LOC는 private 기준) - git-format 전체 셸 코드가 수백~1천 줄 수준이라
비용 문제는 없다. 다만 SonarCloud 계정 생성, 저장소 연동, SONAR_TOKEN
GitHub Actions secret 설정이 필요해 지금의 shellcheck(추가 계정/토큰 없이
바로 실행)보다 설정 단계가 늘어난다. 출처: SonarQube Cloud pricing 검색
결과(2026) 다수 소스 교차 확인.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
결론: 현재는 SonarQube/CodeQL 둘 다 도입하지 않는다.

- CodeQL: Bash/POSIX sh를 공식 지원하지 않아(C/C++/C#/Go/Java/Kotlin/JS/TS/
  Python/Ruby/Swift/Rust만 지원) 이 저장소 훅에 적용 불가능.
- SonarQube: Shell(bash/POSIX) 분석을 2026년에 공식 지원하기 시작했지만
  SonarQube Cloud 기준 아직 beta 상태다. 공개 저장소는 무료(비용 문제 없음)지만
  SonarCloud 계정 생성 + SONAR_TOKEN GitHub Actions secret 설정이 추가로
  필요해, 지금 쓰는 shellcheck -s sh(추가 계정/토큰 없이 바로 실행)보다
  설정/유지보수 부담이 늘어난다. 규칙 카테고리(버그/취약점/코드스멜/보안
  핫스팟)는 shellcheck과 다르지만, 이 저장소 코드량이 수백~1천 줄 수준으로
  작고 이미 shellcheck -s sh를 전체 통과하고 있어(GF-86/87 검증 포함) 베타
  단계 도구를 지금 도입할 유인이 크지 않다.
- 이 프로젝트가 이번 세션에서 반복적으로 확인한 방향(decision-11의 서버사이드
  검증 범위 축소, decision-14의 vendoring 제거)과도 일관된다 - 외부 의존성/
  이동 부품을 늘리기보다 최소 구성을 유지하는 쪽.
- 재검토 트리거: SonarQube Shell 분석기가 GA로 전환되거나, 저장소 코드량이
  크게 늘어나 shellcheck만으로 부족하다고 느껴질 때.

근거는 Implementation Notes에 출처 링크와 함께 기록. 코드/CI 설정 변경 없음
(순수 리서치 결론 - 도입하지 않기로 했으므로).
<!-- SECTION:FINAL_SUMMARY:END -->
