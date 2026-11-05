---
id: doc-21
title: 개념 지도 — trail·provenance·attestation·audit이 어디에 구현돼 있나
type: specification
created_date: '2026-10-03 03:46'
updated_date: '2026-10-12 10:02'
---
git-trail이라는 이전 이름(decision-26)과 설명에 쓰는 네 용어가 이 저장소에서 실제로 무엇을 가리키는지
정리한다. 용어마다 **뜻 → 구현 위치 → 빈 곳** 순서다. 구현 위치는 함수 이름과 파일 경로로 적는다
(줄 번호는 바뀌므로 적지 않는다). 훅이 도는 순서는 README "커밋 한 번에 훅이 도는 순서"를 본다.

## 한눈에

| 용어 | 한 줄 뜻 | 주로 사는 곳 | 상태 |
| --- | --- | --- | --- |
| trail | 고칠 수 없는 작업 기록 | `hooks/prepare-commit-msg`의 트레일러 삽입, GitHub 원격 설정 | 기록은 동작, 로컬 재작성 차단은 계획 |
| provenance | 누가·무엇으로·무슨 태스크로 만들었나 | `hooks/prepare-commit-msg`의 `trailer_*` 함수와 게이트 | 동작. 토큰 · 툴콜 측정은 범위 밖(decision-31) |
| attestation | 검증 가능한 증명 | 이 도구에는 없음, 사용자 git 서명 설정에 의존 | 미구현 |
| audit | 기록을 사후에 대조·검사 | `hooks/prepare-commit-msg`의 `validate_fixes_trailer`, doc-20 확인 명령 | 커밋 시점 검사만, 사후 검사는 계획 |

## trail — 감사 추적

**뜻**: 누가·언제·무엇을 했는지 순서대로 남기고, 남긴 것은 고치지 않는 기록. coding-agent-git-commit-tool에서는
커밋 이력 자체가 trail이고, 트레일러가 그 기록의 항목이며, append-only 정책이 "고치지 않음"을 지킨다.

**구현 위치**

| 무엇 | 어디 |
| --- | --- |
| 트레일러를 커밋에 붙인다 | `hooks/prepare-commit-msg`의 `insert_trailers()` — 각 `trailer_*` 함수의 값을 모아 커밋 객체가 생기기 전에 `git interpret-trailers --in-place`로 메시지 파일에 직접 쓴다. 커밋을 다시 만들지 않는다(GF-128) |
| 같은 트레일러를 두 번 붙이지 않는다 | `hooks/prepare-commit-msg`의 `message_has_key()` — 메시지 원문에 그 키의 줄이 있으면(대소문자 무시) 건너뛴다(decision-19) |
| 재생·병합 커밋은 커밋 시점 검사와 삽입을 면제한다 | `hooks/prepare-commit-msg`의 `is_replay_commit()` — 원래 커밋의 트레일러를 그대로 들고 온다 |
| 기록 형식의 기준값 | `hooks/gitformat.conf`의 `[gitformat "trailer"]` 섹션(키 이름) |
| push된 이력을 다시 쓰지 못하게 한다 | GitHub ruleset `main-protection`(`non_fast_forward`, `deletion`), 머지 커밋만 허용 — doc-20 |
| 정책 | decision-24(append-only), decision-25(이력 불변 기둥) |

**빈 곳**
- 로컬에서 cherry-pick·`--amend`·squash를 막지 않는다. `is_replay_commit()`은 면제만 한다. 차단은 DRAFT-18 계획.
- 원격 보호는 이 저장소의 main 브랜치뿐이다. task 브랜치와 태그는 보호되지 않고, main 직접 push도 원격이 막지 않는다(로컬 claude-code-agile-hooks 훅만 막는다, DRAFT-20). 컨슈머 저장소는 각자 설정해야 한다(README, doc-20).
- 웹 UI 커밋과 PR 머지 버튼으로 만든 머지 커밋은 훅을 거치지 않아 트레일러가 하나도 없다(DRAFT-19).

## provenance — 출처 기록

**뜻**: 결과물이 어디서, 무엇으로, 어떻게 만들어졌는지에 대한 기록. SLSA(공급망 보안 표준)의 용어다.
coding-agent-git-commit-tool에서는 커밋마다 붙는 출처 트레일러가 provenance다.

**구현 위치** — 모든 트레일러는 `hooks/prepare-commit-msg`의 `insert_trailers()`가 붙인다.

| 트레일러 | 만드는 함수 | 값의 출처 | 관련 게이트(커밋을 막는 곳) |
| --- | --- | --- | --- |
| `Task-Id` | `trailer_task_id()` | 브랜치명의 `<prefix>-<번호>` | `enforce_task_id_branch()` — 패턴이 없으면 거부. 예외 브랜치(main/master/develop/release/*)·detached HEAD는 면제(decision-4) |
| `AI-Agent` | `trailer_ai_agent()` → `read_transcript_model()`, `claude_transcript_path()` | 도구 · 버전: `AI_AGENT` 환경변수(Claude Code가 주입). 모델: Claude Code는 세션 트랜스크립트의 `message.model`, 그 외는 `gitformat.aiModel` 설정 | `enforce_ai_model_gate()` — Claude Code 외 도구는 `gitformat.aiModel`이 있고 `gitformat.knownModel` 목록에 있어야 함 |
| `Co-Authored-By` | `insert_trailers()` 안에서 conf 값 | `gitformat.coAuthoredBy`. 도구가 `claude-code`일 때만 | — |
| `Hooks-Commit` | `trailer_hooks_commit()` | 훅이 들어 있는 coding-agent-git-commit-tool 클론의 `rev-parse --short HEAD` | — |
| `Signed-off-by` | `trailer_signed_off_by()` | 커미터 ident(`git var GIT_COMMITTER_IDENT`). AI 도구가 감지되지 않은 커밋에만(decision-30) | — |

트레일러별 레퍼런스는 doc-3, 에이전트 판정 신호는 doc-17. 토큰 · 툴콜 측정(`Tokens-Used`/`Tool-Calls`)은
GF-146에서 걷어냈다 — 별도 컴포넌트의 몫이다(decision-31, 폐기된 측정 문서는 doc-16).

**빈 곳**
- Claude Code 외 도구의 `AI-Agent` 모델은 자가신고다(decision-15).
- 트랜스크립트 경로는 Claude Code의 문서화되지 않은 규칙에 기댄다(`claude_transcript_path()` 주석).
- 에이전트 판정은 `AI_AGENT` 환경변수 하나에 기댄다. 검증 가능한 신호로 바꾸는 일은 GF-130의 몫이다.

## attestation — 증명

**뜻**: provenance를 **기계가 검증할 수 있는 형태**로 남긴 것. 보통 암호 서명이 붙는다(in-toto,
Sigstore, GitHub artifact attestations). "누가 그렇다고 주장했다"가 아니라 "그 주장이 위조되지
않았음을 확인할 수 있다"가 핵심이다.

**구현 위치 — coding-agent-git-commit-tool 자체에는 없다.**

| 무엇 | 어디 | 비고 |
| --- | --- | --- |
| 트레일러 | 커밋 메시지 안의 평문 | 서명되지 않은 주장. 누구나 손으로 쓸 수 있다 |
| 커밋 서명 | 사용자의 git 설정(`commit.gpgsign`, `gpg.format=ssh`) | coding-agent-git-commit-tool이 설정하지 않는다. 켜져 있으면 트레일러가 커밋 객체가 생기기 전에 메시지에 들어가므로 트레일러까지 서명 범위에 들어간다 |
| 서명 강제 | GitHub ruleset `required_signatures` | 켜지 않았다(decision-24, DRAFT-20) |

**빈 곳**
- 이 저장소에서 `git log --format=%G?`는 로컬 커밋이 `N`, GitHub 머지 커밋이 `E`로 나온다. 로컬 커밋이 `N`인 건
  서명이 없어서가 아니라 검증용 `gpg.ssh.allowedSignersFile`이 설정돼 있지 않아서다. 검증 설정부터 정리해야 서명 강제를 검토할 수 있다.
- 트레일러 내용을 서명된 별도 증명(in-toto statement 등)으로 내보내는 기능은 없다. 계획도 아직 없다.

## audit — 감사

**뜻**: 남은 기록을 사후에 대조하고 검사하는 일. trail이 "남기기"라면 audit는 "확인하기"다.

**구현 위치**

| 무엇 | 어디 | 시점 |
| --- | --- | --- |
| `Fixes:`가 가리키는 커밋이 실재하는지 | `hooks/prepare-commit-msg`의 `validate_fixes_trailer()` | 커밋 시점 |
| 제목·본문 형식 | `hooks/prepare-commit-msg`의 `validate_format()`, `validate_length()` | 커밋 시점. `--no-verify`로 건너뛸 수 없다(decision-18) |
| 원격 설정이 그대로인지 | doc-20 "확인 방법"의 `gh api` 명령 | 수동 |
| 이력에서 트레일러 읽기 | `git log --format='%h %(trailers)'`, `git interpret-trailers --parse` | 수동 |

**빈 곳**
- 커밋이 만들어진 뒤 트레일러가 참인지 자동으로 다시 확인하는 곳이 없다. CI 검사(DRAFT-19)가
  `Signed-off-by`와 실제 커미터, `Hooks-Commit`의 실재, `Task-Id`와 브랜치, 키 중복을 대조할 계획이다.
- 원격 설정이 되돌려지는 것을 감지하는 장치가 없다(DRAFT-20).

## 관련 문서

decision-24(append-only) · decision-25(목적) · decision-26(이름) · doc-3(트레일러 레퍼런스) ·
doc-16(토큰 측정, 폐기 — decision-31) · doc-17(에이전트 판정 신호) · doc-19(이력 연산 판별) · doc-20(원격 설정)
