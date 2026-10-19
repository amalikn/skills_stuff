"""Read existing draw.io drawings as data: every page's boxes and connections with labels as text, every shape's rectangle and every line's path in
page coordinates (group offsets resolved), compressed pages decoded, and loose labels matched to the line they sit nearest. Stdlib only.

Promoted from unified-network-controller `wc-local/scripts/site_onboarding/asbuilt_read.py` (draw.io part) and the port-label matching of its
as-built reader (2026-10-19). A hand-drawn drawing is source: this module only reads it, so a project can compare it with discovery or an
inventory, never regenerate over it.

Format facts relied on (references/file-format.md, references/reading-drawings.md): a `<diagram>` holds either an `<mxGraphModel>` or its
compressed form (URL-encoded XML, raw-deflated, base64-encoded); a cell with a link or tooltip is a `<UserObject>` (id and label) wrapping its
`<mxCell>`; a child's geometry is relative to its parent group's corner; a line's ends are its source and target boxes at the style's exit and
entry fractions (else their centres), or its own sourcePoint and targetPoint.

Imported, not run: `from drawio import read` with the skill's scripts/ on sys.path; the command line is scripts/drawio_read.py.
"""

from __future__ import annotations

import base64
import html
import math
import re
import urllib.parse
import xml.etree.ElementTree as ET
import zlib

Cells = dict[str, tuple[ET.Element, str]]


def decode_page(data: str) -> str:
    """A compressed page's XML.

    Args:
        data: the `<diagram>` element's text (base64 of raw deflate of the URL-encoded XML).

    Returns:
        The `<mxGraphModel>` XML.

    Raises:
        ValueError: the text is not a compressed page (bad base64 or deflate data).
    """
    try:
        return urllib.parse.unquote(zlib.decompress(base64.b64decode(data.strip()), -15).decode("utf-8"))
    except (zlib.error, ValueError) as exc:
        raise ValueError(f"not a compressed draw.io page: {exc}") from exc


def encode_page(xml: str) -> str:
    """Compress a page's XML the way draw.io does (encodeURIComponent, raw deflate, base64); decode_page() inverts it.

    Args:
        xml: the `<mxGraphModel>` XML.

    Returns:
        The text for a `<diagram>` element.
    """
    raw = urllib.parse.quote(xml, safe="-_.!~*'()")
    comp = zlib.compressobj(9, zlib.DEFLATED, -15)
    return base64.b64encode(comp.compress(raw.encode("utf-8")) + comp.flush()).decode("ascii")


def text(value: str | None) -> str:
    """A draw.io HTML label as plain text.

    Args:
        value: the cell's value or the UserObject's label (HTML).

    Returns:
        The text, tags removed and whitespace collapsed.
    """
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(value or ""))).strip()


def style(value: str | None) -> dict[str, str]:
    """A draw.io style string as a dict.

    Args:
        value: for example "exitX=0.5;exitY=1;rounded=0".

    Returns:
        {"exitX": "0.5", "exitY": "1", "rounded": "0"}; bare words (a shape name such as "ellipse") are left out.
    """
    return dict(kv.split("=", 1) for kv in (value or "").split(";") if "=" in kv)


def models(file_text: str) -> list[tuple[str, ET.Element]]:
    """Every page of a draw.io file as its graph model, compressed or not.

    Args:
        file_text: the .drawio file's XML.

    Returns:
        (page name, mxGraphModel element) per page, in tab order; a page with neither form is skipped.

    Raises:
        ValueError: the file is not XML, or a page's compressed text cannot be decoded.
    """
    try:
        root = ET.fromstring(file_text)
    except ET.ParseError as exc:
        raise ValueError(f"not a draw.io file: {exc}") from exc
    out = []
    for d in root.iter("diagram"):
        model = d.find("mxGraphModel")
        if model is None and (d.text or "").strip():
            model = ET.fromstring(decode_page(d.text))
        if model is not None:
            out.append((d.get("name") or "", model))
    return out


def cells(model: ET.Element) -> Cells:
    """Every cell of a page by id, with its label: plain mxCells and the mxCell inside each UserObject.

    Args:
        model: the page's mxGraphModel.

    Returns:
        {id: (the mxCell element, its label as text)}.
    """
    out = {c.get("id"): (c, text(c.get("value"))) for c in model.iter("mxCell") if c.get("id")}
    for u in model.iter("UserObject"):
        c = u.find("mxCell")
        if c is not None:
            out[u.get("id")] = (c, text(u.get("label")))
    return out


def box(cs: Cells, cid: str | None) -> tuple[float, float, float, float] | None:
    """A vertex's rectangle in page coordinates, adding the offsets of the groups it sits in.

    Args:
        cs: the page's cells.
        cid: the vertex's id (None, an edge or a cell without a size give None).

    Returns:
        (x, y, width, height), or None.
    """
    if cid not in cs or cs[cid][0].get("edge") == "1":
        return None
    g = cs[cid][0].find("mxGeometry")
    if g is None or g.get("width") is None:
        return None
    ox, oy = origin(cs, cs[cid][0].get("parent"))
    return (ox + float(g.get("x") or 0), oy + float(g.get("y") or 0), float(g.get("width") or 0), float(g.get("height") or 0))


def origin(cs: Cells, pid: str | None) -> tuple[float, float]:
    """The page position a child's coordinates are relative to: its parent group's corner, or the page's (layers have no geometry).

    Args:
        cs: the page's cells.
        pid: the parent's id.

    Returns:
        (x, y).
    """
    b = box(cs, pid)
    return (b[0], b[1]) if b else (0.0, 0.0)


def _end(cs: Cells, cid: str | None, fx: str | None, fy: str | None, fallback: list[float] | None) -> list[float] | None:
    """Where a line meets a box: at the style's fraction of it, else at its centre; a line with no box at that end keeps its own end point.

    Args:
        cs: the page's cells.
        cid: the box's id, or None.
        fx: exitX or entryX from the line's style, or None.
        fy: exitY or entryY, or None.
        fallback: the line's own sourcePoint or targetPoint, or None.

    Returns:
        [x, y], or None when neither a box nor a point is given.
    """
    b = box(cs, cid)
    if b is None:
        return fallback
    x, y, w, h = b
    return [round(x + w * float(fx if fx is not None else 0.5), 1), round(y + h * float(fy if fy is not None else 0.5), 1)]


def wire(cs: Cells, cid: str, c: ET.Element, label: str) -> dict:
    """One connection with the path it is drawn along.

    Args:
        cs: the page's cells.
        cid: the edge's id.
        c: the edge's mxCell.
        label: its label as text.

    Returns:
        {"id", "source_id", "target_id", "label", "path": [[x, y], ...]}.
    """
    g, st = c.find("mxGeometry"), style(c.get("style"))
    ox, oy = origin(cs, c.get("parent"))
    pts = {p.get("as"): [ox + float(p.get("x") or 0), oy + float(p.get("y") or 0)] for p in (g.findall("mxPoint") if g is not None else [])}
    way = [[round(ox + float(p.get("x") or 0), 1), round(oy + float(p.get("y") or 0), 1)]
           for a in (g.findall("Array") if g is not None else []) for p in a.findall("mxPoint")]
    path = [_end(cs, c.get("source"), st.get("exitX"), st.get("exitY"), pts.get("sourcePoint")), *way,
            _end(cs, c.get("target"), st.get("entryX"), st.get("entryY"), pts.get("targetPoint"))]
    return {"id": cid, "source_id": c.get("source"), "target_id": c.get("target"), "label": label, "path": [p for p in path if p]}


def layout(model: ET.Element) -> tuple[list[dict], list[dict]]:
    """Where each box sits and the path each connection takes, in page coordinates.

    Args:
        model: the page's mxGraphModel.

    Returns:
        (shapes, wires): shapes [{"id", "label", "geo": [x, y, width, height]}] for every vertex with a size, labelled or not; wires as wire().
    """
    cs = cells(model)
    shapes, wires = [], []
    for cid, (c, label) in cs.items():
        if c.get("edge") == "1":
            wires.append(wire(cs, cid, c, label))
        elif (b := box(cs, cid)) is not None:
            shapes.append({"id": cid, "label": label, "geo": [round(v, 1) for v in b]})
    return shapes, wires


def pages(file_text: str) -> list[dict]:
    """Every page of a draw.io file: its labelled boxes, its connections by end labels, and its shapes and wires with geometry.

    Args:
        file_text: the .drawio file's XML.

    Returns:
        [{"name", "boxes": [{"id", "label"}], "edges": [{"source", "target", "label"}], "shapes", "wires"}]; an edge's ends are the labels
        of the cells it joins ("" for an end with no label or no cell).
    """
    out = []
    for name, model in models(file_text):
        cs = cells(model)
        label = {k: lab for k, (_c, lab) in cs.items()}
        shapes, wires = layout(model)
        out.append({"name": name,
                    "boxes": [{"id": k, "label": lab} for k, (c, lab) in cs.items() if c.get("edge") != "1" and lab],
                    "edges": [{"source": label.get(c.get("source") or "", ""), "target": label.get(c.get("target") or "", ""), "label": lab}
                              for c, lab in cs.values() if c.get("edge") == "1"],
                    "shapes": shapes, "wires": wires})
    return out


def distance_to_path(point: tuple[float, float], path: list) -> float:
    """How far a point is from a line drawn as straight segments.

    Args:
        point: (x, y).
        path: [[x, y], ...], at least one point.

    Returns:
        The shortest distance.
    """
    best = math.inf
    for (x1, y1), (x2, y2) in zip(path, path[1:] or path):
        dx, dy = x2 - x1, y2 - y1
        t = 0.0 if dx == dy == 0 else max(0.0, min(1.0, ((point[0] - x1) * dx + (point[1] - y1) * dy) / (dx * dx + dy * dy)))
        best = min(best, math.hypot(point[0] - x1 - t * dx, point[1] - y1 - t * dy))
    return best


def match_labels(labels: list[dict], wires: list[dict], reach: float = 35.0) -> dict[str, str]:
    """Give each loose label (a port name in its own small box beside a line) to the line it sits nearest, nearest pairs first.

    Args:
        labels: shapes [{"id", "geo"}] to place; each is measured from its centre.
        wires: lines [{"id", "path"}].
        reach: the furthest (drawing units) a label may sit from its line.

    Returns:
        {label id: wire id} for every label within reach of a line; each label is used once, a line may take several.
    """
    pairs = sorted((distance_to_path((s["geo"][0] + s["geo"][2] / 2, s["geo"][1] + s["geo"][3] / 2), w["path"]), s["id"], w["id"])
                   for s in labels for w in wires if w["path"])
    out: dict[str, str] = {}
    for dist, sid, wid in pairs:
        if dist <= reach and sid not in out:
            out[sid] = wid
    return out
