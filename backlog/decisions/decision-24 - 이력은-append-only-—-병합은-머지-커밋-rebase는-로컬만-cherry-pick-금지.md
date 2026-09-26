---
id: decision-24
title: '이력은 append-only — 병합은 머지 커밋, rebase는 로컬만, cherry-pick 금지'
date: '2026-09-26 08:28'
status: accepted
---
## Context

이 프로젝트의 전제는 **에이전트가 프로그래밍하고 git이 그 작업의 로그로 동작한다**는
것이다(README). 그런데 이력을 다시 쓰는 연산에 대한 정책이 없었고, 오히려 PR을 GitHub의
rebase-merge로 병합하는 관행이 있었다.

**그 관행이 실제로 기록을 거짓으로 만들고 있었다.** 실측(2026-09-26, main의 최근 3개 커밋):

```
커밋 72755d0  committer = coralstay <...>       ← git이 기록한 실제 커미터
             Signed-off-by: cpu-once <...>     ← 트레일러가 주장하는 커미터
%G? = N (세 커밋 모두)
```

`post-commit`이 로컬 커밋 시점의 커미터로 `Signed-off-by`를 썼는데, GitHub이 rebase로
커밋을 다시 만들면서 커미터가 바뀌었다. **트레일러가 자기가 앉아 있는 커밋에 대해 거짓을
말한다.**

같은 논리가 다른 트레일러에도 적용된다. `Tokens-Used`는 "그 세션 그 구간"의 측정값이고
`Hooks-Commit`은 "이 커밋을 검사한 훅 버전"인데, 재생된 객체는 그 세션에서 만들어진 것도
아니고 그 훅이 검사한 것도 아니다.

## 외부 근거

- **Linux 커널 메인테이너 문서**: "History that has been exposed to the world beyond your
  private system should usually not be changed." / "Reparenting a patch series ... invalidates
  much of the testing that was done." / "The kernel community is not scared by seeing merge
  commits in its development history." — rebase로 merge를 피하려는 시도 자체를 문제로 본다.
  단 금지 선은 "공개된 이력"이다.
- **서명**: rebase는 부모를 바꾸고 부모는 서명 대상이므로 서명이 무효화된다. GitHub의
  rebase-merge는 서명 검증 없이 커밋을 추가한다(GitHub이 서명 키를 갖고 있지 않다).
- **provenance 연구**(arXiv 2607.02774): force-push 1억 6,671만 건 / 저장소 1,992만 개.
  이력 재작성이 "이력은 불변"이라는 가정을 무너뜨려 저자 귀속과 취약점 추적 분석을
  무효화한다.
- **Gerrit `Change-Id`**: 커밋 SHA가 불안정하다는 전제로 SHA와 독립된 안정 식별자를
  트레일러에 둔 선례. 그 `commit-msg` 훅 규칙이 우리와 같다 — 이미 있으면 건드리지 않는다.

## Decision

**커밋이 만들어진 뒤에는 그 객체를 다시 만들지 않는다(append-only).**

금지선은 커널 문서와 같이 **공개(push)된 이력**에 둔다 — 아직 push하지 않은 로컬 작업
정리는 로그 위조가 아니다.

| 연산 | 정책 | 판별 방법 (전부 실측, doc 참고) |
| --- | --- | --- |
| 커밋 | 허용 | — |
| **revert** | **권장** — append-only의 되돌리기 수단 | 제목 `Revert "` + 본문 `This reverts commit <실재 해시>` |
| **merge** | 허용 — 통합 수단 | `MERGE_HEAD` |
| **rebase (push 전 로컬)** | 허용 | `CHERRY_PICK_HEAD` + `$GIT_DIR/rebase-merge/` 디렉터리 |
| **rebase (push 후)** | 거부 | `pre-rebase`에서 재생 대상이 원격 ref에 이미 있는지 |
| **cherry-pick** | 거부 | `CHERRY_PICK_HEAD` 있고 `rebase-*/` **없음** |
| **`--amend`** | 거부 | `source=commit` |
| **squash merge** | 거부 | `source=squash` / `SQUASH_MSG` |

**PR 병합은 머지 커밋으로 한다.** rebase-merge와 squash는 쓰지 않는다. 선형 뷰가 필요하면
`git log --first-parent`를 쓴다.

**이미 어긋난 과거 커밋은 고치지 않는다.** 그것을 고치는 것 자체가 이력 재작성이고, 그때의
결정에는 그때의 이유가 있었다.

## 강제 계층 — 로컬과 원격이 맞물리는 지점

**`--no-verify`는 로컬 훅을 건너뛸 수 있다.** 그래서 로컬만으로는 정책이 완결되지 않는다.
계층을 나눈다.

### 로컬 (git 훅) — 볼 수 있는 모든 재작성 경로를 막는다

| 대상 | 판별 |
| --- | --- |
| cherry-pick | `CHERRY_PICK_HEAD` 있고 `rebase-merge/`·`rebase-apply/` 없음 |
| `--amend` | `source=commit` + `$3`이 `HEAD` + `rebase-merge/` 없음 |
| squash | `source=squash` 또는 `SQUASH_MSG` |
| 에디터 경로 | 메시지 파일에 비주석 내용 없음(GF-125) |
| push된 커밋을 다시 쓰는 rebase | `pre-rebase`에서 재생 대상이 원격 ref에 있는지 |

`--no-verify`로 건너뛸 수 있는 것은 `pre-rebase`와 `pre-push`다. `prepare-commit-msg`는
건너뛸 수 없으므로 커밋 단계 강제는 그대로 유지된다(doc-15).

### 원격 (GitHub) — 로컬이 닿지 않는 것을 막는다

**github.com에는 `pre-receive` 훅을 설치할 수 없다** — 그건 GitHub Enterprise 전용 기능이다.
대신 rulesets와 저장소 설정이 그 자리를 대신한다. 2026-09-26 적용 완료:

| 설정 | 값 | 무엇을 막나 |
| --- | --- | --- |
| `allow_merge_commit` | `true` | — |
| `allow_rebase_merge` | **`false`** | rebase-merge가 커밋을 다시 만들어 트레일러를 거짓으로 만드는 것 |
| `allow_squash_merge` | **`false`** | squash |
| ruleset `non_fast_forward` | 활성 | **force push** — `--no-verify`로 로컬 훅을 건너뛰어 다시 쓴 이력이 원격에 도달하는 것 |
| ruleset `deletion` | 활성 | 브랜치 삭제 |

**이게 두 계층이 맞물리는 지점이다.** `--no-verify`로 로컬에서 이력을 다시 쓰는 것 자체는
막을 수 없다. 그러나 다시 쓴 결과는 **fast-forward가 아니므로 원격이 거부한다.** 즉 로컬
재작성은 가능하지만 **공개될 수 없다** — 금지선을 "공개된 이력"에 둔 것과 정확히 일치한다.

**켜면 안 되는 규칙**: rulesets의 `required_linear_history`는 이름이 좋아 보이지만
**merge commit을 금지하는 규칙**이다. append-only와 정반대다.

**켜지 않은 것**: `required_signatures`(서명 강제). 현재 이 저장소의 커밋은 `%G?`가 `N`으로
나오므로 켜면 자기 push가 막힌다. 서명 설정을 먼저 정리한 뒤 검토할 사항이다.

## Consequences

- 트레일러가 자기 커밋에 대해 참인 상태가 유지된다. `Signed-off-by`가 실제 커미터와,
  `Hooks-Commit`이 실제로 검사한 훅과, `Tokens-Used`가 실제 그 작업 구간과 맞물린다.
- 서명이 병합 후에도 유효하게 남는다.
- 실제 분기 구조가 보존된다 — rebase가 만드는 가짜 선형 순서 대신, 병렬로 일어난 작업이
  병렬로 기록된다. 에이전트 작업 이력을 분석할 때 이게 사실과 일치한다.
- **기존 정책이 뒤집힌다.** 로컬 claude-rails 훅이 `git merge`를 `--ff-only` 없이 거부하고
  있고, 유저 메모리에 "항상 rebase-merge" 지시가 있었다. 둘 다 갱신해야 한다.
- **cherry-pick과 rebase는 훅 인자로 구분되지 않는다** — `source`와 상태 파일이 동일하고
  진행 디렉터리(`rebase-merge/`)만 다르다. cherry-pick만 막으려면 그 디렉터리를 봐야 한다.
- **merge와 revert는 git이 메시지를 지어주므로** `[type][subsystem]` 규칙에 맞지 않는다.
  둘 다 새 커밋이라 트레일러는 붙여야 하고 제목 형식 검사만 예외로 둬야 한다.
- `git log`가 머지 커밋으로 덜 선형이 된다. `--first-parent`로 완화한다.
