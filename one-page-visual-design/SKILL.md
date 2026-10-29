---
name: one-page-visual-design
description: Create, revise or review a one-page visual design in Stone Librande's sense, a single wall-ready or print-ready page where a diagram, map, matrix or annotated illustration shows how one bounded system works, such as a process or production cycle, value chain, supply chain, factory flow, product anatomy, roadmap, game or UX system. Produces an editable HTML and SVG page with PNG and PDF export at A4 to A1, a render, lint and self-critique loop, light and dark themes, and project brand tokens. Use for requests like one-pager, process map, cycle diagram, poster for the wall or visual spec. Not for prose executive summaries, single-page websites, slide decks, data dashboards or decorative posters with no explanatory model.
---

# One-Page Visual Design

> **Credit:** based on Stone Librande's "One Page Design Philosophy" talk (while creative director at EA Maxis, video: https://youtu.be/E9_wLks1kAg). The idea and the method are his; this skill packages them as an agent workflow. Not affiliated with or endorsed by Stone Librande or Electronic Arts.

Turn one bounded subject into a page people want on their wall: a visual model they can read at a glance, trace, challenge, write on and revise. It is a thinking tool and a working document, not a compressed essay, a dashboard of unrelated facts, a branded poster or a slide.

`<skill>` below is the folder containing this file. Run scripts as `python3 <skill>/scripts/render.py ...`. Read references only when the step says so.

## Principles that decide every choice (details and timestamps: [one-page-principles.md](references/one-page-principles.md))
1. **Relationships over sections.** Bibles and wikis chop a design into chunks and hide how parts connect; one page shows the connections [09:23].
2. **Nobody reads long documents;** people read headlines and pictures [10:32]. One page gets read.
3. **Title = why the page exists.** If you cannot write it, stop and discover [23:25]. Date and version every print.
4. **Default composition:** title, lots of white space, a main illustration or anchor in the middle, callouts around it, short notes [24:19].
5. **Three tiers** of information (glance, label, detail); type that no longer reads on the printed sheet is a failure, so cut instead [46:15].
6. **Every mark has a reason;** no decoration [22:24]. The shape of the diagram is part of the design [32:58].
7. **Rough first** (grayscale, early, show it), then polish [49:14]. A page that will not fit means the model is too big or wrongly shaped [37:42].
8. **Print it, hand it over, write on it;** success is people asking for a copy [44:08], [48:15].

## Choose the operating mode
Inspect available project material first, then pick one:
- **Discovery:** subject, rules or relationships are not defined well enough to model. Ask or research only what changes the page; render a wireframe at most.
- **Exploration:** the user wants to think visually before decisions settle. Provisional, assumptions visible (dashed), alternatives editable. Never present as reference.
- **Reference:** important rules are supported by sources or confirmed decisions. A page the team can rely on.
- **Revision:** a page exists (including a photo or scan of a marked-up print). Preserve valid content; list the marks as change requests; bump the version.
- **Unattended (no human to ask):** do not stop at questions. Mine the project, build an evidence table, deliver an **exploration** with open questions listed first. If no source exists, every number is *Assumed*: say so once in the masthead and keep dashed outlines for what differs from that default. See `references/discovery-and-evidence.md`.

Sparse evidence is a reason to discover, not permission to invent numbers, product philosophy or a brand.

## Workflow
Each step has an exit condition. Do not start the next until it holds. Reference files are read at the step that names them.

### 0. Environment and brand check (2 minutes)
- **Renderer:** `ls "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"` (or `which chromium google-chrome`). Without a browser you cannot run the loop; say so and deliver SVG plus the checklist below.
- **Image tools:** note whether an image generator (for example an image-generation MCP server or API) is available and whether a credit rule exists. Not needed for most pages.
- **Brand:** look for `brand/` (BRAND.md, tokens.css, logo/) and project instruction files. If present, read `references/brand-and-tokens.md` now. The brand guide's chart, line and logo rules win over template defaults.
- **Target:** audience, medium and sheet (default A3 landscape, light for print, dark for screens). Sizes, type floors and PDF rules: `references/canvas-print-and-themes.md`.
Exit: you know the renderer, brand status, sheet and theme(s).

### 1. Contract
Write the title and one sentence: **This page helps [audience] understand or decide [specific thing] by showing [relationships].** Several independent subjects means several pages (a family of linked pages beats a miniature encyclopedia). Pick the primary type: concept, system, flow, state, spatial, comparison or production.
Exit: a title that states the job, not a topic.

### 2. Information model (before any layout)
Extract and reconcile: nouns (actors, objects, places), verbs (actions, transfers), rules (triggers, quantities, timing), states and transitions, relationships (sequence, causality, dependency, containment), feedback, exceptions and failure paths, evidence (source, decision, observation) and boundaries (what belongs on another page). Add at least one **concrete example** that exercises the model, and one **exception** the model must survive. Label every claim: Observed, Specified, Decided, Proposed, Assumed, Open. A connector that cannot be labelled with a relationship means the relationship is not understood. Template and question bank: `references/discovery-and-evidence.md`.
Exit: model is consistent; unknowns are marked next to what they affect; numbers have sources.

### 3. Grammar and recipe
Choose the form from the dominant relationship, not from taste: flow, loop, system map, matrix, timeline/storyboard, spatial map, state model, annotated anatomy, tension map (`references/visual-grammars.md`, including the shape test and quantity encodings). Then pick the closest recipe: swimlane process, closed cycle, value chain, supply chain, factory flow, anatomy with callouts, space-time band, matrix, time-scaled swimlane (generated from a JSON spec), or the end-to-end composite (`references/layout-recipes.md`). At most two grammars, aligned on a shared axis. Do not default to a centred loop, numbered cards or a three-column poster.
Exit: one primary grammar, one recipe, and a sentence saying what position, size, colour, shape and connector each encode.

### 4. Wireframe pass (P0)
Create the page with the generator, which sets the size block (four places that must agree), title, purpose, status, version, ISO date and the recipe:
```bash
python3 <skill>/scripts/new_page.py design/one-page/<slug>.html --recipe R1 --size A3L --title "<title that states the job>" --purpose "<contract sentence>"
python3 <skill>/scripts/new_page.py design/one-page/<slug>.html --spec schedule.json   # R9 time-scaled swimlane from your data
```
(`--brand-css` and `--logo` link the brand files; recipes and the stage geometry are in `references/layout-recipes.md`.) Build the structure in **grayscale with real words**: nodes, connectors, quantities, the example and the exception. No illustration, no brand colour yet. Author in A3 millimetres inside the fixed stage (392 x 215; the viewBox must match, the lint's `svg-scale` checks it); hooks the lint relies on (`data-canvas`, `g.node[data-node]`, `[data-edge]`) are in `references/render-and-critique-loop.md`. Replace every sample word and delete anything that encodes nothing.
Exit: `python3 <skill>/scripts/render.py page.html` runs (it writes to `render/` next to the page) and you can state the structure from the PNG.

### 5. Structure and hierarchy pass (P1)
Render, **look at the PNG**, then answer in one sentence what the page explains. Fix hierarchy first: one dominant element, three visibly different type tiers, reading path equals process order, legend next to what it explains, white space preserved, evidence status visible (solid decided, dashed proposed, dotted open). If detail does not fit: remove repetition and prose, group repeated structures, encode lists visually, link detail to another page, split genuine concepts. Never shrink type to fit.
Exit: gates G1-G4 below pass by eye.

### 6. Legibility and lint loop (P2)
```bash
python3 <skill>/scripts/render.py page.html --theme both --tiles 2x2 --zoom 2   # PNGs + tiles + lint, ~2 s
python3 <skill>/scripts/render.py page.html --region X,Y,W,H --zoom 3           # box=[x,y,w,h] from a lint finding
python3 <skill>/scripts/render.py page.html --no-png --strict                   # exit 1 while errors remain
```
Each iteration: render, look (glance, squint, trace), read tiles, read the lint, list at most five defects by root cause, fix causes, re-render. Stop after four iterations of one pass without progress and report what is stuck (usually the model is too big: cut or split). Procedure, plain Chrome fallback commands, failure-mode table and lint reference: `references/render-and-critique-loop.md`.
Exit: 0 lint errors in every target theme, warnings fixed or justified, tiles readable.

### 7. Illustration, icons and brand pass (P3)
Only after structure is stable. Does the subject need a picture (an object, a place, an anchor)? If yes: SVG-built, supplied asset, or AI-generated hero with callouts as SVG on top, plus one icon family; if no, leave it out. Apply the brand bridge and logo. Rules, prompts, acceptance checks and provenance: `references/illustration-and-assets.md`, `references/brand-and-tokens.md`. Re-run the loop; images change contrast, dpi and whitespace.
Exit: gates G8-G9 below.

### 8. Export and hand over (P4)
```bash
python3 <skill>/scripts/render.py page.html --theme both --pdf --scale 2 --strict
```
Check the PDF: one page, correct size, text live, raster images >= 150 dpi (`pdfinfo`, `pdftoppm -r 100 -png file.pdf check`). Set status to `reference` only if readiness conditions hold. Write the handoff (below). Optionally run a cold-read test: give a fresh reader or sub-agent only the PNG and ask what it explains, how the flow runs, and what happens on failure.
Exit: all gates pass; files named and listed.

## Quality gates (all must hold for delivery; the lint covers only part)
| Gate | Check | Pass |
|---|---|---|
| G1 Purpose | title and purpose sentence | the intended reader can say what the page explains and why it exists |
| G2 Glance | 5-second look, then squint (`--scale 0.25`) | subject and dominant structure identified; one thing is biggest and it is the right thing |
| G3 Encoding | deletion test: remove boxes, colour, arrows, layout | information is lost; no device lacks a meaning; legend present |
| G4 Trace | follow the main relationship without narration | order and direction unambiguous; exception path visible; a concrete example proves the model |
| G5 Truth | evidence labels | sources/decisions/assumptions/open questions distinguishable; every number sourced |
| G6 Legibility | lint `font-too-small`, tiles | >= 7/8/10/14 pt at A4/A3/A2/A1 (14 px screen); three type tiers; text never shrunk to fit |
| G7 Contrast and access | lint `low-contrast`, light and dark | text 4.5:1 (large 3:1); meaning never by colour alone; svg has `aria-label` |
| G8 Print | PDF check | 1 page, right size, images >= 150 dpi, nothing within 6 mm of the edge, date/version/status present |
| G9 Brand | brand files, if any | tokens, fonts, logo variant, clear space and chart rules applied; exceptions recorded |
| G10 Boundary | page count and density | one page at the intended size; <= ~320 words; whitespace >= 25%; detail linked, not crammed |

## Known failure modes (fixes in the render reference)
Posterized prose; diagram wallpaper (arrows with no relationship); equal-weight soup; decorative metaphor; miniature encyclopedia; orphan legend; card collage; false certainty (invented numbers); text overflowing its node; illegible small type; overdense page; weak hierarchy; ugly connectors (diagonals mixed with elbows, lines through nodes, floating ends, several arrowheads); inconsistent icon style; brand colour used as category; AI illustration with wrong part counts or baked-in text; PDF that differs from the screen; a diagram silently scaled by a wrong viewBox; one device carrying two meanings (dashes for both status and flow); several accents competing.

## Handoff (what to leave behind)
- `<slug>.html` (source, editable, content separate from styling), `render/` PNG and PDF for each theme, `assets/` with provenance for any generated image.
- A short `handoff.md`: status, version, date, the page-contract sentence, how to read the page (30 words), evidence table path, open questions and assumptions (first), lint summary and exceptions, critique log (one line per iteration), brand files used, print instructions (sheet, 100% scale, leave margins), and how to return marks: **print, annotate in pencil, photograph or scan, send back**; marks become change requests for the next version.
- Version every iteration (`v0.1`, `v0.2`) and keep the previous reference in `archive/`. Never overwrite a printed version without bumping it.

## Reference map
| Need | File |
|---|---|
| why and how (talk principles with timestamps) | `references/one-page-principles.md` |
| readiness test, evidence labels, question bank, unattended mode | `references/discovery-and-evidence.md` |
| choosing the form; shape test; semantic encoding audit; anti-slop | `references/visual-grammars.md` |
| copy-ready layouts and the connector toolkit | `references/layout-recipes.md` |
| render commands, loop, lint rules, failure fixes | `references/render-and-critique-loop.md` |
| sheet sizes, type tiers, PDF, light/dark, accessibility | `references/canvas-print-and-themes.md` |
| hero images, AI generation, icons, provenance | `references/illustration-and-assets.md` |
| brand tokens, logo, fonts, precedence | `references/brand-and-tokens.md` |
| page generator, recipe fragments, schedule spec | `scripts/new_page.py`, `assets/recipes/`, `scripts/lanes_gantt.py` |
| renderer, lint, starter page, lint fixture | `scripts/render.py`, `scripts/lint_page.js`, `assets/page-template.html`, `assets/lint-fixture.html` |
