# Changelog

The talk's principles with timestamps are condensed in `references/one-page-principles.md`.

## 2.0.0 - 2026-10-03
Upgrade of the 1.0 skill.

### Kept (the contract)
Name `one-page-visual-design`, intent (a bounded visual model that is a working document, not posterized prose), the four operating modes, the page-contract sentence, the information-model checklist, evidence labels, the semantic-encoding audit and the anti-slop test. SKILL.md frontmatter still has only `name` and `description`. Existing reference file names are unchanged.

### Added
- **Talk fidelity:** `references/one-page-principles.md`: why one page, audience, composition template, forms, iteration, wall use, subtraction, each with `[mm:ss]` timestamps; SKILL.md carries the eight decisive principles. Anchor-with-callouts is now the stated default composition.
- **Workflow with exit conditions and gates:** steps 0-8 (environment and brand check, contract, model, grammar and recipe, wireframe P0, structure P1, legibility P2, illustration and brand P3, export P4) and gates G1-G10 with measurable checks.
- **Unattended mode:** mine the project, evidence table, exploration with open questions first, "all values assumed" convention.
- **Render, look, critique, fix loop:** `scripts/render.py` (Chrome DevTools protocol, standard library only): exact-size PNG at any scale, zoom tiles and regions, PDF at the `@page` size with page-count and MediaBox checks, light/dark via emulated media, `--strict` exit code, `--freeze`, SVG input. `scripts/lint_page.js` (browser-side, no DOM changes): canvas size, type floors by sheet, WCAG text contrast, non-text contrast, text overflow and overlap, clipped content, SVG node fit, connector endpoints/crossings, svg scale and clipping, image resolution, hierarchy, metadata, density, whitespace, fonts. `references/render-and-critique-loop.md`: exact commands, plain Chrome fallback, loop protocol, glance/squint/tile procedure, failure-to-fix table.
- **Authoring kit:** `scripts/new_page.py` (sets the four-place size block for A4-A1, L/P, title, metadata, brand link, logo, recipe), `assets/page-template.html` (tokens, light/dark, fixed stage geometry, masthead metadata, legend, evidence styles, markers), `assets/lint-fixture.html` (smoke test), `references/layout-recipes.md` with the connector toolkit and nine recipes (swimlane, cycle, value chain, supply chain, factory flow, anatomy with callouts, space-time band, matrix, time-scaled swimlane) as `assets/recipes/*`, composite end-to-end layout, and `scripts/lanes_gantt.py` (JSON spec to time-scaled swimlane with critical path).
- **Print, themes, accessibility:** `references/canvas-print-and-themes.md`: sheets A4-A1 with type floors, the A3-millimetre unit system, PDF and raster checks, light for print and dark for screens, WCAG rules, colour-blind-safe default palette, never colour alone.
- **Illustration:** `references/illustration-and-assets.md`: when a picture is warranted, capability check (Codex `imagegen`, Claude Code image tools), credit rule, prompt formula, acceptance checks, provenance, dpi and `<image>` lint, icon family.
- **Brand hook:** `references/brand-and-tokens.md`: discovery order, read-the-guide-first, rule precedence, token bridge with fallbacks (tested against a real `brand/tokens.css`), per-theme category colours, fonts, logo variants, brand/subject mismatch.
- **Handoff contract:** files to leave, `handoff.md` contents, versioning, the print-annotate-return loop.
- **Compatibility:** `agents/openai.yaml` refreshed to the Codex spec; text is tool-agnostic with explicit Codex and Claude Code notes; helpers are Python 3 plus Chrome only.

### Changed
- `description`: names the output and the user's own words (one-pager, process map, cycle diagram, poster for the wall, visual spec) with explicit negatives; 728 characters.
- `references/visual-grammars.md`: forms from the talk mapped to grammars with timestamps, anchor/tiers/reading path, shape test, quantity encodings, "one channel, one meaning", new failure modes (connectors, icon family, tiny type).
- `references/discovery-and-evidence.md`: unattended mode, title test.
- Reconciled the old "avoid centred hero objects" rule with the talk's template.

### Fixed or hardened (found by testing and by an independent cold-read run)
Headless Chrome inherits the OS dark mode (theme now explicit); `--print-to-pdf-no-header` is a no-op (use `--no-pdf-header-footer`); `--dump-dom` does not wait; a fresh `--user-data-dir` hangs at exit (scripts manage their own profile); viewport is ~87 px short of `--window-size` (fixed-size canvas, never `vh`); A4 type was shrinking below legibility (`--k`); a token bridge without fallbacks collapses the page (fallbacks mandatory); a diagram whose viewBox did not match the stage was silently scaled 91-95% (fixed masthead/footer rows give a known stage, lint `svg-scale` prints the right viewBox); SVG content past the viewBox was silently clipped (`svg-clipped`); pale or accent strokes under 3:1 (`graphic-contrast`); a brand ramp that passes on dark failed on light (per-theme steps); connectors through unrelated nodes (`edge-crosses-node`); default render output could land inside the skill folder (now redirected to the system temp folder); `lanes_gantt.py` had a variable-shadowing bug (found by the lint) and skipped zero-gap finish-to-start links.

### Compatibility
- **Codex:** loads from `~/.codex/skills/one-page-visual-design/`; `agents/openai.yaml` is UI metadata (display name, blurb, default prompt, implicit-invocation policy) read by the harness, not by the agent.
- **Claude Code:** copy or symlink the skill folder into `~/.claude/skills/` (all projects) or a project's `.claude/skills/`. Claude Code ignores `agents/`.
- Requirements: Python 3.8+ and Google Chrome/Chromium for the scripts (macOS tested; Linux and Windows paths best effort); poppler (`pdfinfo`, `pdftoppm`) optional for PDF checks.

### Verification
Every documented command was run on macOS 15.7 / Chrome 154: CLI baseline, 8 sheet configurations (A4-A1, L/P) with 1-page PDFs, 9 recipes in both themes with `--strict`, the lint fixture (must exit 1) and the template (must exit 0), the brand bridge on a real token file, both official `quick_validate.py` scripts, and a cold-read run by a fresh agent (rated 4/5 before the fixes listed above).

### Known limits
Not exercised: image generation (credits), printing on paper, Google Fonts loading, Linux/Windows, implicit-trigger accuracy, installation into Claude Code. The lint cannot judge meaning; the loop requires the agent to look at the render.

## 1.0.0 - 2026-09-27
Original skill: `SKILL.md` (103 lines), `agents/openai.yaml`, `references/discovery-and-evidence.md`, `references/visual-grammars.md`.
