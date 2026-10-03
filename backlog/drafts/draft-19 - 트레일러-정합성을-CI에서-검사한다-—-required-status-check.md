---
id: DRAFT-19
title: 트레일러 정합성을 CI에서 검사한다 — required status check
status: Draft
assignee: []
created_date: '2026-09-26 13:22'
updated_date: '2026-10-03 03:14'
labels:
  - ci
  - policy
dependencies: []
references:
  - decision-24
documentation:
  - backlog/docs/doc-20 - GitHub-원격-강제-설정-관리-—-rulesets와-저장소-설정.md
  - backlog/docs/doc-19 - 이력을-바꾸는-git-연산별-훅-판별-방법-실측.md
priority: high
type: feature
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
원격에는 트레일러가 참인지 검사하는 수단이 없다. rulesets에 커밋 메시지 패턴 규칙이 아예 없다(GitHub 문서 확인). 그래서 로컬 훅을 거치지 않은 커밋이 그대로 들어온다.

## 막지 못하는 경로

- GitHub 웹 UI의 파일 편집 → 커밋 생성. 로컬 훅을 전혀 거치지 않으므로 트레일러가 **하나도 없다**
- 훅을 지운 클론에서의 push
- 손으로 쓴 거짓 트레일러 — `Signed-off-by`를 아무 이름으로 쓰거나 `Hooks-Commit`에 없는 해시를 적어도 아무도 확인하지 않는다
- 실제로 이 저장소에서 그 일이 일어났다: main의 커밋들이 `Signed-off-by: cpu-once`를 달고 있는데 실제 committer는 `coralstay`다(rebase-merge가 원인, 지금은 차단됨)

## 왜 CI인가

유저가 제안한 "트레일러를 직접 뜯어 마커와 실제 값이 맞물리는지 최종 검사"의 자리가 여기다. `post-commit`은 커밋이 이미 만들어진 뒤라 **막을 수 없다**. CI는 **완성된 커밋 객체를 보면서 required status check으로 병합을 막을 수 있는** 유일한 자리다.

decision-24가 마커를 "지워질 훅의 오판을 막으려 살려둔 죽은 코드"로 만든 것도 여기서 해소된다 — 트레일러 자체가 직접 증거이므로 마커라는 대리 지표가 필요 없다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 PR의 각 커밋에 대해 트레일러를 파싱해 검사한다 (git interpret-trailers --parse 또는 %(trailers) 포맷)
- [ ] #2 Signed-off-by가 그 커밋의 실제 committer와 일치하는지 확인한다 — 불일치는 이력 재작성의 증거다
- [ ] #3 Hooks-Commit이 git-format 저장소에 실재하는 커밋을 가리키는지 확인한다
- [ ] #4 Task-Id가 브랜치명의 패턴과 일치하는지 확인한다
- [ ] #5 같은 트레일러 키가 두 번 나타나지 않는지 확인한다
- [ ] #6 제목이 [type][subsystem] 형식인지 확인한다 — 웹 UI 커밋은 로컬 검증을 거치지 않았다
- [ ] #7 merge 커밋과 revert 커밋은 git이 메시지를 지어주므로 제목 형식 검사에서 제외한다
- [ ] #8 GitHub Actions 워크플로로 구현하고 ruleset의 required_status_checks로 등록한다
- [ ] #9 실패 메시지가 어느 커밋의 어느 트레일러가 왜 어긋났는지 지목한다
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 의도적으로 어긋난 트레일러를 가진 커밋으로 실제 PR을 만들어 CI가 막는지 확인
- [ ] #2 정상 커밋으로 만든 PR은 통과하는지 확인
<!-- DOD:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-10-03 03:14
---
2026-10-03: decision-19가 Signed-off-by 제거를 정했지만, 이 드래프트(09-26)가 더 최근이라 유저 규칙(최근 문서 우선)에 따라 Signed-off-by는 유지된다 — decision-25에 기록. AC#2(Signed-off-by와 실제 committer 대조)는 유효하다. 컨슈머 배포 여부는 이 드래프트에서 정한다(decision-25 미결 항목).
---
<!-- COMMENTS:END -->
