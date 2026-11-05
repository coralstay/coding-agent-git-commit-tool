---
id: doc-9
title: hooks POSIX sh → Python 전환 초기 계획
type: specification
created_date: '2026-09-24 09:22'
updated_date: '2026-09-24 09:22'
tags:
  - python-migration
  - hooks
  - plan
---
# git-format 훅 POSIX sh → Python 전환

## Context

git-format의 소비자 저장소용 git 훅(`hooks/pre-commit`, `hooks/commit-msg`,
`hooks/post-commit`, `hooks/checks/*.sh`)은 지금 순수 POSIX sh로 작성돼 있다.
이걸 Python으로 옮기려는 게 이번 요청이다.

이 저장소에는 정확히 이 주제를 다룬 두 개의 기존 결정이 있다:

- **GF-88**(Done, 2026-09-03): Python 전환을 평가했지만 **채택하지 않기로
  기각**했다. 이유는 두 가지 — (1) 당시 실측한 훅 복잡도(최대 224줄, 분기
  평탄)로는 Python의 표현력 이득이 크지 않았고, (2) 검토한 배포 방식이
  "Nuitka/PyInstaller로 컴파일한 네이티브 바이너리"였는데, 이게 README의
  "적용 전에 hooks/ 코드를 직접 읽고 검토하라"는 감사 가능성 약속과 정면
  충돌했다(바이너리만 배포하면 실제로 뭐가 실행되는지 소스만 봐서는 확인 불가).
- **decision-9**(여전히 accepted): `hooks/*`, `install.sh`,
  `hooks/checks/*.sh`를 "별도 런타임 없이 git 자체만으로" 동작해야 한다는
  이유로 POSIX sh에 의도적으로 묶어둔 결정. bash조차 보장 안 되는 환경(최소
  컨테이너 등)에서도 깨지지 않아야 한다는 제약 때문이다. Consequences 절에
  "이탈하려면 이 결정을 먼저 재검토해야 한다"고 명시돼 있다.

이번 대화에서 사용자와 확인한 결과, 이번 전환은 GF-88이 기각한 것과
**다른 배포 모델**이다 — 컴파일된 바이너리가 아니라, 지금 sh 훅과 같은
"읽는 파일 = 실행되는 파일" 감사 가능성을 유지하는 Python 소스를 배포한다.
GF-88의 기각 사유는 이번 전환에는 적용되지 않는다.

**엄밀히는 이 작업은 순수 리팩토링이 아니다.** 리팩토링(관찰 가능한
동작은 그대로, 내부 구조만 변경)에 해당하는 부분과, 소비자에게 실제로
달라지는 새 계약(python3 의존성)을 도입하는 부분이 섞여 있다 — 그래서
아래에서 두 마일스톤으로 나눈다.

**설계 확정: git이 직접 실행하는 3개 훅(`pre-commit`/`commit-msg`/
`post-commit`)은 sh 런처 없이 `#!/usr/bin/env python3` 셔뱅을 가진 단일
Python 파일 그대로 간다.** 예시(사용자 제시):

```python
#!/usr/bin/env python3
import sys

print("커밋 메시지 검사 중...")
sys.exit(0)
```

**받아들이는 트레이드오프**: 소비자 저장소에 `python3`이 설치돼 있어야
하고, **설치돼 있는 것만으로 충분하지 않다 — 훅이 실행되는 시점의
PATH 환경에도 `python3`이 잡혀야 한다**는 전제가 생긴다. GUI git
클라이언트(SourceTree, GitHub Desktop, IDE 내장 git 패널 등)는 셸
프로파일(.zshrc 등)을 거치지 않고 OS의 최소 PATH(macOS는 launchd가
물려주는 `/usr/bin:/bin:/usr/sbin:/sbin` 수준)만 물려받는 경우가 흔해서,
Homebrew/pyenv로만 설치된 python3(`/opt/homebrew/bin/python3` 등)을 그
환경에서 못 찾을 수 있다. 이 문제는 **코드로 우회하지 않고, README에
알려진 한계로 문서화**한다(sh 런처 + `git config`로 경로를 저장해두는
우회 방식은 검토했으나 채택하지 않음 — "파이썬은 설치해야 하는 것"이라는
전제를 그대로 받아들이기로 함).

영향 범위는 훅마다 다르다:
- `pre-commit`/`commit-msg`: python3을 못 찾으면 훅이 nonzero로 실패하고
  git이 **커밋을 막는다** — 실패가 눈에 띄므로 안전한 실패.
- `post-commit`: 이미 커밋이 완료된 뒤라 실패해도 git이 신경 쓰지
  않는다 — python3을 못 찾으면 Task-Id/AI-Model/Signed-off-by 같은
  트레일러가 **조용히 누락된 채 커밋은 그냥 성공한 것처럼 보인다**.
  이게 이 트레이드오프의 가장 날카로운 지점.
- `install.sh`의 python3 설치 확인은 설치 시점(보통 터미널, 풍부한
  PATH)에만 검증하므로, 실제 커밋이 일어나는 실행 시점(GUI 클라이언트,
  좁은 PATH)의 동작까지는 보장하지 못한다.

`hooks/checks/*.py` 5개는 git이 아니라 `pre-commit`이 호출하므로 PATH
탐색 문제 자체가 없다 — `pre-commit`이 이미 실행 중인 자신의 인터프리터
경로(`sys.executable`)를 그대로 재사용해 checks 스크립트를 실행한다.

`template/hooks/*` 심볼릭 링크 배포 때문에, git이 직접 실행하는 3개
파일은 각자 자신의 실제 위치를 알아야 하는 문제(기존 sh의
`resolve_self()`가 하던 일)가 여전히 남는다 — 다만 Python에서는
`os.path.realpath(__file__)`가 심볼릭 링크 체인을 기본으로 따라가므로
sh처럼 수동 루프를 짤 필요가 없다(정당한 단순화).

중복 로직을 Python `import`로 공유 모듈화할지 물었고, 사용자는 **지금처럼
파일마다 독립적으로 중복 유지**를 선택했다 — sh의 "파일 하나 = 독립적으로
읽고 감사 가능" 원칙을 유지한다.

git 서브프로세스 호출과 관련해 두 가지를 확정했다: (1) 모든
`subprocess.run(...)` 호출에 `encoding="utf-8"`을 명시한다 — 안 그러면
로케일에 따라 디코딩이 달라져 GF-80과 같은 성격의 버그가 새 형태로
재현될 수 있다. (2) 인터프리터 기동 비용은 `-S`(site 모듈 스캔 생략)
플래그, 무거운 import의 지연 로딩으로 낮추고, 최적화 여부는 마일스톤 1
검증에서 실측 후 판단한다 — 미리 과도하게 최적화하지 않는다.
`gitformat.conf`는 지금처럼 `subprocess`로 `git config --file`을 계속
호출한다(ini 파서 직접 구현 안 함 — git의 실제 파싱 의미론과 갈라질
위험, `tests/consistency.bats` GF-61이 가정하는 동작과 어긋날 위험 때문).

추가로 사용자는 (1) 새로 쓰는 Python 코드에 불필요한 주석을 넣지 말고
정리된 상태로 작성할 것, (2) `hooks/`, `hooks/checks/` 등 관련 디렉토리에
각각 역할을 설명하는 readme.md를 추가할 것을 요청했다. (2)는 이미
`backlog/` 하위 7개 폴더에 readme.md를 추가한 선례(GF-103, 소문자
파일명, "무엇인가"/"언제 쓰나"/"관련 명령" 구조)를 재사용한다.

**스코프 밖(이번 전환 완료 후 별도 검토)**:
- "스트림 계열을 써서 훅들을 정리하는 방법" — 이번 전환은 기능 동작이
  sh 버전과 동일함을 검증하는 게 최우선이라 포함하지 않는다.
- "bats 테스트를 다시 짜는 것" — 이번엔 기존 103개 bats 테스트를 안전망
  그대로 재사용하고, 언어 변경에 따라 꼭 필요한 경로 수정만 반영한다.
- "토큰 사용량 강제(초과 시 커밋 거부)" 같은 향후 기능 — 구조적으로
  `post-commit`은 커밋이 이미 만들어진 뒤 실행돼 막을 수 없으므로, 그런
  기능은 나중에 `pre-commit`/`commit-msg` 쪽으로 옮겨 설계해야 한다는
  점만 기록해두고, 지금은 코드에 반영하지 않는다.

## 마일스톤 구성

- **마일스톤 1 — 엄밀한 리팩토링**: python3이 정상 동작하는 환경에서
  기존 sh와 관찰 가능한 동작이 완전히 동일하도록 로직만 옮기는 부분.
  기존 bats 103개(블랙박스, 언어 무관)로 검증 가능하다.
- **마일스톤 2 — 리팩토링이 아닌 부분**: 소비자에게 실제로 달라지는
  새 계약/정책 — python3 의존성이 새로 생기는 것, 그걸 강제하는
  install.sh 가드, decision-9를 부분 대체하는 새 backlog decision,
  README에 새 필요조건을 명시하는 것, sh에는 없던 새 실패 모드(GUI
  PATH)를 검증하는 것.

**순서 제약(마일스톤이 실행 순서와 일치하지 않음)**: 마일스톤 2의 일부
(새 decision 기록, install.sh 가드)는 이 저장소 관례상 코드 변경보다
먼저 커밋돼야 하고, 안전상으로도 마일스톤 1의 파일 포팅이 시작되기
전에 끝나 있는 게 낫다(python3 없는 환경에서 포팅된 훅을 테스트하다
원인 파악이 늦어지는 걸 방지). 마일스톤 2의 나머지(README 필요조건
문구, 새 실패 모드 bats)는 마일스톤 1의 파일 포팅과 함께 마무리한다.
그래서 실행 순서는: **(1) 마일스톤 2 선행 작업 → (2) 마일스톤 1 본작업 →
(3) 마일스톤 2 마무리 작업**이다.

---

## 마일스톤 2 선행 작업

**선행/병렬 구분**: Phase 0(decision 기록)과 Phase 1(install.sh 가드)은
파일 내용상 서로를 직접 참조하지 않아 기술적으로는 병렬 가능하다. 다만
이 저장소 관례(코드 변경 전에 decision부터 커밋)를 따라 **Phase 0을
먼저 끝내고 Phase 1을 시작**하는 순서를 권장한다 — 강제 의존은 아니고
관례상 선후관계다.

### Phase 0 — 거버넌스: 새 decision 기록

`backlog decision create "hooks Python 전환: decision-9의 POSIX 정책을
hooks/*, hooks/checks/*.sh 범위에서 대체" -s accepted`로 생성한 뒤,
decision-13과 같은 구조(대체 대상 decision-9 조항 재서술 → 지정한 범위에서만
대체 선언 → decision-9의 나머지 조항은 유효함을 재확인)로 본문을 채운다.

포함할 내용:
- **Context**: GF-88의 기각 사유(컴파일 바이너리의 감사 가능성 문제)와
  decision-9의 제약을 요약하고, 이번 결정이 GF-88과 다른 배포 모델(해석되는
  Python 소스, 단일 파일)을 쓴다는 점을 명시.
- **Decision**: `hooks/pre-commit`, `hooks/commit-msg`, `hooks/post-commit`,
  `hooks/checks/{ts,python,sql,java,cpp}.py`만 decision-9 범위에서 제외.
  `install.sh`는 계속 decision-9 적용(POSIX sh 유지). 파일 간 로직 중복은
  유지. stdlib만 사용, pip/venv/pyproject.toml 등 패키징 도입 안 함.
- **Consequences**: 소비자 저장소에 `python3`이 설치돼 있고 **실행 시점
  PATH에도 잡혀야 함**(신규 요구사항, install.sh가 설치 시점에만 검증 —
  실행 시점 GUI 클라이언트 PATH까지는 보장 못 함, README에 알려진 한계로
  문서화). README "Runtime deps: none" 문구 갱신 필요.

이 decision 기록이 실제 코드 변경보다 먼저 커밋되는 첫 단계다.

### Phase 1 — `install.sh`에 python3 존재 확인 가드 추가

기존 `gitformat.conf` 읽기 가드 바로 다음 자리에, 같은 스타일로 추가:

```sh
if ! command -v python3 >/dev/null 2>&1; then
  echo "install.sh: python3을 찾을 수 없습니다 - git-format 훅은 Python으로 실행됩니다." >&2
  exit 1
fi
```

`tests/robustness-install.bats`에 python3 없는 환경(기존 `path_without()`
헬퍼 재사용) 케이스는 마일스톤 2 마무리 작업에서 추가한다(이 가드 코드
자체는 지금 넣되, 테스트는 마일스톤 2 검증 단계에 묶어서 한 번에 확인).

---

## 마일스톤 1 — 엄밀한 리팩토링

**작업 분해(선행 vs 병렬)**: 아래는 "파일마다 독립 중복" 원칙 때문에
코드 의존이 거의 없다는 걸 이용한 병렬화다.

- **의존 없음, 바로 시작**: `.gitignore`에 `__pycache__/` 추가 — 다른
  어떤 작업과도 무관, 아무 때나(가장 먼저 해도 됨).
- **1차 병렬 그룹 (서로 완전 독립)**: `hooks/checks/{python,ts,java,cpp,
  sql}.py` 5개 — 언어별로 코드 공유가 없으므로 5개를 동시에 진행해도
  서로 부딪힐 일이 없다. 각각 대응하는 `tests/checks-*.bats`의 `.sh`
  경로 하드코딩 확인/갱신도 같은 그룹 안에서 각자 처리.
- **1차 그룹 완료 후에만 가능(선행 필수)**: `hooks/pre-commit` 포팅 —
  디스패치 로직이 `hooks/checks/<lang>.py`를 파일명으로 직접 참조하므로,
  적어도 그 파일들이 `.py`로 존재해야 한다.
- **1차 그룹/`pre-commit`과 병렬 가능**: `hooks/commit-msg` 포팅 —
  `pre-commit`이나 checks 스크립트를 호출하지 않는 독립 로직(메시지
  검증)이라 코드 의존이 없다. 언제든 동시에 진행 가능.
- **코드 의존은 없으나 실무적으로는 `pre-commit` 이후 권장**:
  `hooks/post-commit` 포팅 — `pre-commit`이 쓰는 `.gitformat-verified`
  마커를 읽는 역할이지만, 이 마커는 포맷 기반 계약이라 pre-commit이 sh든
  Python이든 상관없이 작동한다(언어 무관 상호운용). 그래도 "마커를 쓰는
  쪽 → 읽는 쪽" 순서로 검증하는 게 원인 추적이 쉬워 순차 권장(강제 아님).
- **첫 `.py` 파일(예: checks/python.py) 등장 이후 아무 때나, 포팅
  작업과 병렬 가능**: Phase 3의 CI `ruff check` 스텝 추가.
- **포팅과 병렬로 초안 작성 가능, 단 내용 확정은 8개 파일 전부 끝난
  뒤**: Phase 4의 `hooks/readme.md`/`hooks/checks/readme.md` — 최종
  구조를 설명하는 문서라 초안은 미리 써도 되지만 마지막 파일까지
  끝나야 내용이 확정된다.
- **8개 파일 전부 끝난 뒤에만 가능(마지막, 전체 의존)**:
  `tests/consistency.bats` 갱신(모든 포팅 파일에 걸친 바이트 동일성
  검사라 부분 상태로는 의미가 없음), 마일스톤 1 전체 검증(`bats
  tests/` 전체 재실행, 지연시간 실측, 수동 스모크 테스트).

### Phase 2 — 훅 파일별 포팅 순서 (AC 단위 커밋 + 각 단계 후 관련 bats 실행)

1. **`hooks/checks/python.py`** (원본 18줄, 가장 단순 — 패턴 검증용) →
   `bats tests/checks-python.bats`
2. **`hooks/checks/ts.py`** — `package.json`의 `scripts.lint` 확인을
   `json.load()`로 직접 파싱(정당한 단순화). `tsc` 우선순위(로컬
   `node_modules/.bin/tsc` > PATH, `npx` 금지, GF-79)는 그대로 유지 →
   `bats tests/checks-ts.bats`
3. **`hooks/checks/java.py`** → `bats tests/checks-java.bats`
4. **`hooks/checks/cpp.py`** — `git diff --cached -z` 출력을 `\0`로
   split(NUL-안전, `mktemp`/`xargs -0` 불필요 — 정당한 단순화) →
   `bats tests/checks-cpp.bats`
5. **`hooks/checks/sql.py`** — 동일한 NUL-split 단순화 →
   `bats tests/checks-sql.bats`
6. **`hooks/pre-commit`** (단일 파일, `#!/usr/bin/env python3`) —
   `os.path.realpath(__file__)`로 자기 실제 위치 확인, 마커 파일 기반
   언어 감지, 5개 체크 스크립트를 `sys.executable`로 호출, 성공 시
   `.gitformat-verified` 마커 기록. **같은 커밋에 `.github/workflows/
   test.yml`의 shellcheck 대상 목록에서 `hooks/pre-commit`을 제거**
   (CI의 shellcheck 대상이 글롭이 아니라 파일명 직접 지정이라, 이걸
   미루면 이 커밋부터 CI가 Python 파일을 sh로 린트하려다 깨진다) →
   `bats tests/robustness-dispatch.bats tests/smoke.bats
   tests/conf-guard.bats`
7. **`hooks/commit-msg`** (단일 파일) — 커밋 메시지를 `errors="replace"`로
   UTF-8 디코드하면 `LC_ALL=C`(GF-80)와 `LC_ALL=C.UTF-8`+`wc -m` 트릭이
   모두 필요 없어짐(Python `str`/`len()`이 코드포인트 단위 — 정당한
   단순화). Task-Id 앵커링 정규식(GF-34) 그대로 이식. **같은 커밋에
   shellcheck 대상 목록에서 `hooks/commit-msg` 제거**(위와 같은 이유) →
   `bats tests/robustness-commit-msg.bats tests/robustness-injection.bats`
8. **`hooks/post-commit`** (단일 파일) — amend-재귀 방지 가드가 반드시
   맨 먼저 실행돼야 함(지금과 동일). `git interpret-trailers --if-exists`의
   prefix 매칭 문제(GF-33)를 피하려고 지금처럼 직접 "key: value" 파싱
   유지(단순화 금지 대상). `jq` 호출을 `json.loads()`로 대체(jq 의존성
   제거, 부수적 개선)하되 한 줄이라도 파싱 실패 시 전체 배치를 실패
   처리하는 현재의 fail-open 단위(`MEASUREMENT_REASON=
  "transcript-parse-failed"`)는 유지. AI-Model 조회는 지금처럼 좁은
   범위에서만 실패를 삼키는 유일한 예외로 남김. **같은 커밋에
   shellcheck 대상 목록에서 `hooks/post-commit` 제거**(위와 같은 이유 —
   이 시점에 `install.sh`만 남는다) →
   `bats tests/robustness-post-commit.bats` 후 전체 `bats tests/` 1회 더
   실행

각 파일은 sh 버전의 gotcha를 문자 그대로가 아니라 **동일한 실패 모드
방지**로 이식한다:
- sh의 `readonly VAR="$(cmd)"`가 실패를 삼키는 문제(GF-76) → Python
  subprocess 호출은 기본적으로 실패 시 예외를 던지게 한다.
- `git config --get`은 명시적 빈 값도 성공 취급(GF-35) → Python에서도
  빈 문자열 명시 체크를 유지.
- 모든 `subprocess.run(...)`에 `encoding="utf-8"` 명시(로케일 의존 디코딩
  방지, GF-80과 같은 성격의 새 버그 방지).

### Phase 3 — CI 갱신 (`.github/workflows/test.yml`)

- shellcheck 대상 목록에서 `hooks/pre-commit`/`commit-msg`/`post-commit`은
  Phase 2의 6~8번 각 커밋에서 이미 제거됨(뒤로 미루면 그 사이 커밋들에서
  CI가 깨짐). `hooks/checks/*.sh`는 글롭이라 파일이 하나씩 `.py`로
  바뀔 때마다 자동으로 줄어들어 별도 조치 불필요. Phase 3에서는 남은
  `install.sh` 하나만 대상인지 최종 확인.
- 새 Python 파일들(`hooks/pre-commit`, `commit-msg`, `post-commit`,
  `hooks/checks/*.py`)에 대해 `ruff check`(또는 `pyflakes`) 스텝 추가.

### Phase 4 — `hooks/readme.md`, `hooks/checks/readme.md` 신설

- **`hooks/readme.md`**: 훅 생애주기 흐름(pre-commit → commit-msg →
  커밋 생성 → post-commit), 각 훅이 이제 Python으로 실행된다는 점,
  `gitformat.conf` 역할. `backlog/` 하위 폴더 readme.md와 같은 스타일.
- **`hooks/checks/readme.md`**: pre-commit이 마커 파일로 언어를 감지해
  이 디렉토리의 스크립트를 `sys.executable`로 호출하는 디스패치
  메커니즘, 5개 언어별 체크 스크립트의 역할과 외부 도구 의존성.

### Phase 5 — 기존 테스트 최소 반영 (재작성 아님)

- `tests/consistency.bats`: 대상 파일 경로를 `.sh`에서 확장자 없는 새
  Python 파일/`.py`로 갱신(중복 유지하므로 바이트 동일성 검사 구조 자체는
  안 바뀜).
- **`tests/checks-{ts,python,sql,java,cpp}.bats` 내부에 `hooks/checks/
  *.sh` 같은 경로가 하드코딩돼 있는지 각 파일 포팅 시점에 확인하고
  `.py`로 갱신** — Phase 2에서 "해당 bats 실행"만으로는 이 하드코딩을
  못 잡을 수 있으므로 파일을 열어 직접 확인하는 단계를 포함한다.
- 스위트 자체의 재설계는 이번 전환 범위 밖(스코프 밖 항목 참고).

### `.gitignore`

`__pycache__/`, `*.pyc` 추가(Python이 자동 생성하는 바이트코드 캐시가
untracked로 지저분해지거나 실수로 커밋되는 것 방지).

### 코드 스타일

새로 작성하는 Python 코드는 불필요한 주석 없이 작성한다. WHY가 비자명한
경우에만 한 줄 주석을 남긴다 — 예: GF-33/34/35/76/80처럼 과거 회귀를 막기
위한 특정 패턴, AI-Model 조회가 의도적으로 실패를 삼키는 이유, 파일 간
로직을 의도적으로 중복 유지하는 이유. "무엇을 하는지" 설명하는 주석은
넣지 않는다.

### 마일스톤 1 검증

- Phase 2의 각 파일 포팅 후 해당 bats 서브셋 실행 — 전부 sh 버전과 동일하게
  통과해야 한다(블랙박스 테스트라 언어 무관).
- 8개 파일 전부 포팅 후 `bats tests/` 전체 1회 재실행.
- 인터프리터 기동 지연시간 실측(sh 대비 체감 지연) — 필요시에만 `-S`
  플래그/지연 import 최적화 적용.
- **수동 스모크 테스트(정상 동작 확인)**: bats의 `make_isolated_repo()`는
  `core.hooksPath`를 직접 가리키는 방식만 쓰고, `install.sh`의
  `sync_template()`이 만드는 심볼릭 링크 경로(`template/hooks/*`)는
  거치지 않는다 — `os.path.realpath(__file__)`를 통한 심볼릭 링크 해석
  경로는 bats만으로는 검증되지 않는다. 스크래치 디렉터리에서
  `install.sh`를 실제로 실행해 템플릿 경로로 새 저장소를 만들고: (a)
  정상 형식 커밋 성공, (b) 형식 위반 커밋 거부, (c) `--no-verify` 커밋에
  `Verify-Bypassed: true` 소급 삽입, (d) AI 귀속 환경변수 설정 시
  `AI-Tool`/`Co-Authored-By`/`AI-Model` 트레일러 삽입을 직접 확인한다.
  이 객관적 증거 없이는 AC를 체크하지 않는다(이 저장소의
  task-finalization 지침).

---

## 마일스톤 2 마무리 작업

**선행/병렬 구분**:
- **의존 없음, 아주 일찍부터 병렬 가능**: README 필요조건 섹션 자체는
  코드 상태와 무관한 소개 문구라 마일스톤 2 선행 작업 시점부터도 써 둘
  수 있다(마일스톤 1 완료를 기다릴 필요 없음).
- **Phase 1(install.sh 가드) 완료 후 아무 때나, 마일스톤 1과 병렬
  가능**: `tests/robustness-install.bats`의 python3 없는 **설치 시점**
  케이스 — install.sh는 마일스톤 1의 훅 파일들과 무관하므로 Phase 1만
  끝나 있으면 언제든 검증 가능.
- **마일스톤 1에서 해당 훅이 포팅된 뒤에만 가능(순차 의존)**: 훅
  **실행 시점** PATH에 python3이 없을 때의 동작을 검증하는 신규 bats
  케이스 — 예를 들어 `pre-commit`의 PATH-없음 테스트는 `pre-commit`이
  실제로 Python으로 포팅된 뒤에야 의미가 있다. 이 항목만 마일스톤 1의
  진행 상황을 따라간다(3개 훅 각각 포팅 완료 시점에 맞춰 하나씩 추가
  가능 — 8개 전부 끝날 때까지 기다릴 필요는 없고, 해당 훅만 끝나면
  그 훅의 케이스부터 병렬로 추가 가능).

### README 필요조건 섹션 + GUI PATH 한계 문서화

- 루트 `README.md`의 "Runtime deps: none"을 **명시적 필요조건 섹션**으로
  교체: "Requirements: git, python3 (PATH에서 실행 가능해야 함)"을 설치
  안내보다 먼저 보이는 자리에 둔다. 그 아래에 **GUI git 클라이언트 PATH
  한계를 문서화**: python3은 설치돼 있는 것만으로는 부족하고 훅 실행
  시점 PATH에도 잡혀야 하며, 특히 `post-commit` 트레일러가 조용히
  누락될 수 있다는 비대칭 위험을 강조.
- `hooks/readme.md`(마일스톤 1에서 신설)에도 이 python3 PATH 요구사항을
  한 줄 반영.

### 새 실패 모드 검증 (신규 bats — sh엔 없던 동작이라 "재검증"이 아니라 "신규 검증")

- `tests/robustness-install.bats`: python3 없는 설치 환경(기존
  `path_without()` 헬퍼 재사용) 케이스 — Phase 1에서 만든 가드가
  명확한 에러로 설치를 막는지 확인.
- **훅 실행 시점(설치 시점 아님) PATH에 python3이 없을 때의 동작을
  검증하는 bats 케이스 신설** — `path_without()`으로 python3을 숨긴
  환경에서 (a) `pre-commit`/`commit-msg`가 nonzero로 실패해 커밋이
  막히는지, (b) `post-commit`이 실패해도 커밋 자체는 유지되고 트레일러만
  누락되는지 직접 확인한다 — README에 문서화한 두 훅의 비대칭 실패
  동작이 실제로 그런지 객관적 증거 없이 문서만 써두지 않는다.

---

## 실행 방식 (PR/머지)

- **이번 마이그레이션 한정으로 push → PR → 머지까지 자동 진행 권한을
  받았다**(사용자 확인: "이번 마이그레이션은 알아서 머지까지 진행하길
  원해") — 다른 일반 작업에는 적용되지 않는, 이번 건에 한정된 승인이다.
  머지는 이 저장소 관례대로 rebase-merge만 사용한다(squash/merge-commit
  금지 — 로컬 훅이 fast-forward-only도 강제).
- **트렁크 방식이 아니라 로컬/리모트가 어긋날 수 있다는 점을 사용자가
  주의로 줌** — push/PR 생성/머지 각각을 하기 전에 매번 `git fetch`로
  원격 상태를 먼저 확인하고, 필요하면 최신 `main`으로 rebase한 뒤
  진행한다. branch protection은 현재 `main`에 걸려있지 않음을 확인했다
  (`gh api repos/.../branches/main/protection` → 404).
- PR을 몇 개로 나눌지(마일스톤당 1개/전체 1개/파일 단위)는 **지금 정하지
  않는다** — 이후 이 계획을 backlog draft로 옮길 때 그 단위에 맞춰
  정한다(사용자: "이후 백로그 나눌 거고 그때 단위를 정할 것. 지금은 보류").

## backlog 구조화 (마일스톤 2개 + 태스크 7개) — 채울 필드 전체

CLI 확인 결과 채울 수 있는 항목 전체는 다음과 같다(프론트매터 + 본문 섹션):

- **프론트매터**: `id`(자동), `title`, `status`, `assignee`, `labels`,
  `dependencies`, `type`(bug/feature/enhancement/task/chore/docs/spike),
  `priority`(High/Medium/Low), `ordinal`, `milestone`, `due_date`,
  `parent`, `references`(--ref/--add-ref), `docs`(--doc),
  `modified_files`(--modified-file)
- **본문 섹션**: Description, Acceptance Criteria(--ac),
  Definition of Done(--dod), Implementation Plan(--plan),
  Implementation Notes(--notes), Final Summary(--final-summary),
  Comments(--comment)
- **단계 제약**: `--plan`/`--notes`는 활성 상태(In Progress)에서만,
  `--final-summary`는 종료 상태에서만 채울 수 있다 → 실행 단계에서 채운다.
  `draft create`는 title/description/assignee/status/labels만 지원하므로
  나머지 필드는 promote 직후 `task edit`으로 채운다.
- 이 저장소에는 DoD 기본값 설정이 없고 기존 태스크에 DoD 사용 이력도
  없다 — 이번엔 7개 태스크 전부에 공통 DoD를 명시적으로 채운다.

**공통 필드**: assignee `@claude`, labels `python-migration` + 태스크별
보조 라벨, ordinal은 실행 순서대로 부여.

**공통 DoD(7개 태스크 전부 동일)**:
1. 해당 AC 범위의 bats 서브셋이 통과한다
2. CI(shellcheck + ruff)가 초록이다
3. 변경 파일이 AC 범위를 벗어나지 않는다(범위 밖 발견 시 유저 확인)
4. 커밋이 `[type][subsystem]` 규칙 + Task-Id 트레일러를 만족한다
5. Done 전환 전 final summary에 객관적 검증 증거를 남긴다

**태스크별 채울 내용**:

| # | 제목 | milestone | type | 보조 labels | depends-on | AC 수 | modified-file |
|---|------|-----------|------|-------------|------------|-------|---------------|
| 1 | 거버넌스: decision 기록 + install.sh python3 가드 | M2 | chore | governance | — | 2 | install.sh |
| 2 | hooks/checks/*.sh → Python 포팅 (5개 언어) | M1 | enhancement | hooks,checks | — | 7 | checks 5개, .gitignore, tests/checks-*.bats |
| 3 | hooks/pre-commit → Python 포팅 | M1 | enhancement | hooks | #2 | 6 | hooks/pre-commit, test.yml |
| 4 | hooks/commit-msg → Python 포팅 | M1 | enhancement | hooks | — | 4 | hooks/commit-msg, test.yml |
| 5 | hooks/post-commit → Python 포팅 | M1 | enhancement | hooks | #3 | 6 | hooks/post-commit, test.yml |
| 6 | CI/문서 마무리: ruff, readme.md, consistency.bats | M1 | chore | ci,docs | #2,#3,#4,#5 | 5 | test.yml, hooks/readme.md, hooks/checks/readme.md, tests/consistency.bats |
| 7 | python3 필요조건 문서화 + 실행시점 PATH 없음 bats | M2 | enhancement | docs,tests | #1,#3,#4,#5 | 4 | README.md, hooks/readme.md, tests/robustness-install.bats, 신규 bats |

**문서 참조(--doc)**: #6 → `backlog/docs/doc-5`(저장소 구조),
#7 → `backlog/docs/doc-6`(주의점과 한계). **참조(--add-ref)**: Phase 0의
새 decision이 생성된 뒤 해당 ID를 #1~#7 전부에 연결한다.

**실행 명령 순서**:
1. `backlog milestone add` × 2 (M1/M2, --description 포함)
2. `backlog draft create` × 7 (title/description/assignee/labels)
3. `backlog draft promote` × 7
4. `backlog task edit` × 7 (--ac ×N, --dod ×5, -m, --type, --depends-on,
   --modified-file, --doc, --ordinal, --priority)
5. `backlog doctor`로 중복/순환 의존성 검증 후 `backlog board view`로 확인

## 대상 파일

- `hooks/pre-commit` (단일 파일, 원본 100줄 기반) / `hooks/commit-msg`
  (단일 파일, 원본 305줄 기반) / `hooks/post-commit` (단일 파일, 원본
  423줄 기반) — 마일스톤 1
- `hooks/checks/{ts,python,sql,java,cpp}.sh` → `.py` — 마일스톤 1
- `hooks/gitformat.conf` (읽기 방식 불변)
- `.gitignore`: `__pycache__/`, `*.pyc` — 마일스톤 1
- 신설: `hooks/readme.md`, `hooks/checks/readme.md` — 마일스톤 1
- `tests/consistency.bats`, `tests/checks-*.bats` 경로 갱신 — 마일스톤 1
- `.github/workflows/test.yml` — 마일스톤 1(shellcheck 목록 정리, ruff
  추가)
- `install.sh` (언어는 POSIX sh 유지, python3 존재 확인 가드 추가) —
  마일스톤 2
- `backlog/decisions/` 새 decision — 마일스톤 2
- 루트 `README.md` (필요조건 섹션) — 마일스톤 2
- `tests/robustness-install.bats`, 신규 런타임 PATH 없음 bats 케이스 —
  마일스톤 2
