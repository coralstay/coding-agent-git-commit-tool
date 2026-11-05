# decisions

**무엇인가**: 아키텍처/정책 판단을 기록한, 원칙적으로 되돌릴 수 없는 역사적 기록이다.
태스크가 아니라 "왜 이렇게 하기로 했는지"에 대한 근거를 남긴다. 현재 decision-1부터
decision-15까지 15건이 있다.

**언제 쓰나**: 여러 방식 중 하나를 선택하고 그 선택이 앞으로의 작업에 계속 영향을
줄 때(예: 커밋 메시지 스타일, AI 귀속 정책, POSIX sh 유지 여부) 기록한다. 판단이
바뀌면 기존 파일을 지우거나 고치지 않고 새 decision을 만들어 "이전 decision-N을
대체한다"고 명시하거나(예: decision-10이 decision-1을 대체), 영향이 작으면 기존
decision 파일 본문에 `## Amendment (날짜, GF-N)` 섹션을 이어붙인다(decision-5가
GF-13/GF-97 두 차례 이렇게 갱신됨).

**중요 — 대체 관계는 목록에 안 보인다**: `backlog decision list`는 모든 decision을
항상 `accepted`로만 표시하고, 어떤 decision이 나중 decision으로 대체됐는지는
상태값에 드러나지 않는다. 실제 대체 관계는 각 파일 본문에만 산문으로 적혀 있다 —
지금 유효한 decision이 뭔지 확인하려면 `backlog/docs/`의 "decision 이력 지도"
문서(doc-8)를 먼저 보거나, 번호가 가장 큰 decision부터 본문에 "대체" 언급이
있는지 직접 확인해야 한다.

**CLI 제약**: `decision update`나 `decision delete` 명령이 없다. Amendment를
추가하거나 내용을 고쳐야 할 때는 직접 파일을 다루게 되며, 이는 CLAUDE.md의
"backlog task/draft/document/decision/milestone 마크다운을 직접 수정하지 말고
CLI로만 수정하라"는 원칙과 정면으로 충돌하는 지점이다 — GF-13/GF-97 amendment
작업 모두 이 gray area를 인지한 채 조심스럽게 직접 편집했다.

**관련 명령**:

- `backlog decision create "title"` — 새 의사결정 기록 생성
- `backlog decision list` — 전체 의사결정 목록 조회(상태는 항상 accepted로만 표시됨에 주의)
