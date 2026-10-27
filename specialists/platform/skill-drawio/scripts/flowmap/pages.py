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
from .e2e_family import family_pages
from .model import GAP, MARGIN, Outcome, comp_style, load, status_style, status_text
from .map_parts import flow_labels, paged_flows
from .model import option_blocks
from .options import options_page
from .fold import fold_rows, folded_page
from .flow_geometry import LANE_HEAD_W, back_arrow, step_edges, col_gap, column_lefts, label_gaps, label_widths, plan_runs, reserve, run_ys, step_width
from .lanes import draw_lanes
from .routing import route_flow
from .uncross import uncross, unshare
from .shapes import FIT, PERSON_ICON, SHAPES, SLANTED, fit_height, lane_shape, shape_legend, step_shape
from .overview import overview_page
from .profile import Profile
from .tips import flow_arrow_tip, step_tags, step_tip

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


def size_steps(steps: list[dict], shapes: dict, profile: Profile) -> tuple[dict, dict, dict]:
    """Each step's text, width and height. A box is as tall as its text needs; when that would make it taller than `look.max_aspect` times its
    width (`look.decision_aspect` for a decision), it is widened (in 20 px steps, up to `look.decision_width`) so long text makes a wider box,
    not a tall narrow one (operator review 2026-10-21: a tall terminator squeezed its text against its curved ends), and short text a small
    diamond (2026-10-27).

    Args:
        steps: the flow's steps.
        shapes: each step's shape.
        profile: the drawing profile.

    Returns:
        (texts, widths, heights), each by step id.
    """
    look = profile.look
    texts = {s["id"]: step_lines(s, k + 1, look["action_bullets"], look["heading_scale"]) for k, s in enumerate(steps)}
    # A decision starts at the step width and widens only until its diamond is no taller than `look.decision_aspect` times its width, up to
    # `look.decision_width`: a fixed 380 px made "Overlay SMC?" a long flat sliver (operator review 2026-10-27, smc_change Apply page).
    box_w = {sid: step_width("process" if sh == "decision" else sh, look) for sid, sh in shapes.items()}
    box_h = {}
    widest = max(int(look.get("decision_width", 380)), max(box_w.values(), default=0))
    # A long decision may pass decision_width up to decision_max_width, so it stays a diamond and not a tall kite (operator review 2026-10-27,
    # smc_change Resume: "disproportionately elongated vertically").
    widest_decision = max(widest, int(look.get("decision_max_width", 560)))
    for sid, lines in texts.items():   # the outline eats into the text area: fewer characters a line, a taller box
        _style, wf, hf = SHAPES[shapes[sid]][:3]
        decision = shapes[sid] == "decision"
        aspect = float(look.get("decision_aspect", 0.6) if decision else look.get("max_aspect", 0.8))
        while True:
            chars = int(look["step_chars"] * box_w[sid] / look["step_width"] * wf)
            box_h[sid] = round(max(STEP_H, 20 + sum(wrapped_lines(x.replace("*", ""), chars) for x in lines) * STEP_LINE_H) * hf)
            if box_h[sid] <= aspect * box_w[sid] or box_w[sid] >= (widest_decision if decision else widest):
                break
            box_w[sid] += 20
    return texts, box_w, box_h

def _step(page: Page, flow: dict, k: int, comps: dict, profile: Profile, where: tuple, number: int | str = 1) -> float:
    """Draw one step box, centred in its lane, and its note below the lanes.

    Args:
        page: the page.
        flow: the flow.
        k: the step's index.
        comps: every component by id.
        profile: the kind colours.
        where: (lanes, lane tops, lane heights, step box heights, step texts, notes top, step shapes, column left edges, room for runs,
            step box widths).
        number: the flow's number or label, for the x.y in the step's hover text.

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
    tip = step_tip(s, f"{number}.{k + 1}", comps[s["actor"]]["name"])
    page.box(f"{fid}-s-{s['id']}", label(*texts[s["id"]]), x, y, w, h,
             comp_style(comps[s["actor"]]["kind"], profile, "fontSize=10;align=left;verticalAlign=top;spacingLeft=8;spacingRight=6;spacingTop=6;"
                        + ("strokeWidth=2;" if gate else "") + SHAPES[shapes[s["id"]]][0]), tooltip=tip, tags=step_tags(s, shapes[s["id"]]),
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
    page.box(f"{flow['id']}-head", label(*header), MARGIN, MARGIN, head_w, head_h,
             "rounded=0;whiteSpace=wrap;html=1;fillColor=#fafafa;strokeColor=#666666;align=left;verticalAlign=top;spacingLeft=8;spacingTop=4;fontSize=12;",
             link="data:page/id,overview")
    return head_h


def flow_page(flow: dict, comps: dict[str, dict], number: int | str, profile: Profile) -> Page:
    """One flow: a header, a lane per component (in order of first use), the steps left to right with numbered arrows, a note per step, and a
    legend of the shapes the page uses (flowmap.shapes).

    Args:
        flow: the flow from the map.
        comps: every component by id.
        number: the flow's number or label (flowmap.map_parts.flow_labels), for the tab name unless the flow sets `tab`.
        profile: the kind colours.

    Returns:
        The page.
    """
    fid, steps = flow["id"], flow["steps"]
    page = Page(f"flow-{fid}", (flow.get("tab") or f"{number}. {flow['title']}")[:60])   # `tab` names it outright (operator, 2026-10-26)
    shapes = {s["id"]: (step_shape(steps, k, comps, profile.kind_shapes, profile.io_vias) if profile.look["shapes"] else "process")
              for k, s in enumerate(steps)}
    texts, box_w, box_h = size_steps(steps, shapes, profile)
    edges = step_edges(steps, fid)
    order = {s["id"]: k for k, s in enumerate(steps)}
    by_id = {s["id"]: s for s in steps}
    for cid, a, b, text, _st in edges:   # hover text and tags on each arrow and its number: where it goes and what the step there does
        back = "back to" in text
        page.tags[cid] = ("back-arrow",) if back else ("step-arrow",)
        page.tips[cid] = flow_arrow_tip(number, (order[a], by_id[a]), (order[b], by_id[b]), comps[by_id[b]["actor"]]["name"], back)
    widths = label_widths(steps, edges, profile.look)
    rows = fold_rows(flow, profile.look)
    if len(rows) > 1:   # a long flow drawn in rows (`drawing.look.fold`; operator, 2026-10-27)
        return folded_page(page, (flow, comps, number, profile), (shapes, texts, box_w, box_h, edges, widths), (rows, _step, flow_header))
    gaps = label_gaps(col_gap(profile.look), widths, len(steps))
    # Lanes and header span the label-widened gaps, so a long branch label never pushes the last step past the lanes (operator, 2026-10-23).
    width = LANE_HEAD_W + sum(box_w.values()) + sum(gaps) + GAP
    top = MARGIN + flow_header(page, flow, comps, number, width) + GAP
    plan = plan_runs(steps, [(a, b) for _cid, a, b, text, _st in edges if "back to" not in text])
    tg = float(profile.look.get("track_gap", 12))
    room = {key: reserve(n, tg) for key, n in plan["count"].items()}
    lanes, lane_y, lane_h = draw_lanes(page, flow, comps, profile, top, box_h, box_w, room, width)
    lefts = column_lefts([box_w[s["id"]] for s in steps], gaps)
    notes_top = top + sum(lane_h) + GAP
    note_h = [_step(page, flow, k, comps, profile, (lanes, lane_y, lane_h, box_h, texts, notes_top, shapes, lefts, room, box_w), number) for k in range(len(steps))]
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
    if profile.look.get("unshare", "on") != "off":   # part two arrows merged at one decision corner (operator review 2026-10-27)
        unshare(page, drawn, corridors, reserved)
    return page


def render(data: dict, profile: Profile) -> str:
    """The whole draw.io file for a validated map.

    Args:
        data: the validated map.
        profile: the project's drawing profile.

    Returns:
        The file text: banner, then an uncompressed `<mxfile>` with the Overview, the End-to-end page (then one per family when
        `look.e2e_family_pages` is on), one page per flow, and the decision pages after the
        Overview when the map has an `options` block, `decision_pages` or `option_pages`.
    """
    comps, labels = {c["id"]: c for c in data["components"]}, flow_labels(data, profile)
    pages = ([overview_page(data, profile), end_to_end_page(data, profile)] + family_pages(data, profile)   # family pages only with look.e2e_family_pages
             + [flow_page(f, comps, labels[f["id"]], profile) for f in paged_flows(data, profile)])
    for k, (pid, name, block) in enumerate(option_blocks(data)):   # optional: decision pages go right after the Overview, in map order
        pages.insert(1 + k, options_page(data, profile, block, pid, name))
    for page in pages:   # the background layer locked on every page: nothing on it moves by accident (operator, 2026-10-26)
        page.base_locked = bool(profile.look.get("lock_base_layer"))
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
    # The banner is an XML comment, where "--" is illegal: draw.io then refuses the whole file ("Export failed").
    problems += [f"drawing.{k}: {v!r} contains '--', which an XML comment cannot hold; name a recipe (just ...) instead"
                 for k, v in (("command", profile.command), ("check", profile.check)) if "--" in v]
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
