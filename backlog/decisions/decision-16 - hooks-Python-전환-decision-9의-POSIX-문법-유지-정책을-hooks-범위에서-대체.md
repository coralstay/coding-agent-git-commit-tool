---
id: decision-16
title: "hooks Python 전환: decision-9의 POSIX 문법 유지 정책을 hooks/* 범위에서 대체"
date: "2026-09-24 10:09"
status: accepted
---

## Context

decision-9는 `hooks/*`, `install.sh`, `hooks/checks/*.sh`를 순수 POSIX sh로
유지하기로 결정했다. 근거는 이 훅들이 컨슈머 저장소 어디서든 커밋마다
실행되므로 bash조차 보장되지 않는 환경(최소 구성 컨테이너, 오래된 시스템
bash)에서도 깨지지 않아야 한다는 것이었다. Consequences 절에 "그런 변경이
필요하다면 이 decision을 먼저 재검토해야 한다"고 명시돼 있다.

GF-88에서 한 차례 Python 전환을 평가했으나 채택하지 않았다. 기각 사유는 두
가지였다 — (1) 당시 실측한 훅 복잡도(최대 224줄, 분기가 평평하고 주석이
충분함)로는 Python의 표현력 이득이 크지 않았고, (2) 검토한 배포 방식이
"Nuitka/PyInstaller로 컴파일한 네이티브 바이너리"였는데, 이것이 README의
"적용 전에 hooks/ 코드를 직접 읽고 검토하라"는 감사 가능성 약속과 정면으로
충돌했다. 바이너리만 배포하면 소비자가 실제로 실행되는 것이 무엇인지 소스만
보고는 확인할 수 없기 때문이다.

이번에는 기여 접근성(POSIX sh보다 Python에 익숙한 개발자가 훨씬 많다)을
이유로 전환을 다시 제안받았고, GF-88의 기각 사유가 이번에도 적용되는지
검토했다.

## Decision

- **decision-9의 "POSIX sh 문법만 사용한다" 조항을 다음 파일 범위에서
  대체한다**: `hooks/pre-commit`, `hooks/commit-msg`, `hooks/post-commit`,
  `hooks/checks/{ts,python,sql,java,cpp}.py`. 이 8개 파일은 Python 3으로
  작성한다.
- **`install.sh`는 decision-9의 적용을 그대로 받는다** — POSIX sh를 유지한다.
  다만 이 스크립트가 연결하는 훅들이 Python 실행을 요구하게 되므로, 설치
  시점에 `command -v python3`으로 존재를 확인하는 가드를 추가한다.
- **배포 방식은 해석되는 Python 소스 그대로다.** 컴파일하지 않는다. git이
  직접 실행하는 3개 훅은 `#!/usr/bin/env python3` 셔뱅을 가진 단일 파일로,
  지금 sh 훅과 같은 "읽는 파일 = 실행되는 파일" 성질을 유지한다. **GF-88이
  기각한 것은 이 배포 모델이 아니라 컴파일된 바이너리 배포였고, 그 기각
  사유(감사 가능성 충돌)는 이번 결정에는 적용되지 않는다.**
- **표준 라이브러리만 사용한다.** pip/venv/pyproject.toml 등 패키징을
  도입하지 않으므로 소비자에게 별도 설치 단계가 생기지 않는다.
- **`gitformat.conf` 읽기는 지금처럼 `git config --file` 서브프로세스 호출을
  유지한다.** ini 파서를 직접 구현하면 git 자신의 파싱 의미론(다중값
  `--get-all`, 따옴표 처리)과 조용히 갈라질 위험이 있다.
- **파일 간 로직 중복은 유지한다.** Python에는 `import`가 있지만 공유 모듈을
  만들지 않는다. "파일 하나를 읽으면 그 훅의 동작을 독립적으로 전부 파악할
  수 있다"는 성질은 sh 때문에 생긴 제약이 아니라 이 저장소가 지키려는
  감사 가능성의 일부다. `tests/consistency.bats`가 중복 블록의 동일성을
  계속 검증한다.

## Consequences

- **소비자 저장소에 `python3`이 필요해진다.** 지금까지 "git만 있으면 된다"던
  전제가 깨진다. README의 "Runtime deps: none" 문구를 명시적 필요조건
  섹션("Requirements: git, python3")으로 교체해야 한다(GF-113).
- **설치돼 있는 것만으로는 부족하고, 훅이 실행되는 시점의 PATH에도 잡혀야
  한다.** GUI git 클라이언트(SourceTree, GitHub Desktop, IDE 내장 패널)는 셸
  프로파일을 거치지 않고 OS 최소 PATH만 물려받는 경우가 흔해, Homebrew/pyenv로
  설치된 python3를 못 찾을 수 있다. 이 문제는 코드로 우회하지 않고 알려진
  한계로 문서화하기로 했다(sh 런처 + git config로 경로를 저장하는 방식을
  검토했으나 채택하지 않음).
- **훅별로 실패 양상이 다르다.** `pre-commit`/`commit-msg`는 python3을 못
  찾으면 커밋이 막혀 실패가 눈에 띄지만, `post-commit`은 이미 커밋이 만들어진
  뒤라 트레일러가 조용히 누락된 채 커밋이 성공한 것처럼 보인다. 이 비대칭을
  README에 명시하고 실제 동작을 bats로 검증한다(GF-113).
- **`install.sh`의 확인은 설치 시점만 보장한다.** 보통 터미널에서 실행되므로
  PATH가 풍부하고, 실제 커밋이 일어나는 GUI 환경의 좁은 PATH까지 보장하지는
  못한다.
- **CI의 shellcheck 대상이 `install.sh` 하나로 줄고, Python 린트(ruff)가
  추가된다.** shellcheck 대상 목록이 글롭이 아니라 파일명 직접 지정이므로,
  각 훅이 Python이 되는 커밋에서 해당 파일명을 목록에서 같이 빼야 한다.
  미루면 그 사이 커밋들에서 CI가 Python 파일을 sh로 린트하려다 깨진다.
- **decision-9의 나머지 조항은 그대로 유효하다** — `install.sh`의 POSIX sh
  유지, 표기 관례(들여쓰기 2칸, 줄 길이 제한, 네이밍), `tests/*.bats`가
  bash인 것에 대한 예외 인정은 모두 계속 적용된다. decision-13이 대체한
  vendoring 조항도 그대로다.
- **앞으로 이 8개 파일에 기여하려면 Python을, `install.sh`에 기여하려면
  POSIX sh를 써야 한다.**
