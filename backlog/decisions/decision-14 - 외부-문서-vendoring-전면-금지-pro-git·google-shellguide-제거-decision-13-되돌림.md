---
id: decision-14
title: '외부 문서 vendoring 전면 금지: pro-git·google-shellguide 제거, decision-13 되돌림'
date: '2026-09-03 12:15'
status: accepted
---
## Context

decision-13은 셸 스타일 가이드 판단을 위해 외부 문서(Google Shell Style
Guide)를 vendoring하도록 decision-9의 금지 조항을 대체했다. 이 작업 직후
사용자가 라이선스 리스크를 다시 검토했다: `docs/references/pro-git/`는
CC BY-NC-SA 3.0(비영리)이라 저장소 전체의 MIT 라이선스와 레이어가 다르고
(GF-67에서 이미 이 위험을 인지해 LICENSE/README에 경고 고지를 추가하는
방식으로 완화했었다), 이번에 새로 추가한 `docs/references/google-shellguide/`도
CC BY 3.0으로 별도 라이선스 레이어를 만든다. 사용자는 "경고 고지로
완화"가 아니라 "애초에 라이선스가 다른 외부 콘텐츠를 저장소에 담지 않는다"는
방향으로 판단을 바꿨다 — 이 저장소 전체가 단일 라이선스(MIT)로 깔끔하게
유지되는 게 vendoring의 편의보다 중요하다는 결론이다.

## Decision

- `docs/references/pro-git/`(CC BY-NC-SA 3.0, GF-29에서 vendoring, GF-67에서
  라이선스 고지 보강)를 저장소에서 완전히 삭제한다.
- `docs/references/google-shellguide/`(CC BY 3.0, decision-13/GF-87에서
  vendoring)를 저장소에서 완전히 삭제한다.
- decision-13("외부 셸 스타일 가이드 vendoring 허용")을 대체한다 —
  decision-9의 원래 조항("외부 자료 원문을 vendoring하지 않고 출처 URL도
  남기지 않는다. 규칙만 참고해 적용한다")이 다시 유효하다.
- 최상위 `LICENSE` 파일의 pro-git 예외 고지, README.md/README.en.md의
  라이선스 섹션·저장소 구조 트리·훅 관련 언급에서 pro-git/google-shellguide
  vendoring 흔적을 모두 제거한다.
- `docs/references/conventional-commits-ko.md`는 예외로 유지한다 — 원문을
  그대로 옮긴 vendoring이 아니라 Conventional Commits 스펙 내용을 요약·번역해
  새로 쓴 문서이고, 별도 라이선스를 명시하지도 않는다. 이후 코드 스타일 판단이
  필요하면 외부 문서를 저장소에 담지 않고 매번 다시 조회해 규칙만 뽑아
  적용한다(decision-9 원칙으로 복귀).

## Consequences

- git-format 저장소는 다시 단일 라이선스(MIT)로 통일된다 — 별도 라이선스
  레이어를 문서화/추적할 필요가 없어진다.
- Pro Git 원문(Git Hooks, Git Internals 등)과 Google Shell Style Guide
  원문을 오프라인에서 직접 대조하며 참고하던 편의는 사라진다 — 필요할 때마다
  다시 조회해야 한다.
- hooks/commit-msg의 함수 분해(GF-87)는 이 vendoring과 무관하게 유지한다 —
  POSIX 문법 안에서의 함수 분해 자체는 decision-9의 "bash 전용 문법 금지"
  범위 밖이라 이 decision의 영향을 받지 않는다. 다만 코드 주석에 남긴
  "Google Shell Style Guide 참조 — decision-13" 같은 출처 언급은 제거한다.

