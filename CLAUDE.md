
<!-- BACKLOG.MD GUIDELINES START -->
<!-- backlog.md-instructions-version: 1.55.3 -->
<CRITICAL_INSTRUCTION>

## Backlog.md Workflow

This project uses Backlog.md for task and project management.

**For every user request in this project, run `backlog instructions overview` before answering or taking action.**

Use the overview to decide whether to search, read, create, or update Backlog tasks.

Before task lifecycle actions, read the matching detailed guide:
- `backlog instructions task-creation` before creating or splitting tasks
- `backlog instructions task-execution` before planning, changing status or assignee, adding a plan or implementation notes, or implementing task work
- `backlog instructions task-finalization` before checking acceptance criteria, writing final summaries, or moving tasks to terminal statuses

Use `backlog <command> --help` before running unfamiliar commands. Help shows options, fields, and examples.

Do not edit Backlog task, draft, document, decision, or milestone markdown files directly. Use the `backlog` CLI so metadata, relationships, and history stay consistent.

</CRITICAL_INSTRUCTION>
<!-- BACKLOG.MD GUIDELINES END -->

## Backlog Decision 상태 확인 관례

`backlog decision` CLI에는 `create`/`list`만 있고 상태(status)를 바꾸는 명령이
없다. 그래서 어떤 decision이 나중 decision으로 대체(superseded)돼도
`backlog decision list`에는 여전히 `accepted`로 표시된다(예: decision-7은
decision-8로 대체됐지만 목록상 상태는 그대로다).

**decision을 참고할 때는 `backlog decision list`의 상태 표시만 보지 말고,
`backlog/decisions/`의 해당 파일 본문(Context/Decision/Consequences)에 "OO으로
대체됨/superseded" 같은 언급이 있는지 항상 확인할 것.** (`backlog decision`
CLI에는 `view`가 없어 파일을 직접 읽어야 한다.) 가장 번호가 큰 decision이
같은 주제를 다루고 있으면 그게 최신 결정이다.

## `hooks/*`, `install.sh`에서 `readonly VAR="$(cmd)"`를 한 줄로 합치지 말 것

`VAR="$(cmd)"` 다음 줄에 `readonly VAR`를 쓰는 두 줄짜리 패턴이 hooks/*,
install.sh 전체에 반복된다. "한 줄로 합칠 수 있지 않나" 싶어도(POSIX 문법상
`readonly VAR="$(cmd)"`도 유효하다) **절대 합치지 말 것** — 실측 확인 결과,
`set -eu` 아래에서 `cmd`가 실패해도 `readonly VAR="$(cmd)"` 형태는 여러 셸
(bash의 sh 모드, dash, zsh의 sh 에뮬레이션)에서 그 실패를 **조용히 삼켜버리고**
빈 문자열로 계속 진행한다. 반면 `VAR="$(cmd)"; readonly VAR`처럼 대입과
readonly를 분리하면 대입 실패 시점에 정상적으로 `set -e`가 걸려 스크립트가
즉시 중단된다. 즉 지금의 "장황해 보이는" 두 줄 패턴은 스타일이 아니라
안전장치이며, 한 줄로 "정리"하면 조용한 실패를 유발하는 회귀가 생긴다.

## `hooks/*`, `install.sh`에서 파이프 왼쪽 명령의 실패를 그냥 흘려보내지 말 것

POSIX sh에는 `pipefail`이 없다 — `a | b`의 종료 코드는 오른쪽 명령(`b`)의
것만 반영되고, `a`가 실패해도 `b`가 성공하면 파이프라인 전체는 성공으로
취급된다. `set -e`도 이 파이프라인 성공/실패만 보므로 `a`의 실패를 못 잡는다.

실제로 GF-76에서 `hooks/commit-msg`의 `TYPES="$(git config ... | tr '\n' '|')"`가
이 문제였다: `git config`가 실패해도 `tr`은 항상 성공해 TYPES가 조용히 빈
문자열이 되고, 이후 정규식이 `^()...`가 돼 모든 커밋이 원인 모를 이유로
거부됐다. 왼쪽 명령의 실패가 파이프라인 전체의 성패에 영향을 줘야 하는
자리라면, 파이프로 바로 연결하지 말고 왼쪽 명령의 결과를 먼저 평범한
변수에 담아(`RAW="$(cmd)"`) `set -e`가 그 실패를 잡게 한 뒤, 그 변수를
오른쪽 명령으로 변환할 것.

반대로, 마지막 명령이 항상 성공하는 걸 **의도적으로** 이용해 "조회 실패 시
조용히 생략" 같은 fail-safe 동작을 구현한 곳도 있다(`post-commit`의 AI-Model
트랜스크립트 조회, decision-5) — 이런 곳은 고치면 안 된다. 파이프를 볼 때마다
"왼쪽이 실패했을 때 지금 동작이 의도된 것인가"를 먼저 판단할 것.
