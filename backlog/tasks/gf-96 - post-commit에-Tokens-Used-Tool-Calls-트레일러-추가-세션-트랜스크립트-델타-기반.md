---
id: GF-96
title: post-commit에 Tokens-Used/Tool-Calls 트레일러 추가 (세션 트랜스크립트 델타 기반)
status: Done
assignee: []
created_date: '2026-09-11 12:12'
updated_date: '2026-09-12 00:55'
labels: []
dependencies: []
ordinal: 93000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
사용자가 커밋당 실제 LLM 토큰 소비량을 알고 싶어한다. LLM 에이전트는 자신의 실시간 토큰 사용량을 도구로 조회할 방법이 없지만, Claude Code는 API 응답을 그대로 세션 트랜스크립트(~/.claude/projects/<slug>/<session-id>.jsonl)에 기록하고, 각 assistant 메시지에는 Anthropic API가 실제로 반환한 usage 객체(input_tokens/output_tokens/cache_creation_input_tokens/cache_read_input_tokens)가 들어있다. 이는 trailer_ai_model()이 이미 같은 파일에서 같은 방식(CLAUDE_CODE_SESSION_ID + jq 게이팅)으로 읽어오는 것과 동일한 성격의, 자가신고가 아닌 신뢰 가능한 데이터 출처다. 한 세션에서 커밋이 여러 번 나오므로 매 커밋마다 세션 누적치를 반복해서 붙이면 의미가 없다 - 이전 커밋 이후의 델타만 집계해야 하며, 이를 위해 .gitformat-verified 마커와 같은 관례로 GIT_DIR 아래 git-미추적 커서 파일에 '이미 처리한 트랜스크립트 줄 수'를 저장해뒀다가 다음 커밋에서 그 이후 줄만 읽는 방식이 필요하다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 hooks/post-commit에 trailer_ai_model()과 동일한 gating(AI_TOOL_ID=claude-code, CLAUDE_CODE_SESSION_ID 존재, jq 설치)을 거쳐 세션 트랜스크립트에서 이전 커밋 이후 구간만 읽어 usage 필드(input/output/cache_creation/cache_read)를 합산한 Tokens-Used와 tool_use 콘텐츠 블록 개수를 센 Tool-Calls 트레일러를 추가하는 trailer_tokens_used() 함수가 추가된다
- [x] #2 ${GIT_DIR}/.gitformat-token-cursor 커서 파일이 매 성공적인 조회마다(계산값이 0이어도) 트랜스크립트의 새 총 줄 수로 갱신되어 같은 세션의 후속 커밋이 누적치가 아니라 델타만 집계하며, 트랜스크립트/jq/session-id 조회가 실패하면 커서를 갱신하지 않고 조용히 트레일러를 생략한다
- [x] #3 hooks/gitformat.conf의 [gitformat "trailer"] 섹션에 tokensUsed=Tokens-Used, toolCalls=Tool-Calls 키가 추가되고 post-commit이 다른 트레일러 키와 동일한 방식(git config --file "$CONF" --get)으로 읽는다
- [x] #4 bats 테스트가 (a) 알려진 usage 값을 가진 가짜 트랜스크립트로 만든 커밋의 Tokens-Used/Tool-Calls 합산이 정확함을, (b) 같은 세션의 두 번째 커밋이 첫 커밋 이후 새로 추가된 줄만 집계함(델타/커서 로직)을, (c) 트랜스크립트 파일 부재 또는 jq 미설치 시 커밋이 막히지 않고 두 트레일러가 조용히 생략됨을 검증한다
- [x] #5 shellcheck -s sh hooks/post-commit이 경고 없이 통과한다
- [x] #6 README.md와 README.en.md의 AI 귀속 footer 표(decision-5 섹션)에 Tokens-Used/Tool-Calls 설명이 기존 AI-Model/Hooks-Commit 행과 같은 스타일로 추가된다
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. hooks/gitformat.conf [gitformat "trailer"]에 tokensUsed=Tokens-Used, toolCalls=Tool-Calls 추가
2. hooks/post-commit: TRAILER_TOKENS_USED/TRAILER_TOOL_CALLS 변수 읽기 추가, CURSOR 상수 추가(${GIT_DIR}/.gitformat-token-cursor)
3. trailer_tokens_used() 함수 작성: trailer_ai_model과 동일 gating -> transcript 총 줄수 계산 -> 커서 읽기(기본 0) -> 커서 이후 구간만 tail -> jq로 usage 합산 + tool_use 개수 동시 계산 -> 성공시에만 커서 갱신 -> 0보다 크면 트레일러 큐잉
4. 호출 리스트에 trailer_tokens_used 추가 (trailer_ai_model 다음)
5. tests/robustness-post-commit.bats에 (a) 합산 정확성 (b) 델타/커서 (c) transcript/jq 부재 테스트 추가 - 기존 AI-Model 테스트의 FAKE_HOME/SLUG 기법 재사용
6. bats tests/ 전체 실행, shellcheck -s sh hooks/post-commit 실행 및 수정
7. README.md/README.en.md AI 귀속 footer 표 + 실행중 생성 파일 표에 문서 반영
8. 작은 단위 커밋 반복, 최종적으로 브랜치 push
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
구현/테스트/문서 완료: hooks/gitformat.conf(tokensUsed/toolCalls 키), hooks/post-commit(trailer_tokens_used() + CURSOR 커서 파일), tests/robustness-post-commit.bats(GF-96 케이스 4개), tests/consistency.bats(키 목록 갱신), README.md/README.en.md(AI 귀속 footer 표 + 실행중 생성 파일 표). bats tests/ 전체 99/99 통과, shellcheck -s sh 전체 통과. 커밋 시도가 이 세션의 샌드박스 제약으로 차단됨 - Bash 세션의 cwd가 이 저장소가 아니라 무관한 다른 워크트리(simple_react_spring_web)에 고정돼 있어(inline cd로는 안 바뀜), 그 워크트리의 claude-rails PreToolUse 훅(pre_commit_check.py)이 모든 git commit 호출을 가로채 그 무관한 프로젝트의 .claude-rails.json testCommand(scripts/test-all.sh, frontend node_modules 미설치로 항상 실패)를 대상으로 검사해 커밋 자체가 실행 전에 거부됨. git add/commit 모두 실행 전 차단되어 실제 손실은 없음 - 워킹트리 변경사항은 전부 그대로 남아있음. 커밋/푸시는 이 저장소 경로에 정확히 고정된 별도 세션/에이전트가 이어서 처리해야 함.

--- 이어받은 세션(커밋/finalize 담당) ---
이전 세션이 남긴 워킹트리 변경사항(코드/테스트/문서)을 그대로 이어받아
검증 후 커밋/push까지 완료. 이번 세션에서 발견한 것: 이 저장소 자신의
.git/config core.hooksPath/commit.template이 이미 삭제된 임시 디렉터리
(/var/folders/.../tmp.kyByl4Bz3k/...)를 가리키고 있어 로컬 훅이 전혀
실행되지 않는 상태였다(이전 세션이 보고한 cwd 고정 문제와는 별개의,
이 저장소 자체의 stale local git config 문제). `./install.sh --no-global .`
로 core.hooksPath/commit.template을 이 저장소 자신의 hooks/.gitmessage로
재설정해 정상화한 뒤 커밋 진행 - 훅 로직/설정을 변경한 게 아니라 이
저장소가 스스로에게 dogfooding 설치해둔 상태를 install.sh로 복구한 것.

검증 재확인: bats tests/ 전체 99/99 통과(exit 0), shellcheck -s sh
hooks/commit-msg hooks/pre-commit hooks/post-commit hooks/checks/*.sh
install.sh 경고 없이 통과.

커밋 3개 생성, 전부 Task-Id/AI-Tool/Hooks-Commit/Signed-off-by 트레일러
자동 부착 확인(0cd8aff, 3cbb904, a5ec61f). 다만 Tokens-Used/Tool-Calls는
이 세션 자신의 커밋에는 안 붙었다 - 이 에이전트 세션의 실제 트랜스크립트가
~/.claude/projects/-Users-my-user-simple-react-spring-web/(세션을 원래
실행한 다른 프로젝트 디렉터리 slug)에 저장돼 있어, PWD 기반 slug
(-Users-my-user-githubs-git-format)로는 찾지 못해 AC #2/#4c가 의도한
대로 조용히 생략됐다(버그 아님, 이 메타적 상황에서만 발생하는 한계).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/post-commit에 trailer_tokens_used() 추가: trailer_ai_model()과 동일한
gating(AI_TOOL_ID=claude-code + CLAUDE_CODE_SESSION_ID + jq)을 거쳐 세션
트랜스크립트에서 이전 커밋 이후 구간만 읽어 usage 토큰 합계(Tokens-Used)와
tool_use 블록 개수(Tool-Calls)를 커밋 트레일러로 추가한다. 델타 집계를 위해
${GIT_DIR}/.gitformat-token-cursor에 누적 처리 줄 수를 저장하며, 조회가 실패하면
커서를 갱신하지 않고 조용히 트레일러를 생략한다. hooks/gitformat.conf에
tokensUsed/toolCalls 키를 추가하고 다른 트레일러와 동일한 방식으로 읽는다.

검증: bats tests/ 전체 99/99 통과, shellcheck -s sh 전체(commit-msg/pre-commit/
post-commit/checks/*.sh/install.sh) 경고 없음. tests/robustness-post-commit.bats에
GF-96 케이스 4개(합산 정확성/델타·커서/트랜스크립트 부재/jq 부재) 추가, README.md·
README.en.md AI 귀속 표에 신규 트레일러 문서화.

커밋 3개: 0cd8aff([feat][post-commit]), 3cbb904([test][post-commit]),
a5ec61f([docs][readme]) - 전부 Task-Id/AI-Tool/Hooks-Commit/Signed-off-by
트레일러 자동 부착 확인. 이 저장소 자신의 .git/config core.hooksPath가 삭제된
임시 디렉터리를 가리키던 stale 상태였던 것을 install.sh로 재설정해 정상화.
<!-- SECTION:FINAL_SUMMARY:END -->
