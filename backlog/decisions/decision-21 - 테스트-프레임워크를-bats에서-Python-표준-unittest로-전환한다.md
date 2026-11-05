---
id: decision-21
title: 테스트 프레임워크를 bats에서 Python 표준 unittest로 전환한다
date: '2026-09-25 19:34'
status: accepted
---
## Context

훅은 Python 3 표준 라이브러리만 쓰는데(decision-16) 테스트는 bats다. 그래서 CI가
bats-core를 GitHub에서 clone해 설치하는 스텝을 따로 둔다 — 훅은 "설치할 것 없음"인데
테스트만 외부 도구를 요구하는 비대칭이다. 현재 규모는 bats 1,880줄 / 17파일이다.

재설계로 훅 구조가 바뀌어 테스트가 어차피 전면 개편된다. 바꿀 타이밍이다. 새 설계에서
특히 두 가지가 문제가 된다.

- **트랜스크립트 픅스처가 복잡해진다.** `requestId`/`message.id`로 그룹핑되고 `content`에
  `thinking`/`text`/`tool_use` 블록이 여러 개, `tool_use`에 `input.file_path`까지 필요하다.
  셸에서 `printf '%s\n' '{...}'`로 쓰면 따옴표 지옥이 된다.
- **중복 검사가 어렵다.** 지금은 `[[ "$MSG" == *"Task-Id: GF-1"* ]]` 부분 일치라 "한 번만
  나오는지"를 확인하기 번거롭고, 그게 중복 버그를 고정하는 테스트가 없는 이유 중 하나다.

## Decision

테스트를 **Python 표준 라이브러리 `unittest`**로 이관한다. `pytest`는 편하지만 설치가
필요해 "stdlib만, 설치할 것 없음"이라는 decision-16의 원칙과 어긋나므로 쓰지 않는다.

- `tests/*.bats` 전량을 `tests/test_*.py`로 이관하고 bats 파일을 삭제한다.
- `tests/helpers/git-format.bash` → `tests/isolated_repo.py` (임시 저장소 + `env` 조작).
- **파일명을 검증 내용으로 바꾼다.** `robustness-*` 같은 성격 분류를 쓰지 않는다. 예:
  `test_editor_commit_rejected.py`, `test_no_verify_cannot_bypass.py`,
  `test_trailers_never_duplicated.py`, `test_token_usage_attribution.py`,
  `test_agent_detection.py`, `test_config_keys_match_hooks.py`.
- CI에서 bats-core clone·설치 스텝을 제거하고 `python3 -m unittest discover -s tests`로
  실행한다. `shellcheck -s sh install.sh` 게이트(decision-9)와 언어별 실도구 설치
  (sqlfluff/ruff, GF-22)는 **유지한다**.
- ruff 검사 대상에 `tests/`를 포함한다.

## Consequences

- CI에서 외부 저장소 clone 의존이 사라진다. 공급망 표면이 줄고 러너에 이미 있는 `python3`만
  쓴다.
- 언어가 통일된다 — 훅과 테스트가 Python, `install.sh`만 POSIX sh.
- 픅스처를 dict → `json.dumps`로 만들 수 있어 복잡한 트랜스크립트 테스트가 가능해진다.
- 트레일러를 파싱해 **개수까지** 검증할 수 있다.
- 설정 키 일치 테스트가 설정 파일을 동적으로 읽게 되어, 손으로 나열한 목록이 드리프트하는
  문제가 없어진다.
- `python3` 부재 테스트는 자식 프로세스의 `env`만 조작한다 — 러너는 자기 `python3`로 계속
  돈다. bats판보다 오히려 명시적이다.
- 이관 비용이 든다. 다만 재설계가 어차피 요구하는 개편과 합쳐진다.
