---
id: GF-100
title: 백로그 문서(backlog/docs) 채우기 + decision 이력 지도 작성
status: Done
assignee:
  - '@coralstay'
created_date: '2026-09-19 05:17'
updated_date: '2026-09-19 09:38'
labels: []
dependencies:
  - GF-99
type: docs
ordinal: 97000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GF-99가 README.md를 3섹션(왜/무엇을/훅 생애주기)으로 대폭 줄이면서 기존에 있던 세부 내용(설치 상세, 커밋 메시지 규칙 전문, AI 귀속 트레일러 표 전체, 커스터마이즈, 저장소 구조, 주의점/한계 전문, 실사용 예시 워크스루)이 빠진다. 정보를 잃지 않으려면 이 내용을 backlog/docs로 이관해야 한다 - 지금 backlog/docs는 완전히 비어있다(backlog doc list -> "No docs found.").

추가로 사용자가 "backlog 디렉토리에 뭐가 중복되어있는지 모르겠다"고 피드백했다. 조사 결과 진짜 중복 파일은 없고(backlog doctor 클린), 헷갈리는 원인은: (1) tasks/completed/archive가 서로 다른 라이프사이클 단계(활성/오래된 완료/도중 폐기)를 나타내는 의도된 구조라는 게 안 보이는 것, (2) decision 파일들의 대체(supersede) 체인이 backlog decision list 상태 표시(항상 accepted)로는 안 보이고 각 파일 본문에만 산문으로 적혀있는 것(decision-1->10, decision-3의 5번항목->11, decision-11의 pre-push판단->12, decision-9<->13<->14, decision-7->8, decision-5는 본문 내 Amendment로 갱신). 이걸 명확히 보여주는 지도 문서가 필요하다.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 설치 가이드, 커밋 메시지 규칙 상세, AI 귀속 트레일러 레퍼런스, 커스터마이즈 가이드, 저장소 구조, 주의점과 한계, 실사용 예시 워크스루 - 7개 backlog document가 생성되고 README에서 빠진 원문 정보를 요약 없이 그대로 담는다
- [x] #2 "decision 이력 지도" backlog document가 생성되어 decision 15개 전부를 다루고, 대체 체인이 있는 6개 주제(커밋스타일/서버검증범위/pre-push/vendoring/견고성테스트/AI귀속)를 표로 명시하며, tasks/completed/archive 디렉터리 구분(라이프사이클 단계이지 중복 아님)을 설명한다
- [x] #3 README.md의 "무엇을 만들었는가" 또는 "훅 생애주기" 섹션 끝에 backlog/docs의 관련 문서로 가는 링크가 최소 하나 있다
- [x] #4 backlog doctor가 새 문서 추가 후에도 클린하다(중복 ID 없음)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. 7개 backlog doc 생성(guide 타입): 설치 가이드/커밋 메시지 규칙 상세/AI 귀속 트레일러 레퍼런스/커스터마이즈 가이드/저장소 구조/주의점과 한계/실사용 예시 워크스루 - GF-99 이전 README(git show 11e874a:README.md) 원문을 요약 없이 그대로 옮김
2. decision 이력 지도 doc 신규 작성 - decision 15개 전부 커버, 대체체인 6개 표, tasks/completed/archive 라이프사이클 설명
3. README.md에 backlog/docs 링크 한 줄 추가(무엇을 만들었는가 또는 훅 생애주기 섹션 끝)
4. backlog doctor로 중복 ID 없음 확인
5. shellcheck+bats 재확인
6. AC 4개 검증 후 Done
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
검증 근거: (1) doc-1~doc-7이 backlog doc list에 존재하고 원문 README 세부내용을 요약 없이 그대로 담고 있음을 직접 대조 확인(특히 doc-3 AI귀속표, doc-6의 비-Claude-Code 8개 도구 나열 전체 보존 확인). (2) 검증 중 doc-1/doc-6/doc-7이 옛 README 앵커(#-커밋-메시지-규칙 등)를 가리키는 죽은 링크를 그대로 갖고 있는 걸 발견해 backlog doc update로 수정(다른 doc-N 참조 또는 README 훅 생애주기 섹션 참조로 교체). (3) doc-8 decision 이력 지도의 6개 대체 체인 주장을 실제 decision-11/decision-6 파일 원문과 대조해 정확함을 확인. 15개 decision 전부(standalone 3개 포함) 계정. tasks/completed/archive 디렉터리 구분과 GF-42 폐기 경위도 설명. (4) README.md "무엇을 만들었는가" 섹션 끝에 backlog/docs 링크 추가 확인(grep). (5) backlog doctor 클린, shellcheck -s sh 전체 clean, bats tests/ 103/103 통과 재확인.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
README.md에서 GF-99가 들어낸 7개 영역(설치/커밋규칙/AI귀속/커스터마이즈/저장소구조/주의점한계/실사용예시)을 backlog doc 7개(doc-1~doc-7)로 원문 그대로 이관했다. 추가로 "backlog 디렉토리가 헷갈린다"는 피드백에 답하기 위해 decision 이력 지도(doc-8)를 작성 - 15개 decision의 대체(supersede) 체인 6개를 실제 파일 원문 대조로 검증해 표로 정리하고, tasks/completed/archive 디렉터리가 중복이 아니라 서로 다른 라이프사이클 단계임을 설명했다. README.md에 backlog/docs로 가는 링크를 추가했다.

검증 중 이관된 문서 3개(doc-1/6/7)에 원래 README 앵커를 가리키던 죽은 링크가 남아있던 걸 발견해 다른 backlog doc/README 섹션을 가리키도록 수정했다.

검증: backlog doctor 클린, shellcheck -s sh 전체 clean, bats tests/ 103/103 통과.
<!-- SECTION:FINAL_SUMMARY:END -->
