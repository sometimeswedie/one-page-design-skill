# Canvas, print sizes, PDF, light/dark, accessibility

Librande prints on whatever paper fits the page (legal, tabloid, plotter posters) and judges legibility on paper [16:06], [22:59]. Decide the sheet first; every size below follows from it.

## 1. Choose the sheet
| Sheet | mm (landscape) | CSS px @96 dpi | Typical use (rules of thumb, not from the talk) | Type floor (tier 3) |
|---|---|---|---|---|
| A4 | 297 x 210 | 1123 x 794 | desk reading, attach to an email/ticket | 7 pt |
| **A3** (default) | 420 x 297 | 1587 x 1123 | meeting table, office printer / print shop; about Librande's tabloid | 8 pt |
| A2 | 594 x 420 | 2245 x 1587 | wall, read standing at ~1 m | 10 pt |
| A1 | 841 x 594 | 3179 x 2245 | big wall poster, read at 1-1.5 m | 14 pt |
| Screen 16:9 | n/a | 1920 x 1080 | review on a monitor/projector; make it a separate canvas, do not project a print page | 14 px |

Portrait for journeys and vertical hierarchies (swap w/h, `A3P`). Landscape for flows and systems. Square only for radial structure. A-series sheets are all 1:1.414, so a page designed for A3 scales cleanly to A2/A1 (vector) but **text must not shrink below the floor** when going down to A4 (use `--k`).
Decision rule: wall page for a team room = A2 or A1; shared by hand or on a desk = A3; if nobody will print it, use the screen size and say so in the handoff. The floors in the table are what `lint_page.js` enforces; tier 2 should be about 1.4x the floor and tier 1 (stage heads) about 2x.

## 2. Units and scaling system (what the template does)
- Design in **A3 millimetres**. The masthead (28 mm) and footer (16 mm) rows are fixed, so the stage is exactly 392 x 215 A3-mm in landscape (269 x 338 in portrait) and the SVG viewBox matches it: scale 1.0, type sizes true. SVG content then scales with the paper for free. HTML uses `calc(var(--s) * ...)` with `--s` = 1 (A3), 1.414 (A2), 2 (A1), 0.707 (A4). `--k` boosts type only on small paper (A4: 1.25).
- `scripts/new_page.py --size A2L` writes the whole **size block** correctly. By hand, keep it consistent in four places: `<meta name="opd:size">`, `data-size` on `<main>`, `--page-w/--page-h/--s/--k`, and `@page { size: Wmm Hmm; margin: 0 }`. `@page` cannot read CSS variables, which is why the literal is repeated. The lint flags a mismatch (`canvas-size`) and render.py flags a PDF MediaBox mismatch (`pdf-size`).
- Use mm/pt/px only. Never `vh`, `vw`, or `height: 100%` on the canvas (headless Chrome's viewport is not the window; see render loop gotcha 1).
- Grid: 4 mm modules, 14 mm outer margin (keeps everything outside the ~6 mm unprintable band and leaves room for pencil notes), 5 mm between masthead/stage/footer.
- Stroke weights at A3: connectors 0.4-0.6 mm, outlines 0.4-0.5 mm, hairlines 0.25-0.3 mm (never thinner; thin lines vanish when printed at lower resolution).

## 3. Type tiers (A3 baseline; scale with `--s`)
| Tier | Job | Size at A3 | In the template |
|---|---|---|---|
| Title | what the page is for | 30 pt bold | `h1` |
| Purpose | one sentence, audience + subject + relationships | 12 pt | `.purpose` |
| Tier 1 | stage / section heads, key figures | 18 pt (figures up to 34 pt) | `.t1`, `.num` |
| Tier 2 | node labels, axis labels | 11 pt, semibold | `.t2` |
| Tier 3 | annotations, units, sources, metadata | 8.5 pt, never below 8 | `.t3`, `.meta`, `.foot` |

Three tiers means three clearly different sizes (ratio >= 1.5), not five similar ones. Use one display family and one text family at most, plus a mono face for metadata only. Numbers that carry the story get tier-1 size; units stay tier 3.

## 4. Print and PDF
- `render.py page.html --pdf` prints a vector PDF at the CSS `@page` size with backgrounds, no header/footer, one page (`pdf-pages` error otherwise). Chrome embeds fonts and keeps SVG as vector.
- Check what the printer will get: `pdfinfo out.pdf` (Pages: 1, expected size) and `pdftoppm -r 100 -png out.pdf check`, then look at `check-1.png`.
- **Raster images** inside the page must be >= 150 dpi at printed size (lint `img-soft` below that, `img-low-res` below 96). A 200 mm wide slot on A3 needs about 1200 px; on A1 the same relative slot needs about 2400 px. Upscale or regenerate; vector (SVG) is always preferable for diagrams and icons.
- **Colour:** Chrome writes RGB. Avoid fully saturated screen blues/greens/neons and 100% black fills over large areas (they print muddy or shift); keep tint panels at >= 10% so they survive office printers. For a professional print run, give the PDF to the print shop and ask for proofs.
- **Printers:** office printers cannot print to the edge; "fit to page" shrinks everything (type floors then fail). Keep the 14 mm margin and tell the user to print at 100% on the right paper.
- Hand-over (Librande [44:08]-[45:50]): print it, hand it over, bring a pencil. Leave white margin or an empty notes strip for handwriting, and keep status/version/date in the masthead so a marked-up copy can be matched to the source.

## 5. Light and dark
- Same tokens, two value sets: `:root` (light) and `:root[data-theme="dark"]`. Theme comes from `?theme=` first, then the OS setting. render.py emulates the media feature and appends `?theme=`; never leave the theme implicit in a render (headless inherits the OS).
- **Light = print default** (paper, ink cost, projectors in lit rooms). **Dark = screen/wall display.** Produce both when the page may be shown on a display: `--theme both`.
- Dark rules: no pure `#000`/`#fff` (use near-black paper, off-white ink); raise category colours' lightness instead of reusing the light ones; node fill = colour mixed 18-24% into the paper (light: 12-16%); shadows do not work, use outlines; hairlines lighter than paper by ~15%.
- Raster assets and logos need a variant per theme (or a neutral panel behind them). Check both rasters; a transparent PNG with a dark outline vanishes on dark.
- Every contrast check runs in both themes (`--theme both` runs the lint twice).

## 6. Accessibility and contrast
- **Text:** 4.5:1 against its real background (3:1 for text >= 24 px or bold >= 18.66 px). Includes text on tints, on category colours and on images. `low-contrast` blocks delivery.
- **Meaningful graphics** (outlines, markers, connector lines that carry meaning): 3:1 against neighbours. Light grey structure is fine only when it carries no information.
- **Never colour alone:** every category also differs by label, position, shape or dash; evidence status is an outline style (solid / dashed / dotted) plus a legend entry. Default palette is Okabe-Ito based (blue, vermilion, bluish green, purple, amber, steel) so it survives common colour-vision deficiencies; it does not survive being the *only* signal.
- **Meaning for assistive tech:** `role="img"` and an `aria-label` that states the page's takeaway on the main `<svg>`; add `<title>`/`<desc>` for the long description; keep DOM order = reading order (title, purpose, diagram, notes).
- **Motion:** none. The page is static.
- **Language/numbers:** units next to numbers; abbreviations spelled out once; dates ISO (`2026-10-03`).
- Contrast in brand colours: compute before use; if the brand accent fails 4.5:1 as text, use it for fills, strokes and large type only (see `brand-and-tokens.md`).
