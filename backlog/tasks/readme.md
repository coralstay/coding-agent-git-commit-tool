# tasks

**무엇인가**: 실제로 진행 중이거나 완료된 작업 단위를 담는다(현재 99개). 각 파일은
제목, 설명, 수용 기준(AC), 상태(To Do/In Progress/Done), 소속 마일스톤 등을 가진
하나의 태스크다.

**언제 쓰나**: 계획이 필요한 작업은 plan mode에서 계획을 프롬프트로 먼저 보여주고
승인받은 뒤 `backlog draft create`로 초안을 남기고, 다시 승인받아
`backlog draft promote`로 승격될 때 생긴다. 계획이 필요 없는 명확한 작업(버그 수정,
문서 보강 등)은 draft를 거치지 않고 `backlog task create`로 바로 만든다 — 이
저장소에서는 후자가 더 흔하다. 완료된 태스크는 삭제되지 않고 이 폴더에 Done 상태로
남아있다가, 오래되면 `backlog cleanup`으로 `completed/`로 이동한다.

**시작 전 필수 확인**: 이 저장소의 `require_active_task.py` 훅이 `backlog task view
<ID> --plain`으로 태스크를 먼저 읽지 않으면 Edit/Write 자체를 차단한다. 또한 태스크를
`In Progress`로 바꾸고 `task/<ID>`(예: `task/GF-103`) 브랜치로 전환해야 실제 코드
수정이 가능하다.

**관련 명령**:

- `backlog task create "title" --ac "..."` — 새 태스크 생성
- `backlog task edit GF-N -s "In Progress"` — 상태/마일스톤 등 메타데이터 수정
- `backlog task view GF-N --plain` — 작업 시작 전 반드시 읽어야 하는 상세 내용
- `backlog task list --status "<status>" --plain` — 상태별 목록 조회
- `backlog task archive GF-N` — 더 이상 유효하지 않은 태스크를 `archive/`로 이동
- `backlog task complete GF-N` — 완료된 태스크를 바로 `completed/`로 이동
