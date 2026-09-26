---
id: doc-20
title: GitHub 원격 강제 설정 관리 — rulesets와 저장소 설정
type: guide
created_date: '2026-09-26 12:54'
updated_date: '2026-09-26 12:54'
---
# GitHub 원격 강제 설정 관리

decision-24(append-only)는 **로컬 훅만으로 달성할 수 없다.** `--no-verify`가 로컬 훅을
건너뛸 수 있고, GitHub의 병합 버튼은 로컬 훅을 아예 거치지 않는다. 그 몫을 원격 설정이
맡는다. 이 문서는 무엇이 왜 걸려 있고 어떻게 확인·변경하는지를 적는다.

## 전제: github.com에는 `pre-receive` 훅이 없다

서버측 훅으로 push를 검사하는 기능은 **GitHub Enterprise 전용**이다. github.com에서는
**rulesets**와 **저장소 설정**이 그 자리를 대신한다.

- [Available rules for rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)
- [Working with pre-receive hooks (Enterprise 전용)](https://docs.github.com/en/enterprise-server@3.0/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/working-with-pre-receive-hooks)

## 현재 걸려 있는 것 (2026-09-26 적용)

### 저장소 설정 — 병합 방식

| 설정 | 값 | 왜 |
| --- | --- | --- |
| `allow_merge_commit` | `true` | append-only가 허용하는 유일한 병합 방식. 원본 커밋 객체를 그대로 두고 합치는 커밋만 얹는다 |
| `allow_rebase_merge` | **`false`** | 커밋을 다시 만들어 SHA·커미터를 바꾼다. 실측으로 이 저장소의 `Signed-off-by`가 실제 커미터와 어긋난 원인이다 |
| `allow_squash_merge` | **`false`** | 여러 커밋을 하나로 합쳐 커밋 단위 기록을 파괴한다 |

### ruleset `main-protection` (id 23313297, active)

| 규칙 | 무엇을 막나 |
| --- | --- |
| `non_fast_forward` | **force push.** `--no-verify`로 로컬 훅을 건너뛰어 다시 쓴 이력이 원격에 도달하는 것을 막는다 |
| `deletion` | 브랜치 삭제 |

대상: `~DEFAULT_BRANCH`(= `main`).

## 두 계층이 맞물리는 지점

`--no-verify`는 `pre-rebase`와 `pre-push`를 건너뛴다. 즉 **로컬에서 이력을 다시 쓰는 것
자체는 막을 수 없다.** 그러나 다시 쓴 결과는 fast-forward가 아니므로 **원격이 거부한다.**

로컬 재작성은 가능하지만 **공개될 수 없다** — decision-24가 금지선을 "공개된 이력"에 둔 것과
정확히 일치한다. `prepare-commit-msg`는 `--no-verify`로 건너뛸 수 없으므로 커밋 단계 강제는
로컬에서 그대로 유지된다(doc-15).

## 켜면 안 되는 규칙

| 규칙 | 왜 안 되나 |
| --- | --- |
| `required_linear_history` | 이름이 좋아 보이지만 **merge commit을 금지하는** 규칙이다. squash 또는 rebase 병합만 허용하게 되어 append-only와 정반대가 된다 |

## 아직 켜지 않은 것

| 규칙 | 상태 | 조건 |
| --- | --- | --- |
| `required_signatures` | 끔 | 현재 이 저장소 커밋은 `%G?`가 `N`으로 나온다. 켜면 자기 push가 막힌다. 서명 설정(ssh-agent에 키 등록 등)을 먼저 정리한 뒤 검토 |
| `pull_request` (PR 필수) | 끔 | 로컬 claude-rails 훅이 이미 main 직접 push를 막고 있다. 이중으로 걸 가치가 있는지 판단 필요 |
| `required_status_checks` | 끔 | CI 통과를 병합 조건으로 강제할지. 지금은 사람이 확인하고 병합한다 |
| 대상을 `~ALL`로 확대 | 끔 | 현재 `main`만 보호한다. task 브랜치까지 force push를 막으면 "push 후 rebase 금지"가 완전해지지만, 운영 부담을 먼저 판단해야 한다 |

## 확인 방법

```sh
# 병합 방식
gh api repos/coralstay/git-format \
  --jq '{allow_merge_commit, allow_rebase_merge, allow_squash_merge}'

# ruleset 목록
gh api repos/coralstay/git-format/rulesets \
  --jq '.[] | "\(.name) | \(.enforcement) | id=\(.id)"'

# 특정 ruleset 상세
gh api repos/coralstay/git-format/rulesets/23313297 \
  --jq '{name, enforcement, include: .conditions.ref_name.include, rules: [.rules[].type]}'
```

## 변경 방법

```sh
# 병합 방식 변경
gh api -X PATCH repos/coralstay/git-format \
  -f allow_merge_commit=true -F allow_rebase_merge=false -F allow_squash_merge=false

# ruleset 갱신 (PUT은 전체 교체다 - 기존 규칙을 빠뜨리면 사라진다)
gh api -X PUT repos/coralstay/git-format/rulesets/23313297 --input ruleset.json
```

## 함정

**ruleset의 `conditions.ref_name.include`가 비어 있으면 아무 브랜치에도 적용되지 않는다.**
`main-protection`이 실제로 그 상태로 `disabled`로 있었다 — 그냥 활성화만 하면 규칙이 걸린
것처럼 보이지만 대상이 없어 아무 일도 하지 않는다. 활성화할 때 `include`를 반드시 확인할 것.

**`PUT`은 전체 교체다.** 규칙 하나를 추가하려고 `PUT`을 쓰면서 기존 규칙을 빠뜨리면 그
규칙이 사라진다.

**저장소 설정과 ruleset은 다른 레이어다.** 병합 방식은 저장소 설정(`allow_*_merge`)이고,
force push 차단은 ruleset이다. 한쪽만 보면 정책이 걸려 있다고 오판한다.

## 관련 문서

- decision-24 — append-only 이력 정책과 강제 계층
- doc-19 — 이력을 바꾸는 git 연산별 훅 판별 방법(실측)과 우회 경로 전수 조사
- doc-15 — 훅 실행 경로 실측
