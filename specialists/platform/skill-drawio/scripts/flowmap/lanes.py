"""Flow page lanes: one lane per acting component, its head (a plain panel, or the component's symbol sized to its text inside one), the room each
lane keeps for arrow runs, and where those runs lie. Stdlib only.

Split from flowmap.pages on 2026-10-21 (module size) when lane heads gained structure and sized symbols (operator review, smc-resiliency).

Imported, not run: `from flowmap.lanes import draw_lanes, head_symbol_h` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.mxfile import BLANK, Page, heading, label, wrapped_lines

from .flow_geometry import LANE_HEAD_W, col_gap
from .model import MARGIN, GAP, comp_style, status_style
from .profile import Profile
from .shapes import FIT, PERSON_ICON, SHAPES, fit_height, lane_shape
from .tips import comp_tip

LANE_H = 120


def head_symbol_h(comp: dict, profile: Profile) -> float:
    """The height a lane head's symbol needs for its text (0 for a plain head), so the lane is at least that tall plus a margin.

    Args:
        comp: the lane's component.
        profile: the drawing profile.

    Returns:
        Pixels.
    """
    shape = lane_shape(comp, profile.kind_shapes)
    if shape in ("process", "person"):
        return 0.0
    chars = int((LANE_HEAD_W - 12) / 6.5 * SHAPES[shape][1])
    lines = (heading(comp["name"], profile.look["heading_scale"]), comp["kind"], BLANK, comp["host"])
    return fit_height(comp, profile, 16 + sum(wrapped_lines(x, chars) for x in lines) * 13)

def draw_lanes(page: Page, flow: dict, comps: dict, profile: Profile, top: float, box_h: dict, box_w: dict, room: dict | None = None,
               width: float | None = None) -> tuple[list, list, list]:
    """Draw one lane per component, in order of first use; each lane as tall as its tallest step.

    Args:
        page: the page.
        flow: the flow.
        comps: every component by id.
        profile: the kind colours.
        top: the first lane's top.
        box_h: each step box's height.
        box_w: each step box's width.
        room: {(lane index, "top" or "bottom"): pixels} reserved for arrow runs along that edge.
        width: the lanes' width (flow_page passes it from the label-widened gaps); None for the base column gaps.

    Returns:
        (lane component ids, lane tops, lane heights).
    """
    fid, steps = flow["id"], flow["steps"]
    lanes: list[str] = []
    for s in steps:
        if s["actor"] not in lanes:
            lanes.append(s["actor"])
    width = width or LANE_HEAD_W + sum(box_w.values()) + len(steps) * col_gap(profile.look) + GAP
    room = room or {}
    lane_h = [max([LANE_H, head_symbol_h(comps[cid], profile) + 16] + [box_h[s["id"]] + 28 for s in steps if s["actor"] == cid])
              + room.get((li, "top"), 0) + room.get((li, "bottom"), 0) for li, cid in enumerate(lanes)]
    lane_y = [top + sum(lane_h[:li]) for li in range(len(lanes))]
    for li, cid in enumerate(lanes):
        c = comps[cid]
        fill, stroke = profile.style(c["kind"])
        page.box(f"{fid}-lane-{li}", "", MARGIN, lane_y[li], width, lane_h[li], f"rounded=0;html=1;fillColor={fill};strokeColor={stroke};opacity=35;")
        shape = lane_shape(c, profile.kind_shapes)
        # name as a heading, kind in italics, host on its own line after a gap (operator review 2026-10-21: the left column needed structure)
        text = label(heading(f"**{c['name']}**", profile.look["heading_scale"]), f"*{c['kind']}*", BLANK, c["host"])
        if shape in ("process", "person"):
            page.box(f"{fid}-lanehead-{li}", text, MARGIN, lane_y[li], LANE_HEAD_W, lane_h[li],
                     comp_style(c["kind"], profile, "rounded=0;align=left;verticalAlign=middle;spacingLeft=10;spacingRight=8;fontSize=10;" + status_style(c)
                                + ("spacingRight=40;" if shape == "person" else "")), tooltip=comp_tip(c))
        else:   # a plain head panel, the symbol inside sized to its text (operator review 2026-10-21: a cloud stretched to the lane's height)
            page.box(f"{fid}-lanehead-{li}", "", MARGIN, lane_y[li], LANE_HEAD_W, lane_h[li],
                     comp_style(c["kind"], profile, "rounded=0;" + status_style(c)), tooltip=comp_tip(c))
            inner_w, inner_h = LANE_HEAD_W - 12, head_symbol_h(c, profile)
            page.box(f"{fid}-lanehead-{li}-shape", text, MARGIN + 6, lane_y[li] + (lane_h[li] - inner_h) / 2, inner_w, inner_h,
                     comp_style(c["kind"], profile, "fontSize=10;" + status_style(c) + SHAPES[shape][0] + FIT.get(shape, ("",))[0]),
                     tooltip=comp_tip(c))
        if shape == "person":   # a figure in the lane head's top right corner
            page.box(f"{fid}-lanehead-{li}-icon", "", MARGIN + LANE_HEAD_W - 34, lane_y[li] + 8, 22, 40, PERSON_ICON)
    return lanes, lane_y, lane_h
