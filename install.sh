#!/bin/sh
# ---
# title: install
# description: 대상 저장소에 .githooks 디스패처와 플러그인을 설치하고 hooksPath를 설정하는 설치 스크립트
# authors: [coralstay]
# license: AGPL-3.0-only
# status: draft
# created_date: '2026-11-06'
# updated_date: '2026-11-06'
# ---
# coding-agent-git-commit-tool 설치 스크립트(~/githubs/bin에서는 `git-commit-tool`).
# 대상 저장소에 커밋되는 .githooks/(공용 디스패처 + 플러그인)를 만들고
# core.hooksPath=.githooks와 commit.template을 설정한다(decision-32, decision-2 대체).
# 훅 실행에 필요한 python3 존재도 확인한다(decision-16). 실제 훅 로직은 이 스크립트가
# 위치한 클론의 hooks/에 있고, .githooks의 플러그인은 `git-commit-tool hook ...`으로
# 그 로직을 부른다.
#
# 사용법:
#   git-commit-tool [install] [--plugins 이름,...] [target-repo-dir]   .githooks 설치(기본 동작)
#   git-commit-tool migrate [--plugins 이름,...] [target-repo-dir]     옛 설치(hooksPath=클론의 hooks/)를 .githooks로
#   git-commit-tool hook <훅 이름> [훅 인자...]    .githooks 플러그인이 부르는 진입점
# target-repo-dir을 생략하면 현재 디렉터리를 대상으로 한다.
# --plugins(또는 --plugins=이름,...)는 설치할 플러그인을 고른다(GF-149): commit-format,
# source-header. 생략하면 둘 다 설치한다. 디스패처는 항상 설치한다. 모르는 이름이면
# 아무것도 쓰지 않고 exit 1. 이미 있는 플러그인 파일은 고르지 않았어도 지우지 않는다.
# 옵션은 서브커맨드 뒤(생략하면 맨 앞)의 어디에나 둘 수 있다.
set -eu

_SRC="$0"
while [ -h "$_SRC" ]; do  # ---- 1
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
if ! git config --file "$CONF" --list >/dev/null 2>&1; then  # ---- 2
  echo "gitformat: gitformat.conf를 읽을 수 없습니다: ${CONF}" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then  # ---- 3
  echo "install.sh: python3을 찾을 수 없습니다 - coding-agent-git-commit-tool 훅은 Python으로 실행됩니다." >&2
  exit 1
fi

if [ "${1:-}" = "hook" ]; then  # ---- 4
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
  echo "사용법 (Usage): git-commit-tool [install] [--plugins 이름,...] [target-repo-dir]"
  echo "                git-commit-tool migrate [--plugins 이름,...] [target-repo-dir]"
  echo "                git-commit-tool hook prepare-commit-msg <훅 인자...>"
  echo "  install  지정한 git 저장소(생략 시 현재 디렉터리)에 .githooks/(디스패처 +"
  echo "           기본 플러그인)를 만들고 core.hooksPath=.githooks, commit.template을 설정"
  echo "  migrate  core.hooksPath가 이 도구의 hooks/를 가리키는 옛 설치를 .githooks로 옮김"
  echo "  --plugins 이름,...  설치할 플러그인(commit-format, source-header). 생략하면 둘 다"
  echo "  hook     .githooks 플러그인이 부르는 진입점 - 직접 쓸 일은 없습니다"
  echo "  -h, --help   이 도움말 출력"
}

COMMAND="install"
case "${1:-}" in
  install) shift ;;
  migrate) COMMAND="migrate"; shift ;;
esac

# 템플릿 플러그인 파일 경로(<훅>.d/<NN>-<이름>)에서 이름만 뽑는다: 10-commit-format -> commit-format.
plugin_name() {
  _base="${1##*/}"
  _base="${_base#"${_base%%[!0-9]*}"}"
  printf '%s\n' "${_base#-}"
}

# 템플릿에 있는 플러그인 이름을 쉼표로 이어 출력한다(오류 안내용).
known_plugins() {
  _list=""
  for _src in "$GITHOOKS_TEMPLATE"/*.d/*; do
    [ -f "$_src" ] || continue
    _list="${_list:+${_list}, }$(plugin_name "$_src")"
  done
  printf '%s\n' "$_list"
}

# --plugins로 고른 이름(양쪽을 쉼표로 감싼 ",a,b,"). PLUGINS_GIVEN이 비어 있으면
# 옵션이 없었던 것이라 모든 플러그인을 설치한다.
PLUGINS_GIVEN=""
PLUGINS=""
set_plugins() {
  PLUGINS_GIVEN=1
  PLUGINS=",$1,"
  if [ -z "$1" ]; then
    echo "install.sh: --plugins에 플러그인 이름이 필요합니다 (지원: $(known_plugins))" >&2
    exit 1
  fi
}

TARGET=""
while [ "$#" -gt 0 ]; do
  arg="$1"
  shift
  case "$arg" in
    --plugins)
      if [ "$#" -eq 0 ]; then
        echo "install.sh: --plugins에 플러그인 이름이 필요합니다 (지원: $(known_plugins))" >&2
        exit 1
      fi
      set_plugins "$1"
      shift
      ;;
    --plugins=*) set_plugins "${arg#--plugins=}" ;;
    -h|--help|help)
      usage
      exit 0
      ;;
    --global)  # ---- 5
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

# 모르는 플러그인 이름이 하나라도 있으면 아무것도 쓰기 전에 멈춘다.
if [ -n "$PLUGINS_GIVEN" ]; then
  _known=","
  for _src in "$GITHOOKS_TEMPLATE"/*.d/*; do
    [ -f "$_src" ] || continue
    _known="${_known}$(plugin_name "$_src"),"
  done
  _names="${PLUGINS#,}"
  _names="${_names%,}"
  _old_ifs="$IFS"
  IFS=","
  for _name in $_names; do
    case "$_known" in
      *",${_name},"*) ;;
      *)
        IFS="$_old_ifs"
        echo "install.sh: 알 수 없는 플러그인: ${_name:-(빈 이름)} (지원: $(known_plugins))" >&2
        exit 1
        ;;
    esac
  done
  IFS="$_old_ifs"
fi
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

is_tool_hooks_dir() {  # ---- 6
  _dir="$(cd "$TARGET" && cd -P "$1" 2>/dev/null && pwd)" || return 1
  [ "$_dir" = "$HOOKS_DIR" ] && return 0
  [ -f "${_dir}/prepare-commit-msg" ] && [ -f "${_dir}/gitformat.conf" ]
}

unmanaged_git_hooks() {  # ---- 7
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

install_githooks() {
  for _src in "$GITHOOKS_TEMPLATE"/* "$GITHOOKS_TEMPLATE"/*.d/*; do
    [ -f "$_src" ] || continue
    # --plugins가 있으면 고르지 않은 플러그인은 만들지 않는다(디스패처는 항상 만든다).
    # 이미 있는 파일은 지우지 않는다 - 이 함수는 복사만 한다.
    _rel="${_src#"$GITHOOKS_TEMPLATE"/}"
    case "$_rel" in
      *.d/*)
        if [ -n "$PLUGINS_GIVEN" ]; then
          case "$PLUGINS" in
            *",$(plugin_name "$_rel"),"*) ;;
            *) continue ;;
          esac
        fi
        ;;
    esac
    _dst="${TARGET}/.githooks/${_rel}"
    if [ ! -e "$_dst" ]; then  # ---- 8
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
    if [ -n "$HOOKS_PATH" ] && [ "$HOOKS_PATH" != ".githooks" ]; then  # ---- 9
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
    if [ -z "$HOOKS_PATH" ]; then  # ---- 10
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
  migrate)  # ---- 11
    if [ "$HOOKS_PATH" = ".githooks" ]; then  # ---- 12
      echo "coding-agent-git-commit-tool: ${TARGET}는 이미 .githooks를 씁니다. 빠진 파일만 채웁니다."
      install_githooks
      exit 0
    fi
    if [ -z "$HOOKS_PATH" ] || ! is_tool_hooks_dir "$HOOKS_PATH"; then  # ---- 13
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


# ======== 노트 ========
# 1 심볼릭 링크를 끝까지 따라가 클론 위치를 찾음
#   설명: ~/githubs/bin/git-commit-tool은 이 클론의 install.sh로 가는 링크다. $0이 링크여도 readlink로 실제 파일
#   위치(SELF_DIR)를 구해야 hooks/·githooks/·.gitmessage를 클론 기준으로 찾는다. 상대 링크는 링크가 있는 디렉터리 기준으로 풀어 준다.
#   관련: README.md, decision-32
#   개념: symlink 해석
# 2 gitformat.conf 읽기 가드
#   설명: gitformat.conf 자체를 못 읽으면(파일 없음/문법 깨짐) 이후 모든 git config --file 읽기가 하나씩 실패하면서 원인을 알기 어려운
#   에러로 이어진다. 여기서 미리 검증해 원인을 명확히 알린다. 이 블록은 CONF를 읽는 다른 파일들에도 byte-identical하게 있다(예전에는
#   tests/consistency.bats가 동일성을 보장).
#   관련: tests/test_config_file_unreadable.py, GF-76, GF-77
#   개념: 읽기 검증 가드(fail-closed)
# 3 python3 가드
#   설명: 훅은 Python으로 실행된다(decision-16). 여기서 막지 않으면 설정은 다 끝난 뒤 첫 커밋에서야 훅이 실행 실패로 깨져 원인을 찾기 어렵다. 이
#   가드는 설치 시점만 본다.
#   관련: decision-16, GF-113, tests/test_install_script.py, tests/test_python3_missing.py
#   개념: fail-closed
# 4 hook 하위 명령: .githooks 플러그인의 진입점
#   설명: prepare-commit-msg.d/10-commit-format이 한 줄로 `exec git-commit-tool hook
#   prepare-commit-msg "$@"`를 부르면 여기서 이 클론의 hooks/prepare-commit-msg를 절대경로로 exec한다. 훅은
#   realpath(__file__)로 자기 위치를 찾으므로 gitformat.conf와 Hooks-Commit(이 클론의 HEAD)이 옛 설치와 똑같이 이 클론
#   기준으로 해석된다. 훅 로직은 바꾸지 않는다. 위의 conf·python3 가드보다 뒤에 둔다 - python3가 없으면 여기서 exit 1로 커밋을 막는다.
#   가드보다 앞에서 exec하면 env가 127을 내고, 디스패처는 127을 '명령 없음'으로 보고 검사를 건너뛰므로 python3 부재가 조용한 통과로 바뀐다. 모르는
#   훅 이름은 exit 1.
#   관련: GF-148, decision-32, githooks/prepare-commit-msg.d/10-commit-format,
#   tests/test_githooks_commit_format.py
#   개념: 진입점, 종료 코드 127 = 명령 없음
# 5 --global은 실패로 알린다
#   설명: --global(init.templateDir)은 decision-32로 없앴다. 조용히 무시하면 예전처럼 전역 설치가 된 줄 알게 되므로 실패로 알린다.
#   --no-global은 원래 '전역은 건너뜀'이라 지금 동작과 같으므로 예전 스크립트 호환을 위해 받아 준다.
#   관련: decision-32, tests/test_install_githooks.py, tests/test_install_script.py
#   개념: 하위 호환
# 6 옛 방식(decision-2) 설치 판별
#   설명: 그 경로가 이 도구의 hooks/(어느 클론이든)인지 본다. 이 클론의 HOOKS_DIR와 같거나, 다른 클론이라도 prepare-commit-msg와
#   gitformat.conf가 둘 다 있으면 이 도구의 hooks/로 본다. 상대경로 hooksPath는 저장소 루트 기준이라 TARGET에서 해석한다.
#   관련: decision-2, tests/test_migrate_githooks.py
# 7 링크가 아닌 .git/hooks 훅 찾기
#   설명: .git/hooks/에서 링크가 아닌 훅(*.sample 제외)을 한 줄에 하나씩 출력한다. core.hooksPath를 설정하면 이 훅들은 git이 더 이상
#   실행하지 않는다. 심볼릭 링크는 예전 init.templateDir이 심은 이 도구의 링크일 수 있어 막지 않는다(.githooks가 이 도구의 훅을 대신 돌린다).
#   관련: tests/test_install_githooks.py
# 8 없는 파일만 만들고 고친 파일은 덮지 않음
#   설명: githooks/ 템플릿을 TARGET/.githooks/로 복사한다. 없는 파일만 만들고, 이미 있는 파일이 템플릿과 다르면 그 저장소에서 고친 것으로 보고
#   덮지 않는다(멱등, 덮지 않음). 같으면 실행 권한만 보장한다. 템플릿 구조는 <훅>와 <훅>.d/<플러그인> 두 단계뿐이다.
#   관련: githooks/, tests/test_install_githooks.py
#   개념: 멱등(idempotent)
# 9 다른 hooksPath가 있으면 덮지 않고 실패
#   설명: hooksPath를 바꾸면 기존 훅이 조용히 무시되므로 .githooks가 아닌 값이 이미 있으면 아무것도 쓰지 않고 exit 1이다. 이 도구의 옛 설치면
#   migrate를, 그 밖이면 플러그인으로 옮기라고 안내한다.
#   관련: tests/test_install_githooks.py
#   개념: fail-closed
# 10 hooksPath가 아직 없을 때만 .git/hooks를 확인
#   설명: hooksPath가 아직 없을 때만 .git/hooks/가 실제로 돌고 있다. 이미 .githooks면 그 훅들은 지금도 무시되는 중이라 막을 이유가 없다.
# 11 migrate: 옛 설치를 .githooks로 옮김
#   설명: 옛 설치(decision-2)는 core.hooksPath가 클론의 hooks/를 직접 가리킨다. 그 상태에서는 .git/hooks/가 이미 무시되고 있으므로
#   install과 달리 그 훅들 때문에 멈추지 않는다. hooksPath를 .githooks로 바꿔도 무시되는 건 그대로이므로 목록만 알린다.
#   관련: decision-2, decision-32, tests/test_migrate_githooks.py
#   개념: 마이그레이션
# 12 이미 .githooks면 빠진 파일만 채우고 성공
#   설명: 두 번째 migrate는 설정을 바꾸지 않고 install_githooks만 다시 돌려 빠진 파일만 채운다(멱등).
#   관련: tests/test_migrate_githooks.py
#   개념: 멱등(idempotent)
# 13 옛 설치가 아니면 건드리지 않고 멈춤
#   설명: hooksPath가 없거나 이 도구의 hooks/가 아니면 아무것도 바꾸지 않고 exit 1이다. 새로 설치하려면 install을 쓰라고 안내한다.
#   관련: tests/test_migrate_githooks.py
#   개념: fail-closed
