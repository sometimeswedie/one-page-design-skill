#!/usr/bin/env python3
"""Time-scaled swimlane (Gantt-like) SVG fragment for assets/page-template.html, from a JSON spec.

  python3 lanes_gantt.py spec.json > frag.svgfrag        then:  new_page.py page.html --fragment frag.svgfrag
  python3 new_page.py page.html --spec spec.json         (one step)

Spec (see assets/recipes/R9-timeline-lanes.spec.json):
  axis        {"start": 0, "end": 60, "step": 10, "label": "days from order"}
  lanes       [{"id": "eng", "label": "Engineering"}]
  tasks       [{"id": "t1", "lane": "eng", "start": 0, "end": 8, "label": "Design freeze", "sub": "drawings + BOM",
                "cls": "c1", "status": "decided|proposed|open", "critical": false}]
  links       [{"from": "t1", "to": "t2", "xm": 9, "label": "", "loop": false}]      xm = time of the vertical run (optional)
  milestones  [{"at": 8, "label": "G1", "text": "design frozen"}]
  legend      one line of text (optional)
Rules baked in: x is time to scale; lanes are owners; bars are packed into rows per lane; a label that does not fit inside its
bar goes outside to the right (and that space is reserved); connectors are orthogonal with rounded corners and start/end on bar
edges; `critical` gets the single accent outline. Geometry is A3 mm for the template stage (392 x 215). Standard library only.
"""
import json, sys
from xml.sax.saxutils import escape

W, H = 392, 215
X0, X1 = 40.0, 390.0            # plot area
Y0 = 12.0                       # first lane
T2, T3 = 2.15, 1.65             # mm per character at t2 (bold 3.9) and t3 (3.0): estimates, the lint is the judge
BH, GAP = 16.0, 3.0


def ortho(pts, r=2.5):
    d = f"M{pts[0][0]:g} {pts[0][1]:g}"
    for i in range(1, len(pts) - 1):
        (ax, ay), (bx, by), (cx, cy) = pts[i - 1], pts[i], pts[i + 1]
        rr = min(r, (abs(bx - ax) + abs(by - ay)) / 2, (abs(cx - bx) + abs(cy - by)) / 2)
        sg = lambda a, b: (b > a) - (b < a)
        d += f" L{bx - sg(ax, bx) * rr:g} {by - sg(ay, by) * rr:g} Q{bx:g} {by:g} {bx + sg(bx, cx) * rr:g} {by + sg(by, cy) * rr:g}"
    return d + f" L{pts[-1][0]:g} {pts[-1][1]:g}"


def build(spec):
    ax = {"start": 0, "end": 60, "step": 10, "label": "time", **spec.get("axis", {})}
    lanes, tasks = spec["lanes"], spec["tasks"]
    sx = (X1 - X0) / (ax["end"] - ax["start"])
    X = lambda t: X0 + (t - ax["start"]) * sx
    lane_idx = {l["id"]: i for i, l in enumerate(lanes)}
    ms = spec.get("milestones", [])

    # ---- measure and pack rows per lane
    info = {}
    for t in tasks:
        x0, x1 = X(t["start"]), X(t["end"]); w = max(x1 - x0, 3.0); x1 = x0 + w
        lab, sub = t["label"], t.get("sub", "")
        inside_label = len(lab) * T2 + 4 <= w
        inside_sub = bool(sub) and inside_label and len(sub) * T3 + 4 <= w
        out = []
        if not inside_label: out.append((lab, "t2"))
        if sub and not inside_sub: out.append((sub, "t3"))
        out_w = sum(len(s) * (T2 if c == "t2" else T3) + 3 for s, c in out)
        info[t["id"]] = dict(t=t, x0=x0, x1=x1, w=w, il=inside_label, isub=inside_sub, out=out, occ0=x0, occ1=x1 + (out_w + 1.5 if out else 0))
    rows = {l["id"]: [] for l in lanes}
    for t in sorted(tasks, key=lambda t: ("row" not in t, t["start"], t["end"])):
        i = info[t["id"]]; r = rows[t["lane"]]
        if "row" in t:                       # explicit row: use it when a connector would otherwise cross another bar
            while len(r) <= t["row"]: r.append(-1e9)
            r[t["row"]] = max(r[t["row"]], i["occ1"]); i["row"] = t["row"]; continue
        for k, end in enumerate(r):
            if i["occ0"] >= end + 2: r[k] = i["occ1"]; i["row"] = k; break
        else: r.append(i["occ1"]); i["row"] = len(r) - 1
    nrows = [max(1, len(rows[l["id"]])) for l in lanes]
    avail = H - Y0 - 12 - (22 if ms else 2)
    pitch = BH + GAP
    while sum(n * pitch + 5 for n in nrows) > avail and pitch > 12.5: pitch -= 0.5
    if sum(n * pitch + 5 for n in nrows) > avail:
        sys.exit(f"too many rows ({sum(nrows)}) for one page; group tasks or split the page")
    bh = min(BH, pitch - 2.5)
    natural = [n * pitch + 5 for n in nrows]
    extra = max(0.0, (avail - sum(natural)) / len(lanes)); extra = min(extra, 14.0)
    ytop, y = [], Y0
    for nat in natural: ytop.append(y); y += nat + extra
    bottom = y - 2
    lane_h = [nat + extra - 2 for nat in natural]

    o = []
    # ---- axis, lanes
    o.append(f'<text class="t3" x="0" y="6" style="font-weight:700">{escape(str(ax["label"]).upper())}</text>')
    t = ax["start"]
    while t <= ax["end"] + 1e-9:
        o.append(f'<line class="rule" x1="{X(t):g}" x2="{X(t):g}" y1="9" y2="{bottom:g}" stroke-dasharray=".8 1.4"/><text class="t3" x="{X(t):g}" y="6" text-anchor="middle">{t:g}</text>')
        t += ax["step"]
    for i, l in enumerate(lanes):
        h = lane_h[i]
        o.append(f'<rect x="0" y="{ytop[i]:g}" width="392" height="{h:g}" rx="2" fill="var(--panel)" opacity=".6"/>')
        words = l["label"].upper().split(); line1, line2 = l["label"].upper(), ""
        if len(line1) * T3 > 34 and len(words) > 1: line1, line2 = words[0], " ".join(words[1:])
        o.append(f'<text class="t3" x="3" y="{ytop[i] + 6:g}" style="font-weight:700">{escape(line1)}</text>' + (f'<text class="t3" x="3" y="{ytop[i] + 10.4:g}" style="font-weight:700">{escape(line2)}</text>' if line2 else ""))
    for m in ms:
        o.append(f'<line class="rule" x1="{X(m["at"]):g}" x2="{X(m["at"]):g}" y1="9" y2="{bottom + 2:g}" stroke="var(--ink-3)" stroke-dasharray="1.6 1.2"/>')
    # ---- tasks
    for i in info.values():
        t = i["t"]; li = lane_idx[t["lane"]]; cls = t.get("cls", f"c{li % 6 + 1}")
        ev = {"proposed": " ev-proposed", "open": " ev-open"}.get(t.get("status", ""), "")
        y = ytop[li] + 1.5 + (lane_h[li] - (nrows[li] * pitch + 3)) / 2 + i["row"] * pitch; i["y"], i["yc"] = y, y + bh / 2
        st = ' style="stroke:var(--accent);stroke-width:1.2px"' if t.get("critical") else ""
        txt = ""
        if i["il"] and i["isub"]:
            txt = f'<text class="t2" x="{i["w"] / 2:g}" y="{bh / 2 - 0.6:g}" text-anchor="middle">{escape(t["label"])}</text><text class="t3" x="{i["w"] / 2:g}" y="{bh / 2 + 4:g}" text-anchor="middle">{escape(t["sub"])}</text>'
        elif i["il"]:
            txt = f'<text class="t2" x="{i["w"] / 2:g}" y="{bh / 2 + 1.4:g}" text-anchor="middle">{escape(t["label"])}</text>'
        o.append(f'<g class="node {cls}{ev}" data-node id="{escape(t["id"])}" transform="translate({i["x0"]:g} {y:g})"><rect{st} width="{i["w"]:g}" height="{bh:g}" rx="1.6"/>{txt}</g>')
        if i["out"]:
            xx = i["x1"] + 1.8; parts = []
            for s, c in i["out"]:
                parts.append(f'<tspan class="{c}"{" style=%sfill:var(--ink-2)%s" % (chr(34), chr(34)) if c == "t3" else ""}>{escape(s)}</tspan>')
            o.append(f'<text class="t2" x="{xx:g}" y="{y + bh / 2 + 1.4:g}">' + '<tspan dx="0"> </tspan>'.join(parts) + '</text>')
    # ---- links
    for k in spec.get("links", []):
        a, b = info[k["from"]], info[k["to"]]; x1, y1, x2, y2 = a["x1"], a["yc"], b["x0"], b["yc"]
        if x2 < x1 - 0.5:
            print(f"warning: link {k['from']}->{k['to']} starts before its predecessor ends; skipped (reorder, or draw start-to-start by hand)", file=sys.stderr); continue
        if abs(y1 - y2) < 0.01:
            pts = [(x1, y1), (x2, y2)]; xm = (x1 + x2) / 2
        elif x2 - x1 < 6:   # finish-to-start with (almost) no gap: leave from the end of the bar, drop, enter the next bar's start
            lx = max(a["x0"] + a["w"] / 2, x1 - 2.5); ly = a["y"] + bh if y2 > y1 else a["y"]
            pts = [(lx, ly), (lx, y2), (x2, y2)]; xm = lx
        else:
            xm = X(k["xm"]) if "xm" in k else (x1 + x2) / 2
            xm = min(max(xm, x1 + 1.5), x2 - 1.5); pts = [(x1, y1), (xm, y1), (xm, y2), (x2, y2)]
        o.append(f'<path class="edge{" loop" if k.get("loop") else ""}" data-edge d="{ortho(pts)}"/>')
        if k.get("label"):
            o.append(f'<text class="t3 halo" data-edge-label x="{xm:g}" y="{(y1 + y2) / 2 + 1:g}" text-anchor="middle">{escape(k["label"])}</text>')
    # ---- milestone pills (rules were drawn earlier, under the bars)
    for m in ms:
        x = X(m["at"])
        o.append(f'<g class="node c1" data-node transform="translate({x - 9:g} {bottom + 2:g})"><rect width="18" height="8" rx="1.5"/><text class="t2" x="9" y="5.7" text-anchor="middle">{escape(m["label"])}</text></g>'
                 + (f'<text class="t3" x="{x:g}" y="{bottom + 15:g}" text-anchor="middle">{escape(m["text"])}</text>' if m.get("text") else ""))
    if spec.get("legend"):
        o.append(f'<g class="legend"><text class="t3" x="0" y="{H - 5:g}" style="font-weight:700">LEGEND</text><text class="t3" x="20" y="{H - 5:g}">{escape(spec["legend"])}</text></g>')
    return "\n".join(o)


if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(__doc__)
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    print(build(spec))
