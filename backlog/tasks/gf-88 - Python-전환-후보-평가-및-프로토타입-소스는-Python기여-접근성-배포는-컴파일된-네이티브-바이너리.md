---
id: GF-88
title: 'Python 전환 후보 평가 및 프로토타입: 소스는 Python(기여 접근성), 배포는 컴파일된 네이티브 바이너리'
status: Done
assignee: []
created_date: '2026-09-03 11:26'
updated_date: '2026-09-03 11:30'
labels: []
milestone: m-0
dependencies: []
ordinal: 86000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
git-format은 공개 저장소라 훅을 고치고 싶은 외부 기여자가 진입장벽 없이 수정할 수 있어야 한다는 게 이 스토리의 동기다. POSIX sh보다 Python이 더 많은 개발자에게 익숙해 기여 문턱을 낮출 수 있지만, git-format의 핵심 정체성인 '런타임 의존성 없음'(README/decision-9)은 계속 지켜야 하므로 소스는 Python으로 작성하고 실사용(배포) 시점에는 Nuitka/PyInstaller 등으로 컴파일한 네이티브 바이너리를 배치하는 방식을 검증한다. 이 스토리는 전체 훅을 일괄 전환하지 않고, 어떤 훅을 전환할지 기준을 정하고 훅 1개로 빌드 파이프라인을 프로토타입해 실제로 성립하는 접근인지부터 검증하는 범위로 한정한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 어떤 훅을 Python으로 전환할지(전환 안 하고 sh로 남길 훅은 무엇인지) 판단 기준이 정리된다 - GF-87에서 확립한 sh 컨벤션으로 충분히 읽기 쉬운 훅은 굳이 전환 안 해도 됨을 포함해 검토한다
- [ ] #2 훅 1개를 Python으로 재작성하고 Nuitka 또는 PyInstaller로 컴파일해, macOS/Linux 각각에서 Python 런타임 없이 실행되는 네이티브 바이너리가 실제로 나오는지 검증한다(Windows는 README의 기존 한계와 별개로 우선순위 낮음)
- [ ] #3 컴파일된 바이너리의 훅 실행 지연시간(commit/push 시 체감 딜레이)이 기존 sh 대비 허용 가능한 수준인지 측정한다
- [ ] #4 빌드 산출물을 저장소에 커밋할지, CI로 빌드해 릴리스 아티팩트로 배포할지, 설치 시점에 로컬 컴파일할지 배포 방식이 결정된다
- [ ] #5 바이너리 배포가 README의 '적용 전에 hooks/ 코드를 직접 읽고 검토하라'는 감사 가능성 경고와 어떻게 공존할지(예: Python 소스를 나란히 커밋해 바이너리와 대조 가능하게 하는 등) 방안이 정리된다
- [ ] #6 이 결정이 decision-9(POSIX 문법 유지)를 어느 범위까지 대체하는지 명시하는 새 decision이 기록된다
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
사용자와 논의 후 Python 전환을 채택하지 않기로 결정. 근거: (1) 현재 훅 복잡도를 실측한 결과(최대 224줄, 분기는 평평하고 주석 충분) Python의 표현력 이득이 크지 않음. (2) 이 스토리의 동기였던 '공개 저장소이니 누구나 손쉽게 수정 가능해야 한다'는 목표는, 실행 파일을 Python 소스가 아닌 컴파일된 바이너리로 배포하는 순간 오히려 README의 '적용 전에 hooks/ 코드를 직접 읽고 검토하라'는 감사 가능성 약속과 충돌해 목표에 역행함. sh는 읽는 파일이 곧 실행되는 파일이라 이 목표를 이미 더 잘 만족하고 있음. 프로토타입/빌드/지연시간 측정 등 AC 2~6은 이 결정에 따라 실행하지 않으며, 객관적 검증 증거가 없으므로 AC를 체크하지 않고 미실행 상태로 종료함. 셸 컨벤션 확립은 GF-87로 대체 진행.
<!-- SECTION:FINAL_SUMMARY:END -->
