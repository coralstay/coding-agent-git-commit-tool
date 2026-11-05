---
id: GF-66
title: push --no-verify 우회 방지 안내 강화 검토
status: Done
assignee: []
created_date: '2026-08-27 20:29'
updated_date: '2026-08-27 21:12'
labels: []
dependencies: []
ordinal: 64000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
로컬 git hook 구조상 git push --no-verify는 근본적으로 탐지 불가하고, opt-in GitHub Actions 백스톱(verify.yml)을 브랜치 보호 필수 status check로 걸어야만 실질적 방어가 된다. 현재 README에 이 사실과 백스톱 설치 방법이 안내돼 있지만, '왜 반드시 브랜치 보호를 걸어야 하는지'가 충분히 강조되지 않았을 수 있다. README 안내를 재검토해 필요하면 강화한다(예: 설치 직후 안내 메시지에 opt-in 백스톱 권장 문구 추가 등).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 README 또는 install.sh 출력 메시지에 브랜치 보호 필수화 권장이 명확히 드러나는지 재검토하고, 부족하면 보강한다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
재검토 결과 README 자체 설명은 이미 충분(단순 워크플로 추가만으로는 강제 안 됨을 명시)했지만, 설치 시점(install.sh 실행 직후)에는 이 사실이 전혀 안내되지 않아 사용자가 README의 해당 섹션까지 안 읽으면 놓칠 수 있었다. install.sh 마지막에 'git push --no-verify는 로컬 훅으로 탐지 불가, 백스톱을 브랜치 보호 필수 status check로 설정하라'는 안내를 항상 출력하도록 추가(--global 여부와 무관하게 항상 표시). bats 8/8 통과, shellcheck 통과.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
install.sh 실행 시 마지막에 push --no-verify 우회 방지를 위한 GitHub Actions 백스톱 설정 권장 안내를 항상 출력하도록 추가했다. README의 기존 설명은 이미 충분하다고 판단해 유지.
<!-- SECTION:FINAL_SUMMARY:END -->
