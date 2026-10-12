"""로케일이 UTF-8을 제공하지 않는 환경에서 훅이 한국어를 출력할 때의 동작을 본다.

구 robustness-locale.bats(GF-116, decision-16). sh 시절의 LC_ALL=C.UTF-8
하드코딩(GF-83)은 Python 전환으로 사라졌지만, 같은 위험이 "Python의 출력 인코딩"으로
옮겨왔다.

재현 조건: LC_ALL=C에 PYTHONCOERCECLOCALE=0(PEP 538 로케일 강제 변환 끄기) +
PYTHONUTF8=0(PEP 540 UTF-8 모드 끄기). musl/Alpine처럼 C.UTF-8이 없는 환경에서 Python이
ascii stdout으로 떨어지는 상태를 로컬에서 만들어내기 위한 것이다 — 실제 그런 컨테이너를
CI에 두지 않고도 같은 실패 모드를 고정할 수 있다.

폴백 전에는 checks/python.py의 "ruff/flake8을 찾을 수 없어 건너뜀"(무해해야 하는
경로!)에서 UnicodeEncodeError가 나 커밋이 트레이스백과 함께 막혔다. stdout은 기본
errors="strict"라 죽고, stderr은 기본 errors="backslashreplace"라 죽지는 않지만 한국어가
\\uXXXX 이스케이프로 깨져 읽을 수 없었다.

GF-135에서 언어별 검사가 제거되며 **stdout 경로를 재현할 수단이 없어졌다** — 남은 훅은
한국어를 stderr로만 출력한다(거부 메시지). 그래서 stdout 케이스는 지웠고, 아래
stderr 케이스들이 폴백을 고정한다. 훅의 UTF-8 preamble은 stdout도 함께 재설정한 채로
두는데, 이 저장소의 다른 공유 블록과 같이 훅 3개에 byte-identical하게 있어야 하는
블록이기 때문이다(decision-16).
"""

import unittest

from isolated_repo import IsolatedRepoTestCase

BROKEN_LOCALE = {"LC_ALL": "C", "PYTHONCOERCECLOCALE": "0", "PYTHONUTF8": "0"}


class NonUtf8LocaleTest(IsolatedRepoTestCase):
    def commit_with_broken_locale(self, message, **overrides):
        return self.commit(message, env={**BROKEN_LOCALE, **overrides})

    # ── 통과 경로: 죽지 않고 커밋이 통과한다 ────────────────────────

    def test_정상_커밋이_로케일_때문에_막히지_않는다(self):
        """[GF-116] 로케일이 UTF-8이 아니어도 정상 커밋이 트레이스백 없이 통과한다

        GF-135 전에는 이 자리에서 언어별 검사의 한국어 '건너뜀' 메시지(stdout)로
        인코딩 폴백을 확인했다. 검사가 사라져 그 메시지가 없어졌으므로, 이제는 훅
        전체를 태워도 인코딩 때문에 죽지 않는다는 사실만 본다.
        """
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")

        result = self.commit_with_broken_locale("[feat] non-utf8 locale must not block")

        self.assertAccepted(result)
        self.assertEqual(1, self.commit_count())
        self.assertNotIn("UnicodeEncodeError", result.output)
        self.assertNotIn("Traceback", result.output)

    # ── stderr 경로: 거부 메시지가 읽을 수 있는 한국어여야 한다 ─────

    def test_거부_메시지가_깨지지_않는다(self):
        """[GF-116] 로케일이 UTF-8이 아니어도 prepare-commit-msg 거부 메시지가 깨지지 않는다"""
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")

        result = self.commit_with_broken_locale("bad message format")

        self.assertRejected(result)
        # 폴백 전에는 이 메시지가 \uXXXX 이스케이프로 떨어져 이 단언이 실패했다 —
        # 읽을 수 있는 한국어와 일치한다는 것 자체가 "이스케이프되지 않았다"는 증명이다.
        self.assertIn("커밋 메시지가 [type][subsystem] 형식이 아닙니다", result.output)

    # ── 유니코드 길이 계산이 로케일과 무관해야 한다 ─────────────────

    def test_제목_길이를_코드포인트_단위로_센다(self):
        """[GF-116] 로케일이 UTF-8이 아니어도 제목 길이를 코드포인트 단위로 센다"""
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")

        # 한글 27자(67바이트) — 바이트로 셌다면 50자 제한에 걸려 거부된다(GF-83).
        result = self.commit_with_broken_locale(
            "[feat] 한글제목길이계산이로케일에영향받지않는다"
        )
        self.assertAccepted(result)
        self.assertEqual(1, self.commit_count())

    def test_50자를_넘는_한글_제목은_거부된다(self):
        """[GF-116] 로케일이 UTF-8이 아니어도 50자를 넘는 한글 제목은 거부된다"""
        self.write("a.txt", "hi\n")
        self.git_ok("add", "a.txt")

        # 14자×4 + "[feat] " = 63자. 3회 반복은 49자로 제한에 걸리지 않는다(실측).
        result = self.commit_with_broken_locale(
            "[feat] " + "가나다라마바사아자차카타파하" * 4
        )
        self.assertRejected(result)
        self.assertIn("제목이", result.output)
        # 첫 커밋이라 HEAD가 아직 없다 — 부재를 직접 본다.
        self.assertRejected(self.git("rev-parse", "--verify", "-q", "HEAD"))


if __name__ == "__main__":
    unittest.main()
