---
id: GF-124
title: '테스트를 bats에서 Python 표준 unittest로 1:1 이관 (동작 무변경)'
status: Done
assignee: []
created_date: '2026-09-25 19:34'
updated_date: '2026-09-25 22:44'
labels:
  - tests
  - ci
dependencies: []
references:
  - decision-21
documentation:
  - backlog/docs/doc-13 - git-format-재설계-계획-—-커밋-규칙을-prepare-commit-msg로-통합.md
  - backlog/docs/doc-14 - 용어-정리-—-턴-트랜스크립트-귀속-마커-구분.md
  - backlog/docs/doc-16 - 토큰·툴콜-측정-방법과-한계.md
  - backlog/docs/doc-18 - 재설계-작업-순서와-의존성.md
modified_files:
  - tests/isolated_repo.py
  - .github/workflows/test.yml
priority: high
type: chore
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
훅은 이미 Python 표준 라이브러리만 쓰는데 테스트는 bats라서, CI가 bats-core를 GitHub에서 clone해 설치하는 스텝을 따로 둔다 — 훅은 '설치할 것 없음'인데 테스트만 외부 도구를 요구하는 비대칭이다. 현재 규모는 bats 1,880줄 / 17파일이다.

이 태스크를 재설계의 맨 앞에 둔다. 프레임워크 전환을 먼저 끝내면 이후 모든 훅 변경이 Python 테스트를 안전망으로 삼는다. 반대로 마지막에 두면 훅을 바꾸는 동안 bats를 계속 고쳐야 하고 마지막에 전부 다시 쓰게 되어 두 번 일하게 된다.

그래서 이 태스크는 동작을 바꾸지 않는 순수 1:1 이관이다. 구 훅 3개를 그대로 검증한다. 새 동작(에디터 거부, 귀속 측정 등)에 대한 테스트는 각 동작을 구현하는 태스크에서 함께 작성한다.

pytest가 아니라 unittest를 쓰는 이유는 설치가 필요 없어야 한다는 기존 원칙과 같다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 기존 bats 17파일의 모든 케이스가 Python unittest로 이관되고 동일한 동작을 검증한다
- [x] #2 bats 파일이 모두 삭제된다
- [x] #3 tests/isolated_repo.py가 임시 저장소 생성과 환경변수 조작 헬퍼를 제공한다 (기존 tests/helpers/git-format.bash 대체)
- [x] #4 테스트 파일명이 검증 내용을 드러낸다 (robustness 같은 성격 분류를 쓰지 않는다)
- [x] #5 트레일러 검증이 문자열 부분 일치가 아니라 개수까지 확인한다
- [x] #6 설정 키 일치 테스트가 설정 파일을 동적으로 읽어 대조한다 (손으로 나열한 목록을 없앤다)
- [x] #7 python3 부재 테스트는 자식 프로세스의 환경변수만 조작하고 러너 자신은 계속 동작한다
- [x] #8 CI에서 bats-core clone 설치 스텝이 제거되고 python3 -m unittest discover로 실행된다
- [x] #9 CI의 shellcheck -s sh install.sh 게이트가 유지된다
- [x] #10 CI의 언어별 실도구 설치(sqlfluff, ruff) 스텝이 유지된다
- [x] #11 ruff 검사 대상에 tests 디렉터리가 포함된다
- [x] #12 훅 코드는 이 태스크에서 한 줄도 바꾸지 않는다 (이관 전후로 검증하는 동작이 같다)
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 python3 -m unittest 스위트 전체 통과 (이관 전이면 bats tests/ 통과)
- [x] #2 ruff check 통과
- [x] #3 이 저장소 자신의 커밋이 새 훅으로 정상 생성되는지 확인
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## 이관 기준선 (2026-09-26 실측)

이관 전 `bats tests/` 결과를 기준선으로 고정한다. 1:1 이관이므로 이관 후
`python3 -m unittest`가 같은 동작을 같은 수의 케이스로 검증해야 한다.

```
1..124
ok 124개 / not ok 0개
```

파일별 줄 수(총 1,880줄): robustness-post-commit 312, robustness-commit-msg 236,
checks-ts 167, robustness-install 158, marker-semantics 112, robustness-injection 107,
robustness-python-path 104, robustness-locale 96, robustness-dispatch 86,
conf-guard 76, checks-python 74, consistency 64, checks-java 63, checks-cpp 63,
checks-sql 51, smoke 32, helpers/git-format.bash 79.

AC #12(훅 코드 무변경) 검증 방법: `git diff --stat hooks/`가 비어 있어야 한다.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
bats 17파일 1,880줄을 Python 표준 unittest 22파일로 이관했다. 훅 코드는 한 줄도 바꾸지 않았다.

## 검증 증거 (직접 실측)

- 훅 무변경: `git diff --stat main...HEAD -- hooks/` 출력 없음 (AC #12)
- 케이스 대조: 기준선 `ok` 124개의 **케이스명이 전부** Python docstring에 존재 (기계 대조, 미매칭 0건)
- 스위트: `python3 -m unittest discover -s tests` → **Ran 127 tests / OK** (77초)
- lint: `ruff check hooks/ tests/` → All checks passed
- `.bats` 및 `tests/helpers/` 전부 삭제됨

## 추가된 3개 케이스 (기준선 124 → 127)

모두 AC #5(개수 검증)에 따라 추가했다. bats에 대응 케이스가 없던 구멍이다.
- `Hooks-Commit` 값 검증: bats는 부재만 봤고 값을 대조한 적이 없었다
- `Task-Id` 전용 케이스 2건: 태스크 브랜치에서 정확히 1개, 예외 브랜치에서 0개

## 이관 중 발견한 실제 결함

구 `consistency.bats`의 손으로 나열한 conf 키 목록이 **드리프트해 있었다**. GF-83에서 추가된 `gitformat.subjectMaxLength`와 `gitformat.bodyLineMaxLength`가 목록에 없어, 이 키들이 사라지거나 비어도 테스트가 잡을 수 없었다.

새 `test_config_keys_match_hooks.py`는 훅 소스에서 키를 추출하고 `--get-regexp`로 트레일러 섹션을 동적으로 읽어 대조한다(AC #6). **변이 테스트로 헛돌지 않음을 확인했다** — `subjectMaxLength`를 conf에서 제거하니 `누락되거나 빈 값: gitformat.subjectMaxLength (참조: commit-msg)`로 실패했고, 원복 후 통과했다.

또 하나: 구 스위트는 `AI_AGENT`/`CLAUDE_CODE_SESSION_ID`를 그대로 상속해, **실행하는 사람에 따라 결과가 달라졌다**. Claude Code 안에서 돌리면 CI가 한 번도 안 거친 AI 경로를 조용히 타고 있었다. 새 헬퍼는 이 변수들을 자식 환경에서 제거한다.

## 후속 태스크에 남긴 것

- `hooks/readme.md`, `hooks/checks/readme.md`가 삭제된 `.bats` 파일명과 `bats tests/` 실행법을 아직 안내한다 → GF-134
- `install.sh:24` 주석이 `tests/consistency.bats`가 바이트 동일성을 보장한다고 적혀 있으나, 그 검사는 GF-108에서 이미 삭제됐고 이제 파일 자체도 없다 → GF-132
- `hooks/gitformat.conf` 헤더와 `hooks/readme.md`가 conf를 읽는 파일로 `checks/cpp.py`·`checks/sql.py`만 든다. `checks/java.py`도 읽는다 → GF-133
<!-- SECTION:FINAL_SUMMARY:END -->
