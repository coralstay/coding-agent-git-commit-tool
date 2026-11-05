---
id: GF-126
title: lint 실행을 prepare-commit-msg로 이전
status: Done
assignee: []
created_date: '2026-09-25 19:33'
updated_date: '2026-09-26 03:25'
labels:
  - hooks
  - lint
dependencies:
  - GF-125
references:
  - decision-18
documentation:
  - backlog/docs/doc-13 - git-format-재설계-계획-—-커밋-규칙을-prepare-commit-msg로-통합.md
  - backlog/docs/doc-14 - 용어-정리-—-턴-트랜스크립트-귀속-마커-구분.md
  - backlog/docs/doc-18 - 재설계-작업-순서와-의존성.md
modified_files:
  - hooks/prepare-commit-msg
  - hooks/pre-commit
priority: high
type: feature
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
언어별 검사는 지금 pre-commit이 담당하는데, pre-commit은 --no-verify로 건너뛸 수 있다. prepare-commit-msg는 건너뛸 수 없으므로 검사를 그쪽으로 옮기면 우회가 불가능해진다.

판정 로직은 그대로 옮긴다 — 저장소 루트의 언어 감지 마커 파일로 언어를 고르고, 해당 검사 스크립트를 실행해 실패 시 종료 코드를 전파한다. 언어 마커가 없으면 무해하게 통과한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 저장소 루트의 언어 감지 마커 파일로 언어를 판정하고 해당 검사 스크립트를 실행한다
- [x] #2 검사가 실패하면 그 종료 코드를 전파해 커밋을 막는다
- [x] #3 언어 마커가 하나도 없으면 아무 검사도 하지 않고 통과한다
- [x] #4 git commit --no-verify로도 검사가 실행되어 실패 시 커밋이 막힌다
- [x] #5 검사 전에 저장소 루트로 작업 디렉터리를 옮긴다 (마커 파일을 루트에서 찾기 때문)
- [x] #6 리터럴 경로 마커와 글롭 마커의 해석 차이가 기존과 동일하게 유지된다
- [x] #7 같은 커밋에서 hooks/pre-commit을 삭제한다 — 기능을 옮기고 구 훅을 남기면 lint가 두 번 실행된다
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
created: 2026-09-26 02:57
---
착수 전 확인한 연쇄 문제와 처리 방침 (2026-09-26).

## pre-commit 삭제가 Verify-Bypassed를 오작동시킨다

현재 사슬: pre-commit이 lint 통과 후 $GIT_DIR/.gitformat-verified를 쓰고,
post-commit이 그 **부재**를 --no-verify 우회로 판정해 Verify-Bypassed: true를 붙인다.
commit-msg는 거부 시 스테일 마커를 지운다(GF-31).

AC #7대로 pre-commit을 지우면 마커를 쓰는 곳이 없어져, 아직 살아 있는 post-commit이
**모든 커밋에 Verify-Bypassed: true를 붙인다.** 이 저장소는 자기 훅으로 커밋하므로
잘못된 footer가 실제 이력에 남는다 — doc-18이 경고한 바로 그 문제다.

**처리: prepare-commit-msg가 lint 통과 후 마커를 쓴다(임시 가교).** 형식은 기존 계약
그대로 "<epoch> <pid>" 한 줄이다. GF-128에서 post-commit과 함께 제거한다.
마커를 쓰는 시점은 pre-commit과 같다 — 모든 검사가 통과한 뒤. 실패하면 exit로
빠져나가므로 마커가 남지 않는다.

## 이 태스크가 만드는 1개 태스크짜리 과도기

lint가 prepare-commit-msg로 오면 --no-verify로 건너뛸 수 없으므로 마커가 항상 써지고,
따라서 **Verify-Bypassed가 도달 불가능해진다.** 그런데 이 시점에는 commit-msg가 아직
살아 있고 --no-verify가 여전히 그것을 건너뛴다 — 즉 '메시지 검증 우회'는 남아 있는데
그것을 기록할 신호가 없다.

GF-127이 검증을 옮기면 해소된다. 한 태스크짜리 과도기이므로 수용하되, 기존 테스트
tests/test_verify_bypass_detection.py가 '--no-verify면 Verify-Bypassed가 붙는다'를
단정하므로 이 태스크에서 새 동작으로 고쳐야 한다. 그게 AC #4(--no-verify로도 검사가
실행되어 실패 시 커밋이 막힌다)의 이면이다.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
lint 실행을 `prepare-commit-msg`로 옮기고 같은 커밋에서 `hooks/pre-commit`을 삭제했다(152줄 제거). 언어 감지와 검사 호출 로직은 그대로 옮겼다 — `run_check`, `has_tracked`, 마커 기록 줄이 구 `pre-commit`과 **byte-identical**임을 기계 대조로 확인했다.

실행 순서: 재진입 가드 → 재생 커밋 면제 → 에디터 거부 → 스테일 마커 무효화 → lint → 마커 기록.

## 검증 증거 (직접 실측)

- 범위: 훅 디렉터리에 `pre-commit` 삭제와 `prepare-commit-msg` 수정만. `commit-msg`/`post-commit`/`checks/*` 무변경
- 스위트: `Ran 139 tests / OK` (138 → 139)
- lint: `ruff check hooks/ tests/` 통과
- **lint가 실제로 막는다**: `pyproject.toml` + 미사용 import로 평범한 커밋과 `--no-verify` 커밋 모두 exit 1, HEAD 미생성, 마커 미기록. AC #4 성립
- **마커 가교가 실제로 일을 한다**: 가교를 빼면 평범한 커밋에 `Verify-Bypassed: true`가 나타난다(음성 대조)
- 공유 블록 byte 동일성: UTF-8 preamble, conf 가드, `conf_get`/`conf_get_all`, realpath 해석 모두 동일

## 브리프가 놓친 두 번째 연쇄 문제 (에이전트가 찾아 고침)

`post-commit`이 트레일러를 붙이려 도는 `git commit --amend --no-verify`가 **`prepare-commit-msg`를 다시 발동시킨다** — 이 훅은 `--no-verify`로 건너뛸 수 없기 때문이다. 결과로 같은 트리를 두 번 lint하고, `post-commit`이 지운 마커를 amend 쪽에서 다시 써서 `$GIT_DIR`에 스테일 마커가 남았다. 기존 테스트가 이걸 잡았다.

`post-commit`이 넘기는 `_GITFORMAT_AMEND_GUARD`를 파일 맨 위에서 확인해 즉시 빠져나가도록 고쳤다. **변이 테스트로 확인** — 가드를 제거하면 `post-commit이 마커를 지우지 않았다`로 실패한다. 이 가드도 GF-128에서 `post-commit`과 함께 사라진다.

## 테스트 9건이 영향받았다 (예상은 1건)

`test_verify_bypass_detection` 외에 `test_config_file_unreadable`, `test_config_keys_match_hooks`, `test_end_to_end_commit`, `test_install_script`(2건), `test_lint_dispatch`, `test_lint_python`, `test_python3_missing`, `test_replay_commits_untouched`, `test_shell_metacharacters_safe`가 `pre-commit`을 직접 참조하고 있었다. 전부 `prepare-commit-msg` 기준으로 옮기고 `[GF-nnn]` 태그를 유지했다.

`test_lint_python`의 한 케이스는 **`--no-verify`로 lint 부채를 심는 전제**였는데 AC #4가 그 전제를 없앤다. `git -c core.hooksPath=/dev/null commit`으로 교체했다.

## 정정한 과대 주장

착수 코멘트에 'Verify-Bypassed가 도달 불가능해진다'고 적었으나 **엄밀히는 틀렸다**. 재생 커밋은 마커 기록 전에 빠져나가므로 `post-commit`이 여전히 그 트레일러를 큐에 넣는다 — 다만 재생 중 amend가 DRAFT-18의 기존 트레이스백으로 실패해서 커밋에 반영되지 않을 뿐이다. 이 태스크 전과 동일한 동작이고, 그 경로를 테스트로 고정하지는 않았다(GF-128에서 사라질 경로다).

## 후속 태스크로 넘긴 것

- `checks/java.py`의 conf 가드가 다른 5개 사본과 **byte 동일하지 않다**(472 vs 436바이트). decision-16의 주장에 이미 난 구멍이고 이번 범위 밖이라 GF-133에 기록했다
- `hooks/readme.md`, `hooks/checks/readme.md`, `README.md`, `checks/*.py`와 `post-commit`의 주석, `.github/workflows/test.yml`이 아직 `pre-commit`을 lint 담당으로 서술한다 → GF-133/GF-134
<!-- SECTION:FINAL_SUMMARY:END -->
