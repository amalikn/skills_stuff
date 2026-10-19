---
Title: Reading existing drawings
Category: skill-reference
Status: current
Authority: >-
  This pack's scripts/drawio/read.py (promoted from UNC's as-built reader, which re-exports it since 2026-10-19) and UNC's drawing
  interpreter (src/unc/tasks/asbuilt/drawings.py), with the official format rules; the code wins over this summary
Scope: >-
  Getting text, boxes and connections out of a .drawio file someone else drew: decompressing pages, both cell element kinds, HTML labels to text, group offsets,
  connection paths, and matching free-standing port labels and captions to the line or picture they describe
Last reviewed: 2026-10-19
Summary: How to read a hand-drawn draw.io file as data by decompressing pages, resolving group offsets, stripping HTML labels, building line paths and matching port labels to lines.
---

# Reading existing drawings

Site records, vendor diagrams and operator drawings are often draw.io files with compressed pages and hand placement. Reading them by eye misses things; reading them as data lets a person or an agent
compare them with discovery. The patterns here come from UNC's as-built reader, which exists because a site's as-built drawing showed tower routers cabled to a switch rather than behind a subscriber
module, explaining an inventory puzzle. Claim IDs refer to [sources.yaml](../sources.yaml).

A drawing read this way is evidence, not something to regenerate ([data-first-diagrams.md](data-first-diagrams.md)).

## Contents

- [Steps](#steps)
- [1. Decompress each page](#1-decompress-each-page)
- [2. Index both cell kinds](#2-index-both-cell-kinds)
- [3. Labels to text](#3-labels-to-text)
- [4. Page coordinates through groups](#4-page-coordinates-through-groups)
- [5. Connection paths](#5-connection-paths)
- [6. Port labels and captions](#6-port-labels-and-captions)
- [Pitfalls](#pitfalls)

## Steps

| Step        | Function                       | Output                                   |
| ----------- | ------------------------------ | ---------------------------------------- |
| Decompress  | `read.models`, `read.pages`    | One `mxGraphModel` per page              |
| Index cells | `read.cells`                   | `{id: (mxCell, label text)}`             |
| Text        | `read.text`                    | Plain label text                         |
| Geometry    | `read.box`, `read.origin`      | Page-coordinate rectangles               |
| Paths       | `read.wire`, `read._end`       | Each line's polyline in page coordinates |
| Meaning     | UNC `unc.tasks.asbuilt.drawings` | Units, ports and uplinks                 |

## 1. Decompress each page

For each `<diagram>`: if it has an `<mxGraphModel>` child, use it; otherwise its text is a compressed page. Decode with base64, raw inflate (`wbits=-15`), then URL-decode, and parse the result
[C-D11]:

```python
import base64, urllib.parse, zlib
import xml.etree.ElementTree as ET

def page_models(text: str) -> list[tuple[str, ET.Element]]:
    """(page name, mxGraphModel) for every page of a .drawio file, compressed or not."""
    out = []
    for d in ET.fromstring(text).iter("diagram"):
        model = d.find("mxGraphModel")
        if model is None and (d.text or "").strip():
            model = ET.fromstring(urllib.parse.unquote(zlib.decompress(base64.b64decode(d.text.strip()), -15).decode()))
        if model is not None:
            out.append((d.get("name"), model))
    return out
```

A file can mix the two forms. The `<mxfile modified="...">` attribute, when present, says when the drawing was last saved; record it with whatever you extract. For untrusted files, parse with a
hardened XML parser (for example `defusedxml`) if one is available.

## 2. Index both cell kinds

A cell is either an `mxCell` with an `id`, or a `UserObject`/`object` carrying the `id` and `label` with an inner `mxCell` that holds style, parent and geometry [C-D06]. Index both, or every box with
a link or tooltip disappears from the reading:

```python
cells = {c.get("id"): (c, text(c.get("value"))) for c in model.iter("mxCell") if c.get("id")}
for u in model.iter("UserObject"):            # and model.iter("object") if the file uses that spelling
    c = u.find("mxCell")
    if c is not None:
        cells[u.get("id")] = (c, text(u.get("label")))
```

An edge has `edge="1"` and `source`/`target` ids; a vertex has `vertex="1"`; layers have `parent="0"` and no geometry.

## 3. Labels to text

Labels with `html=1` hold HTML. Unescape entities, replace every tag with a space, collapse whitespace, and strip [C-D34]:

```python
import html, re

def text(label: str | None) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(label or ""))).strip()
```

Replacing tags with a space (not nothing) keeps `A<br>B` as two words. The result loses formatting; keep the raw label too if bold or line structure carries meaning.

## 4. Page coordinates through groups

A child's `mxGeometry` is relative to its parent group or container [C-D13]. To place a vertex on the page, add the `x` and `y` of each ancestor that has a geometry, recursively, stopping at a layer
(no geometry) [C-D33]:

```python
def box(cells, cid):
    """(x, y, w, h) on the page, or None for an edge or a cell without a size."""
    if cid not in cells or cells[cid][0].get("edge") == "1":
        return None
    g = cells[cid][0].find("mxGeometry")
    if g is None or g.get("width") is None:
        return None
    parent = box(cells, cells[cid][0].get("parent"))
    ox, oy = (parent[0], parent[1]) if parent else (0.0, 0.0)
    return (ox + float(g.get("x") or 0), oy + float(g.get("y") or 0), float(g.get("width") or 0), float(g.get("height") or 0))
```

Missing `x` or `y` means 0. Edge waypoints are relative to the edge's own parent in the same way.

## 5. Connection paths

A line's path runs from where it leaves its source, through its waypoints, to where it meets its target [C-D33]:

- An end attached to a box sits at the style's `exitX`/`exitY` (source) or `entryX`/`entryY` (target) fraction of that box; with no fraction, take the box's centre (an approximation: draw.io would
  project onto the perimeter).
- An end attached to nothing uses the geometry's `sourcePoint` or `targetPoint` `mxPoint`.
- Waypoints are the `mxPoint` elements inside `<Array as="points">`, offset by the edge parent's origin.

Parse the style string by splitting on `;` and then on the first `=`.

A line drawn to touch a box without being joined to it has no `source` or `target`; UNC treats a free end within 10 units of a box as touching it, the nearest box first.

## 6. Port labels and captions

Hand drawings often put a port name ("SWP 5", "LAN 3") in a small separate text box beside a line, and a caption beside a picture that has no text of its own. These are matched by distance [C-D33]:

- **Port labels**: compute the distance from each port label's centre to each line's polyline (shortest distance to any segment). Take pairs nearest first; a label further than the reach (UNC: 35
  units) is not matched, and each label is used once.
- **Which end**: give the port to the end of the line whose box holds ports (a switch, a router, a site controller), ranked by kind; when both ends could, the end nearer the label wins.
- **Captions**: a picture with no label takes the nearest unwired text box within reach (UNC: 40 units, box-to-box gap). A text box that has its own line is a unit, not a caption.

Tune the reach to the drawing's scale, and test against several real drawings; the UNC rules were checked against a number of site drawings before being trusted.

## Pitfalls

- Reading only `mxCell` elements: boxes with links or tooltips vanish.
- Using child coordinates as page coordinates: everything inside a group lands near the page origin.
- Matching a port label to the nearest box rather than the nearest line: labels usually sit beside the line, between two boxes.
- Treating the drawing as truth: it records what someone drew, which may differ from what is installed; compare it with discovery and say which one each fact came from.
- Writing back to the file: a reader never modifies the drawing it reads.
