# hooks

**무엇인가**: git이 커밋마다 직접 실행하는 훅 코드와 그 설정 파일을 담는다.
`install.sh`가 대상 저장소의 `core.hooksPath`를 이 디렉터리로 맞추거나(로컬 설치),
`init.templateDir` 경유로 새 저장소의 `.git/hooks/`에 이 디렉터리를 가리키는
심볼릭 링크를 심는다(전역 설치, decision-2). 어느 쪽이든 실행되는 파일은 여기 있는
바로 이 파일들이다.

**훅 생애주기**: 이 디렉터리의 훅은 `prepare-commit-msg` 하나다. 커밋 한 번에 이렇게 돈다.

```
prepare-commit-msg → (에디터 — -m/-F면 열리지 않음) → (커밋 객체 생성)
```

- `prepare-commit-msg` — 커밋 객체가 만들어지기 **전에** 돌고 `--no-verify`로도 건너뛸
  수 없다(실측은 doc-15). 그래서 커밋 규칙 강제가 이 훅 하나로 모인다(decision-18).
  순서는 이렇다.
  1. 재생·병합 커밋 면제 — `MERGE_HEAD`/`CHERRY_PICK_HEAD`/`REBASE_HEAD`/`REVERT_HEAD`가
     있거나 source가 merge/squash면 아무것도 하지 않고 통과한다.
  2. 에디터 경로 거부 — 메시지 파일에 비주석 내용이 없으면 거부한다. 에디터가 이 훅보다
     뒤에 열려 최종 메시지를 볼 수 없기 때문이다.
  3. 메시지 검증(GF-127에서 `commit-msg`로부터 옮겨옴) — `[type][subsystem] <설명>` 형식,
     제목 50자·본문 줄 72자 제한(등록 트레일러 줄은 예외), `Fixes:` 해시의 실재 여부,
     브랜치명의 `<prefix>-<번호>` 패턴(decision-4), Claude Code 외 AI 도구의
     `gitformat.aiModel` 게이트(decision-5).
  4. 트레일러 삽입(GF-128에서 `post-commit`으로부터 옮겨옴) — `Task-Id`, `AI-Agent`,
     `Co-Authored-By`(claude-code일 때), `Hooks-Commit`, `Signed-off-by`(사람 커밋일 때만,
     decision-30)를 `git interpret-trailers --in-place`로 메시지 파일에 직접 쓴다. 키가
     메시지에 이미 있으면 붙이지 않는다(decision-19).

  `commit-msg`와 `post-commit`은 GF-127 · GF-128에서 삭제됐다. 토큰·툴콜 측정
  (`Tokens-Used`/`Tool-Calls`)은 GF-146에서 걷어냈다 — 이 도구는 커밋 포맷만 맞추고
  측정은 별도 컴포넌트의 몫이다(decision-31). `AI-Agent`의 모델을 Claude Code 세션
  트랜스크립트의 `message.model`에서 읽는 것은 출처 기록이라 남아 있다.

**Python 실행 요구사항**: 이 디렉터리의 훅 파일은 전부 Python 3이고 표준 라이브러리만
쓴다(decision-16). 셔뱅은
`#!/usr/bin/env python3`이므로 **설치 시점이 아니라 훅이 실행되는 시점의 PATH에서**
`python3`가 잡혀야 한다. `install.sh`의 확인은 설치 시점만 보장한다 — GUI git
클라이언트는 셸 프로파일을 거치지 않고 OS 최소 PATH만 물려받는 경우가 흔해
Homebrew/pyenv로 깐 python3를 못 찾을 수 있다. 코드로 우회하지 않고 알려진 한계로
둔다. `python3`를 못 찾으면 `prepare-commit-msg`가 실패해 커밋이 막히므로 바로 드러난다.

훅이 여럿이던 시절에는 겹치는 블록(자기 위치 해석, conf 읽기 가드)을 공유 모듈로 빼지
않고 파일마다 중복을 유지했다 — 파일 하나만 읽으면 그 훅의 동작을 전부 알 수 있어야
한다는 감사 가능성 요구사항이다(decision-16). 훅을 다시 늘릴 때도 같은 원칙을 따른다.

**gitformat.conf**: git config 포맷으로 쓴 내부 기본값 상수 파일이다. 커밋 type 목록,
트레일러 키 이름, 길이 제한, 예외 브랜치, 알려진 모델 ID가 들어 있고 훅이
`git config --file`로 읽는다. `[gitformat "trailer"]` 섹션의 키는 본문 72자 제한의
예외 목록이기도 하다 — `Tokens-Used`/`Tool-Calls`는 GF-146에서 빠졌으므로 직접 쓴 그
줄은 평범한 본문 줄로 72자 제한을 받는다. 공유하는 건 값뿐이고 그 값을 쓰는 로직은
훅 파일에 있다. ini를 직접 파싱하지 않고 `git config`에
맡기는 이유는 다중값(`--get-all`)과 따옴표 처리 같은 git 자신의 파싱 의미론과
조용히 갈라지는 걸 막기 위해서다. 읽기가 실패하면 훅 앞부분의 가드가
즉시 멈춘다 — 빈 값으로 진행하면 원인을 알 수 없는 거부가 된다(GF-76).

컨슈머 저장소가 자기 git config에 두는 `gitformat.taskPrefix`/`gitformat.branchExempt`/
`gitformat.aiModel` 오버라이드가 있으면 그쪽이 이긴다.

**언제 쓰나**: 커밋 검증 규칙이나 트레일러 동작을 바꿀 때. 값만 바뀌면
`gitformat.conf`에서 끝내고, 판단 로직이 바뀌면 해당 훅 파일을 고친다. 고친 뒤에는
`python3 -m unittest discover -s tests`를 돌린다 — 이 저장소 자신도
같은 훅으로 커밋하므로 깨진 훅은 곧바로 자기 커밋을 막는다.

**관련 명령**:

- `./install.sh <대상 저장소>` — 대상 저장소의 `core.hooksPath`/`commit.template` 설정
- `./install.sh --global <대상 저장소>` — 위에 더해 `template/hooks/` 심볼릭 링크 생성과 전역 `init.templateDir` 설정
- `git config --get core.hooksPath` — 어떤 훅이 실제로 연결돼 있는지 확인
- `git config --file hooks/gitformat.conf --list` — 내부 기본값 전체 조회
- `git commit --no-verify` — `prepare-commit-msg`는 건너뛸 수 없어 효과가 없다(decision-18)
- `python3 -m unittest discover -s tests` — 훅 전체 동작 검증
