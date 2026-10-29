#!/usr/bin/env python3
"""Measure the layout quality of every page of a drawing: arrows, crossings, shared runs, bends, arrow length, arrows through boxes and
overlapping boxes. Read-only, stdlib only.

Why (2026-10-29, operator: layout quality analysis): the layout audit says clean or not and count_crossings counts crossings and shared runs;
neither says how long or bent the arrows are or whether an arrow runs through a box or label it does not join. This is the baseline the
routing and placement work is measured against, from the drawn file, so any page of any consumer is measured the same way.

Measures per page (paths from drawio.read, so ends are resolved on their boxes and group offsets applied):
    arrows    arrows with a path of two or more points
    cross     crossings between runs of different arrows (count_crossings.crossings)
    shared    pairs of runs lying along each other within 8 px (count_crossings.alongside)
    bends     changes of direction along the arrows (repeated and collinear points ignored)
    length    total arrow length in px
    through   an arrow run passing through the inside of a leaf box (one holding no other box) that is not one of the arrow's ends or its own
              label (a label belongs to the arrow whose id starts its id, else, when no arrow joins it, to the nearest arrow within 3 px of its centre); 2 px inset, so
              a run along an edge does not count
    overlap   pairs of leaf boxes, both labelled, that overlap by more than 2 px each way

Usage:
    layout_quality.py FILE.drawio [--all]                 # pages with crossings, shared runs, arrows through boxes or overlaps (--all: every page)
    layout_quality.py AFTER.drawio --compare BEFORE.drawio   # pages whose measures changed, and the totals
    layout_quality.py FILE.drawio --json                  # every page as JSON
Exit: 0 when measured (compare: no page worse), 1 when a file cannot be read, 2 on bad arguments, 3 when a compared page got worse
(more crossings, shared runs, arrows through boxes or overlaps; bends and length are reported, not judged).
Runtime: about a second on a 40-page drawing.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from count_crossings import alongside, crossings, wire_runs
from drawio import read

#: The oldest Python this script runs on (stdlib only).
REQUIRES_PYTHON = (3, 11)

#: The measures, in report order; JUDGED are those a compare fails on when they rise.
MEASURES = ("arrows", "cross", "shared", "bends", "length", "through", "overlap")
JUDGED = ("cross", "shared", "through", "overlap")


def bends(path: list) -> int:
    """How many times a path changes direction.

    Args:
        path: [[x, y], ...].

    Returns:
        The count; repeated points and points on a straight line are not bends.
    """
    pts = [tuple(p) for k, p in enumerate(path) if k == 0 or tuple(p) != tuple(path[k - 1])]
    n = 0
    for a, b, c in zip(pts, pts[1:], pts[2:]):
        if (b[0] - a[0]) * (c[1] - b[1]) != (b[1] - a[1]) * (c[0] - b[0]):
            n += 1
    return n


def length(path: list) -> float:
    """A path's length.

    Args:
        path: [[x, y], ...].

    Returns:
        The sum of its segment lengths in px.
    """
    return sum(((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5 for a, b in zip(path, path[1:]))


def _inside(outer: list, inner: list) -> bool:
    """Whether one rectangle holds another.

    Args:
        outer: [x, y, width, height].
        inner: [x, y, width, height].

    Returns:
        True when inner lies within outer (edges may touch).
    """
    return (outer[0] <= inner[0] and outer[1] <= inner[1] and inner[0] + inner[2] <= outer[0] + outer[2]
            and inner[1] + inner[3] <= outer[1] + outer[3])


def leaves(shapes: list[dict]) -> list[dict]:
    """The boxes that hold no other box (lanes, frames and stripes hold boxes; boxes and labels do not).

    Args:
        shapes: drawio.read layout shapes, [{"id", "label", "geo"}].

    Returns:
        The shapes with a positive size that hold no other shape with a positive size.
    """
    sized = [s for s in shapes if s["geo"][2] > 0 and s["geo"][3] > 0]
    return [s for s in sized if not any(o is not s and o["geo"] != s["geo"] and _inside(s["geo"], o["geo"]) for o in sized)]


def _run_through(run: tuple, geo: list, inset: float = 2) -> bool:
    """Whether a horizontal or vertical run passes through a rectangle's inside.

    Args:
        run: ((x1, y1), (x2, y2)).
        geo: [x, y, width, height].
        inset: how far inside the edges a run must be to count.

    Returns:
        True when the run enters the rectangle shrunk by inset; diagonal runs are not judged.
    """
    (x1, y1), (x2, y2) = run
    x0, y0, x9, y9 = geo[0] + inset, geo[1] + inset, geo[0] + geo[2] - inset, geo[1] + geo[3] - inset
    if y1 == y2:
        return y0 < y1 < y9 and min(x1, x2) < x9 and max(x1, x2) > x0
    if x1 == x2:
        return x0 < x1 < x9 and min(y1, y2) < y9 and max(y1, y2) > y0
    return False


def label_owner(box: dict, wires: list[dict]) -> str | None:
    """The arrow a box is the label of: the one whose id starts the box's id (the engine names a label `<arrow>-l`), else, for a box no
    arrow joins, the arrow nearest its centre when within 3 px (a label sits on its arrow; the Overview names group labels apart from
    their arrows). A box an arrow joins is a box, never a label, so an arrow through its middle still counts.

    Args:
        box: a layout shape, {"id", "label", "geo"}.
        wires: the page's wires with paths.

    Returns:
        The arrow's id, or None when the box is no arrow's label.
    """
    named = [w["id"] for w in wires if box["id"].startswith(w["id"] + "-")]
    if named:
        return max(named, key=len)
    if any(box["id"] in (w.get("source_id"), w.get("target_id")) for w in wires):
        return None
    x, y, bw, bh = box["geo"]
    near = [(read.distance_to_path((x + bw / 2, y + bh / 2), w["path"]), w["id"]) for w in wires]
    best = min(near, default=None)
    return best[1] if best and best[0] <= 3 else None


def page_quality(page: dict) -> dict:
    """The measures of one page.

    Args:
        page: one entry of drawio.read.pages().

    Returns:
        {measure: value} for every name in MEASURES, plus "where": the ids behind "through" and "overlap".
    """
    wires = [w for w in page["wires"] if len(w["path"]) > 1]
    runs = wire_runs(wires, "")
    boxes = leaves(page["shapes"])
    owner = {b["id"]: label_owner(b, wires) for b in boxes}
    where = []
    through = 0
    for w in wires:
        own = {w["id"], w.get("source_id"), w.get("target_id")}
        for b in boxes:
            if b["id"] in own or owner[b["id"]] == w["id"]:
                continue
            if any(_run_through(r, b["geo"]) for r in runs.get(w["id"], [])):
                through += 1
                where.append(f"through {w['id']} > {b['id']}")
    labelled = [b for b in boxes if b["label"]]
    overlap = 0
    for i, a in enumerate(labelled):
        ax, ay, aw, ah = a["geo"]
        for b in labelled[i + 1:]:
            bx, by, bw, bh = b["geo"]
            if min(ax + aw, bx + bw) - max(ax, bx) > 2 and min(ay + ah, by + bh) - max(ay, by) > 2:
                overlap += 1
                where.append(f"overlap {a['id']} ~ {b['id']}")
    return {"arrows": len(runs), "cross": crossings(runs), "shared": alongside(runs), "bends": sum(bends(w["path"]) for w in wires),
            "length": round(sum(length(w["path"]) for w in wires)), "through": through, "overlap": overlap, "where": where}


def measure(file_text: str) -> list[tuple[str, dict]]:
    """Every page's measures.

    Args:
        file_text: a .drawio file's text.

    Returns:
        [(page name, page_quality())] in file order.
    """
    return [(pg["name"], page_quality(pg)) for pg in read.pages(file_text)]


def _line(k: int, name: str, q: dict) -> str:
    """One page as a report line.

    Args:
        k: the page number, from 1.
        name: the page name.
        q: its measures.

    Returns:
        The line.
    """
    return f"{k:>3} {name[:34]:<34} " + " ".join(f"{m}={q[m]}" for m in MEASURES)


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        The exit code, as the module header says.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file", type=Path)
    ap.add_argument("--compare", type=Path, help="an earlier version of FILE: pages whose measures changed, and the totals")
    ap.add_argument("--all", action="store_true", help="every page, not only those with a judged issue")
    ap.add_argument("--where", action="store_true", help="also list the arrows and boxes behind 'through' and 'overlap'")
    ap.add_argument("--json", action="store_true", help="every page's measures as JSON")
    args = ap.parse_args(argv)
    try:
        after = measure(args.file.read_text(encoding="utf-8"))
        before = measure(args.compare.read_text(encoding="utf-8")) if args.compare else None
    except (OSError, ValueError) as exc:
        print(f"layout_quality: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps([{"page": k + 1, "name": n, **q} for k, (n, q) in enumerate(after)], indent=1))
        return 0
    total = {m: sum(q[m] for _n, q in after) for m in MEASURES}
    if before is None:
        for k, (name, q) in enumerate(after):
            if args.all or any(q[m] for m in JUDGED):
                print(_line(k + 1, name, q))
                if args.where:
                    print("".join(f"      {w}\n" for w in q["where"]), end="")
        print(_line(0, f"total ({len(after)} pages)", total))
        return 0
    old = dict(before)
    worse = False
    for k, (name, q) in enumerate(after):
        b = old.get(name)
        if b is None:
            print(f"{k + 1:>3} {name}: new page")
            continue
        if any(q[m] != b[m] for m in MEASURES):
            worse = worse or any(q[m] > b[m] for m in JUDGED)
            print(f"{k + 1:>3} {name[:34]:<34} " + " ".join(f"{m}={b[m]}->{q[m]}" for m in MEASURES if q[m] != b[m]))
    tb = {m: sum(q[m] for _n, q in before) for m in MEASURES}
    print("total " + " ".join(f"{m}={tb[m]}->{total[m]}" for m in MEASURES))
    return 3 if worse else 0


if __name__ == "__main__":
    sys.exit(main())
