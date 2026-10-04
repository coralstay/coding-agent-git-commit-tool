---
id: GF-128
title: 트레일러 삽입을 prepare-commit-msg로 이전하고 키 단위 중복을 차단
status: In Progress
assignee:
  - '@claude'
created_date: '2026-09-25 19:33'
updated_date: '2026-10-04 06:20'
labels:
  - hooks
  - trailers
dependencies:
  - GF-127
references:
  - decision-19
  - decision-18
  - decision-25
  - decision-28
  - decision-30
documentation:
  - backlog/docs/doc-13 - git-format-재설계-계획-—-커밋-규칙을-prepare-commit-msg로-통합.md
  - backlog/docs/doc-14 - 용어-정리-—-턴-트랜스크립트-귀속-마커-구분.md
  - backlog/docs/doc-18 - 재설계-작업-순서와-의존성.md
  - backlog/docs/doc-22 - 유사-프로젝트-조사-—-AI-커밋-출처-기록-도구-비교.md
modified_files:
  - hooks/prepare-commit-msg
  - hooks/post-commit
  - hooks/gitformat.conf
priority: high
type: feature
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
트레일러가 두 줄씩 붙는 문제가 있다. 실측으로 최근 40커밋 중 Co-Authored-By가 40/40, Task-Id가 12/40 중복이다. 원인은 중복 판정을 git interpret-trailers --parse 출력으로 하는 것인데, 이 명령은 메시지 맨 끝의 연속된 트레일러 블록만 인식해서 빈 줄로 분리된 앞 문단의 트레일러를 보지 못한다. Co-Authored-By는 별도 원인으로, 판정이 키와 값의 완전 일치라서 메시지의 값과 설정의 정규 값이 다르면 새로 추가된다.

메시지 파일에 직접 쓰면 --amend가 사라져 재귀 가드와 rebase 중 실패가 함께 해소된다. 판정 기준도 '키가 있으면 생략'으로 바꿔 사람이 쓴 값을 훅이 덮어쓰지 않게 한다.

트레일러 집합도 이 태스크에서 확정한다 — AI-Tool/AI-Tool-Version/AI-Model을 AI-Agent 한 줄로 합치고, Signed-off-by(커미터 정보는 커밋 객체에 이미 있다)와 Verify-Bypassed(우회가 불가능해져 탐지 대상이 없다)를 없앤다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 트레일러를 git interpret-trailers --in-place로 커밋 메시지 파일에 직접 쓴다 (git commit --amend를 사용하지 않는다)
- [ ] #2 중복 판정은 메시지 원문을 줄 단위로 읽어 해당 키로 시작하는 줄이 있으면 그 키를 건너뛴다
- [ ] #3 메시지에 빈 줄로 분리된 Task-Id 문단이 먼저 있어도 Task-Id가 한 줄만 남는다
- [ ] #4 메시지에 다른 값의 Co-Authored-By가 있으면 훅이 추가하지 않고 원래 값이 보존된다
- [ ] #5 AI-Tool/AI-Tool-Version/AI-Model을 AI-Agent 한 줄(<도구>/<버전> (<모델>))로 합친다
- [ ] #6 AI-Agent는 구성요소를 못 구해도 줄을 남긴다 (version-unavailable / model-unavailable)
- [ ] #7 재귀 가드가 필요 없어져 제거된다
- [ ] #8 git rebase로 커밋을 재생해도 트레일러가 추가되지 않고 훅이 실패하지도 않는다
- [ ] #9 같은 커밋에서 hooks/post-commit을 삭제한다 — 남겨두면 prepare가 넣은 트레일러에 post-commit이 Signed-off-by와 Verify-Bypassed를 또 붙여 이 저장소의 실제 이력에 잘못된 footer가 남는다
- [ ] #10 Verify-Bypassed 트레일러를 더 이상 삽입하지 않는다. Signed-off-by는 AI 도구가 감지되지 않은 커밋에만 삽입한다(decision-30이 decision-25·28의 유지 조항을 대체)
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 python3 -m unittest 스위트 전체 통과 (이관 전이면 bats tests/ 통과)
- [ ] #2 ruff check 통과
- [ ] #3 이 저장소 자신의 커밋이 새 훅으로 정상 생성되는지 확인
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-04 구현(서브에이전트):
- 트레일러 삽입을 prepare-commit-msg로 옮겼다. validate_message() 뒤 insert_trailers()가 git interpret-trailers --in-place --where end --if-exists add --if-missing add로 메시지 파일에 쓴다. hooks/post-commit은 같은 커밋에서 삭제했다(AC #1, #9).
- 중복 판정: 메시지 원문 모든 줄에서 '<키>:'로 시작하는 줄을 대소문자 무시로 찾고, 있으면 그 키는 값도 계산하지 않는다(AC #2~#4). Tokens-Used와 Tool-Calls가 둘 다 이미 있으면 토큰 측정 자체를 건너뛴다. --amend --no-edit이 응답을 소비만 하고 값을 못 남기는 일을 막는다.
- 트레일러 집합: Task-Id, AI-Agent(<도구>/<버전> (<모델>), 빈 자리는 version-unavailable/model-unavailable), Co-Authored-By(claude-code만), Tokens-Used, Tool-Calls, Hooks-Commit, Signed-off-by(AI 도구 미감지일 때만, git var GIT_COMMITTER_IDENT에서 시각을 뗀 값). 판정 신호는 ai_tool_id() 하나로 모델 게이트와 공유한다. conf: aiAgent 추가, verifyBypassed/aiTool/aiToolVersion/aiModel(trailer)/markerFile 삭제.
- 검증마커와 _GITFORMAT_AMEND_GUARD를 삭제했다(AC #7).
- 토큰 측정 대상 경로는 git diff-index --cached <HEAD 또는 빈 트리>다. GIT_INDEX_FILE을 그대로 물려받으므로 commit -a(.git/index.lock)와 commit <경로>(.git/next-index-<pid>.lock)의 임시 인덱스를 읽는다(git 2.54.0 실측, 테스트 2개). --amend도 HEAD와 비교하므로 대상은 amend가 새로 얹는 변경이다. 훅은 --amend -m을 일반 커밋과 구분할 수 없다(source=message, 실측).
- 귀속 기록은 트레일러를 메시지 파일에 쓴 뒤 저장한다. 한계(주석에 기록): 이 훅 뒤에 git이 커밋을 포기하면 귀속된 응답이 기록에만 남는다. 실측 경로는 서명 실패(exit 128 failed to write commit object)와 -e -m 또는 에디터 --amend에서 메시지를 비운 경우다. 빈 커밋(--allow-empty 없음)은 훅 전에 거부돼 해당하지 않는다. 고치려면 커밋 후 확인 단계가 필요해 범위 밖으로 두었다(과소 보고 방향의 실패).
- 테스트: 파일 삭제는 로컬 protect-tests 훅이 막아 test_verify_bypass_detection.py를 'Verify-Bypassed/검증마커가 다시 나타나지 않는다'는 AC #10 회귀 테스트로 바꿨다. tests/test_trailer_key_dedup.py를 새로 만들었다(AC #2~#4, amend). 추가한 것: rebase 재생(AC #8), Signed-off-by 사람/에이전트(AC #10), AI-Agent 축약(AC #6), GIT_INDEX_FILE 2종, amend 측정 2종, 거부 시 기록 불변. install 테스트는 실제 template/hooks의 post-commit 링크가 정리되는지 단언한다.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-10-03 03:14
---
2026-10-03: decision-25가 decision-19의 Signed-off-by 제거 조항을 대체했다(더 최근 문서인 decision-24·DRAFT-19가 Signed-off-by를 전제로 한다). 예전 AC#7(Signed-off-by와 Verify-Bypassed 미삽입)을 지우고 Signed-off-by는 유지하는 AC로 다시 적었다. 설명 본문의 'Signed-off-by를 없앤다'는 이 코멘트로 대체된다.
---
<!-- COMMENTS:END -->
