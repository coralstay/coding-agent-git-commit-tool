#!/usr/bin/env python3
# ---
# title: build-diagrams
# description: design/diagrams의 DOT 원본을 독립 SVG로 렌더하는 빌드 스크립트
# authors: [coralstay]
# license: AGPL-3.0-only
# status: draft
# created_date: '2026-11-06'
# updated_date: '2026-11-06'
# ---
"""design/diagrams/*.dot (·.mmd) → design/diagrams/<이름>.svg 독립 SVG 렌더.

표기 원칙 — DOT 우선:
  그래프 · 트리 · DAG · 플로우차트 · 파이프라인 · 클래스 다이어그램 · 경계 표현은 전부
  Graphviz DOT(.dot)으로 쓴다. DOT에 대응물이 없는 것(시퀀스 다이어그램 등)만 mermaid(.mmd)로
  쓴다. 이유는 레이아웃 품질(특히 의존성 DAG)과 소스 분리다.

원본과 생성물:
  원본은 design/diagrams/ 안의 .dot(그리고 시퀀스 하나는 .mmd)이다. 같은 디렉토리의 .svg는
  이 스크립트가 만드는 생성물이므로 직접 고치지 않는다. 그림을 고치려면 .dot/.mmd를 고치고
  이 스크립트를 다시 돌린다.

색 — 라이트/다크 대응:
  색은 .dot(그리고 mermaid-theme.json)에 센티넬 hex(#f00001 …)로 적는다. 이 스크립트가
  센티넬을 CSS 변수(var(--diagram-*))로 치환하고, 그 변수를 SVG 안의 <style>에 정의한다 —
  라이트 값이 기본이고 @media (prefers-color-scheme: dark)가 다크 값으로 덮는다. 그래서
  SVG 파일 하나가 장 Markdown의 ![](…svg) · GitHub <img> 어디서나
  보는 쪽 테마를 따라간다.

빌드 전제: graphviz(`dot`), mermaid 렌더용 `npx` + 로컬 Chrome.
mermaid-cli가 실패하면 기존 SVG를 그대로 둔다(아직 토큰화되지 않은 원시 mermaid 출력이면
토큰화만 한다).

사용: python3 design/build-diagrams.py
"""
import io, os, re, subprocess, sys, pathlib, tempfile

ROOT = pathlib.Path(__file__).parent
DIA = ROOT / "diagrams"
BUILD_MARK = 'data-generated-by="design/build-diagrams.py"'  # ---- 1

TOKENS = {  # ---- 2
    "#f00001": "var(--diagram-ink)",     "#f00002": "var(--diagram-muted)",
    "#f00003": "var(--diagram-line)",    "#f00004": "var(--diagram-surface)",
    "#f00005": "var(--diagram-surface-2)", "#f00006": "var(--diagram-accent)",
    "#f00007": "var(--diagram-accent-bg)", "#f00008": "var(--diagram-accent-ink)",
    "#f00009": "var(--diagram-impl)",    "#f0000a": "var(--diagram-impl-bg)",
    "#f0000b": "var(--diagram-review)",  "#f0000c": "var(--diagram-review-bg)",
    "#f0000d": "var(--diagram-verify)",  "#f0000e": "var(--diagram-verify-bg)",
    "#f0000f": "var(--diagram-logger)",  "#f00010": "var(--diagram-logger-bg)",
}
MERMAID_TOKENS = {  # ---- 3
    "#262b34": "var(--diagram-ink)",      "#000000": "var(--diagram-ink)",
    "#f2f3f5": "var(--diagram-surface)",  "#eaeaea": "var(--diagram-surface-2)",
    "#9aa4b8": "var(--diagram-line)",     "#a8adb8": "var(--diagram-muted)",
    "#edf2ae": "var(--diagram-accent-bg)", "#fff5ad": "var(--diagram-accent-bg)",
    "#575247": "var(--diagram-muted)",    '"#666"': '"var(--diagram-line)"',
    '"#999"': '"var(--diagram-line)"',
}
LIGHT = {  # ---- 4
    "ink": "#1a2330", "muted": "#51616c", "line": "#c9d3d8",
    "surface": "#ffffff", "surface-2": "#eaf0f2",
    "accent": "#0e7c86", "accent-bg": "#d8eeef", "accent-ink": "#08565d",
    "impl": "#2b6cb0", "impl-bg": "#dbe9f7", "review": "#7c3aed", "review-bg": "#ece3fc",
    "verify": "#2f855a", "verify-bg": "#def0e6", "logger": "#5b6b78", "logger-bg": "#e4e9ec",
}
DARK = {
    "ink": "#e7eef2", "muted": "#9aaab4", "line": "#2e3d47",
    "surface": "#182129", "surface-2": "#1f2a33",
    "accent": "#3fc4ce", "accent-bg": "#163238", "accent-ink": "#8ee3e9",
    "impl": "#7db3e8", "impl-bg": "#1c2c3d", "review": "#b79bf5", "review-bg": "#291f3d",
    "verify": "#7cd1a3", "verify-bg": "#173226", "logger": "#a6b4bd", "logger-bg": "#232e36",
}
FONT = '"IBM Plex Sans", ui-sans-serif, system-ui, sans-serif'


def theme_style() -> str:
    decl = lambda t: " ".join(f"--diagram-{k}: {v};" for k, v in t.items())
    return (f"<style>:root {{ {decl(LIGHT)} }}\n"
            f"@media (prefers-color-scheme: dark) {{ :root {{ {decl(DARK)} }} }}</style>")


def tokenize(svg: str) -> str:
    for table in (TOKENS, MERMAID_TOKENS):
        for sentinel, var in table.items():
            svg = svg.replace(sentinel, var).replace(sentinel.upper(), var)  # ---- 5
    return svg


def finish(svg: str, name: str, mermaid: bool) -> str:
    """정리 · 토큰화 · 테마 <style> 삽입을 거쳐 독립 SVG 문서를 만든다."""
    svg = re.sub(r"<\?xml[^>]*\?>\s*", "", svg)
    svg = re.sub(r"<!DOCTYPE[^>]*>\s*", "", svg, flags=re.S)
    svg = re.sub(r"<!--.*?-->\s*", "", svg, flags=re.S)
    svg = re.sub(r'<polygon fill="white"[^/]*/>\s*', "", svg)  # ---- 6
    svg = tokenize(svg)
    if not mermaid:
        svg = re.sub(r'font-family="[^"]*"', f"font-family='{FONT}'", svg)

    def fix_root(m):
        tag = m.group(0)
        if mermaid:
            vb = re.search(r'viewBox="([-\d.]+) ([-\d.]+) ([\d.]+) ([\d.]+)"', tag)  # ---- 7
            tag = re.sub(r'\s(width|height|style|role|aria-roledescription)="[^"]*"', "", tag)
            if vb:
                tag = tag.replace("<svg", f'<svg width="{vb.group(3)}" height="{vb.group(4)}"', 1)
        if "xmlns=" not in tag:
            tag = tag.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
        return tag.replace("<svg", f'<svg {BUILD_MARK} role="img" aria-label="{name}"', 1)

    svg = re.sub(r"<svg\b[^>]*>", fix_root, svg, count=1)
    svg = re.sub(r"(<svg\b[^>]*>)", lambda m: m.group(1) + "\n" + theme_style(), svg, count=1)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + svg.strip() + "\n"


def render_mmd(path: pathlib.Path) -> str | None:
    """mermaid 소스를 mermaid-cli로 렌더한다. 실패하면 None(기존 SVG 유지 판단은 호출자)."""
    with tempfile.TemporaryDirectory() as tmp:
        raw = pathlib.Path(tmp) / f"{path.stem}.svg"
        cmd = [
            "npx", "-y", "@mermaid-js/mermaid-cli@11",
            "-i", str(path), "-o", str(raw),
            "-c", str(DIA / "mermaid-theme.json"), "-b", "transparent",
        ]
        env = dict(os.environ)
        env.setdefault("PUPPETEER_EXECUTABLE_PATH",
                       "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        print(f"  {path.stem}: mermaid-cli 렌더 중…")
        r = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if r.returncode or not raw.exists():  # ---- 8
            last = r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ""
            print(f"    ! mermaid-cli 실패 — {last}")
            return None
        return finish(io.open(raw, encoding="utf-8").read(), path.stem, mermaid=True)


def render_dot(path: pathlib.Path) -> str:
    out = subprocess.run(["dot", "-Tsvg", str(path)], capture_output=True, text=True)
    if out.returncode:
        sys.exit(f"dot 실패: {path}\n{out.stderr}")  # ---- 9
    return finish(out.stdout, path.stem, mermaid=False)


def main() -> None:
    sources = sorted(DIA.glob("*.dot")) + sorted(DIA.glob("*.mmd"))
    if not sources:
        sys.exit(f"소스 없음: {DIA}")
    written = 0
    for src in sources:
        target = src.with_suffix(".svg")
        if src.suffix == ".dot":
            svg = render_dot(src)
        else:  # DOT에 대응물이 없는 것(시퀀스 등)만 mermaid
            svg = render_mmd(src)
            if svg is None:
                if not target.exists():
                    sys.exit(f"mermaid-cli 실패, 대체할 SVG도 없다: {src}")
                old = io.open(target, encoding="utf-8").read()
                if BUILD_MARK in old:  # ---- 10
                    print(f"    기존 {target.name}을 그대로 둔다")
                    written += 1
                    continue
                svg = finish(old, src.stem, mermaid=True)
                print(f"    기존 원시 {target.name}을 토큰화해 쓴다")
        io.open(target, "w", encoding="utf-8").write(svg)
        written += 1
        print(f"  {target.name}: {len(svg):,} bytes")
    print(f"완료 — SVG {written}개 → {DIA}")


if __name__ == "__main__":
    main()


# ======== 노트 ========
# 1 생성물 표식
#   설명: 이 스크립트가 만든 SVG에는 data-generated-by 속성이 붙는다. mermaid 렌더가 실패했을 때 기존 SVG가 이미 토큰화된 생성물인지
#   가려내는 데 쓴다. 생성물은 직접 고치지 않는다(.dot/.mmd를 고치고 다시 돌린다).
#   관련: design/diagrams/, 사용자 전역 CLAUDE.md의 다이어그램 표기 원칙
#   개념: 생성물 vs 원본
# 2 센티넬 hex를 CSS 변수로 치환하는 표
#   설명: .dot에는 색을 센티넬 hex(#f00001 ...)로 적는다. 이 표가 센티넬을 var(--diagram-*)로 바꾸고, 그 변수를 SVG 안의
#   <style>에 정의한다. 그래서 SVG 파일 하나가 장 Markdown의 ![](...svg)와 GitHub <img> 어디서나 보는 쪽의 라이트/다크 테마를
#   따라간다.
#   관련: design/diagrams/_common.gv, design/diagrams/01-commit-flow.dot
#   개념: 센티넬 색 치환
# 3 mermaid가 하드코딩하는 팔레트도 같은 방식으로 토큰화
#   설명: mermaid가 렌더한 SVG(시퀀스)는 일부 기본 팔레트를 하드코딩한다. 같은 방식으로 CSS 변수로 치환해야 다크 테마를 따라간다.
# 4 토큰 값의 출처
#   설명: 라이트 값은 RFC(2026-09-26, git 이력)의 :root(--diagram-*)이고, 같은 문서의 다크 블록(--ink, --line,
#   --accent, --role-* ...)이 다크 값(DARK)이다.
#   관련: git 이력(2026-09-26 RFC)
#   개념: 라이트/다크 테마
# 5 토큰화는 대문자 hex도 함께 치환
#   설명: Graphviz가 hex를 대문자로 쓰는 경우를 위해 센티넬의 대문자 형태도 같이 바꾼다.
# 6 Graphviz의 흰 배경 폴리곤 제거
#   설명: Graphviz가 깔아두는 흰 배경 폴리곤을 지워 투명 배경을 유지한다. 그래야 다크 테마에서도 배경이 문서와 섞인다.
# 7 mermaid는 크기를 viewBox 기준으로 다시 정함
#   설명: mermaid는 width="100%"와 style max-width를 준다. <img>에서 크기가 잡히도록 viewBox 크기를 width/height로
#   쓴다.
# 8 mermaid-cli 실패는 None으로 알린다
#   설명: 빌드 전제는 graphviz(dot), mermaid 렌더용 npx와 로컬 Chrome이다. mermaid-cli가 실패하면 None을 돌려 호출자가 기존
#   SVG를 그대로 둘지 판단하게 한다. 실패가 빌드 전체를 막지 않는다.
#   관련: main()
#   개념: 우아한 실패(graceful degradation)
# 9 dot 실패는 즉시 멈춘다
#   설명: DOT은 표기 원칙상 주된 경로라 렌더가 실패하면 조용히 넘기지 않고 sys.exit로 원인(stderr)과 함께 멈춘다. mermaid와 달리 대체할 기존
#   생성물에 기대지 않는다.
#   개념: fail-closed
# 10 이미 토큰화된 기존 SVG는 그대로 둔다
#   설명: mermaid-cli가 실패했을 때 기존 SVG에 생성물 표식이 있으면 그대로 둔다. 표식이 없는 원시 mermaid 출력이면 토큰화만 해서 쓴다. 대체할
#   SVG가 아예 없으면 멈춘다.
#   관련: BUILD_MARK(노트 1)
#   개념: 멱등(idempotent)
