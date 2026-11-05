---
id: GF-140
title: git-trail로 개명하고 개념 지도 문서를 만든다
status: Done
assignee:
  - '@claude'
created_date: '2026-10-03 03:31'
updated_date: '2026-10-03 07:17'
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
- [x] #1 decision-26으로 이름을 git-trail로 바꾼다고 기록하고, decision-25의 이름 조항만 대체한다고 명시한다
- [x] #2 README, install.sh, 훅 주석, .gitmessage, CI, 테스트, backlog config, doc-1·5·6·20의 표시 이름 git-logbook이 git-trail로 바뀐다 (설정 키·파일명 gitformat.*은 제외)
- [x] #3 trail·provenance·attestation·audit 각각의 정의, 구현 위치(훅 함수·파일·설정·원격), 빈 곳을 적은 개념 지도 문서를 backlog doc으로 만든다
- [x] #4 개념 지도의 구현 위치는 실제 코드의 함수명·파일 경로와 일치한다
- [x] #5 README에서 개념 지도 문서로 안내한다
- [x] #6 PR을 머지 커밋으로 병합한 뒤 GitHub 저장소를 coralstay/git-trail로 rename하고 origin URL을 갱신한다
- [x] #7 GitHub 저장소 description과 topics에 trail·provenance·attestation·audit을 반영한다
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 python3 -m unittest discover -s tests 전체 통과
- [x] #2 ruff check 통과
- [x] #3 git grep -i git-logbook -- ':!backlog' 결과에 의도한 예외만 남는다
- [x] #4 rename 뒤 예전 URL 두 개(git-format, git-logbook)가 새 저장소로 리다이렉트되고 ruleset이 유지된다
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. decision-26 기록 → 커밋
2. 표시 이름 git-logbook → git-trail 치환(README·install.sh·훅·테스트·CI·.gitmessage·config·doc-1/5/6/20) → 테스트 → 커밋
3. 개념 지도 doc 신규(trail·provenance·attestation·audit, 실제 함수·파일 기준) + README 링크 → 커밋
4. 서브에이전트 독립 검토(함수명·경로 대조)
5. PR → 머지 커밋 → gh repo rename git-trail → origin 갱신 → description/topics → 리다이렉트 확인
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
검증: unittest 98개·ruff·shellcheck 통과. git grep -i git-logbook -- ':!backlog'는 README 개명 이력 줄만 남음. doc-6에는 git-logbook 문자열이 없어 바꿀 것이 없었음(AC#2). 개념 지도 doc-21은 서브에이전트가 함수명·경로·GitHub 설정을 코드와 실측으로 대조 — is_replay_commit 행의 오류(post-commit에는 면제 없음), --no-verify 우회 누락, 원격 보호 빈 곳 누락, %G? 서술을 반영해 고침. 유저 지시로 Tokens-Used 서술을 '설계 의도는 커밋당 토큰량, 현재 구현은 델타라 의도와 다름(GF-129)'으로 정정.

AC#6·7·DoD#4 검증(2026-10-03): PR #43을 머지 커밋 cb3ca9d로 병합 후 gh repo rename git-trail. origin을 git@github.com:coralstay/git-trail.git으로 변경, ls-remote main=cb3ca9d. 예전 URL git-format·git-logbook 모두 HTTPS 301 → coralstay/git-trail, SSH ls-remote 성공. description과 topics(git-hooks, commit-trailers, audit-trail, provenance, attestation, audit, ai-attribution) 설정 확인. 병합 설정(merge만)과 ruleset main-protection(active) 유지.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
이름을 git-trail로 바꾸고(decision-26) 표시 이름을 맞췄으며, trail·provenance·attestation·audit의 구현 위치와 빈 곳을 doc-21로 정리해 README에서 연결했다. 테스트 98개·ruff·shellcheck 통과. PR #43 머지 후 저장소를 coralstay/git-trail로 rename하고 description·topics를 설정했으며, 예전 두 URL의 리다이렉트와 원격 강제 설정 유지를 확인했다.
<!-- SECTION:FINAL_SUMMARY:END -->
