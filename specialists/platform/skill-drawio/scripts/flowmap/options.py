"""The flow map's Options page: design choices side by side, and the decisions taken as a flow beside them.

One row per question (group), one column per option; each option shows its status, its flow as a chain of step boxes joined by routed arrows,
then its pros and cons, aligned across the row. A decision column on the left chains the decisions top to bottom: the block's own decisions
first, then one box per group, level with that group's row, with an arrow routed through the gap above the option heads to each chosen option.
Drawn only when the map has an `options` block. Stdlib only.

Added 2026-10-21 for smc-resiliency, whose operator wanted the update and recovery options, their flows, their trade-offs and the decisions
taken on one page.

Imported, not run: `from flowmap.options import options_page` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.mxfile import BLANK, Page, label, wrapped_lines

from .model import GAP, MARGIN
from .profile import Profile

#: Option column width, the step box width inside it, the vertical gap an arrow runs through, and line heights (font 11 and 12).
COL_W, STEP_W, ARROW_GAP, LINE_H, HEAD_LINE_H = 300, 260, 30, 14, 15
#: Decision column width, and the gap between a group's question and its option heads (a decision arrow runs along its middle).
DEC_W, HEAD_GAP = 280, 56
#: Characters per line: step boxes (260 px, font 11), pros/cons, option heads and decision boxes (280 px, font 11).
STEP_CHARS, BOX_CHARS, DEC_CHARS = 42, 50, 50
#: Fill and stroke per option status; the head of a chosen option is bold green, a rejected one grey.
STATUS_STYLE = {"chosen": ("#d5e8d4", "#82b366"), "evaluate": ("#fff2cc", "#d6b656"), "open": ("#dae8fc", "#6c8ebf"),
                "rejected": ("#f5f5f5", "#999999")}
STATUS_WORD = {"chosen": "CHOSEN", "evaluate": "TO EVALUATE", "open": "OPEN", "rejected": "NOT CHOSEN"}
BOX = "rounded=0;whiteSpace=wrap;html=1;align=left;verticalAlign=top;spacingLeft=6;spacingTop=2;fontSize=11;"
STEP = "rounded=1;whiteSpace=wrap;html=1;fontSize=11;fillColor=#ffffff;strokeColor=#666666;"
DECISION = "rounded=1;whiteSpace=wrap;html=1;align=left;verticalAlign=top;spacingLeft=6;spacingTop=2;fontSize=11;strokeWidth=2;"
TRADEOFF = {"pros": ("Pros", "#d5e8d4;strokeColor=#82b366"), "cons": ("Cons", "#f8cecc;strokeColor=#b85450")}
ARROW = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;endFill=1;strokeColor=#666666;strokeWidth=1;"
OPEN_ARROW = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;endFill=1;strokeColor=#6c8ebf;strokeWidth=2;dashed=1;"
DEC_ARROW = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;endFill=1;strokeColor=#82b366;strokeWidth=2;"


#: The legend's rows: (swatch style, swatch height, text), in two columns.
LEGEND = (
    [(BOX + f"fillColor={STATUS_STYLE[k][0]};strokeColor={STATUS_STYLE[k][1]};strokeWidth=2;", 20, f"Option head: {STATUS_WORD[k].lower()}")
     for k in ("chosen", "evaluate", "open", "rejected")]
    + [(DECISION + "fillColor=#d5e8d4;strokeColor=#82b366;", 20, "Decision taken (blue while open)"),
       (STEP, 20, "A step in the option's flow"),
       (BOX + "fillColor=" + TRADEOFF["pros"][1] + ";", 20, "Pros"),
       (BOX + "fillColor=" + TRADEOFF["cons"][1] + ";", 20, "Cons"),
       ("rounded=0;html=1;fillColor=#82b366;strokeColor=none;", 3, "Green arrow: the next decision, or a decision to its chosen option"),
       ("rounded=0;html=1;fillColor=#666666;strokeColor=none;", 1, "Grey arrow: the next step in an option's flow"),
       ("rounded=0;html=1;fillColor=none;strokeColor=#6c8ebf;strokeWidth=2;dashed=1;", 1, "Blue dashed: an open question to the option under evaluation")])


def _legend(page: Page, x: float, y: float, width: float) -> float:
    """The colour legend, in two columns, in the empty space right of the Decisions taken box.

    Args:
        page: the page to draw on.
        x: the legend's left edge.
        y: its top edge.
        width: the width it may use.

    Returns:
        The y just below it.
    """
    page.box("opt-leg-title", label("**Legend: box and arrow colours**"), x, y, width, 24, "text;html=1;align=left;fontSize=14;")
    half, rows = width / 2, (len(LEGEND) + 1) // 2
    for i, (style, h, text) in enumerate(LEGEND):
        cx, cy = x + (i // rows) * half, y + 30 + (i % rows) * 28
        page.box(f"opt-leg-{i}-s", "", cx, cy + (24 - h) / 2, 40, h, style)
        page.box(f"opt-leg-{i}-t", label(text), cx + 50, cy, half - 60, 24, "text;html=1;align=left;verticalAlign=middle;fontSize=12;")
    return y + 30 + rows * 28


def _height(lines: list[str], chars: int, line_h: int = LINE_H) -> int:
    """A box's height for its text lines at a characters-per-line budget.

    Args:
        lines: the label lines (formatting markers are ignored when counting).
        chars: characters per line.
        line_h: pixel height of one line.

    Returns:
        The height in pixels, padding included.
    """
    return 12 + sum(wrapped_lines(x.replace("*", "") or ".", chars) for x in lines) * line_h


def _list_lines(heading: str, items: list[str]) -> list[str]:
    """A pros or cons box's text: a bold heading, then one bullet per item.

    Args:
        heading: "Pros" or "Cons".
        items: the points; an empty list prints "none listed".

    Returns:
        Label lines.
    """
    return [f"**{heading}**"] + ([f"• {x}" for x in items] or ["none listed"])


def _head_lines(opt: dict) -> list[str]:
    """An option head's text: its title in bold and its status in italics.

    Args:
        opt: the option from the map.

    Returns:
        Label lines.
    """
    return [f"**{opt['title']}**", f"*{STATUS_WORD[opt['status']]}*"]


def _option_chain(page: Page, gid: str, opt: dict, x: float, top: float, head_h: float) -> float:
    """Draw one option's status head and its step chain, joined by routed arrows.

    Args:
        page: the page to draw on.
        gid: the group id (cell ids are `opt-<group>-<option>-...`).
        opt: the option from the map.
        x: the column's left edge.
        top: the column's top edge.
        head_h: the head's height (the row's tallest, so every chain starts level).

    Returns:
        The y just below the last step box.
    """
    cid = f"opt-{gid}-{opt['id']}"
    fill, stroke = STATUS_STYLE[opt["status"]]
    h = head_h
    page.box(f"{cid}-head", label(*_head_lines(opt)), x, top, COL_W, h, BOX + f"fillColor={fill};strokeColor={stroke};strokeWidth=2;", solid=True)
    y = top + h + GAP
    sx, prev = x + (COL_W - STEP_W) / 2, None
    for k, step in enumerate(opt["steps"], 1):
        sh = _height([step], STEP_CHARS)
        sid = f"{cid}-s{k}"
        page.box(sid, label(step), sx, y, STEP_W, sh, STEP, solid=True)
        if prev:
            px, py = prev
            page.route(f"{sid}-in", f"{cid}-s{k - 1}", sid, [(px, py), (px, y)], ARROW, klass="thin")
        prev, y = (sx + STEP_W / 2, y + sh), y + sh + ARROW_GAP
    return y - ARROW_GAP


def _tradeoff_row(page: Page, gid: str, opts: list[dict], key: str, x0: float, top: float) -> float:
    """Draw one row of pros (or cons) boxes, one per option, all starting at the same height so a row reads across.

    Args:
        page: the page to draw on.
        gid: the group id.
        opts: the group's options, in column order.
        key: "pros" or "cons".
        x0: the first option column's left edge.
        top: the row's top edge.

    Returns:
        The y just below the tallest box in the row.
    """
    heading, colour = TRADEOFF[key]
    texts = [_list_lines(heading, o[key]) for o in opts]
    h = max(_height(t, BOX_CHARS) for t in texts)
    for i, (o, t) in enumerate(zip(opts, texts)):
        page.box(f"opt-{gid}-{o['id']}-{key}", label(*t), x0 + i * (COL_W + GAP), top, COL_W, h, BOX + f"fillColor={colour};", solid=True)
    return top + h


def _decision_box(page: Page, g: dict, number: int, top: float, least_h: float) -> str:
    """Draw a group's decision in the decision column: green when an option is chosen, blue while open (its text says what happens next).

    Args:
        page: the page to draw on.
        g: the group from the map.
        number: the group's position, for the box title.
        top: the box's top edge (level with the group's question).
        least_h: the least height, so the box reaches past the arrow's row above the option heads.

    Returns:
        The box's cell id.
    """
    chosen = [o["title"] for o in g["options"] if o["status"] == "chosen"]
    title = f"**Decision {number}**" if chosen else f"**Decision {number}: open**"
    lines = [title, g.get("decision", "No option chosen yet.")] + [f"**→ {t}**" for t in chosen]
    fill, stroke = STATUS_STYLE["chosen" if chosen else "open"]
    cid = f"opt-dec-{g['id']}"
    page.box(cid, label(*lines), MARGIN, top, DEC_W, max(least_h, _height(lines, DEC_CHARS)), DECISION + f"fillColor={fill};strokeColor={stroke};",
             solid=True)
    return cid


def _chain_arrow(page: Page, src: str, dst: str) -> None:
    """A vertical arrow down the decision column from one decision box to the next.

    Args:
        page: the page to draw on.
        src: the upper decision box id.
        dst: the lower decision box id.
    """
    sx, sy, sw, sh = page.rects[src]
    cx = sx + sw / 2
    page.route(f"{dst}-in", src, dst, [(cx, sy + sh), (cx, page.rects[dst][1])], DEC_ARROW, klass="thick")


def _group_row(page: Page, g: dict, number: int, x0: float, width: float, y: float, prev: str) -> tuple[float, str]:
    """Draw one group: its question, its decision box (chained from the previous one), its options and the arrows to the chosen ones.

    Args:
        page: the page to draw on.
        g: the group from the map.
        number: the group's position.
        x0: the first option column's left edge.
        width: the options area's width.
        y: the row's top edge.
        prev: the previous decision box id, chained to this group's.

    Returns:
        The y below the row, and this group's decision box id.
    """
    lines = [f"**{g['title']}**"]
    gh = _height(lines, int((width - 16) / 7), HEAD_LINE_H)
    page.box(f"opt-{g['id']}", label(*lines), x0, y, width, gh, BOX + "fontSize=12;fillColor=#eeeeee;strokeColor=#333333;")
    heads_top, band = y + gh + HEAD_GAP, y + gh + HEAD_GAP / 2
    dec = _decision_box(page, g, number, y, gh + HEAD_GAP)
    _chain_arrow(page, prev, dec)
    head_h = max(_height(_head_lines(o), BOX_CHARS) for o in g["options"])
    bottom = max(_option_chain(page, g["id"], o, x0 + i * (COL_W + GAP), heads_top, head_h) for i, o in enumerate(g["options"]))
    decided = any(o["status"] == "chosen" for o in g["options"])
    for i, o in enumerate(g["options"]):   # solid to a chosen option; while open, dashed to an option under evaluation
        if o["status"] == "chosen" or (not decided and o["status"] == "evaluate"):
            cx = x0 + i * (COL_W + GAP) + COL_W / 2
            style = DEC_ARROW if decided else OPEN_ARROW
            page.route(f"{dec}-to-{o['id']}", dec, f"opt-{g['id']}-{o['id']}-head", [(MARGIN + DEC_W, band), (cx, band), (cx, heads_top)],
                       style, klass="thick", ignore=(f"opt-{g['id']}",))
    y = _tradeoff_row(page, g["id"], g["options"], "pros", x0, bottom + GAP) + GAP / 2
    return _tradeoff_row(page, g["id"], g["options"], "cons", x0, y) + GAP * 2, dec


def options_page(data: dict, profile: Profile) -> Page:
    """The Options page: a header, the Decisions taken box beside the colour legend, then the decision column beside one row per group.

    Args:
        data: the validated map, with an `options` block.
        profile: the drawing profile (unused today; kept so every page builder has the same signature).

    Returns:
        The page.
    """
    del profile
    block = data["options"]
    widest = max(len(g["options"]) for g in block["groups"])
    x0, width = MARGIN + DEC_W + 2 * GAP, widest * COL_W + (widest - 1) * GAP
    page = Page("options", f"Options: {block['title']}"[:60])
    head = [f"**{block['title']}**"] + ([BLANK, block["purpose"]] if block.get("purpose") else []) + [
        BLANK,
        "**Left:** the decisions taken, as a flow; a green arrow leads to the chosen option, a blue dashed one to an option under evaluation.",
        "**Rows:** one question each.",
        "**Columns:** one option each: its flow top to bottom, then its pros and cons.",
        "**Colours:** see the legend.",
        BLANK, "[back to Overview]"]
    total = x0 - MARGIN + width
    h = _height(head, int((total - 16) / 7), HEAD_LINE_H)
    page.box("opt-head", label(*head), MARGIN, MARGIN, total, h, BOX + "fontSize=12;fillColor=#fafafa;strokeColor=#666666;",
             link="data:page/id,overview")
    y = MARGIN + h + GAP
    start = ["**Decisions taken**"] + [f"• {d}" for d in block.get("decisions", [])]
    page.box("opt-dec-start", label(*start), MARGIN, y, DEC_W, _height(start, DEC_CHARS),
             DECISION + "fillColor=#d5e8d4;strokeColor=#82b366;", solid=True)
    prev = "opt-dec-start"
    y = max(y + page.rects[prev][3], _legend(page, x0, y, width)) + GAP * 2
    for n, g in enumerate(block["groups"], 1):
        y, prev = _group_row(page, g, n, x0, width, y, prev)
    return page
