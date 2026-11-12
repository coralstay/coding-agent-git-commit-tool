<!-- work-order-hash: e65fcc530d46c307387da246351b4bae8e1274badd8fe1e39ded9ad209ee7e0e -->
# 작업 순서

`work_order.py`가 backlog/tasks의 의존(`dependencies`)으로 만든 파일이다 — 직접 고치지 말고 다시 생성한다. 같은 단계의 태스크는 병렬로, 단계는 위에서 아래로 순차로 진행한다. Done 태스크와 없는 태스크에 대한 의존은 충족된 것으로 본다.

| 단계 | ID | 제목 |
|---|---|---|
| 1 | GF-130 | 에이전트 판정을 검증 가능한 신호로 재작성 |
| 1 | GF-131 | applypatch-msg 훅 신설 — git am 차단 |
| 1 | GF-132 | 설정 정리 — install.sh의 commit.template 제거와 .gitmessage 삭제 |
| 1 | GF-149 | install에 플러그인 선택 옵션 추가: source-header만 설치 |
| 1 | GF-150 | source-header 적용: coralstay-software-factory/components/coding-agent-git-commit-tool |
| 1 | GF-151 | pre-push 플러그인: 서명 없는 커밋과 수동 검증 게이트를 통과하지 못한 Done 카드의 push를 git 단계에서 거부 |
| 2 | GF-133 | 파일·디렉터리 이름을 역할이 드러나게 개칭 |
| 3 | GF-134 | README와 hooks/README.md를 새 구조로 재작성 |
