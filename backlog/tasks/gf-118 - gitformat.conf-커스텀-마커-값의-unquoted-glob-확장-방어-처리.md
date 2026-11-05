---
id: GF-118
title: gitformat.conf 커스텀 마커 값의 unquoted glob 확장 방어 처리
status: Done
assignee: []
created_date: '2026-09-19 15:46'
updated_date: '2026-09-25 03:08'
labels: []
dependencies: []
documentation:
  - backlog/docs/doc-4 - 커스터마이즈-가이드.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
hooks/pre-commit:86, hooks/checks/java.sh:49가 ls ${MARKER_JAVA_GRADLE}처럼 unquoted glob 확장을 의도적으로 사용한다(shellcheck disable=SC2086 명시). 현재는 gitformat.conf가 유일한 신뢰된 값 출처라 실질 위험은 낮지만, marker.javaGradle 등 커스텀 값에 공백/특수문자가 섞이면 예기치 않은 파일 매칭이 될 수 있다. 방어적으로 quoting하거나 값 검증을 추가할지 검토.

발견 경위: 2026-09-20 '이 프로젝트의 부족한점?' 조사(Explore agent, hooks/pre-commit:86, hooks/checks/java.sh:49)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 sh 시절의 unquoted glob 확장(SC2086) 위험이 Python 포팅으로 실제로 해소됐는지 실측으로 확인되고 그 근거가 기록된다
- [x] #2 hooks/gitformat.conf의 marker 항목에 어떤 키가 glob 패턴으로 해석되고 어떤 키가 리터럴 경로로 해석되는지 명시된다
- [x] #3 리터럴 키에 glob을 넣으면 조용히 미매칭된다는 함정이 doc-4에 기록된다
- [x] #4 마커 값이 단어 분리되지 않는다는 것을 고정하는 회귀 테스트가 추가되고 통과한다
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Python 포팅 후 마커 값이 실제로 어떻게 해석되는지 실측해 sh 시절 SC2086 위험이 남았는지 판정한다
2. conf_get이 gitformat.conf만 읽는지(로컬 git config 오버레이 없음) 확인해 값의 신뢰 경계를 확정한다
3. 남은 결함을 정의하고 그에 맞는 조치를 한다
4. tests/marker-semantics.bats로 규약을 회귀 고정한다
5. ruff + bats 전체로 회귀가 없음을 확인한다
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
판정: GF-118이 지적한 원래 위험(unquoted glob 확장으로 인한 단어 분리 → 예기치 않은 파일 매칭)은 Python 전환으로 실제로 해소됐다. 실측: glob.glob('a b') -> ['a b'], os.path.isfile('a b') -> True — 값이 단일 인자로 넘어가 단어 분리가 원리적으로 일어나지 않는다. 그래서 quoting 추가는 할 일이 없고, 값 검증도 넣지 않았다.

값 검증을 넣지 않은 이유: conf_get()은 git config --file CONF만 읽고 컨슈머 저장소의 로컬 git config는 전혀 참조하지 않는다(hooks/pre-commit:48-56 확인). 즉 마커 값의 출처는 git-format 클론 안의 gitformat.conf 하나뿐이고, doc-4가 이미 '컨슈머가 직접 건드릴 파일은 아니고 포크/커스터마이즈할 때 참고하는 내부 설정 파일'이라고 못박고 있다. 신뢰 경계가 이렇게 좁은 값에 런타임 검증을 붙이는 건 비용만 늘린다.

대신 실제로 남아 있던 결함을 고쳤다: 어떤 키가 글롭이고 어떤 키가 리터럴인지 아무 곳에도 적혀 있지 않았고, 틀리면 에러가 아니라 조용한 미매칭이 된다. 실측: os.path.isfile('build.gradle*') -> False. 포크한 사람이 java = pom*.xml로 바꾸면 자바 검사가 영원히 안 돌지만 경고가 없다. 이 규약을 hooks/gitformat.conf 주석과 doc-4 표로 남기고, tests/marker-semantics.bats 6개로 고정했다.

java.py:49 주석은 손대지 않았다 — 같은 시점에 GF-115가 그 파일을 수정 중이어서 충돌을 피했고, 규약을 값이 실제로 사는 gitformat.conf에 두는 게 참조 지점으로도 낫다고 판단했다.

검증 증거: (AC1) 실측 출력 — glob.glob('a b') -> ['a b'], os.path.isfile('a b') -> True (단어 분리 없음), glob.glob('build.gradle*') -> ['build.gradle'] (글롭은 정상 확장). 원래 위험 해소 확인. (AC2) hooks/gitformat.conf의 [gitformat "marker"] 위에 리터럴 키/글롭 키 목록과 읽는 방식이 명시됐고, git config --file로 conf가 여전히 정상 파싱됨을 확인(javaGradle=build.gradle*, python 2줄 모두 조회됨). (AC3) doc-4에 해석 표와 'java = pom*.xml은 영원히 매칭되지 않고 경고도 없다'는 함정이 기록됐다. (AC4) bats tests/marker-semantics.bats 6/6 통과. 회귀: bats tests/ 전체 110/110 통과(기존 104 + 신규 6, 실패 0), ruff check . 통과.

테스트 설계 중 실측으로 고친 점: 첫 작성에서 java 감지 신호를 'mvn/gradlew를 찾을 수 없어 건너뜀' 출력으로 잡았는데, 이 머신에는 mvn이 실제로 설치돼 있어 marker.java 경로를 쓰는 테스트가 감지 후 실제 mvn compile을 돌려 실패했다(6개 중 1개). path_without mvn으로 커밋하도록 바꿔 '감지 여부'만 관측하게 분리했다.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
GF-118이 지적한 원래 위험은 이미 해소돼 있었다 — Python 전환으로 마커 값이 glob.glob()/os.path.isfile()에 단일 인자로 넘어가 단어 분리가 원리적으로 불가능하다(실측: glob.glob('a b') -> ['a b']). 그래서 quoting/값 검증은 추가하지 않았고, conf_get()이 gitformat.conf만 읽어 값의 출처가 하나뿐이라는 점(pre-commit:48-56)을 근거로 남겼다. 대신 실제로 남아 있던 결함을 고쳤다: 리터럴 키와 글롭 키가 섞여 있는데 어디에도 적혀 있지 않고, 틀리면 조용한 미매칭이 된다(실측: os.path.isfile('build.gradle*') -> False). 규약을 hooks/gitformat.conf 주석과 doc-4 표에 명시하고 tests/marker-semantics.bats 6개로 고정했다. bats 110/110, ruff 통과.
<!-- SECTION:FINAL_SUMMARY:END -->
