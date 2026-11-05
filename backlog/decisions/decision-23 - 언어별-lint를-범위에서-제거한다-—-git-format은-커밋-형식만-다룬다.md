---
id: decision-23
title: 언어별 lint를 범위에서 제거한다 — git-format은 커밋 형식만 다룬다
date: '2026-09-26 03:30'
status: accepted
---
## Context

git-format은 커밋 메시지 형식과 트레일러를 강제하는 도구다. 그런데 `hooks/checks/`에
TS·Python·Java·C/C++·SQL 5종의 언어별 lint 실행기(496줄)를 두고, 저장소 루트의 마커 파일로
언어를 감지해 커밋 전에 그 도구들을 돌려왔다(decision-6이 SQL을 추가했다).

유저 판단: **커밋 형식을 맞추는 도구가 언어 lint를 돌릴 이유가 없다.** 결이 다른 기능이
한 도구에 섞여 있다.

실제로 이 결합은 비용을 만들고 있었다.

- 컨슈머 저장소에 npm/ruff/clang-format/mvn/sqlfluff의 존재를 전제하게 된다. "있으면 쓰고
  없으면 건너뛴다"로 완화했지만, 그 조용한 건너뜀 자체가 GF-22에서 "차단돼야 할 테스트가
  도구 부재로 통과"하는 사고를 냈다.
- CI가 테스트를 위해 sqlfluff를 설치해야 한다.
- 언어 감지 마커의 리터럴/글롭 의미론 차이(GF-118), C/C++ 확장자 목록, SQL dialect 기본값
  같은 설정이 conf의 절반을 차지한다.
- 이 기능을 지탱하는 테스트가 전체 스위트의 상당 부분이다.

## Decision

`hooks/checks/` 전체와 그것을 호출하는 코드·설정·테스트·문서를 **제거한다.** git-format의
범위는 커밋 메시지 형식, 트레일러, 그리고 그 강제 메커니즘으로 좁힌다.

- `hooks/checks/` 디렉터리 삭제 (5개 검사기 + readme)
- `prepare-commit-msg`에서 언어 감지와 검사 호출 제거 (GF-126에서 방금 옮겨온 코드다)
- `gitformat.conf`에서 `[gitformat "marker"]`, `[gitformat "cpp"]`, `sqlDialectDefault` 제거
- 언어별 lint 테스트 제거
- README의 "지원 언어 5종" 서술 제거

**`ruff`는 CI에 남긴다.** 그것은 이 저장소 자신의 훅 코드를 검사하는 개발 도구이고,
컨슈머에게 강제하는 기능이 아니다. 같은 이유로 `shellcheck`도 남는다.

decision-6(SQL 지원 추가, sqlfluff 기반)을 이 decision이 대체한다.

## Consequences

- 컨슈머 저장소가 어떤 언어를 쓰든 git-format이 요구하는 외부 도구가 없어진다 —
  `python3`만 있으면 된다.
- conf가 트레일러 키와 길이 제한, 커밋 type 목록만 남아 단순해진다.
- 테스트 스위트가 크게 줄고, CI에서 sqlfluff 설치가 불필요해진다.
- **잃는 것**: 커밋 전에 언어 검사를 강제하는 기능. 필요한 저장소는 자기 `pre-commit`이나
  CI에서 직접 하면 된다 — git-format이 `core.hooksPath`를 점유하므로, 컨슈머가 자기 훅을
  함께 쓰려면 방법을 문서에 안내해야 한다(GF-134에서 다룰 것).
- GF-126이 옮긴 lint 코드가 곧 삭제된다. 그 태스크가 헛일이 된 것은 아니다 — `pre-commit`
  삭제와 amend 재진입 가드, 마커 가교는 그대로 남는다.
- 검증 마커(`.gitformat-verified`)는 gate할 대상이 없어지지만, `post-commit`이 살아 있는
  동안은 계속 써야 한다 — 안 쓰면 `Verify-Bypassed`가 모든 커밋에 붙는다. GF-128에서
  `post-commit`과 함께 사라진다.
