"""커밋 한 번이 훅 전체를 통과하는지 보는 최소 확인(구 smoke.bats, GF-21).

세부 동작은 각 동작별 테스트 파일이 따로 검증한다 — 여기서는 하네스와 훅 연결
자체가 살아 있는지만 본다.
"""

import unittest

from isolated_repo import GITFORMAT_ROOT, INSTALL_SH, IsolatedRepoTestCase


class EndToEndCommitTest(IsolatedRepoTestCase):
    def test_형식에_맞는_커밋은_통과한다(self):
        """[type][subsystem] 형식의 커밋은 통과한다"""
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")
        self.assertAccepted(self.commit("[feat] smoke test"))

    def test_형식에_안_맞는_커밋_메시지는_거부된다(self):
        """형식에 안 맞는 커밋 메시지는 거부된다"""
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")
        self.assertRejected(self.commit("이상한 메시지"))

    def test_언어_도구가_거부할_파일도_커밋이_통과한다(self):
        """[GF-135] 언어별 검사가 제거돼 ruff가 거부할 파일도 커밋을 막지 않는다

        GF-135 전에는 pyproject.toml이 있는 저장소의 `import os`(F401)가
        checks/python.py의 ruff에 걸려 커밋이 막혔다. 지금은 coding-agent-git-commit-tool이 언어
        도구를 전혀 실행하지 않는다(decision-23) — 이 단언이 없으면 lint가 슬그머니
        돌아와도 스위트가 똑같이 통과한다.
        """
        self.write("pyproject.toml", "")
        self.write("unused.py", "import os\n")
        self.git_ok("add", "pyproject.toml", "unused.py")

        result = self.commit("[feat][py] unused import must not block")

        self.assertAccepted(result)
        self.assertEqual(1, self.commit_count())
        self.assertNotIn("ruff", result.output)

    def test_template_심볼릭_링크_설치에서도_훅이_자기_설정을_찾는다(self):
        """[GF-16 회귀] template/ 심볼릭 링크로 설치된 저장소에서도 훅이 자기 위치를 찾는다

        훅은 .git/hooks/에 놓인 심볼릭 링크가 아니라 링크가 가리키는 실제 위치를
        기준으로 gitformat.conf를 찾아야 한다(GF-16) — realpath가 그 일을 한다.
        realpath가 빠지면 conf를 못 찾아 각 훅 앞부분의 읽기 가드가 커밋을 거부한다.

        이 회귀는 GF-135까지 test_lint_dispatch.py가 "심볼릭 링크 설치에서도 checks/를
        찾는다"로 고정하고 있었다. checks/가 삭제됐어도 realpath가 필요한 이유(conf)는
        그대로 남으므로, 단언을 conf 기준으로 바꿔 이 파일로 옮겨왔다.
        """
        # 이 테스트만 HOME을 가짜 디렉터리로 바꾼다. 러너의 HOME은 그대로이므로
        # asdf 버전 해석(isolated_repo.asdf_pins)은 영향을 받지 않는다.
        fake_home = self.fake_home()
        env = {"HOME": str(fake_home)}

        # --global은 전역 설정만 하는 플래그가 아니다 — install.sh는 타깃(기본값
        # CWD)에 대한 로컬 설치도 함께 수행하므로 격리된 타깃을 명시한다(GF-123).
        self.run_cmd_ok([INSTALL_SH, "--global", self.repo], env=env)

        new_repo = self.temp_dir()
        self.make_repo(path=new_repo, hooks_path=None, env=env)

        # init.templateDir이 .git/hooks/*를 coding-agent-git-commit-tool 클론을 가리키는 심볼릭 링크로
        # 채웠는지부터 확인한다 — 이게 아니면 GF-16 시나리오 자체가 재현 안 된다.
        linked_hook = new_repo / ".git" / "hooks" / "prepare-commit-msg"
        self.assertTrue(
            linked_hook.is_symlink(), f"{linked_hook}가 심볼릭 링크가 아니다"
        )
        self.assertEqual(
            str(GITFORMAT_ROOT / "hooks" / "prepare-commit-msg"),
            str(linked_hook.readlink()),
        )

        self.write("a.txt", "hi\n", cwd=new_repo)
        self.git_ok("add", "a.txt", cwd=new_repo, env=env)
        result = self.commit("[feat] via symlinked hooks", cwd=new_repo, env=env)

        self.assertAccepted(result)
        # conf를 못 찾았다면 읽기 가드가 이 메시지를 내고 커밋을 막았을 것이다.
        self.assertNotIn("gitformat.conf를 읽을 수 없습니다", result.output)
        # conf에서 읽은 트레일러 키가 실제로 붙었는지까지 본다 — 종료 코드만 보면
        # 훅이 아예 실행되지 않은 경우에도 똑같이 통과한다.
        self.assertTrailerCount(
            self.head_message(cwd=new_repo, env=env), "Hooks-Commit:", 1
        )


if __name__ == "__main__":
    unittest.main()
