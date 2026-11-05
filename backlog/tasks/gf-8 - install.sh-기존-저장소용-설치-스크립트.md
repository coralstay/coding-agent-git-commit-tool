---
id: GF-8
title: install.sh (기존 저장소용 설치 스크립트)
status: Done
assignee: []
created_date: '2026-08-24 03:12'
updated_date: '2026-08-24 03:45'
labels: []
dependencies:
  - GF-7
type: task
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
core.hooksPath, commit.template 설정 자동화(decision-2)
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
install.sh 작성: core.hooksPath/commit.template을 대상 저장소에 설정하고, --global/--no-global 플래그 또는 TTY 프롬프트로 전역 init.templateDir도 선택 설정. fake HOME으로 실제 전역 설정을 건드리지 않고 양쪽 경로 검증.
<!-- SECTION:FINAL_SUMMARY:END -->
