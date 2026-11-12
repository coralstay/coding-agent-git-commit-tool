# ---
# title: test_githooks_source_header
# description: 20-source-header 플러그인이 source-header hook pre-commit을 호출하는 연결을 검증하는 테스트
# authors: [coralstay]
# license: AGPL-3.0-only
# status: draft
# created_date: '2026-11-06'
# updated_date: '2026-11-06'
# ---
# GF-148: pre-commit.d/20-source-header 플러그인이 source-header hook pre-commit을 부름
"""pre-commit.d/20-source-header 플러그인을 실제 커밋으로 본다(decision-32).

source-header(dev-tools/source-header)의 규칙 자체는 그 저장소의 몫이다 — 여기서는
"플러그인이 `source-header hook pre-commit`을 부르고, 그 결과로 커밋이 막히거나
통과하며, 명령이 없으면 건너뛴다"는 연결만 본다. 그래서 진짜 source-header 대신 인자를
기록하고 정해진 코드로 끝나는 가짜 명령을 PATH에 세운다. 진짜 명령과의 연결은 DoD의
실측(임시 저장소 E2E)이 맡는다.
"""

import unittest

from isolated_repo import INSTALL_SH, IsolatedRepoTestCase


class GithooksSourceHeaderTest(IsolatedRepoTestCase):
    def setUp(self):
        self.repo = self.make_repo(hooks_path=None)
        self.git_ok("config", "core.hooksPath", self.githooks_copy())
        self.log = self.temp_dir(prefix="gitformat-log-") / "log"
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")

    def fake_source_header(self, exit_code):
        path = self.temp_dir(prefix="gitformat-fake-") / "source-header"
        path.write_text(  # ---- 1
            f'#!/bin/sh\necho "$*" >> "{self.log}"\n'
            f'echo "fake source-header" >&2\nexit {exit_code}\n',
            encoding="utf-8",
        )
        path.chmod(0o755)
        return {
            "PATH": self.path_with_tools(
                source_header=path, git_commit_tool=INSTALL_SH
            )
        }

    def calls(self):
        if not self.log.exists():
            return []
        return self.log.read_text(encoding="utf-8").splitlines()

    # == AC/DoD ==

    def test_source_header_hook_pre_commit을_부르고_실패하면_커밋을_막는다(self):
        """GF-148#4 플러그인이 source-header hook pre-commit을 부르고, 실패하면 커밋이 막힌다"""
        result = self.commit("[feat] blocked by header", env=self.fake_source_header(1))
        self.assertRejected(result)
        self.assertEqual(["hook pre-commit"], self.calls())  # ---- 2
        self.assertRejected(self.git("rev-parse", "--verify", "HEAD"))  # ---- 3

    def test_source_header가_통과하면_커밋된다(self):
        """GF-148#4 source-header가 0으로 끝나면 커밋 형식 검사까지 거쳐 커밋된다"""
        result = self.commit("[feat] header ok", env=self.fake_source_header(0))
        self.assertAccepted(result)
        self.assertEqual(["hook pre-commit"], self.calls())
        self.assertTrailerCount(self.head_message(), "Hooks-Commit:", 1)

    def test_source_header가_없으면_경고하고_건너뛴다(self):
        """GF-148#4 source-header가 PATH에 없으면 경고 후 건너뛰고 커밋은 진행된다"""
        shadow = self.path_without("source-header")
        env = {"PATH": self.path_with_tools(shadow, git_commit_tool=INSTALL_SH)}
        result = self.commit("[feat] no source-header here", env=env)
        self.assertAccepted(result)
        self.assertIn("20-source-header", result.output)
        self.assertIn("건너뜁니다", result.output)  # ---- 4

    # == Coverage ==

    def test_no_verify는_pre_commit_플러그인을_건너뛴다(self):
        """pre-commit 단계는 git 규칙대로 --no-verify로 건너뛰어진다(prepare-commit-msg는 아님)"""
        result = self.commit(
            "[feat] skip pre-commit", "--no-verify", env=self.fake_source_header(1)
        )
        self.assertAccepted(result)
        self.assertEqual([], self.calls())  # ---- 5


if __name__ == "__main__":
    unittest.main()


# ======== 노트 ========
# 1 진짜 source-header 대신 가짜 명령을 세움
#   설명: 규칙 자체는 dev-tools/source-header 저장소의 몫이다. 여기서는 플러그인이 source-header hook pre-commit을 부르고 그
#   결과로 커밋이 막히거나 통과하는 연결만 본다. 가짜 명령은 인자를 기록하고 정해진 코드로 끝난다.
#   관련: decision-32
#   개념: 연결 테스트(계약 테스트)
# 2 인자가 정확히 hook pre-commit
#   설명: 플러그인이 부르는 인자 목록을 그대로 고정한다. 이 호출 형식이 바뀌면 도구 쪽과 어긋난다.
#   관련: GF-148#4
# 3 실패하면 커밋 객체가 생기지 않는다
#   설명: source-header가 1로 끝나면 pre-commit이 커밋을 막는다. HEAD가 만들어지지 않았음까지 확인한다.
#   관련: GF-148#4
#   개념: fail-closed
# 4 도구가 없으면 경고 후 건너뜀
#   설명: source-header가 PATH에 없는 머신에서 커밋을 막지 않는다. 경고에 20-source-header가 나와야 무엇을 건너뛰었는지 안다.
#   관련: GF-148#4
#   개념: fail-open(의도된)
# 5 --no-verify는 pre-commit 플러그인을 건너뜀
#   설명: pre-commit은 git 규칙대로 --no-verify로 건너뛰어진다. 건너뛰어도 되는 검사(헤더)와 건너뛸 수 없는
#   검사(prepare-commit-msg의 커밋 형식)가 다르다는 점을 고정한다.
#   관련: decision-18, tests/test_githooks_commit_format.py
