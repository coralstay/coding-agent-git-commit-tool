---
id: decision-2
title: core.hooksPath + init.templateDir 이원화 배포
date: '2026-08-24 02:45'
status: superseded
---
## Context

여러 언어(TS, C/C++, Java, Python) 프로젝트에 훅을 배포해야 하는데, 프로젝트는 이미 존재하는
경우(기존 저장소)와 앞으로 새로 만들어질 경우(신규 저장소) 두 가지가 있다. 하나의 git 설정
메커니즘만으로는 두 경우를 모두 커버하지 못한다.

## Decision

두 가지 git 기능을 함께 사용한다.

1. **`core.hooksPath`** — 기존 저장소용. git-format 저장소를 clone/submodule로 옆에 두고,
   `install.sh`가 `git config core.hooksPath <path>/hooks` 와
   `git config commit.template <path>/.gitmessage` 를 설정한다. 런타임 의존성 없음(POSIX sh).
2. **`init.templateDir`(global)** — 신규 저장소용. `git config --global init.templateDir
   <path>/template` 을 한 번 설정해두면 이후 모든 `git init`/`git clone`이 자동으로 훅과
   `.gitmessage`를 심는다.

`install.sh`는 두 가지를 모두 제안(기존 저장소엔 core.hooksPath, 전역 설정 여부를 물어
init.templateDir도 옵션으로 설정)한다.

## Consequences

- 기존/신규 저장소를 모두 커버하지만 설정 지점이 두 곳이라 문서화가 중요하다.
- `template/`와 `hooks/`의 내용이 어긋나지 않도록 `template/hooks`는 `hooks/`의 심볼릭
  링크 또는 install.sh가 동기화되도록 관리해야 한다(중복 유지보수 방지).
- `core.hooksPath`가 설정된 저장소는 `.git/hooks/`의 로컬 훅이 완전히 무시되므로, 팀원에게
  이 사실을 README에 명확히 알려야 한다(기존 로컬 커스텀 훅과 충돌 가능).
