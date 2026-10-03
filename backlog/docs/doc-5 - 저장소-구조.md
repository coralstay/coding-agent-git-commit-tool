---
id: doc-5
title: 저장소 구조
type: guide
created_date: '2026-09-19 05:27'
updated_date: '2026-10-03 03:16'
---
## 📁 저장소 구조

```
git-logbook/
├── hooks/                    # core.hooksPath가 가리키는 실제 훅(Python 3, decision-16)
│   ├── readme.md             # 훅 3개의 역할·생애주기와 python3 실행 요구사항
│   ├── prepare-commit-msg    # 재생 커밋 면제, 에디터 경로 거부(decision-18)
│   ├── commit-msg            # 메시지 형식·Task-Id·AI-Model 검증
│   ├── post-commit           # 트레일러 삽입
│   └── gitformat.conf        # 내부 기본값 한 곳에 모음(git config 포맷, 이름은 GF-133에서 변경 예정)
├── template/                 # init.templateDir용 (hooks/*는 install.sh --global이 생성)
├── .gitmessage               # commit.template (GF-132에서 제거 예정)
├── install.sh                # POSIX sh 유지(decision-9) + python3 존재 확인 가드
├── tests/                    # Python unittest(dev 전용, decision-21)
├── .github/workflows/        # test.yml - 이 저장소 자신의 dev용 CI(shellcheck + ruff + unittest)
└── backlog/                  # 이 저장소 자체 개발 관리(decision, task)
```

훅 3개는 모두 Python 3이고 표준 라이브러리만 쓴다(decision-16).
셔뱅이 `#!/usr/bin/env python3`이므로 훅이 실행되는 시점의 PATH에서 `python3`가
잡혀야 한다. `install.sh`만 POSIX sh를 유지하며, 그래서 CI의 shellcheck 대상도
이 파일 하나다.

디렉터리 단위 설명은 각 `readme.md`에 있다 - `hooks/readme.md`(훅 생애주기,
gitformat.conf, python3 요구사항), `hooks/checks/readme.md`(마커 테이블, 스크립트별
검사 내용).
