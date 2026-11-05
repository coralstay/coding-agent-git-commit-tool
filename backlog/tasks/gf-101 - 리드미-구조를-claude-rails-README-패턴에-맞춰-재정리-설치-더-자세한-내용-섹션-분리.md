---
id: GF-101
title: 리드미 구조를 claude-rails README 패턴에 맞춰 재정리 (설치/더 자세한 내용 섹션 분리)
status: Done
assignee: []
created_date: '2026-09-19 12:50'
updated_date: '2026-09-19 12:56'
labels: []
dependencies: []
type: docs
ordinal: 98000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
사용자가 같은 훅 계열 저장소인 coralstay/claude-rails의 README를 참고 모델로 지정했다. claude-rails README 구조: 왜 필요했는지 / 무엇을 만들었는지 / 주요 특징 / 훅을 생애주기별로 정리 / 설치 방법 / "더 자세한 내용이 궁금하시다면"(backlog doc list/decision list/draft list/board로 안내하는 마무리 섹션). 특히 마지막 섹션이 git-format README에는 없다 - 지금은 "무엇을 만들었는가" 섹션 끝에 backlog/docs 링크 한 줄만 있다.

또한 사용자가 "토발즈니 뭐니 이런 내용 빼고 목차도 빼라"고 명시했다 - 확인 결과 GF-99에서 이미 리누스 토발즈 언급과 목차(📖 목차) 둘 다 제거된 상태다(README.md에 grep 결과 0건). 이번 작업에서 재작업 중 실수로 되살리지 않도록 확인만 하면 된다.

변경 범위: README.md의 "무엇을 만들었는가" 섹션에 섞여있던 설치 명령(기존 저장소 적용/--global)을 별도 "🚀 설치 방법" 섹션으로 분리하고, "무엇을 만들었는가" 끝의 backlog/docs 링크 한 줄과 라이선스 언급을 claude-rails 스타일의 별도 마무리 섹션("더 자세한 내용이 궁금하시다면" - backlog doc list/decision list/board를 각각 가리키는 불릿 목록)으로 확장한다. "훅 생애주기" 섹션 표 형식은 이미 claude-rails의 훅 생애주기 표 패턴과 유사하므로 구조는 유지하고 내용만 그대로 둔다. 톤(문체)은 claude-rails의 정중체("~드립니다")까지 맞추지 않고 git-format 기존 평문 문체를 유지한다 - 구조만 참고한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 README.md에 리누스 토발즈 언급과 목차(📖) 섹션이 없다(재작업 후에도 없음을 재확인)
- [x] #2 설치 명령(기존 저장소 적용 + --global)이 "🚀 설치 방법" 이름의 별도 섹션으로 분리된다
- [x] #3 README.md 끝에 claude-rails의 "더 자세한 내용이 궁금하시다면" 패턴과 유사한 마무리 섹션이 추가되어 backlog doc/decision/board 각각을 가리키는 불릿과 라이선스 한 줄을 담는다
- [x] #4 "왜 만들었는가"/"무엇을 만들었는가"/"훅 생애주기" 세 섹션의 기존 내용(에이전트 다중커밋 분석+사람이해 핵심문장, 훅 생애주기 표, AI귀속 트레일러 표)은 이번 재구성 후에도 그대로 보존된다
- [x] #5 shellcheck -s sh 전체와 bats tests/ 전체가 통과한다
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
무엇을 만들었는가에서 설치 명령을 분리해 새 설치 방법 섹션으로, 마지막 backlog/docs 한 줄을 claude-rails 스타일 마무리 섹션으로 확장. 왜/무엇을/훅생애주기 3개 섹션 본문은 그대로 유지.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
검증: (1) grep "토발즈\|목차" README.md -> 0건 (GF-99에서 이미 제거됨, 이번 재작업도 재도입 안 함). (2) 설치 명령이 새 "🚀 설치 방법" 섹션(96행)으로 분리됨. (3) 끝에 "📚 더 자세한 내용이 궁금하시다면" 섹션 추가 - backlog doc list/decision list/board 각각을 가리키는 불릿 + 라이선스 한 줄. (4) 왜/무엇을/훅 생애주기 세 섹션 본문(핵심 두 문장, 훅 생애주기 순서, AI귀속 트레일러 표, 사유 슬러그 6종)이 diff에서 그대로 유지됨을 확인. (5) shellcheck -s sh 전체 clean, bats tests/ 103/103 통과.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
같은 훅 계열 저장소 coralstay/claude-rails의 README 구조(왜/무엇을/훅 생애주기/설치/"더 자세한 내용이 궁금하시다면")를 참고해 git-format README를 5개 섹션으로 재정리했다. "무엇을 만들었는가"에 섞여있던 설치 명령을 별도 "설치 방법" 섹션으로 분리하고, 끝의 backlog/docs 링크 한 줄을 backlog doc list/decision list/board를 각각 가리키는 claude-rails 스타일 마무리 섹션으로 확장했다. 문체는 claude-rails의 정중체까지 맞추지 않고 git-format 기존 평문 문체를 유지했다. 리누스 토발즈 언급과 목차는 GF-99에서 이미 제거된 상태였고 이번 재작업에서도 없음을 재확인했다.

검증: shellcheck -s sh 전체 clean, bats tests/ 103/103 통과.
<!-- SECTION:FINAL_SUMMARY:END -->
