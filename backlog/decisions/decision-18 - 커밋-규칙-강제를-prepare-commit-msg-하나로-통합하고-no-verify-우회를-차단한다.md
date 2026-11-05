---
id: decision-18
title: 커밋 규칙 강제를 prepare-commit-msg 하나로 통합하고 --no-verify 우회를 차단한다
date: '2026-09-25 19:34'
status: accepted
---
## Context

git-format은 지금 훅 3개(`pre-commit`/`commit-msg`/`post-commit`)로 동작하고, 트레일러를
커밋이 만들어진 **뒤에** `git commit --amend`로 붙인다. 이 구조에서 네 가지가 깨져 있다.

- `git commit --no-verify`로 검사와 검증을 전부 건너뛸 수 있다. 우회를 막는 대신 사후에
  `Verify-Bypassed` 트레일러로 기록만 한다.
- cherry-pick/rebase 중에는 `--amend`가 불가능해 훅이 트레이스백을 낸다.
- `--amend`가 `post-commit`을 재발동시켜 재귀 가드가 필요하다.
- `commit-msg`가 트레일러보다 먼저 돌기 때문에 훅이 삽입한 트레일러는 검증을 받지 않는다.

git 2.54.0에서 훅 실행 경로를 실측했다(재현 절차는 doc-15).

| 경로 | prepare-commit-msg | `$2` (source) |
| --- | --- | --- |
| `git commit -m "..."` | 실행 | `message` |
| `git commit` (에디터) | 실행 — 에디터는 그 뒤에 열린다 | `template` |
| `git commit --no-verify` | **실행** (`pre-commit`·`commit-msg`만 스킵) | `message` |
| `git commit --amend` | 실행 | `commit` |
| `git revert` / cherry-pick / rebase 재생 | 실행 (`commit-msg`는 안 돈다) | — |
| `git am` | **안 돈다** — `applypatch-msg` 계열만 | — |
| `git commit-tree`, `git stash` | 훅 없음 (plumbing) | — |

`prepare-commit-msg`의 `exit 1`이 커밋을 막는 것도 실측으로 확인했다.

## Decision

검사·검증·트레일러 삽입을 **`hooks/prepare-commit-msg` 하나로 통합**한다. `pre-commit`,
`commit-msg`, `post-commit`을 삭제한다. `git am`은 `hooks/applypatch-msg`에서 거부한다.

실행 순서: 재생·병합 커밋 면제 → 에디터 경로 거부 → lint → 메시지 검증 → 트레일러 삽입.

**에디터 경로(`source=template`)는 거부한다.** 이 훅은 사람이 타이핑하기 전에 돌아 빈
메시지를 보므로 메시지 검증이 원리적으로 불가능하다. 거부하면 통과한 모든 커밋이 검증을
거친 것이 된다. 따라서 `install.sh`의 `commit.template` 설정과 `.gitmessage`도 함께
제거한다 — 에디터 안내가 목적인 기능이라 쓰이지 않는다.

**재생·병합 커밋에서는 아무 것도 하지 않는다.** `MERGE_HEAD`/`CHERRY_PICK_HEAD`/
`REBASE_HEAD`/`REVERT_HEAD`가 있거나 `source`가 `merge`/`squash`면 종료한다. 재생 커밋은
이미 검증된 커밋의 복제이므로 다시 도장을 찍는 것도, 토큰을 다시 계산하는 것도 틀렸다.

## Consequences

**얻는 것**

- `--no-verify`로 우회할 방법이 없다. 그래서 **검증 마커(`.gitformat-verified`)와
  `Verify-Bypassed` 트레일러가 존재 이유를 잃고 삭제된다** — 우회 탐지를 규정한 기존
  decision(decision-3)을 이 decision이 대체한다.
- `--amend`가 사라져 재귀 가드가 불필요해지고, rebase 중 트레이스백(DRAFT-18)이 해결된다.
- 커밋이 처음부터 최종 메시지로 만들어져 이력 재작성이 없다.
- 트레일러 중복이 구조적으로 사라진다(상세는 decision-19).

**대가와 한계**

- 사람도 `-m`으로만 커밋할 수 있다. 되돌리려면 `commit-msg`를 검증 전용으로 살리면 된다.
- `git commit-tree`/`git stash` 같은 plumbing과 `core.hooksPath` 변경·훅 삭제는 여전히
  무력하다. 훅은 보안 경계가 아니다.
- `python3` 부재 시 실패 양상이 바뀐다 — 이전에는 트레일러만 조용히 누락됐지만 이제
  커밋이 막힌다. 조용한 실패에서 드러나는 실패로 바뀐 것이므로 개선으로 본다.
