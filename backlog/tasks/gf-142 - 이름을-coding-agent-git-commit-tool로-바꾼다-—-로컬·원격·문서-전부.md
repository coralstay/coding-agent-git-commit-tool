---
id: GF-142
title: 이름을 coding-agent-git-commit-tool로 바꾼다 — 로컬·원격·문서 전부
status: Done
assignee:
  - '@claude'
created_date: '2026-10-03 13:10'
updated_date: '2026-10-03 13:14'
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
- [x] #1 decision-29가 이름 변경을 기록하고 decision-26의 이름 조항만 대체한다고 명시한다(범용 유지 판단, 개명 사유 포함)
- [x] #2 표시 이름 git-trail이 README·install.sh·훅 주석·.gitmessage·CI·테스트·backlog config·backlog docs에서 새 이름으로 바뀐다(gitformat.* 설정 키·파일명, 지난 decision·task 본문은 제외)
- [x] #3 README 첫 설명이 커밋 규칙 검사와 커밋마다 작성자·AI 모델·태스크·토큰 자동 기록을 말한다
- [x] #4 전체 테스트와 ruff가 통과한다
- [x] #5 GitHub 저장소가 coralstay/coding-agent-git-commit-tool로 rename되고 origin URL·description·topics가 갱신된다
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. decision-29 기록
2. 표시 이름 일괄 치환(문서는 backlog doc update로), README 제목·첫 설명·이름 변천 문장 수정
3. 테스트·ruff·shellcheck
4. GitHub rename, origin URL·description·topics 갱신 (push 훅이 Done을 요구하므로 PR 전에)
5. PR 머지 후 운영 단계: 로컬 폴더 이동, hooksPath 재설치(이 저장소·agent-orchestartor), 메모리 복사
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
검증: unittest 106건 OK, ruff·shellcheck 통과. git-trail 잔존은 README의 이름 변천 문장과 doc-21의 "이전 이름" 서술뿐(의도). GitHub: coralstay/coding-agent-git-commit-tool, 옛 URL 301 리다이렉트 확인, ruleset 23313297 active 유지, origin URL 갱신. 승격 커밋 3393957 제목에서 태스크 번호가 빠졌다(셸이 $id로를 변수명으로 읽음) — amend 금지라 그대로 둔다. backlog 문서는 처음에 파일로 직접 고쳤다가 되돌리고 backlog doc update로 다시 적용했다.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
이름을 git-trail에서 coding-agent-git-commit-tool로 바꿨다(decision-29, decision-26의 이름 조항 대체, 범용 범위 유지). README·install.sh·훅 주석·.gitmessage·CI·테스트·backlog config·doc-1·5·16·20·21의 표시 이름을 바꾸고, README 첫 설명을 하는 일(규칙 검사 + 작성자·모델·태스크·토큰 자동 기록) 중심으로 다시 썼다. GitHub 저장소를 rename하고 origin URL·description·topics를 갱신했다. 검증: 테스트 106건·ruff·shellcheck 통과, 옛 URL 301 리다이렉트와 ruleset 유지 확인. 로컬 폴더 이동과 hooksPath 재설치는 병합 뒤 운영 단계로 한다.
<!-- SECTION:FINAL_SUMMARY:END -->
