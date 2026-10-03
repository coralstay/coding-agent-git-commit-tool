---
id: GF-140
title: git-trail로 개명하고 개념 지도 문서를 만든다
status: In Progress
assignee:
  - '@claude'
created_date: '2026-10-03 03:31'
updated_date: '2026-10-03 03:43'
labels:
  - docs
  - naming
dependencies: []
references:
  - decision-25
  - decision-24
documentation:
  - backlog/docs/doc-3 - AI-귀속-트레일러-레퍼런스.md
  - backlog/docs/doc-20 - GitHub-원격-강제-설정-관리-—-rulesets와-저장소-설정.md
priority: medium
type: docs
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GF-138에서 git-logbook으로 개명했지만 유저가 이름을 다시 정했다(2026-10-03). 개발자들이 이런 도구를 부르는 말 네 가지, trail(audit trail)·provenance·attestation·audit 중 짧은 git-trail을 저장소 이름으로 쓰고, 네 용어는 설명과 GitHub topics에 모두 적는다. git-trail은 audit trail에서 왔고 git trailer와 소리도 겹친다.

decision-25가 정한 목적 세 기둥(형식·출처 기록·이력 불변)은 그대로다. 바뀌는 건 이름뿐이다.

이름에 용어를 다 넣는 대신, 각 용어가 이 저장소의 어느 훅·함수·파일·원격 설정으로 구현돼 있는지 짚는 문서를 만든다. 지금은 그런 문서가 없어서, 예컨대 attestation이라는 말을 보고 서명된 증명을 기대한 사람이 실제로는 서명 없는 트레일러뿐이라는 걸 알기 어렵다. 그래서 구현된 것과 빈 곳을 함께 적는다.

GF-138과 같은 원칙으로 설정 키 gitformat.*(GF-133), 태스크 접두어 GF, 지난 기록 본문은 바꾸지 않는다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 decision-26으로 이름을 git-trail로 바꾼다고 기록하고, decision-25의 이름 조항만 대체한다고 명시한다
- [ ] #2 README, install.sh, 훅 주석, .gitmessage, CI, 테스트, backlog config, doc-1·5·6·20의 표시 이름 git-logbook이 git-trail로 바뀐다 (설정 키·파일명 gitformat.*은 제외)
- [ ] #3 trail·provenance·attestation·audit 각각의 정의, 구현 위치(훅 함수·파일·설정·원격), 빈 곳을 적은 개념 지도 문서를 backlog doc으로 만든다
- [ ] #4 개념 지도의 구현 위치는 실제 코드의 함수명·파일 경로와 일치한다
- [ ] #5 README에서 개념 지도 문서로 안내한다
- [ ] #6 PR을 머지 커밋으로 병합한 뒤 GitHub 저장소를 coralstay/git-trail로 rename하고 origin URL을 갱신한다
- [ ] #7 GitHub 저장소 description과 topics에 trail·provenance·attestation·audit을 반영한다
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 python3 -m unittest discover -s tests 전체 통과
- [ ] #2 ruff check 통과
- [ ] #3 git grep -i git-logbook -- ':!backlog' 결과에 의도한 예외만 남는다
- [ ] #4 rename 뒤 예전 URL 두 개(git-format, git-logbook)가 새 저장소로 리다이렉트되고 ruleset이 유지된다
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. decision-26 기록 → 커밋
2. 표시 이름 git-logbook → git-trail 치환(README·install.sh·훅·테스트·CI·.gitmessage·config·doc-1/5/6/20) → 테스트 → 커밋
3. 개념 지도 doc 신규(trail·provenance·attestation·audit, 실제 함수·파일 기준) + README 링크 → 커밋
4. 서브에이전트 독립 검토(함수명·경로 대조)
5. PR → 머지 커밋 → gh repo rename git-trail → origin 갱신 → description/topics → 리다이렉트 확인
<!-- SECTION:PLAN:END -->
