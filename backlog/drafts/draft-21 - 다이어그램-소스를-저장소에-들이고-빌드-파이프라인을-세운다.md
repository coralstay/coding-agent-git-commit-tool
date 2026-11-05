---
id: DRAFT-21
title: 다이어그램 소스를 저장소에 들이고 빌드 파이프라인을 세운다
status: Draft
assignee: []
created_date: '2026-10-03 02:41'
updated_date: '2026-10-03 02:41'
labels:
  - docs
  - tooling
dependencies: []
priority: medium
type: docs
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
훅 3개의 동작을 DOT 다이어그램 6개로 그려 아티팩트로 발행했는데(2026-10-03), 소스가 세션 스크래치패드에만 있다. 저장소에 들여야 diff·리뷰가 되고 훅을 고칠 때 다이어그램이 같이 갱신된다.

원본은 diagrams/*.dot이고 렌더된 SVG는 생성물이다. 색은 .dot에 센티넬 hex로 적고 빌드가 CSS 변수로 치환한다 — SVG 하나가 문서의 라이트/다크 테마를 그대로 따라간다. 참고 구현은 coralstay-software-factory의 build-diagrams.py(<!--dot:이름--> 마커 사이를 교체하는 방식).

결정이 필요한 지점은 주입 대상이다. GitHub은 마크다운 안의 인라인 <svg>/<style>을 sanitize하므로 README에 인라인하는 방식은 GitHub에서 보이지 않는다. <img src="diagrams/x.svg">로 참조하면 렌더되지만 그 SVG는 바깥 문서의 CSS 변수를 못 받는다. 실측해서 정하고 근거를 남긴다.

제약: graphviz 의존은 개발·CI 전용이어야 한다. decision-23에서 언어별 lint를 들어낸 이유가 컨슈머에게 도구 존재를 전제하게 만든다는 것이었다 — install.sh와 훅 실행 경로에는 graphviz가 새면 안 된다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 diagrams/*.dot 6개(lifecycle, hook1-prepare, hook2-commitmsg, hook3-postcommit, marker, token-cursor)를 저장소에 들인다
- [ ] #2 build-diagrams.py를 추가한다 — DOT→SVG 렌더, 센티넬 hex→CSS 변수 치환, <!--dot:이름--> 마커 교체
- [ ] #3 주입 대상을 실측해 결정하고 근거를 남긴다 — GitHub 마크다운의 svg/style sanitize 동작과 CSS 변수 상속 여부
- [ ] #4 렌더 산출물이 .dot과 어긋나면 실패하는 검사를 테스트에 추가한다
- [ ] #5 graphviz 의존이 install.sh와 훅 실행 경로에 새지 않음을 확인한다(decision-23의 교훈)
- [ ] #6 diagrams/readme.md에 '원본은 .dot, SVG는 생성물' 규약과 센티넬 색 대응표를 기록한다
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 .dot 하나를 고치고 빌드를 안 돌린 상태에서 AC#4의 검사가 실제로 실패하는 것을 확인한다
- [ ] #2 CI가 통과한다
<!-- DOD:END -->
