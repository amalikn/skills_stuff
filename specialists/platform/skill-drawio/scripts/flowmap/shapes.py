"""Flow page shapes: the standard flowchart symbols (ISO 5807 / draw.io's Flowchart set) a step or a lane head is drawn with, how each is derived
from the map, and the per-page shape legend. Stdlib only.

Adopted 2026-10-21 (smc-resiliency's operator chose all twelve after the sample in references/screenshots/20261021-shape-vocabulary-sample/).
A step's shape comes from, in order: its own `shape`; a gate (decision); a `flow` it runs (predefined process); an actor whose kind draws as a
person (manual operation); the first step or a step nothing follows (terminator); a transport that crosses a network (data in or out); else a
process. A lane head's shape comes from the component's own `shape`, else its kind (`drawing.kind_shapes`, else DEFAULT_KIND_SHAPES).

Imported, not run: `from flowmap.shapes import step_shape, lane_shape` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.mxfile import Page, label, wrapped_lines

#: Each shape: (style fragment, text-width factor, height factor, legend text). The style replaces the box's rectangle; the factors shrink the
#: characters per line and grow the height where the outline eats into the text area (a diamond most).
SHAPES = {
    "terminator": ("rounded=1;absoluteArcSize=1;arcSize=36;spacingLeft=14;spacingRight=12;spacingTop=8;", 0.92, 1.05,
                   "Terminator: where a flow starts or ends"),   # a fixed corner radius, so a tall box keeps straight sides (2026-10-21)
    "process": ("rounded=0;", 1.0, 1.0, "Process: a step that does work"),
    # A text block w wide and h tall fits inside a W x H diamond only when w/W + h/H <= 1: at half the width (0.5) the diamond needs twice
    # the text's height; 1.45 let the block's corners reach the edges (operator, 2026-11-06, on a UNC onboarding gate).
    "decision": ("rhombus;align=center;verticalAlign=middle;spacingLeft=72;spacingRight=72;spacingTop=0;", 0.5, 2.0,
                 "Decision: a gate that picks the next step"),
    "manual-operation": ("shape=trapezoid;perimeter=trapezoidPerimeter;flipV=1;fixedSize=1;size=12;spacingLeft=18;spacingRight=18;", 0.88, 1.0,
                         "Manual operation: a person acts"),
    "preparation": ("shape=hexagon;perimeter=hexagonPerimeter2;fixedSize=1;size=12;spacingLeft=18;spacingRight=18;", 0.88, 1.0,
                    "Preparation: set-up before the change"),
    "predefined-process": ("shape=process;backgroundOutline=1;size=0.06;spacingLeft=20;spacingRight=20;", 0.75, 1.0,   # draw.io also insets the label by the bars (2026-11-06)
                           "Predefined process: runs another flow (click to open it)"),
    "delay": ("shape=delay;spacingRight=24;", 0.9, 1.0, "Delay: waits for time (a timer, a deadline)"),
    "stored-data": ("shape=cylinder3;boundedLbl=1;backgroundOutline=1;size=10;", 1.0, 1.1, "Stored data: a store that persists"),
    "document": ("shape=document;boundedLbl=1;size=0.15;", 1.0, 1.2, "Document: a file or record written"),
    "data-io": ("shape=parallelogram;perimeter=parallelogramPerimeter;fixedSize=1;size=10;spacingLeft=16;spacingRight=16;", 0.88, 1.0,
                "Data in or out: data crossing a link"),
    "external": ("ellipse;shape=cloud;align=center;spacingLeft=30;spacingRight=28;spacingTop=26;", 0.72, 1.35,   # the outline bulges in at the corners: text
                 "External system: outside the box"),                                               # past it at 16 px (operator review 2026-11-06)
    "person": ("rounded=0;", 1.0, 1.0, "Person: who starts or approves (the figure marks the box)"),
}
#: Shapes with slanted sides: an arrow end is pinned to the box edge, not projected onto the outline (projection slid arrow ends along the
#: slant to a corner; operator review, 2026-10-21).
SLANTED = frozenset({"data-io", "manual-operation", "preparation"})
#: Lane head shapes for common kinds when the map's `drawing.kind_shapes` does not name them.
DEFAULT_KIND_SHAPES = {"person": "person", "operator": "person", "timer": "delay", "store": "stored-data", "database": "stored-data",
                       "external": "external", "document": "document"}
#: Transports that cross a network (case-insensitive) unless the map's `drawing.io_vias` lists its own.
DEFAULT_IO_VIAS = ("http", "https", "api", "rest", "graphql", "mqtt", "dhcp", "snmp", "download", "upload")
PERSON_ICON = "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;outlineConnect=0;fillColor=#ffffff;strokeColor=#333333;"


def lane_shape(comp: dict, kind_shapes: dict) -> str:
    """The shape a component's lane head is drawn with.

    Args:
        comp: the component from the map.
        kind_shapes: the map's `drawing.kind_shapes` ({kind: shape}).

    Returns:
        A SHAPES key ("process" when nothing names one).
    """
    return comp.get("shape") or kind_shapes.get(comp["kind"]) or DEFAULT_KIND_SHAPES.get(comp["kind"], "process")


def step_shape(steps: list[dict], k: int, comps: dict, kind_shapes: dict, io_vias: tuple) -> str:
    """The shape the k-th step is drawn with (the rule order is in the module docstring).

    Args:
        steps: the flow's steps.
        k: the step's index.
        comps: every component by id.
        kind_shapes: the map's `drawing.kind_shapes`.
        io_vias: transports that cross a network, lower case.

    Returns:
        A SHAPES key.
    """
    s = steps[k]
    if s.get("shape"):
        return s["shape"]
    if s.get("gate"):
        return "decision"
    if s.get("flow"):
        return "predefined-process"
    if lane_shape(comps[s["actor"]], kind_shapes) == "person":
        return "manual-operation"
    last = s.get("next") == [] or (k == len(steps) - 1 and "next" not in s)
    if k == 0 or last:
        return "terminator"
    if any(v.lower() in io_vias for v in s.get("via", [])):
        return "data-io"
    return "process"


def shape_legend(page: Page, used: list[str], x: float, y: float, prefix: str, cols: int = 3) -> float:
    """A row of the shapes this page uses, each a small sample beside its meaning.

    Args:
        page: the page.
        used: SHAPES keys in first-use order.
        x: the legend's left edge.
        y: its top edge.
        prefix: the cell id prefix (the flow id, or `ov` / `e2e`).
        cols: samples per row (1 for the Overview's narrow legend column).

    Returns:
        The y just below the legend.
    """
    page.box(f"{prefix}-shp-title", label("**Shapes on this page**"), x, y, 300, 24, "text;html=1;align=left;fontSize=13;")
    for i, key in enumerate(used):
        cx, cy = x + (i % cols) * 330, y + 30 + (i // cols) * 46
        style, _w, _h, text = SHAPES[key]
        if key == "person":   # the figure keeps its proportions
            page.box(f"{prefix}-shp-{key}", "", cx + 24, cy, 22, 36, PERSON_ICON)
        else:
            page.box(f"{prefix}-shp-{key}", "", cx, cy, 70, 36, f"whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#333333;{style}")
        page.box(f"{prefix}-shp-{key}-t", label(text), cx + 80, cy, 240, 36, "text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;fontSize=11;")
    return y + 30 + ((len(used) + cols - 1) // cols) * 46


def component_shape(comp: dict, profile) -> str:
    """The style fragment that draws a component box on the Overview or End-to-end page as its lane head's symbol (2026-10-21).

    Args:
        comp: the component.
        profile: the drawing profile (its kind_shapes and look).

    Returns:
        "" when `look.component_shapes` is off or the symbol is a plain process box, else the shape's style (a person keeps a rectangle and gets
        the figure from `person_badge`).
    """
    shape = lane_shape(comp, profile.kind_shapes)
    if not profile.look.get("component_shapes", True) or shape in ("process", "person"):
        return ""
    return SHAPES[shape][0] + FIT.get(shape, ("", 1.0, 0))[0]


#: Component boxes on the Overview and End-to-end pages are sized by their text; an outline that eats into the box needs room and centred text
#: (operator review, 2026-10-21: cloud labels spilled out of the cloud and store labels sat on the cylinder's rim). (style, height factor, extra px).
FIT = {
    "external": ("align=center;verticalAlign=middle;spacingLeft=34;spacingRight=34;spacingTop=10;spacingBottom=10;", 1.6, 24),
    "stored-data": ("verticalAlign=middle;spacingTop=16;spacingBottom=2;", 1.0, 30),
}


#: A step drawn as a store keeps its text on the cylinder's flat body: draw.io's boundedLbl only clears the top rim, so the label crowded the
#: rim and the last line (the italic via) sat on the bottom curve (operator review 2026-11-07, step "5. write"). (style, extra px of height);
#: `look.store_insets` "off" draws the 2026-10-21 cylinder.
STEP_FIT = {"stored-data": ("spacingTop=14;spacingBottom=14;", 34)}


def step_fit(shape: str, look: dict) -> tuple[str, int]:
    """The extra label inset and height a step box of this shape needs on a flow page so its text stays inside the outline's flat part.

    Args:
        shape: the step's SHAPES key.
        look: the drawing's look.

    Returns:
        (style fragment, extra height in px); ("", 0) for a shape that needs none or when `look.store_insets` is "off".
    """
    if look.get("store_insets", "on") == "off":
        return "", 0
    return STEP_FIT.get(shape, ("", 0))


#: Smallest diamond, so a one-line question still reads as a diamond with its title (`look.decision_min_width` overrides it).
DECISION_MIN_W = 160
#: A diamond's characters are estimated this much narrower than a box's: step_chars is a left-aligned box's safe budget (about 5.4 px a
#: character at font 10) while a centred diamond label rendered at about 4.4 (draw.io 32.6.1, smc-resiliency X2 page, 2026-11-07); the full
#: box budget made the text block a third shorter than the diamond was sized for, so every diamond was oversized.
DIAMOND_CHAR_FILL = 0.85
#: Room above and below a diamond's text block (px each side, before doubling).
DIAMOND_PAD = 4


def diamond_size(lines: list[str], px_per_char: float, line_h: float, look: dict) -> tuple[int, int]:
    """A decision diamond sized to hold its full text and no more (operator review 2026-11-07: "all diamonds are almost extra large").

    A W x H rhombus holds a centred w x h rectangle when w/W + h/H <= 1; the largest such rectangle is W/2 x H/2. So the text is wrapped at
    half the width (diamond_inset sets draw.io's label to exactly that) and the diamond is twice the text block's height. It starts at
    `look.decision_min_width` and widens in 20 px steps until its height is at most `look.decision_aspect` times its width, up to
    `look.decision_max_width`: wider rather than taller.

    Args:
        lines: the label lines (markers such as ** allowed).
        px_per_char: the width one character takes at the box's font (the box budget; DIAMOND_CHAR_FILL narrows it for a centred label).
        line_h: the height of one line.
        look: the drawing's look.

    Returns:
        (width, height).
    """
    w, aspect = int(look.get("decision_min_width", DECISION_MIN_W)), float(look.get("decision_aspect", 0.6))
    widest = max(w, int(look.get("decision_max_width", 560)))
    while True:
        chars = max(8, int((w / 2 - 4) / (px_per_char * DIAMOND_CHAR_FILL)))
        h = round(2 * (sum(wrapped_lines(x.replace("*", ""), chars) for x in lines) * line_h + 2 * DIAMOND_PAD))
        if h <= aspect * w or w >= widest:
            return w, h
        w += 20


def inscribed(look: dict) -> bool:
    """Whether diamonds are sized to their text's inscribed rectangle (`look.decision_fit`: "inscribed", the default, or "widen", the
    2026-10-27 rule that sized a diamond like a box with fixed 72 px insets).

    Args:
        look: the drawing's look.

    Returns:
        True unless the map sets decision_fit to "widen".
    """
    return look.get("decision_fit", "inscribed") != "widen"


def diamond_inset(width: float) -> str:
    """The label inset that makes draw.io wrap a diamond's text at half its width: the inscribed rectangle diamond_size sized it for.

    Args:
        width: the diamond's width.

    Returns:
        A style fragment that overrides the shape's fixed spacing (draw.io takes the last value of a repeated key).
    """
    return f"spacingLeft={width / 4:g};spacingRight={width / 4:g};spacingTop=0;spacingBottom=0;"


def fit_height(comp: dict, profile, height: float) -> float:
    """A component box's height on the Overview or End-to-end page once its symbol's outline is allowed for.

    Args:
        comp: the component.
        profile: the drawing profile.
        height: the height its text needs.

    Returns:
        The height to draw (unchanged for rectangles and when `look.component_shapes` is off).
    """
    if not profile.look.get("component_shapes", True):
        return height
    _style, factor, extra = FIT.get(lane_shape(comp, profile.kind_shapes), ("", 1.0, 0))
    return round(height * factor + extra)


def person_badge(page: Page, comp: dict, profile, cell: str, right: float, bottom: float) -> None:
    """A person figure in a component box's bottom right corner (the top right holds the Overview's dependency dots), when the component
    draws as a person.

    Args:
        page: the page.
        comp: the component.
        profile: the drawing profile.
        cell: the component's cell id (the figure is `<cell>-icon`).
        right: the box's right edge.
        bottom: the box's bottom edge.
    """
    if profile.look.get("component_shapes", True) and lane_shape(comp, profile.kind_shapes) == "person":
        page.box(f"{cell}-icon", "", right - 20, bottom - 28, 12, 22, PERSON_ICON)


def component_shapes_used(comps: list[dict], profile) -> list[str]:
    """The symbols the Overview or End-to-end page draws its components with, for that page's shape legend.

    Args:
        comps: the components on the page.
        profile: the drawing profile.

    Returns:
        SHAPES keys in first-use order; empty when `look.component_shapes` is off.
    """
    if not profile.look.get("component_shapes", True):
        return []
    return list(dict.fromkeys(lane_shape(c, profile.kind_shapes) for c in comps))
