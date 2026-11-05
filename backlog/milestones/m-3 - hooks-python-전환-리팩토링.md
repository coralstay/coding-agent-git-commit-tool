---
id: m-3
title: "hooks Python 전환: 리팩토링"
---

## Description

python3이 정상 동작하는 환경에서 기존 POSIX sh 훅과 관찰 가능한 동작이 완전히 동일하도록 로직만 Python으로 옮기는 부분.

기존 bats 103개(블랙박스, 언어 무관)를 그대로 안전망으로 재사용해 동작 보존을 검증한다. 대상: hooks/checks/*.py 5개, hooks/pre-commit, hooks/commit-msg, hooks/post-commit, 그리고 이에 따른 CI/문서/테스트 경로 정리.
