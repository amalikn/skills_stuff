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
from .flow_geometry import COL_W, LANE_HEAD_W, STEP_W, back_arrow, column_lefts, skip_arrow, step_width
from .shapes import FIT, PERSON_ICON, SHAPES, SLANTED, lane_shape, shape_legend, step_shape
from .overview import overview_page
from .profile import Profile

#: Flow page geometry: lane heading width, least lane height, step column width, step box width and least height.
LANE_H, STEP_H = 120, 92
#: Note text budget (characters per line) and line height.
NOTE_CHARS, NOTE_LINE_H = 44, 15
#: Step box text budget (200 px at font size 10) and line height.
STEP_LINE_H = 13   # the characters a line a step box is sized for are drawing.look.step_chars
#: A flow page header's line height (font 12).
HEAD_LINE_H = 15
#: A step note's sections, in reading order: (step key, heading, whether its items are code).
NOTE_SECTIONS = (("reads", "Reads", False), ("writes", "Writes", False), ("code", "Code", True), ("failures", "Fails", False), ("look", "Look", False))


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
    clauses = [c.strip() for c in step["action"].split("; ") if c.strip()]
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


def _lanes(page: Page, flow: dict, comps: dict, profile: Profile, top: float, box_h: dict, box_w: dict) -> tuple[list, list, list]:
    """Draw one lane per component, in order of first use; each lane as tall as its tallest step.

    Args:
        page: the page.
        flow: the flow.
        comps: every component by id.
        profile: the kind colours.
        top: the first lane's top.
        box_h: each step box's height.
        box_w: each step box's width.

    Returns:
        (lane component ids, lane tops, lane heights).
    """
    fid, steps = flow["id"], flow["steps"]
    lanes: list[str] = []
    for s in steps:
        if s["actor"] not in lanes:
            lanes.append(s["actor"])
    width = LANE_HEAD_W + sum(box_w.values()) + len(steps) * (COL_W - STEP_W) + GAP
    lane_h = [max([LANE_H] + [box_h[s["id"]] + 28 for s in steps if s["actor"] == cid]) for cid in lanes]
    lane_y = [top + sum(lane_h[:li]) for li in range(len(lanes))]
    for li, cid in enumerate(lanes):
        c = comps[cid]
        fill, stroke = profile.style(c["kind"])
        page.box(f"{fid}-lane-{li}", "", MARGIN, lane_y[li], width, lane_h[li], f"rounded=0;html=1;fillColor={fill};strokeColor={stroke};opacity=35;")
        shape = lane_shape(c, profile.kind_shapes)
        page.box(f"{fid}-lanehead-{li}", label(f"**{c['name']}**", c["kind"], c["host"]), MARGIN, lane_y[li], LANE_HEAD_W, lane_h[li],
                 comp_style(c["kind"], profile, "rounded=0;align=left;spacingLeft=6;" + status_style(c) + SHAPES[shape][0] + FIT.get(shape, ("",))[0]
                            + ("spacingRight=40;" if shape == "person" else "")), tooltip=f"health: {c['health']}")
        if shape == "person":   # a figure in the lane head's top right corner
            page.box(f"{fid}-lanehead-{li}-icon", "", MARGIN + LANE_HEAD_W - 34, lane_y[li] + 8, 22, 40, PERSON_ICON)
    return lanes, lane_y, lane_h


def _step(page: Page, flow: dict, k: int, comps: dict, profile: Profile, where: tuple) -> float:
    """Draw one step box, centred in its lane, and its note below the lanes.

    Args:
        page: the page.
        flow: the flow.
        k: the step's index.
        comps: every component by id.
        profile: the kind colours.
        where: (lanes, lane tops, lane heights, step box heights, step texts, notes top, step shapes, column left edges).

    Returns:
        The note's height.
    """
    lanes, lane_y, lane_h, box_h, texts, notes_top, shapes, lefts = where
    w = step_width(shapes[flow["steps"][k]["id"]], profile.look)
    fid, s = flow["id"], flow["steps"][k]
    x = lefts[k]
    li = lanes.index(s["actor"])
    h = box_h[s["id"]]
    y = lane_y[li] + (lane_h[li] - h) / 2
    gate = f"GATE: {s['gate']}" if s.get("gate") else ""
    tip = "\n".join(x for x in (
        "reads: " + "; ".join(s.get("reads", [])) if s.get("reads") else "",
        "writes: " + "; ".join(s.get("writes", [])) if s.get("writes") else "",
        "code: " + "; ".join(s.get("code", [])) if s.get("code") else "") if x)
    page.box(f"{fid}-s-{s['id']}", label(*texts[s["id"]]), x, y, w, h,
             comp_style(comps[s["actor"]]["kind"], profile, "fontSize=10;align=left;verticalAlign=top;spacingLeft=8;spacingRight=6;spacingTop=6;"
                        + ("strokeWidth=2;" if gate else "") + SHAPES[shapes[s["id"]]][0]), tooltip=tip,
             link=f"data:page/id,flow-{s['flow']}" if s.get("flow") else "")
    note = note_lines(s, k + 1)
    nh = 20 + sum(wrapped_lines(n.replace("`", ""), NOTE_CHARS) for n in note) * NOTE_LINE_H
    page.box(f"{fid}-n-{s['id']}", label(*note), x - (COL_W - STEP_W) / 2 + 2, notes_top, w + (COL_W - STEP_W) - 4, nh,
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
    box_w = {sid: step_width(sh, profile.look) for sid, sh in shapes.items()}
    width = LANE_HEAD_W + sum(box_w.values()) + len(steps) * (COL_W - STEP_W) + GAP
    header = flow_header_lines(flow, comps, number)
    head_w = max(width, 900)
    head_chars = int((head_w - 16) / 7)   # font 12: about 6.5 px a character, so 7 px is conservative
    head_h = 14 + sum(wrapped_lines(h.replace("*", ""), head_chars) for h in header) * HEAD_LINE_H
    page.box(f"{fid}-head", label(*header), MARGIN, MARGIN, head_w, head_h,
             "rounded=0;whiteSpace=wrap;html=1;fillColor=#fafafa;strokeColor=#666666;align=left;verticalAlign=top;spacingLeft=8;spacingTop=4;fontSize=12;",
             link="data:page/id,overview")
    top = MARGIN + head_h + GAP
    # Each step box is as tall as its text needs, and each lane as tall as its tallest step.
    texts = {s["id"]: step_lines(s, k + 1, profile.look["action_bullets"], profile.look["heading_scale"]) for k, s in enumerate(steps)}
    box_h = {}
    for sid, lines in texts.items():   # the outline eats into the text area: fewer characters a line, a taller box
        _style, wf, hf = SHAPES[shapes[sid]][:3]
        chars = int(profile.look["step_chars"] * box_w[sid] / profile.look["step_width"] * wf)
        box_h[sid] = round(max(STEP_H, 20 + sum(wrapped_lines(x.replace("*", ""), chars) for x in lines) * STEP_LINE_H) * hf)
    lanes, lane_y, lane_h = _lanes(page, flow, comps, profile, top, box_h, box_w)
    lefts = column_lefts([box_w[s["id"]] for s in steps])
    notes_top = top + sum(lane_h) + GAP
    note_h = [_step(page, flow, k, comps, profile, (lanes, lane_y, lane_h, box_h, texts, notes_top, shapes, lefts)) for k in range(len(steps))]
    used = list(dict.fromkeys(list(shapes.values()) + [lane_shape(comps[c], profile.kind_shapes) for c in lanes]))
    shape_legend(page, used, MARGIN, notes_top + max(note_h) + GAP * 2, fid)
    band = notes_top - GAP / 2
    order = {s["id"]: k for k, s in enumerate(steps)}
    runs: dict = {}   # engine-routed arrows per lane edge, so each takes its own run
    lane_box = {s["id"]: (lane_y[lanes.index(s["actor"])], lane_h[lanes.index(s["actor"])]) for s in steps}
    for cid, src, dst, text, style in step_edges(steps, fid):
        pin = ("exitPerimeter=0;" if shapes[src] in SLANTED else "") + ("entryPerimeter=0;" if shapes[dst] in SLANTED else "")
        if "back to" in text:
            band = back_arrow(page, (cid, f"{fid}-s-{src}", f"{fid}-s-{dst}", text, style), band, profile.look["back_arrows"])
            continue
        skips = order[dst] > order[src] + 1   # a column or more in between: routed by the engine so it never crosses a step
        track = runs.get(lane_box[dst], 0)
        drawn = skips and skip_arrow(page, (cid, f"{fid}-s-{src}", f"{fid}-s-{dst}", text, style), (lane_box[src], lane_box[dst]),
                                     COL_W - STEP_W, track)
        runs[lane_box[dst]] = track + (1 if drawn else 0)
        if not drawn:
            page.edge(cid, f"{fid}-s-{src}", f"{fid}-s-{dst}", label=text, style=style + pin)
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
        The file text: banner, then an uncompressed `<mxfile>` with the Overview, the End-to-end page, one page per flow, and the option pages after the
        Overview when the map has an `options` block or `option_pages`.
    """
    comps = {c["id"]: c for c in data["components"]}
    pages = [overview_page(data, profile), end_to_end_page(data, profile)] + [flow_page(f, comps, i + 1, profile) for i, f in enumerate(data["flows"])]
    for k, (pid, name, block) in enumerate(option_blocks(data)):   # optional: option pages go right after the Overview, in map order
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
