---
id: GF-75
title: README 영어판 추가
status: Done
assignee: []
created_date: '2026-08-28 09:29'
updated_date: '2026-08-28 09:36'
labels: []
dependencies:
  - GF-74
ordinal: 73000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
지금 README.md는 한국어만 제공한다. 영어를 쓰는 사용자도 프로젝트 목적/설치/커스터마이즈를 이해할 수 있도록 영어판을 추가한다. 두 언어 버전이 서로 다른 내용을 말하게 되면 문서 정합성 문제가 생기므로, 번역은 정합성 감사(문서 정합성 감사 태스크) 이후에 최종 한국어 내용을 기준으로 진행한다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 README.md 상단(또는 별도 README.en.md)에서 한국어/영어 버전을 서로 오갈 수 있는 링크가 있다
- [x] #2 영어판이 한국어판과 동일한 섹션 구성과 내용을 담는다
- [x] #3 영어판의 커맨드/경로/설정 키 등 코드 관련 내용이 실제 코드와 일치한다
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
README.en.md 신설(별도 파일 방식). README.md/README.en.md 상단에 서로를 가리키는 언어 전환 링크 추가. 섹션 구성/표/불릿을 1:1 대응으로 번역, 코드 관련 내용(설정 키, 트레일러 이름, 마커 파일, 기본값)은 실제 hooks/*, gitformat.conf와 대조하며 작성. 이모지 코드포인트를 한/영 헤더 간 python으로 비교해 TOC 앵커가 깨지지 않음을 확인. 완료 후 별도 서브에이전트(일반 목적, 이 세션 컨텍스트 공유 안 함)를 띄워 코드 대비 정확성 + 한/영 내용 일치 + 앵커 + 문체를 독립적으로 재검증 - 결함 없음으로 확인됨.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
README.en.md를 신설해 한/영 언어 전환 링크를 양쪽에 추가했다. 코드 대비 정확성과 한/영 내용 일치를 독립 서브에이전트로 재검증해 결함 없음을 확인.
<!-- SECTION:FINAL_SUMMARY:END -->
