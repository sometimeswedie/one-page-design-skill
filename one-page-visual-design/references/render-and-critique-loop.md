# Render and critique loop

Never judge a page from its source. Render it, look at the pixels, read the lint, fix the root cause, render again. All commands below were run on macOS with Chrome 154; `<skill>` means the folder that contains SKILL.md.

## 1. Authoring conventions (so the lint can help)
Author as **one HTML file with inline SVG**. Start with `python3 <skill>/scripts/new_page.py design/one-page/<slug>.html --recipe R1 --size A3L --title "..."` (sets the size block, title, metadata, recipe; see `layout-recipes.md`; `--brand-css`, `--logo` link brand files). Fixed physical canvas, never `vh`/`vw`. The stage is a fixed size (A3 landscape 392 x 215 A3-mm, portrait 269 x 338), so the SVG viewBox must match it.

| Hook | Meaning |
|---|---|
| `<main data-canvas data-size="A3L">` | the page; size = `A0-A4` + `L`/`P` (A3L, A2P) or `1920x1080` for screen pages; also `<meta name="opd:size">` |
| `<g class="node" data-node>` shape first, then text | SVG node: lint checks the text fits the shape and nodes do not overlap |
| `[data-edge]` on path/line/polyline | connector: ends must touch a node; must not cross text or other nodes; crossings counted |
| `data-edge-free` / `data-edge-label` | a free end is intended (leader line) / text sits on a line |
| `[data-anchor]` | invisible target a leader may end in (hero illustration) |
| `h1` or `[data-title]`, `[data-meta]` | title, and status + version + ISO date |
| `.legend` or `[data-legend]` | legend glyphs are exempt from connector rules |
| `data-units="mm"` on the canvas | SVG units are real millimetres (default assumes A3 millimetres) for the `svg-scale` check |

## 2. One command: `scripts/render.py`
Standard library only, needs Chrome/Chromium (looks in the usual macOS, Linux and Windows locations, tested on macOS only; override with `--chrome PATH` or `CHROME_BIN`). Talks to Chrome over the DevTools protocol, exits cleanly, about 1.5 s per page.

```bash
python3 <skill>/scripts/render.py page.html                       # light PNG + lint -> ./render/
python3 <skill>/scripts/render.py page.html --theme both --pdf    # + dark, + vector PDF at the @page size
python3 <skill>/scripts/render.py page.html --scale 0.5           # glance view of a big sheet (A1L -> 1590x1123)
python3 <skill>/scripts/render.py page.html --tiles 2x2 --zoom 2  # read small type (each tile is a crisp re-render, not an upscale)
python3 <skill>/scripts/render.py page.html --region 120,340,400,200 --zoom 3   # box=[x,y,w,h] printed by the lint
python3 <skill>/scripts/render.py page.html --no-png --strict     # lint only; exit 1 on errors or a non-1-page PDF
python3 <skill>/scripts/render.py page.html --freeze              # page.static.html: scripts removed, JS-built SVG baked in
python3 <skill>/scripts/render.py page.svg --size 800x400         # bare SVG is wrapped in an HTML shell first
```
Outputs in `render/`: `<name>-<theme>.png`, `.pdf`, `-tile-rXcY.png`, `-region.png`, `<name>-<theme>.lint.json`. `--scale 2` gives retina PNG (A3L 3174x2246). Canvas pixel sizes at 96 dpi: A4L 1123x794, A3L 1587x1123, A2L 2245x1587, A1L 3179x2245 (portrait: swap). The PDF is checked for page count (must be 1) and MediaBox against the declared size.

Without `--out`, output goes to `render/` next to the page (or the system temp folder if the page lives inside the skill folder). Repeated identical findings are collapsed to one line with a count.

Self-test of the tooling (write outside the skill folder): `python3 <skill>/scripts/render.py <skill>/assets/lint-fixture.html --out /tmp/opd-selftest --no-png --strict` must exit 1 and list errors for tiny type, contrast, node overflow, box spill, clipping, overlap and a broken image; `assets/page-template.html` must exit 0.

## 3. Plain Chrome commands (no scripts; fallback and sanity check)
```bash
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PAGE="file://$PWD/page.html"          # absolute path; percent-encode spaces
"$CHROME" --headless --hide-scrollbars --force-device-scale-factor=2 --window-size=1587,1123 \
  --screenshot="$PWD/page@2x.png" "$PAGE?theme=light" 2>/dev/null                # PNG: 3174x2246 for A3L
"$CHROME" --headless --no-pdf-header-footer --print-to-pdf="$PWD/page.pdf" "$PAGE?theme=light" 2>/dev/null
pdfinfo page.pdf | grep -E "Pages|Page size"                                      # expect Pages: 1, A3
pdftoppm -r 100 -png page.pdf page-print                                          # what the printer receives -> page-print-1.png
"$CHROME" --headless --dump-dom "$PAGE?theme=light" > page.dom.html 2>/dev/null   # DOM after the page's own JS ran
```
`--window-size` must equal the canvas size in CSS px (table above). `pdftoppm`/`pdfinfo` come with poppler (`brew install poppler`).

Gotchas observed on this Mac (Chrome 154):
1. New headless makes the **layout viewport about 87 px shorter** than `--window-size` height. A fixed mm/px canvas still screenshots whole; anything sized with `vh` or `100%` height does not. Use fixed sizes.
2. Headless **inherits the OS appearance** (this Mac is dark, so `prefers-color-scheme: dark` is true by default). `--blink-settings=preferredColorScheme=` is unreliable. Drive the theme with `?theme=light|dark` plus `[data-theme]` (the template does), or use render.py (emulates the media feature).
3. `--no-pdf-header-footer` removes the date/title/URL header. The old `--print-to-pdf-no-header` is ignored.
4. `--dump-dom` snapshots at load; timers and async work are not awaited, and `--virtual-time-budget` did not change that. Use `render.py --freeze`.
5. A fresh `--user-data-dir` with plain `--screenshot`/`--print-to-pdf` writes the file in under a second and then **never exits** (observed while the user's own Chrome was open). Omit the flag, or let render.py manage the process (it launches its own profile and kills Chrome when done).
6. stderr noise (`CVDisplayLink`, `allocator multiple times`) is harmless.
7. Stop only a Chrome you started (`kill <pid>`); never `pkill` by name, which can hit someone else's browser.
8. A Chrome DevTools/browser tool in the agent environment (Claude in Chrome, Playwright, Codex browser) is fine for looking; set the same viewport and theme, and call `await opdLint()` after pasting `scripts/lint_page.js`.

## 4. The loop
```
P0 wireframe -> P1 structure -> P2 legibility -> P3 illustration + brand -> P4 export
   each pass:  render -> LOOK -> test -> lint -> list <=5 defects -> fix root causes -> render
```
- **P0 wireframe:** grayscale, real words, no illustration, no brand colour. Judge only structure and hierarchy. Cheap to throw away (Librande shows rough black-and-white pages first).
- **P1 structure:** model correct, grammar right, reading path obvious, example and exception present.
- **P2 legibility:** lint clean at the target size, tiles read, contrast and type tiers fine in light and dark.
- **P3 illustration + brand:** only after structure is stable; re-run lint (images add contrast and dpi risks).
- **P4 export:** `--theme both --pdf --scale 2`, copy finals, write the handoff.

### Each iteration
1. **Render** the whole page. For A2/A1 use `--scale 0.5` so the whole sheet fits one view.
2. **Look (glance):** open the PNG. In one sentence, say what the page explains and which structure dominates. If you cannot, the hierarchy failed; fix that before anything else.
3. **Squint/5-second test:** render `--scale 0.25` (or imagine it blurred). The title, the hero/anchor and the main flow must still separate from the background; equal-weight soup means weak hierarchy.
4. **Read the details:** `--tiles 2x2 --zoom 2` and view each tile. Check labels, arrowheads, alignment, collisions, the legend.
5. **Lint:** read errors first, then warnings. Each finding has `box=[x,y,w,h]`; zoom with `--region`.
6. **List at most 5 defects**, ordered by damage, each with its root cause (not "move label" but "node too narrow for its longest label"). Fix causes in the model/CSS, not by nudging pixels.
7. **Re-render** and confirm the defects are gone and nothing new broke. Log one line per iteration (what failed, what changed).

Stop when the gates in SKILL.md pass. After 4 iterations of one pass without progress, stop and report what is stuck (usually the model is too big for one page: cut, group, or split). Do not polish a page whose structure failed P1.

## 5. What a human would see that the lint cannot (check by eye)
- **Dominant idea:** is one thing biggest, and is it the right thing? Does the eye start at the title and anchor, then follow the process order?
- **Alignment and rhythm:** shared left edges, consistent gaps (use a 4 mm grid); nodes of equal rank are equal size.
- **Connectors:** orthogonal or smooth, one style, corner radius consistent, arrowheads only at the end, leaving from the node edge in the direction of flow, no diagonals mixed with elbows, no line passing behind unrelated nodes, labels sit on the line with a halo, few crossings.
- **Icons/illustration:** one family (same stroke weight, corner style, level of detail, palette); no decorative icons; nothing from a generator with garbled text.
- **Colour meaning:** each colour/shape/dash has one meaning, shown in the legend; brand accent is used for emphasis, not as category.
- **Light/dark parity:** both themes keep hierarchy and contrast; images and logos have a variant that works on each background.
- **Print reality:** look at the PDF raster (`pdftoppm`), not only the screen PNG; check bleed of tint panels near the trim and that nothing important is within 6 mm of the edge.
- **Truth:** proposed/assumed/open items look different from decided ones; the numbers on the page match the source. If *every* number is assumed, say so once in the masthead status and keep dashes for what differs from that default, otherwise the dashes stop carrying information.
- **One channel, one meaning:** node outline dash = evidence status, connector dash = flow type; check they still differ in grayscale. One accent per view.

## 6. Failure modes and fixes
| Symptom | Usual cause | Fix |
|---|---|---|
| `svg-text-overflow`, `text-spills-box`, `clipped-content` | label longer than its box; fixed height; `overflow:hidden` | shorten label (verb + noun), widen node to longest label + 6 mm, wrap into `<tspan dy>` lines (max 2), let HTML boxes size by content (`min-height`, not `height`), never hide overflow to silence it |
| `font-too-small` | type scaled with the canvas, or detail crammed in | raise to tier minimums (`references/canvas-print-and-themes.md`), then cut content; on A4 set `--k` |
| `low-contrast` | pale grey labels, tinted fill + coloured text, text on image | use `--ink`/`--ink-2` text on tints; put text on a solid panel; darken the colour, never rely on size |
| `text-overlap`, `node-overlap` | absolute coordinates collided after a label grew | re-grid; stagger; move the annotation to a callout |
| `edge-floating-end` | connector hand-typed, node moved later | derive endpoints from node edges; anchors at mid-edges; add `data-edge-free` only for leader lines |
| `edge-crosses-node` | a flow skips a tier or lane | put each node in the tier/lane where it is consumed, or route through the gutter between nodes |
| `edge-crosses-text` | label placed on the path | put labels on the segment with a halo (`data-edge-label`), or beside it |
| `connector-tangle` (> 6 crossings) | node order ignores the flows | reorder nodes by their neighbours (barycentre), group, or split the page |
| `prose-block`, `dense` | paragraphs, comprehensive coverage | convert to label + number + 1-line annotation; move detail to a linked page |
| `no-whitespace` | everything filled | delete the least important tier-3 items; enlarge margins; split |
| `weak-hierarchy` | all text similar in size | enforce 3 tiers with ratio >= 1.5 between tiers and title >= 2.2x body |
| `many-hues` | colour as decoration | one colour per category, max 6; greys for the rest |
| `font-missing` | brand font not installed or not loaded | `@font-face` from the brand folder with a relative URL, or pick the declared fallback; do not ship a silent fallback |
| `img-low-res`, `img-soft` | generated image too small for the sheet | regenerate larger or upscale to >= 150 dpi at print size; or reduce its printed size |
| `img-broken` | wrong relative path | keep images in `assets/` beside the page |
| `canvas-size`, `pdf-size`, `pdf-pages` | size declared in four places disagree | use `new_page.py --size`, or edit the SIZE block together (meta, `data-size`, CSS vars, `@page`) |
| `svg-scale` | viewBox does not match the stage: the whole diagram is silently scaled (type shrinks, margins appear) | set the viewBox the lint prints; if you changed masthead/footer height, change the viewBox with it |
| `svg-clipped` | content below/right of the viewBox is cut off by the SVG | move it inside, or shrink the content; never enlarge the viewBox without the stage |
| `graphic-contrast` | an accent/pale stroke has < 3:1 against its background in this theme | darken the stroke for that theme (brand text-safe accent), add weight and a label; check both themes |
| PDF looks different from the screen | background colours dropped; `vh` units; fonts | keep `print-color-adjust: exact`; fixed units; inspect the `pdftoppm` raster |

## 7. Lint reference (`scripts/lint_page.js`)
Browser-side, no DOM changes, returns `{ok, canvas, errors[], warnings[], info{}}`; every finding has `id`, `msg`, `box`.
- **Errors** (block delivery): `canvas-size`, `font-too-small`, `text-outside-canvas`, `svg-clipped`, `low-contrast`, `text-spills-box`, `clipped-content`, `text-overlap`, `svg-text-overflow`, `img-broken`, `img-low-res`.
- **Warnings** (fix or justify in the handoff): `svg-scale`, `graphic-contrast`, `page-scrolls`, `near-edge`, `prose-block` (> 28 words in one block), `font-missing`, `node-tight`, `node-overlap`, `edge-floating-end`, `edge-crosses-node`, `edge-crosses-text`, `connector-tangle`, `img-soft`, `weak-hierarchy`, `no-title`, `meta-date`, `meta-version`, `meta-status`, `dense` (> 320 words), `no-whitespace` (< 25% empty), `many-hues` (> 7).
- `info`: words, text items, type tiers (pt), title/body ratio, whitespace %, hue families, minimum contrast.
- Thresholds: minimum text size 7 / 8 / 10 / 14 pt at A4 / A3 / A2 / A1 (14 px for screen sizes); contrast 4.5:1 (3:1 for text >= 24 px or bold >= 18.66 px). They are floors, not targets.
- The lint cannot judge meaning. A page can pass every check and still say nothing; steps 2-4 of the loop are not optional.
- Heuristic limits: contrast is skipped over gradients/images; SVG text backgrounds come from the shape under the text centre; word and whitespace budgets are advisory. It does not see a legend label running into the next glyph, an edge label sitting between two parallel lines, or two meanings sharing one dash style: look for those by eye (section 5).
