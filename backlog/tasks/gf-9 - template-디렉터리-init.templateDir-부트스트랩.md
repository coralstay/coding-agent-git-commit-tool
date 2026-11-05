---
id: GF-9
title: template/ 디렉터리 (init.templateDir 부트스트랩)
status: Done
assignee: []
created_date: '2026-08-24 03:12'
updated_date: '2026-08-24 03:47'
labels: []
dependencies:
  - GF-7
type: task
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
신규 저장소 자동 부트스트랩용 hooks/.gitmessage 구성(decision-2)
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
template/ 디렉터리와 .gitignore(template/hooks/ 제외) 추가, install.sh --global이 sync_template()으로 hooks/*를 가리키는 절대경로 심볼릭 링크를 template/hooks/에 생성하고 init.templateDir+commit.template을 전역 설정하도록 구현. git init --template이 심볼릭 링크를 그대로 복사하며 절대경로라 항상 올바르게 동작함을 실측 확인. fake HOME으로 install.sh --global → git init --template → 실제 commit-msg 검증까지 전체 체인 테스트 완료.
<!-- SECTION:FINAL_SUMMARY:END -->
