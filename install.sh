#!/bin/sh
# coding-agent-git-commit-tool 설치 스크립트(~/githubs/bin에서는 `git-commit-tool`).
# 대상 저장소에 커밋되는 .githooks/(공용 디스패처 + 플러그인)를 만들고
# core.hooksPath=.githooks와 commit.template을 설정한다(decision-32, decision-2 대체).
# 훅 실행에 필요한 python3 존재도 확인한다(decision-16). 실제 훅 로직은 이 스크립트가
# 위치한 클론의 hooks/에 있고, .githooks의 플러그인은 `git-commit-tool hook ...`으로
# 그 로직을 부른다.
#
# 사용법:
#   git-commit-tool [install] [target-repo-dir]   .githooks 설치(기본 동작)
#   git-commit-tool migrate [target-repo-dir]     옛 설치(hooksPath=클론의 hooks/)를 .githooks로
#   git-commit-tool hook <훅 이름> [훅 인자...]    .githooks 플러그인이 부르는 진입점
# target-repo-dir을 생략하면 현재 디렉터리를 대상으로 한다.
set -eu

_SRC="$0"
while [ -h "$_SRC" ]; do
  _DIR="$(cd -P "$(dirname "$_SRC")" && pwd)"
  _SRC="$(readlink "$_SRC")"
  case "$_SRC" in
    /*) ;;
    *) _SRC="$_DIR/$_SRC" ;;
  esac
done
SELF_DIR="$(cd -P "$(dirname "$_SRC")" && pwd)"
readonly SELF_DIR
HOOKS_DIR="${SELF_DIR}/hooks"
readonly HOOKS_DIR
GITMESSAGE="${SELF_DIR}/.gitmessage"
readonly GITMESSAGE
GITHOOKS_TEMPLATE="${SELF_DIR}/githooks"
readonly GITHOOKS_TEMPLATE
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
  echo "install.sh: python3을 찾을 수 없습니다 - coding-agent-git-commit-tool 훅은 Python으로 실행됩니다." >&2
  exit 1
fi

# `hook <이름> [인자...]`: 대상 저장소 .githooks/의 플러그인이 부르는 진입점
# (GF-148, decision-32). prepare-commit-msg.d/10-commit-format이 한 줄로
# `exec git-commit-tool hook prepare-commit-msg "$@"`를 부르면 여기서 이 클론의
# hooks/prepare-commit-msg를 절대경로로 exec한다. 훅은 realpath(__file__)로 자기
# 위치를 찾으므로 gitformat.conf와 Hooks-Commit(이 클론의 HEAD)이 옛 설치와 똑같이
# 이 클론 기준으로 해석된다. 훅 로직은 바꾸지 않는다.
#
# 위의 conf·python3 가드보다 뒤에 둔다 — python3가 없으면 여기서 exit 1로 커밋을
# 막는다. 가드보다 앞에서 exec하면 env가 127을 내고, 디스패처는 127을 "명령 없음"으로
# 보고 검사를 건너뛰므로 python3 부재가 조용한 통과로 바뀐다.
if [ "${1:-}" = "hook" ]; then
  shift
  case "${1:-}" in
    prepare-commit-msg)
      shift
      exec "${HOOKS_DIR}/prepare-commit-msg" "$@"
      ;;
    *)
      echo "git-commit-tool hook: 지원하지 않는 훅입니다: ${1:-(없음)} (지원: prepare-commit-msg)" >&2
      exit 1
      ;;
  esac
fi

usage() {
  echo "사용법 (Usage): git-commit-tool [install] [target-repo-dir]"
  echo "                git-commit-tool migrate [target-repo-dir]"
  echo "                git-commit-tool hook prepare-commit-msg <훅 인자...>"
  echo "  install  지정한 git 저장소(생략 시 현재 디렉터리)에 .githooks/(디스패처 +"
  echo "           기본 플러그인)를 만들고 core.hooksPath=.githooks, commit.template을 설정"
  echo "  migrate  core.hooksPath가 이 도구의 hooks/를 가리키는 옛 설치를 .githooks로 옮김"
  echo "  hook     .githooks 플러그인이 부르는 진입점 - 직접 쓸 일은 없습니다"
  echo "  -h, --help   이 도움말 출력"
}

COMMAND="install"
case "${1:-}" in
  install) shift ;;
  migrate) COMMAND="migrate"; shift ;;
esac

TARGET=""
for arg in "$@"; do
  case "$arg" in
    -h|--help|help)
      usage
      exit 0
      ;;
    # --global(init.templateDir)은 decision-32로 없앴다. 조용히 무시하면 예전처럼
    # 전역 설치가 된 줄 알게 되므로 실패로 알린다. --no-global은 원래 "전역은
    # 건너뜀"이라 지금 동작과 같으므로 예전 스크립트 호환을 위해 받아 준다.
    --global)
      echo "install.sh: --global(init.templateDir)은 decision-32에서 없앴습니다." >&2
      echo "  새 저장소마다 git-commit-tool을 한 번 실행하고 .githooks/를 커밋하세요." >&2
      echo "  예전에 설정한 전역 templateDir은 git config --global --unset init.templateDir로 지웁니다." >&2
      exit 1
      ;;
    --no-global) ;;
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

# 지금 적용되는 core.hooksPath(로컬·전역 어느 쪽이든). 값이 없으면 git config가
# 1로 끝나므로 빈 값으로 보고, 그 밖의 실패(설정 파일 깨짐 등)는 멈춘다.
current_hooks_path() {
  _status=0
  _value="$(git -C "$TARGET" config --get core.hooksPath)" || _status=$?
  case "$_status" in
    0) printf '%s\n' "$_value" ;;
    1) ;;
    *)
      echo "install.sh: ${TARGET}의 core.hooksPath를 읽지 못했습니다." >&2
      exit 1
      ;;
  esac
}

# 그 경로가 이 도구의 hooks/(어느 클론이든)인지 - 옛 방식(decision-2) 설치 판별.
# 상대경로 hooksPath는 저장소 루트 기준이라 TARGET에서 해석한다.
is_tool_hooks_dir() {
  _dir="$(cd "$TARGET" && cd -P "$1" 2>/dev/null && pwd)" || return 1
  [ "$_dir" = "$HOOKS_DIR" ] && return 0
  [ -f "${_dir}/prepare-commit-msg" ] && [ -f "${_dir}/gitformat.conf" ]
}

# .git/hooks/에서 링크가 아닌 훅(*.sample 제외)을 한 줄에 하나씩 출력한다.
# core.hooksPath를 설정하면 이 훅들은 git이 더 이상 실행하지 않는다. 심볼릭 링크는
# 예전 init.templateDir이 심은 이 도구의 링크일 수 있어 막지 않는다(.githooks가
# 이 도구의 훅을 대신 돌린다).
unmanaged_git_hooks() {
  _common="$(git -C "$TARGET" rev-parse --path-format=absolute --git-common-dir)"
  for _hook in "${_common}"/hooks/*; do
    [ -L "$_hook" ] && continue
    [ -f "$_hook" ] || continue
    case "$_hook" in
      *.sample) continue ;;
    esac
    printf '%s\n' "$_hook"
  done
}

# githooks/ 템플릿을 TARGET/.githooks/로 복사한다. 없는 파일만 만든다 - 이미 있는
# 파일이 템플릿과 다르면 그 저장소에서 고친 것으로 보고 덮지 않는다(멱등, 덮지 않음).
# 템플릿 구조는 <훅>와 <훅>.d/<플러그인> 두 단계뿐이다.
install_githooks() {
  for _src in "$GITHOOKS_TEMPLATE"/* "$GITHOOKS_TEMPLATE"/*.d/*; do
    [ -f "$_src" ] || continue
    _rel="${_src#"$GITHOOKS_TEMPLATE"/}"
    _dst="${TARGET}/.githooks/${_rel}"
    if [ ! -e "$_dst" ]; then
      mkdir -p "$(dirname "$_dst")"
      cp "$_src" "$_dst"
      chmod 755 "$_dst"
      echo "  생성  .githooks/${_rel}"
    elif cmp -s "$_src" "$_dst"; then
      [ -x "$_dst" ] || chmod 755 "$_dst"
    else
      echo "  유지  .githooks/${_rel} (템플릿과 달라 덮지 않습니다)"
    fi
  done
}

finish_install() {
  install_githooks
  git -C "$TARGET" config core.hooksPath .githooks
  git -C "$TARGET" config commit.template "$GITMESSAGE"
  echo "coding-agent-git-commit-tool: ${TARGET} 설정 완료"
  echo "  core.hooksPath  = .githooks"
  echo "  commit.template = ${GITMESSAGE}"
  echo "  .githooks/를 커밋하세요 - 플러그인은 PATH의 git-commit-tool·source-header를 부르고,"
  echo "  명령이 없는 머신에서는 경고 후 건너뜁니다(decision-32)."
  # 예전 --global이 남긴 전역 init.templateDir은 새 저장소의 .git/hooks/에 이 클론
  # 훅의 링크를 계속 심는다. 해롭지는 않지만(.githooks가 설정되면 무시된다) 이제
  # 쓰지 않으므로 지우는 방법을 알린다. 전역 설정은 여기서 바꾸지 않는다.
  _template_dir="$(git config --global --get init.templateDir)" || _template_dir=""
  if [ "$_template_dir" = "${SELF_DIR}/template" ]; then
    echo "  참고: 전역 init.templateDir이 이 도구의 template/을 가리킵니다(decision-2, 폐지)."
    echo "        git config --global --unset init.templateDir로 지우세요."
  fi
}

HOOKS_PATH="$(current_hooks_path)"
readonly HOOKS_PATH

case "$COMMAND" in
  install)
    if [ -n "$HOOKS_PATH" ] && [ "$HOOKS_PATH" != ".githooks" ]; then
      if is_tool_hooks_dir "$HOOKS_PATH"; then
        echo "install.sh: ${TARGET}는 예전 방식(core.hooksPath=${HOOKS_PATH})으로 설치돼 있습니다." >&2
        echo "  git-commit-tool migrate ${TARGET}로 .githooks로 옮기세요." >&2
      else
        echo "install.sh: ${TARGET}에 이미 다른 core.hooksPath가 있어 덮지 않습니다: ${HOOKS_PATH}" >&2
        echo "  그 훅을 .githooks/<훅>.d/ 플러그인으로 옮기고 git config --unset core.hooksPath 뒤 다시 실행하세요." >&2
        echo "  (어디서 설정됐는지: git -C ${TARGET} config --show-origin --get core.hooksPath)" >&2
      fi
      exit 1
    fi
    # hooksPath가 아직 없을 때만 .git/hooks/가 실제로 돌고 있다 - 이미 .githooks면
    # 그 훅들은 지금도 무시되는 중이라 막을 이유가 없다.
    if [ -z "$HOOKS_PATH" ]; then
      UNMANAGED="$(unmanaged_git_hooks)"
      if [ -n "$UNMANAGED" ]; then
        echo "install.sh: .git/hooks/에 링크가 아닌 훅이 있어 덮지 않습니다:" >&2
        printf '%s\n' "$UNMANAGED" | sed 's/^/  /' >&2
        echo "  core.hooksPath를 설정하면 이 훅들은 실행되지 않습니다. .githooks/<훅>.d/ 플러그인으로" >&2
        echo "  옮기거나 지운 뒤 다시 실행하세요." >&2
        exit 1
      fi
    fi
    finish_install
    ;;
  # 옛 설치(decision-2)는 core.hooksPath가 클론의 hooks/를 직접 가리킨다. 그 상태에서는
  # .git/hooks/가 이미 무시되고 있으므로 install과 달리 그 훅들 때문에 멈추지 않는다 -
  # hooksPath를 .githooks로 바꿔도 무시되는 건 그대로다. 목록만 알린다.
  migrate)
    if [ "$HOOKS_PATH" = ".githooks" ]; then
      echo "coding-agent-git-commit-tool: ${TARGET}는 이미 .githooks를 씁니다. 빠진 파일만 채웁니다."
      install_githooks
      exit 0
    fi
    if [ -z "$HOOKS_PATH" ] || ! is_tool_hooks_dir "$HOOKS_PATH"; then
      echo "install.sh: ${TARGET}는 옛 방식 설치(core.hooksPath=이 도구의 hooks/)가 아닙니다: ${HOOKS_PATH:-(설정 없음)}" >&2
      echo "  새로 설치하려면 git-commit-tool install ${TARGET}를 쓰세요." >&2
      exit 1
    fi
    echo "coding-agent-git-commit-tool: 옛 설치에서 옮깁니다 (core.hooksPath=${HOOKS_PATH} -> .githooks)"
    finish_install
    UNMANAGED="$(unmanaged_git_hooks)"
    if [ -n "$UNMANAGED" ]; then
      echo "  참고: .git/hooks/의 다음 훅은 예전처럼 계속 실행되지 않습니다. 필요하면"
      echo "        .githooks/<훅>.d/ 플러그인으로 옮기세요:"
      printf '%s\n' "$UNMANAGED" | sed 's/^/        /'
    fi
    ;;
esac

echo "coding-agent-git-commit-tool: 참고 - git push --no-verify는 로컬 훅으로 탐지할 수 없습니다."
echo "  push된 이력은 원격 설정이 지킵니다 - 대상 저장소의 원격(GitHub rulesets·병합 방식)을"
echo "  직접 구성하세요 (예시: coding-agent-git-commit-tool 저장소의 backlog doc-20)."
