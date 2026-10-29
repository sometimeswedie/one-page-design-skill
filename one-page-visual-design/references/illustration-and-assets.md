# Illustration, icons and images

Librande's template puts **one main illustration in the middle** and callouts around it [24:19], keeps everything purposeful [22:24], and prints vector [24:32]. The diagram and every word stay deterministic SVG; images only supply what a drawing of boxes cannot: the look of a physical thing or place.

## 1. Decide whether the page needs a picture
| The subject is... | Use |
|---|---|
| a physical object, place or product (anatomy, floor, site) | a hero illustration is load-bearing: R6 in `layout-recipes.md` |
| a process, flow, system, matrix, timeline | no hero; diagram only. A picture here is decoration |
| a process about a physical product | a small hero of the product as an **anchor** (where the flow starts/ends), not wallpaper |

If you cannot say what information the picture encodes (shape, scale, position of parts, context), leave it out. Never add "mood" imagery.

## 2. Options, in order of preference
1. **SVG built from primitives** (rectangles, circles, paths): perfectly editable, themeable, sharp at any size. Good for schematic top/side views and plans.
2. **Supplied assets** (project photos, CAD renders, logos in `brand/`): authoritative for shape. Prefer these as reference input for option 3.
3. **AI-generated illustration** (an image-generation tool or API): for a hero when no asset exists. Generate the *picture only*; callouts, labels and numbers are SVG on top.
4. **Icons:** one hand-built SVG family (below). Do not generate icons one at a time with an image model.

## 3. Capability check (do this once, before planning a generated hero)
1. Which image tools exist in this session? In Codex the built-in `imagegen` skill / `image_gen` tool is the default (it saves under `$CODEX_HOME/generated_images/`; copy the chosen file into the project's `assets/`, never leave a referenced asset there). In Claude Code, look at the tool list (for example an MCP image tool with `generate_image`, `remove_background`, `upscale_image`) and at project docs (`brand/`, README, AGENTS.md/CLAUDE.md) for a media prompt kit, approved models and a credit rule. Prior generations in the repo usually encode tool and model in their file names: reuse the winner for consistency.
2. API keys come from the environment or the project's config. Never write a key into a file, log or prompt.
3. Generation usually **costs credits**. Use the tool's quote/balance call if it has one. Budget rule unless the project says otherwise: one hero plus at most three retries per page; no batch of variants without a reason.
4. No tool available, or no budget: build the hero as SVG (option 1) and say so in the handoff.

## 4. Prompting a diagram-friendly hero
Structure: **subject + view + style + palette + background + margins + exclusions**, plus reference images for fidelity.
```
Technical illustration of <object>, <view: top-down | three-quarter | exploded view | cut-away | side elevation>,
matching the attached reference photos (shape, proportions, number of <arms/parts>).
Flat vector look, uniform thin dark outlines, limited palette <hex list from the brand tokens>,
plain light-grey background, subject centred with generous empty margin on every side for callout lines.
No text, no labels, no numbers, no logos, no watermark, no people.
```
- Use **reference images** (image-edit / reference-capable models) for products; text-only prompts invent parts. Say the part counts explicitly.
- **One style clause, one model, one seed (if exposed) per page** so a set of images matches. When regenerating one image, reuse the exact style clause.
- Ask for a **plain or transparent background**; then use the tool's background removal. Place the cut-out on a `--panel` plate so it works in light and dark.
- Match the aspect ratio of the slot (the R6 slot is 136 x 170 mm = 4:5).
- Text rendered by the model is wrong more often than not: never rely on it; the "no text" clause is mandatory.

## 5. Accept or reject
View it at 100% (use `--region` on the page and the raw file), against the reference.
- Reject: wrong part counts (arms, rotors, wheels), impossible joins, garbled text or logos, a style that disagrees with the rest of the page, busy backgrounds, cropped subject, faces/people.
- Accept only if every fact it implies is true or labelled. Add **"illustrative, not to scale / not CAD"** in the footer or beside the hero when it is generated.
- Keep the **provenance**: tool, model, prompt, reference files, date, output path, and whether it was edited (the project's `assets/PROVENANCE.md`, one block per image). Check the tool's licence for the intended use; do not depict third-party logos or identifiable people.

## 6. Prepare for the page
- **Resolution:** at least 150 dpi at printed size (lint `img-soft` under 150, `img-low-res` under 96). A 136 mm hero on A3 needs >= 800 px wide; on A1 (2x) >= 1600 px. Upscale with the tool's upscaler or regenerate larger. Resize/convert on macOS with built-ins: `sips -Z 1600 in.png --out out.png` (longest edge) and `sips -s format jpeg -s formatOptions 85 in.png --out out.jpg` (opaque photos only; keep PNG/WebP for cut-outs with alpha).
- **Files:** keep them in `assets/` next to the page and reference them relatively. A 1-3 MB hero is fine; a page whose assets total tens of MB is not a deliverable. If the HTML must be single-file, base64 the images last, and only if small.
- **Placement:** inside the stage SVG: `<image href="assets/hero.png" x="128" y="30" width="136" height="170" preserveAspectRatio="xMidYMid meet"/>` plus an invisible `<rect data-anchor ...>` of the same box for leader lines. Both the lint and render.py load it.
- **Dark theme:** transparent PNGs with dark outlines vanish on dark. Use a plate, a theme-specific file, or an outline that works on both (`<image class="hero-light">` / `.hero-dark` toggled by `[data-theme]`).
- Run `python3 scripts/render.py page.html --theme both --tiles 2x2` after adding images; they change contrast, dpi and whitespace.

## 7. Icons (one family)
Hand-build them in the same 24-unit grid, one stroke weight, round caps and joins, no fills, `currentColor`. Reuse via `<use>`. Do not mix with emoji, generated icons or a second library. If the brand specifies icon geometry (stroke weight, caps, joins, corner style), change `.ico` to match: this set is the neutral default. Icons are for recognition aids on repeated categories, not decoration; give each a text label.
```svg
<defs>
  <style>.ico{fill:none;stroke:currentColor;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}</style>
  <symbol id="i-radial" viewBox="0 0 24 24"><circle class="ico" cx="12" cy="12" r="3.2"/><path class="ico" d="M12 2.8v3M12 18.2v3M2.8 12h3M18.2 12h3M5.5 5.5l2.1 2.1M16.4 16.4l2.1 2.1M18.5 5.5l-2.1 2.1M7.6 16.4l-2.1 2.1"/></symbol>
  <symbol id="i-box" viewBox="0 0 24 24"><path class="ico" d="M3.5 7.5L12 3l8.5 4.5v9L12 21l-8.5-4.5zM3.5 7.5L12 12l8.5-4.5M12 12v9"/></symbol>
  <symbol id="i-check" viewBox="0 0 24 24"><circle class="ico" cx="12" cy="12" r="9"/><path class="ico" d="M7.8 12.4l2.9 2.9 5.5-6"/></symbol>
  <symbol id="i-alert" viewBox="0 0 24 24"><path class="ico" d="M12 3.5L21.5 20h-19zM12 10v4.5M12 17.4v.2"/></symbol>
</defs>
<!-- use: <g style="color:var(--ink)"><use href="#i-box" x="40" y="60" width="10" height="10"/></g> -->
```
Rendered and checked at 3x zoom: the four glyphs share weight and corner style. Size an icon at least 6 mm at A3 so strokes survive print.

## 8. Logos and brand marks
Use the supplied SVG (never redraw or recolour it); respect clear space and minimum size from the brand guide; use the dark-surface variant in dark theme (see `brand-and-tokens.md`).
