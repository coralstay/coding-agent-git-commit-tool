"""gitformat.conf를 읽을 수 없을 때 각 파일이 즉시 멈추는지 본다(구 conf-guard.bats).

GF-76에서 CONF를 읽는 파일들에 "읽기 검증 가드"를 넣었고, GF-77에서 그 가드가 텍스트로
동일한지만 검증되던 것을 런타임 검증으로 바꿨다. conf가 깨진 상태에서 각 파일을 직접
실행해 exit 0이 아니고 명확한 에러 메시지가 나오는지 본다 — 빈 값으로 진행하면 원인을
알 수 없는 거부가 된다.

대상은 훅 2개와 install.sh다. GF-135에서 checks/가 삭제되며 그 3개 파일의 가드 검증
케이스도 함께 사라졌고, GF-127에서 commit-msg가 삭제되며 그 케이스도 사라졌다 — 검증할
파일 자체가 없어졌기 때문이지, 가드 정책이 바뀐 게 아니다.

진짜 저장소의 hooks/gitformat.conf는 절대 건드리지 않고, 매 테스트마다 hooks/를 임시
디렉터리에 복사해 그 사본의 conf만 깨뜨린다.
"""

import shutil
import unittest

from isolated_repo import (
    CONF_GUARD_MESSAGE,
    HOOKS_DIR,
    INSTALL_SH,
    IsolatedRepoTestCase,
)


class ConfigFileUnreadableTest(IsolatedRepoTestCase):
    def setUp(self):
        self.hooks_copy = self.copy_hooks()
        self.break_conf(self.hooks_copy)
        # 가드가 conf를 읽는 시점에 걸리는지만 보므로 core.hooksPath는 연결하지 않고
        # 각 파일을 직접 실행한다.
        self.repo = self.make_repo(hooks_path=None)

    def assertConfGuardFires(self, result):
        self.assertNotEqual(0, result.returncode, str(result))
        self.assertIn(CONF_GUARD_MESSAGE, result.output)

    def test_prepare_commit_msg가_멈춘다(self):
        """prepare-commit-msg(python): conf가 깨지면 명확한 에러로 즉시 멈춘다"""
        # GF-126에서 pre-commit이 삭제되며 가드 검증 대상이 이 훅으로 옮겨왔다.
        # GF-135에서 언어별 검사가 사라진 뒤에도 이 훅은 gitformat.markerFile을
        # conf에서 읽으므로 가드가 여전히 필요하다.
        msg_file = self.write("msgfile", "[feat] test\n")
        self.assertConfGuardFires(
            self.python(self.hooks_copy / "prepare-commit-msg", msg_file)
        )

    def test_post_commit이_멈춘다(self):
        """post-commit(python): conf가 깨지면 명확한 에러로 즉시 멈춘다"""
        self.assertConfGuardFires(self.python(self.hooks_copy / "post-commit"))

    def test_install_sh가_멈춘다(self):
        """install.sh: conf가 깨지면 명확한 에러로 즉시 멈춘다"""
        # install.sh는 자기 옆의 hooks/를 읽으므로 클론 구조를 그대로 흉내낸다.
        clone_copy = self.temp_dir(prefix="gitformat-clone-")
        shutil.copytree(HOOKS_DIR, clone_copy / "hooks")
        (clone_copy / "install.sh").write_bytes(INSTALL_SH.read_bytes())
        self.break_conf(clone_copy / "hooks")
        self.assertConfGuardFires(
            self.run_cmd(["sh", clone_copy / "install.sh", self.repo])
        )


if __name__ == "__main__":
    unittest.main()
