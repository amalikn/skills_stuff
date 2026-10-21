"""The Overview page's right-hand column: the flow index (a clickable box per page), the component kind legend, the status legend and the
arrow colour legend. Moved out of flowmap.overview on 2026-10-21 to keep that module within its size budget; behaviour unchanged. Stdlib only.

Imported, not run: `from flowmap.overview_index import flow_index, colour_legend` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.mxfile import Page, label

from .model import comp_style, option_blocks
from .shapes import component_shape, fit_height, person_badge
from .overview_layout import THIN_GREY
from .profile import DISTINCT, Profile


def colour_legend(page: Page, x: float, y: float, thick: list) -> float:
    """The arrow colour legend, below the component kind legend on the right: one swatch per thick colour, the thin grey, and the dots.

    Args:
        page: the page.
        x: left edge.
        y: top edge.
        thick: (colour, text) per thick arrow colour.

    Returns:
        The y just below the legend.
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
    return y + 40


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
    for pid, name, block in option_blocks(data):   # option pages (flowmap.options) sit after the End-to-end entry; without them the index is unchanged
        page.box(f"ov-f-{pid}", label(f"**{name}**", "the choices, each option's flow, pros, cons and the decisions"),
                 x, y + 102, 340, 52, "rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=11;align=left;spacingLeft=6;",
                 link=f"data:page/id,{pid}", tooltip=block.get("purpose", block["title"]))
        y += 62
    for fi, f in enumerate(data["flows"]):
        sub = f"{f['trigger']['kind']} · runs on {f['runs_on']} · {f['category']}"
        page.box(f"ov-f-{f['id']}", label(f"**{fi + 1}. {f['title']}**", f"*{f['status']['state']} since {f['status']['since']}* · {sub}" if f.get("status") else sub),
                 x, y + 102 + fi * 62, 340, 52, "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#3d5a80;fontSize=11;align=left;spacingLeft=6;",
                 link=f"data:page/id,flow-{f['id']}", tooltip=f["purpose"])
    ly = y + 122 + len(data["flows"]) * 62
    page.box("ov-legend", label("**Legend: component kinds**"), x, ly - 18, 340, 30, "text;html=1;align=left;fontSize=12;whiteSpace=wrap;")
    kinds = list(profile.kind_style)   # each kind drawn as it appears in the drawing: its colour and, when on, its symbol
    sample_h = [fit_height({"kind": k}, profile, 28) for k in kinds]
    row_h = [max(sample_h[r * 2:r * 2 + 2]) + 6 for r in range((len(kinds) + 1) // 2)]
    for ki, kind in enumerate(kinds):
        sample, top = {"kind": kind}, ly + 20 + sum(row_h[:ki // 2])
        page.box(f"ov-k-{kind}", label(kind), x + (ki % 2) * 175, top, 165, sample_h[ki],
                 comp_style(kind, profile, "verticalAlign=middle;" + component_shape(sample, profile)))
        person_badge(page, sample, profile, f"ov-k-{kind}", x + (ki % 2) * 175 + 165, top + sample_h[ki] + 2)
    bottom = ly + 20 + sum(row_h)
    blocks = option_blocks(data)
    if blocks:   # the index's box colours (operator, 2026-10-21: the green option boxes had no legend)
        page.box("ov-idx-leg", label("**Legend: index boxes**"), x, bottom + 8, 340, 24, "text;html=1;align=left;fontSize=12;whiteSpace=wrap;")
        for n, (key, text, fill, stroke) in enumerate((("opt", "option page: choices and decisions", "#d5e8d4", "#82b366"),
                                                       ("e2e", "End-to-end flow", "#f0f4fa", "#3d5a80"),
                                                       ("flow", "one flow's page", "#ffffff", "#3d5a80"))):
            page.box(f"ov-idx-{key}", label(text), x, bottom + 38 + n * 32, 340, 26,
                     f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};fontSize=11;align=left;spacingLeft=6;")
        bottom += 38 + 3 * 32
    if any(i.get("status") for i in data["components"] + data["flows"]):   # only maps that record status get this legend
        page.box("ov-status-leg", label("**Status:** a dashed border is proposed or designed (not yet run); a flow's index line and page header "
                                        "name its state (proposed, designed, spike-proved, built, live) and since when."),
                 x, bottom + 8, 340, 64, "text;html=1;align=left;verticalAlign=top;fontSize=11;whiteSpace=wrap;")
        bottom += 80
    return bottom
