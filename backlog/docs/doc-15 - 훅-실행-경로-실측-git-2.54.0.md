---
id: doc-15
title: 훅 실행 경로 실측 (git 2.54.0)
type: specification
created_date: '2026-09-25 19:34'
updated_date: '2026-09-26 02:34'
---
# 훅 실행 경로 실측 (git 2.54.0)

decision-18의 근거 데이터. 어떤 커밋 경로에서 어떤 훅이 실행되는지를 직접 측정한 결과다.
**재현 절차를 함께 남긴다** — git 버전이 올라가면 다시 확인해야 하는 성질의 사실이다.

## 결과

| 경로 | pre-commit | prepare-commit-msg | commit-msg | post-commit | `$2` (source) |
| --- | --- | --- | --- | --- | --- |
| `git commit -m "..."` | 실행 | 실행 | 실행 | 실행 | `message` |
| `git commit` (에디터) | 실행 | 실행 — **에디터는 그 뒤에 열린다** | 실행 | 실행 | `template` |
| `git commit --no-verify` | 스킵 | **실행** | 스킵 | 실행 | `message` |
| `git commit --amend` | 실행 | 실행 | 실행 | 실행 | `commit` |
| `git revert --no-edit` (clean) | 스킵 | **실행** | 스킵 | 실행 | `message` |
| `git revert` (에디터) | 스킵 | **실행** | 스킵 | 실행 | `merge` |
| `git revert` 충돌 후 `git commit` | 실행 | 실행 | 실행 | 실행 | `message` |
| cherry-pick (rebase 재생) | 스킵 | **실행** | 스킵 | 실행 | `message` |
| **`git am`** | 스킵 | **스킵** | 스킵 | 실행 | — |
| `git commit-tree` | 스킵 | 스킵 | 스킵 | 스킵 | — |
| `git stash` | 스킵 | 스킵 | 스킵 | 스킵 | — |

`git am`에서는 대신 `applypatch-msg` → `pre-applypatch` → `post-applypatch`가 실행된다.

## 설계에 쓰인 결론

1. **`--no-verify`는 `prepare-commit-msg`를 건너뛰지 못한다.** 검사·검증을 이 훅에 모으면
   우회가 불가능해진다.
2. **에디터는 `prepare-commit-msg` 뒤에 열린다.** 그래서 이 훅은 사람이 타이핑한 최종
   메시지를 볼 수 없다. `$2=template`으로 그 경로를 식별해 거부한다.
3. **`git am`은 이 훅을 타지 않는다.** 별도로 `applypatch-msg`에서 거부한다.
4. `prepare-commit-msg`의 `exit 1`은 커밋을 막는다 — 검증을 이 훅에 둘 수 있다.
5. `commit-msg`도 메시지 파일을 고쳐 쓸 수 있고 그 변경이 커밋에 남는다(참고용 사실).

## 재현 절차

```sh
cd "$(mktemp -d)"
git init -q . && git config user.email t@t && git config user.name t
mkdir hk && git config core.hooksPath hk
for h in pre-commit prepare-commit-msg commit-msg post-commit \
         applypatch-msg pre-applypatch post-applypatch; do
  printf '#!/bin/sh\necho "RAN: %s (args=$*)" >> /tmp/hooklog\n' "$h" > "hk/$h"
  chmod +x "hk/$h"
done
echo a > a.txt && git add .
: > /tmp/hooklog && git commit -m "[feat] x" && cat /tmp/hooklog
```

경로별로 `: > /tmp/hooklog` 후 해당 명령을 실행하고 로그를 읽는다.

**에디터 경로를 측정할 때 주의**: `GIT_EDITOR`를 파일을 `>`로 덮어쓰는 스크립트로 만들면
훅이 넣은 내용이 사라져 "훅이 동작하지 않았다"고 오판하게 된다. 실제 에디터는 파일을 열어
편집하므로, 시뮬레이션도 기존 내용을 보존해야 한다.

```sh
cat > /tmp/realeditor.sh <<'E'
#!/bin/sh
tmp=$(mktemp)
printf '[feat] subject typed by human\n' > "$tmp"
cat "$1" >> "$tmp"     # 기존 내용(템플릿·트레일러) 보존
mv "$tmp" "$1"
E
chmod +x /tmp/realeditor.sh
GIT_EDITOR=/tmp/realeditor.sh git commit
```

**`source` 값 판별**: 훅에서 `$2`를 찍으면 `-m`은 `message`, 에디터는 `template`,
`--amend`는 `commit`으로 나온다. 비주석 내용 줄 수(`grep -v '^#' "$1" | grep -c '[^[:space:]]'`)로도
확인할 수 있다 — 에디터 경로는 0이다.

## revert 경로 정정 (2026-09-26 재측정, GF-125)

초판의 `git revert` 행은 `source` 값이 비어 있었다. 재측정 결과 세 경로가 서로 다르고,
**진행 상태 파일도 예상과 다르다.**

| revert 방식 | `source` | `$GIT_DIR`에 있는 파일 |
| --- | --- | --- |
| `--no-edit` (clean) | `message` | `MERGE_MSG` **만** — `REVERT_HEAD` 없음 |
| 에디터로 열 때 | `merge` | `MERGE_MSG` 만 |
| 충돌로 멈춘 뒤 `git commit` | `message` | **`REVERT_HEAD`** 존재 |

핵심은 **clean revert에 `REVERT_HEAD`가 없다**는 점이다. `REVERT_HEAD`는 revert가 충돌로
멈췄을 때만 생긴다. 따라서 `MERGE_HEAD`/`CHERRY_PICK_HEAD`/`REBASE_HEAD`/`REVERT_HEAD`
네 파일을 검사하는 면제 조건은 **clean revert를 면제하지 않는다** — source도 `message`라
source 검사로도 걸리지 않는다.

실측 로그:

```
$ git revert --no-edit HEAD
source=[message] MERGE_MSG msg=[Revert "[feat] base commit"]
```

### 측정할 때 빠지기 쉬운 함정

훅 디렉터리를 저장소 **안**에 두고 `git add .`로 커밋하면, 그 커밋을 revert할 때
**훅 파일 자체가 삭제**되어 훅이 안 돈 것처럼 보인다. `core.hooksPath`를 저장소 밖
경로로 두고 측정할 것. (초기 측정에서 실제로 이 함정에 걸려 "revert에서는 훅이 안 돈다"고
잘못 판단했다.)

### 이 사실이 만드는 문제

git이 만드는 revert 메시지는 `Revert "[feat] base commit"`이다. 이 저장소의 제목 규칙은
`[type][subsystem] <설명>`이므로 **형식에 맞지 않는다.** 지금은 revert 경로에서
`commit-msg`가 돌지 않아 드러나지 않지만, 메시지 검증이 `prepare-commit-msg`로 옮겨오면
(GF-127) clean revert가 거부된다. GF-127에서 처리 방침을 정해야 한다.
