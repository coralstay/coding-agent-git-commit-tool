---
id: doc-22
title: 유사 프로젝트 조사 — AI 커밋 출처 기록 도구 비교
type: other
created_date: '2026-10-04 01:43'
updated_date: '2026-10-04 01:43'
---
2026-10-04 조사. AI 에이전트 커밋의 출처를 git에 남기는 도구·관례를 이 프로젝트와 비교한다.

## 조사 대상

| 대상 | 기록 위치 | 기록 시점 | 강제 | 메시지 형식 검증 |
| --- | --- | --- | --- | --- |
| [block/aittributor](https://github.com/block/aittributor) | `Co-authored-by` 트레일러 | `prepare-commit-msg` | 훅 | 없음 |
| [mgoodric/ai-attribution-hooks](https://github.com/mgoodric/ai-attribution-hooks) | `Assisted-by`/`Co-authored-by`/`Generated-by` | `prepare-commit-msg` + `commit-msg` | 훅 + 집계 스크립트 | 없음 |
| [git-ai](https://github.com/git-ai-project/git-ai) | git notes(`refs/notes/ai`), 줄 단위 | 에이전트가 편집할 때마다 `git ai checkpoint` | 에이전트 훅. git 훅·래퍼 없음 | 없음 |
| [Codex CLI `commit_attribution`](https://codex.danielvaughan.com/2026/03/28/codex-cli-commit-attribution/) | 트레일러 | 모델 프롬프트에 지시 주입 | 없음(모델이 따를 뿐) | 없음 |
| [Aider](https://aider.chat/docs/git.html) | `Co-authored-by` 또는 author에 `(aider)` | 도구가 커밋할 때 | 도구 안에서만 | 없음 |
| [Linux 커널 정책](https://docs.kernel.org/process/coding-assistants.html) | `Assisted-by:` 에이전트·모델 + 보조 분석 도구 | 사람이 씀 | 리뷰 | 기존 커널 규칙 |
| [crashoverride 가이드](https://crashoverride.com/resources/knowledge-base/code-ownership/attributing-ai-commits-git) | `Generated-By: <agent>/<version> (model: <id>; operator: <email>)` | — | CI "Agent Trailer Lint" | — |
| commitlint, gitlint | — | `commit-msg`(+ CI에서 커밋 범위 검사) | 훅 + CI | 있음 |

## 각 대상에서 확인한 사실

- **aittributor**: 에이전트 판정을 4단계로 한다 — 환경변수, 자기 프로세스 조상, 같은 저장소의 형제 프로세스, 에이전트 상태 파일(`~/.claude/projects/`, `~/.codex/sessions/`). 같은 이메일의 `Co-authored-by`가 이미 있으면 붙이지 않는다. lefthook 연동 또는 `.git/hooks/`에 심볼릭 링크로 설치.
- **ai-attribution-hooks**: AI 기여 비율에 따라 트레일러를 셋으로 나눈다(~33% / 35–67% / 67%+). AI 트레일러가 있으면 `commit-msg`가 `Signed-off-by`를 요구한다 — 사람이 책임진다는 이중 서명. `ai-attribution-stats.sh`가 커밋 범위에서 AI 커밋 비율과 서명 누락을 집계한다.
- **git-ai**: 커밋 메시지를 건드리지 않는다. 귀속 정보를 notes에 두고, rebase·cherry-pick·squash·reset 뒤에 최종 코드를 분석해 notes를 새 커밋으로 옮긴다(비동기, 결과적 일관성). 프롬프트는 마스킹해 git 밖에 저장. 커밋·PR별 토큰과 비용을 계산한다.
- **Codex**: 훅을 쓰지 않는다. 문서 스스로 "compliance is high but not absolute"라고 하고, 보장이 필요하면 `prepare-commit-msg` 훅을 덧대라고 권한다.
- **Linux 커널**: "AI agents MUST NOT add Signed-off-by tags. Only humans can legally certify the DCO."
- **crashoverride**: `Signed-off-by`를 운영자(사람)의 책임 인정으로 쓰라고 권한다. 과거 커밋은 다시 쓰지 말고 별도 CSV로 감사하라고 한다.

## 이 프로젝트와 비교

### 강점

- **형식·출처·이력 불변을 한 도구에서 강제한다.** 출처 도구들은 메시지 형식을 보지 않고, 형식 검사기는 출처를 남기지 않는다.
- **훅으로 강제한다.** Codex·Aider처럼 도구나 모델이 협조해야 붙는 방식이 아니어서, 에이전트가 잊어도, 사람이 커밋해도 남는다.
- **모델명과 토큰이 서버가 발급한 값이다**(Claude Code 한정). 트랜스크립트의 `message.model`과 usage를 읽는다. 다른 도구는 고정 문자열이거나 에이전트 이름까지만 남긴다.
- **`Hooks-Commit`**: 훅 자체의 버전을 커밋마다 남겨, 훅 버그의 영향 범위를 역추적할 수 있다. 다른 도구에는 없다.
- **`Task-Id` 브랜치 강제**로 커밋과 작업을 잇는다.
- **의존성이 git + python3 표준 라이브러리뿐**이고, 트레일러가 메시지에 있어 `git log`만으로 읽히며 clone·push에 그대로 따라간다. notes는 따로 push·fetch해야 한다.

### 약점

- **커밋 단위다.** git-ai는 줄 단위로 `blame`까지 된다.
- **기록이 메시지에 있어 이력을 다시 쓰면 깨진다.** git-ai는 재작성 뒤 notes를 옮겨 붙이는데, 이 프로젝트는 재작성을 금지하는 쪽(decision-24)으로 풀었다 — 사용자에게 워크플로 제약을 지운다.
- **지금은 `post-commit`의 `--amend`로 붙인다.** 해시가 바뀌고, 트레일러가 중복되고, rebase 중 실패한다. 비교한 훅 기반 도구는 전부 `prepare-commit-msg`에서 메시지 파일에 쓴다(GF-128이 같은 방향).
- **에이전트 판정이 `AI_AGENT` 하나다.** aittributor는 신호 4개를 본다(GF-130).
- **토큰 측정이 Claude Code에만 되고, 커밋 시점에 트랜스크립트를 거슬러 재구성한다**(실험 단계, doc-16). git-ai는 편집 시점에 체크포인트를 쌓는다.
- **`Signed-off-by`를 에이전트 커밋에도 자동으로 붙인다.** 커널·crashoverride·ai-attribution-hooks가 쓰는 의미(사람의 DCO 서명)와 충돌한다.
- **에디터 경로를 거부한다.** commitlint·gitlint는 `commit-msg`에서 돌아 에디터 커밋도 검증한다. 우회 차단(decision-18)과 맞바꾼 비용이다.
- **`core.hooksPath`를 점유해 다른 훅과 조합할 수 없다.** aittributor는 lefthook으로 조합된다.
- **집계 도구가 없다.** ai-attribution-hooks의 stats 스크립트, git-ai의 `stats`/`blame` 같은 읽기 도구가 없다.
- **트레일러를 손으로 위조해도 확인하는 곳이 없다.** CI 검사(DRAFT-19)는 아직 드래프트이고 서명·증명(attestation)도 없다.
- **트레일러 이름이 독자적이다.** 업계는 `Assisted-by`/`Generated-By` 쪽으로 모이는 중이다(표준은 아직 없음). GF-128의 `AI-Agent` 이름을 정할 때 고려할 것.

## 후속

- `Signed-off-by` 재검토, 체크포인트·notes 기반 측정 검토는 각각 드래프트로 남겼다.
- 이미 있는 작업과 겹치는 것: 메시지 파일 직접 쓰기·키 단위 중복 차단(GF-128), 에이전트 판정(GF-130), CI 검사(DRAFT-19).
