#!/bin/sh
# git-trail 설치 스크립트: 기존 저장소에 core.hooksPath와 commit.template을 설정하고
# (decision-2), 훅 실행에 필요한 python3 존재를 확인한다(decision-16). 이 스크립트가
# 위치한 git-trail 클론 자체를 훅 소스로 사용한다.
#
# 사용법:
#   /path/to/git-trail/install.sh [target-repo-dir]
# target-repo-dir을 생략하면 현재 디렉터리를 대상으로 한다.
set -eu

SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
readonly SELF_DIR
HOOKS_DIR="${SELF_DIR}/hooks"
readonly HOOKS_DIR
GITMESSAGE="${SELF_DIR}/.gitmessage"
readonly GITMESSAGE
TEMPLATE_DIR="${SELF_DIR}/template"
readonly TEMPLATE_DIR
CONF="${HOOKS_DIR}/gitformat.conf"
readonly CONF
# gitformat.conf 자체를 못 읽으면(파일 없음/문법 깨짐) 이후 모든 git config
# --file 읽기가 하나씩 실패하면서 원인을 알기 어려운 에러로 이어진다. 여기서
# 미리 검증해 원인을 명확히 알려준다. 이 블록은 CONF를 읽는 다른 파일들에도
# byte-identical하게 있다(tests/consistency.bats가 동일성을 보장).
if ! git config --file "$CONF" --list >/dev/null 2>&1; then
  echo "gitformat: gitformat.conf를 읽을 수 없습니다: ${CONF}" >&2
  exit 1
fi

# 훅은 Python으로 실행된다(decision-16). 여기서 막지 않으면 설정은 다 끝난
# 뒤 첫 커밋에서야 훅이 실행 실패로 깨져 원인을 찾기 어렵다.
if ! command -v python3 >/dev/null 2>&1; then
  echo "install.sh: python3을 찾을 수 없습니다 - git-trail 훅은 Python으로 실행됩니다." >&2
  exit 1
fi

GLOBAL_MODE="ask"
TARGET=""
for arg in "$@"; do
  case "$arg" in
    --global) GLOBAL_MODE="yes" ;;
    --no-global) GLOBAL_MODE="no" ;;
    -*) echo "install.sh: 알 수 없는 옵션: $arg" >&2; exit 1 ;;
    *) TARGET="$arg" ;;
  esac
done
TARGET="${TARGET:-$(pwd)}"
TARGET="$(cd "$TARGET" && pwd)"
readonly TARGET

if ! git -C "$TARGET" rev-parse --git-dir >/dev/null 2>&1; then
  echo "install.sh: ${TARGET}는 git 저장소가 아닙니다." >&2
  exit 1
fi

git -C "$TARGET" config core.hooksPath "$HOOKS_DIR"
git -C "$TARGET" config commit.template "$GITMESSAGE"

echo "git-trail: ${TARGET} 설정 완료"
echo "  core.hooksPath  = ${HOOKS_DIR}"
echo "  commit.template = ${GITMESSAGE}"

sync_template() {
  mkdir -p "${TEMPLATE_DIR}/hooks"
  for h in "${HOOKS_DIR}"/*; do
    [ -f "$h" ] || continue
    ln -sf "$h" "${TEMPLATE_DIR}/hooks/$(basename "$h")"
  done
  # hooks/에서 삭제된 파일에 대응하는 template/hooks/의 예전 심볼릭 링크를
  # 지운다. hooks/*가 줄어들면(예: GF-86의 hooks/pre-push 삭제) 위 루프는
  # 새로 만들 뿐 지우지 않으므로, 그대로 두면 대상 없는 깨진 심볼릭 링크가
  # 영구히 남는다. template/hooks/는 이 함수가 전적으로 관리하는 산출물
  # 디렉터리이고 심볼릭 링크만 들어있다는 불변조건이 있으므로(GF-9), 이름이
  # hooks/에 더 이상 대응하지 않는 심볼릭 링크는 안전하게 지울 수 있다.
  for link in "${TEMPLATE_DIR}"/hooks/*; do
    [ -L "$link" ] || continue
    name="$(basename "$link")"
    [ -f "${HOOKS_DIR}/${name}" ] && continue
    rm -f "$link"
  done
}

# 전역 init.templateDir(decision-2): 앞으로 git init/clone하는 모든 새 저장소에
# 자동으로 훅이 심어지게 한다. template/hooks/*는 이 클론 위치를 가리키는 절대경로
# 심볼릭 링크로 그때그때 생성한다(GF-9). --global/--no-global로 비대화형 지정 가능.
case "$GLOBAL_MODE" in
  yes)
    sync_template
    git config --global init.templateDir "$TEMPLATE_DIR"
    git config --global commit.template "$GITMESSAGE"
    echo "git-trail: 전역 init.templateDir/commit.template 설정 완료 (앞으로 만드는 새 저장소에 자동 적용)"
    ;;
  no)
    echo "git-trail: 전역 설정은 건너뜁니다."
    ;;
  ask)
    if [ -t 0 ]; then
      printf '전역(init.templateDir)도 설정해 앞으로 만드는 모든 새 저장소에 자동 적용할까요? [y/N] '
      read -r answer
      case "$answer" in
        y|Y|yes|YES)
          sync_template
          git config --global init.templateDir "$TEMPLATE_DIR"
          git config --global commit.template "$GITMESSAGE"
          echo "git-trail: 전역 init.templateDir/commit.template 설정 완료."
          ;;
        *)
          echo "git-trail: 전역 설정은 건너뜁니다. 나중에: ${SELF_DIR}/install.sh --global"
          ;;
      esac
    else
      echo "git-trail: 비대화형 환경이라 전역 설정은 건너뜁니다. --global로 자동 적용 가능."
    fi
    ;;
esac

echo "git-trail: 참고 - git push --no-verify는 로컬 훅으로 탐지할 수 없습니다."
echo "  push된 이력은 원격 설정이 지킵니다 - 대상 저장소의 원격(GitHub rulesets·병합 방식)을"
echo "  직접 구성하세요 (예시: git-trail 저장소의 backlog doc-20)."
