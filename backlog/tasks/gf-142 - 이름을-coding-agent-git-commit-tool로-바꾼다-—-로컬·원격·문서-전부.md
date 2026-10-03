---
id: GF-142
title: 이름을 coding-agent-git-commit-tool로 바꾼다 — 로컬·원격·문서 전부
status: To Do
assignee: []
created_date: '2026-10-03 13:10'
updated_date: '2026-10-03 13:11'
labels:
  - docs
  - chore
dependencies: []
references:
  - decision-25
  - decision-26
  - GF-140
  - GF-133
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
"git-trail"은 이 도구가 하는 일을 말해주지 못했다. 유저가 2026-10-03 "와닿지 않는다"며 프로젝트가 무엇을 하는지부터 다시 정리했고, 오해의 여지가 없도록 하는 일을 그대로 적은 이름으로 정했다: coding-agent-git-commit-tool. 지원 범위는 Claude 전용으로 좁히지 않는다(유저 판단 — git-claude 대신 범용 이름). 유저 지시: 로컬·원격·문서 모두 바꾼다.

바꾸지 않는 것: gitformat.* 설정 키(GF-133), 태스크 접두어 GF, 지난 기록 본문.

로컬 폴더 이동은 병합 뒤 마지막에 한다 — 세션 도중 옮기면 트랜스크립트 경로가 어긋나 남은 커밋의 Tokens-Used/AI-Model 측정이 끊긴다. 옮긴 뒤 이 저장소와 agent-orchestartor의 core.hooksPath를 새 경로로 다시 설치하고, Claude 메모리를 새 프로젝트 경로로 복사한다. 이 단계는 저장소 파일을 바꾸지 않으므로 AC가 아니라 병합 후 운영 단계로 두고 결과를 노트에 남긴다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 decision-29가 이름 변경을 기록하고 decision-26의 이름 조항만 대체한다고 명시한다(범용 유지 판단, 개명 사유 포함)
- [ ] #2 표시 이름 git-trail이 README·install.sh·훅 주석·.gitmessage·CI·테스트·backlog config·backlog docs에서 새 이름으로 바뀐다(gitformat.* 설정 키·파일명, 지난 decision·task 본문은 제외)
- [ ] #3 README 첫 설명이 커밋 규칙 검사와 커밋마다 작성자·AI 모델·태스크·토큰 자동 기록을 말한다
- [ ] #4 전체 테스트와 ruff가 통과한다
- [ ] #5 GitHub 저장소가 coralstay/coding-agent-git-commit-tool로 rename되고 origin URL·description·topics가 갱신된다
<!-- AC:END -->
