---
id: doc-19
title: 이력을 바꾸는 git 연산별 훅 판별 방법 (실측)
type: specification
created_date: '2026-09-26 08:29'
updated_date: '2026-09-26 12:55'
---
# 이력을 바꾸는 git 연산별 훅 판별 방법

decision-24(append-only)를 구현하려면 훅이 각 연산을 **구분할 수 있어야** 한다. 어떤 연산이
훅에게 어떻게 보이는지 실측한 결과다(git 2.54.0, 2026-09-26). 용어는 doc-14, 훅 실행 순서는
doc-15 참고.

## 결론 표

| 연산 | `$2` (source) | `$GIT_DIR`의 파일 | `$GIT_DIR`의 디렉터리 | 정책 |
| --- | --- | --- | --- | --- |
| `git commit -m` / `-F` | `message` | — | — | 허용 |
| `git commit` (에디터) | `template` 또는 **없음** | — | — | 거부(GF-125) |
| `git commit --amend` | `commit` | — | — | **거부** |
| `git revert --no-edit` | `message` | `MERGE_MSG` | — | **권장** |
| `git revert` (에디터) | `merge` | `MERGE_MSG` | — | 권장 |
| `git revert` 충돌 후 커밋 | `message` | `REVERT_HEAD` | — | 권장 |
| **`git cherry-pick`** | `message` | `CHERRY_PICK_HEAD`, `MERGE_MSG` | **없음** | **거부** |
| **rebase 재생** | `message` | `CHERRY_PICK_HEAD`, `MERGE_MSG` | **`rebase-merge/`** | 로컬만 허용 |
| merge 커밋 (`-m` 없이) | `merge` | `MERGE_HEAD`, `MERGE_MSG` | — | 허용 |
| merge 상태 + `git commit -m` | `message` | `MERGE_HEAD`, `MERGE_MSG` | — | 허용 |
| squash | `squash` | `SQUASH_MSG` | — | 거부 |

## 가장 중요한 사실: cherry-pick과 rebase는 인자로 구분되지 않는다

rebase는 내부적으로 각 커밋을 cherry-pick으로 재생한다. 그래서 **`source`도 같고 상태 파일도
같다.**

```
사용자 cherry-pick : files: CHERRY_PICK_HEAD MERGE_MSG   dirs:
rebase 재생        : files: CHERRY_PICK_HEAD MERGE_MSG   dirs: rebase-merge/
```

차이는 **진행 상태 디렉터리 하나뿐**이다. git은 rebase 진행을 `$GIT_DIR/rebase-merge/`에
기록한다(`git status`가 "rebase in progress"를 아는 방법이다). 구 backend(`--apply`)는
`rebase-apply/`를 쓰므로 둘 다 확인해야 한다.

**따라서 cherry-pick만 거부하려면**: `CHERRY_PICK_HEAD`가 있고 `rebase-merge/`와
`rebase-apply/`가 **둘 다 없을 때만** 거부한다. 상태 파일만 보고 거부하면 로컬 rebase까지
막힌다.

`REBASE_HEAD`는 믿을 수 없다 — rebase 재생 중에 **존재하지 않았다**(초기 조사에서 있다고
기록했으나 실측으로 틀렸음).

## revert의 세 갈래

`REVERT_HEAD`는 **revert가 충돌로 멈췄을 때만** 생긴다. 깔끔한 revert에는 없다.

```
$ git revert --no-edit HEAD
source=[message] MERGE_MSG msg=[Revert "[feat] base commit"]
```

그래서 `MERGE_HEAD`/`CHERRY_PICK_HEAD`/`REBASE_HEAD`/`REVERT_HEAD` 네 파일만 검사하는 조건은
**깔끔한 revert를 잡지 못한다.**

그리고 revert 커밋에는 **지금 트레일러가 붙는다**(실측):

```
Revert "[feat] base commit"

This reverts commit 91023bd7c790...

AI-Tool: claude-code / AI-Tool-Version: 2.1.267 / Co-Authored-By: Claude
Tokens-Used: unavailable (transcript-not-found) / Tool-Calls: unavailable (...)
Hooks-Commit: 72755d0 / Signed-off-by: t <t@t>
```

revert에서는 `prepare-commit-msg`와 `post-commit`이 돌고 **`commit-msg`는 돌지 않는다.**
그래서 이 제목은 지금까지 형식 검사를 받은 적이 없다. 검증을 `prepare-commit-msg`로 옮기면
`Revert "`로 시작하는 제목이 `[type][subsystem]` 규칙에 걸려 **revert가 전부 막힌다.**

→ revert는 새 커밋이므로 **트레일러는 붙이고 제목 형식 검사만 예외**로 둔다. 판별은 좁게:
제목이 `Revert "`로 시작하고 본문에 `This reverts commit <해시>`가 있고 그 해시가 실재할 때만.
merge 커밋(`Merge branch ...`)도 같은 예외가 필요하다.

## `pre-rebase`는 rebase를 막을 수 있다

```
pre-rebase argc=1 upstream=[main] branch=[]
rebase exit=1 → HEAD 그대로 (막힘)
```

인자는 upstream 하나뿐이고, **현재 브랜치를 rebase할 때 `$2`(branch)는 빈 값**이다.
`exit 1`이 rebase 전체를 중단시킨다 — 커밋이 만들어지기 전이므로 "이미 push된 커밋을 다시
쓰는 rebase"를 막을 자리는 여기다.

판정 방법(제안): `git rev-list <upstream>..HEAD`로 재생 대상을 구하고, 그중 하나라도
`git branch -r --contains <sha>`에 걸리면 이미 공개된 커밋이므로 거부한다.

## 재현 절차

저장소 **밖**에 훅 디렉터리를 두고 측정한다. 훅을 저장소 안에 두고 커밋하면 revert가
**훅 파일 자체를 삭제**해서 "훅이 안 돌았다"고 오판한다(실제로 걸렸던 함정).

```sh
mkdir -p /tmp/hk && cat > /tmp/hk/prepare-commit-msg <<'H'
#!/bin/sh
{ printf "source=[%s] files:" "$2"
  for f in MERGE_HEAD CHERRY_PICK_HEAD REBASE_HEAD REVERT_HEAD MERGE_MSG SQUASH_MSG; do
    [ -f "$(git rev-parse --git-dir)/$f" ] && printf " %s" "$f"; done
  printf " dirs:"
  for d in rebase-merge rebase-apply sequencer; do
    [ -d "$(git rev-parse --git-dir)/$d" ] && printf " %s/" "$d"; done
  printf " | %s\n" "$(head -1 "$1")"; } >> /tmp/hooklog
H
chmod +x /tmp/hk/prepare-commit-msg
# 대상 저장소에서: git config core.hooksPath /tmp/hk
```

**측정 함정 둘**: (1) cherry-pick으로 같은 변경을 이미 올려놓고 rebase를 측정하면, git이
"이미 적용됨"으로 보고 커밋을 건너뛰어 훅이 안 돈다 — 매번 깨끗한 저장소에서 측정할 것.
(2) 전역 `commit.template` 유무로 `source` 값이 달라진다 — `GIT_CONFIG_GLOBAL=/dev/null`로
격리할 것(GF-125에서 CI와 로컬이 갈린 원인이다).

## decision-24의 우회 경로 전수 조사 (실측, 2026-09-26)

이력을 만들거나 바꿀 수 있는 git 명령을 훑어 정책이 닿지 않는 곳을 정리했다.

### A. 훅이 아예 없는 경로

| 명령 | 무엇을 하나 | 훅 |
| --- | --- | --- |
| `git stash` | 커밋 객체를 **만든다** | **없음** (실측) |
| `git commit-tree` | 커밋을 직접 만든다 | **없음** (실측) |
| `git fast-import`, `hash-object`+`update-ref` | 대량 생성 | 없음 |
| `git reset --hard`, `git update-ref` | 커밋을 만들지 않고 브랜치를 옮겨 이력을 버린다 | 없음 |
| `git filter-branch`, `git filter-repo` | 이력 전체를 다시 쓴다 | 없음 |
| `git replace` | 객체를 바꾸지 않고 **보이는 이력**을 바꾼다 | 없음 |
| `git reflog expire`, `git gc --prune=now` | 복구 경로를 파괴한다 | 없음 |

이 부류는 git 훅의 공통 한계다. 훅은 보안 경계가 아니다 — 막을 수 없고, 막으려 해서도 안 된다.
문서에 알려진 한계로 적는다.

### B. 훅이 돌지만 판별이 안 되는 경로

**`git cherry-pick -n` 후 수동 커밋** — 실측 결과 상태 파일이 **하나도 없다**:

```
cherry-pick -n 후 수동 커밋:  source=[message] files: dirs:
```

`CHERRY_PICK_HEAD`가 없으므로 **평범한 커밋과 구별할 수 없다.** cherry-pick 차단의 우회
경로다. `git revert -n`도 같은 부류일 것으로 보이나 미측정.

**`git commit -C <ref>` vs `--amend`** — 둘 다 `source=commit`이다. 구분은 `$3`로 한다:

```
--amend          : source=[commit] $3=[HEAD]
commit -C HEAD~1 : source=[commit] $3=[HEAD~1]
```

`GIT_REFLOG_ACTION`은 설정되지 않았다(확인). 남는 모호성: `git commit -C HEAD`는 `--amend`와
완전히 같게 보인다. 드문 명령이고 "새 커밋에 HEAD의 메시지를 재사용"이라 어차피 제 메시지를
쓰게 하는 편이 낫다 — 오탐으로 수용하고 문서에 적는다.

### C. 로컬 훅이 도달할 수 없는 경로 — 가장 큰 구멍

**GitHub 병합 버튼은 로컬 훅을 전혀 거치지 않는다.** 실측으로 이 저장소의 현재 설정:

```
allow_merge_commit: true
allow_rebase_merge: true     ← Signed-off-by 불일치를 만든 원인
allow_squash_merge: true     ← decision-24가 금지한 연산
브랜치 보호: 없음 (main에 force push 가능)
```

**decision-24는 훅만으로 달성할 수 없다.** GitHub 저장소 설정에서 rebase-merge와 squash-merge를
끄고 merge commit만 남겨야 하고, `main`에 브랜치 보호(force push 금지)를 걸어야 한다.
이건 코드가 아니라 설정이다. 웹 UI의 파일 편집도 같은 부류다.

### D. 우회 의도가 없어도 막히는 오탐

**`rebase -i`의 reword는 rebase 안에서 `source=commit`을 만든다** (실측):

```
rebase -i reword:
  [pre-rebase 실행됨]
  source=[message] files: CHERRY_PICK_HEAD dirs: rebase-merge/   ← 재생
  source=[commit]  files:                  dirs: rebase-merge/   ← reword(내부 amend)
```

amend 거부를 `source=commit`만으로 하면 **`rebase -i`가 깨진다.** `rebase-merge/` 디렉터리가
있으면 면제해야 한다.

### E. 정책 자체의 충돌

로컬 claude-rails 훅이 `git merge`를 `--ff-only` 없이 거부한다. 이 조사 중 실제로 두 번 막혀
merge 케이스를 측정조차 할 수 없었다. decision-24의 "병합은 머지 커밋" 정책과 정면 충돌하므로
그 훅을 먼저 갱신해야 한다(claude-rails 저장소).

## 원격 쪽 강제 설정

이 조사에서 드러난 "로컬 훅이 도달할 수 없는 경로"는 GitHub 설정으로 막았다. 무엇이 왜
걸려 있고 어떻게 확인·변경하는지는 **doc-20(GitHub 원격 강제 설정 관리)** 에 있다.
