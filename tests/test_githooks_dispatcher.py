# GF-148: .githooks 공용 디스패처의 실행 순서·중단·건너뜀 동작
"""githooks/의 공용 디스패처 동작을 본다(decision-32).

디스패처(githooks/pre-commit, githooks/prepare-commit-msg)는 자기 이름에 `.d`를 붙인
디렉터리의 플러그인을 이름순으로 실행하고, 하나라도 실패하면 그 종료 코드로 멈춘다.
플러그인이 부르는 명령이 PATH에 없으면(sh의 exec 실패 = 종료 코드 127) 경고만 내고
건너뛴다 — 다른 머신에서 그 도구가 없다고 커밋이 막히면 안 되고, 강제는 CI가 맡는다.

진짜 githooks/는 건드리지 않는다 — 디스패처만 임시 디렉터리에 복사하고, 플러그인은
테스트마다 직접 만든다. 커밋을 태우지 않고 디스패처를 직접 실행한다(훅 인자 전달까지
여기서 본다). 실제 커밋 경로는 test_githooks_commit_format.py가 본다.
"""

import shutil
import unittest

from isolated_repo import GITHOOKS_TEMPLATE, IsolatedRepoTestCase

DISPATCHERS = ("pre-commit", "prepare-commit-msg")


class GithooksDispatcherTest(IsolatedRepoTestCase):
    def setUp(self):
        self.repo = self.make_repo(hooks_path=None)
        self.hooks = self.temp_dir(prefix="gitformat-githooks-")
        for name in DISPATCHERS:
            shutil.copy2(GITHOOKS_TEMPLATE / name, self.hooks / name)
        self.log = self.temp_dir(prefix="gitformat-log-") / "log"

    def plugin(self, hook, name, body, *, executable=True):
        """`<hook>.d/<name>`에 sh 플러그인을 만든다. 실행될 때 log에 자기 이름을 적는다."""
        directory = self.hooks / f"{hook}.d"
        directory.mkdir(exist_ok=True)
        path = directory / name
        path.write_text(
            f'#!/bin/sh\necho "{name} $*" >> "{self.log}"\n{body}\n', encoding="utf-8"
        )
        path.chmod(0o755 if executable else 0o644)
        return path

    def ran(self):
        if not self.log.exists():
            return []
        return self.log.read_text(encoding="utf-8").splitlines()

    def dispatch(self, hook, *args):
        return self.run_cmd([self.hooks / hook, *args])

    # == AC/DoD ==

    def test_플러그인을_이름순으로_실행한다(self):
        """GF-148#1 <hook>.d/*를 이름순으로 실행한다"""
        self.plugin("pre-commit", "30-c", "exit 0")
        self.plugin("pre-commit", "10-a", "exit 0")
        self.plugin("pre-commit", "20-b", "exit 0")
        self.assertAccepted(self.dispatch("pre-commit"))
        self.assertEqual(["10-a ", "20-b ", "30-c "], self.ran())

    def test_실패한_플러그인의_종료_코드로_멈춘다(self):
        """GF-148#1 플러그인이 실패하면 뒤 플러그인을 실행하지 않고 그 종료 코드로 끝난다"""
        self.plugin("pre-commit", "10-ok", "exit 0")
        self.plugin("pre-commit", "20-fail", "exit 3")
        self.plugin("pre-commit", "30-never", "exit 0")
        result = self.dispatch("pre-commit")
        self.assertEqual(3, result.returncode, str(result))
        self.assertEqual(["10-ok ", "20-fail "], self.ran())

    def test_명령이_없으면_경고하고_건너뛴다(self):
        """GF-148#1 플러그인이 부르는 명령이 PATH에 없으면 경고 후 다음 플러그인으로 간다"""
        self.plugin("pre-commit", "10-missing", "exec no-such-gitformat-tool hook")
        self.plugin("pre-commit", "20-ok", "exit 0")
        result = self.dispatch("pre-commit")
        self.assertAccepted(result)
        self.assertIn("10-missing", result.output)
        self.assertIn("건너뜁니다", result.output)
        self.assertEqual(["10-missing ", "20-ok "], self.ran())

    # == Coverage ==

    def test_두_디스패처는_같은_파일이다(self):
        """pre-commit과 prepare-commit-msg 디스패처는 내용이 같다(이름으로 .d를 고른다)"""
        self.assertEqual(
            (GITHOOKS_TEMPLATE / "pre-commit").read_bytes(),
            (GITHOOKS_TEMPLATE / "prepare-commit-msg").read_bytes(),
        )

    def test_훅_인자를_플러그인에_그대로_넘긴다(self):
        """prepare-commit-msg의 인자("$@")를 공백·빈 값까지 그대로 넘긴다"""
        self.plugin(
            "prepare-commit-msg",
            "10-args",
            f'for a in "$@"; do echo "[$a]" >> "{self.log}"; done',
        )
        self.assertAccepted(
            self.dispatch("prepare-commit-msg", "msg file", "message", "")
        )
        self.assertEqual(
            ["10-args msg file message ", "[msg file]", "[message]", "[]"], self.ran()
        )

    def test_실행_권한이_없는_플러그인은_경고하고_건너뛴다(self):
        """실행 권한이 없는 파일은 조용히 넘기지 않고 경고 후 건너뛴다"""
        self.plugin("pre-commit", "10-noexec", "exit 1", executable=False)
        self.plugin("pre-commit", "20-ok", "exit 0")
        result = self.dispatch("pre-commit")
        self.assertAccepted(result)
        self.assertIn("10-noexec", result.output)
        self.assertEqual(["20-ok "], self.ran())

    def test_플러그인_디렉터리가_없거나_비면_통과한다(self):
        """<hook>.d가 없거나 비어 있으면 아무것도 하지 않고 통과한다"""
        self.assertAccepted(self.dispatch("pre-commit"))
        (self.hooks / "pre-commit.d").mkdir()
        self.assertAccepted(self.dispatch("pre-commit"))
        self.assertEqual([], self.ran())

    def test_훅_디렉터리_안에서_상대경로로_불려도_자기_d를_찾는다(self):
        """$0이 상대경로여도 자기 옆의 .d를 찾는다"""
        self.plugin("pre-commit", "10-a", "exit 0")
        result = self.run_cmd(["./pre-commit"], cwd=self.hooks)
        self.assertAccepted(result)
        self.assertEqual(["10-a "], self.ran())


if __name__ == "__main__":
    unittest.main()
