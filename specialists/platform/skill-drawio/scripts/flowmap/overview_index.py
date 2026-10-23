"""The Overview page's right-hand column: the flow index (a clickable box per page), the component kind legend, the status legend and the
arrow colour legend. Moved out of flowmap.overview on 2026-10-21 to keep that module within its size budget; behaviour unchanged. Stdlib only.

Imported, not run: `from flowmap.overview_index import flow_index, colour_legend` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.mxfile import Page, label, wrapped_lines

from .model import comp_style, flow_family, option_blocks
from .shapes import component_shape, fit_height, person_badge
from .overview_layout import THIN_GREY
from .profile import DISTINCT, Profile

# An index box is 340 px wide at font 11 with a bold first line: about 50 characters a line, 14 px a line (operator, 2026-10-22: two-line
# titles overflowed the fixed 52 px box). A box is never shorter than INDEX_MIN_H; boxes stack INDEX_GAP apart.
INDEX_CHARS, INDEX_LINE_H, INDEX_MIN_H, INDEX_GAP = 50, 14, 52, 10


def index_height(*lines: str) -> int:
    """How tall a flow index box must be for its text.

    Args:
        lines: the label lines, formatting markers included (ignored when counting).

    Returns:
        The height in pixels, padding included, at least INDEX_MIN_H.
    """
    return max(INDEX_MIN_H, 10 + round(sum(wrapped_lines(x.replace("*", ""), INDEX_CHARS) for x in lines)) * INDEX_LINE_H)


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
                                "×n on a thick arrow = how many box-to-box dependencies it stands for (one per box in the source group "
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


def family_entries(page: Page, data: dict, profile: Profile, x: float, y: float) -> float:
    """One index entry per family End-to-end page (flowmap.e2e_family), right under the full page's; none unless `look.e2e_family_pages`.

    Args:
        page: the Overview.
        data: the validated map.
        profile: the drawing profile (families, look).
        x: the index column's left edge.
        y: the index's running offset (entries go at y + 102, as decision page entries do).

    Returns:
        The offset after the entries.
    """
    if not profile.look.get("e2e_family_pages"):
        return y
    of = [flow_family(f, profile) for f in data["flows"]]
    for fam, name, _col, _ids in (g for g in profile.families if g[0] in of):
        nums = ", ".join(str(i) for i, f in enumerate(of, 1) if f == fam)
        page.box(f"ov-f-end-to-end-{fam}", label(f"**End-to-end: {name}**", f"flows {nums} only"), x, y + 102, 340, 52,
                 "rounded=1;whiteSpace=wrap;html=1;fillColor=#f0f4fa;strokeColor=#3d5a80;fontSize=11;align=left;spacingLeft=6;",
                 link=f"data:page/id,end-to-end-{fam}", tooltip=f"The {name} flows only, and the components they touch")
        y += 62
    return y


def flow_index(page: Page, data: dict, profile: Profile, x: float, y: float) -> float:
    """The flow index (one clickable box per flow page, plus the End-to-end page and, when the map has them, the decision pages) and the component
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
    y = family_entries(page, data, profile, x, y)
    for pid, name, block in option_blocks(data):   # decision pages (flowmap.options) sit after the End-to-end entry; without them the index is unchanged
        page.box(f"ov-f-{pid}", label(f"**{name}**", "the questions, each choice's flow, pros and cons, and what was decided"),
                 x, y + 102, 340, 52, "rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=11;align=left;spacingLeft=6;",
                 link=f"data:page/id,{pid}", tooltip=block.get("purpose", block["title"]))
        y += 62
    top = y + 102
    for fi, f in enumerate(data["flows"]):
        sub = f"{f['trigger']['kind']} · runs on {f['runs_on']} · {f['category']}"
        title, line2 = f"**{fi + 1}. {f['title']}**", (f"*{f['status']['state']} since {f['status']['since']}* · {sub}" if f.get("status") else sub)
        h = index_height(title, line2)
        page.box(f"ov-f-{f['id']}", label(title, line2),
                 x, top, 340, h, "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#3d5a80;fontSize=11;align=left;spacingLeft=6;",
                 link=f"data:page/id,flow-{f['id']}", tooltip=f["purpose"])
        top += h + INDEX_GAP
    ly = top + 20
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
        for n, (key, text, fill, stroke) in enumerate((("opt", "decision page: questions, choices and what was decided", "#d5e8d4", "#82b366"),
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
