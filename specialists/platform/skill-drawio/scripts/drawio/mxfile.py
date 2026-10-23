#!/usr/bin/env python3
"""Build draw.io (diagrams.net) files from code: pages, boxes, routed edges, edge labels, layers and HTML labels. Stdlib only.

Promoted from unified-network-controller `scripts/render/flows_drawio.py` (2026-10-19), where it renders the flow map. A generator builds one
`Page` per diagram tab, adds cells in a fixed order (so the output is byte-for-byte deterministic and a drift check can compare it with the
committed file), routes every edge along explicit points with `Page.route()` (static export does not route around shapes), and hands the pages
to `mxfile()`. The page keeps each box's rectangle, which boxes are solid, every routed polyline, every edge label and the layers, so
`drawio.audit.page_audit()` can check the drawing without parsing it back.

Imported, not run: `from drawio.mxfile import Page, label, mxfile` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

import html
import math
import re
from dataclasses import dataclass
from xml.sax.saxutils import quoteattr

from .cell import cell_xml

#: A `code` span in a label line, drawn in a monospace font.
CODE_SPAN = re.compile(r"`([^`]+)`")
#: A `**...**` span in a label line, matched after HTML escaping (asterisks survive it).
BOLD_SPAN = re.compile(r"\*\*(.+?)\*\*")
#: A `*span*` (single stars) in italics, applied after bold.
ITALIC_SPAN = re.compile(r"(?<![*\w])\*([^*]+)\*(?![*\w])")
#: A label line that renders as an empty line (an en space: kept by label(), invisible), to separate a box's sections.
BLANK = "\u2002"
#: A whole-line heading, `^^<percent>|text` (made by `heading()`): drawn at that percentage of the cell's font size (2026-10-21, operator: headings in
#: boxes bigger). `wrapped_lines` counts it with fewer characters a line and as a taller line, so boxes sized by it grow to fit.
HEADING_LINE = re.compile(r"^\^\^(\d+)\|(.*)$")
#: A token this long or longer gets invisible break points (soft_breaks), so draw.io can wrap a code path inside its shape.
LONG_TOKEN = 24
#: The orthogonal style draw.io's own router uses for Page.edge().
#: Appended to every generated cell's style: draw.io's Movable, Resizable, Rotatable, Bendable, Editable and Deletable properties off (mxConstants
#: STYLE_* keys), so nothing is dragged, resized, re-bent, retyped or deleted by mistake while every box and arrow stays selectable, hoverable and
#: taggable (a locked layer would block clicks; operator, 2026-10-23). Change the map, not the drawing.
FROZEN = "movable=0;resizable=0;rotatable=0;bendable=0;editable=0;deletable=0;"
EDGE_BASE = "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;endArrow=block;endFill=1;fontSize=16;fontStyle=1;labelBackgroundColor=#ffffff;"

Rect = tuple[float, float, float, float]
Point = tuple[float, float]


def soft_breaks(text: str, long_token: int = LONG_TOKEN) -> str:
    """Give a long unbroken token (a code path) invisible break points, so draw.io can wrap it inside its shape.

    Args:
        text: one label line, already HTML-escaped.
        long_token: the shortest token that gets break points.

    Returns:
        The line with a zero-width space after each `/ _ . : -` inside tokens of `long_token` characters or more; shorter words unchanged.
    """
    return re.sub(rf"\S{{{long_token},}}", lambda m: re.sub(r"([/_.:-])", "\\1\u200b", m.group(0)), text)


def label(*lines: str) -> str:
    """An HTML label for a draw.io cell (style `html=1`): each line escaped, then joined with <br>.

    Args:
        *lines: plain-text lines; `**bold**`, `*italic*` and `` `code` `` spans are formatted (a whole line or part of one); an empty line is
            dropped, so use BLANK for a visible gap.

    Returns:
        The label HTML (Page escapes it again as an XML attribute).
    """
    return "<br>".join(_line_html(line) for line in lines if line)


def _line_html(line: str) -> str:
    """One label line as HTML: spans formatted, and a heading line (see HEADING_LINE) wrapped in a font-size span.

    Args:
        line: a plain-text line.

    Returns:
        The line's HTML.
    """
    head = HEADING_LINE.match(line)
    text = head.group(2) if head else line
    out = CODE_SPAN.sub(r'<font face="Courier New">\1</font>',
                        ITALIC_SPAN.sub(r"<i>\1</i>", BOLD_SPAN.sub(r"<b>\1</b>", soft_breaks(html.escape(text)))))
    return f'<span style="font-size:{head.group(1)}%">{out}</span>' if head else out


def heading(text: str, percent: int) -> str:
    """A label line drawn as a heading at `percent` of the cell's font size; 100 or less leaves the line as it is.

    Args:
        text: the line (spans such as `**bold**` allowed).
        percent: the size relative to the cell's font.

    Returns:
        The line, marked for label() and wrapped_lines().
    """
    return f"^^{percent}|{text}" if percent > 100 else text


def wrapped_lines(text: str, width: int) -> float:
    """How many lines a text takes when wrapped at a fixed width: the estimate that sizes a box to its text.

    draw.io wraps on its own at render time; a generator sizes boxes before that, so it estimates with a conservative characters-per-line
    budget for the box width and font (bold text is wider; measure with an export when in doubt).

    Args:
        text: the text (formatting markers already removed).
        width: characters per line.

    Returns:
        The line count, at least 1; a heading line counts its lines times its scale (a fraction), so a box sized from it grows with the font.
    """
    head = HEADING_LINE.match(text)
    if head:   # a heading: fewer characters a line, and each of its lines as tall as the font grew
        scale = int(head.group(1)) / 100
        return wrapped_lines(head.group(2), max(1, int(width / scale))) * scale
    lines, used = 1, 0
    for word in text.split():
        size = len(word)
        if size > width:   # a long token wraps at its break points (see soft_breaks); count it as spanning whole lines
            lines += (1 if used else 0) + math.ceil(size / width) - 1
            used = size % width or width
        elif used == 0:
            used = size
        elif used + 1 + size <= width:
            used += 1 + size
        else:
            lines, used = lines + 1, size
    return lines


def num(value: float) -> str:
    """A style number, rounded to four places and printed without trailing zeros.

    Args:
        value: the number.

    Returns:
        Its text.
    """
    return f"{round(value, 4):g}"



def _unflip(style: str, fx: float, fy: float) -> tuple[float, float]:
    """A port's fraction as draw.io reads it on a shape that may be flipped (2026-10-21: an arrow into a flipV trapezoid's top drew to its bottom).

    Args:
        style: the shape's style.
        fx: the x fraction of the point on the box.
        fy: the y fraction.

    Returns:
        (x fraction, y fraction) mirrored for flipH=1 and flipV=1.
    """
    return (1 - fx if "flipH=1" in style else fx), (1 - fy if "flipV=1" in style else fy)

@dataclass
class Route:
    """One routed edge as drawn: the full polyline from the source's border to the target's, for the layout audits.

    Args:
        cid: the edge cell id.
        src: the source cell id.
        dst: the target cell id.
        points: the polyline; the first point lies on the source's border, the last on the target's.
        klass: "thick" or "thin": which head room (drawio.audit.HEAD_ROOM) the audit asks for, and whether shared runs are checked.
        ignore: cell ids the edge may pass over (its ends and the group holding them).
        jump: the arc size draw.io draws where the edge crosses another (0 for none).
        layer: the layer cell id the edge sits in.
    """

    cid: str
    src: str
    dst: str
    points: list
    klass: str = "thick"
    ignore: frozenset = frozenset()
    jump: float = 0.0
    layer: str = "1"


@dataclass
class TextMark:
    """A text box that belongs to one edge (a count, a step number), for the label audit.

    Args:
        cid: the text cell id.
        rect: its (x, y, width, height).
        owner: the edge cell id it labels (it may sit on that edge, never on another).
        layer: the layer cell id it sits in.
    """

    cid: str
    rect: Rect
    owner: str
    layer: str = "1"


class Page:
    """One draw.io diagram page being built, cell by cell, in insertion order (which keeps the output deterministic).

    Besides the cells it keeps each vertex's rectangle, which vertices are solid (an edge must not cross them), every routed edge's polyline,
    every edge label and the page's layers, so drawio.audit.page_audit() can check the drawing without parsing it back.
    """

    def __init__(self, page_id: str, name: str) -> None:
        """Start an empty page.

        Args:
            page_id: the diagram id (page links `data:page/id,<page_id>` point at it).
            name: the tab name shown in draw.io.
        """
        self.page_id, self.name, self.cells = page_id, name, []
        self.cell_style: dict[str, str] = {}   # each vertex's style, so a route can account for a flipped shape
        self.rects: dict[str, Rect] = {}
        self.solid: list[str] = []
        self.routes: list[Route] = []
        self.marks: list[TextMark] = []
        self.layers: list[tuple[str, str]] = []
        self.tips: dict[str, str] = {}   # hover text per edge id, set before the edge is drawn; its label mark shows the same text
        self.tags: dict[str, tuple] = {}   # draw.io tags per cell id (edges, and boxes drawn without a `tags` argument); a mark takes its edge's

    def box(self, cid: str, label: str, x: float, y: float, w: float, h: float, style: str, link: str = "", tooltip: str = "",
            layer: str = "1", solid: bool = False, tags: tuple = ()) -> None:
        """Add a vertex; one with a link, tooltip or tags is written as a `UserObject` wrapping its `mxCell`, as draw.io itself does.

        Args:
            cid: the cell id, unique in the file.
            label: the HTML label.
            x: left edge.
            y: top edge.
            w: width.
            h: height.
            style: the draw.io style string.
            link: an optional link (`data:page/id,<page>` for another page).
            tooltip: an optional hover text.
            layer: the layer cell id (default the base layer "1").
            solid: True when no edge may cross it (a component or group box).
            tags: optional draw.io tags (Tags dialog: select, hide or show every cell carrying one); else any set in `tags` for this id.
        """
        geo = f'<mxGeometry x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" as="geometry"/>'
        self.cells.append(cell_xml(cid, label, f'style={quoteattr(style + FROZEN)} vertex="1" parent="{layer}"', geo, link, tooltip, tags or self.tags.get(cid, ())))
        self.rects[cid] = (x, y, w, h)
        self.cell_style[cid] = style
        if solid:
            self.solid.append(cid)

    def edge(self, cid: str, source: str, target: str, label: str = "", style: str = "") -> None:
        """Add an edge between two vertices routed by draw.io (fine for simple pages; static export draws it straight through shapes).

        Args:
            cid: the cell id.
            source: the source cell id.
            target: the target cell id.
            label: an optional edge label.
            style: extra style, appended to EDGE_BASE (exitX/exitY/entryX/entryY pin the ports).
        """
        self.cells.append(cell_xml(cid, label, f'style={quoteattr(EDGE_BASE + style + FROZEN)} edge="1" parent="1" source="{source}" target="{target}"',
                                   '<mxGeometry relative="1" as="geometry"/>', tooltip=self.tips.get(cid, ""), tags=self.tags.get(cid, ())))

    def add_layer(self, lid: str, name: str) -> None:
        """Declare a draw.io layer (shown in the Layers panel, where it can be hidden); serialised right after the root cells.

        Args:
            lid: the layer cell id.
            name: the name shown in the panel.
        """
        self.layers.append((lid, name))

    def route(self, cid: str, src: str, dst: str, points: list, style: str, klass: str = "thick", layer: str = "1",
              ignore: tuple = (), jump: float = 0.0) -> None:
        """Add an edge drawn along explicit points (the generator's route, not draw.io's), and record it for the audits.

        Args:
            cid: the cell id.
            src: the source vertex id (already added).
            dst: the target vertex id (already added).
            points: the full polyline: first point on the source's border, waypoints, last point on the target's border.
            style: the edge style; exit and entry fractions (with perimeter snapping off) are appended from the first and last points.
            klass: "thick" or "thin" (which head room the audit asks for).
            layer: the layer cell id.
            ignore: further cell ids the edge may pass over (for example the group holding both ends).
            jump: the style's jumpSize when it hops at crossings, else 0.
        """
        pts: list[Point] = []
        for px, py in points:   # a repeated point is a zero-length run: drop it
            if not pts or (round(px, 1), round(py, 1)) != pts[-1]:
                pts.append((round(px, 1), round(py, 1)))
        sx, sy, sw, sh = self.rects[src]
        tx, ty, tw, th = self.rects[dst]
        (x0, y0), (x1, y1) = pts[0], pts[-1]
        fx0, fy0, fx1, fy1 = (x0 - sx) / sw, (y0 - sy) / sh, (x1 - tx) / tw, (y1 - ty) / th
        # draw.io mirrors connection points on a flipped shape (flipV=1 puts entryY=0 at the bottom): mirror the fraction back
        fx0, fy0 = _unflip(self.cell_style.get(src, ""), fx0, fy0)
        fx1, fy1 = _unflip(self.cell_style.get(dst, ""), fx1, fy1)
        ends = f"exitX={num(fx0)};exitY={num(fy0)};entryX={num(fx1)};entryY={num(fy1)};exitPerimeter=0;entryPerimeter=0;"
        geo = "".join(f'<mxPoint x="{px:g}" y="{py:g}"/>' for px, py in pts[1:-1])
        self.cells.append(cell_xml(cid, "", f'style={quoteattr(style + ends + FROZEN)} edge="1" parent="{layer}" source="{src}" target="{dst}"',
                                   f'<mxGeometry relative="1" as="geometry"><Array as="points">{geo}</Array></mxGeometry>',
                                   tooltip=self.tips.get(cid, ""), tags=self.tags.get(cid, ())))   # hover text and tags set before drawing
        self.routes.append(Route(cid, src, dst, pts, klass, frozenset({src, dst, *ignore}), jump, layer))

    def mark(self, cid: str, label: str, cx: float, cy: float, w: float, h: float, style: str, owner: str, layer: str = "1") -> None:
        """Add a text box centred on a point that labels one edge, and record it for the audits.

        Args:
            cid: the cell id.
            label: the HTML label.
            cx: centre x.
            cy: centre y.
            w: width.
            h: height.
            style: the text style.
            owner: the edge it labels; its hover text and tags, if any, are the mark's too.
            layer: the layer cell id.
        """
        x, y = round(cx - w / 2, 1), round(cy - h / 2, 1)
        self.box(cid, label, x, y, w, h, style, tooltip=self.tips.get(owner, ""), layer=layer, tags=self.tags.get(owner, ()))
        self.marks.append(TextMark(cid, (x, y, w, h), owner, layer))

    def xml(self) -> str:
        """Serialise the page; layer cells follow the root cells `0` and `1`.

        Returns:
            The `<diagram>` element.
        """
        layers = "".join(f'        <mxCell id="{lid}" value={quoteattr(name)} parent="0"/>\n' for lid, name in self.layers)
        body = "\n".join(f"        {c}" for c in self.cells)
        return (f'  <diagram id="{self.page_id}" name={quoteattr(self.name)}>\n'
                '    <mxGraphModel grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="0" pageScale="1" '
                'math="0" shadow="0">\n      <root>\n        <mxCell id="0"/>\n        <mxCell id="1" parent="0"/>\n'
                f"{layers}{body}\n      </root>\n    </mxGraphModel>\n  </diagram>")


def banner(generator: str, source: str, command: str, check: str) -> str:
    """The comment a generated file starts with, so a reader knows not to edit it and how to regenerate it.

    Args:
        generator: the script that writes the file.
        source: the data file it is rendered from.
        command: the command that regenerates it.
        check: the command that fails when it is out of step.

    Returns:
        The XML comment line, newline-terminated.

    Raises:
        ValueError: a part contains "--", which an XML comment cannot hold (the file would not parse).
    """
    if any("--" in part for part in (generator, source, command, check)):
        raise ValueError(f"banner part contains '--', illegal in an XML comment: {[generator, source, command, check]}")
    return (f"<!-- GENERATED by {generator} from {source}; do not edit by hand. "
            f"Change the map and run `{command}`; `{check}` fails when this file is out of step. -->\n")


def mxfile(pages: list[Page], host: str, head: str = "") -> str:
    """A whole uncompressed draw.io file.

    Args:
        pages: the pages, in tab order.
        host: the `host` attribute (the generator's name).
        head: text placed between the XML declaration and `<mxfile>` (usually banner()).

    Returns:
        The file text. Uncompressed on purpose: it diffs, and a drift check can compare it byte for byte.
    """
    body = "\n".join(p.xml() for p in pages)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{head}<mxfile host="{host}" type="device" compressed="false">\n{body}\n</mxfile>\n'


#: A page header's box (flow pages, Overview, End-to-end): light grey, left-aligned, font 13.
HEADER_STYLE = "rounded=0;whiteSpace=wrap;html=1;fillColor=#fafafa;strokeColor=#666666;align=left;verticalAlign=top;spacingLeft=8;spacingTop=4;fontSize=13;"


def header_height(lines: list[str], width: float, least: float, px_per_char: float = 7.6, line_h: float = 17.0) -> float:
    """A boxed page header's height for its text: at least `least`, taller when the wrapped lines need it.

    Args:
        lines: the header's label lines (markers `*` and backticks are ignored when counting).
        width: the box width in pixels.
        least: the height the page layout was built around.
        px_per_char: the conservative width of one character at the header's font size (13 px: 7.6).
        line_h: one line's height.

    Returns:
        The height in pixels.
    """
    chars = max(20, int((width - 20) / px_per_char))
    need = 12 + sum(wrapped_lines(x.replace("*", "").replace("`", ""), chars) for x in lines if x) * line_h
    return max(least, need)
