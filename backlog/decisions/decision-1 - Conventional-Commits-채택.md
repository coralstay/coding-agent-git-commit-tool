---
id: decision-1
title: Conventional Commits 채택
date: '2026-08-24 02:44'
status: accepted
---
## Context

TS, C/C++, Java, Python 등 언어가 다른 여러 프로젝트에 동일한 커밋 메시지 규칙을 적용해야 한다.
언어 특화 규칙이 아니라 업계에서 이미 널리 쓰이고 도구 생태계(체인지로그 자동 생성, semver 자동
산정 등)와 잘 맞는 표준이 필요하다.

## Decision

[Conventional Commits v1.0.0](https://www.conventionalcommits.org/ko/v1.0.0/)을 채택한다.

- 커밋 메시지 구조: `<type>[(scope)][!]: <description>` + 빈 줄 + `[body]` + 빈 줄 + `[footer]`
- 허용 type 11종: `feat`(MINOR), `fix`(PATCH), `docs`, `style`, `refactor`, `perf`, `test`,
  `build`, `ci`, `chore`, `revert`
- Breaking change는 `type!:` 또는 footer의 `BREAKING CHANGE:` (MAJOR)
- 이 규칙은 `commit-msg` 훅에서 정규식으로 검증하고, `.gitmessage` 템플릿에도 동일한 type
  목록을 주석으로 노출한다.
- 원문은 `docs/references/conventional-commits-ko.md`로 로컬 vendoring해 오프라인에서도
  참조 가능하게 한다.

## Consequences

- 모든 언어 프로젝트가 동일한 정규식/화이트리스트를 공유하므로 유지보수 지점이 하나로 줄어든다.
- CHANGELOG 자동 생성, semver 자동 산정 같은 후속 도구 연동이 쉬워진다.
- 기존에 다른 커밋 컨벤션(예: 지라 티켓 접두어)을 쓰던 팀은 마이그레이션 비용이 발생할 수 있다.
