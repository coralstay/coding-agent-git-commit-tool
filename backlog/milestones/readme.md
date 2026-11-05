# milestones

**무엇인가**: 관련 태스크 여러 개를 하나의 큰 목표(Epic)로 묶는다. 태스크 자체가
아니라 태스크들을 그룹화하는 상위 단위다. 현재 활성 마일스톤은 m-0("훅 스크립트
언어/스타일 정책" — POSIX sh 유지 여부와 컨벤션을 다루는 에픽)과 m-2("AI 커밋 토큰
측정" — GF-96/97/98이 속한 에픽) 2개이고, m-1("GitHub 이슈 관리")은 구체 태스크로
쪼개지기 전에 통째로 보류돼 `archive/milestones/`에 있다.

**언제 쓰나**: 여러 태스크가 하나의 큰 흐름을 이룰 때, `task list`만으로는 그 묶음이
안 보이므로 milestone으로 묶어둔다.

**관련 명령**:

- `backlog milestone add "name" --description "..."` — 새 마일스톤 생성
- `backlog task edit GF-N -m "milestone"` — 태스크를 마일스톤에 배정
- `backlog milestone list --show-completed` — 완료/보관된 마일스톤까지 포함해 조회
