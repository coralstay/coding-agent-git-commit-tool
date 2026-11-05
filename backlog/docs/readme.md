# docs

**무엇인가**: 태스크나 의사결정으로 분류하기엔 애매한 참고 문서(레퍼런스, 가이드)를
담는다. 현재 doc-1부터 doc-8까지 8건이 있으며, 서브폴더 없이 평평한 구조를 유지한다.
대부분은 GF-99가 README.md를 3섹션으로 크게 줄이면서 빠진 상세 내용(설치 가이드,
커밋 메시지 규칙 상세, AI 귀속 트레일러 레퍼런스, 커스터마이즈 가이드, 저장소 구조,
주의점과 한계, 실사용 예시 워크스루)을 정보 손실 없이 옮겨 담은 것이고, doc-8은
`backlog/decisions/`의 대체(supersede) 체인을 정리한 지도 문서다.

**언제 쓰나**: README를 짧게 유지하면서도 상세 정보를 잃지 않아야 할 때, 또는
`backlog/` 구조 자체처럼 여러 곳에 흩어진 사실을 한 곳에 정리해야 할 때 새 doc을
만든다. 같은 주제를 다시 손볼 때는 새 doc을 만들지 않고 기존 doc을
`backlog doc update`로 갱신한다.

**관련 명령**:

- `backlog doc create "title" -t guide` — 새 문서 생성
- `backlog doc update doc-N --content "..."` — 문서 내용 갱신(전체 교체)
- `backlog doc view doc-N --plain` — 문서 내용 조회
- `backlog doc list` — 전체 문서 목록 조회
