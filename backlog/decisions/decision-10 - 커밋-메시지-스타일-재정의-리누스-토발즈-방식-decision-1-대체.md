---
id: decision-10
title: '커밋 메시지 스타일 재정의: 리누스 토발즈 방식 (decision-1 대체)'
date: '2026-09-03 06:39'
status: accepted
---
## Context

decision-1은 여러 언어 프로젝트가 커밋 규칙을 공유할 표준으로 Conventional
Commits를 채택하면서, CHANGELOG 자동 생성·semver 자동 산정 같은 도구 생태계
연동을 근거로 들었다. 그런데 이 프로젝트는 실제로 그런 도구를 연동한 적이
없고, 커밋 이력의 핵심 목적은 오히려 "무엇을 왜 바꿨는지"를 사람과 LLM이
`git log`만으로 정확히 읽어내는 것(GF-41, README 🎯 목적 섹션)이다. 사용자가
커밋 스타일을 리누스 토발즈(리눅스 커널) 방식으로 바꾸자고 요청했다 —
원인 중심의 본문, 원자적 커밋, `Signed-off-by`/`Fixes:` 같은 트레일러 관행이
이 목적에 Conventional Commits의 type/scope 분류 체계보다 더 잘 맞는다는
판단이다. 다만 서브젝트를 리누스 스타일의 자유 산문(`subsystem: description`)
그대로 가져가면 `gitformat.conf`의 type 화이트리스트 검증(기계적으로 파싱
가능한 카테고리를 유지하는 것 자체는 여전히 유효한 가치)을 잃게 되므로,
"타입 화이트리스트는 유지하되 표기만 대괄호로 바꾼다"는 절충안을 택했다.

## Decision

- 서브젝트 형식: `[type][subsystem] <description>` + 빈 줄 + `[body]` +
  `[footer(s)]`. `subsystem`은 생략 가능(`[type] <description>`).
- 허용 type 11종은 decision-1과 동일하게 유지: `feat` `fix` `docs` `style`
  `refactor` `perf` `test` `build` `ci` `chore` `revert`.
- BREAKING CHANGE `!` 마커는 제거한다 — 리누스 스타일에는 SemVer 개념이
  없고, 이 프로젝트가 semver 자동화를 실제로 연동한 적도 없다. 필요하면
  footer에 `BREAKING CHANGE: <설명>`으로만 표시한다(이건 원래도 훅이
  강제 검증한 적이 없어 그대로 유지).
- 본문이 있으면 제목과의 사이에 빈 줄이 필요하다 — `commit-msg`가 두 번째
  non-comment 줄이 비어있지 않으면 거부한다.
- `Signed-off-by`: `post-commit`이 모든 커밋에 커미터 정보
  (`git log -1 --format='%cn <%ce>'`)로 자동 삽입한다(`git commit -s`와
  동일한 방식). 이 저장소의 다른 자동 트레일러(Task-Id, AI-Tool,
  Co-Authored-By, Hooks-Commit)와 같은 패턴 — 사람이 직접 타이핑하도록
  강제하지 않는다.
- `Fixes: <hash> ("<원인 커밋 제목>")`: 강제하지 않는다 — 모든 버그 수정
  커밋에 원인 커밋이 항상 식별 가능한 건 아니기 때문이다(예: 최초 구현부터
  있던 버그). 다만 트레일러가 존재하면 `commit-msg`가
  `git rev-parse --quiet --verify "<hash>^{commit}"`으로 참조 해시가
  실재하는 커밋인지 검증해 오타/잘못된 참조를 잡는다.
- 원자적 커밋(커밋 하나 = 논리적 변경 하나) 관행은 `.gitmessage`에 안내로만
  남긴다 — "논리적 단위"는 자동 판별이 불가능해 훅으로 강제할 수 없다.

## Consequences

- decision-1은 이 decision으로 대체(superseded)된다. decision-1 파일 자체는
  과거 기록으로 남겨두고, 새 작업은 이 decision을 근거로 삼는다.
- decision-1이 근거로 들었던 "CHANGELOG 자동 생성·semver 자동 산정 도구
  연동"이라는 장점은 포기한다 — type 화이트리스트는 유지하지만 표준
  Conventional Commits 파서(semantic-release 등)는 더 이상 이 저장소의
  서브젝트를 그대로 파싱하지 못한다. 이 프로젝트가 그런 도구를 실제로
  연동한 적이 없으므로 실질적 손실은 없다고 판단했다.
- `docs/references/conventional-commits-ko.md` vendoring 파일은 과거 기록으로
  남기고 삭제하지 않는다 — 더 이상 "현재 따르는 표준"은 아니다.
- 기존 GF-82 이전 커밋 이력(Conventional Commits 형식)은 소급 변경하지
  않는다 — 이 decision은 이 시점 이후의 신규 커밋에만 적용된다.

