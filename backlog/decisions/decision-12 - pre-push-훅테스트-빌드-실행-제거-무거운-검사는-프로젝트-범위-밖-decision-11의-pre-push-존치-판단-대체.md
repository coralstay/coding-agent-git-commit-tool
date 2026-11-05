---
id: decision-12
title: 'pre-push 훅(테스트/빌드 실행) 제거: 무거운 검사는 프로젝트 범위 밖 (decision-11의 pre-push 존치 판단 대체)'
date: '2026-09-03 11:09'
status: accepted
---
## Context

decision-11은 서버사이드(GitHub Actions 재사용 워크플로) 백스톱만 git-format
범위에서 뺐고, `hooks/pre-push`(테스트/전체 빌드 실행: npm test/build, pytest,
mvn verify/gradle check, cmake+ctest, sqlfluff 전체 lint) 자체는 "여전히
git-format이 제공하는 것"이라고 명시했었다.

사용자가 이 판단을 재검토했다: `pre-push`가 하는 "무거운 검사"(테스트 실행,
전체 빌드)는 커밋 규칙 검증·형식 정형화라는 git-format의 핵심 정체성(커밋
단계의 가벼운 훅 도구)과 성격이 다르고, 프로젝트 스코프에 맞지 않는다는
결론에 도달했다. `pre-commit`의 언어별 lint/컴파일 검사와 달리 `pre-push`의
테스트/빌드 실행은 실행 시간이 길고, 언어별 테스트 러너에 대한 가정(스크립트
이름, 종료 코드 규약 등)이 더 깊어 유지보수 부담도 크다.

## Decision

- `hooks/pre-push`를 저장소에서 완전히 삭제한다. git-format은 이제
  `commit-msg`/`pre-commit`/`post-commit`(커밋 단계)까지만 다루고, push
  단계는 전혀 훅하지 않는다.
- `hooks/gitformat.conf`의 `buildDir` 키(`.gitformat-build` 산출물 디렉터리
  이름, pre-push 전용)를 제거한다.
- `install.sh`의 C/C++ 프로젝트 `.gitformat-build/` 자동 `.gitignore` 추가
  로직을 제거한다 — pre-push가 없으면 이 디렉터리 자체가 생기지 않으므로
  보호할 대상이 없다.
- decision-11의 나머지 판단(서버사이드/CI 기반 검증을 이 프로젝트 범위에서
  제외한다는 것, `commit-msg`/`pre-commit`은 여전히 제공한다는 것)은 이
  decision과 무관하게 그대로 유효하다. 대체되는 건 "`pre-push`(push 단계
  테스트/빌드 실행)도 여전히 제공한다"는 부분뿐이다.
- decision-3의 5번 항목("`git push --no-verify`는 로컬에서 탐지 불가능하다는
  git 구조상의 한계")도 그대로 유효하다 — 이제는 애초에 push 단계를 훅하지
  않으므로 이 한계가 더 근본적으로 적용된다.

## Consequences

- git-format을 설치하는 컨슈머는 더 이상 push 시점에 테스트/전체 빌드가
  자동으로 실행되지 않는다. 필요하면 컨슈머가 직접 CI나 로컬 git 설정으로
  구성해야 한다.
- `.gitformat-build/` 산출물, 관련 `.gitignore` 자동 추가 안내는 더 이상
  발생하지 않는다.
- README/README.en.md의 실제 사용법(push 워크플로), 훅이 하는 일 표, SQL
  섹션, 저장소 구조 트리, 한계 섹션, "왜 만들었나" 섹션을 이 decision에
  맞게 갱신한다(GF-86).
- `tests/`의 `conf-guard.bats`/`robustness-dispatch.bats`/`consistency.bats`/
  `robustness-install.bats`에서 `pre-push`와 `.gitformat-build` 자동
  `.gitignore`를 검증하던 테스트를 제거·수정한다(GF-86).

