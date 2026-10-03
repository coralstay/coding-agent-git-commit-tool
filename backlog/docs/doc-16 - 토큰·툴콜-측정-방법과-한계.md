---
id: doc-16
title: 토큰·툴콜 측정 방법과 한계
type: specification
created_date: '2026-09-25 19:34'
updated_date: '2026-10-03 03:39'
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

## 현재 post-commit 구현 (GF-139 핫픽스)

아래 "귀속 필터"와 "기록 형식"은 GF-129가 `prepare-commit-msg`로 옮기며 들일 목표 설계다.
지금 `post-commit`은 귀속 필터 없이 직전 커밋 이후 구간 전체를 합산해 `Tokens-Used: <N>`
한 값으로 남긴다. 다만 두 가지는 GF-139에서 먼저 고쳤다.

- **응답 단위 계상.** 위 알고리즘 1·2단계를 그대로 적용한다. `(requestId, message.id)`가
  같은 assistant 줄은 `usage`를 한 번만 더하고, 둘 중 하나라도 없는 줄은 줄 단위로 더한다.
  `Tool-Calls`는 모든 줄의 `tool_use` 블록을 센다.
- **세션별 커서.** `.git/.gitformat-token-cursor`는 `<세션 ID> <줄 수>` 한 줄이다(개행 없음).
  트랜스크립트는 세션마다 새 파일이라 줄 수만 저장하면 새 세션의 짧은 파일을 이전 세션의
  줄 수로 읽어 첫 커밋이 0이 됐다. 세션 ID가 다르거나, 숫자만 든 예전 형식이거나, 손상됐으면
  0줄부터 센다.
- **커밋 경계를 걸친 응답.** 응답 하나의 줄이 커서 앞뒤로 나뉘면 앞 커밋이 이미 그 `usage`를
  더했다. 그래서 같은 세션이면 커서 앞 구간의 응답 키를 먼저 모아 두고, 뒤 커밋에서는 그
  키의 `usage`를 다시 더하지 않는다.

형식 변경(`in`/`out`/`delta`)과 귀속 필터는 GF-129에 남아 있다. GF-129는 위 세 가지를
`prepare-commit-msg`로 옮길 때 함께 가져가야 한다.

## 귀속 필터

쌓인 턴 중 **이 커밋과 관계있는 턴만 골라내는 체**다. 기준은 하나 — 그 턴의 도구 호출이
이 커밋에 스테이징된 파일을 건드렸는가.

대상 경로는 `git diff --cached --name-only`로 얻는다. `prepare-commit-msg`는 커밋 전에
돌기 때문에 스테이징 목록이 정확히 이 커밋의 내용이다.

### 예시

스테이징 파일이 `hooks/prepare-commit-msg` 하나이고 다섯 턴이 쌓인 경우:

| 턴 | 도구 호출의 `input` | in | out | 필터 |
| --- | --- | --- | --- | --- |
| 1 | `Grep {pattern:"trailer"}` | 120,000 | 800 | 탈락 — 경로가 없다 |
| 2 | `Read {file_path:"hooks/post-commit"}` | 200,000 | 1,200 | 탈락 — 스테이징 안 된 파일 |
| 3 | `Write {file_path:"hooks/prepare-commit-msg"}` | 210,000 | 5,000 | **통과** — 완전 일치 |
| 4 | `Bash {command:"ruff check hooks/prepare-commit-msg"}` | 30,000 | 400 | **통과** — 명령에 경로가 있다 |
| 5 | 설계 논의 (도구 호출 0개) | 180,000 | 2,000 | 탈락 — 매칭할 입력이 없다 |

결과: `Tokens-Used: in=240000 out=5400 delta=749400`, `Tool-Calls: 2`.
차이 504,000이 귀속하지 못한 양이다.

### 판정 규칙 — 정확한 경로 비교만 쓴다

- `file_path`/`notebook_path` 필드를 가진 도구(Read/Edit/Write 등) → 저장소 상대경로로
  정규화해 **완전 일치**. 오귀속이 원리적으로 불가능하다.
- Bash `command` → 명령 문자열에 저장소 상대경로가 들어 있는지만 본다. **파일명이나 파일명
  앞토큰으로는 매칭하지 않는다** — `README.md` 같은 흔한 이름이나 `a.txt` → `a` 같은 짧은
  토큰이 무관한 턴을 끌어오는 것을 막기 위해서다.

## 기록 형식

`Tokens-Used: in=<N> out=<N> delta=<N>` — 한 줄에 세 값을 묶는다.

| 값 | 정의 |
| --- | --- |
| `in` | 귀속된 턴의 입력측 합 = `input_tokens` + `cache_creation_input_tokens` + `cache_read_input_tokens` |
| `out` | 귀속된 턴의 `output_tokens` 합 |
| `delta` | 직전 커밋 이후 구간 **전체** 합(귀속 필터 없음). `in+out`과의 차이가 귀속되지 못한 양 |

`delta`를 함께 남기는 이유: 귀속 필터는 정밀도를 위해 재현율을 버리므로 반드시 과소 보고된다.
문서에만 적어두면 로그를 읽는 쪽이 알 수 없다. 두 값을 나란히 쓰면 **커밋 자체가 측정의
정밀도를 드러낸다.**

캐시 토큰은 `in`에 합쳤다. 실측 비율은 in 9,821,179 / out 143,129로 거의 전부가 입력측이다 —
캐시를 빼면 값이 무의미해진다. 분리가 필요하면 `cache=`를 덧붙이면 된다.

`usage`는 응답 단위로만 존재해 파일별로 쪼갤 수 없으므로 `in`/`out`의 최소 단위는 턴이다.
`Tool-Calls`는 대상 경로를 실제로 건드린 `tool_use` **블록 개수**로 더 좁게 센다.

## 측정 실패를 0으로 위장하지 않는다

| 상황 | 기록 |
| --- | --- |
| 정상 | `Tokens-Used: in=240000 out=5400 delta=749400` |
| 구간에 턴이 아예 없음(진짜 0) | `Tokens-Used: in=0 out=0 delta=0` |
| 턴은 있으나 귀속된 게 없음 | `Tokens-Used: in=0 out=0 delta=749400 (no-attributed-turn)` |
| 트랜스크립트를 못 읽음 | `Tokens-Used: unavailable (transcript-not-found)` 등 사유 슬러그 |

세 번째 행이 핵심이다 — `delta`가 살아 있으므로 "토큰을 안 썼다"와 "귀속에 실패했다"가
footer만 봐도 구별된다.

## 한계

- **서브에이전트 토큰은 부모 트랜스크립트에 없다.** 실측으로 assistant 줄의 `isSidechain`이
  전부 `false`이고 sidechain 토큰 합이 0이다. 위임한 작업의 비용은 어떤 방식으로도 이
  지표에 잡히지 않는다.
- 파일명을 말하지 않는 도구 호출(`bats tests/`, `backlog task edit GF-116`)과 도구를 아예
  쓰지 않은 턴(설계·논의)은 빠진다. 다만 손실은 걱정보다 작다 — 실측으로 57개 응답 중
  도구를 쓰지 않은 것은 3개(5%)다(줄 단위로 세면 57%로 보이지만 쪼개짐 때문에 생긴 착시다).
- 한 턴에서 커밋을 둘 연달아 만들면 먼저 나온 커밋이 그 구간을 가져간다.
- **`file-history-snapshot`은 쓸 수 없다.** 파일 편집을 정확히 기록하는 구조처럼 보이지만,
  실측으로 `trackedFileBackups`가 전부 비어 있다(한 세션 3건, 파일을 많이 고친 다른 세션
  28건 모두). 더 정확한 귀속 재료를 찾는다면 여기서 다시 시작하지 말 것.
- 트랜스크립트 경로·슬러그 규칙은 Claude Code의 문서화되지 않은 내부 구현이다. 상대가 규칙을
  바꾸면 측정이 조용히 어긋나는 대신 `unavailable (transcript-not-found)`로 드러난다.
