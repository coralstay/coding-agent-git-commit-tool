---
id: doc-4
title: 커스터마이즈 가이드
type: guide
created_date: '2026-09-19 05:27'
updated_date: '2026-09-25 02:58'
---
## 🔧 커스터마이즈

```sh
git config gitformat.taskPrefix PROJ                # Task-Id 접두어 변경 (기본 GF)
git config --add gitformat.branchExempt 'hotfix/*'   # 예외 브랜치 패턴 추가
git config gitformat.aiModel claude-opus-5           # Claude Code가 아닌 AI 도구의 모델명
```

`hooks/gitformat.conf`의 `gitformat.knownModel` 항목에 조직 내부 모델 ID를 추가해도 됩니다.

위 `git config` 오버라이드는 컨슈머 저장소가 값을 바꿀 때 쓰는 것이고, 이
git-format 저장소 자체의 내부 기본값(마커 파일명, trailer 키 이름, 언어 감지
마커, 커밋 타입 목록, AI-Model 화이트리스트 등)은 전부 `hooks/gitformat.conf`
(git config 포맷) 한 곳에 모여 있습니다. 컨슈머가 직접 건드릴 파일은 아니고,
git-format을 포크/커스터마이즈할 때 참고하는 내부 설정 파일입니다.

### 언어 감지 마커 값을 바꿀 때 (포크/커스터마이즈 시)

`[gitformat "marker"]`의 키는 **해석 방식이 두 가지로 나뉩니다.** 에러가 아니라 조용한
미매칭으로 끝나므로 바꿀 때 주의하세요.

| 해석 | 키 | 읽는 방식 |
| --- | --- | --- |
| 리터럴 경로 | `ts`, `python`, `java`, `cpp`, `cppMake`, `sql` | `os.path.isfile()` |
| 글롭 패턴 | `javaGradle`, `sqlGlob` | `glob.glob()` / `git ls-files` 경로명세 |

- **리터럴 키에 글롭을 넣으면 확장되지 않습니다.** `java = pom*.xml`은 `pom*.xml`이라는
  이름의 파일을 찾으므로 영원히 매칭되지 않고, 경고도 나오지 않습니다. 후보가 여러 개
  필요하면 `python`처럼 같은 키를 여러 줄로 나열하세요.
- **글롭 키에는 리터럴 파일명을 넣어도 됩니다.** 글롭 패턴은 리터럴의 상위 집합입니다.
- **값은 단어 분리되지 않습니다.** 공백이 든 값은 한 경로로 취급되므로, 예기치 않은
  파일이 매칭되는 일은 없습니다(GF-118). 이 규약은
  `tests/marker-semantics.bats`가 고정하고 있습니다.
