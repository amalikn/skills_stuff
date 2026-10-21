"""Flow page shapes: the standard flowchart symbols (ISO 5807 / draw.io's Flowchart set) a step or a lane head is drawn with, how each is derived
from the map, and the per-page shape legend. Stdlib only.

Adopted 2026-10-21 (smc-resiliency's operator chose all twelve after the sample in references/screenshots/20261021-shape-vocabulary-sample/).
A step's shape comes from, in order: its own `shape`; a gate (decision); a `flow` it runs (predefined process); an actor whose kind draws as a
person (manual operation); the first step or a step nothing follows (terminator); a transport that crosses a network (data in or out); else a
process. A lane head's shape comes from the component's own `shape`, else its kind (`drawing.kind_shapes`, else DEFAULT_KIND_SHAPES).

Imported, not run: `from flowmap.shapes import step_shape, lane_shape` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.mxfile import Page, label

#: Each shape: (style fragment, text-width factor, height factor, legend text). The style replaces the box's rectangle; the factors shrink the
#: characters per line and grow the height where the outline eats into the text area (a diamond most).
SHAPES = {
    "terminator": ("rounded=1;arcSize=40;spacingLeft=22;spacingRight=18;spacingTop=12;", 0.85, 1.1, "Terminator: where a flow starts or ends"),
    "process": ("rounded=0;", 1.0, 1.0, "Process: a step that does work"),
    "decision": ("rhombus;align=center;verticalAlign=middle;spacingLeft=72;spacingRight=72;spacingTop=0;", 0.5, 1.45,
                 "Decision: a gate that picks the next step"),
    "manual-operation": ("shape=trapezoid;perimeter=trapezoidPerimeter;flipV=1;fixedSize=1;size=12;spacingLeft=18;spacingRight=18;", 0.95, 1.0,
                         "Manual operation: a person acts"),
    "preparation": ("shape=hexagon;perimeter=hexagonPerimeter2;fixedSize=1;size=12;spacingLeft=18;spacingRight=18;", 0.95, 1.0,
                    "Preparation: set-up before the change"),
    "predefined-process": ("shape=process;backgroundOutline=1;size=0.06;spacingLeft=20;spacingRight=20;", 0.88, 1.0,
                           "Predefined process: runs another flow (click to open it)"),
    "delay": ("shape=delay;spacingRight=24;", 0.9, 1.0, "Delay: waits for time (a timer, a deadline)"),
    "stored-data": ("shape=cylinder3;boundedLbl=1;backgroundOutline=1;size=10;", 1.0, 1.1, "Stored data: a store that persists"),
    "document": ("shape=document;boundedLbl=1;size=0.15;", 1.0, 1.2, "Document: a file or record written"),
    "data-io": ("shape=parallelogram;perimeter=parallelogramPerimeter;fixedSize=1;size=10;spacingLeft=16;spacingRight=16;", 0.95, 1.0,
                "Data in or out: data crossing a link"),
    "external": ("ellipse;shape=cloud;spacingLeft=16;spacingRight=16;spacingTop=10;", 0.8, 1.2, "External system: outside the box"),
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
