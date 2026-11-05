---
id: decision-3
title: 'post-commit 트레일러로 --no-verify 우회 탐지 (push는 한계, 서버사이드 백스톱 필요)'
date: '2026-08-24 02:45'
status: accepted
---
## Context

`git commit --no-verify`는 `pre-commit`/`commit-msg` 훅을 건너뛴다. 훅 기반 검증을 아무리
잘 만들어도 이 플래그 하나로 전부 무력화되는데, 이 사실을 텍스트 안내(문서/컨벤션)로만
막는 건 강제력이 없다. 반면 git은 `--no-verify`를 써도, `--amend`를 해도 **`post-commit`
훅은 항상 실행**한다는 보장을 제공한다. 이 비대칭을 이용해 프로그래밍적으로 흔적을 남긴다.

## Decision

1. `pre-commit` 훅이 모든 언어별 체크를 통과하면 마지막 단계에서
   `$(git rev-parse --git-dir)/.gitformat-verified` 마커 파일을 기록한다(타임스탬프+PID 포함,
   커밋 직전 시점).
2. `post-commit` 훅은 매 커밋마다 무조건 실행되어 이 마커를 확인한다.
   - 마커가 있고 방금 생성된 것이면 검증 통과 → 마커 삭제 후 종료.
   - 마커가 없으면 `pre-commit`/`commit-msg`가 스킵됐다는 뜻(`--no-verify` 사용) →
     `git commit --amend --no-verify -m "<원본 메시지>\n\nVerify-Bypassed: true"` 로
     커밋 메시지 footer(git trailer)에 프로그래밍적으로 흔적을 삽입한다.
3. **재귀 방지**: `--amend`도 `post-commit`을 재발동시키므로, amend 직전에
   `_GITFORMAT_AMEND_GUARD=1`을 export하고 훅 시작부에서 이 값이 있으면 즉시 종료한다.
4. **멱등성**: 메시지에 이미 `Verify-Bypassed:` 트레일러가 있으면 재작업하지 않는다.
5. **명시적 한계**: `git push --no-verify`는 `pre-push`만 건너뛰고, git에는 push 이후
   무조건 실행되는 로컬 훅(post-push 같은 것)이 존재하지 않는다. 이 트릭은 push 단계에는
   적용할 수 없다 — git 구조 자체의 한계다. push까지 강제하려면 GitHub 브랜치 보호 규칙 +
   필수 status check(GitHub Actions에서 동일 검사 재실행)로 서버사이드 백스톱을 둬야 하며,
   이는 git-format이 제공하는 **선택적(opt-in)** 재사용 워크플로로 제공한다.

## Consequences

- `git commit`에서의 `--no-verify` 우회는 커밋 기록 자체에 영구적으로 남으므로, 리뷰어나
  나중의 감사(audit)가 `git log`만으로 우회 여부를 알 수 있다.
- `post-commit`이 매 커밋마다 `git commit --amend`를 조건부로 실행하므로, 커밋 해시가
  우회 시에는 한 번 더 바뀐다(정상 커밋은 영향 없음) — CI나 훅 외부에서 커밋 해시를
  미리 캐싱하는 도구가 있다면 이 점을 인지해야 한다.
- `git push --no-verify`는 로컬에서 탐지 불가하다는 한계는 README에 명확히 문서화한다.
