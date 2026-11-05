---
id: GF-125
title: prepare-commit-msg 훅 신설 — 재생 커밋 면제와 -m 강제 게이트
status: Done
assignee: []
created_date: '2026-09-25 19:33'
updated_date: '2026-09-26 02:50'
labels:
  - hooks
dependencies:
  - GF-124
references:
  - decision-18
  - decision-22
documentation:
  - backlog/docs/doc-13 - git-format-재설계-계획-—-커밋-규칙을-prepare-commit-msg로-통합.md
  - backlog/docs/doc-14 - 용어-정리-—-턴-트랜스크립트-귀속-마커-구분.md
  - backlog/docs/doc-15 - 훅-실행-경로-실측-git-2.54.0.md
  - backlog/docs/doc-18 - 재설계-작업-순서와-의존성.md
modified_files:
  - hooks/prepare-commit-msg
priority: high
type: feature
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
git-format은 지금 커밋이 만들어진 뒤 post-commit이 --amend로 트레일러를 붙인다. 이 구조는 rebase/cherry-pick 중 amend가 불가능해 훅이 트레이스백을 내고, 재귀 가드를 필요로 하며, --no-verify로 검사와 검증을 모두 건너뛸 수 있다.

실측(git 2.54.0)으로 prepare-commit-msg는 --no-verify로도 건너뛸 수 없고 커밋 객체가 만들어지기 전에 돈다는 것을 확인했다. 이 훅을 본체로 삼으면 위 문제가 원인 단계에서 사라진다. 이 태스크는 그 골격만 세운다 — lint/검증/트레일러는 후속 태스크에서 옮긴다.

에디터 경로(source=template)에서는 훅이 사람이 타이핑하기 전에 돌아 빈 메시지를 보므로 메시지 검증이 원리적으로 불가능하다. 그래서 그 경로를 거부해 통과한 모든 커밋이 검증을 거친 것이 되게 한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 재생·병합 커밋에서는 아무 것도 하지 않고 종료한다 (MERGE_HEAD/CHERRY_PICK_HEAD/REBASE_HEAD/REVERT_HEAD 중 하나가 있거나 source가 merge 또는 squash)
- [x] #2 source가 template이면 커밋을 거부하고 git commit -m 사용을 안내한다
- [x] #3 훅 파일 위치를 os.path.realpath(__file__)로 해석해 init.templateDir 심볼릭 링크 설치에서도 lint 디렉터리와 설정 파일을 찾는다
- [x] #4 설정 파일을 읽을 수 없으면 원인을 밝히는 메시지와 함께 즉시 중단한다
- [x] #5 stdout/stderr 인코딩을 UTF-8로 고정해 LC_ALL=C 환경에서도 트레이스백 없이 동작한다
- [x] #6 표준 라이브러리만 사용한다
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 python3 -m unittest 스위트 전체 통과 (이관 전이면 bats tests/ 통과)
- [x] #2 ruff check 통과
- [x] #3 이 저장소 자신의 커밋이 새 훅으로 정상 생성되는지 확인
<!-- DOD:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: claude
created: 2026-09-26 02:10
---
설계 구멍 발견 (2026-09-26 실측): source 값으로 에디터 경로를 판별하는 방식에 한 가지 빈틈이 있다.

실측 결과 source 값은 -m/-F/-F -가 모두 `message`, 에디터는 `template`(commit.template 설정 여부와 무관), --amend는 `commit`이다.

문제는 `commit`이 모호하다는 점이다 — `git commit --amend --no-edit`은 메시지가 최종이지만, `git commit --amend`는 훅이 돈 뒤에 에디터가 열려 사람이 고친 텍스트가 검증을 받지 않는다. source만으로는 이 둘을 구분할 수 없다.

즉 '통과한 모든 커밋이 검증을 거친 것이 된다'(decision-18)는 --amend 경로에서 완전하지 않다. 이 태스크의 AC #2는 `template` 거부만 규정하므로 그대로 구현하고, 이 빈틈은 GF-127(메시지 검증 이전)에서 어떻게 다룰지 결정한다.

선택지: (a) source=commit에서도 검증해 --no-edit 경우를 커버하고 에디터 편집분은 포기, (b) commit-msg를 검증 전용으로 남겨 완전히 막는다(훅 3개가 된다), (c) --amend를 아예 거부한다.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
`hooks/prepare-commit-msg` 골격(124줄)을 신설했다. 하는 일은 두 가지뿐이다 — 재생·병합 커밋 면제와 에디터 경로 거부. lint/검증/트레일러는 GF-126~128에서 옮겨온다.

## 검증 증거 (직접 실측)

- 범위: `git diff --stat main...HEAD -- hooks/`가 새 파일 1개만 (124줄 추가). 구 훅 3개와 checks/ 무변경
- 스위트: `Ran 136 tests / OK` (127 → 136, 신규 9개)
- lint: `ruff check hooks/ tests/` 통과
- 공유 블록 동일성: 인코딩 preamble과 conf 가드가 pre-commit·commit-msg·post-commit과 **byte-identical** (기계 대조)
- 심볼릭 링크 경로 해석(AC #3): 링크 설치 저장소에서 conf를 찾음을 확인. **음성 대조**도 했다 — `realpath` 대신 `__file__`을 쓴 사본은 `.git/hooks/gitformat.conf`를 찾다 실패한다. 즉 realpath가 실제로 일을 하고 있다

## 순서가 고정된 이유

면제(Step 0)가 에디터 거부(Step 1)보다 **반드시 먼저**다. 에디터로 여는 revert/merge는 source가 `template`이 아니라 `merge`로 오지만, 앞으로 판단을 더 붙이면서 면제를 뒤로 미루면 사람이 메시지를 고를 수조차 없는 재생 경로가 거부된다.

면제 조건을 source와 상태 파일의 OR로 묶은 것도 실측 결과다 — cherry-pick과 rebase 재생은 `source=message`라 `CHERRY_PICK_HEAD`로만 잡히고, `MERGE_HEAD`가 있는 상태의 `git commit -m`도 `source=message`라 파일로만 잡히며, 반대로 `SQUASH_MSG`만 있는 커밋은 네 파일이 하나도 없어 `source=squash`로만 잡힌다.

## 기존 테스트 1건을 고쳤다 (범위 밖이지만 필요)

`tests/test_python3_missing.py`는 검증 대상 훅보다 앞서 도는 훅을 지워 그 훅을 고립시킨다. 새 훅이 체인에 끼어들면서 `test_post_commit만_실패해...`가 실제로 실패했고(트레일러 누락이 아니라 커밋 차단), `test_commit_msg가_실패해...`는 **조용히 commit-msg가 아닌 새 훅을 검증하고 있었다**. 두 테스트의 생략 목록에 `prepare-commit-msg`를 추가해 각 테스트의 선언된 의도를 복원했다.

## 후속 태스크로 넘긴 것

- **GF-127 위험**: clean `git revert --no-edit`은 `source=message`이고 `REVERT_HEAD`가 없어(충돌 시에만 생긴다) 면제되지 않는다. 자동 메시지 `Revert "..."`가 제목 규칙에 맞지 않으므로, 검증을 옮기면 clean revert가 거부된다. GF-127에 선택지 3개와 함께 기록했고 doc-15도 정정했다
- **--amend 모호성**: `source=commit`이 `--amend --no-edit`(최종)과 `--amend`(뒤에 에디터)를 구분하지 못한다. 이 골격은 일반 경로로 취급한다. GF-127에서 함께 결정
- doc-15의 revert 행이 미측정 상태였다 → 세 경로(clean/에디터/충돌 후)와 상태 파일을 측정해 정정했고, 측정 함정(훅을 저장소 안에 두면 revert가 훅을 삭제해 '안 돈 것'처럼 보인다)도 적었다

## CI가 잡은 버그 (추가 커밋)

처음 구현은 에디터 경로를 `source == "template"`으로 판정했다. **로컬 138개 통과, CI 실패.** 원인: `commit.template`이 설정돼 있지 않으면 git은 **source 인자를 아예 넘기지 않는다**(실측 `argc=1`). 제 개발 기계에는 `install.sh --global`이 심은 전역 `commit.template`이 있어 `source=template`이 왔고, 그 설정이 없는 CI에서는 빈 값이 되어 에디터 커밋이 조용히 통과했다.

게다가 **GF-132에서 `commit.template`을 제거할 예정**이라 이 검사는 곧 어디서도 작동하지 않게 될 것이었다.

수정: 메시지 파일의 **비주석·비공백 내용 유무**로 판정한다. 템플릿 설정과 무관하고, `--amend --no-edit`(직전 메시지가 들어 있음)도 정확히 통과한다.

| 조건 | source | 비주석 내용 | 판정 |
| --- | --- | --- | --- |
| template 있음 + 에디터 | `template` | 0줄 | 거부 |
| template 없음 + 에디터 | (없음) | 0줄 | 거부 |
| -m / -F | `message` | 1줄+ | 통과 |
| --amend --no-edit | `commit` | 1줄+ | 통과 |

**테스트 헬퍼도 고쳤다** — 실제 `~/.gitconfig`가 격리 저장소로 새어 들어오고 있었다. HOME을 기본적으로 임시 디렉터리로 돌려 로컬과 CI 조건을 일치시켰다. 이 누출이 버그를 로컬에서 숨긴 직접 원인이다.

회귀 테스트 3건 추가(138개): template 설정 있는 경우, 없는 경우, `--amend --no-edit`. **변이 테스트로 헛돌지 않음을 확인** — 판정을 source 기반으로 되돌리면 정확히 1건 실패한다.

## CI가 두 번째로 잡은 것 — 격리 범위

전역 config 누출을 막으려 HOME을 임시 디렉터리로 돌렸는데, **CI가 `pip install`로 sqlfluff/ruff를 실제 HOME 아래 사용자 site-packages에 깔기 때문에** 언어별 검사가 도구를 못 찾아 3건이 실패했다(`ModuleNotFoundError: No module named 'sqlfluff'`). GF-22가 고정한 "실도구가 있어야 한다"는 조건을 제 격리가 깨뜨린 것이다.

수정: HOME은 그대로 두고 **`GIT_CONFIG_GLOBAL`을 빈 파일, `GIT_CONFIG_SYSTEM`을 /dev/null**로 돌려 설정만 격리한다. HOME을 명시적으로 넘긴 테스트는 건드리지 않는다 — `install.sh --global`은 가짜 HOME의 `.gitconfig`에 쓰고 테스트가 그 파일을 읽어 확인하므로, `GIT_CONFIG_GLOBAL`을 씌우면 경로가 어긋난다(이 변수가 HOME보다 우선한다).

세 그룹을 따로 돌려 확인했다 — 에디터 테스트(전역 template 차단됨), SQL lint(도구 찾음), install.sh --global(가짜 HOME 유지) 모두 통과.
<!-- SECTION:FINAL_SUMMARY:END -->
