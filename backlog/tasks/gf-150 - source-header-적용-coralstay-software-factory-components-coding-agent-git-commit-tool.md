---
id: GF-150
title: >-
  source-header 적용:
  coralstay-software-factory/components/coding-agent-git-commit-tool
status: In Progress
assignee: []
created_date: '2026-10-31T11:08:00Z'
updated_date: '2026-10-31T12:44:00Z'
labels:
  - source-header
  - rollout
dependencies: []
documentation:
  - /Users/flynn_macpro/.claude/plans/giggly-kindling-snowglobe.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## 배경
source-header 6단계(dev-tools/source-header TASK-3)의 저장소별 적용 카드. 유저 결정(2026-10-31):
~/githubs 아래 내가 짠 코드는 AGPL-3.0-only, 외부 코드·책 예제는 제외, description은 서브에이전트 초안,
README·CHANGELOG는 제외하고 설계 문서는 포함, 기존 저장소의 .githooks에는 source-header 플러그인만 설치.

## 대상 저장소
`~/githubs/coralstay-software-factory/components/coding-agent-git-commit-tool` (순서 그룹: 1-now)

## .source-header.json (초안)
```json
{"include": ["**"], "exclude": ["**/README.md", "**/CHANGELOG.md", "backlog/**", ".opensource/**", "contents/**", "content_data/**", "githooks/**"]}
```

## 라이선스 조치
AGPL 유지(README 표기를 AGPL-3.0-only로)

## 메모
이 저장소 자신은 아직 옛 방식(hooksPath=클론 hooks/) → migrate로 .githooks 전환 포함. 커밋 형식 플러그인도 유지.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 .mailmap(전역 ~/.mailmap과 같은 매핑)을 저장소에 커밋해 다른 클론·CI에서도 authors가 coralstay로 나온다
- [x] #2 라이선스 조치를 마친다: AGPL 유지(README 표기를 AGPL-3.0-only로)
- [ ] #3 .source-header.json을 확정하고(제외 대상 재확인) source-header init으로 헤더를 넣고, 서브에이전트가 description 초안을 쓴다. source-header lint 오류 0
- [ ] #4 이 저장소의 hooksPath를 git-commit-tool migrate로 .githooks로 옮기고 커밋 형식 검사가 계속 동작함을 확인한다
- [ ] #5 git-commit-tool --plugins source-header로 .githooks를 설치하고(core.hooksPath=.githooks) 헤더 없는 파일 커밋이 막히는 것을 실측한다
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 source-header lint . 오류 0 (출력을 Implementation Notes에 첨부)
- [ ] #2 저장소의 기존 테스트·빌드가 헤더 추가 후에도 통과
- [ ] #3 유저가 description diff를 검토
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
### Subjective
유저가 ~/githubs 기존 파일 전체에 소스 헤더 적용을 결정했다(2026-10-31). 이 카드는 `coralstay-software-factory/components/coding-agent-git-commit-tool` 담당.

### Objective
TASK-3 조사 결과는 Description 참고. source-header(init/lint/fix/hook)와 git-commit-tool .githooks(GF-148)가 준비됐고, --plugins 옵션은 git-commit-tool 별도 draft에서 추가한다.

### Assessment
헤더는 git에서 유도 가능한 값은 init에 맡기고 description만 서브에이전트가 쓴다. 생성물은 생성기에서 헤더를 넣는다. 커밋은 단계별로 나눠 diff 검토가 쉽게 한다.

### Plan
1. .mailmap 커밋
2. 라이선스 조치 커밋
3. .source-header.json → init → description 초안(서브에이전트) → lint 0 → 커밋(파일이 많으면 디렉터리 단위로 나눔)
4. (해당 시) 생성기 수정
5. .githooks 설치(--plugins source-header) → 실측
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
AC #2 (2026-10-31): README 배지·라이선스 절·기여 조항을 AGPL-3.0-only로 명확히 함. LICENSE 본문은 그대로.
<!-- SECTION:NOTES:END -->
