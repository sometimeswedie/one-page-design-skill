#!/usr/bin/env python3
"""Create a starter one-page design from assets/page-template.html with the size block, metadata and (optionally) a layout recipe set.

  python3 new_page.py design/one-page/cycle.html --recipe R1 --size A3L --title "From order to delivery: where time and cost accumulate"
  python3 new_page.py page.html --spec my-schedule.json        # R9: time-scaled swimlane generated from a JSON spec (see lanes_gantt.py)
  python3 new_page.py page.html --fragment my-diagram.svgfrag   # any inner-SVG fragment
  python3 new_page.py page.html --recipe blank --size A2P --brand-css ../../brand/tokens.css --logo ../../brand/logo/mark.svg

Sets the four places that must agree (meta opd:size, data-size, --page-w/--page-h/--s/--k, @page) so you cannot get them wrong.
Recipes: R1 swimlane, R2 cycle, R3 value chain, R4 supply chain, R5 factory flow, R6 anatomy, R7 space-time, R8 matrix,
R9 time-scaled swimlane (from a spec), blank (template sample).
Recipes are landscape; for portrait re-lay the sample (a warning is printed). Standard library only.
"""
import argparse, datetime, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIZES = {"A4": (297, 210, 0.707, 1.25), "A3": (420, 297, 1, 1), "A2": (594, 420, 1.414, 1), "A1": (841, 594, 2, 1)}


def sub1(text, old, new):
    if old not in text:
        sys.exit(f"template changed: could not find {old[:60]!r}; update new_page.py or the template")
    return text.replace(old, new, 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out", help="output HTML path (parent dirs are created)")
    ap.add_argument("--recipe", default="blank", help="R1..R8 or blank (default blank)")
    ap.add_argument("--size", default="A3L", help="A4|A3|A2|A1 + L|P (default A3L)")
    ap.add_argument("--title", default="[Specific title: what this page explains]")
    ap.add_argument("--purpose", help="the one-sentence page contract (audience, subject, relationships)")
    ap.add_argument("--status", default="exploration", choices=["exploration", "reference"])
    ap.add_argument("--version", default="v0.1")
    ap.add_argument("--date", default=datetime.date.today().isoformat(), help="ISO date (default today)")
    ap.add_argument("--spec", help="JSON spec for the R9 time-scaled swimlane (scripts/lanes_gantt.py)")
    ap.add_argument("--fragment", help="file whose contents replace the sample diagram (inner SVG markup, A3 mm, stage viewBox)")
    ap.add_argument("--brand-css", help="relative href of a brand tokens.css to link (then add the bridge block; see references/brand-and-tokens.md)")
    ap.add_argument("--logo", help="relative href of a logo SVG for the masthead")
    ap.add_argument("--force", action="store_true", help="overwrite an existing file")
    a = ap.parse_args()

    m = re.fullmatch(r"(A[1-4])([LP])?", a.size.strip(), re.I)
    if not m: sys.exit("--size must look like A3L, A2P, A4, A1L")
    code, o = m.group(1).upper(), (m.group(2) or "L").upper()
    long_, short, s, k = SIZES[code]
    w, h = (long_, short) if o == "L" else (short, long_)

    out = Path(a.out)
    if out.exists() and not a.force: sys.exit(f"{out} exists (use --force to overwrite)")
    t = (ROOT / "assets" / "page-template.html").read_text(encoding="utf-8")

    t = sub1(t, 'content="A3L"', f'content="{code}{o}"')
    t = sub1(t, 'data-size="A3L"', f'data-size="{code}{o}"')
    t = sub1(t, "@page { size: 420mm 297mm; margin: 0 }", f"@page {{ size: {w}mm {h}mm; margin: 0 }}")
    t = sub1(t, "--page-w: 420mm; --page-h: 297mm; --s: 1; --k: 1;", f"--page-w: {w}mm; --page-h: {h}mm; --s: {s}; --k: {k};")
    if o == "P": t = sub1(t, 'viewBox="0 0 392 215"', 'viewBox="0 0 269 338"')
    if code == "A4" and o == "P": t = sub1(t, "--title-pt: 30pt;", "--title-pt: 21pt;")

    safe_title = a.title.replace("&", "&amp;").replace("<", "&lt;")
    t = sub1(t, "<title>[Specific page title] - one-page design</title>", f"<title>{safe_title}</title>")
    t = sub1(t, "[Specific title: what this page explains]", safe_title)
    if a.purpose: t = sub1(t, "This page helps [audience] see [thing] by showing [relationships].", a.purpose.replace("&", "&amp;").replace("<", "&lt;"))
    t = sub1(t, "<dd>exploration</dd>", f"<dd>{a.status}</dd>")
    t = sub1(t, "<dd>v0.1</dd>", f"<dd>{a.version}</dd>")
    t = sub1(t, "<dd>2026-01-01</dd>", f"<dd>{a.date}</dd>")
    t = sub1(t, "[one-sentence description of what the diagram shows]", safe_title)
    if a.brand_css: t = sub1(t, '<!-- <link rel="stylesheet" href="../brand/tokens.css"> -->', f'<link rel="stylesheet" href="{a.brand_css}">')
    if a.logo: t = sub1(t, '<!-- <img class="logo" src="../brand/logo.svg" alt="Brand"> -->', f'<img class="logo" src="{a.logo}" alt="Logo">')

    frag = None; label = a.recipe
    if a.spec or a.recipe.upper() == "R9":
        sys.path.insert(0, str(Path(__file__).resolve().parent)); import lanes_gantt
        sp = Path(a.spec) if a.spec else ROOT / "assets" / "recipes" / "R9-timeline-lanes.spec.json"
        import json; frag = lanes_gantt.build(json.loads(sp.read_text(encoding="utf-8"))); label = f"R9 ({sp.name})"
    elif a.fragment:
        frag = re.sub(r"^<!--.*?-->\n", "", Path(a.fragment).read_text(encoding="utf-8"), count=1, flags=re.S).rstrip(); label = a.fragment
    elif a.recipe.lower() != "blank":
        key = a.recipe.upper()
        found = sorted((ROOT / "assets" / "recipes").glob(f"{key}-*.svgfrag"))
        if not found: sys.exit(f"unknown recipe {a.recipe!r}; available: " + ", ".join(sorted({p.name.split('-')[0] for p in (ROOT / 'assets' / 'recipes').iterdir() if p.suffix in ('.svgfrag', '.json')})))
        frag = re.sub(r"^<!--.*?-->\n", "", found[0].read_text(encoding="utf-8"), count=1, flags=re.S).rstrip(); label = found[0].stem
    if frag is not None:
        i, j = t.index("</defs>") + len("</defs>"), t.index("</svg>")
        t = t[:i] + f"\n      <!-- diagram: {label} (replace sample words, then re-grid) -->\n" + frag + "\n    " + t[j:]
        if o == "P": print("warning: recipes are landscape; re-lay the diagram for portrait (viewBox is 269 x 338)", file=sys.stderr)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(t, encoding="utf-8")
    print(f"wrote {out}  ({code}{o}, {label}).  Next: python3 {ROOT / 'scripts' / 'render.py'} {out}")


if __name__ == "__main__":
    main()
