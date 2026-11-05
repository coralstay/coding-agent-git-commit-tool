---
id: GF-123
title: install.sh 이식성 테스트가 실제 저장소의 core.hooksPath를 임시 경로로 덮어씀
status: Done
assignee:
  - '@claude'
created_date: '2026-09-24 15:50'
updated_date: '2026-09-24 15:54'
labels:
  - bug
  - tests
dependencies: []
references:
  - GF-109
  - GF-26
type: bug
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## 증상

tests/를 한 번 돌릴 때마다 git-format 저장소 자신의 core.hooksPath가 곧 삭제될 임시 디렉터리를 가리키게 된다. 테스트가 끝나면 그 디렉터리가 사라지므로, 이후 이 저장소에서 만드는 모든 커밋에서 훅이 조용히 실행되지 않는다 - 커밋 메시지 검증도, Task-Id/AI 귀속 트레일러 삽입도 전부 사라진다. 에러 메시지가 없어 알아채기 어렵다.

## 원인

tests/robustness-install.bats의 '[정리] hooks/에서 파일이 삭제된 뒤 --global을 재실행하면 ...' 케이스가 install.sh 사본을 **타깃 인자 없이** 실행한다.

    cp "${GITFORMAT_ROOT}/install.sh" "${FAKE_ROOT}/install.sh"
    run env HOME="$FAKE_HOME" "${FAKE_ROOT}/install.sh" --global

install.sh는 타깃 인자가 없으면 CWD를 대상으로 삼는데, bats의 CWD는 실제 저장소다. 그리고 SELF_DIR이 FAKE_ROOT(임시 디렉터리)이므로 HOOKS_DIR도 임시 경로다. 결과적으로 실제 저장소에 대해 core.hooksPath를 임시 경로로 설정한다.

이 테스트의 주석은 '실제 hooks/ 파일을 지우는 테스트이므로 이 저장소 자신이 아니라 격리된 사본(FAKE_ROOT)에서 진행한다'고 적고 있다. 즉 격리 의도는 있었으나 **훅 소스만 격리했고 설치 대상은 격리하지 못했다.** --global 경로만 검증하려던 것이고 로컬 설치가 함께 일어난다는 점을 놓친 것으로 보인다.

## 실측 근거

GF-109 작업 중 반복 확인했다. 전체 스위트 실행 직후 core.hooksPath가 매번 다른 /var/folders/.../tmp.XXXX/hooks를 가리켰다. 그 상태에서 만든 커밋(4c1ea01)에는 Task-Id/AI 트레일러가 전혀 붙지 않았고, 훅을 복구한 뒤 만든 커밋에는 정상적으로 붙었다.

부수 피해도 확인됐다: 훅이 죽어 있던 동안 post-commit의 토큰 커서가 갱신되지 않아, 복구 직후 커밋(cbfa564)의 Tokens-Used가 실제 델타가 아닌 누적 오염값(55890695)으로 기록됐다.

## 왜 지금 고쳐야 하나

Python 전환(GF-110~113)이 남아 있고 매 태스크마다 전체 스위트를 돌린다. 그때마다 훅이 죽어 수동 복구가 필요하고, 복구를 잊으면 그 커밋의 트레일러가 소실된다. 이 프로젝트의 산출물 자체가 트레일러이므로 단순 불편이 아니라 데이터 손실이다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 tests/robustness-install.bats의 --global 케이스가 실제 저장소의 core.hooksPath를 건드리지 않는다 - 전체 스위트를 돌린 직후 git config --get core.hooksPath가 여전히 <저장소>/hooks를 가리키는 것으로 확인한다
- [x] #2 그 케이스가 원래 검증하려던 것(hooks/에서 파일이 삭제되면 sync_template이 대응 심볼릭 링크도 지운다)은 그대로 통과한다
- [x] #3 같은 함정이 남아 있는 다른 install.sh 호출부가 있는지 tests/ 전체를 확인하고, 있으면 함께 고친다
- [x] #4 회귀 방지: 스위트 실행 후 실제 저장소의 core.hooksPath가 보존되는지 검증하는 케이스를 추가한다
- [x] #5 bats tests/ 전체가 통과한다
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 해당 AC 범위의 bats 서브셋이 통과한다
- [ ] #2 CI(shellcheck + ruff)가 초록이다
- [x] #3 변경 파일이 AC 범위를 벗어나지 않는다
- [x] #4 커밋이 [type][subsystem] 규칙과 Task-Id 트레일러를 만족한다
- [x] #5 Done 전환 전 final summary에 객관적 검증 증거를 남긴다
- [x] #6 PR은 rebase-merge로만 머지한다
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. tests/robustness-install.bats의 '[정리] ...' 케이스를 읽고, install.sh가 --global만 처리하는 게 아니라 타깃(기본값 CWD)에 대한 로컬 설치도 함께 수행한다는 점을 확인한다.
2. 그 케이스에 격리된 타깃을 명시적으로 넘긴다. FAKE_ROOT는 git 저장소가 아니므로 install.sh가 거부한다 - 임시 git 저장소를 따로 만들어 타깃으로 준다. 이 케이스의 목적은 template/hooks 심볼릭 링크 정리(sync_template)이므로 타깃이 어디든 검증 내용은 바뀌지 않는다.
3. tests/ 전체에서 install.sh 호출부를 다시 훑어 같은 함정(타깃 생략)이 남아 있는지 확인한다.
4. 회귀 방지 케이스를 추가한다 - 실제 저장소의 core.hooksPath를 미리 읽어두고, --global 케이스 실행 후에도 값이 그대로인지 확인한다.
5. bats tests/ 전체를 돌리고, 실행 직후 git config --get core.hooksPath가 저장소 hooks를 그대로 가리키는지 확인한다(이게 이 태스크의 핵심 증거다).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
검증(2026-09-25):
- bats tests/robustness-install.bats 6/6 통과(신규 회귀 케이스 포함)
- bats tests/ 101/101 통과, 실패 0
- 핵심 증거: 전체 스위트 실행 직전/직후 git config --get core.hooksPath가 둘 다 ~/githubs/git-format/hooks로 동일. 수정 전에는 매 실행마다 /var/folders/.../tmp.XXXX/hooks로 바뀌었다.

고친 곳은 세 군데다 - [멱등성] 케이스의 --global 2회, [정리] 케이스의 --global 2회 중 나머지. 전부 setup()이 이미 만드는 TARGET_REPO를 타깃으로 넘기는 것으로 해결했다. 이 케이스들이 검증하는 것은 template/hooks 심볼릭 링크 생성/정리라 타깃이 어디든 검증 내용이 바뀌지 않는다.

AC #3(다른 호출부 확인): tests/ 전체에서 install.sh 호출부를 다시 훑었다. conf-guard.bats는 타깃을 명시하고 있고(TEST_REPO), robustness-dispatch.bats의 GF-16 케이스는 GITFORMAT_ROOT/install.sh --global을 타깃 없이 부르지만 HOOKS_DIR이 실제 저장소 hooks라 값이 정상값으로 유지된다 - 임시 경로 오염은 없다. 다만 같은 함정의 잠재 자리이므로 신규 회귀 케이스가 이 계열 전체를 잡는다.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
install.sh의 --global은 전역 설정만 하는 플래그가 아니라 타깃(기본값 CWD)에 대한 로컬 설치도 함께 수행한다. tests/robustness-install.bats의 세 호출부가 타깃을 생략해 bats의 CWD인 이 저장소 자신이 설치 대상이 됐고, 특히 [정리] 케이스는 HOOKS_DIR이 임시 디렉터리라 스위트를 돌릴 때마다 이 저장소의 core.hooksPath가 곧 삭제될 경로를 가리키게 만들었다. 그 뒤로는 커밋 메시지 검증도 트레일러 삽입도 에러 없이 조용히 사라진다.

setup()이 이미 만드는 격리된 TARGET_REPO를 타깃으로 넘겨 해결했다. 이 케이스들이 검증하는 것은 template/hooks 심볼릭 링크 생성/정리이므로 타깃이 어디든 검증 내용은 바뀌지 않는다.

회귀 방지 케이스를 추가했다 - 실행 전후로 이 저장소의 core.hooksPath를 비교하고, 동시에 타깃 쪽에 실제로 설치됐는지도 확인한다(설치가 아예 안 된 것으로 통과하면 안 되므로).

검증: bats tests/ 101/101 통과(실패 0). 핵심 증거는 전체 스위트 실행 직전/직후 core.hooksPath가 둘 다 저장소 hooks로 동일하다는 것 - 수정 전에는 매 실행마다 임시 경로로 바뀌었다.
<!-- SECTION:FINAL_SUMMARY:END -->
