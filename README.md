<div align="center">

# 🤖 coding-agent-git-commit-tool

**코딩 에이전트의 git 커밋을 검사하고, 누가·어떤 모델로·무슨 태스크로·얼마를 들여 만들었는지 커밋에 자동으로 기록하는 git 훅**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
[![Hooks: Python 3](https://img.shields.io/badge/hooks-Python%203-3776ab.svg)](./hooks/)
[![Installer: POSIX sh](https://img.shields.io/badge/installer-POSIX%20sh-89e051.svg)](./install.sh)
[![Requires: git + python3](https://img.shields.io/badge/requires-git%20%2B%20python3-brightgreen.svg)](#-필요조건을-말씀드립니다)

커밋할 때마다 두 가지를 합니다. 메시지 규칙(제목 형식·길이, 태스크 번호가 든 브랜치)을
검사해 어기면 커밋을 거부하고, 통과한 커밋 끝에 작성자·AI 도구와 모델·태스크·토큰
사용량을 트레일러로 자동으로 붙입니다. 한 번 남긴 이력은 다시 쓰지 않는다는 원칙도
지향하지만, 지금은 GitHub 원격 설정으로만 지키고 있습니다.
`core.hooksPath` · `git interpret-trailers` 등 **git 자체 기능**으로 동작합니다.
훅은 Python 3 표준 라이브러리만 쓰므로 설치할 패키지는 없지만, `python3` 자체는
필요합니다([필요조건](#-필요조건을-말씀드립니다)).

</div>

> ⚠️ **이 저장소의 코드는 AI(Claude Code)와 함께 작성했습니다.** 훅이 커밋을 거부하거나
> `--amend`로 내용을 바꾸는 등 실제 동작을 하므로, 적용 전에 `hooks/`의 코드를 직접 읽고
> 검토해 주시기 바랍니다.

---

## 📋 완성되는 커밋은 이런 모양입니다

```
[docs][backlog] DRAFT-18을 GF-136으로 승격          ← 사람(또는 에이전트)이 씀
                                                    ← 빈 줄 (규칙)
왜 바꿨는지 설명하는 본문. 한 줄 72자 이내.            ← 선택, 사람이 씀
                                                    ← 빈 줄
Task-Id: GF-136                                     ↓ 아래는 전부 훅이 자동으로 붙임
AI-Tool: claude-code
AI-Tool-Version: 2.1.267
Co-Authored-By: Claude <noreply@anthropic.com>
AI-Model: claude-opus-5
Tokens-Used: in=5067994 out=15794
Tool-Calls: 31
Hooks-Commit: c828491
Signed-off-by: cpu-once <231006716+cpu-once@users.noreply.github.com>
```

`git log` 한 번으로 "무엇을, 왜, 누가(사람인지 어떤 모델인지), 얼마를 써서 바꿨는지"가
읽히게 하는 것이 목표입니다. AI 에이전트가 커밋을 대량으로 남길 때 그 이력을 나중에
분석할 수 있어야 하고, 동시에 사람이 읽어도 이해되어야 합니다.

## 🧩 각 필드가 무엇이고 언제 만들어지는지

**제목과 본문** — 사람(또는 에이전트)이 직접 씁니다. `commit-msg`가 검증합니다.

| 필드        | 무엇인가 · 왜 필요한가                                     | 규칙                                                                   |
| ----------- | ---------------------------------------------------------- | ---------------------------------------------------------------------- |
| `type`      | 변경의 종류. `git log`를 종류별로 걸러 읽을 수 있게 합니다 | `feat fix docs style refactor perf test build ci chore revert` 중 하나 |
| `subsystem` | 영향 범위. 어느 부분이 바뀌었는지 제목만 보고 알게 합니다  | 선택. `[a-zA-Z0-9_.-]`                                                 |
| 설명        | 무엇을 했는지                                              | **50자 이내**(유니코드 코드포인트), 명령형 현재형                      |
| 본문        | **왜** 바꿨는지. 어떻게는 diff가 이미 보여줍니다           | 선택. 한 줄 **72자 이내**, 제목과 빈 줄로 분리                         |

**트레일러** — 훅이 자동으로 붙입니다. 사람이 타이핑하지 않습니다.

| 트레일러                       | 무엇인가 · 왜 필요한가                                                                                    | 만드는 훅 · 값의 출처                                                                                 | 신뢰 수준                                                     |
| ------------------------------ | --------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| `Task-Id`                      | 이 커밋이 어느 작업의 일부인지. 커밋과 태스크를 잇습니다                                                  | `post-commit` · 브랜치명의 `<prefix>-<번호>`(decision-4)                                              | 자동                                                          |
| `AI-Tool`<br>`AI-Tool-Version` | 어떤 도구가 커밋을 만들었는지                                                                             | `post-commit` · `AI_AGENT` 환경변수(Claude Code가 하위 프로세스에 주입)                               | 강제 — LLM이 스스로 만든 값이 아님                            |
| `AI-Model`                     | 어떤 모델이 썼는지. 모델별 작업 품질을 나중에 비교할 수 있게 합니다                                       | `post-commit` · Claude Code는 세션 트랜스크립트의 `message.model`, 그 외는 `gitformat.aiModel` 설정값 | Claude Code는 서버 발급 사실 / 그 외는 자가신고               |
| `Tokens-Used`                  | 이 커밋에 든 토큰(`in=<입력> out=<출력>`). 작업 비용을 이력에서 읽게 합니다                               | `post-commit` · 이 커밋이 바꾼 파일을 건드린 응답의 토큰 합(귀속), 델타 아님(decision-27)             | 서버 발급 사실(Claude Code 한정), **측정 방법론은 실험 단계** |
| `Tool-Calls`                   | 이 커밋의 파일을 건드린 도구 호출 수                                                                      | `post-commit` · 귀속된 응답에서 대상 파일을 건드린 `tool_use` 블록 개수                               | 위와 동일                                                     |
| `Co-Authored-By`               | 공동저자 귀속                                                                                             | `post-commit` · `AI-Tool`이 `claude-code`일 때만                                                      | 자동                                                          |
| `Hooks-Commit`                 | 이 커밋을 검사한 coding-agent-git-commit-tool 자체의 버전. 훅에 버그가 있었을 때 어느 커밋들이 그 훅을 거쳤는지 역추적합니다 | `post-commit` · 훅 클론의 `rev-parse --short HEAD`                                                    | 완전 자동, 모든 커밋                                          |
| `Signed-off-by`                | 커미터 정보(DCO 관례)                                                                                     | `post-commit` · `git log -1 --format='%cn <%ce>'`                                                     | 완전 자동, 모든 커밋                                          |
| `Verify-Bypassed`              | `--no-verify`로 검사를 건너뛴 사실. 우회를 막지는 못하니 대신 기록합니다(decision-3)                      | `post-commit` · `prepare-commit-msg`가 남긴 검증 마커의 **부재**                                      | 자동                                                          |
| `Fixes`                        | 이 버그를 만든 커밋                                                                                       | **사람이 씀**(원인 커밋을 아는 경우만) · `commit-msg`가 해시 실재를 검증                              | 검증됨                                                        |

`Tokens-Used`/`Tool-Calls`는 측정에 실패하면 사유와 함께 `unavailable (사유)`로 남습니다 —
`no-session-id`, `transcript-not-found`, `transcript-unreadable`, `transcript-parse-failed`,
`no-usage-channel`. 이 커밋의 파일을 건드린 응답이 없으면 0과 함께 `(no-attributed-turn)`이
붙습니다(`Tokens-Used: in=0 out=0 (no-attributed-turn)`).

## 🪝 커밋 한 번에 훅이 도는 순서

> 공식 문서: [githooks(5)](https://git-scm.com/docs/githooks). git이 제공하는 훅은 28개이고,
> coding-agent-git-commit-tool의 훅은 지금 커밋 단계만 다룹니다. push된 이력의 보호는 원격 설정이 맡습니다
> ([다루는 범위](#-다루는-범위)).

| 순서 | 훅                                               | 커밋 객체가 있는가 | `--no-verify`로 건너뛰나 | coding-agent-git-commit-tool이 하는 일                                                                  |
| ---- | ------------------------------------------------ | ------------------ | ------------------------ | ------------------------------------------------------------------------------------ |
| 1    | [`prepare-commit-msg`](hooks/prepare-commit-msg) | 아직 없음          | **건너뛸 수 없음**       | 재생·병합 커밋 면제, 에디터 경로 거부, 검증 마커 기록                                |
| 2    | (에디터)                                         | 아직 없음          | —                        | 사람이 메시지를 씁니다. 훅보다 **뒤**라서 1번은 최종 메시지를 볼 수 없습니다         |
| 3    | [`commit-msg`](hooks/commit-msg)                 | 아직 없음          | 건너뜀                   | 제목 형식·길이, 빈 줄, `Fixes` 해시, 브랜치 `Task-Id`, `AI-Model` 화이트리스트 검증  |
| 4    | (커밋 생성)                                      | **생성됨**         | —                        | git이 커밋 객체를 만듭니다                                                           |
| 5    | [`post-commit`](hooks/post-commit)               | 있음               | 건너뛸 수 없음           | 트레일러를 `git commit --amend`로 삽입. exit code가 커밋 결과에 영향을 주지 못합니다 |

여기서 두 가지가 나옵니다. **에디터가 1번보다 뒤에 열리므로** 최종 메시지 검증은
`git commit -m`(또는 `-F`)만 가능하고, 그래서 에디터 경로는 거부합니다.
그리고 **4번에서 커밋이 이미 만들어지므로** `post-commit`은 커밋을 막을 수 없습니다 —
검사가 아니라 기록만 합니다.

## 🎯 다루는 범위

git 이력을 작업 로그로 만드는 데 필요한 세 가지입니다(decision-25).

| 기둥          | 하는 일                                                      | 지금 있는 것                                                                                                       | 계획                                                                                         |
| ------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------- |
| **형식**      | 사람이 쓰는 제목·본문을 정해진 양식으로                      | 제목·본문 검증, 에디터 경로 거부, 커밋 단위 규칙(decision-22, 강제 없음)                                           | 검증을 `prepare-commit-msg`로 통합(GF-127)                                                   |
| **출처 기록** | 누가·어떤 도구와 모델로·얼마를 들여 만들었는지 자동으로 남김 | 위 트레일러 전체, `Task-Id` 브랜치 강제, `AI-Model` 게이트                                                         | 측정 재작성(GF-129), 트레일러 집합 재정의(decision-19, `Signed-off-by`는 유지 — decision-25) |
| **이력 불변** | 한 번 남긴 기록은 다시 쓰지 않음(append-only, decision-24)   | 이 저장소의 GitHub 설정: 머지 커밋만 허용, main의 force push·삭제 금지(doc-20). 컨슈머는 doc-20을 참고해 직접 설정 | 로컬 훅 강제(DRAFT-18 append-only 훅 강제), CI 트레일러 검사(DRAFT-19)                       |

용어로 말하면 trail(감사 추적)이 세 기둥 전체이고, provenance(출처 기록)가 두 번째 기둥입니다.
attestation(서명된 증명)은 아직 없고, audit(사후 검사)은 커밋 시점 검사까지만 있습니다 —
자세한 구현 위치는 [개념 지도(doc-21)](<backlog/docs/doc-21 - 개념-지도-—-trail·provenance·attestation·audit이-어디에-구현돼-있나.md>)를 보세요.

세 기둥은 서로를 필요로 합니다. 이력이 다시 쓰이면 트레일러가 자기 커밋에 대해 거짓이
되고, 기록할 내용이 정형화돼 있지 않으면 지킬 가치가 줄어듭니다. 로컬 훅은
`--no-verify`를 막지 못합니다. 그렇게 다시 쓴 이력이 main에 force push되는 것은 원격
설정이 거부합니다. 웹 UI 커밋과 트레일러 검사는 CI로 할 계획입니다(DRAFT-19).

**언어별 lint는 다루지 않습니다**(decision-23) — 세 기둥 어디에도 속하지 않고, 컨슈머에게
npm/ruff/clang-format 같은 도구를 전제하게 만듭니다. 언어 검사가 필요하면 CI에서 돌리시기
바랍니다. coding-agent-git-commit-tool이 `core.hooksPath`를 점유하므로 그 저장소의 `.git/hooks/*`는
무시되고, 자기 훅과 함께 쓰는 방법은 아직 정하지 않았습니다.

> 이름은 git-format → git-logbook → git-trail → coding-agent-git-commit-tool 순으로 바뀌었습니다(decision-25, decision-26, decision-29). 설정 키와 파일명
> (`gitformat.*`, `gitformat.conf`, `.gitformat-*`)은 기존 설치를 깨지 않도록 아직 예전 이름입니다(GF-133).

구성은 Python 훅 + 설정 파일 하나(`hooks/gitformat.conf`) + POSIX sh 설치
스크립트(`install.sh`)입니다. `core.hooksPath` · `init.templateDir` ·
`git interpret-trailers` 같은 git 내장 메커니즘만 쓰고, 훅은 Python 3 표준 라이브러리만
씁니다(decision-16).

## ✅ 필요조건을 말씀드립니다

- **git**
- **python3** — 훅이 Python 3로 작성돼 있습니다(decision-16).
  표준 라이브러리만 쓰므로 설치할 패키지는 없지만, **훅이 실행되는 시점의 PATH에서
  `python3`가 잡혀야 합니다.**

`python3`를 못 찾을 때의 증상은 훅마다 다릅니다.

| 훅                                 | python3가 PATH에 없을 때                                                                                                                                              |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `prepare-commit-msg`, `commit-msg` | 훅이 실패하고 git이 커밋을 막습니다 — 에러가 바로 보이는 안전한 실패입니다.                                                                                           |
| `post-commit`                      | 커밋이 이미 만들어진 뒤라 git이 훅의 실패를 반영하지 않습니다 — 커밋은 성공한 것처럼 보이지만 `Task-Id`/`AI-Model`/`Signed-off-by` 같은 트레일러가 조용히 누락됩니다. |

GUI git 클라이언트(SourceTree, GitHub Desktop, IDE 내장 git 패널)는 셸
프로파일(`.zshrc` 등)을 거치지 않고 OS 최소 PATH만 물려받는 경우가 흔합니다. 최신
macOS는 `/usr/bin/python3`를 기본 내장하지 않으므로, Homebrew나 pyenv로 설치한
python3는 이런 환경에서 보이지 않을 수 있습니다.

`install.sh`도 설치할 때 `python3` 존재를 확인하지만, 그건 보통 PATH가 풍부한
터미널에서 실행되는 시점만 보장합니다 — 실제 커밋이 일어나는 시점(GUI 클라이언트의
좁은 PATH)의 동작까지 보장하지는 못합니다. 이 한계는 코드로 우회하지 않고 알려진
제약으로 두기로 했습니다(decision-16).

## 🚀 설치 방법을 안내해 드립니다

### 기존 저장소에 적용하는 방법입니다

```sh
git clone https://github.com/coralstay/coding-agent-git-commit-tool.git ~/coding-agent-git-commit-tool   # 원하는 위치에 한 번만 클론
cd ~/my-project
~/coding-agent-git-commit-tool/install.sh
```

대상 디렉터리를 인자로 주셔도 됩니다: `~/coding-agent-git-commit-tool/install.sh ~/my-project`.
클론 위치와 폴더 이름은 자유롭게 정하셔도 됩니다 — `install.sh`는 자기가 놓인 클론의 `hooks/`를 씁니다.

### 앞으로 만들 모든 새 저장소에 자동 적용하는 방법입니다

```sh
~/coding-agent-git-commit-tool/install.sh --global
```

`git init`/`git clone`을 실행할 때마다 훅과 커밋 템플릿이 자동으로 심어집니다
(`init.templateDir`). 대화형 터미널에서 인자 없이 실행하시면 이 적용 여부를 물어보고,
`--global`/`--no-global`로 비대화형 지정도 하실 수 있습니다.

## 📚 더 자세한 내용이 궁금하시다면

- **trail·provenance·attestation·audit이 각각 어느 훅·함수·설정에 구현돼 있고 어디가
  비어 있는지**는 [개념 지도(doc-21)](<backlog/docs/doc-21 - 개념-지도-—-trail·provenance·attestation·audit이-어디에-구현돼-있나.md>)에
  정리했습니다.
- **설치 상세, 커밋 메시지 규칙 전문, AI 귀속 트레일러 표, 커스터마이즈, 저장소 구조,
  주의점·한계**는 `backlog doc list`에서 확인하실 수 있습니다.
- **설계 배경과 각 결정 이유**는 `backlog decision list`에서
  확인하실 수 있습니다.
- **작업 단위와 진행 상황**은 `backlog board`에서 확인하실 수 있습니다.
- **라이선스**는 MIT입니다(전문: [`LICENSE`](./LICENSE)) — 외부 문서를 원문 그대로
  vendoring하지 않는다는 점도 함께 말씀드립니다(decision-14).
