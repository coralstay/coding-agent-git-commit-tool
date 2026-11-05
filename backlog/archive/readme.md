# archive

**무엇인가**: 완료되지 못한 채 도중에 폐기/보류된 태스크·초안·마일스톤을 담는
soft-delete 보관소다. 삭제가 아니라 이동이라서 이력은 남는다. `tasks/completed/`가
"끝까지 갔다"라면 archive는 "가다가 멈췄다"다.

**지금 들어있는 것**:
- `tasks/gf-42`(+ 서브태스크 `.1`~`.6`) — 훅 스크립트들 사이의 공용 로직(`resolve_self`,
  `TASK_PREFIX`/`BRANCH`, `AI_TOOL_ID` 계산 등)을 라이브러리로 뽑아내려던 시도였다.
  "버그 수정을 쉽게 하기 위해 각 훅 파일이 자기 안에서 완결되게 한다"는 목표와
  정면으로 상충한다고 판단해 폐기됐고, 대신 "값은 `gitformat.conf` 하나로 공유하되
  로직은 각 훅 파일 안에 절대 공유하지 않는다"는 지금의 원칙(decision-9)으로
  방향을 바꿨다.
- `milestones/m-1`("GitHub 이슈 관리") — 공개 저장소로 들어오는 GitHub Issues를
  gh CLI로 트리아지하고 backlog.md와 연결하는 방법을 정하려던 에픽. 구체 태스크로
  쪼개지기 전에 통째로 보류됐다.

**언제 쓰나**: 계획을 세웠지만 진행하지 않기로 한 태스크, 혹은 방향이 바뀌어 더
이상 의미가 없어진 태스크/초안/마일스톤을 옮길 때 생긴다.

**관련 명령**:

- `backlog task archive GF-N` — 태스크를 이 폴더로 이동(soft delete)
- `backlog task list --plain` — archive된 태스크는 기본 목록에서 제외되고 조회됨
