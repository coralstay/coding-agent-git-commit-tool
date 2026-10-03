---
id: doc-1
title: 설치 가이드
type: guide
created_date: '2026-09-19 05:27'
updated_date: '2026-10-03 07:30'
---
## 🚀 설치

### 기존 저장소에 적용

```sh
git clone https://github.com/coralstay/git-trail.git ~/git-trail   # 원하는 위치에 한 번만 클론
cd ~/my-project
~/git-trail/install.sh
```

대상 디렉터리를 인자로 줘도 됩니다: `~/git-trail/install.sh ~/my-project`.

### 앞으로 만들 모든 새 저장소에 자동 적용

```sh
~/git-trail/install.sh --global
```

`git init`/`git clone`을 실행할 때마다 훅과 커밋 템플릿이 자동으로 심어집니다
(`init.templateDir`). 대화형 터미널에서 인자 없이 실행하면 이 적용 여부를 물어보고,
`--global`/`--no-global`로 비대화형 지정도 가능합니다.


## 🗂️ 이 저장소가 만들거나 바꾸는 것

**설치 시 컨슈머 저장소에서 바뀌는 것** — 파일이 아니라 git 설정뿐입니다. 어떤 소스
파일도 건드리지 않습니다.

| 대상              | 명령                                                           | 효과                                       |
| ----------------- | -------------------------------------------------------------- | ------------------------------------------ |
| 로컬(대상 저장소) | `git config core.hooksPath <git-trail>/hooks`                 | `.git/hooks/`의 기존 로컬 훅을 완전히 대체 |
| 로컬(대상 저장소) | `git config commit.template <git-trail>/.gitmessage`          | 커밋 에디터에 스켈레톤 표시                |
| 전역(`--global`)  | `git config --global init.templateDir <git-trail>/template`   | 이후 모든 신규 저장소에 자동 적용          |
| 전역(`--global`)  | `git config --global commit.template <git-trail>/.gitmessage` | 위와 동일, 전역 기본값                     |

**실행 중 새로 생기는 파일**

| 파일/디렉터리             | 위치                                     | 언제                                               | 비고                                                                    |
| ------------------------- | ---------------------------------------- | -------------------------------------------------- | ----------------------------------------------------------------------- |
| `.gitformat-verified`     | `<대상 저장소>/.git/`                    | `pre-commit` 통과 시 생성, `post-commit`이 곧 삭제 | 커밋 사이에 남지 않는 임시 마커                                         |
| `.gitformat-token-attributed` | `<대상 저장소>/.git/`                | Claude Code 실측 성공 시에만 `post-commit`이 갱신(`unavailable`일 때는 갱신 안 함) | `Tokens-Used`/`Tool-Calls` 귀속 기록(첫 줄 세션 ID, 이후 이미 귀속된 응답 키 — 세션이 바뀌면 새로 시작, GF-129), 커밋 간 유지됨. 예전 델타 커서 `.gitformat-token-cursor`는 더 쓰지 않으며 측정 성공 시 지워짐 |
| `template/hooks/*`        | 이 git-trail 클론 자신의 `template/` 안 | `install.sh --global` 실행 시                      | 클론 위치를 가리키는 심볼릭 링크, 커밋 안 됨(`.gitignore`)              |

**커밋 자체가 바뀌는 경우**: `post-commit`이 조건에 따라 `git commit --amend`로
방금 만든 커밋의 footer에 트레일러를 추가합니다(README의 "훅 생애주기" 섹션과
doc-3 "AI 귀속 트레일러 레퍼런스" 참고) — 이 경우 커밋 해시가 한 번 더 바뀝니다.
기존 소스 파일 내용은 건드리지 않습니다.
