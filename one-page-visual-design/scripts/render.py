#!/usr/bin/env python3
"""Render a one-page HTML/SVG design with headless Chrome: PNG, PDF, zoom tiles, layout lint.

Pure standard library (Python 3.8+) + a local Chrome/Chromium. Talks to Chrome over the DevTools
Protocol so the viewport is exact, the colour scheme is explicit, and the lint can wait for fonts.

  python3 render.py page.html                         # light PNG + lint -> ./render/
  python3 render.py page.html --theme both --pdf      # light+dark PNG, plus PDF at the CSS @page size
  python3 render.py page.html --tiles 2x2 --zoom 2    # four zoomed crops, to read small type
  python3 render.py page.html --region 100,300,500,300 --zoom 3
  python3 render.py page.html --no-png --strict       # lint only; exit 1 if any error
  python3 render.py page.html --freeze                # write page.static.html (scripts removed, SVG baked in)

Full workflow: references/render-and-critique-loop.md. If this script cannot run, use the plain
`Google Chrome --headless --screenshot / --print-to-pdf` commands documented there.
"""
import argparse, base64, json, os, re, shutil, signal, socket, struct, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
LINT_JS = HERE / "lint_page.js"
CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]


def find_chrome(explicit):
    for c in [explicit, os.environ.get("CHROME_BIN")]:
        if c and os.path.exists(c):
            return c
    for c in CHROME_CANDIDATES:
        if os.path.exists(c):
            return c
    for n in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"):
        p = shutil.which(n)
        if p:
            return p
    sys.exit("No Chrome/Chromium found. Install Chrome or pass --chrome PATH (or set CHROME_BIN).")


# ---------------------------------------------------------------- minimal WebSocket + CDP
class WS:
    def __init__(self, url, timeout=90):
        m = re.match(r"ws://([^:/]+):(\d+)(/.*)", url)
        host, port, path = m.group(1), int(m.group(2)), m.group(3)
        self.s = socket.create_connection((host, port), timeout=timeout)
        key = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((f"GET {path} HTTP/1.1\r\nHost: {host}:{port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                        f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            chunk = self.s.recv(4096)
            if not chunk:
                raise EOFError("websocket handshake failed")
            buf += chunk
        head, self.buf = buf.split(b"\r\n\r\n", 1)
        if b" 101 " not in head.split(b"\r\n")[0]:
            raise RuntimeError("websocket upgrade refused: " + head.decode(errors="replace")[:200])

    def _read(self, n):
        out = bytearray()
        if self.buf:
            take = self.buf[:n]; self.buf = self.buf[len(take):]; out += take
        while len(out) < n:
            chunk = self.s.recv(min(1 << 20, n - len(out)))
            if not chunk:
                raise EOFError("websocket closed")
            out += chunk
        return bytes(out)

    def send(self, text):
        data = text.encode(); n = len(data); hdr = bytearray([0x81])
        if n < 126: hdr.append(0x80 | n)
        elif n < 65536: hdr += bytes([0x80 | 126]) + struct.pack(">H", n)
        else: hdr += bytes([0x80 | 127]) + struct.pack(">Q", n)
        mask = os.urandom(4)
        self.s.sendall(bytes(hdr) + mask + bytes(b ^ mask[i & 3] for i, b in enumerate(data)))

    def recv(self):
        msg = bytearray()
        while True:
            b1, b2 = self._read(2); fin, op, ln = b1 & 0x80, b1 & 0x0F, b2 & 0x7F
            if ln == 126: ln = struct.unpack(">H", self._read(2))[0]
            elif ln == 127: ln = struct.unpack(">Q", self._read(8))[0]
            payload = self._read(ln)
            if op == 0x8: raise EOFError("websocket closed by Chrome")
            if op == 0x9: continue
            msg += payload
            if fin: return msg.decode()


class CDP:
    def __init__(self, ws):
        self.ws, self.n, self.events = ws, 0, []

    def call(self, method, params=None, sid=None):
        self.n += 1
        msg = {"id": self.n, "method": method, "params": params or {}}
        if sid: msg["sessionId"] = sid
        self.ws.send(json.dumps(msg))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == self.n:
                if "error" in m: raise RuntimeError(f"{method}: {m['error'].get('message')}")
                return m.get("result", {})
            self.events.append(m)

    def wait(self, event, sid, timeout=60):
        end = time.time() + timeout
        while True:
            for i, m in enumerate(self.events):
                if m.get("method") == event and m.get("sessionId") == sid:
                    del self.events[i]; return m
            if time.time() > end: raise TimeoutError(f"timed out waiting for {event}")
            m = json.loads(self.ws.recv()); self.events.append(m)

    def eval(self, sid, expr, await_promise=True):
        r = self.call("Runtime.evaluate", {"expression": expr, "awaitPromise": await_promise, "returnByValue": True}, sid)
        if "exceptionDetails" in r:
            d = r["exceptionDetails"]; raise RuntimeError("page JS error: " + (d.get("exception", {}).get("description") or d.get("text", "")))
        return r["result"].get("value")


class Chrome:
    def __init__(self, path):
        self.ud = tempfile.mkdtemp(prefix="opd-chrome-")
        args = [path, "--headless=new", "--remote-debugging-port=0", f"--user-data-dir={self.ud}", "--no-first-run",
                "--no-default-browser-check", "--disable-extensions", "--hide-scrollbars", "--force-color-profile=srgb",
                "--disable-background-networking", "--disable-component-update", "--disable-sync", "--mute-audio", "about:blank"]
        if hasattr(os, "geteuid") and os.geteuid() == 0: args.append("--no-sandbox")
        self.p = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        port_file = Path(self.ud) / "DevToolsActivePort"
        for _ in range(150):
            if port_file.exists() and len(port_file.read_text().split("\n")) >= 2: break
            if self.p.poll() is not None: sys.exit("Chrome exited at startup")
            time.sleep(0.1)
        else:
            self.close(); sys.exit("Chrome did not open a DevTools port within 15s")
        port, path_ = port_file.read_text().split("\n")[:2]
        self.cdp = CDP(WS(f"ws://127.0.0.1:{port.strip()}{path_.strip()}"))

    def close(self):
        try: self.cdp.call("Browser.close")
        except Exception: pass
        for _ in range(30):
            if self.p.poll() is not None: break
            time.sleep(0.1)
        if self.p.poll() is None:
            try: os.killpg(self.p.pid, signal.SIGKILL)
            except Exception: pass
        shutil.rmtree(self.ud, ignore_errors=True)


# ---------------------------------------------------------------- helpers
def png_size(b):
    return struct.unpack(">II", b[16:24]) if b[:8] == b"\x89PNG\r\n\x1a\n" else (0, 0)


def pdf_info(b):
    pages = len(re.findall(rb"/Type\s*/Page(?![s\w])", b))
    m = re.search(rb"/MediaBox\s*\[\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\]", b)
    mm = (round(float(m.group(3)) * 25.4 / 72), round(float(m.group(4)) * 25.4 / 72)) if m else None
    return pages, mm


def to_html(path):
    """SVG input is wrapped in a minimal HTML shell so the lint and PDF paths are identical."""
    if path.suffix.lower() != ".svg": return path, None
    svg = re.sub(r"<\?xml[^>]*\?>|<!DOCTYPE[^>]*>", "", path.read_text(encoding="utf-8"))
    tmp = path.with_name(f".{path.stem}.opd-wrap.html")
    tmp.write_text('<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0}svg{display:block}</style></head><body>' + svg + "</body></html>", encoding="utf-8")
    return tmp, tmp


def fmt_finding(kind, f, pad=30):
    box = f.get("box")
    where = ""
    if box:
        x, y, w, h = box
        where = f"  box=[{x},{y},{w},{h}]  zoom: --region {max(0, x - pad)},{max(0, y - pad)},{w + 2 * pad},{h + 2 * pad}"
    return f"  {kind:5s} {f['id']:20s} {f['msg']}{where}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page", help="HTML (or SVG) file")
    ap.add_argument("--out", help="output dir (default: ./render next to the page)")
    ap.add_argument("--size", help="override canvas size: A0-A4 + L|P (A3L) or WxH px (1920x1080)")
    ap.add_argument("--theme", choices=["light", "dark", "both"], default="light")
    ap.add_argument("--scale", type=float, default=1.0, help="device scale for PNG (1 = CSS px; 2 = retina)")
    ap.add_argument("--pdf", action="store_true", help="also print a vector PDF at the CSS @page size")
    ap.add_argument("--no-png", action="store_true")
    ap.add_argument("--no-lint", action="store_true")
    ap.add_argument("--strict", action="store_true", help="exit 1 if the lint reports errors or the PDF is not one page")
    ap.add_argument("--tiles", help="CxR zoom tiles of the canvas, e.g. 2x2")
    ap.add_argument("--region", help="x,y,w,h in canvas CSS px: one zoomed crop")
    ap.add_argument("--zoom", type=float, default=2.0, help="zoom for tiles/region (default 2)")
    ap.add_argument("--freeze", action="store_true", help="write <page>.static.html with scripts removed")
    ap.add_argument("--wait", type=float, default=0.4, help="extra seconds after load (default 0.4)")
    ap.add_argument("--chrome", help="path to Chrome/Chromium")
    a = ap.parse_args()

    src = Path(a.page).resolve()
    if not src.exists(): sys.exit(f"not found: {src}")
    page, tmp = to_html(src)
    out = Path(a.out) if a.out else src.parent / "render"
    if not a.out and HERE.parent in out.resolve().parents:
        out = Path(tempfile.gettempdir()) / "opd-render"; print(f"note: page is inside the skill folder; writing to {out} (pass --out to choose)", file=sys.stderr)
    out.mkdir(parents=True, exist_ok=True)
    themes = ["light", "dark"] if a.theme == "both" else [a.theme]
    lint_src = LINT_JS.read_text(encoding="utf-8")
    exit_code, summary = 0, []
    chrome = Chrome(find_chrome(a.chrome))
    cdp = chrome.cdp
    try:
        tid = cdp.call("Target.createTarget", {"url": "about:blank"})["targetId"]
        sid = cdp.call("Target.attachToTarget", {"targetId": tid, "flatten": True})["sessionId"]
        cdp.call("Page.enable", sid=sid)
        for theme in themes:
            tag = f"{src.stem}-{theme}"
            cdp.call("Emulation.setEmulatedMedia", {"features": [{"name": "prefers-color-scheme", "value": theme}]}, sid)
            cdp.call("Emulation.setDeviceMetricsOverride", {"width": 1600, "height": 1200, "deviceScaleFactor": 1, "mobile": False}, sid)
            cdp.call("Page.navigate", {"url": page.as_uri() + f"?theme={theme}"}, sid)
            cdp.wait("Page.loadEventFired", sid)
            cdp.eval(sid, lint_src, await_promise=False)
            cdp.eval(sid, f"document.fonts.ready.then(()=>new Promise(r=>setTimeout(r,{int(a.wait * 1000)})))")
            info = cdp.eval(sid, "(()=>{const c=document.querySelector('[data-canvas]')||document.querySelector('.canvas')||document.querySelector('svg')||document.body.firstElementChild;"
                                 "const r=c.getBoundingClientRect();const m=document.querySelector('meta[name=\"opd:size\"]');"
                                 "return {x:r.left+scrollX,y:r.top+scrollY,w:r.width,h:r.height,size:c.getAttribute('data-size')||(m&&m.content)||null}})()", await_promise=False)
            size_code = a.size or info["size"]
            if size_code and not a.size:
                pass
            W, H = int(round(info["w"])), int(round(info["h"]))
            cdp.call("Emulation.setDeviceMetricsOverride", {"width": W, "height": H, "deviceScaleFactor": a.scale, "mobile": False}, sid)
            cdp.eval(sid, "new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))")
            line = f"[{theme}] {size_code or 'undeclared'} canvas {W}x{H}px"

            def shot(name, clip, scale=1.0, dpr=None):
                if dpr is not None:
                    cdp.call("Emulation.setDeviceMetricsOverride", {"width": W, "height": H, "deviceScaleFactor": dpr, "mobile": False}, sid)
                r = cdp.call("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": True,
                             "clip": {"x": clip[0], "y": clip[1], "width": clip[2], "height": clip[3], "scale": scale}}, sid)
                data = base64.b64decode(r["data"]); (out / name).write_bytes(data)
                return name, png_size(data)

            cx, cy = info["x"], info["y"]
            if not a.no_png:
                n, (pw, ph) = shot(f"{tag}.png", (cx, cy, W, H))
                line += f"\n  png  {out / n} ({pw}x{ph})"
            if a.tiles:
                c, r_ = (int(v) for v in a.tiles.lower().split("x"))
                for j in range(r_):
                    for i in range(c):
                        x0, y0 = i * W / c, j * H / r_
                        n, (pw, ph) = shot(f"{tag}-tile-r{j + 1}c{i + 1}.png", (cx + x0, cy + y0, W / c, H / r_), a.zoom, dpr=1)
                        line += f"\n  tile {out / n} ({pw}x{ph})"
            if a.region:
                x, y, w, h = (float(v) for v in a.region.split(","))
                n, (pw, ph) = shot(f"{tag}-region.png", (cx + x, cy + y, w, h), a.zoom, dpr=1)
                line += f"\n  crop {out / n} ({pw}x{ph})"
            if a.pdf:
                code = size_code or ""
                m = re.match(r"A([0-4])([LP])?$", code, re.I)
                params = {"printBackground": True, "preferCSSPageSize": True, "displayHeaderFooter": False,
                          "marginTop": 0, "marginBottom": 0, "marginLeft": 0, "marginRight": 0}
                params["paperWidth"], params["paperHeight"] = W / 96, H / 96
                pdf = base64.b64decode(cdp.call("Page.printToPDF", params, sid)["data"])
                (out / f"{tag}.pdf").write_bytes(pdf)
                pages, mm = pdf_info(pdf)
                line += f"\n  pdf  {out / (tag + '.pdf')} ({pages} page{'s' if pages != 1 else ''}, MediaBox {mm[0]}x{mm[1]}mm)" if mm else f"\n  pdf  {out / (tag + '.pdf')} ({pages} pages)"
                if pages != 1:
                    line += f"\n  ERROR pdf-pages: PDF has {pages} pages; content overflows the @page box"; exit_code = 1 if a.strict else exit_code
                if m and mm:
                    ex = {"A0": (1189, 841), "A1": (841, 594), "A2": (594, 420), "A3": (420, 297), "A4": (297, 210)}["A" + m.group(1)]
                    if (m.group(2) or "L").upper() == "P": ex = (ex[1], ex[0])
                    if abs(mm[0] - ex[0]) > 3 or abs(mm[1] - ex[1]) > 3:
                        line += f"\n  ERROR pdf-size: MediaBox {mm[0]}x{mm[1]}mm != declared {code} {ex[0]}x{ex[1]}mm (@page size and data-size disagree)"; exit_code = 1 if a.strict else exit_code
            if a.freeze:
                html = cdp.eval(sid, "(()=>{const c=document.documentElement.cloneNode(true);c.querySelectorAll('script').forEach(s=>s.remove());return '<!doctype html>\\n'+c.outerHTML})()", await_promise=False)
                fz = src.with_name(src.stem + ".static.html"); fz.write_text(html, encoding="utf-8"); line += f"\n  html {fz} (scripts removed)"
            if not a.no_lint:
                opts = {"size": a.size} if a.size else {}
                rep = cdp.eval(sid, f"opdLint({json.dumps(opts)})")
                (out / f"{tag}.lint.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
                i = rep["info"]
                line += (f"\n  LINT {len(rep['errors'])} errors, {len(rep['warnings'])} warnings | words {i['words']} | whitespace {i['whitespacePct']}% | "
                         f"type tiers {i['typeTiers']} | title/body {i['titleOverMedian']}x | min contrast {i['minContrast']:.1f}")
                for kind, items in (("ERROR", rep["errors"]), ("warn", rep["warnings"])):
                    seen = {}
                    for f in items: seen.setdefault((f["id"], f["msg"]), []).append(f)
                    for group in seen.values():
                        line += "\n" + fmt_finding(kind, group[0]) + (f"  (+{len(group) - 1} identical)" if len(group) > 1 else "")
                if rep["errors"] and a.strict: exit_code = 1
            print(line)
    finally:
        chrome.close()
        if tmp: tmp.unlink(missing_ok=True)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
