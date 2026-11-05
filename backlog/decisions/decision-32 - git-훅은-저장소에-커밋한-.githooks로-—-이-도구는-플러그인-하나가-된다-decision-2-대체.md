---
id: decision-32
title: git 훅은 저장소에 커밋한 .githooks로 — 이 도구는 플러그인 하나가 된다 (decision-2 대체)
date: '2026-10-30T21:23:00Z'
status: accepted
---
## Context

decision-2는 훅을 두 갈래로 배포했다. 기존 저장소는 `core.hooksPath`를 이 도구 클론의
`hooks/`로 직접 잡고(로컬 설치), 새 저장소는 전역 `init.templateDir`이 `.git/hooks/`에
클론 훅을 가리키는 심볼릭 링크를 심었다(`install.sh --global`, GF-9).

2026-10-31 유저 결정: **앞으로 만드는 모든 프로젝트의 git 훅은
`git config core.hooksPath .githooks`(저장소에 커밋된 디렉터리)로 관리한다.**
dev-tools/source-header의 pre-commit처럼 이 도구 말고도 커밋 훅이 필요한 도구가 생겼다.

- `core.hooksPath`는 저장소당 디렉터리 하나만 가리킨다. 이 도구가 그 값을 자기 클론
  경로로 차지하면 다른 도구의 훅이 들어갈 자리가 없다(README의 "자기 훅과 함께 쓰는
  방법은 아직 정하지 않았다"가 이 문제였다).
- `init.templateDir`은 `.git/` 안만 채운다. 저장소에 커밋되는 `.githooks/`를 만들 수
  없고, 심은 링크는 클론 경로에 묶여 다른 머신·다른 클론에서 깨진다.
- 훅 구성이 각 머신의 git 설정에만 있으면 저장소를 읽어서는 어떤 훅이 도는지 알 수 없다.

## Decision

**대상 저장소의 `.githooks/`가 훅 호스트다. 훅마다 공용 디스패처를 두고, 각 도구는
`<훅>.d/`의 한 줄짜리 플러그인으로 들어간다. 이 도구는 그 구조의 템플릿과 설치·이전
명령을 제공하고, 커밋 형식 로직은 플러그인 하나(`10-commit-format`)가 된다.**

```
<프로젝트>/.githooks/                      (커밋됨, core.hooksPath=.githooks)
  pre-commit                               공용 디스패처(POSIX sh)
  pre-commit.d/20-source-header            exec source-header hook pre-commit
  prepare-commit-msg                       공용 디스패처(pre-commit과 같은 파일)
  prepare-commit-msg.d/10-commit-format    exec git-commit-tool hook prepare-commit-msg "$@"
```

1. **디스패처 규칙** — `<훅>.d/*`를 이름순(셸 glob)으로 실행하고 훅 인자를 그대로
   넘긴다. 0이 아닌 종료 코드가 나오면 뒤 플러그인은 실행하지 않고 그 코드로 끝난다.
   종료 코드 127(sh의 `exec`가 명령을 못 찾음)은 경고 후 건너뛴다 — 그 도구가 없는
   머신에서 커밋이 막히지 않게 하고, 강제는 CI가 맡는다. 실행 권한 없는 파일도 경고 후
   건너뛴다(조용히 넘기면 검사가 사라진 걸 모른다). 원본은 이 저장소의 `githooks/`다.
2. **플러그인은 한 줄, 로직은 명령에** — 플러그인은 PATH의 명령을 `exec`할 뿐이다. 이
   도구의 진입점은 `git-commit-tool hook prepare-commit-msg "$@"`다
   (`~/githubs/bin/git-commit-tool` → 이 클론의 `install.sh`). install.sh는 심볼릭 링크
   체인을 따라 자기 클론을 찾고 `hooks/prepare-commit-msg`를 **절대경로로** exec한다.
   훅은 `realpath(__file__)`로 자기 위치를 정하므로 `gitformat.conf`와
   `Hooks-Commit`(`git -C <클론 hooks> rev-parse HEAD`)이 옛 설치와 똑같이 클론 기준으로
   해석된다 — 대상 저장소의 `.githooks/`에는 conf도 클론도 없지만 상관없다. 훅 로직은
   바꾸지 않았다. 기존 tests/ 전체를 이 경로로 다시 돌려 확인한다
   (`GITFORMAT_TEST_VIA_GITHOOKS=1`, CI의 두 번째 테스트 스텝).
3. **python3 부재는 여전히 커밋을 막는다** — `hook` 분기는 install.sh의 python3 가드
   뒤에 있어 python3가 없으면 exit 1이다. 가드보다 앞에서 exec하면 `env python3`가
   127을 내고 디스패처가 "명령 없음"으로 건너뛰어 조용한 통과가 된다.
4. **install** — `git-commit-tool [install] [대상]`이 `githooks/`를 대상의 `.githooks/`로
   복사(없는 파일만, 실행 권한 부여)하고 `core.hooksPath=.githooks`와 `commit.template`을
   설정한다. 이미 다른 `core.hooksPath`가 있거나, hooksPath가 없는데 `.git/hooks/`에
   링크가 아닌 훅(`*.sample` 제외)이 있으면 아무것도 쓰지 않고 멈춘다 — hooksPath를
   설정하는 순간 그 훅들이 조용히 꺼지기 때문이다. 템플릿과 내용이 다른 기존 파일은
   그 저장소에서 고친 것으로 보고 덮지 않는다. 다시 실행해도 결과가 같다.
5. **migrate** — `git-commit-tool migrate [대상]`은 `core.hooksPath`가 이 도구의
   `hooks/`(이 클론이든 다른 클론이든 — `prepare-commit-msg`와 `gitformat.conf`가 있는
   디렉터리)인 옛 설치를 `.githooks`로 옮긴다. 옛 설치에서 `.git/hooks/`는 이미 무시되고
   있었으므로 install과 달리 그 훅 때문에 멈추지 않고 목록만 알린다. 옛 설치가 아니면
   멈추고, 이미 `.githooks`면 빠진 파일만 채운다. install은 옛 설치를 만나면 migrate를
   안내하고 멈춘다.
6. **전역 `init.templateDir`은 없앤다(유지·용도 변경 아님)** — `install.sh --global`은
   이제 이유를 알리고 실패하고, `template/`과 `sync_template()`을 지운다. `--no-global`은
   원래 "전역은 건너뜀"이라 지금 동작과 같으므로 호환용으로 받아 준다.
   - 유지하지 않는 이유: templateDir은 `.git/hooks/`만 채울 수 있어 커밋된 `.githooks`를
     만들지 못하고, 이 도구의 훅만 클론 경로에 묶어 심는다 — 이번 결정이 없애려는 구조
     그 자체다.
   - 용도 변경(예: 전역 `core.hooksPath=.githooks`)을 고르지 않은 이유: 전역 상대경로
     hooksPath는 `.githooks`가 없는 **모든** 저장소의 `.git/hooks/`(pre-commit
     프레임워크 등이 쓰는 자리)를 조용히 꺼 버린다. 새 저장소마다 `git-commit-tool`을
     한 번 실행하는 비용이 그보다 작다.
   - 예전에 설정한 전역 templateDir은 자동으로 지우지 않는다(전역 설정을 바꾸는 건
     사용자의 몫). 그 링크로 연결된 훅은 `hooks/prepare-commit-msg`가 그대로 있어 계속
     동작하고(GF-16 회귀 테스트가 고정), install/migrate가 끝날 때 templateDir이 이
     클론의 `template/`을 가리키면 `git config --global --unset init.templateDir`을
     안내한다.

이 decision이 대체하는 조항: decision-2 전체(`core.hooksPath`=클론 경로의 로컬 설치,
`init.templateDir` 전역 설치, `template/hooks` 동기화). `commit.template` 설정은 그대로다.

## Consequences

- 한 저장소에 여러 도구의 훅이 공존한다. 새 도구는 `<훅>.d/NN-이름` 한 줄을 더하면 된다.
- 어떤 훅이 도는지 저장소만 읽어도 알 수 있다(`.githooks/`가 커밋돼 있다).
- **강제력이 머신에 따라 달라진다.** 예전에는 설치된 저장소에서 `prepare-commit-msg`를
  건너뛸 방법이 없었지만(decision-18), 이제 `git-commit-tool`이 PATH에 없는 머신에서는
  디스패처가 경고만 내고 커밋 형식 검사를 건너뛴다. 이 공백은 의도된 것이고 CI가 메운다
  (DRAFT-19의 CI 트레일러 검사). `--no-verify`로 건너뛸 수 없다는 성질은 그대로다 —
  디스패처도 `prepare-commit-msg` 단계에서 돈다. 반면 `pre-commit.d/`의 플러그인
  (source-header)은 git 규칙대로 `--no-verify`에 건너뛰어진다.
- GUI 클라이언트처럼 PATH가 좁은 환경에서는 python3뿐 아니라 `git-commit-tool` ·
  `source-header`도 못 찾을 수 있다. 그때는 막히지 않고 경고와 함께 건너뛴다(python3만
  찾지 못하면 여전히 막힌다).
- 종료 코드 127은 "명령 없음"으로 해석되므로, 플러그인이 부른 도구가 내부에서 127로
  끝나도 건너뜀이 된다. 이 도구는 python3 가드로 그 경로를 막았고, 다른 도구의
  플러그인을 쓸 때도 같은 점을 고려해야 한다.
- 디스패처는 stdin을 나눠 주지 않는다. stdin을 읽는 훅(pre-push, post-rewrite)에
  플러그인을 여럿 둘 때는 디스패처를 손봐야 한다 — 지금 쓰는 두 훅에는 stdin이 없다.
- 이 저장소 자신은 아직 옛 방식(`core.hooksPath`=클론 `hooks/`)으로 커밋한다. 자기
  클론에 `migrate`를 적용할지는 이 결정과 별개로 정한다.
- 대상 저장소마다 `.githooks/` 사본이 생기므로 디스패처를 고치면 각 저장소에 다시 퍼뜨려야
  한다(install은 다른 내용을 덮지 않으므로, 갱신 절차는 필요해지면 따로 정한다).

