"""The Overview page's right-hand column: the flow index (a clickable box per page), the component kind legend, the status legend and the
arrow colour legend. Moved out of flowmap.overview on 2026-10-21 to keep that module within its size budget; behaviour unchanged. Stdlib only.

Imported, not run: `from flowmap.overview_index import flow_index, colour_legend` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.mxfile import Page, label

from .model import comp_style
from .overview_layout import THIN_GREY
from .profile import DISTINCT, Profile


def colour_legend(page: Page, x: float, y: float, thick: list) -> None:
    """The arrow colour legend, below the component kind legend on the right: one swatch per thick colour, the thin grey, and the dots.

    Args:
        page: the page.
        x: left edge.
        y: top edge.
        thick: (colour, text) per thick arrow colour.
    """
    w = 340
    page.box("ov-leg-title", label("**Legend: arrow colours**"), x, y, w, 24, "text;html=1;align=left;fontSize=14;")
    y += 30
    page.box("ov-leg-h1", label("**Thick: dependencies into a group**",
                                "Number on a thick arrow = how many box-to-box dependencies it stands for (one per box in the source group "
                                "needing a box in the target group, counted per need)"), x, y, w, 76,
             "text;html=1;align=left;verticalAlign=top;whiteSpace=wrap;fontSize=12;")
    y += 82
    for i, (colour, text) in enumerate(thick):
        page.box(f"ov-leg-into-{i}-s", "", x, y + i * 26 + 10, 40, 5, f"rounded=0;html=1;fillColor={colour};strokeColor=none;")
        page.box(f"ov-leg-into-{i}-t", label(text), x + 50, y + i * 26, w - 50, 24, "text;html=1;align=left;verticalAlign=middle;fontSize=12;")
    y += len(thick) * 26 + 10
    page.box("ov-leg-thin-s", "", x, y + 10, 40, 2, f"rounded=0;html=1;fillColor={THIN_GREY};strokeColor=none;")
    page.box("ov-leg-thin-t", label("**Thin grey:** a dependency inside a group (a box sits above what it needs)"), x + 50, y, w - 50, 36,
             "text;html=1;align=left;verticalAlign=top;whiteSpace=wrap;fontSize=12;")
    y += 46
    page.box("ov-leg-dot", "", x + 14, y + 3, 12, 12, f"ellipse;html=1;fillColor={DISTINCT[0]};strokeColor=#ffffff;")
    page.box("ov-leg-dot-t", label("A dot on a box: it feeds the thick arrow of that colour (its Needs list names what)"), x + 50, y, w - 50, 36,
             "text;html=1;align=left;verticalAlign=top;whiteSpace=wrap;fontSize=12;")


def flow_index(page: Page, data: dict, profile: Profile, x: float, y: float) -> float:
    """The flow index (one clickable box per flow page, plus the End-to-end page and, when the map has one, the Options page) and the component
    kind legend, right of the group grid.

    Args:
        page: the page.
        data: the validated map.
        profile: the kind colours.
        x: left edge.
        y: top edge.

    Returns:
        The bottom of the kind legend (the colour legend goes below it).
    """
    page.box("ov-flows", label("**Flows** (click to open the page)"), x, y, 340, 30, "text;html=1;align=left;verticalAlign=middle;fontSize=13;")
    page.box("ov-f-end-to-end", label("**End-to-end flow**", "every component and every flow on one page"), x, y + 40, 340, 52,
             "rounded=1;whiteSpace=wrap;html=1;fillColor=#f0f4fa;strokeColor=#3d5a80;fontSize=11;align=left;spacingLeft=6;",
             link="data:page/id,end-to-end", tooltip="All flows as coloured paths through their components, one layer per family")
    if data.get("options"):   # the Options page (flowmap.options) sits after the End-to-end entry; without it the index is unchanged
        page.box("ov-f-options", label(f"**Options: {data['options']['title']}**", "the choices, each option's flow, pros, cons and the decisions"),
                 x, y + 102, 340, 52, "rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=11;align=left;spacingLeft=6;",
                 link="data:page/id,options", tooltip=data["options"].get("purpose", data["options"]["title"]))
        y += 62
    for fi, f in enumerate(data["flows"]):
        sub = f"{f['trigger']['kind']} · runs on {f['runs_on']} · {f['category']}"
        page.box(f"ov-f-{f['id']}", label(f"**{fi + 1}. {f['title']}**", f"*{f['status']['state']} since {f['status']['since']}* · {sub}" if f.get("status") else sub),
                 x, y + 102 + fi * 62, 340, 52, "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#3d5a80;fontSize=11;align=left;spacingLeft=6;",
                 link=f"data:page/id,flow-{f['id']}", tooltip=f["purpose"])
    ly = y + 122 + len(data["flows"]) * 62
    page.box("ov-legend", label("**Legend: component kinds**"), x, ly - 18, 340, 30, "text;html=1;align=left;fontSize=12;whiteSpace=wrap;")
    for ki, kind in enumerate(profile.kind_style):
        page.box(f"ov-k-{kind}", label(kind), x + (ki % 2) * 175, ly + 20 + (ki // 2) * 34, 165, 28, comp_style(kind, profile))
    bottom = ly + 20 + ((len(profile.kind_style) + 1) // 2) * 34
    if any(i.get("status") for i in data["components"] + data["flows"]):   # only maps that record status get this legend
        page.box("ov-status-leg", label("**Status:** a dashed border is proposed or designed (not yet run); a flow's index line and page header",
                                        "name its state (proposed, designed, spike-proved, built, live) and since when."),
                 x, bottom + 8, 340, 64, "text;html=1;align=left;verticalAlign=top;fontSize=11;whiteSpace=wrap;")
        bottom += 80
    return bottom
