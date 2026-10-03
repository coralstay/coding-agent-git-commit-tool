---
id: doc-6
title: 주의점과 한계
type: guide
created_date: '2026-09-19 05:27'
updated_date: '2026-10-03 03:16'
---
## ⚠️ 주의점

- **`core.hooksPath`는 로컬 훅을 완전히 대체합니다.** 기존에 `.git/hooks/`에 다른 훅을
  쓰고 있었다면 install.sh 실행 전에 충돌 여부를 확인하세요.
- **로컬 훅은 우회할 수 있고, push된 이력은 원격 설정이 지킵니다.** 훅은 지금 커밋
  단계(`prepare-commit-msg`/`commit-msg`/`post-commit`)만 다루고, `--no-verify`나
  `core.hooksPath` 해제로 건너뛸 수 있습니다. 이력 불변은 원격 강제까지 포함해야 완결되므로
  범위 안입니다(decision-25가 decision-11·12의 범위 제외 조항을 대체). 지금 원격 강제는
  이 저장소 main의 force push·삭제 금지와 머지 커밋 전용 병합뿐입니다(doc-20). 컨슈머는
  doc-20을 참고해 자기 원격을 직접 설정해야 합니다. 웹 UI 커밋과 트레일러 검사는 CI로 할
  계획입니다(DRAFT-19).
- **`post-commit`이 커밋 해시를 amend로 바꿀 수 있습니다.** Verify-Bypassed나 AI 귀속
  트레일러가 붙을 때마다 커밋이 한 번 더 amend됩니다 — 커밋 해시를 미리 캐싱하는
  외부 도구가 있다면 이 점을 인지해야 합니다.
- **비-Claude-Code AI 도구는 설정 없이 커밋이 막힐 수 있습니다.** `AI_AGENT` 환경변수가
  감지되는데 `gitformat.aiModel`을 안 정했다면 `commit-msg`가 거부합니다(doc-4
  "커스터마이즈 가이드" 참고).

## 🚧 한계 및 향후 검토 과제

- **Windows를 네이티브로 지원하지 않습니다.** 훅은 Python 3로 작성돼 있지만
  (decision-16) `install.sh`가 POSIX sh이고 훅이 `git`을 하위 프로세스로 호출하는 방식에
  POSIX 전제가 남아 있어, WSL이나 Git Bash 같은 POSIX 호환 환경이 필요합니다.
- **훅 메시지는 UTF-8로 출력됩니다.** 로케일이 UTF-8을 제공하지 않으면 Python의 출력
  인코딩이 ascii로 떨어져 한국어 메시지를 쓰는 순간 훅이 죽었습니다 — "도구가 없어
  건너뜀"처럼 무해해야 하는 경로에서도 커밋이 트레이스백과 함께 막혔습니다. 지금은
  모든 훅이 stdout/stderr을 UTF-8로 고정하므로 죽지 않습니다(GF-116). 대신 UTF-8을
  못 읽는 터미널에서는 글자가 깨져 보일 수 있습니다 — 커밋을 막는 것보다 낫다고
  판단한 트레이드오프입니다.
- **언어별 lint는 하지 않습니다**(decision-23). 언어 검사가 필요하면 CI에서 돌리세요.
- **push 단계에서 테스트·빌드는 돌리지 않습니다**(decision-12에서 유지되는 부분). 무거운
  검사는 컨슈머의 CI 몫입니다.
- **커밋 이력을 반정형 데이터로 남기는 것까지가 이 프로젝트의 범위입니다.** 그
  데이터를 실제로 파싱하거나 학습용으로 가공하는 도구는 포함돼 있지 않습니다.
- **`AI-Model`/`Tokens-Used` 측정은 Claude Code의 문서화되지 않은 내부 경로 규칙에
  의존합니다.** `post-commit`은 트랜스크립트를
  `~/.claude/projects/<슬러그>/<세션ID>.jsonl`에서 찾고, 이때 슬러그를 "저장소 절대경로의
  영숫자가 아닌 모든 문자를 하이픈으로 치환"해 계산합니다. 이건 Claude Code의 내부
  구현이라 이 프로젝트가 지킬 수 있는 약속이 아닙니다 — 상대가 규칙을 바꾸면 이쪽은
  에러를 내지 않고 그냥 "파일이 없다"로 판단합니다(GF-119).
  관측되는 신호는 트레일러마다 다릅니다: `Tokens-Used`/`Tool-Calls`는
  `unavailable (transcript-not-found)`로 사유가 커밋 footer에 남지만, `AI-Model`은
  decision-5의 fail-open 때문에 아무 신호 없이 누락됩니다. 이 비대칭은 의도된
  것입니다.
  진단하려면 Claude Code 세션 안에서 대상 저장소로 이동해 다음 둘을 비교하세요 —
  일치하지 않으면 규칙이 바뀐 것이고, `hooks/post-commit`의
  `claude_transcript_path()`를 새 규칙에 맞춰 고쳐야 합니다.
  ```sh
  ls ~/.claude/projects/                                      # 실제 디렉터리명
  python3 -c 'import os,re; print(re.sub(r"[^A-Za-z0-9]","-",os.getcwd()))'
  ```
- **비-Claude-Code AI 도구의 `AI-Model` 값은 자가신고 수준입니다.** Claude Code처럼
  세션 트랜스크립트로 검증하지 않고, 사용자가 `gitformat.aiModel`에 설정한 값을
  그대로 신뢰합니다. Cursor/GitHub Copilot CLI/Aider/Cline/Windsurf/OpenAI Codex
  CLI/Google Gemini CLI/Amazon Q Developer CLI를 조사했지만, Claude Code처럼
  "앱이 직접 주입하는 세션 상관관계 채널 + API 응답이 확정한 model 값"을 동시에
  제공하는 도구는 찾지 못했습니다(decision-15). 가장 근접한 OpenAI Codex CLI도
  세션 로그의 model 필드가 로컬 설정값을 그대로 옮겨 적은 것으로 보여 자가신고와
  신뢰 수준이 같았습니다.
- **`mvn`/`gradle` 컴파일과 `npm run lint`은 이번 커밋과 무관한 기존 에러로도 커밋을
  막을 수 있습니다.** 언어별 검사는 도구가 허용하는 한 스테이징된 파일만 봅니다 —
  ruff/flake8, clang-format, sqlfluff는 파일 목록을 인자로 받고, tsc는 `tsconfig.json`을
  `extends`하는 임시 프로젝트 파일로 대상을 좁힙니다. 하지만 mvn/gradle에는 "이 파일들만
  컴파일" 모드가 없고(자바 컴파일은 같은 소스 트리의 다른 클래스를 참조해야 성립합니다),
  `npm run lint`은 컨슈머가 직접 쓴 스크립트라 파일 인자를 덧붙였을 때의 계약을 알 수
  없습니다. 이 둘만 프로젝트 전체 범위로 남아 있으므로, 기존 부채가 있는 프로젝트에서는
  무관한 커밋도 막힐 수 있습니다(GF-115).
