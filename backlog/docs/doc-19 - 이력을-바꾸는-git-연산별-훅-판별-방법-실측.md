---
id: doc-19
title: 이력을 바꾸는 git 연산별 훅 판별 방법 (실측)
type: specification
created_date: '2026-09-26 08:29'
updated_date: '2026-09-26 08:29'
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
