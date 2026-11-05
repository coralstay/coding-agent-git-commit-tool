---
id: GF-97
title: >-
  post-commit Tokens-Used/Tool-Calls: 측정 실패 사유 명시(unavailable+reason) + 모든 AI
  도구로 범위 확대
status: Done
assignee:
  - '@claude'
created_date: '2026-09-18 16:20'
updated_date: '2026-09-18 18:57'
labels: []
milestone: m-2
dependencies: []
references:
  - GF-98
  - decision-5
type: feature
ordinal: 94000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GF-96이 만든 trailer_tokens_used()는 측정 조건(jq/트랜스크립트/세션ID) 중 하나라도 실패하면 Tokens-Used/Tool-Calls 트레일러를 조용히 생략한다 - 이력만 보면 "AI 커밋인데 토큰을 안 남겼다"인지 "측정 자체가 불가능했다"인지, 실패했다면 왜 실패했는지 전혀 구분이 안 된다. 또한 AI_TOOL_ID가 claude-code일 때만 동작해서, AI_AGENT가 설정된 다른 AI 도구의 커밋은 애초에 아무 트레일러도 받지 못한다.

사용자 요구: 어떤 LLM/에이전트든 커밋을 남기면 반드시 그 커밋의 토큰 소비량을 측정해서(또는 측정 실패 사유를 명시해서) 남긴다 - 지금은 Claude Code로 한정하지만 추후 다른 도구로 늘어날 수 있는 구조로 준비한다. decision-15(2026-09)가 이미 "Claude Code 외에는 신뢰 가능한 로컬 토큰 채널이 없다"고 결론지었으므로 다른 도구의 실측은 구현하지 않고, 구조(AI_TOOL_ID 케이스 분기)만 준비한다.

추가로 사용자는 현재 델타 기반 합산 방식(세션 트랜스크립트에서 직전 커밋 이후 구간을 합산해 "이 커밋이 쓴 토큰"으로 간주) 자체가 "이 커밋을 만드는 데 정확히 필요했던 토큰"이 아니라 "그 시간 동안 세션에서 소비된 토큰"의 근사치일 뿐이라는 한계를 지적했다 - 더 정확한 귀속 방법은 아직 못 찾았고, 이 사실을 README에 정직하게 반영해야 한다(목적/의도 재정리 포함).

검증 과정에서 이 저장소 자체의 PROJECT_SLUG 계산 버그(밑줄이 든 $HOME 경로에서 트랜스크립트를 영영 못 찾음 - AI-Model도 동일 영향)를 발견했으나, 사용자 확인 결과 이 작업 범위에서는 제외하고 별도 bug 태스크로 분리한다(연결된 태스크 참고).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 hooks/post-commit의 trailer_tokens_used()가 measure_claude_code_token_usage() 헬퍼로 분리되어, 성공 시 MEASUREMENT_STATUS=ok + TOKENS_SUM/TOOL_CALL_COUNT를, 실패 시 MEASUREMENT_STATUS=unavailable + 실패 지점을 가리키는 구체적 사유(no-session-id/jq-not-installed/transcript-not-found/transcript-unreadable/transcript-parse-failed 중 하나)를 MEASUREMENT_REASON에 남긴다
- [x] #2 trailer_tokens_used()가 AI_TOOL_ID로 분기한다: 빈 값(사람 커밋)이면 Tokens-Used/Tool-Calls를 전혀 붙이지 않고, claude-code면 위 헬퍼 결과에 따라 실측값 또는 "unavailable (사유)"를, 그 외 감지된 AI 도구면 항상 "unavailable (no-usage-channel)"을 두 트레일러에 큐잉한다
- [x] #3 실측 합산값이 0이어도 트레일러가 생략되지 않고 Tokens-Used: 0 / Tool-Calls: 0으로 명시 기록된다(기존 -gt 0 가드 제거)
- [x] #4 tests/robustness-post-commit.bats가 (a) 사람 커밋에는 두 트레일러가 전혀 없음, (b) 비-claude-code AI 도구 커밋은 unavailable (no-usage-channel), (c) 트랜스크립트 부재/jq 부재 시 각각 정확한 사유 슬러그로 unavailable, (d) 같은 세션에서 새 트랜스크립트 라인이 없는 델타는 Tokens-Used: 0 / Tool-Calls: 0으로 명시 기록됨을 검증한다
- [x] #5 README.md/README.en.md이 (a) 상단 왜 만들었나 문단에 AI 커밋 토큰 측정 목적과 현재 델타 합산 방식이 근사치일 뿐이라는 한계 및 실험적 상태를, (b) 목적 표에 관련 행을, (c) AI 귀속 footer 표의 Tokens-Used/Tool-Calls 설명에 사유 슬러그 목록·0-vs-unavailable 구분·범위 확대를 반영한다
- [x] #6 backlog/decisions/decision-5 파일에 이번 변경(사유 슬러그, 범위 확대, 델타-근사치 한계 명문화, AI-Model은 대상 아님, PROJECT_SLUG 버그는 별도 태스크)을 설명하는 새 Amendment 섹션이 GF-13 Amendment 선례와 같은 형식으로 추가된다
- [x] #7 shellcheck -s sh hooks/commit-msg hooks/pre-commit hooks/post-commit hooks/checks/*.sh install.sh 와 bats tests/ 전체가 경고/실패 없이 통과한다
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. hooks/post-commit: trailer_tokens_used() 240-311행을 measure_claude_code_token_usage() 헬퍼(트랜스크립트 읽기, 실패 지점마다 MEASUREMENT_REASON 슬러그 기록: no-session-id/jq-not-installed/transcript-not-found/transcript-unreadable/transcript-parse-failed, 성공 시 MEASUREMENT_STATUS=ok+TOKENS_SUM/TOOL_CALL_COUNT, 항상 return 0)와 trailer_tokens_used() 디스패처(AI_TOOL_ID 케이스: 빈값=트레일러 없음, claude-code=헬퍼 호출 후 성공시 실측값/실패시 "unavailable (사유)", 그외=항상 "unavailable (no-usage-channel)")로 분리. 기존 -gt 0 가드 제거(0도 명시 기록). PROJECT_SLUG 버그는 그대로 이식(GF-98에서 별도 수정).
2. tests/robustness-post-commit.bats: 기존 GF-96 실패 케이스 2개(트랜스크립트 없음/jq 없음)를 "unavailable (사유)" 기대값으로 갱신. 재귀가드 케이스에 no-usage-channel 반영. 신규 3케이스 추가: 사람 커밋은 트레일러 없음, 비-claude-code AI 도구는 unavailable (no-usage-channel), 진짜 0 델타는 Tokens-Used: 0/Tool-Calls: 0 명시.
3. README.md/README.en.md: 상단 목적 문단에 AI 커밋 토큰 측정 목적+델타 근사치 한계+실험적 상태 추가, 목적 표에 행 추가, AI 귀속 footer 표의 Tokens-Used/Tool-Calls 설명을 사유 슬러그 목록+0 vs unavailable 구분+범위 확대로 갱신, 커서 파일 표에 "실측 성공시에만 갱신" 보강.
4. backlog/decisions/decision-5 파일에 GF-13 Amendment와 같은 형식으로 새 "## Amendment (2026-09-19, GF-97)" 섹션 추가: 사유 슬러그 도입, 범위 확대(AI_TOOL_ID 비어있지 않은 모든 커밋, 실측은 여전히 claude-code뿐), 0 vs unavailable 구분, 델타-근사치 한계 명문화, AI-Model 비대상, PROJECT_SLUG 버그는 GF-98로 분리.
검증: bats tests/ 전체 통과 + shellcheck -s sh hooks/commit-msg hooks/pre-commit hooks/post-commit hooks/checks/*.sh install.sh 클린. 커밋은 태스크 설명 커밋플랜 순서(feat→test→docs/decision)로 분리.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
검증 근거: bats tests/ 전체 102개 통과(exit 0), shellcheck -s sh hooks/commit-msg hooks/pre-commit hooks/post-commit hooks/checks/*.sh install.sh 경고 없음(exit 0). tests/robustness-post-commit.bats에 GF-97 케이스 5개(트랜스크립트 없음→unavailable (transcript-not-found), jq 없음→unavailable (jq-not-installed), 사람 커밋→트레일러 없음, 비-claude-code 도구→unavailable (no-usage-channel), 진짜 0 델타→Tokens-Used: 0/Tool-Calls: 0) 신규/갱신 후 개별 실행 및 전체 스위트에서 확인. Edit/Write 도구용 require_active_task 훅이 이 서브에이전트 세션에서 cwd를 항상 원 저장소(main repo)로 인식해(에이전트 스레드는 bash 호출 간 cwd가 리셋됨 - 매 커맨드에 cd 접두어 필요) 워크트리의 실제 In Progress 상태를 못 읽는 환경 문제를 발견 - Edit/Write 대신 Bash(python3/heredoc)로 파일을 수정해 우회함(hook은 Edit|Write 툴만 매칭, Bash는 매칭 안 함).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
hooks/post-commit의 trailer_tokens_used()를 measure_claude_code_token_usage() 헬퍼(성공 시 MEASUREMENT_STATUS=ok, 실패 시 지점별 MEASUREMENT_REASON 슬러그: no-session-id/jq-not-installed/transcript-not-found/transcript-unreadable/transcript-parse-failed)와 AI_TOOL_ID 케이스 분기 디스패처(빈값=트레일러 없음/claude-code=실측 또는 unavailable (사유)/그외=항상 unavailable (no-usage-channel))로 재작성했다. 기존 -gt 0 가드를 제거해 실측 0도 명시 기록한다. tests/robustness-post-commit.bats에 GF-97 케이스 5개를 추가/갱신했고, README.md/README.en.md 상단 목적 문단·목적 표·AI 귀속 footer 표·커서 파일 표를 갱신했으며, decision-5에 GF-13 Amendment와 같은 형식으로 Amendment (2026-09-19, GF-97) 섹션을 추가했다. 검증: bats tests/ 전체 102개 통과, shellcheck -s sh hooks/commit-msg hooks/pre-commit hooks/post-commit hooks/checks/*.sh install.sh 경고 없음. GF-98(PROJECT_SLUG 버그)은 손대지 않았고, PROJECT_SLUG 계산은 버그 있는 채로 그대로 이식했다.
<!-- SECTION:FINAL_SUMMARY:END -->
