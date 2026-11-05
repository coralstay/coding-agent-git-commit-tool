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
        path.write_text(
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
        self.assertEqual(["hook pre-commit"], self.calls())
        self.assertRejected(self.git("rev-parse", "--verify", "HEAD"))

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
        self.assertIn("건너뜁니다", result.output)

    # == Coverage ==

    def test_no_verify는_pre_commit_플러그인을_건너뛴다(self):
        """pre-commit 단계는 git 규칙대로 --no-verify로 건너뛰어진다(prepare-commit-msg는 아님)"""
        result = self.commit(
            "[feat] skip pre-commit", "--no-verify", env=self.fake_source_header(1)
        )
        self.assertAccepted(result)
        self.assertEqual([], self.calls())


if __name__ == "__main__":
    unittest.main()
