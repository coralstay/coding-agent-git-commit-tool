---
id: GF-135
title: 언어별 lint 제거 — git-format은 커밋 형식만 다룬다
status: Done
assignee: []
created_date: '2026-09-26 03:32'
updated_date: '2026-09-26 07:51'
labels:
  - hooks
  - scope
dependencies: []
references:
  - decision-23
documentation:
  - backlog/docs/doc-13 - git-format-재설계-계획-—-커밋-규칙을-prepare-commit-msg로-통합.md
  - backlog/docs/doc-18 - 재설계-작업-순서와-의존성.md
modified_files:
  - hooks/prepare-commit-msg
  - hooks/gitformat.conf
  - .github/workflows/test.yml
  - README.md
  - hooks/readme.md
priority: high
type: chore
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
git-format은 커밋 메시지 형식과 트레일러를 강제하는 도구인데, hooks/checks/에 TS·Python·Java·C/C++·SQL 5종의 언어별 lint 실행기(496줄)를 두고 커밋 전에 그 도구들을 돌려왔다. 커밋 형식을 맞추는 도구가 언어 lint를 돌릴 이유가 없다 — 결이 다른 기능이 한 도구에 섞여 있다(decision-23).

이 결합이 만든 비용: 컨슈머 저장소에 npm/ruff/clang-format/mvn/sqlfluff 존재를 전제하고, 그 '없으면 조용히 건너뜀'이 GF-22에서 실제 사고를 냈다. CI가 테스트를 위해 sqlfluff를 설치해야 하고, 언어 감지 마커의 리터럴/글롭 의미론(GF-118)과 C/C++ 확장자 목록, SQL dialect 기본값이 conf의 절반을 차지한다.

주의: 검증 마커(.gitformat-verified)는 gate할 대상이 없어지지만 post-commit이 살아 있는 동안은 조건 없이 계속 써야 한다. 안 쓰면 post-commit이 모든 커밋에 Verify-Bypassed를 붙인다(GF-126에서 실측). GF-128에서 post-commit과 함께 사라진다.

컨슈머가 언어 검사를 원하면 자기 pre-commit이나 CI에서 하면 된다 — 단 git-format이 core.hooksPath를 점유하므로 자기 훅을 함께 쓰는 방법을 문서에 안내해야 한다(GF-134).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 hooks/checks/ 디렉터리 전체를 삭제한다 (검사기 5개 + readme)
- [x] #2 prepare-commit-msg에서 언어 감지와 검사 호출을 전부 제거한다 (CHECKS_DIR, 언어 MARKER_* 변수, run_check, has_tracked, run_language_checks, REPO_ROOT와 chdir)
- [x] #3 gitformat.conf에서 marker 섹션, cpp 섹션, sqlDialectDefault를 제거한다
- [x] #4 검증 마커 기록은 조건 없이 유지한다 — post-commit이 살아 있는 동안 Verify-Bypassed 오작동을 막는 임시 가교이고 GF-128에서 사라진다
- [x] #5 언어별 lint 테스트를 삭제한다 (test_lint_typescript/python/java/c_cpp/sql, test_lint_dispatch, test_language_detection)
- [x] #6 CI에서 sqlfluff 설치를 제거한다. ruff와 shellcheck는 유지한다 — 이 저장소 자신의 코드를 검사하는 개발 도구다
- [x] #7 README와 hooks/readme.md에서 언어 지원 서술과 lint 생애주기 설명을 제거한다
- [x] #8 제거 후에도 커밋 형식 강제와 트레일러 삽입이 그대로 동작한다 (남은 테스트 전부 통과)
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 python3 -m unittest 스위트 전체 통과
- [x] #2 ruff check 통과
- [x] #3 이 저장소 자신의 커밋이 정상 생성되는지 확인
<!-- DOD:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
언어별 lint를 범위에서 제거했다(decision-23). `hooks/checks/` 5개 검사기와 readme(496줄), `prepare-commit-msg`의 언어 감지·검사 호출, conf의 marker/cpp 섹션과 sqlDialectDefault, 언어별 테스트, CI의 sqlfluff 설치가 모두 사라졌다.

## 검증 증거 (직접 실측)

- 스위트: `Ran 93 tests / OK` (139 → 93, lint 테스트 46개 제거)
- lint: `ruff check hooks/ tests/` 통과
- `hooks/checks/` 삭제됨. README와 `hooks/readme.md`에 `checks/` 참조 0건
- **lint가 정말 사라졌다**: `pyproject.toml` + ruff가 거부할 `import os`로 커밋 → **exit 0으로 통과**. 이 태스크 전에는 막혔다
- **마커 가교가 동작한다**: 같은 커밋의 footer에 `Verify-Bypassed` 없음

## 마커의 의미가 바뀌었다

`.gitformat-verified`는 GF-126까지 "언어 lint를 전부 통과했다"는 뜻이었다. lint를 지운 지금 남은 뜻은 "prepare-commit-msg가 돌았다"뿐이므로 **조건 없이 쓴다**.

그런데도 계속 써야 하는 이유는 `post-commit`이다. 그 훅은 마커의 **부재**를 `--no-verify` 우회의 증거로 읽어 `Verify-Bypassed`를 붙이므로, 아무도 마커를 쓰지 않으면 **모든 커밋에** 그 트레일러가 붙는다(GF-126 실측). 이 저장소는 자기 훅으로 커밋하므로 잘못된 footer가 실제 이력에 남는다.

`invalidate_stale_marker()`(GF-31)도 유지했다 — 마커의 나이가 판정에 쓰이지는 않지만 "직전 실행이 남긴 파일"이 그대로 살아 있는 상태를 만들지 않는다.

## 컨슈머 공백 — 발명하지 않고 한계로 남겼다

lint를 없애면 언어 검사가 필요한 컨슈머가 갈 곳이 없다. git-format이 `core.hooksPath`를 점유하므로 그 저장소의 `.git/hooks/*`는 무시된다. 함께 쓰는 지원 방법을 만들어내지 않고 **알려진 한계로 README에 적었다** — 결정은 GF-134에서 한다.

## 후속

README 전면 재작성은 GF-134가 맡으므로, 이번에는 거짓이 된 서술만 걷어냈다(지원 언어 5종, 언어별 도구 표, `pre-commit` 생애주기 항목).
<!-- SECTION:FINAL_SUMMARY:END -->
