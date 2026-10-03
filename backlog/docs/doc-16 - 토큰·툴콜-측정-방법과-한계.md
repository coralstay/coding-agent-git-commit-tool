---
id: doc-16
title: 토큰·툴콜 측정 방법과 한계
type: specification
created_date: '2026-09-25 19:34'
updated_date: '2026-10-03 13:12'
---
# 토큰·툴콜 측정 방법과 한계

`Tokens-Used`와 `Tool-Calls` 트레일러가 어떻게 계산되는지, 무엇을 세지 못하는지.
용어는 doc-14 참고.

## 왜 줄 단위로 더하면 안 되는가 (필수)

트랜스크립트는 **한 번의 API 응답을 content 블록 개수만큼 여러 줄로 쪼개** 기록하고,
**각 줄이 동일한 `usage`를 반복해서** 들고 있다. 실측:

```
apiBlockIndex=0  content=['thinking']  usage합=87932
apiBlockIndex=1  content=['text']      usage합=87932
apiBlockIndex=2  content=['tool_use']  usage합=87932
apiBlockIndex=3  content=['tool_use']  usage합=87932
→ 줄마다 더하면 351,728 (실제는 87,932. 4배)
```

한 세션 전체로는 assistant 줄 146개에 고유 응답 57개였고, 줄 단위 합산 26,102,818 대
응답 단위 합산 9,964,308으로 **2.62배** 차이가 났다.

**집계 알고리즘은 반드시 이 순서다.**

1. assistant 줄을 `(requestId, message.id)`로 **그룹핑**한다
2. 그룹의 `usage`는 **한 번만** 센다(첫 줄의 값을 쓴다 — 나머지는 같은 값의 반복이다)
3. 그룹의 `tool_use` 블록은 **모든 줄에서 모은다**(한 응답의 도구 호출이 여러 줄에 흩어져
   있다). 이 목록으로 귀속 여부를 판정한다

## 현재 post-commit 구현 (GF-129, decision-27)

`Tokens-Used`는 **이 커밋에 귀속된 응답의 토큰 합**이다. 직전 커밋 이후 구간 전체(델타)는
어디에도 세거나 기록하지 않는다(decision-27이 decision-19의 `delta` 조항을 대체). 구현은
`hooks/post-commit`의 `measure_claude_code_token_usage()`다. `prepare-commit-msg`로 옮기는
일은 GF-128에 남아 있다.

1. **후보 응답.** 세션 트랜스크립트 전체와 `<트랜스크립트 디렉터리>/<세션 ID>/subagents/*.jsonl`
   (서브에이전트 트랜스크립트, 이름순)을 읽는다. 직전 커밋 이후 구간이 아니라 세션 전체다 —
   그래야 "a 수정 → b 먼저 커밋 → a 커밋" 순서에서 a를 고친 응답을 놓치지 않는다.
2. **응답 단위로 묶기.** 위 알고리즘 그대로다. `(requestId, message.id)`가 같은 줄은 한 응답이고,
   `usage`는 첫 줄 값을 한 번만, `tool_use`는 모든 줄에서 모은다. id가 하나라도 없는 줄은 각자
   하나의 응답이다(GF-139 규칙). 키가 같으면 파일이 달라도 같은 응답으로 본다.
3. **대상 경로.** 방금 만든 커밋이 바꾼 파일 목록 —
   `git diff-tree --root --no-commit-id --name-only -r -z HEAD`. `post-commit`은 커밋이 이미
   만들어진 뒤라 `git diff --cached`는 비어 있다.
4. **귀속 판정.** 응답의 `tool_use` 중 하나라도 대상 경로를 건드렸으면 귀속한다(아래 "판정 규칙").
5. **한 응답은 한 커밋에만.** 귀속한 응답 키를 `.git/.gitformat-token-attributed`에 남기고, 다음
   커밋은 이 파일에 있는 응답을 건너뛴다.

### 귀속 기록 파일 `.git/.gitformat-token-attributed`

```
<세션 ID>
<requestId> <message.id>
<requestId> <message.id>
<파일>:<줄 번호>
```

- 첫 줄은 세션 ID, 그다음은 이미 귀속된 응답 키다. id가 없는 줄의 키는 트랜스크립트 디렉터리
  기준 파일 경로와 1부터 센 줄 번호다(예: `<세션 ID>.jsonl:12`,
  `<세션 ID>/subagents/agent-1.jsonl:3`). 트랜스크립트는 뒤에 덧붙기만 하므로 키가 바뀌지 않는다.
- 첫 줄이 지금 세션과 다르거나 파일이 없거나 손상됐으면 기록을 새로 시작한다. 응답 키가 세션
  사이에 유일하다는 보장이 없어서다.
- 측정에 성공했을 때만 쓴다(귀속된 응답이 없어도 쓴다). 실패하면 그대로 둔다.

### 과거: 델타 커서 (GF-96 ~ GF-139, 폐기)

GF-129 이전에는 `.git/.gitformat-token-cursor`(`<세션 ID> <줄 수>`)에 이미 읽은 줄 수를 두고,
직전 커밋 이후 구간 전체를 귀속 필터 없이 더해 `Tokens-Used: <N>` 한 값으로 남겼다. GF-139는
여기에 응답 단위 계상, 세션별 커서, 커서 경계를 걸친 응답의 중복 방지를 더했다. 커서 파일은
이제 읽지 않으며, 측정에 성공하면 `post-commit`이 지운다. 그 시절 커밋의 `Tokens-Used`는 단일
숫자라 새 형식(`in=… out=…`)과 구별된다. 고치지 않는다.

## 귀속 필터

쌓인 응답 중 **이 커밋과 관계있는 응답만 골라내는 체**다. 기준은 하나 — 그 응답의 도구 호출이
이 커밋이 바꾼 파일을 건드렸는가.

### 예시

커밋한 파일이 `hooks/post-commit` 하나이고 세션에 다섯 응답이 있는 경우:

| 응답 | 도구 호출의 `input` | in | out | 필터 |
| --- | --- | --- | --- | --- |
| 1 | `Grep {pattern:"trailer"}` | 120,000 | 800 | 탈락 — 건드린 경로가 없다 |
| 2 | `Read {file_path:"hooks/commit-msg"}` | 200,000 | 1,200 | 탈락 — 이 커밋의 파일이 아니다 |
| 3 | `Edit {file_path:"/…/coding-agent-git-commit-tool/hooks/post-commit"}` | 210,000 | 5,000 | **통과** — 정규화 후 완전 일치 |
| 4 | `Bash {command:"ruff check hooks/post-commit"}` | 30,000 | 400 | **통과** — 명령에 경로가 있다 |
| 5 | 설계 논의 (도구 호출 0개) | 180,000 | 2,000 | 탈락 — 매칭할 입력이 없다 |

결과: `Tokens-Used: in=240000 out=5400`, `Tool-Calls: 2`. 응답 1·2·5는 어느 커밋에도 들어가지
않는다 — 커밋당 토큰량이라는 정의에서 의도된 결과다(decision-27).

### 판정 규칙 — 경로 문자열 대조만 쓴다

- `file_path`/`notebook_path` 필드를 가진 도구(Read/Edit/Write/NotebookEdit 등) → 저장소
  상대경로로 정규화해 **완전 일치**. 상대경로는 저장소 최상위 기준이다. 절대경로는 디렉터리
  부분의 심볼릭 링크를 풀어(`/tmp` → `/private/tmp` 같은) 최상위의 물리 경로와 비교한다. 파일
  자체가 링크면 링크 이름을 유지한다(커밋에는 링크 이름으로 들어간다). 저장소 밖 경로는 탈락.
  Read도 여기에 해당하므로 커밋한 파일을 읽은 응답은 귀속된다.
- Bash `command` → 명령 문자열에 대상 경로가 **경계로 구분돼** 들어 있는지만 본다.
  - 경로 앞: 문자열 시작, 공백, 따옴표, 백틱, 셸 구두점(`= ( < > | ; & , :`).
  - 경로 뒤: 문자열 끝, 또는 경로를 이어 쓰는 글자(영숫자 `_ . - /`)가 아닌 것.
    `hooks/post-commit-old`, `a.txt.bak`는 다른 파일이다.
  - 하위 디렉터리 안의 파일(`hooks/post-commit`)은 경로 앞에 `/`도 허용한다 — 절대경로나
    `../coding-agent-git-commit-tool/hooks/post-commit`도 잡힌다. `myhooks/post-commit`은 잡히지 않는다.
  - **파일명이나 파일명 앞토큰으로는 매칭하지 않는다** — `cd hooks && cat post-commit`은 귀속되지
    않는다. `README.md` 같은 흔한 이름이나 `a.txt` → `a` 같은 짧은 토큰이 무관한 응답을 끌어오는
    것을 막기 위해서다.
  - 최상위 파일(`a.txt`)은 상대경로가 곧 파일명이라 경계로 구분된 이름을 받되, 앞에 `/`는
    허용하지 않는다(`sub/a.txt`는 다른 파일). 대신 `./a.txt`와 저장소 최상위 절대경로를 붙인
    표기는 받는다.
- 그 밖의 도구(Grep/Glob 등)는 귀속하지 않는다. 경로 인자가 있어도 검색 범위일 뿐이다.

## 기록 형식

`Tokens-Used: in=<N> out=<N>` — 한 줄에 두 값을 묶는다.

| 값 | 정의 |
| --- | --- |
| `in` | 귀속된 응답의 입력측 합 = `input_tokens` + `cache_creation_input_tokens` + `cache_read_input_tokens` |
| `out` | 귀속된 응답의 `output_tokens` 합 |

캐시 토큰은 `in`에 합쳤다. 실측 비율은 in 9,821,179 / out 143,129로 거의 전부가 입력측이다 —
캐시를 빼면 값이 무의미해진다. 분리가 필요하면 `cache=`를 덧붙이면 된다.

`usage`는 응답 단위로만 존재해 파일별로 쪼갤 수 없으므로 `in`/`out`의 최소 단위는 응답이다.
`Tool-Calls`는 귀속된 응답의 `tool_use` 중 대상 경로를 실제로 건드린 **블록 개수**로 더 좁게 센다.

과거 설계(decision-19)는 `delta=<구간 전체>`를 함께 남겨 귀속 정밀도를 드러내려 했다.
decision-27로 폐기했다 — 델타는 커밋의 비용이 아니라 커밋 간격을 잰다.

## 측정 실패를 0으로 위장하지 않는다

| 상황 | 기록 |
| --- | --- |
| 정상 | `Tokens-Used: in=240000 out=5400`, `Tool-Calls: 2` |
| 귀속된 응답의 usage가 정말 0 | `Tokens-Used: in=0 out=0`, `Tool-Calls: <N>` |
| 귀속된 응답이 하나도 없음 | `Tokens-Used: in=0 out=0 (no-attributed-turn)`, `Tool-Calls: 0 (no-attributed-turn)` |
| 트랜스크립트를 못 읽음 | `unavailable (사유)` — `no-session-id`, `transcript-not-found`, `transcript-unreadable`, `transcript-parse-failed` |
| Claude Code 외 도구 | `unavailable (no-usage-channel)` |

세 번째 행이 핵심이다 — `(no-attributed-turn)`이 붙어 "토큰을 안 썼다"와 "이 커밋 파일을 건드린
응답을 못 찾았다"가 footer만 봐도 구별된다.

트랜스크립트(본 파일이나 서브에이전트 파일)에 깨진 줄이 하나라도 있으면 배치 전체가
`transcript-parse-failed`다(일부만 집계한 값을 정상값처럼 남기지 않는다, GF-112). 이제 매번 세션
전체를 읽으므로, 깨진 줄이 한 번 생기면 그 세션의 이후 커밋도 계속 이 사유가 된다.

## 한계

- **경로 문자열 대조라 완벽하지 않다.** 경로를 쓰지 않고 파일을 바꾸는 명령(글롭, 변수,
  `cd` 후 파일명만 쓰기, `sed -i` 대상이 글롭)은 놓친다. 반대로 경로를 문자열로 담기만 한
  명령(`git add hooks/post-commit`, 커밋 메시지에 경로 언급)은 귀속한다. 놓치는 쪽을 택한 것은
  오귀속보다 과소 보고가 낫다는 판단이다.
- **탐색 비용은 기록되지 않는다.** 어느 커밋의 파일도 건드리지 않은 응답(무관한 파일 읽기·검색,
  도구 없는 설계 논의)은 어느 트레일러에도 들어가지 않으므로, 트레일러를 다 더해도 세션 총량이
  나오지 않는다(decision-27). 실측으로 도구를 쓰지 않은 응답은 57개 중 3개(5%)였다(줄 단위로 세면
  57%로 보이지만 쪼개짐 때문에 생긴 착시다).
- **먼저 커밋된 쪽이 응답을 가져간다.** 한 응답이 a와 b를 함께 고쳤는데 a만 먼저 커밋하면 그
  응답 전체가 a 커밋에 들어가고, b 커밋에는 들어가지 않는다.
- **`--amend`는 같은 응답을 다시 세지 않는다.** 원래 커밋이 이미 귀속한 응답은 기록 파일에 있어,
  amend한 커밋에는 새로 생긴 응답만 들어간다(없으면 `no-attributed-turn`).
- 서브에이전트 토큰은 부모 트랜스크립트에 없다(실측으로 부모의 assistant 줄 `isSidechain`이 전부
  `false`, sidechain 토큰 합 0). 그래서 `<세션 ID>/subagents/*.jsonl`을 따로 읽는다(GF-129). 이
  레이아웃도 문서화되지 않은 내부 구현이라, 바뀌면 서브에이전트 몫이 조용히 빠진다.
- **`file-history-snapshot`은 쓸 수 없다.** 파일 편집을 정확히 기록하는 구조처럼 보이지만,
  실측으로 `trackedFileBackups`가 전부 비어 있다(한 세션 3건, 파일을 많이 고친 다른 세션
  28건 모두). 더 정확한 귀속 재료를 찾는다면 여기서 다시 시작하지 말 것.
- 트랜스크립트 경로·슬러그 규칙은 Claude Code의 문서화되지 않은 내부 구현이다. 상대가 규칙을
  바꾸면 측정이 조용히 어긋나는 대신 `unavailable (transcript-not-found)`로 드러난다.
