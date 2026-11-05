---
id: decision-6
title: SQL 지원 추가 (sqlfluff 기반)
date: '2026-08-24 04:29'
status: accepted
---
## Context

TS/C·C++/Java/Python 4개 언어로 시작했지만, SQL(마이그레이션/쿼리 파일)을 다루는
프로젝트에도 같은 훅 프레임워크를 적용하고 싶다는 요구가 추가됐다. SQL은 다른
언어와 달리 `package.json` 같은 단일 매니페스트 파일이 없어 언어 감지 방식을
다르게 잡아야 한다.

## Decision

- **언어 감지**: `.sqlfluff` 설정 파일이 있거나, `git ls-files -- '*.sql'`로 추적된
  `.sql` 파일이 하나라도 있으면 SQL 프로젝트로 간주한다.
- **lint 도구**: [sqlfluff](https://sqlfluff.com/)를 채택한다 — 여러 SQL dialect를
  지원하는 사실상 표준 SQL 린터. 다른 언어 체크와 마찬가지로 도구가 없으면 조용히
  건너뛴다(강제 설치 요구 안 함).
- **pre-commit**(`hooks/checks/sql.sh`): C/C++와 동일한 패턴으로 스테이징된
  `.sql` 파일만 lint한다(빠른 피드백).
- **pre-push**: 저장소 전체를 대상으로 `sqlfluff lint .`를 실행한다(다른 언어의
  pre-commit=가벼움/pre-push=무거움 원칙과 동일).

## Consequences

- sqlfluff 미설치 환경에서는 SQL 검증이 그냥 스킵된다 — 다른 언어와 동일한 트레이드오프.
- dialect(PostgreSQL/MySQL/... )별 설정은 프로젝트의 `.sqlfluff` 파일에 위임하고
  git-format은 dialect를 강제하지 않는다.
