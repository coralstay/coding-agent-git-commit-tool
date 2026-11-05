---
id: doc-8
title: decision 이력 지도
type: guide
created_date: '2026-09-19 05:31'
updated_date: '2026-10-03 03:16'
---
## backlog/ 디렉토리, 왜 헷갈리는가

`backlog doctor`는 클린하다 — 중복 ID나 순환 의존은 없다. 그런데도 "뭔가 중복된 것
같다"는 인상을 주는 원인은 실제 중복이 아니라 두 가지다: (1) `tasks/`·`completed/`·
`archive/`가 서로 다른 라이프사이클 단계라는 게 디렉토리 이름만 봐서는 안 보이는 것,
(2) `backlog decision list`가 모든 decision을 항상 `accepted`로만 보여줘서 나중
decision이 앞선 decision을 대체(supersede)했다는 관계가 목록 화면에는 전혀 드러나지
않는 것. 이 문서는 이 두 가지를 명확히 보여주기 위해 만들었다.

## 1. tasks / completed / archive는 중복이 아니라 서로 다른 라이프사이클 단계다

| 디렉토리 | 의미 | 지금 들어있는 것 |
| --- | --- | --- |
| `backlog/tasks/` | 활성 상태이거나 최근에 처리된 태스크 | GF-N 대부분 |
| `backlog/completed/` | Done 처리된 태스크 중 오래돼서 자동으로 옮겨진 것 | GF-43 (checks/cpp.sh·sql.sh의 NUL-safe 파일목록 수집 패턴 중복 제거) |
| `backlog/archive/tasks/`, `backlog/archive/drafts/`, `backlog/archive/milestones/` | 완료되지 못한 채 **도중에 폐기/보류**된 것 | GF-42 + 서브태스크 6개(`.1`~`.6`), 마일스톤 `m-1` |

같은 "지나간 태스크"라도 completed는 "끝까지 갔다"이고 archive는 "가다가 멈췄다"라는
점이 다르다 — 파일 형식이나 내용이 겹치는 게 아니라 각 항목이 정확히 한 디렉토리에만
있는, 서로 배타적인 상태다.

**`backlog/archive/tasks/gf-42`** (+ `gf-42.1`~`gf-42.6`, "hooks 공용
로직(resolve_self/TASK_PREFIX/BRANCH/AI_TOOL_ID) 중복 제거")는 훅 스크립트들
사이의 중복 로직을 공용 라이브러리로 뽑아내려던 시도였다. GF-42 자신의 코멘트에
따르면, 이 방향은 "버그 수정을 쉽게 하기 위해 각 훅 파일이 자기 안에서 완결되게
하는 것"과 "특정 훅 하나만 다른 셸/언어로 갈아끼울 수 있게 하는 것"이라는 두 목표와
정면으로 상충한다고 판단해 폐기됐다 — 여러 파일이 공용 lib을 source하면 이 두
목표에 반대로 가기 때문이다. 대신 "값은 `gitformat.conf` 하나로 공유하되 로직은
각 훅 파일 안에 절대 공유하지 않는다"는 지금의 원칙(파일별 리터럴 지역화)으로
방향을 바꿨고, 그 결과물이 서브태스크 `.1`~`.6`(훅별 리터럴 지역화 + 계약 문서화/
drift 감지 테스트)이다. 같은 이유로 GF-43(cpp.sh/sql.sh 공용 함수화)도 애초 계획은
은퇴했지만, 대체 작업 자체는 이후 완료돼 `backlog/completed/`에 있다 — GF-42(폐기)와
GF-43(완료)이 같은 디렉토리에 있지 않은 이유이기도 하다.

**`backlog/archive/milestones/m-1`** ("GitHub 이슈 관리 (gh CLI + Claude 연동)")은
공개 저장소로 들어오는 GitHub Issues를 gh CLI로 트리아지하고 backlog.md와 연결하는
방법을 정하려던 에픽이었다. 구체 태스크로 쪼개지기 전에 통째로 보류됐다.

## 2. decision 대체(supersession) 체인 — `backlog decision list`에는 안 보이는 관계

`backlog decision` CLI는 `create`/`list`만 제공하고 상태를 바꾸는 명령이 없다. 그래서
어떤 decision이 나중 decision으로 대체돼도 `backlog decision list`에는 영원히
`accepted`로만 표시된다. 실제 대체 관계는 각 decision 파일의 본문(Context/Decision/
Consequences)에만 산문으로 적혀 있다. 17개 decision 중 7개 주제는 대체 체인이 있고,
나머지 3개(decision-2, 4, 6)는 한 번도 대체된 적 없는 standalone decision이다.

### 대체 체인이 있는 7개 주제

| 주제 | 지금 유효 | 대체된 것 |
| --- | --- | --- |
| 커밋 메시지 스타일 | decision-10 | decision-1 |
| 서버사이드 검증 범위 | decision-25 | decision-11의 범위 제외(← decision-3의 5번 항목) |
| pre-push 존치 | decision-12(테스트·빌드 미실행 부분만), decision-25 | decision-11의 판단, decision-12의 push 단계 제외 |
| 외부 문서 vendoring | decision-9(원안) | decision-13 → decision-14가 되돌림(2단 반전) |
| 견고성 테스트 전략 | decision-8 | decision-7 |
| AI 귀속 footer | decision-5 + 본문 내 Amendment(GF-13, GF-97) | decision-15·decision-17은 대체 아니고 보완 |
| hooks 구현 언어 | decision-16 | decision-9의 POSIX 문법 유지 정책(hooks/* 범위만) |
| 우회 탐지 | decision-18 | decision-3(검증 마커·Verify-Bypassed) |
| 테스트 프레임워크 | decision-21 | decision-8의 bats-core 채택 |
| 트레일러 집합 | decision-19, decision-25(Signed-off-by 유지) | decision-10의 Signed-off-by 조항 → decision-19의 Signed-off-by 제거 조항 |
| 언어 lint | decision-23 | decision-6 |
| 프로젝트 목적·이름 | decision-25 | decision-23 제목의 "커밋 형식만" 범위 표현 |

각 행의 근거(해당 decision 파일 본문을 직접 대조):

1. **커밋 메시지 스타일** — decision-10의 Consequences: "decision-1은 이 decision으로
   대체(superseded)된다. decision-1 파일 자체는 과거 기록으로 남겨두고, 새 작업은
   이 decision을 근거로 삼는다." Conventional Commits(decision-1) → `[type][subsystem]`
   리누스 토발즈 스타일(decision-10)로 전환, type 화이트리스트 11종은 그대로 유지.

2. **서버사이드 검증 범위** — decision-11의 Decision: "decision-3의 1~4번(pre-commit
   검증마커 → post-commit이 `--no-verify`를 감지해 `Verify-Bypassed: true` 트레일러를
   삽입하는 메커니즘)은 이 decision과 무관하게 그대로 유효하다. 대체되는 건 5번의
   'git-format이 opt-in 재사용 워크플로를 제공한다'는 부분뿐이다." 즉 decision-3
   전체가 아니라 5번 항목(GitHub Actions 재사용 워크플로 제공)만 부분 대체됐고,
   `verify.yml`/`self-verify.yml`/`docs/examples/github-actions-caller.yml`이
   제거됐다.

3. **pre-push 존치** — decision-12의 제목 자체가 "decision-11의 pre-push 존치 판단
   대체"이고, Decision 항목: "decision-11의 나머지 판단 ... 은 이 decision과 무관하게
   그대로 유효하다. 대체되는 건 '`pre-push`(push 단계 테스트/빌드 실행)도 여전히
   제공한다'는 부분뿐이다." decision-11은 서버사이드 백스톱만 범위 밖으로 뺐고
   `hooks/pre-push` 자체는 유지한다고 했었는데, decision-12가 그 판단만 뒤집어
   `hooks/pre-push`를 완전히 삭제했다.

4. **외부 문서 vendoring** — 2단 반전이라 순서가 중요하다. decision-9(원안)가 "외부
   자료는 vendoring하지 않고 출처 URL도 남기지 않는다"를 원칙으로 세웠다. decision-13이
   "이 항목을 대체한다"며 셸 스타일 가이드 vendoring을 허용하는 쪽으로 뒤집었다.
   그런데 decision-14가 다시 "decision-13('외부 셸 스타일 가이드 vendoring 허용')을
   대체한다 — decision-9의 원래 조항이 다시 유효하다"고 명시하며 원상복귀시켰다.
   결과적으로 **지금 유효한 건 decision-9의 vendoring 금지 원안**이고, decision-13은
   과거에 잠깐 유효했다가 폐기된 중간 단계다. (decision-9의 다른 조항 — POSIX 문법만
   사용, 표기 관례 참고 적용 — 은 이 반전과 무관하게 계속 유효하다. 대체된 건 그중
   vendoring/출처 URL 금지 조항 하나뿐이다.)

5. **견고성 테스트 전략** — decision-8의 제목: "견고성 테스트 전략 재정의: 실무 근거
   기반 (decision-7 대체)". decision-7이 근거로 든 ISO/IEC 25010, ISO/IEC/IEEE
   29119-4 같은 표준 문서 인용을 걷어내고, 이 저장소에서 실제로 발생한 버그 이력
   (GF-15, GF-16, GF-30~39)을 근거로 재정의했다. 테스트 대상(GF-23~28)과 하네스
   (bats-core) 선택 자체는 그대로 유지된다 — 바뀐 건 "왜 이 전략을 쓰는가"의 근거뿐.

6. **AI 귀속 footer** — decision-5가 원안이고, 본문 안에 Amendment 두 개가 직접
   추가돼 갱신됐다(파일을 완전히 대체하는 새 decision이 아니라 같은 파일 안의
   수정 이력): Amendment (2026-08-24, GF-13)이 `AI-Session-Id` 트레일러를
   프라이버시 이유로 제거했고, Amendment (2026-09-19, GF-97)이 `Tokens-Used`/
   `Tool-Calls`의 "조용한 생략"을 "`unavailable (사유 슬러그)` 명시"로 바꿨다.
   decision-15는 제목에 "(decision-5 보완)"이라고 스스로 밝히듯 대체가 아니다 —
   decision-15 본문: "decision-5의 표를 대체하지 않고, '왜 그 외 도구까지
   확대하지 않았는지'를 보완 설명하는 문서로 decision-5 옆에 남긴다." 8개
   비-Claude-Code AI 도구(Cursor, GitHub Copilot CLI, Aider, Cline, Windsurf/
   Cascade, OpenAI Codex CLI, Google Gemini CLI, Amazon Q Developer CLI)를
   조사했지만 Claude Code 수준의 검증 가능한 채널을 찾지 못했다는 결론만 보완했다.
   decision-17(2026-09-25, GF-114)도 같은 성격의 보완이다 — 같은 8개 도구를 다시
   조사해 OpenAI Codex CLI가 조건 1(세션 상관관계 채널, `CODEX_THREAD_ID`)은 이제
   충족하지만 조건 2(서버 확정 usage)가 과소계상으로 성립하지 않아 구현을 보류한다는
   결론을 기록하고, 재검토 트리거를 남겼다. decision-15의 `AI-Model` 결론은 그대로
   유효하다.

7. **hooks 구현 언어** — decision-16(2026-09-21)이 hooks/*를 POSIX sh에서 Python 3
   표준 라이브러리로 전환했다. decision-9("POSIX 문법 유지 + 표기 관례만 참고 적용")을
   전면 철회하는 게 아니라 **`hooks/*` 범위에서만** 대체한다 — `install.sh`는 여전히
   POSIX sh이고 decision-9가 그대로 적용된다. 이 전환 이후 일부 문서에 "훅이 POSIX
   sh로 작성돼"라는 서술이 남아 있었다(GF-116에서 정정).

### 한 번도 대체된 적 없는 standalone decision (3개)

- **decision-2** — `core.hooksPath`(기존 저장소) + `init.templateDir`(신규 저장소)
  이원화 배포 메커니즘. 프로젝트 초기부터 지금까지 그대로 유효하다.
- **decision-4** — Task-Id를 브랜치명 패턴(`GF-<번호>`) 파싱으로 강제하는 메커니즘.
  그대로 유효하다.
- **decision-6** — SQL 지원(sqlfluff 기반) 추가. 본문에 pre-push 단계의 전체 lint를
  언급하고 있는데, 이 부분은 decision-12가 `hooks/pre-push` 자체를 완전히 삭제하며
  사실상 실효됐다 — 다만 decision-12는 decision-6을 대체 대상으로 지목하지 않았고,
  decision-6이 도입한 "언어 감지 방식(`.sqlfluff`/추적된 `.sql`)과 pre-commit 단계의
  sqlfluff lint"라는 핵심 결정 자체는 지금도 유효하다. 즉 decision으로서 공식
  대체(superseded)된 적은 없지만, 본문 일부가 이후 변경(decision-12)으로 stale해진
  사례다.

### 17개 decision 전부 계정

decision-1(대체됨) · decision-2(standalone) · decision-3(부분 대체됨, 1~4번은 유효)
· decision-4(standalone) · decision-5(원안, Amendment로 갱신 중) · decision-6
(standalone, 일부 stale) · decision-7(대체됨) · decision-8(유효) · decision-9(hooks/*
범위는 decision-16이 대체, install.sh 범위는 유효) · decision-10(유효) · decision-11
(부분 대체됨, 나머지는 유효) · decision-12(유효) · decision-13(폐기됨) · decision-14
(유효) · decision-15(decision-5를 보완, 그 자체로 유효) · decision-16(decision-9를
hooks/* 범위에서 대체, 유효) · decision-17(decision-5·decision-15를 보완, 그 자체로
유효) — 17개 모두 위 표 또는 목록 중 하나에 속한다.

### decision-18~25 (2026-09-25 이후)

decision-18(decision-3을 대체, 유효) · decision-19(decision-10의 Signed-off-by 조항을
대체, 자신의 Signed-off-by 제거 조항은 decision-25가 대체, 나머지 유효) · decision-20
(standalone) · decision-21(decision-8의 bats 채택을 대체) · decision-22(standalone) ·
decision-23(decision-6을 대체) · decision-24(standalone) · decision-25(decision-11·12의
범위 제외 조항과 decision-19의 Signed-off-by 제거 조항을 대체). 위 "17개 decision 전부
계정"의 decision-11·decision-12 상태는 이 목록이 우선한다. 문서끼리 충돌하면 가장 최근
문서를 우선한다.
