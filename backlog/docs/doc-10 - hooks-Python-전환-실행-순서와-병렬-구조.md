---
id: doc-10
title: hooks Python 전환 실행 순서와 병렬 구조
type: guide
created_date: '2026-09-24 09:56'
updated_date: '2026-09-24 10:08'
tags:
  - python-migration
  - planning
  - execution-order
---
# hooks Python 전환 실행 순서와 병렬 구조

전환 작업(GF-107~14)을 어떤 순서로, 무엇을 동시에 할 수 있는지 정리한다.
전체 설계 배경은 doc-9(초기 계획 문서)를 참고한다.

## ordinal과 dependencies는 다른 것을 뜻한다

- **`ordinal`**: 혼자 순차로 진행할 때 따라가면 안전한 "한 줄 순서". 의존성을
  하나도 위반하지 않는 유효한 순서지만, 유일한 순서는 아니다.
- **`dependencies`**: 실제로 강제되는 제약. 병렬로 진행할지 판단할 때는
  ordinal이 아니라 이쪽을 봐야 한다.

처음에는 ordinal을 훅 파일 크기 순(checks → pre-commit → commit-msg →
post-commit)으로 매겼는데, 그러면 의존이 전혀 없는 commit-msg가 pre-commit
뒤에 오는 것처럼 보여 병렬 가능성이 가려졌다. 그래서 **의존이 없는 3건을
앞으로 당겨 재배치**했다.

## 의존 그래프

강제되는 사슬은 두 갈래뿐이다.

```
GF-108 (checks 5개) ──> GF-110 (pre-commit) ──> GF-111 (post-commit)
                                                          │
GF-109 (commit-msg) ────────────────────────────────────┤
                                                          v
                                              GF-112 (CI/문서 마무리)

GF-107 (거버넌스) ──> (GF-113의 install.sh 테스트 부분)
GF-110/11/12 ──────> (GF-113의 실행시점 PATH 테스트 부분)
```

| ordinal | 드래프트 | 마일스톤 | 선행 조건 |
|---|---|---|---|
| 1 | GF-107 거버넌스(decision + install.sh 가드) | m-4 | 없음 |
| 2 | GF-108 checks/*.sh → Python 5개 | m-3 | 없음 |
| 3 | GF-109 commit-msg → Python | m-3 | 없음 |
| 4 | GF-110 pre-commit → Python | m-3 | GF-108 |
| 5 | GF-111 post-commit → Python | m-3 | GF-110 |
| 6 | GF-112 ruff CI + readme 2종 + consistency.bats | m-3 | 9, 10, 11, 12 |
| 7 | GF-113 README 필요조건 + PATH 부재 bats | m-4 | 8, 10, 11, 12 |

## 동시에 착수할 수 있는 것

- **GF-107, GF-108, GF-109 세 건은 서로 의존이 없어 동시 착수 가능**하다.
  다만 GF-107(새 decision 기록)은 이 저장소 관례상 코드 변경보다 먼저
  커밋돼야 하므로, 실제로는 이것부터 끝내고 나머지를 여는 편이 안전하다.
- GF-108의 체크 스크립트 5개(python/ts/java/cpp/sql)는 서로 코드를 공유하지
  않아 **5개 자체도 완전 병렬**이다.
- GF-109(commit-msg)은 pre-commit이나 checks를 호출하지 않는 독립 로직이라
  GF-108/10과 나란히 진행해도 된다. ordinal이 3인 이유.
- GF-113는 **한 카드 안에서 착수 시점이 갈린다**. README 필요조건 문구는
  코드 상태와 무관해 언제든 쓸 수 있고, install.sh 부재 테스트는 GF-107
  이후면 가능하며, 실행 시점 PATH 부재 테스트는 해당 훅이 실제로 포팅된
  뒤에만 의미가 있다(10/11/12가 하나씩 끝날 때마다 그 훅 케이스부터 추가 가능).

## 순서를 지켜야 하는 이유 (놓치기 쉬운 것)

- **GF-108 → GF-110**: pre-commit 디스패처가 체크 스크립트를 파일명으로
  직접 참조한다. 그래서 GF-108에서 구 `.sh`를 지우기 전에 **아직 sh인
  pre-commit의 호출 경로를 `.py`로 먼저 갱신**해야 한다. 이 순서를 어기면
  GF-110이 끝나기 전까지 중간 커밋들에서 훅 체인이 깨진다.
- **GF-110 → GF-111**: 코드 의존은 없다. post-commit이 읽는
  `.gitformat-verified` 마커는 포맷 기반 계약이라 pre-commit이 sh든 Python이든
  상호운용된다. 다만 마커를 쓰는 쪽을 먼저 옮긴 뒤 읽는 쪽을 옮기는 편이
  문제 발생 시 원인 추적에 유리해 순차를 권장한다(강제 아님).
- **CI는 각 포팅 커밋에서 같이 손봐야 한다**: `.github/workflows/test.yml`의
  shellcheck 대상이 글롭이 아니라 파일명 직접 지정이라, pre-commit/commit-msg/
  post-commit이 Python이 되는 커밋에서 해당 파일명을 목록에서 빼지 않으면
  그 시점부터 CI가 Python 파일을 sh로 린트하려다 깨진다. 이 작업을 마지막
  마무리 단계로 미루면 안 된다.
- **GF-112은 마지막**: consistency.bats는 여러 파일에 걸친 바이트 동일성
  검사라 부분 상태에서는 의미가 없고, readme 2종도 최종 구조가 확정돼야
  정확히 쓸 수 있다. 단 ruff CI 스텝 추가만은 첫 `.py`가 생긴 뒤 아무 때나
  병렬로 넣어도 된다.
