# Layout recipes

Nine tested layouts for process, cycle, value-chain, supply-chain and related one-pagers, plus a composite for an end-to-end page. Each recipe is an **SVG fragment file** in `assets/recipes/` (read only the one you need). `new_page.py` drops it into `assets/page-template.html` with the size block, title and metadata set:

```bash
python3 <skill>/scripts/new_page.py design/one-page/cycle.html --recipe R1 --size A3L --title "From order to delivery: where time and cost accumulate"
python3 <skill>/scripts/new_page.py design/one-page/schedule.html --spec my-schedule.json   # R9, generated from your JSON
```
Fragments use the template vocabulary (`.node .c1-.c6 .ev-proposed .ev-open`, `.t1 .t2 .t3 .num .halo`, `.edge .edge.loop .rule`, `.legend`) and **A3 millimetres** inside the stage `<svg viewBox="0 0 392 215">` (portrait 269 x 338). Every recipe was generated through `new_page.py`, rendered and linted with `--strict` in light and dark: 0 errors, 0 warnings. The sample words are a neutral manufacturing vocabulary: replace them, do not keep them.

The grammar comes from the information problem (`visual-grammars.md`), then the recipe. Combine at most two, aligned on a shared axis.

| The reader needs to know... | Recipe |
|---|---|
| who does what, in what order, with which handoffs and rework | R1 swimlane |
| a loop in which the outcome feeds the input | R2 cycle |
| where time and cost accumulate along stages | R3 value chain |
| what is made vs bought, from where, and where we are exposed | R4 supply chain |
| how the physical flow runs, how long each station takes, where it chokes | R5 factory flow |
| what the object is made of and who supplies each part | R6 anatomy + callouts |
| how a quantity (capacity, headcount, cash) grows through gates | R7 space-time band |
| which items are covered by which options, and the gaps | R8 matrix |
| how long each step takes on a real time axis, what is critical, and the gates | R9 time-scaled swimlane |
| the whole product cycle on one sheet | Composite (end of file) |

## Connector toolkit (read before drawing any arrow)
Ugly connectors are the most common visible defect. Rules, in order of importance:
1. **Derive endpoints from the nodes**; never type coordinates for a node you may move later. Leave from the **mid-point of the edge facing the flow** and arrive at the opposite edge. Several connectors on one edge: ports >= 5 mm apart.
2. **One style per page:** orthogonal elbows with a 3 mm corner radius (processes, handoffs) or smooth S-curves (quantity ribbons between columns). Never diagonal lines mixed with elbows. Leaders from callouts to a part are the one exception: a short horizontal run, then a straight line.
3. **One arrowhead,** at the end only (`marker-end="url(#arrow)"` with `context-stroke` so it takes the line colour). Ribbons whose direction is the column order get no head.
4. Stroke about 0.5 mm; **feedback/rework = dashed accent** (`.edge.loop`); dependencies thin grey.
5. **Label with a verb** on the line (`text.halo[data-edge-label]`), only when the relation is not obvious.
6. **Never pass through an unrelated node or label.** Route through the gutter between nodes. If a flow must skip a tier, the node is in the wrong tier (R4).
7. **Crossings:** order nodes by their neighbours (barycentre) before drawing; any crossing that remains meets at right angles; more than 6 on a page means regroup or split. The lint warns (`connector-tangle`).

```python
def node(x, y, w, h, label, sub="", cls="c1", extra="", id_=""):
    """Labelled node. Width rule: >= 2.2 mm per character of the longest t2 label (1.7 mm for t3) + 8 mm."""
    t = (f'<text class="t2" x="{w/2:g}" y="{h/2-0.8:g}" text-anchor="middle">{label}</text>'
         f'<text class="t3" x="{w/2:g}" y="{h/2+3.6:g}" text-anchor="middle">{sub}</text>') if sub else \
        f'<text class="t2" x="{w/2:g}" y="{h/2:g}" text-anchor="middle">{label}</text>'
    i = f' id="{id_}"' if id_ else ""
    return f'<g class="node {cls}{(" "+extra) if extra else ""}" data-node{i} transform="translate({x:g} {y:g})"><rect width="{w:g}" height="{h:g}" rx="2.4"/>{t}</g>'

def elbow(x1, y1, x2, y2, xm=None, r=3):
    """Horizontal-vertical-horizontal connector with rounded corners; use as the d attribute of a path.edge."""
    if abs(y1 - y2) < 0.01:
        return f"M{x1:g} {y1:g} H{x2:g}"
    xm = (x1 + x2) / 2 if xm is None else xm
    s = 1 if y2 > y1 else -1
    return (f"M{x1:g} {y1:g} H{xm-r:g} Q{xm:g} {y1:g} {xm:g} {y1+s*r:g} "
            f"V{y2-s*r:g} Q{xm:g} {y2:g} {xm+r:g} {y2:g} H{x2:g}")
# usage: <path class="edge" data-edge d="{elbow(104, 85, 154, 125)}"/>   (x1,y1 = right edge mid of A; x2,y2 = left edge mid of B)

def ortho(pts, r=2.5):
    """Any orthogonal polyline (list of (x, y) corners) with rounded corners, for routes that need more than one bend."""
    d = f"M{pts[0][0]:g} {pts[0][1]:g}"
    sg = lambda a, b: (b > a) - (b < a)
    for i in range(1, len(pts) - 1):
        (ax, ay), (bx, by), (cx, cy) = pts[i - 1], pts[i], pts[i + 1]
        rr = min(r, (abs(bx - ax) + abs(by - ay)) / 2, (abs(cx - bx) + abs(cy - by)) / 2)
        d += f" L{bx - sg(ax, bx) * rr:g} {by - sg(ay, by) * rr:g} Q{bx:g} {by:g} {bx + sg(bx, cx) * rr:g} {by + sg(by, cy) * rr:g}"
    return d + f" L{pts[-1][0]:g} {pts[-1][1]:g}"
```

Two more rules:
8. **One channel, one meaning.** Outline dash on a node = evidence status (proposed/open); dash on a connector = flow type (rework, feedback). Never reuse a device for two meanings, and in grayscale check they still read differently (a failure path and an "assumed" box both dashed is a collision).
9. **One accent per view.** Spend the accent on the single thing the page exists to show (the bottleneck, or the critical path, or the exception), not on all three. Everything else gets weight, outline or position. Check the accent's contrast as a stroke in **both** themes (lint `graphic-contrast`).

## R1 Swimlane process flow
**Use for** a production/delivery process with owners (Engineering, Sourcing, Factory, Quality...), handoffs and a rework loop.
**Structure:** lanes = owners (rows); columns = stages in order (left to right); one node per stage in the owning lane; handoff = elbow crossing a lane boundary; rework = dashed accent loop under the failing stage returning to the stage that fixes it.
**Encode:** lane = owner; node colour = work type; dashed accent = rework; put duration/yield in `t3` under the node when it matters; a gate is a node whose label starts with "Gate:".
**Rules:** <= 7 columns x <= 5 lanes on A3; every lane has at least two nodes (else merge the lane); column heads are nouns/verbs, not slogans; the rework loop is the place to show the exception the model must survive.
**Pitfall:** lane bands filled so strongly they outweigh the nodes (keep `--panel`).
**Fragment:** `assets/recipes/R1-swimlane.svgfrag`. Start a page with it: `python3 <skill>/scripts/new_page.py page.html --recipe R1 --size A3L --title "..."`.


## R2 Closed cycle (racetrack)
**Use for** a real loop: design -> source -> make -> test -> ship -> support -> field data -> design. Deletion test: if nothing returns to the start, it is a flow (R1), not a cycle.
**Structure:** racetrack, not a circle (straight runs keep labels horizontal and readable); 6-10 nodes; an arrow on every segment; the centre carries the loop's key figure and the sentence on what returns.
**Encode:** node colour = owner or phase; centre figure = cycle time or yield; mark the entry point when there is a true start.
**Rules:** direction is clockwise; the return edge is labelled with what comes back; no node on a corner arc (put nodes on straights).
**Pitfall:** a "generic loop" whose last arrow carries no information.
**Fragment:** `assets/recipes/R2-cycle.svgfrag`. Start a page with it: `python3 <skill>/scripts/new_page.py page.html --recipe R2 --size A3L --title "..."`.


## R3 Value chain (width = lead time, height = cost share)
**Use for** showing where time and money accumulate along stages.
**Structure:** chevrons left to right, **width proportional to days**; below, bars on the **same x positions**, **height proportional to % of unit cost**. Optional third row: value-added vs waiting time.
**Rules:** both rows share the x-axis so a long stage and an expensive stage are visibly different stages; state totals (sum of days, 100% of cost) and check that they add up; if stages overlap in time use a Gantt-style band (R7), not chevrons.
**Pitfall:** equal-width chevrons that encode nothing (Librande: every mark has a reason).
**Fragment:** `assets/recipes/R3-value-chain.svgfrag`. Start a page with it: `python3 <skill>/scripts/new_page.py page.html --recipe R3 --size A3L --title "..."`.


## R4 Supply chain (tiers, make vs buy, exposure)
**Use for** sourcing, sovereignty and dependency: what is made in-house, what is bought and from where, where one supplier can stop the line.
**Structure:** columns = tiers (raw material -> components -> sub-assemblies -> product); **every node sits in the tier where it is consumed**; ribbons run left to right with **width = share of unit cost** (or mass, or lead time: say which); a badge marks single-source or long-lead items.
**Encode:** fill = make / bought-domestic / bought-imported (and the word in `t3`, never colour alone); badge = single source; add a country code in `t3` when origin matters.
**Rules:** no tier skipping (a flow that crosses a column is a misplaced node); order nodes in each column by their neighbours to avoid crossings; <= 14 nodes: group parts ("fasteners x40") instead of listing BOM lines; a bought component has no incoming flow unless its upstream is itself a risk worth showing.
**Pitfall:** a BOM dump; flags and logos that do not explain a dependency.
**Fragment:** `assets/recipes/R4-supply-chain.svgfrag`. Start a page with it: `python3 <skill>/scripts/new_page.py page.html --recipe R4 --size A3L --title "..."`.


## R5 Factory flow (floor + cycle times)
**Use for** physical layout, station order, cycle times and the bottleneck.
**Structure:** top: floor zones (dashed boxes) with numbered stations in material-flow order (a U shape keeps first and last stations together); bottom: **cycle-time bars on the same numbering** with a takt line. The bottleneck gets the accent outline in both places.
**Rules:** number stations; arrows only along the material path (information flows are a different colour or a different page); state where takt comes from (demand / shift length); add WIP buffers as small squares between stations when queues matter.
**Pitfall:** a pretty floor plan without times, or times without the plan.
**Fragment:** `assets/recipes/R5-factory-flow.svgfrag`. Start a page with it: `python3 <skill>/scripts/new_page.py page.html --recipe R5 --size A3L --title "..."`.


## R6 Anatomy with callouts (the talk's default composition)
**Use for** an object: its parts, who makes or buys each, which parts matter. This is Librande's template: title, white space, **main illustration in the middle, callouts around it** [23:11]-[24:32].
**Structure:** hero in the centre (SVG built from primitives, a photo/render, or an AI illustration, see `illustration-and-assets.md`); callouts left and right, **ordered by the y position of their anchor**; each callout = number + name + one fact + chip; leader = short horizontal run then a straight line to a dot on the part. Keep an invisible `rect[data-anchor]` the leaders end in.
**Rules:** no leader crosses another; <= 8 callouts per side, numbered clockwise from top left; text is never baked into the image (it will be wrong); label the illustration "illustrative, not CAD" when it is generated.
**Pitfall:** floating callouts with no leader; a hero that is only decoration.
**Fragment:** `assets/recipes/R6-anatomy.svgfrag`. Start a page with it: `python3 <skill>/scripts/new_page.py page.html --recipe R6 --size A3L --title "..."`.


## R7 Space-time band (Minard / Spore style)
**Use for** a quantity that grows through gates: monthly capacity, headcount, cumulative cash, qualified suppliers.
**Structure:** x = time, **band thickness = quantity** (symmetric around the centre line, like the Napoleon chart [13:16]) or a plain line; gates as vertical rules with pills and one-line meanings; values labelled on the band edge. Put the time element in early [29:25].
**Rules:** label start and end values; each gate states its pass criterion; time ticks every quarter or year; two quantities mean two bands or two panels, not two colours in one.
**Pitfall:** an unlabelled ramp that looks like a growth slogan.
**Fragment:** `assets/recipes/R7-space-time.svgfrag`. Start a page with it: `python3 <skill>/scripts/new_page.py page.html --recipe R7 --size A3L --title "..."`.


## R8 Matrix (top-down)
**Use for** items x options/attributes: make vs buy per part, coverage, readiness, risk. Draw the grid first, then fill every cell [33:56]-[34:41].
**Structure:** rows = items; columns = options then attributes; mark grammar (full / partial / none) via `<use>` symbols; numbers as text; risk as a short coloured bar plus the word.
**Rules:** an empty cell is information, so draw it (dashed ring); a row with no mark is a **gap**: ring it in the accent colour; <= 2 dimensions (a 4-D table breaks down [36:23]); sort rows by the key that matters (risk, lead time).
**Pitfall:** a table in rounded boxes: if flattening it to text loses nothing, it was a table, not a visual.
**Fragment:** `assets/recipes/R8-matrix.svgfrag`. Start a page with it: `python3 <skill>/scripts/new_page.py page.html --recipe R8 --size A3L --title "..."`.


## R9 Time-scaled swimlane (the production schedule)
**Use for** when the real time axis matters: lead times, the critical path, gates. This is R1 with x = time to scale.
**Generator:** write a JSON spec (lanes, tasks with start/end/label/sub/status/critical, links, milestones; example `assets/recipes/R9-timeline-lanes.spec.json`), then `python3 <skill>/scripts/new_page.py page.html --spec spec.json` (or `scripts/lanes_gantt.py spec.json > frag.svgfrag` and `--fragment frag.svgfrag`). The generator packs bars into rows per lane, puts a label outside the bar when it does not fit, draws rounded orthogonal finish-to-start links from bar edges, rules for gates, and gives `critical` tasks the one accent outline.
**Rules:** bar length = duration, so the long bar is the long job; a link that would run through another bar is the signal to set `"row"` on the tasks of that lane (put the task that links downward on the lowest row) or give the link an `"xm"` time for its vertical run; the critical path is the longest chain, computed from the data, not by eye; compress a dead period with a labelled axis break, never silently; a day-before/after-night page can use two linear segments with a visible gap.
**Pitfall:** bars with no scale on the axis; every bar accented.
```json
{"axis": {"start": 0, "end": 70, "step": 10, "label": "days from order"},
 "lanes": [{"id": "eng", "label": "Engineering"}, {"id": "src", "label": "Sourcing"}],
 "tasks": [{"id": "t1", "lane": "eng", "start": 0, "end": 8, "label": "Freeze design", "sub": "drawings + BOM"},
           {"id": "t2", "lane": "src", "start": 8, "end": 38, "label": "Long-lead parts", "critical": true, "row": 0}],
 "links": [{"from": "t1", "to": "t2"}],
 "milestones": [{"at": 8, "label": "G1", "text": "design frozen"}],
 "legend": "lane = owner, bar length = duration to scale, accent = critical path"}
```

## Composite: end-to-end product cycle on one sheet
When the brief is the whole lifecycle (design -> sourcing -> manufacturing -> test -> delivery -> support), choose **one primary grammar** (a swimlane R1 or R9, or a cycle R2, as the spine) and **at most one secondary** aligned to it. Align stage columns across bands: a shared x per stage is what turns three diagrams into one model.

```
+------------------------------------------------------------------------------+
| TITLE: what the page explains                       STATUS | VERSION | DATE   |
| purpose sentence                                                              |
+------------------------------------------------------------------------------+
| INPUTS  |  SPINE (55-60% of height): R1/R9 swimlane or R2 cycle, one   | OUTPUTS |
| (left,  |  column per stage; hero illustration of the product feeds    | + return|
|  10%)   |  in from the left or sits in the cycle centre; gates marked  | path    |
|         |  as pills on the stage they close                            | (field  |
+---------+--------------------------------------------------------------+ data -> |
| SECONDARY BAND (20-25%), same x per stage: R3 lead-time/cost bars, or    | design) |
| R5 cycle-time bars, or R7 capacity band                                   |         |
+------------------------------------------------------------------------------+
| legend (with the diagram) | evidence + open questions, near what they affect       |
+------------------------------------------------------------------------------+
```
Rules for the composite: one dominant element (the spine, or the hero); tiers 1-3 visible from 2 m / 1 m / 40 cm; the exception path (rework, supply shock, failed gate) drawn once, in the accent; supply tiers (R4) and the factory floor (R5) are **separate linked pages** unless the brief fits them in the secondary band; a concrete worked example (one unit, one order, one lot) goes beside the rule it proves.

## Adapting a recipe
- Replace the sample words first; then re-grid. Node width >= longest label x 2.2 mm + 8 mm (`t2`), x 1.7 mm for `t3`; height 16-20 mm with a sub-line.
- The stage is exactly 392 x 215 A3-mm (portrait 269 x 338) because the masthead and footer rows are fixed. Content below y = 215 is clipped by the SVG (lint `svg-clipped`); a viewBox that does not match the stage letterboxes the whole diagram (lint `svg-scale` prints the viewBox to use). If you change the masthead or footer height, change the viewBox with it.
- More than 14 nodes or 320 words: split into an overview plus one page per stage, with a page locator ("P3 of 6") in the corner; do not shrink type.
- Portrait: rotate the flow top to bottom; `new_page.py --size A3P` sets the 269 x 338 viewBox; recipes are landscape, so re-lay them.
- Keep the legend inside the SVG, next to what it explains, using the same classes as the nodes.
- Test after every structural change: `python3 <skill>/scripts/render.py page.html --strict`.
