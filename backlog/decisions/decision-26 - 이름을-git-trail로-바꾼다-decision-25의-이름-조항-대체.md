---
id: decision-26
title: 이름을 git-trail로 바꾼다 (decision-25의 이름 조항 대체)
date: '2026-10-03 03:43'
status: accepted
---
## Context

decision-25가 목적을 세 기둥(형식·출처 기록·이력 불변)으로 정하면서 이름을 git-logbook으로
바꿨다. 같은 날(2026-10-03) 유저가 이름을 다시 정했다 — 개발자들이 이런 도구를 부를 때 실제로
쓰는 말에서 고르기로 했다.

| 용어 | 뜻 | 이 프로젝트에서 |
| --- | --- | --- |
| trail (audit trail) | 누가·언제·무엇을 했는지 고칠 수 없게 남긴 기록 | 세 기둥 전체 |
| provenance | 결과물이 어디서 어떻게 만들어졌는지 (SLSA 용어) | 출처 기록 트레일러 |
| attestation | provenance를 기계가 검증할 수 있게 남긴 증명 (in-toto, Sigstore) | 아직 서명 없음 |
| audit | 기록을 사후에 대조·검사하는 일 | Fixes 검증, CI 검사 계획 |

유저 판단: 저장소 이름은 하나로 짧게 하고, 네 용어는 설명과 문서에 모두 적는다.

## Decision

**이름을 git-trail로 바꾼다.** audit trail에서 왔고, 이 도구가 남기는 git trailer와 소리도
겹친다. decision-25의 이름 조항(git-logbook)만 대체하고, 목적 세 기둥과 decision-11·12·19
대체 조항은 그대로 유효하다.

네 용어가 이 저장소의 어느 훅·함수·파일·원격 설정에 구현돼 있는지, 어디가 비어 있는지는
개념 지도 문서(GF-140)에 적는다. 이름에 용어를 다 넣는 대신 문서로 연결한다.

GitHub 저장소는 다시 rename한다(coralstay/git-logbook → coralstay/git-trail). 예전 이름
두 개(git-format, git-logbook)는 GitHub이 리다이렉트한다.

## Consequences

- 표시 이름만 바뀐다. 설정 키·파일명(`gitformat.*`)은 GF-133, 태스크 접두어 GF와 지난 기록
  본문은 decision-25와 같은 이유로 그대로 둔다. decision-25 본문의 "git-logbook"도 당시
  기록이라 고치지 않는다.
- attestation이라는 말을 쓰는 이상, 지금은 서명된 증명이 없다는 점을 개념 지도에 분명히
  적어야 한다. 기대와 실제가 어긋나지 않게 하기 위해서다.
