"""The flow map's per-flow pages and the whole file: one page per flow (a header, a lane per component, numbered step boxes and arrows, a note
per step with its failure modes), render() for the multi-page file, and evaluate() for the drift check. Stdlib only.

Flow pages are simple enough for draw.io's own router (drawio.mxfile.Page.edge with pinned ports); the Overview and End-to-end pages are routed
by flowmap.overview and flowmap.e2e. The output is deterministic (no timestamps; sorted only where the map gives no order), so the file changes
only when the map does, and a project's check compares it byte for byte with the committed drawing.

Imported, not run: `from flowmap.pages import render, evaluate` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from pathlib import Path

from drawio.mxfile import BLANK, Page, banner, heading, label, mxfile, wrapped_lines

from .e2e import end_to_end_page
from .model import GAP, MARGIN, Outcome, comp_style, load, status_style, status_text, step_targets
from .model import option_blocks
from .options import options_page
from .flow_geometry import LANE_HEAD_W, back_arrow, col_gap, column_lefts, label_gaps, plan_runs, reserve, run_ys, step_width
from .lanes import draw_lanes
from .routing import branch_label, route_flow
from .uncross import uncross
from .shapes import FIT, PERSON_ICON, SHAPES, SLANTED, fit_height, lane_shape, shape_legend, step_shape
from .overview import overview_page
from .profile import Profile

#: Flow page geometry: lane heading width, least lane height, step column width, step box width and least height.
STEP_H = 92
#: Note text budget (characters per line) and line height.
NOTE_CHARS, NOTE_LINE_H = 44, 13   # font 10 draws about 12 px a line (measured 2026-10-21); 13 keeps a margin
#: Step box text budget (200 px at font size 10) and line height.
STEP_LINE_H = 13   # the characters a line a step box is sized for are drawing.look.step_chars
#: A flow page header's line height (font 12).
HEAD_LINE_H = 15
#: A step note's sections, in reading order: (step key, heading, whether its items are code).
NOTE_SECTIONS = (("reads", "Reads", False), ("writes", "Writes", False), ("code", "Code", True), ("failures", "Fails", False), ("look", "Look", False))


def action_clauses(text: str) -> list[str]:
    """An action's clauses: split on "; " outside brackets only, so a bracketed aside stays whole (operator review 2026-10-22: "(the operator's
    click; agents never approve)" was cut into two bullets).

    Args:
        text: the step's action.

    Returns:
        The non-empty clauses, stripped.
    """
    out, depth, cur, i = [], 0, "", 0
    while i < len(text):
        if depth == 0 and text.startswith("; ", i):
            out, cur, i = out + [cur], "", i + 2
            continue
        depth = max(0, depth + (text[i] in "([{") - (text[i] in ")]}"))
        cur, i = cur + text[i], i + 1
    return [c.strip() for c in out + [cur] if c.strip()]


def step_lines(step: dict, number: int, bullets: bool = True, scale: int = 100) -> list[str]:
    """A step box's text: the bold title, a blank line, the action, a blank line, the transport in italics, the gate in bold and the status.

    Args:
        step: the step from the map.
        number: its position in the flow.
        bullets: set an action of clauses joined by "; " one clause a line (`drawing.look.action_bullets`).
        scale: the title's size, percent of the box font (`drawing.look.heading_scale`).

    Returns:
        Label lines for drawio.mxfile.label().
    """
    clauses = action_clauses(step["action"])
    action = [step["action"]] if not bullets else clauses if len(clauses) == 1 else [f"• {c}" for c in clauses]   # one clause a line: long actions read as a list
    return ([heading(f"**{number}. {step['id']}**", scale), BLANK] + action + [BLANK, f"*via {' + '.join(step['via'])}*"]
            + ([f"**GATE: {step['gate']}**"] if step.get("gate") else [])
            + ([f"*{step['status']['state']} since {step['status']['since']}*"] if step.get("status") else []))


def note_lines(step: dict, number: int) -> list[str]:
    """A step note as sections: the title, then per non-empty section a blank line, a bold heading and one bullet per item (code in monospace).

    Args:
        step: the step from the map.
        number: its position in the flow.

    Returns:
        Label lines for drawio.mxfile.label().
    """
    out = [f"**{number}. {step['id']}**"]
    for key, heading, is_code in NOTE_SECTIONS:
        if step.get(key):
            out += [BLANK, f"**{heading}**"] + [f"• `{item}`" if is_code else f"• {item}" for item in step[key]]
    return out


def flow_header_lines(flow: dict, comps: dict[str, dict], number: int) -> list[str]:
    """A flow page's header, set out like a note: bold title and category, a blank line, the purpose, a blank line, one line per field with its
    name in bold, a blank line, then the link back.

    Args:
        flow: the flow from the map.
        comps: every component by id.
        number: the flow's position in the map.

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


def size_steps(steps: list[dict], shapes: dict, profile: Profile) -> tuple[dict, dict, dict]:
    """Each step's text, width and height. A box is as tall as its text needs; when that would make it taller than `look.max_aspect` times its
    width, it is widened (in 20 px steps, up to `look.decision_width`) so long text makes a wider box, not a tall narrow one (operator review
    2026-10-21: a tall terminator squeezed its text against its curved ends).

    Args:
        steps: the flow's steps.
        shapes: each step's shape.
        profile: the drawing profile.

    Returns:
        (texts, widths, heights), each by step id.
    """
    look = profile.look
    texts = {s["id"]: step_lines(s, k + 1, look["action_bullets"], look["heading_scale"]) for k, s in enumerate(steps)}
    box_w = {sid: step_width(sh, look) for sid, sh in shapes.items()}
    box_h = {}
    widest = max(int(look.get("decision_width", 380)), max(box_w.values(), default=0))
    for sid, lines in texts.items():   # the outline eats into the text area: fewer characters a line, a taller box
        _style, wf, hf = SHAPES[shapes[sid]][:3]
        while True:
            chars = int(look["step_chars"] * box_w[sid] / look["step_width"] * wf)
            box_h[sid] = round(max(STEP_H, 20 + sum(wrapped_lines(x.replace("*", ""), chars) for x in lines) * STEP_LINE_H) * hf)
            if shapes[sid] == "decision" or box_h[sid] <= float(look.get("max_aspect", 0.8)) * box_w[sid] or box_w[sid] >= widest:
                break
            box_w[sid] += 20
    return texts, box_w, box_h

def _step(page: Page, flow: dict, k: int, comps: dict, profile: Profile, where: tuple) -> float:
    """Draw one step box, centred in its lane, and its note below the lanes.

    Args:
        page: the page.
        flow: the flow.
        k: the step's index.
        comps: every component by id.
        profile: the kind colours.
        where: (lanes, lane tops, lane heights, step box heights, step texts, notes top, step shapes, column left edges, room for runs,
            step box widths).

    Returns:
        The note's height.
    """
    lanes, lane_y, lane_h, box_h, texts, notes_top, shapes, lefts, room, box_w = where
    w = box_w[flow["steps"][k]["id"]]
    fid, s = flow["id"], flow["steps"][k]
    x = lefts[k]
    li = lanes.index(s["actor"])
    h = box_h[s["id"]]
    r_top, r_bot = room.get((li, "top"), 0), room.get((li, "bottom"), 0)
    y = lane_y[li] + r_top + (lane_h[li] - r_top - r_bot - h) / 2   # centred in the lane, below the room kept for arrow runs
    gate = f"GATE: {s['gate']}" if s.get("gate") else ""
    tip = "\n".join(x for x in (
        "reads: " + "; ".join(s.get("reads", [])) if s.get("reads") else "",
        "writes: " + "; ".join(s.get("writes", [])) if s.get("writes") else "",
        "code: " + "; ".join(s.get("code", [])) if s.get("code") else "") if x)
    page.box(f"{fid}-s-{s['id']}", label(*texts[s["id"]]), x, y, w, h,
             comp_style(comps[s["actor"]]["kind"], profile, "fontSize=10;align=left;verticalAlign=top;spacingLeft=8;spacingRight=6;spacingTop=6;"
                        + ("strokeWidth=2;" if gate else "") + SHAPES[shapes[s["id"]]][0]), tooltip=tip,
             link=f"data:page/id,flow-{s['flow']}" if s.get("flow") else "", solid=True)   # an obstacle for the router and the audit
    note = note_lines(s, k + 1)
    if len(note) == 1 and profile.look.get("empty_notes", "hide") == "hide":   # nothing under the title: no note (operator review, 2026-10-21)
        return 0
    gap = col_gap(profile.look)
    chars = max(NOTE_CHARS, int(NOTE_CHARS * (w + gap - 4) / 266))   # NOTE_CHARS fits a 266 px note; a wider note takes more a line
    nh = 20 + sum(wrapped_lines(n.replace("`", ""), chars) for n in note) * NOTE_LINE_H
    page.box(f"{fid}-n-{s['id']}", label(*note), x - gap / 2 + 2, notes_top, w + gap - 4, nh,
             "shape=note;whiteSpace=wrap;html=1;size=10;fillColor=#fffbe6;strokeColor=#bf9000;align=left;verticalAlign=top;spacingLeft=6;spacingTop=4;fontSize=10;")
    return nh


def flow_page(flow: dict, comps: dict[str, dict], number: int, profile: Profile) -> Page:
    """One flow: a header, a lane per component (in order of first use), the steps left to right with numbered arrows, a note per step, and a
    legend of the shapes the page uses (flowmap.shapes).

    Args:
        flow: the flow from the map.
        comps: every component by id.
        number: the flow's position in the map, for the tab name.
        profile: the kind colours.

    Returns:
        The page.
    """
    fid, steps = flow["id"], flow["steps"]
    page = Page(f"flow-{fid}", f"{number}. {flow['title']}"[:60])
    shapes = {s["id"]: (step_shape(steps, k, comps, profile.kind_shapes, profile.io_vias) if profile.look["shapes"] else "process")
              for k, s in enumerate(steps)}
    texts, box_w, box_h = size_steps(steps, shapes, profile)
    width = LANE_HEAD_W + sum(box_w.values()) + len(steps) * col_gap(profile.look) + GAP
    header = flow_header_lines(flow, comps, number)
    head_w = max(width, 900)
    head_chars = int((head_w - 16) / 7)   # font 12: about 6.5 px a character, so 7 px is conservative
    head_h = 14 + sum(wrapped_lines(h.replace("*", ""), head_chars) for h in header) * HEAD_LINE_H
    page.box(f"{fid}-head", label(*header), MARGIN, MARGIN, head_w, head_h,
             "rounded=0;whiteSpace=wrap;html=1;fillColor=#fafafa;strokeColor=#666666;align=left;verticalAlign=top;spacingLeft=8;spacingTop=4;fontSize=12;",
             link="data:page/id,overview")
    top = MARGIN + head_h + GAP
    edges = step_edges(steps, fid)
    plan = plan_runs(steps, [(a, b) for _cid, a, b, text, _st in edges if "back to" not in text])
    tg = float(profile.look.get("track_gap", 12))
    room = {key: reserve(n, tg) for key, n in plan["count"].items()}
    lanes, lane_y, lane_h = draw_lanes(page, flow, comps, profile, top, box_h, box_w, room)
    order = {s["id"]: k for k, s in enumerate(steps)}
    widths = {order[a]: 18 + 9 * len(branch_label(next(s for s in steps if s["id"] == a), b, order[b] + 1, profile.look)[0])
              for _c, a, b, text, _st in edges if "back to" not in text and order[b] == order[a] + 1}
    gaps = label_gaps(col_gap(profile.look), widths, len(steps))
    lefts = column_lefts([box_w[s["id"]] for s in steps], gaps)
    notes_top = top + sum(lane_h) + GAP
    note_h = [_step(page, flow, k, comps, profile, (lanes, lane_y, lane_h, box_h, texts, notes_top, shapes, lefts, room, box_w)) for k in range(len(steps))]
    used = list(dict.fromkeys(list(shapes.values()) + [lane_shape(comps[c], profile.kind_shapes) for c in lanes]))
    shape_legend(page, used, MARGIN, notes_top + max(note_h + [0]) + GAP * 2, fid)
    band = notes_top - GAP / 2
    xs = [lefts[k] + box_w[steps[k]["id"]] + gaps[k] / 2 for k in range(len(steps) - 1)]
    ys = sorted({y for li in range(len(lanes)) for y in run_ys(li, lane_y, lane_h, plan["count"], tg)})
    for cid, src, dst, text, style in edges:   # back arrows first: forward routes and labels then avoid them
        if "back to" in text:
            band = back_arrow(page, (cid, f"{fid}-s-{src}", f"{fid}-s-{dst}", text, style), band, profile.look["back_arrows"])
    drawn, corridors, reserved = route_flow(page, (fid, steps, edges, shapes), {"xs": xs, "ys": ys}, profile.look)
    if profile.look.get("uncross", "on") != "off":   # redraw arrows that cross needlessly (operator review 2026-10-22)
        uncross(page, drawn, corridors, reserved)
    return page


def _slots(items: list) -> dict:
    """Spread arrows evenly along one side of a box.

    Args:
        items: the arrows sharing that side, in order.

    Returns:
        Each arrow's position on the side, between 0 and 1 exclusive.
    """
    return {item: round((i + 1) / (len(items) + 1), 3) for i, item in enumerate(items)}


def step_edges(steps: list[dict], fid: str) -> list[tuple[str, str, str, str, str]]:
    """The flow's arrows with ports that never coincide.

    A forward arrow leaves its step's right side and enters the target's left side; a step with several on one side spreads them over that
    side. A forward arrow that skips a column into another lane enters the target's bottom (lane above) or top (lane below) instead. An arrow back to an earlier step leaves and enters at the bottom, dashed and purple, labelled "back to N", so it never shares a
    path with a forward arrow.

    Args:
        steps: the flow's steps in order.
        fid: the flow id (edge ids are `<fid>-e-<source>-<target>`).

    Returns:
        (edge id, source step id, target step id, label, style) per arrow.
    """
    index = {s["id"]: k for k, s in enumerate(steps)}
    actors = list(dict.fromkeys(s.get("actor") for s in steps))   # lane order, as _lanes draws them
    lane = {s["id"]: actors.index(s.get("actor")) for s in steps}
    pairs = [(s["id"], tg) for k, s in enumerate(steps) for tg in step_targets(steps, k)]
    # A forward arrow that skips a column into another lane enters from below (lane above) or above (lane below), so it climbs in the target's
    # own column instead of crossing the steps in between (operator, 2026-10-21: an arrow 6 to 8 ran over step 7 in 8's lane).
    climb = [(a, b) for a, b in pairs if index[b] > index[a] + 1 and lane[b] != lane[a]]
    fwd = [(a, b) for a, b in pairs if index[b] > index[a] and (a, b) not in climb]
    back = [(a, b) for a, b in pairs if index[b] <= index[a]]
    out_r = {a: _slots([p for p in fwd if p[0] == a]) for a, _ in fwd}
    in_l = {b: _slots([p for p in fwd if p[1] == b]) for _, b in fwd}
    out_b = {a: _slots([p for p in back if p[0] == a]) for a, _ in back}
    in_b = {b: _slots([p for p in back if p[1] == b]) for _, b in back}
    out_r.update({a: _slots([p for p in fwd + climb if p[0] == a]) for a, _ in climb})
    in_v = {b: _slots([p for p in climb if p[1] == b]) for _, b in climb}
    edges = []
    for a, b in pairs:
        if (a, b) in climb:
            style = f"exitX=1;exitY={out_r[a][(a, b)]};entryX={in_v[b][(a, b)]};entryY={1 if lane[b] < lane[a] else 0};"
            text = str(index[b] + 1)
        elif (a, b) in fwd:
            style = f"exitX=1;exitY={out_r[a][(a, b)]};entryX=0;entryY={in_l[b][(a, b)]};"
            text = str(index[b] + 1)
        else:
            style = f"exitX={out_b[a][(a, b)]};exitY=1;entryX={in_b[b][(a, b)]};entryY=1;dashed=1;strokeColor=#6a3fa0;fontColor=#6a3fa0;"
            text = f"back to {index[b] + 1}"
        edges.append((f"{fid}-e-{a}-{b}", a, b, text, style))
    return edges


def render(data: dict, profile: Profile) -> str:
    """The whole draw.io file for a validated map.

    Args:
        data: the validated map.
        profile: the project's drawing profile.

    Returns:
        The file text: banner, then an uncompressed `<mxfile>` with the Overview, the End-to-end page, one page per flow, and the decision pages after the
        Overview when the map has an `options` block, `decision_pages` or `option_pages`.
    """
    comps = {c["id"]: c for c in data["components"]}
    pages = [overview_page(data, profile), end_to_end_page(data, profile)] + [flow_page(f, comps, i + 1, profile) for i, f in enumerate(data["flows"])]
    for k, (pid, name, block) in enumerate(option_blocks(data)):   # optional: decision pages go right after the Overview, in map order
        pages.insert(1 + k, options_page(data, profile, block, pid, name))
    return mxfile(pages, profile.host, banner(profile.generator, profile.map, profile.command, profile.check))


def evaluate(root: Path, profile: Profile) -> Outcome:
    """Validate the map and compare the rendered drawing with the file on disk (what a project's drift check calls).

    Args:
        root: the repository root.
        profile: the project's drawing profile.

    Returns:
        The outcome: problems, the rendered text, and whether the file on disk is stale.
    """
    data, problems = load(root, profile)
    if problems or data is None:
        return Outcome(problems=problems)
    text = render(data, profile)
    out = root / profile.output
    current = out.read_text(encoding="utf-8") if out.is_file() else None
    return Outcome(text=text, drift=current != text)


def flow_list(data: dict | None) -> list[str]:
    """One line per flow: id, trigger kind, where it runs, step count and title (for a `--list` option).

    Args:
        data: the loaded map, or None.

    Returns:
        The lines.
    """
    return [f"{f['id']:<28} {f['trigger']['kind']:<8} {f['runs_on']:<22} {len(f['steps']):>2} steps  {f['title']}" for f in (data or {}).get("flows", [])]


#: What marks a drawing as generated (drawio.mxfile.banner()); a file without it is a hand-made drawing and is never written over.
GENERATED_MARK = "<!-- GENERATED by "


def write_drawing(root: Path, profile: Profile, outcome: Outcome) -> Path:
    """Write a rendered drawing (the renderer's `--write` path; the caller has checked the outcome has no problems).

    A drawing a person edited by hand is source and is never regenerated over (references/data-first-diagrams.md): an existing file at the output
    path without the generated banner in its first lines is refused.

    Args:
        root: the repository root.
        profile: where the drawing goes.
        outcome: evaluate()'s result, with text.

    Returns:
        The file written.

    Raises:
        FileExistsError: the output path holds a drawing without the generated banner.
    """
    out = root / profile.output
    if out.is_file() and GENERATED_MARK not in out.read_text(encoding="utf-8", errors="replace")[:600]:
        raise FileExistsError(f"{profile.output} has no generated banner: it is a hand-made drawing and is never regenerated over; choose another output")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(outcome.text, encoding="utf-8")
    return out
