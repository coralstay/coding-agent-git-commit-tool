---
id: DRAFT-18
title: git rebase 중 post-commit이 cherry-pick 도중 amend를 시도해 트레이스백을 낸다
status: Draft
assignee: []
created_date: '2026-09-25 16:46'
updated_date: '2026-09-25 17:13'
labels: []
dependencies: []
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## 현상

로컬 `git rebase` 중 재생되는 커밋마다 `post-commit`이 트레이스백을 낸다. rebase 자체는 완료되고 커밋 메시지도 원본이 유지되지만, 사용자에게는 원인 불명의 Python 트레이스백이 노출된다.

## 정확한 에러 (2026-09-25 실측, 재현 확인)

```
Rebasing (1/1)fatal: You are in the middle of a cherry-pick -- cannot amend.
Traceback (most recent call last):
  File "hooks/post-commit", line 523, in <module>
    subprocess.run(
  File ".../subprocess.py", line 571, in run
    raise CalledProcessError(retcode, process.args,
subprocess.CalledProcessError: Command '['git', 'commit', '--amend', '--no-verify', '-m',
  '[feat] on branch\n\nTask-Id: GF-999\nAI-Tool: claude-code\nAI-Tool-Version: 2.1.267\n
   Co-Authored-By: Claude <noreply@anthropic.com>\n
   Tokens-Used: unavailable (transcript-not-found)\n
   Tool-Calls: unavailable (transcript-not-found)\n
   Hooks-Commit: ed076e5\nSigned-off-by: t <t@e.com>\n
   Verify-Bypassed: true']' returned non-zero exit status 128.
Successfully rebased and updated refs/heads/task/GF-999.
```

`exit 128`은 git 자체의 fatal 종료 코드다 — post-commit이 부른 `git commit --amend --no-verify`가 거부된 것이고, 이유는 첫 줄의 `fatal: You are in the middle of a cherry-pick -- cannot amend`다.

## 원인 연쇄

1. `git rebase`는 각 커밋을 cherry-pick으로 재생하고, 재생마다 `post-commit`이 발동한다.
2. 재생 중에는 `pre-commit`이 돌지 않아 검증 마커(`.git/.gitformat-verified`)가 없다.
3. `post-commit:107`의 `VERIFIED = os.path.isfile(MARKER)`가 False가 되고, `detect_verify_bypass()`(decision-3, post-commit:196)가 이를 `--no-verify` 우회로 판정해 `Verify-Bypassed: true`를 큐에 넣는다.
4. post-commit이 원본 트레일러 + `Verify-Bypassed: true`로 `git commit --amend --no-verify`를 시도한다(post-commit:523).
5. git이 cherry-pick 진행 중이라 amend를 거부 → exit 128 → `check=True`가 `CalledProcessError`를 올려 트레이스백.
6. git은 post-commit의 종료 코드를 무시하므로 rebase는 완료되고, amend가 실패했으니 커밋 메시지는 원본 그대로 남는다.

## 왜 지금까지 안 드러났는가

이 저장소는 PR을 GitHub의 rebase-merge로 병합한다 — 서버에서 일어나므로 로컬 훅을 거치지 않는다. 로컬 `git rebase`를 쓸 때만 나타난다.

## 위험도 판단

**지금은 git이 막아줘서 결과적으로 안전하다.** 그 amend가 성공했다면 정상 검증된 커밋 전부에 `Verify-Bypassed: true`가 찍혔을 것이다 — 커밋 이력에 거짓 기록이 남는다. 즉 안전성이 git의 거부에 우연히 의존하고 있고, 우리 쪽 논리에는 rebase/cherry-pick 재생을 구분하는 장치가 없다.

`post-commit` 상단에는 `_GITFORMAT_AMEND_GUARD` 재귀 가드만 있고(자기 amend 재발동 방지), rebase/cherry-pick 진행 상태를 보는 가드는 없다.

## 해결 방향 후보 (아직 결정 아님)

- **A. 진행 상태 감지 후 조기 종료** — `.git/CHERRY_PICK_HEAD`, `.git/rebase-merge/`, `.git/rebase-apply/` 중 하나라도 있으면 post-commit이 아무것도 하지 않고 exit 0. 재생되는 커밋은 이미 원본 트레일러를 갖고 있으므로 손댈 것이 없다는 판단.
- **B. Verify-Bypassed 판정만 억제** — 재생 중에는 `detect_verify_bypass()`를 건너뛰고 나머지 트레일러 로직은 유지. 다만 amend 자체가 여전히 금지되므로 exit 128은 그대로 난다 — A와 병행해야 의미가 있다.
- **C. amend 실패를 fail-open으로** — `check=True`를 풀어 실패를 조용히 흘린다. 트레이스백은 사라지지만 "트레일러 삽입 실패를 조용히 삼키지 않는다"(GF-76)는 이 파일의 원칙에 반한다. 단독으로는 부적절.

A가 유력해 보인다.

**참고(2026-09-26 정정)**: 이 draft 초안에는 "rebase/amend 후 처리는 원래 `post-rewrite`의 몫으로 설계돼 있다"고 적혀 있었으나 사실이 아니다. `hooks/post-rewrite`는 존재하지 않는다 — README의 훅 생애주기 표에서 `—`로 표시된, git이 제공하지만 이 프로젝트가 구현하지 않은 훅이다. 따라서 참고할 기존 역할 분담은 없고, 재생된 커밋을 사후 처리할 필요가 있다고 판단되면 `post-rewrite`를 새로 만드는 것 자체가 별도 결정 사항이다(decision-11/12가 정한 "커밋 단계까지만 다룬다"는 범위와 충돌하지 않는지 확인 필요).

## 착수 시 필요한 검증

- 위 재현 절차를 bats로 고정(rebase 시 트레이스백이 없고, 재생된 커밋에 `Verify-Bypassed`가 붙지 않는다)
- 진짜 `--no-verify` 우회 탐지(decision-3)가 여전히 동작하는지 회귀 확인 — 이게 깨지면 프로젝트의 핵심 기능이 무력화된다. 기존 케이스가 tests/robustness-injection.bats 등에 있으므로 그것들이 계속 통과해야 한다
- `git commit --amend`를 사용자가 직접 할 때의 동작이 바뀌지 않는지 확인(이 경우는 pre-commit이 정상 실행되므로 마커가 있고 Verify-Bypassed가 붙지 않아야 한다)
- `git cherry-pick`을 사용자가 직접 할 때의 기대 동작을 먼저 정해야 한다 — A안은 cherry-pick 커밋에 트레일러를 아예 붙이지 않게 되는데, 그게 맞는지는 별도 판단이 필요하다

## 재현 절차

```sh
D=$(mktemp -d); cd "$D"
git init -q; git config commit.gpgsign false
git config user.email t@e.com; git config user.name t
git config core.hooksPath <git-format>/hooks
git checkout -q -b main
echo base > base.txt; git add .; git commit -q -m "[feat] base"
git checkout -q -b task/GF-999
echo a > a.txt; git add .; git commit -q -m "[feat] on branch"
git checkout -q main
echo b > b.txt; git add .; git commit -q -m "[feat] on main"
git checkout -q task/GF-999
GIT_EDITOR=true git rebase main    # 여기서 트레이스백
```

## 우회 방법 (수정 전까지)

`git -c core.hooksPath=/dev/null rebase origin/main` — `rebase --continue`에도 같이 붙인다. 재생되는 커밋은 이미 트레일러를 갖고 있으므로 post-commit이 할 일이 없다.

발견 경위: 2026-09-25 GF-114 브랜치를 origin/main에 rebase하다가 노출됨.
<!-- SECTION:DESCRIPTION:END -->
