---
id: decision-19
title: >-
  커밋 footer 트레일러 집합 재정의 — AI-Agent 병합, Signed-off-by 제거, Tokens-Used를
  in/out/delta로
date: '2026-09-25 19:34'
status: accepted
---
## Context

footer가 트레일러 10종까지 늘어나 커밋 본문보다 길어졌고, 그 중 일부는 중복이거나 이
저장소에 값을 더하지 않는다. 실측으로 최근 40커밋 중 `Co-Authored-By`가 40/40,
`Task-Id`가 12/40 중복이다.

중복의 원인은 두 갈래다.

- 중복 판정을 `git interpret-trailers --parse` 출력으로 한다. 이 명령은 메시지 **맨 끝의
  연속된 트레일러 블록만** 인식하므로, 빈 줄로 분리된 앞 문단의 `Task-Id:`를 보지 못한다.
- `Co-Authored-By`는 판정이 "키: 값" 완전 일치라서, 메시지의 값과 설정의 정규 값이 다르면
  매번 새로 추가된다.

`AI-Tool`/`AI-Tool-Version`의 분리는 과거 버그의 원인이기도 했다(GF-33) —
`interpret-trailers --if-exists`가 키를 **접두어**로 매칭해 `AI-Tool` 존재를
`AI-Tool-Version` 존재로 오판했다.

## Decision

트레일러 집합을 다음으로 재정의한다.

| 트레일러 | 값 | 붙는 조건 |
| --- | --- | --- |
| `Task-Id` | 브랜치명의 `<prefix>-<번호>` | 브랜치명에 패턴이 있을 때 |
| `AI-Agent` | `<도구>/<버전> (<모델>)` | 검증된 에이전트 신호가 있으면 항상 |
| `Co-Authored-By` | `Claude <noreply@anthropic.com>` | 도구가 `claude-code`일 때 |
| `Tokens-Used` | `in=<입력> out=<출력> delta=<구간 전체>` | 에이전트 커밋일 때 |
| `Tool-Calls` | 스테이징 파일을 건드린 `tool_use` 블록 수 | 에이전트 커밋일 때 |
| `Hooks-Commit` | 훅 클론의 `rev-parse --short HEAD` | 항상 |

- **`AI-Tool` + `AI-Tool-Version` + `AI-Model` → `AI-Agent` 한 줄로 병합.** 구성요소를 못
  구해도 줄은 남긴다(`version-unavailable`/`model-unavailable`).
- **`Signed-off-by` 제거.** 커미터 정보는 커밋 객체의 committer 필드에 이미 있다.
  decision-10의 해당 조항을 이 decision이 대체한다.
- **`Verify-Bypassed` 제거.** 근거는 decision-18.
- **중복 판정 방식 변경.** `--parse` 출력이 아니라 **메시지 원문을 줄 단위로** 읽어
  `^<키>: `로 시작하는 줄이 있으면 그 키를 건너뛴다. 기준이 "값까지 같을 때만 생략"에서
  "**키가 있으면 생략**"으로 바뀐다.

## Consequences

- `--parse`의 "마지막 블록만" 의미론에 의존하지 않으므로 문단 분리 함정이 사라진다.
  공백 정규화·연속 줄 접기·블록 전체 무효화 같은 `--parse`의 다른 함정도 함께 사라진다.
- 콜론+공백까지 비교하므로 접두어 오매치(GF-33)가 원리적으로 불가능해진다. `AI-Agent`
  병합도 같은 버그 클래스를 구조적으로 없앤다.
- **사람이나 에이전트가 메시지에 직접 쓴 트레일러 값을 훅이 덮어쓰지 않는다.** 대신 잘못된
  값을 훅이 교정해주지도 않는다 — 의도된 트레이드오프다.
- footer가 6줄로 줄어든다.
- `Tokens-Used` 값의 의미가 바뀌므로 로그를 숫자로 파싱하던 것이 있다면 형식을 맞춰야 한다
  (측정 방식은 doc-16).
