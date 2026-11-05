---
id: GF-60
title: decision-7 상태 표시 관례 정리
status: Done
assignee: []
created_date: '2026-08-27 20:29'
updated_date: '2026-08-27 21:01'
labels: []
dependencies: []
ordinal: 58000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
decision-7은 decision-8로 대체됐지만 backlog decision CLI에 상태(status)를 바꾸는 명령이 없어(create/list만 존재) backlog decision list에는 여전히 accepted로 남아있다. CLI 자체를 고칠 수 없으므로, 이런 대체 관계를 어떻게 표시/확인할지 관례를 정하고 문서화한다(예: CLAUDE.md에 'decision 목록을 볼 때 본문에 superseded 언급이 있는지 항상 확인' 명시, 또는 backlog.md 자체에 기능 요청).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 decision 상태 CLI 한계와 대응 관례가 어딘가에(CLAUDE.md 또는 별도 문서) 명시된다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
CLAUDE.md에 '## Backlog Decision 상태 확인 관례' 섹션을 추가(backlog.md 자동생성 블록 밖에 별도로 둬서 도구 업데이트 시 덮어써지지 않게 함). backlog decision CLI에 view가 없다는 것까지 확인 후 문구를 파일 직접 읽기로 정정.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
backlog decision CLI에 상태 변경/조회(view) 명령이 없다는 한계를 CLAUDE.md에 문서화하고, decision 참고 시 파일 본문에서 superseded 여부를 확인하라는 관례를 명시했다.
<!-- SECTION:FINAL_SUMMARY:END -->
