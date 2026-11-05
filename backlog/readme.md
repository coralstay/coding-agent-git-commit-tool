# backlog

**무엇인가**: 이 저장소(git-format)의 작업 기록 전체를 담는 최상위 디렉토리다. 할 일부터
초안, 참고 문서, 의사결정, 마일스톤, 완료/보관 태스크까지 Backlog.md CLI가 관리하는
모든 산출물이 여기 들어간다.

**언제 쓰나**: `backlog init`으로 저장소를 초기화할 때 한 번 생성됐고(태스크 접두어
`GF`로 지정, 이후 변경 불가), 이후로는 직접 건드릴 일 없이 아래 서브폴더별 CLI 명령을
통해서만 내용이 채워진다.

**관련 명령**:

- `backlog overview` — 전체 현황(진행 중 태스크, 마일스톤 진척도 등) 요약
- `backlog board view` — 상태별 칸반 보드로 태스크 확인
- `backlog search "query"` — 태스크/문서/의사결정 전체에서 키워드 검색
- `backlog doctor` — 중복 ID, 순환 의존성 등 구조적 문제 진단

**서브폴더 안내**: `tasks/`, `drafts/`, `docs/`, `decisions/`, `milestones/`,
`completed/`, `archive/` — 각 폴더의 역할은 폴더 안의 readme.md를 참고한다.

**이 프로젝트만의 특이점**: 이 저장소는 `hooks/commit-msg`가 브랜치명에서
`GF-<번호>` 패턴(`gitformat.taskPrefixDefault`)을 찾아 `Task-Id` 트레일러를
강제로 붙인다 — backlog CLI의 태스크 접두어(`GF`)와 git-format 자신의 훅 기본값이
같은 문자열을 쓰도록 우연이 아니라 의도적으로 맞춰져 있다. 다른 backlog.md
프로젝트(예: claude-code-agile-hooks, 접두어 `task`)를 옮겨 다닐 때 이 점이 헷갈릴 수 있다.
