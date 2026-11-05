---
id: m-4
title: "hooks Python 전환: 비리팩토링"
---

## Description

소비자에게 실제로 달라지는 새 계약/정책 부분 - 순수 리팩토링이 아닌 변경들.

python3 런타임 의존성이 새로 생기는 것, 그것을 강제하는 install.sh 가드, decision-9(POSIX sh 유지)를 해당 범위에서 대체하는 새 decision, README에 명시적 필요조건을 고지하는 것, 그리고 sh에는 없던 새 실패 모드(GUI git 클라이언트 최소 PATH에서 python3 미탐지)를 실제로 검증하는 것.
