---
id: doc-2
title: 커밋 메시지 규칙 상세
type: guide
created_date: '2026-09-19 05:27'
updated_date: '2026-09-19 05:27'
---
## 📝 커밋 메시지 규칙

리누스 토발즈(리눅스 커널) 스타일을 따릅니다 — 서브젝트 프리픽스만 대괄호
형식으로 바꾸고, 나머지(빈 줄, "왜"에 집중하는 본문, 트레일러, 원자적 커밋
관행)는 그대로 채택했습니다(결정: decision-10, decision-1을 대체).

```
[type][subsystem] <description>

[body]

[footer(s)]
```

- `subsystem`은 생략 가능합니다: `[type] <description>`.
- 허용 type: `feat` `fix` `docs` `style` `refactor` `perf` `test` `build` `ci` `chore` `revert`.
- 제목은 50자 이내여야 합니다(유니코드 문자 수 기준, 바이트 아님 — `commit-msg`가 검증).
- 본문이 있으면 제목과의 사이에 빈 줄이 필요합니다(`commit-msg`가 검증).
- 본문의 각 줄은 72자 이내로 줄바꿈해야 합니다(`commit-msg`가 검증). `Task-Id`/`Fixes`/
  `BREAKING CHANGE` 등 등록된 footer 트레일러로 시작하는 줄은 이 제한에서 예외입니다.
- `Fixes: <hash> ("<원인 커밋 제목>")`은 강제하지 않지만, 있으면 해시가 실재하는
  커밋인지 `commit-msg`가 검증합니다.
- `Signed-off-by: <이름> <이메일>`은 `post-commit`이 커미터 정보로 모든 커밋에
  자동 삽입합니다(`git commit -s`와 동일한 방식) — 직접 쓸 필요 없습니다.
- BREAKING CHANGE는 `!` 마커 없이 footer의 `BREAKING CHANGE: <설명>`으로만 표시합니다.

`git config commit.template`이 설정돼 있으면 커밋 시 에디터에 이 형식과 type 목록이
주석으로 채워집니다.
