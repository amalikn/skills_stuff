#!/usr/bin/env python3
"""Click cells of a .drawio page in draw.io's own viewer (headless browser) and print each probed cell's opacity after every click: the
test for `data:action/json` links such as `look.click_isolate`. Writes nothing but an HTML page beside --out and optional screenshots.

Needs Playwright for Python and a Chromium-family browser (default channel msedge), run with an interpreter that has them; the pack's
own venv does not. The viewer is draw.io's `js/viewer-static.min.js` for the same version as the desktop app, from the jgraph/drawio tag
(https://raw.githubusercontent.com/jgraph/drawio/v<version>/src/main/webapp/js/viewer-static.min.js): the desktop bundle holds only the
editor. A target written `!<id>` runs through draw.io's click path with the cell given (Graph.customLinkClicked), which is what a real
click does and works off-screen; a plain `<id>` is a mouse click at the middle of the cell's longest run (an edge) or its centre.

Usage:
    viewer_click.py FILE.drawio --viewer viewer-static.min.js --page 2 --click '!e2e-a-x-2,!e2e-a-x-2' --probe e2e-a-y-1 --out DIR
Exit: 0 when every target was found and clicked, 1 when one was not, 2 on bad arguments or no Playwright.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

#: The oldest Python this script runs on (Playwright is imported only when it runs).
REQUIRES_PYTHON = (3, 11)
#: Milliseconds allowed for the page to load and the viewer to start, and to wait after each click.
LOAD_MS, SETTLE_MS = 60000, 1200

#: Each probed cell's drawn opacity and text opacity (its state's style, where transient actions write).
PROBE_JS = """ids => ids.map(id => { var c = V.graph.model.getCell(id), s = c && V.graph.view.getState(c);
    return [id, s ? String(mxUtils.getValue(s.style, 'opacity', '100')) : 'missing', s ? String(mxUtils.getValue(s.style, 'textOpacity', '100')) : '-']; })"""
#: Where a mouse click lands: the middle of an edge's longest run (on the line), else the cell's centre; null when not drawn.
SPOT_JS = """id => { var s = V.graph.view.getState(V.graph.model.getCell(id)), r = V.graph.container.getBoundingClientRect();
    if (!s) return null; var p = s.absolutePoints, best = null, len = -1;
    if (p && p.length > 1) { for (var i = 1; i < p.length; i++) { var l = Math.abs(p[i].x - p[i-1].x) + Math.abs(p[i].y - p[i-1].y);
        if (l > len) { len = l; best = [(p[i].x + p[i-1].x) / 2, (p[i].y + p[i-1].y) / 2]; } } return [r.left + best[0], r.top + best[1]]; }
    return [r.left + s.getCenterX(), r.top + s.getCenterY()]; }"""
#: A click through draw.io's own path, the clicked cell given; false when the cell has no link.
LINK_JS = """id => { var c = V.graph.model.getCell(id), l = c && V.graph.getLinkForCell(c); if (!l) return false;
    V.graph.customLinkClicked(l, c); return true; }"""
#: Counts draw.io's action runs, so a click that ran nothing shows.
COUNT_JS = """() => { window.RUNS = 0; var g = V.graph, f = g.executeCustomActions;
    g.executeCustomActions = function() { RUNS++; return f.apply(this, arguments); }; }"""


def viewer_html(viewer: Path, drawing: str, page: int) -> str:
    """A page that opens one diagram of a drawing in draw.io's viewer and exposes it as `window.V`.

    Args:
        viewer: the viewer-static.min.js file.
        drawing: the .drawio file text (a leading banner comment is dropped).
        page: the diagram, counted from 0.

    Returns:
        The HTML.
    """
    xml = drawing.split("-->", 1)[1] if drawing.lstrip().startswith("<!--") else drawing
    cfg = json.dumps({"xml": xml, "page": page, "toolbar": "", "nav": True, "border": 10})
    return (f'<html><body style="margin:0"><div id="g"></div><script src="{viewer.resolve().as_uri()}"></script><script>'
            f"var d = document.getElementById('g'); d.setAttribute('data-mxgraph', {json.dumps(cfg)});"
            "GraphViewer.createViewerForElement(d, function(v) { window.V = v; });</script></body></html>")


def parse_targets(text: str) -> list[tuple[str, bool]]:
    """The cells to click, in order.

    Args:
        text: comma-separated ids; `!id` clicks through draw.io's click path, `id` with the mouse.

    Returns:
        [(id, through the click path)].
    """
    return [(t[1:], True) if t.startswith("!") else (t, False) for t in (x.strip() for x in text.split(",")) if t.lstrip("!")]


def run(args: argparse.Namespace) -> int:
    """Open the page, click each target, print the runs and the probed opacities after each.

    Args:
        args: the parsed command line.

    Returns:
        0 when every target was clicked, 1 when one was missing or had no link, 2 without Playwright.
    """
    try:
        from playwright.sync_api import sync_playwright   # imported here: an optional dependency of this one front end
    except ImportError:
        print("viewer_click: Playwright is not installed for this interpreter", file=sys.stderr)
        return 2
    args.out.mkdir(parents=True, exist_ok=True)
    page_file = args.out / "viewer.html"
    page_file.write_text(viewer_html(args.viewer, args.file.read_text(encoding="utf-8"), args.page - 1), encoding="utf-8")
    missed = 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel=args.channel, headless=True)
        try:
            pg = browser.new_page(viewport={"width": 1800, "height": 1400})
            pg.goto(page_file.as_uri(), timeout=LOAD_MS)
            pg.wait_for_function("window.V && V.graph", timeout=LOAD_MS)
            pg.evaluate(COUNT_JS)
            print("before", json.dumps(pg.evaluate(PROBE_JS, args.probe)))
            for n, (cid, via_path) in enumerate(parse_targets(args.click), 1):
                if via_path:
                    hit = pg.evaluate(LINK_JS, cid)
                else:
                    spot = pg.evaluate(SPOT_JS, cid)
                    hit = spot is not None
                    if hit:
                        pg.mouse.click(spot[0], spot[1])
                pg.wait_for_timeout(SETTLE_MS)
                missed += not hit
                print(f"click {n} {'!' if via_path else ''}{cid}: runs {pg.evaluate('() => RUNS')}", json.dumps(pg.evaluate(PROBE_JS, args.probe)))
                if args.screenshots:
                    pg.screenshot(path=str(args.out / f"after-{n}.png"), full_page=True)
        finally:
            browser.close()
    return 1 if missed else 0


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0, 1 or 2 as the module header says.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file", type=Path)
    ap.add_argument("--viewer", type=Path, required=True, help="draw.io's js/viewer-static.min.js, same version as the desktop app")
    ap.add_argument("--page", type=int, default=1, help="the page, counted from 1 (default 1)")
    ap.add_argument("--click", required=True, help="comma-separated cell ids; !id runs draw.io's click path with the cell given")
    ap.add_argument("--probe", nargs="*", default=[], help="cell ids whose opacity is printed after each click")
    ap.add_argument("--out", type=Path, required=True, help="folder for the viewer page and screenshots")
    ap.add_argument("--channel", default="msedge", help="Playwright browser channel (default msedge)")
    ap.add_argument("--screenshots", action="store_true", help="save a full-page screenshot after each click")
    args = ap.parse_args(argv)
    if not args.file.is_file() or not args.viewer.is_file():
        print("viewer_click: the drawing and the viewer must exist", file=sys.stderr)
        return 2
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
