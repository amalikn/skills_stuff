"""BPMN notation for a flow: the same graph and lanes as a swimlane page, drawn in BPMN's symbols with draw.io's own BPMN shapes. Stdlib only.

The mapping: start and end are events (a circle, thin at the start and thick at the end), a stop is an error end event, a step is a task, a step
that runs another flow is a call activity (thick border), a decision is an exclusive gateway, every arrow is a sequence flow, and the lanes sit in
a pool named for the flow. BPMN allows an exclusive gateway without its X marker, so a question stays inside its diamond and reads at a glance.
Only what the map states is drawn: a flow map has no message flows between pools, so none are invented. The shape styles come from draw.io's own
example (documents/drawio-sources-20261102/).

Imported, not run: `from flowmap.flowchart import bpmn` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.mxfile import Page, label

#: An event's size, and its words' width beside it.
EVENT, EVENT_TEXT = 36, 110
EVENT_STYLE = ("shape=mxgraph.bpmn.shape;html=1;perimeter=ellipsePerimeter;labelBackgroundColor=none;strokeColor=#000000;strokeWidth=2;fillColor=#ffffff;"
               "outline={outline};symbol={symbol};")
#: An error end event in the step pages' red.
ERROR = EVENT_STYLE.replace("strokeColor=#000000", "strokeColor=#b85450").replace("fillColor=#ffffff", "fillColor=#f8cecc")
OUTLINE = {"start": ("standard", "general"), "end": ("end", "general"), "error": ("end", "error")}
TEXT = "text;html=1;whiteSpace=wrap;align=left;verticalAlign=middle;fontSize=10;labelBackgroundColor=none;spacingLeft=2;"
TASK = "rounded=1;arcSize=14;whiteSpace=wrap;html=1;fontSize=11;fillColor=#ffffff;strokeColor=#000000;strokeWidth=1.5;"
STEP_STYLES = {"decision": "rhombus;whiteSpace=wrap;html=1;fontSize=11;fillColor=#ffffff;strokeColor=#000000;strokeWidth=1.5;spacingLeft=30;spacingRight=30;",
               "terminator": TASK.replace("#000000", "#b3261e"), "predefined-process": TASK.replace("strokeWidth=1.5", "strokeWidth=3")}
LEGEND = (("start", "Start event"), ("end", "End event"), ("error", "Error end event"))


def step_style(shape: str, fill: str = "#ffffff", stroke: str = "#000000") -> str:
    """A step's BPMN style, in its actor's colours as on the step pages (operator, 2026-11-02), a stop in red.

    Args:
        shape: its flowmap.shapes key.
        fill: the actor kind's fill.
        stroke: the actor kind's stroke.

    Returns:
        A gateway, a call activity, else a task.
    """
    style = STEP_STYLES.get(shape, TASK)
    return style if shape == "terminator" else style.replace("fillColor=#ffffff", f"fillColor={fill}").replace("strokeColor=#000000", f"strokeColor={stroke}")


def event(page: Page, cid: str, kind: str, rect: tuple, lines: list[str], turned: bool = False) -> None:
    """Draw an event with its words beside it, centred in its cell, or at the cell's left on a turned page, where arrows arrive from the left.

    Args:
        page: the page.
        cid: the cell id.
        kind: a key of OUTLINE.
        rect: the node's cell (x, y, width, height).
        lines: its words.
        turned: the page runs left to right.
    """
    x, y, w, h = rect
    outline, symbol = OUTLINE[kind]
    left = x if turned else x + w / 2 - EVENT / 2
    top = y + h / 2 - EVENT / 2
    page.box(cid, "", left, top, EVENT, EVENT, (ERROR if kind == "error" else EVENT_STYLE).format(outline=outline, symbol=symbol), solid=True)
    if turned and kind == "start":   # an arrow leaves its right side, so its words go above
        page.box(f"{cid}-text", label(*lines), left - 4, top - 20, EVENT_TEXT + 40, 18, TEXT)
    else:
        page.box(f"{cid}-text", label(*lines), left + EVENT + 4, y, EVENT_TEXT, h, TEXT)   # beside the circle, in the half of the cell to its right


def legend(page: Page, x: float, y: float, prefix: str) -> None:
    """A row of the BPMN symbols.

    Args:
        page: the page.
        x: its left edge.
        y: its top edge.
        prefix: the cell id prefix.
    """
    for k, (kind, name) in enumerate(LEGEND):
        event(page, f"{prefix}-legend-{kind}", kind, (x + k * 200, y, EVENT, EVENT), [name])
    for k, (style, name) in enumerate(((TASK, "Task"), (STEP_STYLES["predefined-process"], "Call activity"), (STEP_STYLES["decision"], "Exclusive gateway"))):
        page.box(f"{prefix}-legend-t{k}", label(name), x + k * 200, y + EVENT + 16, 150, 44, style)
