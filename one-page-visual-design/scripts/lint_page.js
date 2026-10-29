/* one-page-visual-design: layout lint. Plain browser JS, no dependencies, does not mutate the DOM.
 * Run:  python3 scripts/render.py page.html        (injects this file via DevTools)
 *   or  paste into any browser console / javascript tool, then:  JSON.stringify(await opdLint(), null, 1)
 * Conventions it reads (all optional; see references/render-and-critique-loop.md):
 *   [data-canvas data-size="A3L"]  the page; size = A0-A4 + L|P, or "1920x1080" for screen pages; data-units="mm" if SVG units are real mm
 *   g[data-node] / .node           labelled SVG shape groups (shape + text) -> text-fit check
 *   [data-edge]                    connectors (path/line/polyline); data-edge-free = end may float; data-edge-label = label on a line
 *   [data-meta], h1 / [data-title] metadata strip and title
 * Returns {ok, canvas, errors[], warnings[], info{}}. Each finding: {id, msg, box:[x,y,w,h] in canvas px}.
 */
(function () {
  'use strict';
  const MM = 96 / 25.4;
  const ISO = { A0: [1189, 841], A1: [841, 594], A2: [594, 420], A3: [420, 297], A4: [297, 210] };
  const GENERIC = /^(serif|sans-serif|monospace|cursive|fantasy|system-ui|ui-[a-z-]+|-apple-system|blinkmacsystemfont|emoji|math|fangsong)$/i;

  function parseSize(code) {
    if (!code) return null;
    code = String(code).trim();
    let m = /^(A[0-4])([LP])?$/i.exec(code);
    if (m) {
      const [l, s] = ISO[m[1].toUpperCase()], portrait = (m[2] || 'L').toUpperCase() === 'P';
      const wmm = portrait ? s : l, hmm = portrait ? l : s;
      return { code: code.toUpperCase(), wmm, hmm, wpx: wmm * MM, hpx: hmm * MM, physical: true };
    }
    m = /^(\d+)x(\d+)$/i.exec(code);
    return m ? { code, wpx: +m[1], hpx: +m[2], physical: false } : null;
  }
  const minPtFor = (longMm) => (longMm <= 300 ? 7 : longMm <= 430 ? 8 : longMm <= 600 ? 10 : 14);

  // ---------- colour helpers (canvas parses any CSS colour syntax into sRGB) ----------
  const cx2d = document.createElement('canvas').getContext('2d', { willReadFrequently: true });
  function rgba(css) {
    if (!css || css === 'none' || /url\(|gradient|context-/.test(css)) return null;
    cx2d.clearRect(0, 0, 1, 1);
    cx2d.fillStyle = '#010203'; cx2d.fillStyle = css;
    if (cx2d.fillStyle === '#010203' && !/^#010203$/i.test(css)) return null;
    cx2d.fillRect(0, 0, 1, 1);
    const d = cx2d.getImageData(0, 0, 1, 1).data;
    return [d[0], d[1], d[2], d[3] / 255];
  }
  const over = (f, b) => [0, 1, 2].map((i) => f[i] * f[3] + b[i] * (1 - f[3])).concat(1);
  const lum = (c) => { const k = c.slice(0, 3).map((v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }); return 0.2126 * k[0] + 0.7152 * k[1] + 0.0722 * k[2]; };
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  const hue = (c) => { const [r, g, b] = c.map((v) => v / 255), mx = Math.max(r, g, b), mn = Math.min(r, g, b), d = mx - mn; if (d < 0.18 || mx < 0.15) return null; let h = mx === r ? ((g - b) / d) % 6 : mx === g ? (b - r) / d + 2 : (r - g) / d + 4; return ((h * 60) + 360) % 360; };

  const opacityChain = (el, stop) => { let o = 1; for (let e = el; e && e !== stop.parentElement; e = e.parentElement) { const v = parseFloat(getComputedStyle(e).opacity); if (!isNaN(v)) o *= v; } return o; };
  const hasBorder = (cs) => ['Top', 'Right', 'Bottom', 'Left'].some((s) => parseFloat(cs['border' + s + 'Width']) > 0 && cs['border' + s + 'Style'] !== 'none');
  const hasBox = (cs) => { const bg = rgba(cs.backgroundColor); return (bg && bg[3] > 0.05) || ['Top', 'Right', 'Bottom', 'Left'].some((s) => parseFloat(cs['border' + s + 'Width']) > 0 && cs['border' + s + 'Style'] !== 'none'); };

  // background colour under an HTML element (climbs ancestors); returns {c, unknown}
  function htmlBg(el) {
    const layers = [];
    for (let e = el; e; e = e.parentElement) {
      const cs = getComputedStyle(e), c = rgba(cs.backgroundColor);
      if (c && c[3] > 0) { layers.push(c); if (c[3] >= 0.99) break; }
      if (cs.backgroundImage && cs.backgroundImage !== 'none' && !(c && c[3] >= 0.99)) return { unknown: true };
    }
    let base = [255, 255, 255, 1];
    for (let i = layers.length - 1; i >= 0; i--) base = over(layers[i], base);
    return { c: base };
  }
  // background colour under a point on an SVG (topmost filled shape beneath it, else HTML background); skip = element(s) to ignore
  function svgBgAt(cx, cy, skip, fallbackEl) {
    const layers = []; let htmlHit = null;
    for (const e of document.elementsFromPoint(cx, cy)) {
      if (skip(e) || e.tagName.toLowerCase() === 'svg') continue;
      if (e instanceof SVGGraphicsElement) {
        if (!/^(rect|path|circle|ellipse|polygon)$/i.test(e.tagName)) continue;
        const cs = getComputedStyle(e);
        if (/url\(/.test(cs.fill)) return { unknown: true };
        const c = rgba(cs.fill); if (!c) continue;
        c[3] *= parseFloat(cs.fillOpacity) * opacityChain(e, document.body);
        if (c[3] > 0.02) { layers.push(c); if (c[3] >= 0.99) break; }
      } else { htmlHit = e; break; }
    }
    let base = [255, 255, 255, 1];
    if (!(layers.length && layers[layers.length - 1][3] >= 0.99)) { const b = htmlBg(htmlHit || fallbackEl || document.body); if (b.unknown) return b; base = b.c; }
    for (let i = layers.length - 1; i >= 0; i--) base = over(layers[i], base);
    return { c: base };
  }
  const svgBg = (textEl, r) => svgBgAt(r.left + r.width / 2, r.top + r.height / 2, (e) => e === textEl || textEl.contains(e), textEl.ownerSVGElement.parentElement);

  function fontInstalled(name) {
    for (const f of document.fonts) if (f.family.replace(/["']/g, '') === name && f.status === 'loaded') return true;
    const t = 'mmmmmmmmmmlli';
    for (const fb of ['monospace', 'serif', 'sans-serif']) {
      cx2d.font = `72px ${fb}`; const a = cx2d.measureText(t).width;
      cx2d.font = `72px "${name}", ${fb}`; if (cx2d.measureText(t).width !== a) return true;
    }
    return false;
  }

  const inter = (a, b, pad = 0) => !(a.right <= b.left + pad || b.right <= a.left + pad || a.bottom <= b.top + pad || b.bottom <= a.top + pad);
  const area = (r) => Math.max(0, r.width) * Math.max(0, r.height);
  const overlapArea = (a, b) => Math.max(0, Math.min(a.right, b.right) - Math.max(a.left, b.left)) * Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top));
  const short = (s, n = 48) => (s.length > n ? s.slice(0, n - 1) + '…' : s);

  function segInter(a, b, c, d) {
    const o = (p, q, r) => (q.x - p.x) * (r.y - p.y) - (q.y - p.y) * (r.x - p.x);
    return o(a, b, c) * o(a, b, d) < 0 && o(c, d, a) * o(c, d, b) < 0;
  }
  function samplePath(el, step) {
    const len = el.getTotalLength(), ctm = el.getScreenCTM(), pts = [];
    for (let l = 0; l <= len + 0.01; l += step) { const p = el.getPointAtLength(Math.min(l, len)); const q = new DOMPoint(p.x, p.y).matrixTransform(ctm); pts.push({ x: q.x, y: q.y }); }
    if (len > 0) { const p = el.getPointAtLength(len), q = new DOMPoint(p.x, p.y).matrixTransform(ctm); pts.push({ x: q.x, y: q.y }); }
    return pts;
  }

  async function opdLint(opts) {
    opts = opts || {};
    try { await document.fonts.ready; } catch (e) {}
    await Promise.all([...document.images].map((i) => (i.complete ? 0 : new Promise((r) => { i.onload = i.onerror = r; }))));
    const svgImgs = [...document.querySelectorAll('svg image')];
    await Promise.all(svgImgs.map((im) => new Promise((res) => {
      const i = new Image(); i.onload = () => { im._nw = i.naturalWidth; im._nh = i.naturalHeight; res(); }; i.onerror = () => { im._broken = true; res(); };
      i.src = im.getAttribute('href') || im.getAttribute('xlink:href') || '';
    })));
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));

    const canvas = document.querySelector('[data-canvas]') || document.querySelector('.canvas') || document.querySelector('svg') || document.body.firstElementChild;
    const cr = canvas.getBoundingClientRect();
    const meta = document.querySelector('meta[name="opd:size"]');
    const size = parseSize(opts.size || canvas.getAttribute('data-size') || (meta && meta.content));
    const errors = [], warnings = [];
    const rel = (r) => [Math.round(r.left - cr.left), Math.round(r.top - cr.top), Math.round(r.width), Math.round(r.height)];
    const add = (list, id, msg, r) => list.push({ id, msg, box: r ? rel(r) : undefined });
    const err = (id, msg, r) => add(errors, id, msg, r), warn = (id, msg, r) => add(warnings, id, msg, r);

    // ptPerPx: physical canvases map 1 CSS px of canvas width to (wmm/canvasPx) mm
    const ptPerPx = size && size.physical ? (size.wmm / cr.width) * (72 / 25.4) : 0.75;
    const minPt = opts.minPt || (size && size.physical ? minPtFor(Math.max(size.wmm, size.hmm)) : null);
    const minPx = size && !size.physical ? (opts.minPx || 14) : null;
    const canvasInfo = { w: Math.round(cr.width), h: Math.round(cr.height), declared: size ? size.code : null, ptPerPx: +ptPerPx.toFixed(4), minPt, minPx };

    if (size && (Math.abs(cr.width - size.wpx) > 3 || Math.abs(cr.height - size.hpx) > 3))
      err('canvas-size', `canvas is ${Math.round(cr.width)}x${Math.round(cr.height)}px but ${size.code} needs ${Math.round(size.wpx)}x${Math.round(size.hpx)}px (use mm units + matching @page size)`, cr);
    const se = document.scrollingElement;
    if (se.scrollWidth > cr.right + 3 || se.scrollHeight > cr.bottom + 3) warn('page-scrolls', `document extends beyond the canvas (${se.scrollWidth}x${se.scrollHeight}); stray content outside the page?`);

    // ---------- text inventory ----------
    const items = [], seenSvg = new Set();
    const tw = document.createTreeWalker(canvas, NodeFilter.SHOW_TEXT);
    for (let n; (n = tw.nextNode());) {
      const txt = n.nodeValue.replace(/\s+/g, ' ').trim(); const p = n.parentElement;
      if (!txt || !p || p.closest('script,style,title,defs,metadata,noscript,template,[hidden]')) continue;
      if (p.checkVisibility && !p.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true })) continue;
      const st = p.closest('text');
      if (st) {
        if (seenSvg.has(st)) continue; seenSvg.add(st);
        const r = st.getBoundingClientRect(); if (r.width < 0.5) continue;
        const cs = getComputedStyle(st), ctm = st.getScreenCTM(), sc = ctm ? Math.hypot(ctm.a, ctm.b) : 1;
        const col = rgba(cs.fill);
        items.push({ svg: true, el: st, text: st.textContent.replace(/\s+/g, ' ').trim(), rect: r, rects: [r], px: parseFloat(cs.fontSize) * sc, weight: +cs.fontWeight, family: cs.fontFamily, col, alpha: parseFloat(cs.fillOpacity) * opacityChain(st, canvas) });
      } else {
        const rg = document.createRange(); rg.selectNodeContents(n);
        const rects = [...rg.getClientRects()].filter((q) => q.width > 0.5 && q.height > 0.5); if (!rects.length) continue;
        const r = rg.getBoundingClientRect(), cs = getComputedStyle(p);
        items.push({ svg: false, el: p, text: txt, rect: r, rects, px: parseFloat(cs.fontSize), weight: +cs.fontWeight, family: cs.fontFamily, col: rgba(cs.color), alpha: opacityChain(p, canvas) });
      }
    }
    const words = items.reduce((s, i) => s + i.text.split(' ').length, 0);

    // ---------- per-text checks ----------
    const safe = (size && size.physical ? 6 * (cr.width / size.wmm) : 0.006 * cr.width);
    const fam1 = new Map();
    for (const it of items) {
      const pt = it.px * ptPerPx; it.pt = pt;
      if (minPt && pt < minPt - 0.05) err('font-too-small', `"${short(it.text)}" is ${pt.toFixed(1)}pt at print size (minimum ${minPt}pt for ${size.code})`, it.rect);
      else if (minPx && it.px < minPx - 0.05) err('font-too-small', `"${short(it.text)}" is ${it.px.toFixed(1)}px (minimum ${minPx}px for screen pages)`, it.rect);
      if (it.rect.left < cr.left - 1 || it.rect.top < cr.top - 1 || it.rect.right > cr.right + 1 || it.rect.bottom > cr.bottom + 1) err('text-outside-canvas', `"${short(it.text)}" extends outside the canvas`, it.rect);
      else if (it.rect.left < cr.left + safe || it.rect.top < cr.top + safe || it.rect.right > cr.right - safe || it.rect.bottom > cr.bottom - safe) warn('near-edge', `"${short(it.text)}" is inside the ~6mm unprintable/trim margin`, it.rect);
      if (it.svg && it.el.ownerSVGElement) {
        const sr = it.el.ownerSVGElement.getBoundingClientRect();
        if (it.rect.left < sr.left - 1 || it.rect.top < sr.top - 1 || it.rect.right > sr.right + 1 || it.rect.bottom > sr.bottom + 1) err('svg-clipped', `"${short(it.text)}" lies outside its SVG viewport and is clipped (move it inside the viewBox)`, it.rect);
      }
      const nw = it.text.split(' ').length;
      if (nw > (opts.maxProseWords || 28)) warn('prose-block', `${nw}-word text block "${short(it.text, 40)}"; turn prose into labels, numbers, annotations`, it.rect);
      // contrast
      if (it.col) {
        const bg = it.svg ? svgBg(it.el, it.rect) : htmlBg(it.el);
        if (bg.unknown) { it.contrast = null; }
        else {
          const f = over([it.col[0], it.col[1], it.col[2], it.col[3] * it.alpha], bg.c), cr2 = ratio(f, bg.c);
          const large = it.px >= 24 || (it.px >= 18.66 && it.weight >= 700), need = large ? 3 : 4.5;
          it.contrast = cr2;
          if (cr2 < need - 0.01) err('low-contrast', `"${short(it.text)}" contrast ${cr2.toFixed(2)}:1 < ${need}:1 (WCAG AA${large ? ' large text' : ''})`, it.rect);
        }
      }
      const first = (it.family.split(',')[0] || '').replace(/["']/g, '').trim();
      if (first && !GENERIC.test(first)) fam1.set(first, (fam1.get(first) || 0) + 1);
      // HTML: text spilling out of its visual box (vertical slack: glyph boxes exceed tight line-heights)
      if (!it.svg) {
        const lh = parseFloat(getComputedStyle(it.el).lineHeight), slack = isNaN(lh) ? 1 : Math.max(1, (it.rects[0].height - lh) / 2 + 1);
        for (let b = it.el; b && b !== canvas; b = b.parentElement) {
          const cs = getComputedStyle(b);
          if (b.hasAttribute('data-box') || hasBox(cs)) {
            const br = b.getBoundingClientRect();
            if (it.rect.left < br.left - 1 || it.rect.right > br.right + 1 || it.rect.top < br.top - slack || it.rect.bottom > br.bottom + slack) err('text-spills-box', `"${short(it.text)}" spills out of its box`, it.rect);
            break;
          }
        }
      }
    }
    for (const [name, n] of fam1) if (!fontInstalled(name)) warn('font-missing', `font "${name}" (${n} labels) is not installed/loaded; the browser falls back, so the render will not match other machines`);

    // ---------- clipped / scrolling HTML content ----------
    for (const el of canvas.querySelectorAll('*')) {
      if (el instanceof SVGElement) continue;
      const cs = getComputedStyle(el);
      if ((cs.overflowX !== 'visible' || cs.overflowY !== 'visible') && el !== canvas && (el.scrollWidth - el.clientWidth > 1 || el.scrollHeight - el.clientHeight > 1) && el.clientWidth > 0)
        err('clipped-content', `<${el.tagName.toLowerCase()}${el.className && typeof el.className === 'string' ? '.' + el.className.split(' ')[0] : ''}> hides overflowing content (${el.scrollWidth}x${el.scrollHeight} in ${el.clientWidth}x${el.clientHeight})`, el.getBoundingClientRect());
    }

    // ---------- text overlap ----------
    const lines = []; items.forEach((it, i) => it.rects.forEach((r) => lines.push({ i, r })));
    const reported = new Set();
    for (let a = 0; a < lines.length; a++) for (let b = a + 1; b < lines.length; b++) {
      if (lines[a].i === lines[b].i) continue;
      const A = lines[a].r, B = lines[b].r; if (!inter(A, B, 0)) continue;
      const ov = overlapArea(A, B) / Math.min(area(A), area(B));
      const key = lines[a].i + ':' + lines[b].i;
      if (ov > 0.12 && !reported.has(key)) { reported.add(key); err('text-overlap', `"${short(items[lines[a].i].text, 30)}" overlaps "${short(items[lines[b].i].text, 30)}"`, A); }
    }

    // ---------- SVG nodes: text must fit its shape ----------
    const nodes = [...canvas.querySelectorAll('g[data-node], g.node')];
    const nodeRects = [];
    for (const g of nodes) {
      const shape = g.querySelector('rect, circle, ellipse, polygon, path'); if (!shape) continue;
      const sr = shape.getBoundingClientRect(); nodeRects.push({ g, r: sr });
      for (const t of g.querySelectorAll('text')) {
        const tr = t.getBoundingClientRect(); if (tr.width < 0.5) continue;
        const o = Math.max(sr.left - tr.left, tr.right - sr.right, sr.top - tr.top, tr.bottom - sr.bottom);
        if (o > 0.75) err('svg-text-overflow', `"${short(t.textContent.trim())}" overflows its node by ${o.toFixed(1)}px; widen the node, shorten the label, or wrap into tspans`, tr);
        else if (shape.tagName === 'rect' && Math.min(tr.left - sr.left, sr.right - tr.right) < 0.012 * cr.width * 0.4) warn('node-tight', `"${short(t.textContent.trim())}" nearly touches its node edge (add padding)`, tr);
      }
    }
    for (let a = 0; a < nodeRects.length; a++) for (let b = a + 1; b < nodeRects.length; b++)
      if (overlapArea(nodeRects[a].r, nodeRects[b].r) > 16) warn('node-overlap', 'two nodes overlap', nodeRects[a].r);

    // ---------- connectors ----------
    const edges = [...canvas.querySelectorAll('[data-edge], path.edge, line.edge, polyline.edge')].filter((e) => typeof e.getTotalLength === 'function' && !e.closest('.legend, [data-legend]'));
    const tol = Math.max(6, 0.004 * cr.width);
    const targets = nodeRects.map((n) => n.r).concat([...canvas.querySelectorAll('[data-node]:not(g), [data-anchor], img')].map((e) => e.getBoundingClientRect()));
    const allNodes = targets.filter((r) => r.width > 0 && r.height > 0 && r.width < 0.5 * cr.width);
    const polys = [];
    for (const e of edges) {
      const pts = samplePath(e, 6); polys.push({ e, pts });
      if (e.hasAttribute('data-edge-free') || !targets.length) continue;
      for (const [label, p] of [['start', pts[0]], ['end', pts[pts.length - 1]]]) {
        if (!targets.some((r) => p.x >= r.left - tol && p.x <= r.right + tol && p.y >= r.top - tol && p.y <= r.bottom + tol))
          warn('edge-floating-end', `connector ${label} at (${Math.round(p.x - cr.left)},${Math.round(p.y - cr.top)}) touches no node (add data-edge-free if intentional)`, new DOMRect(p.x - 12, p.y - 12, 24, 24));
      }
      const touches = (r, p) => p.x >= r.left - tol && p.x <= r.right + tol && p.y >= r.top - tol && p.y <= r.bottom + tol;
      for (const r of allNodes) {
        if (touches(r, pts[0]) || touches(r, pts[pts.length - 1])) continue;
        if (pts.filter((p) => p.x > r.left + 1 && p.x < r.right - 1 && p.y > r.top + 1 && p.y < r.bottom - 1).length >= 2) { warn('edge-crosses-node', 'a connector runs through a node it does not connect (skipped a tier? reroute through a gap)', r); break; }
      }
      const hit = items.find((it) => !it.el.closest('[data-edge-label]') && pts.slice(2, -2).some((p) => p.x > it.rect.left + 1 && p.x < it.rect.right - 1 && p.y > it.rect.top + 1 && p.y < it.rect.bottom - 1));
      if (hit) warn('edge-crosses-text', `a connector runs through "${short(hit.text)}"`, hit.rect);
    }
    let crossings = 0;
    for (let a = 0; a < polys.length; a++) for (let b = a + 1; b < polys.length; b++) {
      const P = polys[a].pts, Q = polys[b].pts;
      for (let i = 0; i < P.length - 1; i++) for (let j = 0; j < Q.length - 1; j++) if (segInter(P[i], P[i + 1], Q[j], Q[j + 1])) { crossings++; i += 2; break; }
    }
    if (crossings > (opts.maxCrossings || 6)) warn('connector-tangle', `${crossings} connector crossings; reorder nodes or route differently`);

    // ---------- diagram scale (silent letterboxing) ----------
    if (size && size.physical) {
      // design unit = 1 mm at A3 (template convention); pages drawn in real millimetres set data-units="mm" on the canvas
      const designW = canvas.getAttribute('data-units') === 'mm' ? size.wmm : (size.wmm >= size.hmm ? 420 : 297), pxPerMm = cr.width / designW;
      for (const sv of canvas.querySelectorAll('svg[viewBox]')) {
        const r = sv.getBoundingClientRect(); if (r.width < 0.4 * cr.width) continue;
        const a = sv.getScreenCTM() ? sv.getScreenCTM().a : 1, ratio = a / pxPerMm;
        if (Math.abs(ratio - 1) > 0.03) warn('svg-scale', `diagram renders at ${Math.round(ratio * 100)}% of design scale (letterboxed: its viewBox does not match the stage); set viewBox="0 0 ${(r.width / pxPerMm).toFixed(0)} ${(r.height / pxPerMm).toFixed(0)}" and re-check type sizes`, r);
      }
    }

    // ---------- non-text contrast of meaningful strokes (WCAG 1.4.11: 3:1) ----------
    const strokeCheck = (el, where, label) => {
      const cs = getComputedStyle(el), sc = rgba(cs.stroke); if (!sc || !(parseFloat(cs.strokeWidth) > 0)) return;
      const bg = where(); if (!bg || bg.unknown) return;
      const f = over([sc[0], sc[1], sc[2], sc[3] * opacityChain(el, canvas)], bg.c), c = ratio(f, bg.c);
      if (c < 3 - 0.01) warn('graphic-contrast', `${label} stroke has ${c.toFixed(2)}:1 contrast with its background (< 3:1); darken it in this theme, or add weight and a label`, el.getBoundingClientRect());
    };
    for (const e of edges) { const L = e.getTotalLength(), p = e.getPointAtLength(L / 2), q = new DOMPoint(p.x, p.y).matrixTransform(e.getScreenCTM()); strokeCheck(e, () => svgBgAt(q.x, q.y, (x) => x === e, e.ownerSVGElement.parentElement), 'connector'); }
    for (const g of nodes) { const sh = g.querySelector('rect, circle, ellipse, polygon, path'); if (!sh) continue; const r = sh.getBoundingClientRect(); strokeCheck(sh, () => svgBgAt(r.left - 3, r.top + r.height / 2, (x) => g.contains(x), g.ownerSVGElement.parentElement), 'node outline'); }

    // ---------- images ----------
    for (const im of canvas.querySelectorAll('img')) {
      const r = im.getBoundingClientRect();
      if (!im.complete || !im.naturalWidth) { err('img-broken', `image ${short(im.getAttribute('src') || '', 50)} did not load`, r); continue; }
      if (size && size.physical && r.width > 0) { const dpi = im.naturalWidth / (r.width / (cr.width / (size.wmm / 25.4))); if (dpi < 96) err('img-low-res', `${short(im.getAttribute('src') || '', 40)} is ~${Math.round(dpi)} dpi at print size (<96); regenerate/upscale`, r); else if (dpi < 150) warn('img-soft', `${short(im.getAttribute('src') || '', 40)} is ~${Math.round(dpi)} dpi at print size (<150)`, r); }
    }

    for (const im of canvas.querySelectorAll('svg image')) {
      const r = im.getBoundingClientRect(), src = short(im.getAttribute('href') || im.getAttribute('xlink:href') || '', 40);
      if (im._broken || !im._nw) { err('img-broken', `svg image ${src} did not load`, r); continue; }
      if (size && size.physical && r.width > 0) {
        const dw = Math.min(r.width, r.height * (im._nw / im._nh)), dpi = im._nw / (dw / (cr.width / (size.wmm / 25.4)));
        if (dpi < 96) err('img-low-res', `${src} is ~${Math.round(dpi)} dpi at print size (<96); regenerate/upscale`, r); else if (dpi < 150) warn('img-soft', `${src} is ~${Math.round(dpi)} dpi at print size (<150)`, r);
      }
    }

    // ---------- hierarchy, metadata, density ----------
    const sizes = items.map((i) => i.pt).sort((a, b) => a - b);
    const med = sizes.length ? sizes[Math.floor(sizes.length / 2)] : 0, top = sizes.length ? sizes[sizes.length - 1] : 0;
    const clusters = []; for (const s of sizes) if (!clusters.length || s / clusters[clusters.length - 1] > 1.18) clusters.push(s);
    if (items.length > 12 && (clusters.length < 3 || top / med < 2.2)) warn('weak-hierarchy', `type tiers=${clusters.length}, title/median=${(top / (med || 1)).toFixed(1)}x; aim for 3+ tiers and a title >= 2.2x body`);
    const title = canvas.querySelector('h1, [data-title]'); if (!title || !title.textContent.trim()) warn('no-title', 'no <h1> or [data-title]; the title states what the page is for');
    const mEl = canvas.querySelector('[data-meta]') || canvas, metaTxt = mEl.innerText || mEl.textContent;
    if (!/20\d\d-\d\d-\d\d/.test(metaTxt)) warn('meta-date', 'no ISO date (YYYY-MM-DD) in [data-meta]; prints go stale without a date');
    if (!/\bv\d+(\.\d+)*\b/i.test(metaTxt)) warn('meta-version', 'no version (v1, v0.3) in [data-meta]');
    if (!/\b(exploration|reference|draft)\b/i.test(metaTxt)) warn('meta-status', 'no status (exploration|reference) in [data-meta]');
    if (words > (opts.maxWords || 320)) warn('dense', `${words} words on the page (budget ~${opts.maxWords || 320}); cut or move detail to a linked page`);

    // ---------- whitespace estimate (advisory) ----------
    const cols = 60, cell = cr.width / cols, rows = Math.ceil(cr.height / cell), grid = new Uint8Array(cols * rows), carea = area(cr);
    const mark = (r, pad = 0) => { const x0 = Math.max(0, Math.floor((r.left - cr.left - pad) / cell)), x1 = Math.min(cols - 1, Math.floor((r.right - cr.left + pad) / cell)), y0 = Math.max(0, Math.floor((r.top - cr.top - pad) / cell)), y1 = Math.min(rows - 1, Math.floor((r.bottom - cr.top + pad) / cell)); for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) grid[y * cols + x] = 1; };
    items.forEach((i) => i.rects.forEach((r) => mark(r, 3)));
    const hues = new Set();
    const paper = (htmlBg(canvas).c) || [255, 255, 255, 1];
    const prominent = (c, k) => c && ratio(over([c[0], c[1], c[2], c[3] * (k === undefined ? 1 : k)], paper), paper) >= 1.25;
    for (const el of canvas.querySelectorAll('svg *, img, div, section, header, footer, aside, figure, li, span, p')) {
      const r = el.getBoundingClientRect(); if (r.width < 1 || r.height < 1 || area(r) > 0.6 * carea) continue;
      if (el instanceof SVGGeometryElement) {
        const cs = getComputedStyle(el), f = rgba(cs.fill), s = rgba(cs.stroke), fo = parseFloat(cs.fillOpacity);
        const seen = f && f[3] * fo > 0.05, stroked = s && parseFloat(cs.strokeWidth) > 0 && prominent(s, 1);
        const filled = seen && (prominent(f, fo) || (stroked && area(r) < 0.05 * carea));
        if (filled) mark(r); else if (stroked && el.getTotalLength) samplePath(el, Math.max(4, cell / 2)).forEach((p) => mark(new DOMRect(p.x, p.y, 0, 0)));
        if (f && f[3] * fo > 0.05) { const h = hue(f); if (h !== null) hues.add(Math.floor(h / 30)); }
        if (stroked) { const h = hue(s); if (h !== null) hues.add(Math.floor(h / 30)); }
      } else if (el.tagName === 'IMG') mark(r);
      else if (!(el instanceof SVGElement)) { const cs = getComputedStyle(el), b = rgba(cs.backgroundColor); if (prominent(b, 1) || hasBorder(cs)) { mark(r); const h = b && b[3] > 0.3 ? hue(b) : null; if (h !== null) hues.add(Math.floor(h / 30)); } }
    }
    const whitespace = Math.round(100 * (1 - grid.reduce((a, b) => a + b, 0) / grid.length));
    if (whitespace < 25) warn('no-whitespace', `only ~${whitespace}% of the page is empty space; white space is part of the design (Librande). Cut or split.`);
    if (hues.size > 7) warn('many-hues', `${hues.size} distinct hue families in use; colour should encode category, not decorate`);

    return {
      ok: errors.length === 0, canvas: canvasInfo, errors, warnings,
      info: { words, textItems: items.length, nodes: nodes.length, edges: edges.length, crossings, typeTiers: clusters.map((c) => +c.toFixed(1)), titleOverMedian: +(top / (med || 1)).toFixed(2), whitespacePct: whitespace, hueFamilies: hues.size, minContrast: items.filter((i) => i.contrast).reduce((m, i) => Math.min(m, i.contrast), 99) }
    };
  }
  window.opdLint = opdLint; window.opdParseSize = parseSize;
})();
