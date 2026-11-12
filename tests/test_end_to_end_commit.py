# ---
# title: test_end_to_end_commit
# description: 커밋 한 번이 훅 전체를 통과하는지 보는 최소 종단 간 테스트
# authors: [coralstay]
# license: AGPL-3.0-only
# status: draft
# created_date: '2026-11-06'
# updated_date: '2026-11-06'
# ---
"""커밋 한 번이 훅 전체를 통과하는지 보는 최소 확인(구 smoke.bats, GF-21).

세부 동작은 각 동작별 테스트 파일이 따로 검증한다 — 여기서는 하네스와 훅 연결
자체가 살아 있는지만 본다.
"""

import unittest

from isolated_repo import GITFORMAT_ROOT, IsolatedRepoTestCase


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
        self.assertRejected(self.commit("이상한 메시지"))  # ---- 1

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
        self.assertNotIn("ruff", result.output)  # ---- 2

    def test_심볼릭_링크로_연결된_훅도_자기_설정을_찾는다(self):
        """[GF-16 회귀] .git/hooks/의 심볼릭 링크로 연결된 훅도 자기 위치를 찾는다

        훅은 .git/hooks/에 놓인 심볼릭 링크가 아니라 링크가 가리키는 실제 위치를
        기준으로 gitformat.conf를 찾아야 한다(GF-16) — realpath가 그 일을 한다.
        realpath가 빠지면 conf를 못 찾아 훅 앞부분의 읽기 가드가 커밋을 거부한다.

        이 링크를 심던 install.sh --global(init.templateDir)은 GF-148(decision-32)에서
        없앴다. 그래도 예전에 전역 templateDir을 설정한 머신에서는 새 저장소마다 같은
        링크가 계속 심어지고 훅도 그대로 돌므로, 링크를 직접 만들어 회귀를 고정한다.
        """
        new_repo = self.temp_dir()
        self.make_repo(path=new_repo, hooks_path=None)
        linked_hook = new_repo / ".git" / "hooks" / "prepare-commit-msg"
        linked_hook.symlink_to(GITFORMAT_ROOT / "hooks" / "prepare-commit-msg")  # ---- 3

        self.write("a.txt", "hi\n", cwd=new_repo)
        self.git_ok("add", "a.txt", cwd=new_repo)
        result = self.commit("[feat] via symlinked hooks", cwd=new_repo)

        self.assertAccepted(result)
        self.assertNotIn("gitformat.conf를 읽을 수 없습니다", result.output)  # ---- 4
        self.assertTrailerCount(self.head_message(cwd=new_repo), "Hooks-Commit:", 1)  # ---- 5

if __name__ == "__main__":
    unittest.main()


# ======== 노트 ========
# 1 형식 위반 메시지는 거부
#   설명: 하네스와 훅 연결이 살아 있다면 형식에 안 맞는 메시지는 거부돼야 한다. 통과만 보는 테스트는 훅이 연결되지 않아도 통과하므로 거부 쪽을 함께 본다.
#   개념: 스모크 테스트
# 2 언어 검사 도구가 되살아나지 않음을 고정
#   설명: GF-135 전에는 pyproject.toml이 있는 저장소의 import os(F401)가 ruff에 걸려 커밋이 막혔다. 지금은 언어 도구를 전혀 실행하지
#   않는다(decision-23). 이 단언이 없으면 lint가 슬그머니 돌아와도 스위트가 똑같이 통과한다.
#   관련: GF-135, decision-23
#   개념: 회귀 방지
# 3 예전 방식의 심볼릭 링크 훅을 직접 만들어 재현
#   설명: 훅은 .git/hooks/의 링크가 아니라 링크가 가리키는 실제 위치를 기준으로 gitformat.conf를 찾아야 한다(GF-16, realpath).
#   링크를 심던 install.sh --global은 GF-148에서 없앴지만, 예전에 전역 templateDir을 설정한 머신에서는 새 저장소마다 같은 링크가 계속
#   심어지므로 회귀를 고정한다.
#   관련: GF-16, GF-148, decision-32
#   개념: realpath
# 4 conf를 못 찾았다면 읽기 가드가 커밋을 막았을 것
#   설명: realpath가 빠지면 conf를 못 찾아 훅 앞부분의 읽기 가드가 이 메시지를 내고 커밋을 거부한다. 가드 메시지가 없어야 위치 해석이 맞다는 뜻이다.
#   관련: tests/test_config_file_unreadable.py
# 5 트레일러가 실제로 붙었는지까지 확인
#   설명: 종료 코드만 보면 훅이 아예 실행되지 않은 경우에도 똑같이 통과한다. conf에서 읽은 트레일러 키(Hooks-Commit)가 실제로 붙었는지 보아야 훅이
#   돌았다는 증거가 된다.
#   개념: 공허한 통과 방지
