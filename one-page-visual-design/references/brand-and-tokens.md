# Brand hook: use the project's tokens, logo and rules

The page should look like it belongs to the project, **without** letting brand dressing replace the model. Brand supplies colour, type, logo and drawing rules; the information model supplies structure and meaning.

## 1. Find the brand (do this in step 0, before choosing colours)
Search in this order and stop at the first hit; record what you found in the handoff.
1. A path the user or task names.
2. `brand/` (or `design/`, `assets/brand/`, `docs/brand/`) in the project root (not this skill's folders): `BRAND.md` / `brand-guide.md` / `DESIGN.md`, `tokens.css`, `tokens.json`, `logo/` or `*.svg` lockups, a media prompt kit, a brand board page.
3. Project instruction files (`CLAUDE.md`, `AGENTS.md`, `README.md`) that name colours, fonts or a design language.
4. Existing pages in the repo (`design/`, `docs/`, a website) to read tokens from.
5. None found: use the template's neutral tokens and say "no brand supplied" in the handoff. Do not invent a brand.

Brand guides can be long. Find the governing sections first: `grep -n -i -E "chart|diagram|infograph|print|logo|clear|accent" BRAND.md`, then read only those.

Files like these are **read-only inputs**. Never edit the brand folder; if something is missing (a dark logo, a token), note it in the handoff.

## 2. Read the rules before the tokens
Open the brand guide and read only the sections that govern your output: colour usage and proportions, light vs dark mode, typography, logo clear space/minimum size/variants, **charts, diagrams, technical illustration, infographics, print**. Where the guide is more specific than this skill's defaults, **the guide wins**: palette for series, line weights, accent limits, type, logo placement. The guide never overrides legibility minimums or the semantic-encoding rules; if they collide (an accent that fails contrast as text), keep the brand colour for fills/strokes/large type and record the exception.

Typical brand rules and what they change on the page:
| Brand rule | Effect |
|---|---|
| "series use a single ramp; accent marks only the highlight" | set `--c1..--c6` to ramp steps; separate categories by lane, label, shape, hatch, not hue; use the accent for the one thing that matters (the loop, the bottleneck, "your build") |
| "accent at most N% of the page" | one accent element per view; do not use it for category or decoration |
| "dark default for screens, light for print/documents" | produce both (`--theme both`); light is the print master |
| "accent text on light needs a darker variant" | map the page's `--accent` (used for strokes **and** text) to the brand's text-safe accent token, and use the base accent only for large fills; a yellow stroke on a light panel is about 1.7:1 and fails the 3:1 graphic rule (lint `graphic-contrast`) |
| the brand has one accent and the recipes want to highlight several things | one accent per view: bottleneck **or** critical path **or** exception; the rest by weight, outline or position |
| brand icon spec (cap/join/stroke) differs from the neutral icon set | the brand wins: edit `.ico` to the brand's geometry |
| logo clear space / minimum size / mono variants | place the right SVG at or above minimum size with the specified clear space |
| "never redraw, recolour or let a model draw the logo" | embed the supplied SVG; composite, never generate |
| blueprint/technical-illustration line weights | copy them into stroke widths (`0.35 mm` silhouette, `0.18 mm` hairline, etc.) |

## 3. Bridge the tokens into the template
The template reads neutral page tokens: `--paper --panel --ink --ink-2 --ink-3 --line --accent --on-accent --font-display --font-body --font-mono --c1..--c6`. Link the brand file and add a **bridge block after the template's token blocks** (it must win at equal specificity). Rules:
- **Every mapping carries a fallback** `var(--brand-token, neutral-value)`. If the stylesheet path is wrong the page degrades to neutral instead of collapsing (tested: with bare `var(--brand-token)` a missing file made every `font:` shorthand invalid and all text jumped to 16 px Times).
- Link with a **relative path** during development (`<link rel="stylesheet" href="../brand/tokens.css">`, adjust depth), so there is one source of truth. For handoff to someone without the repo, inline a snapshot of the used tokens in `<style>` and comment its source and date.
- Use `:root, :root[data-theme]` as the selector so the bridge also beats the template's `:root[data-theme="dark"]` block, and let the **brand's own light/dark selectors** switch values (render.py sets `data-theme` to `light` or `dark`; brand files that key off `[data-theme="light"|"dark"]` just work). If the brand uses another mechanism, add a small mapping from its attribute/class to `data-theme`.
- Delete the template's unused literal colours once the bridge is verified; keep the template's size/type/layout blocks.

Example for a project whose tokens use an `--rb-` prefix (dark default, `[data-theme="light"]` for print), verified on this machine in both themes:
```css
:root, :root[data-theme] {
  --paper: var(--rb-bg, #fbfaf7);  --panel: var(--rb-surface-2, #f1efe9);  --ink: var(--rb-text, #15171a);
  --ink-2: var(--rb-text-muted, #3d434a);  --ink-3: var(--rb-text-subtle, #5b626b);  --line: var(--rb-border, #c9c5bb);
  --accent: var(--rb-accent-text, var(--rb-accent, #0b5cad));  /* theme-aware text-safe accent: strokes and text pass in both themes */
  --on-accent: var(--rb-on-accent, #fff);
  --font-display: var(--rb-font-display, "Helvetica Neue", Arial, sans-serif);
  --font-body: var(--rb-font-text, "Helvetica Neue", Arial, sans-serif);
  --font-mono: var(--rb-font-mono, Menlo, monospace);
}
/* the brand allows one ramp + one accent: categories = ramp steps chosen PER THEME so outlines keep 3:1 on both the page and the lane panels;
   a ramp separates only ~4 categories by lightness, so tell them apart by lane, label and shape as well */
:root[data-theme="dark"]  { --c1: var(--rb-steel-500, #56b4e9); --c2: var(--rb-steel-400, #ff9e5e); --c3: var(--rb-steel-300, #3ccf9f);
                            --c4: var(--rb-steel-200, #d69cf0); --c5: var(--rb-bare-metal, #e8c25a); --c6: var(--rb-steel-100, #8fb7d4); }
:root[data-theme="light"] { --c1: var(--rb-steel-700, #0072b2); --c2: var(--rb-steel-600, #d55e00); --c3: var(--rb-steel-500, #007a5a);
                            --c4: var(--rb-steel-800, #8a4f9e); --c5: var(--rb-steel-900, #a67a00); --c6: var(--rb-steel-950, #3f6f8f); }
```
When token names are unknown, list them (`grep -o -- '--[a-z0-9-]*:' tokens.css | sort -u`) and map by role: page background, panel, primary text, muted text, rule, accent, font families; take categorical colours from the guide's data-viz rule, not from brand hero colours.

## 4. Fonts
- Use the brand's families through the bridge. If they come from a web font service (tokens file shows a `<link>` to fonts), the render needs network; offline the browser falls back and the lint says `font-missing`. Do not ship a silent fallback: either get the font files from the user/project (relative `@font-face` with `font-display: block`), or accept the brand's declared fallback stack and state it in the handoff. Do not download fonts from untrusted sources.
- Install nothing system-wide for a design task.
- Wide/uppercase display faces take more width: re-check node widths (`svg-text-overflow`).

## 5. Logo
- Choose the variant for the surface: reversed/white-on-dark for dark theme, dark/mono for light, mono for one-colour print. If the page renders both themes, swap the logo with the theme (`<picture>`-style: two `<img>` toggled by `[data-theme]`) or place it on a neutral plate.
- Respect clear space and minimum size from the guide (screen and print minima differ). Place it where the guide or task says (top-left masthead by default in the template; bottom-right if the brand asks) and never next to competing marks.
- Embed the SVG as supplied (`<img src="../brand/logo/...svg">`). Never retype a wordmark, recolour, crop, stretch, add effects, or generate it with an image model.
- Lint: the logo `<img>` is checked for loading; check clear space by eye in the tiles.

## 6. Brand colour vs meaning
- **Brand colour = identity and emphasis** (masthead, title, the single key path). **Semantic colour = category/state** and follows the guide's data rule. Do not recolour a category because a brand colour is prettier.
- Compute contrast for brand pairs on the actual background; the lint does it for text. Large-text-only colours (a signature mid-tone) must not carry labels.
- Status colours (pass/warn/fail) only for actual status, not decoration.
- Keep brand dressing small: logo + palette + type + line weights. No brand patterns or textures unless they encode something. If the brand has a signature graphic device, use it only as structure (a divider, a path) and only when it does not compete with the model.

## 7. When the brand does not fit the subject
A test page, a partner project or a demo may not be the brand's own product (a drone-hardware lockup on a bakery page implies ownership). Use the tokens, **do not** place the logo unless a human confirms it belongs, and say so as an exception in the handoff.

## 8. Verify and report
Render both themes (`render.py page.html --theme both --pdf`) and check: ground and ink are the brand's, the accent appears once or as often as the guide allows, fonts loaded or the fallback is declared, logo variant and clear space correct, 0 lint errors. In the handoff list: brand files used (path + date or hash), rules applied, any exception (and why), and what is missing (e.g. no dark logo).
