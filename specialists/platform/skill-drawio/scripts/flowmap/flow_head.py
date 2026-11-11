"""A step page's header: its lines (title, purpose, fields, link back), and the box itself with the `‹ E2E page` button above its top-left corner
(operator, 2026-11-11). Moved out of flowmap.pages on 2026-11-11 to keep that module within its size budget. Stdlib only.

Imported, not run: `from flowmap.flow_head import flow_header` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.mxfile import BLANK, Page, label, wrapped_lines

from .e2e_family import back_button
from .model import MARGIN, status_text

#: A flow page header's line height (font 12).
HEAD_LINE_H = 15
#: The `‹ E2E page` button's height (flowmap.e2e_family.back_button) and the gap under it, above a step page's header.
BACK_H, BACK_GAP = 22, 8


def flow_header_lines(flow: dict, comps: dict[str, dict], number: int | str) -> list[str]:
    """A flow page's header, set out like a note: bold title and category, a blank line, the purpose, a blank line, one line per field with its
    name in bold, a blank line, then the link back.

    Args:
        flow: the flow from the map.
        comps: every component by id.
        number: the flow's number or label (flowmap.map_parts.flow_labels, "PHP 2" in an own family).

    Returns:
        Label lines for drawio.mxfile.label() (fields the flow does not have are left out).
    """
    deps = flow.get("dependencies", {})
    fields = [f"**Status:** {status_text(flow)}" if flow.get("status") else "",
              f"**Trigger:** {flow['trigger']['kind']}: {flow['trigger']['detail']}",
              f"**Runs on:** {comps[flow['runs_on']]['name']} · **Owner:** {comps[flow['owner']]['name']}",
              f"**Budget:** {flow['budget']}" if flow.get("budget") else "",
              ("**Depends on flows:** " + ", ".join(deps["flows"])) if deps.get("flows") else "",
              ("**Depends on components:** " + ", ".join(comps[c]["name"] for c in deps["components"])) if deps.get("components") else "",
              ("**Credentials:** " + ", ".join(deps["credentials"])) if deps.get("credentials") else "",
              ("**Docs:** " + ", ".join(flow["docs"])) if flow.get("docs") else ""]
    return ([f"**{number}. {flow['title']}** ({flow['category']})", BLANK, flow["purpose"], BLANK]
            + [x for x in fields if x] + [BLANK, "[back to Overview]"])


def flow_header(page: Page, flow: dict, comps: dict, number: int | str, width: float) -> float:
    """Draw a flow page's header box at the top left, linked back to the Overview.

    Args:
        page: the page.
        flow: the flow from the map.
        comps: every component by id.
        number: the flow's number or label.
        width: the lanes' width (the header is at least 900 px wide).

    Returns:
        The header's height.
    """
    header = flow_header_lines(flow, comps, number)
    head_w = max(width, 900)
    head_chars = int((head_w - 16) / 7)   # font 12: about 6.5 px a character, so 7 px is conservative
    head_h = 14 + sum(wrapped_lines(h.replace("*", ""), head_chars) for h in header) * HEAD_LINE_H
    top = MARGIN
    if getattr(page, "back_link", ""):   # `‹ E2E page` above the header's top-left corner, not beside its right end (operator, 2026-11-11)
        back_button(page, MARGIN, MARGIN)
        top = MARGIN + BACK_H + BACK_GAP
    page.box(f"{flow['id']}-head", label(*header), MARGIN, top, head_w, head_h,
             "rounded=0;whiteSpace=wrap;html=1;fillColor=#fafafa;strokeColor=#666666;align=left;verticalAlign=top;spacingLeft=8;spacingTop=4;fontSize=12;",
             link="data:page/id,overview")
    return head_h + top - MARGIN   # callers place the lanes below MARGIN + this
