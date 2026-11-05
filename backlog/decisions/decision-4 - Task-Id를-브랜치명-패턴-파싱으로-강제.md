---
id: decision-4
title: Task-Id를 브랜치명 패턴 파싱으로 강제
date: '2026-08-24 03:09'
status: accepted
---
## Context

각 커밋이 어떤 backlog 태스크(GF-3 등)에 속하는지 커밋 메시지에 남기고 싶다. 사람이나
에이전트가 커밋할 때마다 수동으로 taskId를 타이핑하게 하면 잊어버리기 쉽고, 강제할 방법도
없다(텍스트 안내에 불과). 반면 브랜치명은 작업을 시작하는 시점에 한 번만 정하고, git이
`git symbolic-ref --short HEAD`로 항상 조회 가능한 값이라 프로그래밍적으로 검증·강제하기
좋은 지점이다.

## Decision

- 브랜치명에 `GF-<번호>` 패턴(설정 가능한 접두어, 기본값은 backlog task prefix와 동일)이
  포함되어야 한다는 규칙을 둔다. 예: `gf-3-pre-commit-dispatcher`, `feature/GF-12-install-script`.
- `commit-msg` 훅이 커밋마다 현재 브랜치명을 정규식으로 검사한다.
  - 패턴이 매치되면 → 이후 `post-commit` 단계에서 `Task-Id: GF-3` 트레일러를 자동 삽입.
  - 패턴이 없고, 현재 브랜치가 예외 목록(`git config --get-all gitformat.branchExempt`,
    기본값 `main`, `master`, `develop`, `release/*`)에도 없으면 → **커밋 자체를 거부**
    (exit 1, 안내 메시지 출력).
- 예외 브랜치에서는 Task-Id 없이 커밋 가능(직접 커밋/핫픽스/머지 커밋 대응).

## Consequences

- 태스크 없이 만든 임시 브랜치에서는 커밋이 막히므로, 작업 시작 시 브랜치명 규칙을
  지키는 습관이 강제된다 — 처음 도입 시 팀 온보딩 문서화 필요.
- 브랜치를 나중에 rename하면(`git branch -m`) 그 이후 커밋부터 다른 Task-Id가 붙을 수 있음
  — 의도된 동작이지만 문서에 명시.
- prefix가 다른 멀티 레포(예: 다른 프로젝트는 `PROJ-`)에서도 재사용 가능하도록 접두어는
  `git config gitformat.taskPrefix`로 오버라이드 가능하게 만든다(기본 `GF`).
