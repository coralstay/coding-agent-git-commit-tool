---
id: doc-13
title: git-format 재설계 계획 — 커밋 규칙을 prepare-commit-msg로 통합
type: specification
created_date: '2026-09-25 19:31'
updated_date: '2026-09-25 19:31'
---
# git-format 재설계: 커밋 규칙을 prepare-commit-msg 하나로

## 용어 정리

이 문서에서 쓰는 말의 정의. 특히 "마커"는 이 프로젝트에서 **두 가지 다른 것**을 가리켜
혼동의 원인이 되므로 구분해 쓴다.

| 용어 | 정의 |
| --- | --- |
| **턴** | **한 번의 API 응답.** 트랜스크립트에서는 `(requestId, message.id)` 한 쌍이 한 턴이다. 한 턴 안에 `thinking`(생각)·`text`(말)·`tool_use`(도구 호출) 블록이 여러 개 들어간다. **트랜스크립트는 이를 블록마다 한 줄씩 쪼개 기록하고 각 줄이 동일한 `usage`를 반복해서 들고 있다** — 그래서 "턴"은 줄이 아니라 응답 단위이고, 줄 단위로 토큰을 더하면 중복 계상된다 |
| **트랜스크립트** | Claude Code가 세션마다 남기는 JSONL 로그. 경로는 `~/.claude/projects/<슬러그>/<세션UUID>.jsonl`이고 슬러그는 저장소 절대경로의 영숫자 아닌 문자를 하이픈으로 치환한 것이다. 모델 이름과 토큰 사용량의 출처 |
| **`tool_use` 블록** | 턴 안에서 도구를 한 번 호출한 기록. `name`(도구 이름)과 `input`(인자)을 갖는다. 귀속 판정은 이 `input`을 본다 |
| **`usage`** | 한 턴의 토큰 사용량. `input_tokens`·`output_tokens`·`cache_creation_input_tokens`·`cache_read_input_tokens` 네 필드. **턴 단위로만 존재하며 파일별로 쪼갤 수 없다** |
| **귀속 / 귀속 필터** | 쌓인 턴 중 **이 커밋과 관계있는 턴만 골라내는 것**. 기준은 하나 — 그 턴의 도구 호출이 이 커밋에 스테이징된 파일을 건드렸는가 |
| **`delta`** | 직전 커밋 이후 구간의 토큰 **전체** 합(귀속 필터를 적용하지 않은 값). 귀속된 `in+out`과의 차이가 귀속하지 못한 양이다 |
| **트레일러** | 커밋 메시지 맨 끝에 오는 `Key: value` 줄. git이 `git interpret-trailers`로 다루는 1급 개념이다 |
| **footer** | 메시지 끝의 트레일러 블록 전체 |
| **언어 감지 마커 파일** | 저장소 루트에 있으면 그 언어로 판단하는 파일. `package.json`(TypeScript), `pyproject.toml`·`requirements.txt`(Python), `pom.xml`·`build.gradle*`(Java), `CMakeLists.txt`·`Makefile`(C/C++), `.sqlfluff`·추적된 `*.sql`(SQL). `defaults.conf`의 `[gitformat "marker"]`에 정의된다. **이 설계에서 계속 쓴다** |
| **검증 마커** | 현재 구조에서 `pre-commit`이 통과 후 `$GIT_DIR/.gitformat-verified`에 남기던 파일. `post-commit`이 그 부재로 `--no-verify` 우회를 탐지했다. **이 설계에서 삭제된다** — 우회 자체가 불가능해져 탐지할 대상이 없다 |
| **`source`** | `prepare-commit-msg`의 두 번째 인자(`$2`). `message`(`-m`/`-F`), `template`(에디터), `commit`(`--amend`/`-c`), `merge`, `squash` 중 하나. 실측값은 아래 표에 있다 |
| **재생 커밋** | cherry-pick·rebase·revert가 기존 커밋을 다시 적용해 만드는 커밋. 이미 검증된 커밋의 복제이므로 이 설계에서는 검증·삽입 모두 생략한다 |
| **컨슈머 저장소** | git-format을 설치해 쓰는 다른 저장소. 이 프로젝트의 실제 사용 대상이다 |
| **커밋 단위** | 이 프로젝트가 지향하는 커밋 크기 — 논리적 변경 하나, 실질적으로 함수 하나 수준. 아래 "커밋 단위와 턴의 관계" 참고 |
| **lint** | 언어 감지 마커로 고른 `hooks/lint/<언어>.py`가 실행하는 언어별 검사(포맷·컴파일·정적분석). 도구가 없으면 조용히 건너뛴다 |

### 커밋 단위 규칙과 턴의 관계

**커밋 단위 규칙(정책)**: 커밋 하나 = 논리적 변경 하나 = **함수 하나 수준**. 이 프로젝트가
만드는 모든 저장소가 이 규칙을 따른다. 과거 이력에 비추어 검증할 대상이 아니라 앞으로의
정책이다. 이 규칙의 원형은 이미 `.gitmessage:38`("커밋 하나 = 논리적 변경 하나")에 있고,
이번 설계에서 `.gitmessage`를 삭제하므로 **이 문장을 README로 옮기면서 "함수 하나 수준"으로
구체화한다.**

**턴은 커밋 단위가 아니다.** 커밋 하나를 만들려면 최소 몇 턴이 든다 — 파일을 수정하는 턴,
테스트를 돌리는 턴, 커밋하는 턴. `usage`는 API 응답마다 기록되므로 턴 경계를 커밋 경계에
맞출 방법이 없다. 하나의 커밋에는 **여러 턴이 귀속된다** — 이게 정상 동작이다.

**이 규칙은 측정 정밀도를 직접 올린다.** 커밋이 작으면 직전 커밋과 이 커밋 사이 구간에
무관한 작업이 거의 없어, 귀속된 `in+out`이 `delta`에 가까워진다. 정밀도가 규율에서 나온다.

**TDD와 충돌하지 않는다.** 이 프로젝트에는 `.claude-rails.json`이 없어 테스트 실패 시
커밋을 막는 훅이 걸려 있지 않다. 따라서 "실패하는 테스트 커밋 → 구현 커밋"으로 나눌 수
있고 각 커밋이 파일 하나를 건드린다. 규칙을 지키면서 TDD가 된다.

**설계는 파일 수에 의존하지 않는다.** 귀속 필터는 `git diff --cached --name-only`로 얻은
스테이징 목록으로 동작하므로 파일이 1개든 여러 개든 같게 작동한다 — 전부 스테이징되므로
그중 어느 파일을 건드린 턴이든 귀속된다. 따라서 이 규칙은 설계를 바꾸지 않고 정확도만
올린다. **정밀도를 깎는 것은 파일 수가 아니라 도구를 쓰지 않은 턴이다**(설계·논의 턴.
실측으로 57개 응답 중 3개, 5%).

## Context

git-format은 **다른 저장소에 설치되어 커밋 규칙을 강제하는 도구**다. 지금 구조는 훅 3개
(`pre-commit`/`commit-msg`/`post-commit`)이고, 트레일러를 커밋이 만들어진 **뒤에**
`git commit --amend`로 붙인다. 이 구조를 버리고 새로 설계한다. 과거 커밋이나 기존
설치본과의 하위호환은 설계 제약으로 두지 않는다.

새 설계의 목표 두 가지.

1. **커밋 메시지 포맷을 우회 불가능하게 강제한다.** 현재는 `git commit --no-verify`로
   검사와 검증을 전부 건너뛸 수 있고, 우회를 막는 대신 사후에 `Verify-Bypassed`
   트레일러로 기록만 한다.
2. **에이전트가 쓴 커밋은 반드시 그렇게 기록된다.** 현재 `hooks/post-commit`의
   `trailer_ai_tool()`은 `AI_AGENT` 환경변수 **하나만** 보고, 비어 있으면 AI 관련 트레일러를
   **조용히 전부 생략**한다 — 에이전트 커밋이 사람 커밋과 구별되지 않는다.

## 설계 근거 (git 2.54.0 실측)

`prepare-commit-msg`가 실행되는 경로와 `$2`(source) 값:

| 경로 | prepare-commit-msg | `$2` |
| --- | --- | --- |
| `git commit -m "..."` | 실행 | `message` |
| `git commit` (에디터) | 실행 — **에디터는 그 뒤에 열린다** | `template` |
| **`git commit --no-verify`** | **실행** (`pre-commit`·`commit-msg`만 스킵) | `message` |
| `git commit --amend` | 실행 | `commit` |
| `git revert` / cherry-pick / rebase 재생 | 실행 (`commit-msg`는 안 돈다) | — |
| **`git am`** | **안 돈다** — `applypatch-msg`/`pre-applypatch`/`post-applypatch`만 | — |
| `git commit-tree`, `git stash` | 훅 없음 (plumbing) | — |

세 가지가 설계를 결정한다.

- **`--no-verify`가 이 훅을 건너뛰지 못한다.** 검사·검증·삽입을 전부 여기 넣으면 우회할
  방법이 없다. 우회를 탐지할 필요가 없으므로 검증 마커와 `Verify-Bypassed` 트레일러라는
  개념 자체가 설계에서 빠진다.
- **에디터 경로는 검증이 불가능하다.** `$2=template`일 때 이 훅은 사람이 타이핑하기 전에
  돌아 빈 메시지를 본다(실측: 비주석 내용 줄 0). 그래서 **이 경로는 거부**한다.
- **`git am`은 이 훅을 타지 않는다.** 별도로 `applypatch-msg`에서 거부한다.

## 파일 이름을 전부 "무엇을 하는지" 드러나게 바꾼다

대규모 이관을 하는 김에 이름도 정리한다. 기준: 파일명만 보고 무엇을 검증·수행하는지
알 수 있어야 한다. `robustness-*` 같은 성격 분류나 `ts`/`cpp` 같은 축약을 쓰지 않는다.

**바꿀 수 없는 것**: `hooks/prepare-commit-msg`, `hooks/applypatch-msg` — git이 **파일명으로
훅을 찾는다.** 이 둘만 이름이 고정이고 나머지는 자유다. `backlog/`의 `doc-N`/`decision-N`도
backlog CLI가 관리하므로 임의로 바꾸지 않는다.

### 훅과 설정

| 기존 | 새 이름 | 이유 |
| --- | --- | --- |
| `hooks/pre-commit`, `hooks/commit-msg`, `hooks/post-commit` | (삭제) | `prepare-commit-msg`로 통합 |
| — | `hooks/prepare-commit-msg` | git 고정. lint + 검증 + 트레일러 삽입 |
| — | `hooks/applypatch-msg` | git 고정. `git am` 거부 |
| `hooks/checks/` | `hooks/lint/` | "checks"는 무엇을 하는지 모호하다 |
| `hooks/checks/ts.py` | `hooks/lint/typescript.py` | 축약 해제 |
| `hooks/checks/python.py` | `hooks/lint/python.py` | 그대로(이미 명시적) |
| `hooks/checks/java.py` | `hooks/lint/java.py` | 그대로 |
| `hooks/checks/cpp.py` | `hooks/lint/c_cpp.py` | C와 C++ 둘 다 담당한다(`gitformat.cpp.ext`에 `*.c` 포함) |
| `hooks/checks/sql.py` | `hooks/lint/sql.py` | 그대로 |
| `hooks/gitformat.conf` | `hooks/defaults.conf` | "gitformat"은 프로젝트명 반복이고, 내용은 내부 기본값이다 |
| `hooks/readme.md` | `hooks/README.md` | 대소문자 일관성 |
| `.gitmessage` | (삭제) | `commit.template`을 제거하므로 에디터 템플릿이 쓰이지 않는다. 규칙 문서는 `README.md`와 doc-2가 이미 담당한다 |

`hooks/lint/*.py`는 `subprocess.run([sys.executable, script, REPO_ROOT])`로 **경로 실행**되고
import되지 않으므로 `python.py`라는 이름이 stdlib를 가리는 문제는 없다.

### 결과 구조

```
hooks/prepare-commit-msg    본체. lint + 검증 + 트레일러 삽입
hooks/applypatch-msg        git am 거부
hooks/defaults.conf         내부 기본값 (트레일러 키, 길이 제한, 언어 마커)
hooks/lint/typescript.py
hooks/lint/python.py
hooks/lint/java.py
hooks/lint/c_cpp.py
hooks/lint/sql.py
install.sh                  컨슈머 저장소에 core.hooksPath 설정
```

`prepare-commit-msg`의 실행 순서. 인자는 `$1`=메시지 파일, `$2`=source, `$3`=ref.

```
0. 면제 판정    재생·병합 커밋이면 즉시 종료
1. 경로 게이트  source=template(에디터)이면 거부
2. lint         언어 감지 → checks/<lang>.py, 실패 시 exit 1
3. 메시지 검증  형식 / 제목 50자 / 본문 72자 / 빈 줄 / Fixes 해시 / Task-Id 브랜치
4. 트레일러 삽입 interpret-trailers --in-place, 키가 이미 있으면 생략
```

**0. 면제 판정** — `$GIT_DIR`에 `MERGE_HEAD`/`CHERRY_PICK_HEAD`/`REBASE_HEAD`/`REVERT_HEAD`
중 하나라도 있거나 `$2`가 `merge`/`squash`면 그대로 종료한다. 재생 커밋은 이미 검증된
커밋의 복제이므로 다시 도장을 찍는 것도, 토큰을 다시 계산하는 것도 틀렸다. (현재
`post-commit`은 이 경로에서 amend를 시도해 트레이스백을 낸다 — DRAFT-18.)

**1. 경로 게이트** — `$2`가 `template`이면 "이 저장소는 `git commit -m`으로 커밋해야
합니다"로 거부한다. 이렇게 하면 **통과한 모든 커밋이 검증을 거친 것**이 된다.
`install.sh`의 `commit.template` 설정은 에디터에 뜨는 안내가 목적이므로 **함께 제거한다**
(아래 참고).

**2. lint** — 저장소 루트의 마커 파일로 언어를 감지해 `checks/<lang>.py`를 실행한다.
현재 `pre-commit`의 로직을 그대로 옮긴다. 스테이징 파일은 `git diff --cached --name-only`로
얻는다(3·4단계에서도 쓴다).

**3. 메시지 검증** — 현재 `commit-msg`의 검증 함수들을 옮긴다. 트레일러 삽입보다 **먼저**
돈다(사람이 쓴 부분만 검증하고, 훅이 만든 트레일러는 검증 대상이 아니다).

**4. 트레일러 삽입** — 메시지 파일에 `git interpret-trailers --in-place`로 쓴다. 중복
판정은 메시지 원문을 줄 단위로 읽어 `^<키>: `로 시작하는 줄이 있으면 그 키를 건너뛴다.
`interpret-trailers --parse`는 쓰지 않는다 — 이 명령은 메시지 **맨 끝의 연속된 트레일러
블록만** 인식해서 빈 줄로 분리된 앞 문단의 트레일러를 못 보고, 그게 현재 구조에서
`Task-Id`/`Co-Authored-By`가 두 줄씩 붙는 원인이다. 콜론+공백까지 비교하므로 접두어
오매치(`AI-Tool` vs `AI-Tool-Version`)도 없다. 기준은 "**키가 있으면 생략**" — 사람이 쓴
값을 훅이 덮어쓰지 않는다.

`--amend`를 쓰지 않으므로 재귀 가드가 필요 없고, 커밋이 처음부터 최종 메시지로 만들어져
이력 재작성이 없다.

## 커밋 메시지 포맷

```
[fix][parser] 빈 입력 처리

빈 입력에서 인덱스 접근이 터졌다. 경계 검사를 추가한다.

Task-Id: GF-42
AI-Agent: claude-code/2.1.267 (claude-opus-5)
Co-Authored-By: Claude <noreply@anthropic.com>
Tokens-Used: in=240000 out=5400 delta=749400
Tool-Calls: 2
Hooks-Commit: b5bf03a
```

제목·본문 규칙: `[type][subsystem] <설명>`, 제목 50자(유니코드 코드포인트), 본문 줄 72자,
제목-본문 사이 빈 줄, `Fixes:` 해시 실재 검증, 브랜치명 `<prefix>-<번호>`.

| 트레일러 | 값 | 붙는 조건 |
| --- | --- | --- |
| `Task-Id` | 브랜치명의 `<prefix>-<번호>` | 브랜치명에 패턴이 있을 때 |
| `AI-Agent` | `<도구>/<버전> (<모델>)` | 검증된 에이전트 신호가 있으면 항상 |
| `Co-Authored-By` | `Claude <noreply@anthropic.com>` | 도구가 `claude-code`일 때 |
| `Tokens-Used` | `in=<입력> out=<출력> delta=<구간 전체>` | 에이전트 커밋일 때 |
| `Tool-Calls` | 스테이징 파일을 건드린 `tool_use` 블록 수 | 에이전트 커밋일 때 |
| `Hooks-Commit` | 훅 클론의 `rev-parse --short HEAD` | 항상 |

`AI-Agent`는 도구·버전·모델을 한 줄로 합친다. 구성요소가 없으면 축약하되 **줄 자체는
반드시 남긴다** — 버전을 못 구하면 `claude-code/version-unavailable (claude-opus-5)`,
모델을 못 구하면 `claude-code/2.1.267 (model-unavailable)`. 조용한 생략이 곧 잘못된
귀속이기 때문이다.

설계에서 빠지는 트레일러: `Verify-Bypassed`(우회가 불가능해져 탐지 대상이 없다),
`Signed-off-by`(커미터 정보는 커밋 객체에 이미 있다), `AI-Tool`/`AI-Tool-Version`/
`AI-Model`(`AI-Agent`로 병합).

## 토큰·툴콜 — 해당 커밋에 쓴 것만 센다

### 응답 단위 중복 제거 (필수)

턴의 정의는 위 용어 정리 참고. 실측 근거: 한 응답이 `apiBlockIndex` 0~3의 4줄
(`thinking`/`text`/`tool_use`/`tool_use`)로 쪼개지고 **네 줄 모두 usage 합이 87,932**이다.
이 세션 전체로는 assistant 줄 146개에 고유 응답 57개 — 줄 단위로 더하면 26,102,818,
응답 단위로 세면 9,964,308(2.62배 차이).

집계 알고리즘은 반드시 이 순서다.

1. assistant 줄을 `(requestId, message.id)`로 **그룹핑**한다
2. 그룹의 usage는 **한 번만** 센다(첫 줄의 값을 쓴다 — 나머지는 같은 값의 반복이다)
3. 그룹의 `tool_use` 블록은 **모든 줄에서 모은다**(한 응답의 도구 호출이 여러 줄에 흩어져
   있다). 이 목록으로 귀속 여부를 판정한다

### 귀속 필터

트랜스크립트에 쌓인 턴 중 **이 커밋과 관계있는 턴만 골라내는 체**다. 기준은 하나 —
그 턴의 도구 호출이 이 커밋에 스테이징된 파일을 건드렸는가.

예시. 스테이징 파일이 `hooks/prepare-commit-msg` 하나이고 다섯 턴이 쌓인 경우:

| 턴 | 도구 호출의 `input` | in | out | 필터 |
| --- | --- | --- | --- | --- |
| 1 | `Grep {pattern:"trailer"}` | 120,000 | 800 | 탈락 — 경로가 없다 |
| 2 | `Read {file_path:"hooks/post-commit"}` | 200,000 | 1,200 | 탈락 — 스테이징 안 된 파일 |
| 3 | `Write {file_path:"hooks/prepare-commit-msg"}` | 210,000 | 5,000 | **통과** — 완전 일치 |
| 4 | `Bash {command:"ruff check hooks/prepare-commit-msg"}` | 30,000 | 400 | **통과** — 명령에 경로가 있다 |
| 5 | 설계 논의 (도구 호출 0개) | 180,000 | 2,000 | 탈락 — 매칭할 입력이 없다 |

결과: `Tokens-Used: in=240000 out=5400 delta=749400`, `Tool-Calls: 2`.
차이 504,000이 귀속하지 못한 양이다.

판정 규칙 — **정확한 경로 비교만** 쓴다:

- `file_path`/`notebook_path` 필드를 가진 도구(Read/Edit/Write 등) → 저장소 상대경로로
  정규화해 **완전 일치**. 오귀속이 원리적으로 불가능하다.
- Bash `command` → 명령 문자열에 저장소 상대경로가 들어 있는지만 본다. 파일명이나
  파일명 앞토큰으로는 매칭하지 않는다(`README.md` 같은 흔한 이름, `a.txt` → `a` 같은
  짧은 토큰이 무관한 턴을 끌어오는 것을 막는다).

대상 경로는 `git diff --cached --name-only`로 얻는다 — 이 훅은 커밋 전에 돌기 때문에
스테이징 목록이 정확히 이 커밋의 내용이다.

조사 결과 트랜스크립트에서 쓸 수 있는 재료는 `tool_use`의 `input`뿐이다.
`file-history-snapshot`의 `trackedFileBackups`가 파일 편집을 정확히 기록하는 구조처럼
보였으나 **실측 결과 전부 비어 있다**(이 세션 3건, 파일을 많이 고친 다른 세션 28건 모두).

### 기록 형식

`Tokens-Used: in=<N> out=<N> delta=<N>` — 한 줄에 세 값을 묶는다.

| 값 | 정의 |
| --- | --- |
| `in` | 귀속된 턴의 입력측 합 = `input_tokens` + `cache_creation_input_tokens` + `cache_read_input_tokens` |
| `out` | 귀속된 턴의 `output_tokens` 합 |
| `delta` | 직전 커밋 이후 구간 **전체** 합(귀속 필터 없음). `in+out`과의 차이가 곧 귀속되지 못한 양 |

`delta`를 함께 남기는 이유: 귀속 필터는 정밀도를 위해 재현율을 버리므로 반드시 과소
보고된다. 문서에만 적어두면 로그를 읽는 쪽이 알 수 없다. 두 값을 나란히 쓰면 **커밋
자체가 측정의 정밀도를 드러낸다.** 캐시 토큰은 `in`에 합쳤다(실측 비율 in 9,821,179 /
out 143,129 — 거의 전부가 입력측이다). 분리가 필요하면 `cache=`를 덧붙이면 된다.

`usage`는 응답 단위로만 존재해 파일별로 쪼갤 수 없으므로 `in`/`out`의 최소 단위는 턴이다.
`Tool-Calls`는 대상 경로를 실제로 건드린 `tool_use` **블록 개수**로 더 좁게 센다.

### 측정 실패를 0으로 위장하지 않는다

| 상황 | 기록 |
| --- | --- |
| 정상 | `Tokens-Used: in=240000 out=5400 delta=749400` |
| 구간에 턴이 아예 없음(진짜 0) | `Tokens-Used: in=0 out=0 delta=0` |
| 턴은 있으나 귀속된 게 없음 | `Tokens-Used: in=0 out=0 delta=749400 (no-attributed-turn)` |
| 트랜스크립트를 못 읽음 | `Tokens-Used: unavailable (transcript-not-found)` 등 사유 슬러그 |

세 번째 행이 핵심이다 — `delta`가 살아 있으므로 "토큰을 안 썼다"와 "귀속에 실패했다"가
footer만 봐도 구별된다.

### 한계

- **서브에이전트 토큰은 부모 트랜스크립트에 없다.** 실측으로 이 세션 assistant 줄의
  `isSidechain`이 전부 `false`이고 sidechain 토큰 합이 0이다. 위임한 작업의 비용은 어떤
  방식으로도 이 지표에 잡히지 않는다.
- 파일명을 말하지 않는 도구 호출(`bats tests/`)과 도구를 안 쓴 턴(설계·논의)은 빠진다.
  다만 재현율 손실은 걱정보다 작다 — 실측으로 57개 응답 중 도구를 아예 쓰지 않은 것은
  **3개(5%)**뿐이다(줄 단위로 세면 57%로 보이지만 쪼개짐 때문에 생긴 착시다).

## 에이전트 판정 — 검증 가능한 신호만 쓴다

실측으로 확인한 이 세션의 신호와 각각의 역할:

| 환경변수 | 실제 값 | 역할 | 판정에 쓰나 |
| --- | --- | --- | --- |
| `CLAUDE_CODE_SESSION_ID` | UUID | 트랜스크립트 경로 `~/.claude/projects/<슬러그>/<UUID>.jsonl`를 만든다 → 모델·토큰 값의 출처 | **예 — 파일 실재로 확인** |
| `CLAUDE_PID` | `57115` | Claude Code 프로세스 PID | **예 — `ps -p`로 프로세스 실재·이름 확인** |
| `AI_AGENT` | `claude-code_2-1-267_agent` | 도구_버전_역할. `AI-Agent`의 도구·버전 **값 출처**. 주입값이라 자가신고 아님 | 값으로만 — 존재 여부는 검증 불가 |
| `CLAUDE_CODE_EXECPATH` | `…/claude-code/2.1.267/claude` | 경로에 버전이 들어 있다 | 보조(버전 보강) |
| `CLAUDE_CODE_CHILD_SESSION` | `1` | 하위 세션(서브에이전트) 표시 | 보조 |
| `CLAUDECODE` | `1` | 단순 플래그 | 아니오 — 위조·누락이 쉽고 검증 불가 |
| `CLAUDE_CODE_ENTRYPOINT` | `cli` | 실행 경로(cli/vscode) | 아니오 — 진단용 |
| `CLAUDE_EFFORT` | `high` | 추론 강도 | 아니오 |
| `CLAUDE_CODE_MESSAGING_SOCKET` / `_TOKEN` | (생략) | IPC 소켓과 **인증 토큰** | 아니오 — **비밀값. 커밋에 절대 남기지 않는다** |

판정 규칙: `CLAUDE_CODE_SESSION_ID`가 **실재하는 트랜스크립트 파일**을 가리키거나
`CLAUDE_PID`가 **살아 있는 `claude` 프로세스**를 가리키면 에이전트 커밋이다. 이 둘만이
파일시스템·프로세스 테이블과 대조해 확인되는 신호다. 나머지는 "있다/없다"뿐이라 판정
근거로 쓰지 않는다 — `CLAUDECODE=1` 하나로 판정하면 위조와 누락에 모두 취약하다.

모델은 세션 트랜스크립트의 `message.model`(API 응답 기록값)에서 읽는다. 세션 ID 자체는
트랜스크립트를 찾는 데만 쓰고 커밋에는 남기지 않는다.

## 컨슈머 저장소에서 동작하기 위한 제약 (코드 실독)

`install.sh`와 `hooks/pre-commit`을 읽고 확인한, 새 훅이 반드시 지켜야 할 것들.

1. **훅 위치는 `os.path.realpath(__file__)`로 해석한다.** `install.sh --global`은
   `init.templateDir`로 새 저장소의 `.git/hooks/`에 클론을 가리키는 **심볼릭 링크**를
   심는다(`sync_template`). 링크가 놓인 `.git/hooks/`가 아니라 링크가 가리키는 클론에서
   `checks/`와 `gitformat.conf`를 찾아야 한다(GF-16).
2. **`os.chdir(REPO_ROOT)`가 필요하다.** 언어 마커 파일을 저장소 루트에서 찾기 때문이다
   (`pre-commit:96`).
3. **`gitformat.conf` 읽기 가드를 유지한다.** 파일을 못 읽으면 이후 `git config --file`
   읽기가 하나씩 실패해 원인을 알 수 없는 거부가 된다(GF-76). 이 블록은 conf를 읽는
   모든 파일에 byte-identical하게 있다.
4. **`install.sh`는 `hooks/*`를 글롭하고 사라진 훅의 링크를 정리한다.** 훅 파일을 추가·
   삭제해도 설치 스크립트 수정이 필요 없다.
5. **컨슈머 저장소는 Claude Code 프로젝트가 아닐 수 있다.** 그 경우 `SESSION_ID`·`PID`가
   없어 `AI-Agent`/`Tokens-Used`/`Tool-Calls`가 붙지 않는다 — 의도된 동작이다.

## 알려진 한계

| 한계 | 성격 |
| --- | --- |
| `git commit-tree` / `git stash` 등 plumbing은 훅이 없다 | 모든 git 훅의 공통 한계. 훅은 보안 경계가 아니다 |
| `core.hooksPath`를 바꾸거나 훅 파일을 지우면 무력 | 위와 동일 |
| 사람도 `-m`으로만 커밋할 수 있다 | 의도된 설계. 그래서 `commit.template`을 함께 제거한다 |
| 서브에이전트 토큰 미집계 | 위 토큰 절 참고 |

## 영향 받는 파일

- **신설** `hooks/prepare-commit-msg` — 위 4단계 전부
- **신설** `hooks/applypatch-msg` — `git am` 거부. 설정값을 쓰지 않으므로 conf 읽기 가드도 불필요
- **삭제** `hooks/pre-commit`, `hooks/commit-msg`, `hooks/post-commit`
- **유지** `hooks/checks/*.py`
- `hooks/gitformat.conf`: `[gitformat "trailer"]`에서 `aiTool`/`aiToolVersion`/`aiModel`
  삭제 → `aiAgent = AI-Agent` 추가. `verifyBypassed`·`signedOffBy` 삭제. `markerFile` 삭제.
  주의 — `[gitformat]` 최상위의 `coAuthoredBy`는 삽입할 **값**이고
  `[gitformat "trailer"].coAuthoredBy`는 트레일러 **키 이름**이다(이름이 겹쳐 혼동하기 쉽다).
  컨슈머 오버라이드 `gitformat.aiModel`은 모델 **값**의 출처이므로 유지한다.
- `install.sh`: `commit.template` 설정 2곳(로컬 57행, 전역 90·104행)과 관련 출력 제거.
  에디터 경로를 거부하므로 템플릿이 쓰이지 않는다
- `.gitmessage`: 에디터 템플릿에서 **사람이 읽는 규칙 문서**로 역할이 바뀐다. `Signed-off-by`
  안내 삭제, `AI-Agent` 반영. 파일을 남길지 README로 흡수할지 결정한다
- `README.md`: 훅 생애주기, 트레일러 표, 예시 커밋, 설치 안내(`commit.template` 제거),
  python3 누락 시 실패 양상(이제 트레일러가 조용히 누락되는 게 아니라 커밋이 막힌다)
- `hooks/readme.md`: 훅 2개 구조로 전면 수정
- `backlog/docs/`: doc-1(설치), doc-2(커밋 규칙), doc-3(트레일러 표), doc-6(한계),
  doc-7(워크스루) — **`backlog` CLI로 편집한다**(마크다운 직접 편집 금지)
- `.github/workflows/test.yml`: bats 설치·실행 스텝을 `unittest`로 교체(위 테스트 절 참고)
- **decision**: 새 구조를 기록하는 decision을 만들고, 테스트 프레임워크 전환(bats → stdlib
  `unittest`)도 decision-16의 연장으로 함께 기록한다. 대체되는 기존 decision(우회 탐지,
  `Signed-off-by`, AI 트레일러 표)의 파일 본문에 대체 사실을 적는다. `backlog decision`에는
  상태 변경 명령이 없어 본문으로만 추적된다

## 테스트를 bats에서 Python unittest로 이관한다

현재 `tests/`는 bats 1,880줄 / 17파일이고, CI는 **bats-core를 GitHub에서 clone해 설치하는
스텝**을 따로 둔다. 훅은 "설치할 것 없음"인데 테스트만 외부 도구를 요구하는 비대칭이다.
새 설계가 어차피 테스트 전면 개편을 요구하므로 지금 함께 바꾼다.

프레임워크는 **표준 라이브러리 `unittest`**. `pytest`가 편하지만 설치가 필요해
decision-16의 "stdlib만, 설치할 것 없음" 원칙과 어긋난다.

바꾸는 이유(새 설계에서 특히 큰 둘이 앞의 둘):

1. **가짜 트랜스크립트 픅스처가 감당 가능해진다.** 새 픅스처는 `requestId`/`message.id`로
   그룹핑되고 `content`에 `thinking`/`text`/`tool_use` 블록이 여러 개, `tool_use`에
   `input.file_path`까지 필요하다. 셸에서 `printf '%s\n' '{...}'`로 쓰면 따옴표 지옥이다.
   Python이면 dict → `json.dumps`.
2. **중복을 구조적으로 검사할 수 있다.** 지금은 `[[ "$MSG" == *"Task-Id: GF-1"* ]]` 부분
   일치라 "한 번만 나오는지"를 확인하기 번거롭고, 그게 중복 버그를 고정하는 테스트가
   없는 이유 중 하나다. Python이면 `msg.count("Task-Id:") == 1`.
3. CI에서 외부 저장소 clone 의존이 사라진다 — `python3 -m unittest`는 러너에 이미 있다.
4. 훅(Python)과 테스트(Python)로 언어가 통일되고 `install.sh`만 POSIX sh로 남는다.
5. ruff 검사 대상에 테스트도 들어와 린트가 일관된다.

이관 매핑:

테스트 파일명도 **무엇을 검증하는지**로 바꾼다 — `robustness-*` 같은 성격 분류를 쓰지 않는다.

| 기존 bats | 새 Python | 검증 내용 |
| --- | --- | --- |
| `helpers/git-format.bash` | `tests/isolated_repo.py` | 임시 git 저장소 + 훅 설치 + `env` 조작 헬퍼 |
| `robustness-commit-msg.bats` | `test_message_format_enforced.py` | 형식·제목 50자·본문 72자·빈 줄·`Fixes` 해시 |
| `robustness-commit-msg.bats` | `test_branch_task_id_required.py` | 브랜치명 `<prefix>-<번호>` 강제와 예외 브랜치 |
| — (신규) | `test_editor_commit_rejected.py` | `-m` 없는 커밋이 거부된다 |
| — (신규) | `test_no_verify_cannot_bypass.py` | `--no-verify`로도 lint·검증을 못 건너뛴다 |
| — (신규) | `test_git_am_rejected.py` | `git am`이 거부된다 |
| — (신규) | `test_trailers_never_duplicated.py` | 메시지에 같은 키가 있으면 훅이 추가하지 않는다 |
| `robustness-post-commit.bats` | `test_trailer_task_id.py` | 브랜치명에서 뽑은 `Task-Id` |
| `robustness-post-commit.bats` | `test_trailer_ai_agent.py` | `AI-Agent` 값 조립과 축약(`version-unavailable` 등) |
| `robustness-post-commit.bats` | `test_trailer_hooks_commit.py` | 훅 클론 HEAD 해시 |
| `robustness-post-commit.bats` | `test_token_usage_attribution.py` | 응답 중복 제거 + 귀속 필터 + `in`/`out`/`delta` |
| — (신규) | `test_agent_detection.py` | `SESSION_ID`/`PID` 판정, `CLAUDECODE`만으론 판정 안 함 |
| — (신규) | `test_replay_commits_untouched.py` | cherry-pick·revert·rebase·merge에서 삽입 생략 |
| — (신규) | `test_secrets_never_in_message.py` | `MESSAGING_TOKEN` 등 비밀값 누출 없음 |
| `marker-semantics.bats` | `test_language_detection.py` | 저장소 루트 마커로 언어 감지(리터럴 vs 글롭 의미론) |
| `checks-ts.bats` | `test_lint_typescript.py` | TypeScript 검사 동작·도구 부재 시 건너뛰기 |
| `checks-python.bats` | `test_lint_python.py` | 동일(Python) |
| `checks-java.bats` | `test_lint_java.py` | 동일(Java) |
| `checks-cpp.bats` | `test_lint_c_cpp.py` | 동일(C/C++) |
| `checks-sql.bats` | `test_lint_sql.py` | 동일(SQL) |
| `robustness-dispatch.bats` | `test_lint_dispatch.py` | 마커 조합에 따라 어느 검사가 도는지 |
| `robustness-install.bats` | `test_install_script.py` | `install.sh`의 설정·심볼릭 링크·정리 동작 |
| — (신규) | `test_hook_resolves_through_symlink.py` | `templateDir` 링크 설치에서도 `lint/`·`defaults.conf`를 찾는다(GF-16) |
| `conf-guard.bats` | `test_config_file_unreadable.py` | `defaults.conf`를 못 읽으면 명확한 에러로 멈춘다(GF-76) |
| `consistency.bats` | `test_config_keys_match_hooks.py` | conf의 트레일러 섹션을 **동적으로 읽어** 훅이 참조하는 키와 대조 — 손으로 나열한 목록의 드리프트를 없앤다 |
| `robustness-python-path.bats` | `test_python3_missing.py` | 자식 `env`에서만 python3 제거 → 커밋이 막힌다. 러너는 자기 python3로 계속 돈다 |
| `robustness-locale.bats` | `test_non_utf8_locale.py` | `LC_ALL=C`에서도 훅이 죽지 않는다 |
| `robustness-injection.bats` | `test_shell_metacharacters_safe.py` | 셸 메타문자·비UTF8·아주 긴 줄이 삽입을 깨지 않는다 |
| `smoke.bats` | `test_end_to_end_commit.py` | 설치 → 커밋 → footer 확인 |

`.github/workflows/test.yml` 변경:

- `bats` job의 bats-core clone·설치 스텝 **삭제**, `bats tests/` → `python3 -m unittest discover -s tests`
- 언어별 실도구 설치(`sqlfluff`/`ruff`) 스텝은 **유지** — GF-22가 실도구 부재로 테스트가
  조용히 통과한 사고를 고정한 것이다
- `shellcheck -s sh install.sh` 게이트 **유지** — `install.sh`는 여전히 POSIX sh다
- ruff 대상에 `tests/`를 추가한다. 확장자가 `.py`이므로 셔뱅 탐색 없이 디렉터리 지정으로 잡힌다

아래 테스트 목록은 프레임워크와 무관한 시나리오 명세다. 값 검사는 여전히
`git log -1 --pretty=%B` 결과를 보되, 문자열 부분 일치 대신 트레일러를 파싱해 개수까지
확인한다.

1. `--no-verify`로도 lint 실패 커밋이 **막힌다** (1번 목표의 회귀 테스트)
2. 에디터 경로(`$2=template`)가 거부된다 — `GIT_EDITOR`를 스크립트로 대체해 재현.
   현재 스위트는 전부 `-m` 경로만 쓴다
3. `git am`으로 패치를 적용하면 거부된다
4. 메시지에 빈 줄로 분리된 `Task-Id: GF-N` 문단이 먼저 있는 커밋 → `Task-Id` 한 줄만
5. 메시지에 `Co-Authored-By: <다른 값>`이 있는 커밋 → 한 줄만, 원래 값 보존
6. cherry-pick / `git revert`로 만든 커밋 → 트레일러 추가 없음, 훅도 실패하지 않음
7. `--amend` → 트레일러가 늘어나지 않는다
8. **중복 제거**: 한 응답이 같은 `requestId`/`message.id`로 4줄(`thinking`/`text`/
   `tool_use`/`tool_use`)로 쪼개져 각 줄에 동일 usage가 있는 트랜스크립트 → usage가
   **한 번만** 계상되고 두 `tool_use`는 **둘 다** 귀속 판정에 쓰인다
9. **귀속 필터**: 턴1이 스테이징된 `a.txt`, 턴2가 무관한 `other.txt`를 건드린 트랜스크립트로
   `a.txt`만 커밋 → `in`/`out`은 턴1만, `delta`는 두 턴 합. `in+out < delta`를 고정
10. 턴은 있으나 귀속 실패 → `in=0 out=0 delta=<N> (no-attributed-turn)`, 진짜 0(`delta=0`)과 구별
11. `in`에 `cache_read_input_tokens`가 포함된다
12. `AI_AGENT`를 지우고 `SESSION_ID`(+실재 트랜스크립트)만 남긴 커밋 → `AI-Agent` 줄이
    여전히 남고, 버전은 `EXECPATH`로 보강하거나 `version-unavailable`로 남는다
13. `CLAUDECODE=1`만 있고 `SESSION_ID`·`PID`가 없으면 에이전트로 판정하지 않는다
14. `CLAUDE_PID`가 존재하지 않는 PID를 가리키면 그 신호는 무시된다
15. 모델 조회 실패 → `AI-Agent: claude-code/2.1.267 (model-unavailable)`
16. `CLAUDE_CODE_MESSAGING_TOKEN` 등 비밀값이 커밋 메시지에 나타나지 않는다
17. 심볼릭 링크로 설치된 저장소(`init.templateDir` 경로)에서도 `checks/`와
    `gitformat.conf`를 찾는다 (GF-16 회귀)
18. `gitformat.conf`를 못 읽으면 명확한 에러로 즉시 멈춘다 (GF-76 회귀)

## backlog에 남길 것 — 해야 할 일 / 문서로 구분

plan mode를 벗어난 뒤 `backlog` CLI로 아래를 만든다. 워크플로에 따라 **draft로 먼저 만들고,
유저가 확인한 뒤 promote**한다. `draft create`는 `--ac`를 받지 않으므로 AC는 promote 후
`backlog task edit <ID> --ac ...`로 넣고, 관련 decision·doc을 `--add-ref`/`--doc`으로 연결한다.

### A. 해야 할 일 (draft → task)

의존 순서대로. 1~5는 `hooks/prepare-commit-msg` 한 파일을 단계적으로 채우므로 순서를 지킨다.

| # | 제목 | 범위 |
| --- | --- | --- |
| 1 | `hooks/prepare-commit-msg` 신설 — 면제 판정과 `-m` 강제 게이트 | 재생·병합 커밋 조기 종료, `source=template` 거부, 훅 위치 `realpath` 해석, `defaults.conf` 읽기 가드 |
| 2 | lint 실행을 `prepare-commit-msg`로 이전 | 언어 감지 마커 → `hooks/lint/<언어>.py` 호출, `chdir(REPO_ROOT)` |
| 3 | 메시지 검증을 `prepare-commit-msg`로 이전 | 형식·제목 50자·본문 72자·빈 줄·`Fixes` 해시·브랜치 `<prefix>-<번호>` |
| 4 | 트레일러 삽입을 `prepare-commit-msg`로 이전 + 키 단위 중복 차단 | `interpret-trailers --in-place`, `^<키>: ` 존재 시 생략, `AI-Agent` 병합, `Signed-off-by`·`Verify-Bypassed` 제거 |
| 5 | 토큰·툴콜 측정 재작성 | 응답 단위 중복 제거, 귀속 필터, `in`/`out`/`delta`, 실패 슬러그 |
| 6 | 에이전트 판정을 검증 가능한 신호로 재작성 | `SESSION_ID`(파일 실재)·`PID`(프로세스 실재), 구성요소 누락 시에도 줄을 남긴다 |
| 7 | `hooks/applypatch-msg` 신설 — `git am` 차단 | 몇 줄. 설정값을 쓰지 않음 |
| 8 | 구 훅 3개 삭제 + `defaults.conf` 정리 + `install.sh`에서 `commit.template` 제거 + `.gitmessage` 삭제 | 1~7이 끝난 뒤. 트레일러 키 정리, 검증 마커 관련 설정 삭제 |
| 9 | 파일·디렉터리 개칭 | `checks/` → `lint/`, `ts.py` → `typescript.py`, `cpp.py` → `c_cpp.py`, `gitformat.conf` → `defaults.conf`, `hooks/readme.md` → `hooks/README.md` |
| 10 | 테스트를 bats에서 Python `unittest`로 이관 | 27개 파일 개칭·재구성, `tests/isolated_repo.py` 헬퍼, CI에서 bats 설치 제거, ruff 대상에 `tests/` 추가 |
| 11 | README·`hooks/README.md` 재작성 | 훅 생애주기, 트레일러 표, 설치 안내, 커밋 단위 규칙(`.gitmessage`에서 이전) |

의존: 2~6은 1에 의존, 8은 1~7에 의존, 10은 1~9에 의존. 9는 1~8과 병행 불가(같은 파일을
건드림)이므로 8 다음에 둔다.

### B. 문서로 남길 것

**새 decision** (`backlog decision create`)

| 제목 | 내용과 대체 관계 |
| --- | --- |
| 커밋 규칙 강제를 `prepare-commit-msg` 하나로 통합하고 `--no-verify` 우회를 차단한다 | 실측 근거표 포함. 기존 "우회 탐지" decision(검증 마커 + `Verify-Bypassed`)을 대체한다 — 그 파일 본문에 대체 사실을 적는다 |
| 커밋 footer 트레일러 집합 재정의 | `AI-Agent` 병합, `Signed-off-by` 제거, `Tokens-Used`를 `in`/`out`/`delta`로. 기존 AI 귀속 decision과 `Signed-off-by` 조항을 대체 |
| 에이전트 판정은 검증 가능한 신호만 쓴다 | `SESSION_ID`·`PID`만 판정에 사용, 플래그성 변수 배제, 비밀값 취급 |
| 테스트 프레임워크를 bats에서 표준 `unittest`로 전환한다 | "stdlib만, 설치할 것 없음" 원칙(기존 Python 전환 decision)의 연장 |
| 커밋 단위는 논리적 변경 하나 = 함수 하나 수준 | 정책. 이 프로젝트가 만드는 모든 저장소에 적용 |

**새 doc** (`backlog doc create`)

| 제목 | 내용 |
| --- | --- |
| 용어 정리 | 턴·트랜스크립트·`usage`·`tool_use` 블록·귀속/귀속 필터·`delta`·트레일러·footer·**언어 감지 마커와 검증 마커의 구분**·`source`·재생 커밋·컨슈머 저장소·커밋 단위. 이 계획 최상단 표를 그대로 옮긴다 |
| 훅 실행 경로 실측 (git 2.54.0) | 경로별 훅 실행 여부와 `source` 값, **재현 절차**(빈 저장소에 로그 찍는 훅을 심어 확인). 설계의 근거이므로 재현 가능해야 한다 |
| 토큰·툴콜 측정 방법과 한계 | 응답 단위 중복 제거(왜 줄 단위로 더하면 안 되는지, `apiBlockIndex` 실측), 귀속 필터 워크스루 예시, `in`/`out`/`delta` 정의, 실패 슬러그 표, 서브에이전트 미집계와 `file-history-snapshot`이 빈 사실 |
| 에이전트 판정 신호 레퍼런스 | 환경변수별 값·역할·검증 가능성 표, 비밀값(`MESSAGING_TOKEN`) 취급 주의 |

**갱신할 기존 doc**: doc-1(설치 — `commit.template` 제거, 훅 2개), doc-2(커밋 규칙 —
`Signed-off-by` 삭제, `-m` 강제), doc-3(트레일러 표 — `AI-Agent`로 통합), doc-6(한계 —
서브에이전트 미집계·plumbing·`git am` 차단), doc-7(워크스루 — 새 footer로).

### 실행 순서 (확정)

1. **draft 11개를 먼저 만든다.** `backlog draft create` + `backlog draft edit`로 카드의 모든
   항목을 채운다 — `--description`, `--ac`, `--dod`, `--type`, `--priority`, `--label`,
   `--modified-file`
2. decision 5개(`backlog decision create`)와 doc 4개(`backlog doc create` + `doc update
   --content`)를 만든다
3. 각 draft에 `draft edit --add-ref <decision>` · `--doc <경로>`를 붙인다 (2단계 산출물이
   생긴 뒤여야 경로를 정확히 쓸 수 있다)
4. 유저 확인 → `backlog draft promote <ID>` → promote 후 `task edit --dep`으로 의존 연결
   (의존은 task ID를 요구하므로 draft 단계에서는 설정하지 않는다)
5. 기존 doc 갱신(doc-1·2·3·6·7)은 해당 태스크 안에서 코드와 함께 처리한다 — 문서와 코드가
   갈라지지 않게

`decision`에는 `update` 서브커맨드가 없다(`create`/`list`만). 본문은 생성 후 파일에 직접
써야 하는 유일한 예외다 — 프론트매터는 CLI가 만든 것을 건드리지 않고 본문 섹션만 채운다.

## 검증

1. `python3 -m unittest discover -s tests` 전체 통과, `ruff check hooks/ tests/`,
   `shellcheck -s sh install.sh` — CI(`.github/workflows/test.yml`)와 동일
2. **이 저장소 자신이 같은 훅으로 커밋하므로 훅이 깨지면 즉시 자기 커밋이 막힌다** —
   커밋 자체가 통합 테스트다. 커밋 후 `git log -1 --format=%B`로 footer를 눈으로 확인
3. `git config --get core.hooksPath` 확인 — 이 값이 스테일 tmp 디렉터리로 덮어써지는
   사고가 반복됐다. 어긋나면 `./install.sh --no-global .`을 다시 돌린 뒤 신뢰한다
4. **빈 저장소에 설치해 컨슈머 관점으로 확인한다** — `git init`한 임시 저장소에
   `install.sh`를 돌리고, `-m` 커밋 → footer 6줄 / 에디터 커밋 → 거부 /
   `--no-verify` + lint 실패 → 막힘 / `git am` → 거부 / `git rebase` 재생 → 추가 없음,
   트레이스백 없음
