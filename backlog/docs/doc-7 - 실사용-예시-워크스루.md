---
id: doc-7
title: 실사용 예시 워크스루
type: guide
created_date: '2026-09-19 05:27'
updated_date: '2026-10-03 03:16'
---
> 이 워크스루는 언어 lint 제거(GF-135)와 prepare-commit-msg 도입(GF-125) 이전 구조를
> 기준으로 쓰였습니다. 재작성은 GF-134에서 합니다.

## 📌 실제 사용법

설치가 끝나면 평소 하던 `git checkout`/`git add`/`git commit`/`git push`를
그대로 쓰면 됩니다. 아래는 실제로 한 번 돌려서 확인한 흐름입니다.

### 1. Task-Id가 들어간 브랜치에서 작업 시작

```sh
git checkout -b GF-42-fix-login-crash
```

`main`/`master`/`develop`/`release/*`가 아닌 브랜치라면 `GF-<번호>` 패턴이
브랜치명 어딘가에 있어야 합니다(대소문자 무관, 접두어는 `gitformat.taskPrefix`로
변경 가능). 없으면 이 브랜치에서의 모든 커밋이 `commit-msg`에서 거부됩니다.

### 2. 코드를 고치고 스테이징

```sh
git add src/login.ts
```

### 3. 커밋 — 훅이 순서대로 개입

```sh
git commit
```

1. **`pre-commit`**이 저장소 루트의 마커 파일로 언어를 감지해 해당 체크를 돌립니다.
   TS 프로젝트라면 이런 출력이 보입니다:
   ```
   [git-format] ts: npm run lint
   ```
2. **`commit-msg`**가 방금 쓴 커밋 메시지 제목과 브랜치명을 검사합니다.
   `commit.template`이 설정돼 있으면 에디터에 doc-2 "커밋 메시지 규칙 상세"의
   형식 안내가 주석으로 미리 채워져 있습니다. 형식에 안 맞으면:
   ```
   commit-msg: 커밋 메시지가 [type][subsystem] 형식이 아닙니다.
     형식: [type][subsystem] <description>  (subsystem 생략 가능: [type] <description>)
     허용 type: feat fix docs style refactor perf test build ci chore revert
     예: [fix][parser] 빈 입력 처리
   ```
   브랜치에 Task-Id가 없으면:
   ```
   commit-msg: 브랜치명에 GF-<번호> 패턴이 없습니다 (현재 브랜치: fix-login).
     예: GF-12-install-script
     Task-Id 없이 커밋하려면 예외 브랜치(main/master/develop/release/*)에서 작업하세요.
   ```
3. 둘 다 통과하면 커밋이 만들어지고, **`post-commit`**이 `Task-Id`/`Hooks-Commit`
   등 트레일러를 자동으로 붙입니다(내부적으로 `git commit --amend` 1회 실행 —
   README의 "훅 생애주기" 섹션 참고).

### 4. 결과 확인

```sh
git log -1
```

```
    [fix][login] 빈 비밀번호 입력 시 크래시 수정

    Task-Id: GF-42
    Signed-off-by: Jane Dev <jane@example.com>
    Hooks-Commit: b5bf03a
```

AI 코딩 에이전트로 커밋했다면 `AI-Tool`/`AI-Model`/`Co-Authored-By` 등이
더 붙습니다 — doc-3 "AI 귀속 트레일러 레퍼런스" 참고.

### 5. 급할 때 `--no-verify`로 건너뛰기

```sh
git commit --no-verify -m "[chore] 급한 핫픽스"
```

lint/형식 검사는 건너뛰지만 이력에 흔적이 남습니다:

```sh
git log -1
```

```
    [chore] 급한 핫픽스

    Verify-Bypassed: true
    Task-Id: GF-42
    Signed-off-by: Jane Dev <jane@example.com>
    Hooks-Commit: b5bf03a
```

훅은 커밋 단계까지만 돕니다. push된 이력의 보호는 원격 설정이 맡고, 컨슈머는
doc-20을 참고해 직접 설정합니다(decision-25, doc-6 "주의점과 한계" 참고).
