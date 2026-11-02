"""A regular flowchart page for a flow: top to bottom with no lanes, a terminator at each end, diamonds with labelled branches and a red stop box
beside a step that can fail. The flow pages show who does what and when; this page shows the logic. It reads the same map, so it needs no data
of its own, and `drawing.look.flowcharts` turns it on (a list of flow ids, `family:<id>` for a family joined into one chart, or "all"), and `drawing.look.swimlanes` draws the same chart in
vertical lanes, one per actor, and `drawing.look.bpmn` in BPMN symbols (flowmap.flowchart.bpmn).

A box shows a step's `label`, else its gate, else its action's first clause cut short; the whole step is the hover text. A box takes its actor's
colour and names the actor on a second line, which keeps what the lanes showed. flowmap.flowchart.graph places the nodes on a grid; this module
sizes them and routes every arrow with explicit waypoints: down a column, along a numbered track in the gap between two rows, and an arrow back
to an earlier step up a channel right of the columns. Tracks are spaced for the arrows' hops, so page_audit() reads the result like any page.

Imported, not run: `from flowmap.flowchart.page import chart_page` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.mxfile import ARROW_HEAD, BLANK, Page, header_height, label, wrapped_lines

from ..flow_geometry import BACK_MARK
from . import bpmn
from .labels import mark_size, place_labels
from .branches import expand_branches
from .graph import END, START, Graph, Grid, chart_graph, is_decision, lane_columns, lane_map, place, swap_branches
from .route import CHANNEL, TRACK, assign_tracks, exit_point, left_channels, plan_gaps
from ..model import GAP, MARGIN, comp_style, step_targets
from ..profile import Profile
from ..shapes import SHAPES, shape_legend
from ..tips import step_tip

#: Box width, characters a line at that width (font 11), line height, least box height and the widest a decision grows to.
BOX_W, BOX_CHARS, LINE_H, BOX_H, DECISION_MAX = 240, 34, 15, 56, 440
#: A swimlane's heading height, and the space after its gutter.
LANE_HEAD, GUTTER_GAP = 30, 16
TABS = {"chart": "Chart", "lanes": "Lanes", "bpmn": "BPMN"}
#: Space between columns; in a gap between rows, the room under a box for a label and the room above a box for an arrowhead.
COL_GAP, LABEL_ROOM, HEAD_ROOM = 70, 24, 30
#: Where a step with no `label` is cut, in characters.
CUT = 64
JUMP = 6
EDGE = "edgeStyle=none;rounded=1;html=1;" + ARROW_HEAD + f"jumpStyle=arc;jumpSize={JUMP};"
COLOURS = {"Yes": "#1b7a3a", "No": "#b3261e", "": "#333333"}
BACK = EDGE + "dashed=1;strokeColor=#6a3fa0;"
STOP_EDGE = EDGE + "dashed=1;strokeColor=#b3261e;"
STOP_BOX = ("rounded=1;absoluteArcSize=1;arcSize=30;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=10;align=left;"
            "verticalAlign=middle;spacingLeft=10;spacingRight=8;")
END_BOX = ("rounded=1;absoluteArcSize=1;arcSize=30;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#333333;strokeWidth=2;fontSize=11;"
           "fontStyle=1;spacingLeft=10;spacingRight=10;")
LABEL_MARK = "text;html=1;align=center;verticalAlign=middle;fontSize=10;labelBackgroundColor=#ffffff;"


def short_text(step: dict) -> str:
    """A box's words: the `label`, else a gate's question, else the action cut at a word.

    Args:
        step: the step from the map.

    Returns:
        The text.
    """
    text = step.get("label") or step.get("gate") or step["action"].split("; ")[0].split(". ")[0]
    return text if len(text) <= CUT else text[:CUT].rsplit(" ", 1)[0] + " ..."


def step_chart_shape(step: dict, targets: list[str]) -> str:
    """A step's symbol on the chart: its own, else a decision, else a predefined process when it runs a flow, else a process.

    Args:
        step: the step from the map.
        targets: where it leads.

    Returns:
        A flowmap.shapes key.
    """
    if is_decision(step, targets):
        return "decision"
    return step.get("shape") or ("predefined-process" if step.get("flow") else "process")


def _size(lines: list[str], shape: str) -> tuple[int, int]:
    """A box's size for its text; a diamond widens until it is no taller than 0.6 of its width.

    Args:
        lines: the label lines.
        shape: the flowmap.shapes key.

    Returns:
        (width, height).
    """
    _style, wf, hf = SHAPES[shape][:3]
    w = BOX_W
    while True:
        chars = int(BOX_CHARS * w / BOX_W * wf)
        h = round(max(BOX_H, 16 + sum(wrapped_lines(x.replace("*", ""), chars) for x in lines) * LINE_H) * hf)
        if shape != "decision" or h <= 0.6 * w or w >= DECISION_MAX:
            return w, h
        w += 20


def _branch(graph: Graph, edge: object, targets: list[str]) -> str:
    """The words on an arrow: a step's `when` for that target, else Yes and No out of a decision.

    Args:
        graph: the graph.
        edge: the arrow.
        targets: where its source leads.

    Returns:
        The label, "" for none.
    """
    step = graph.steps.get(edge.src)
    if step is None:
        return ""
    if edge.dst in step.get("when", {}):
        return step["when"][edge.dst]
    if not is_decision(step, targets) or len(targets) > 2:
        return ""
    return "Yes" if edge.index == 0 else "No"


class Chart:
    """One flowchart being laid out: node sizes, then ports and tracks, then the drawing."""

    def __init__(self, flow: dict, comps: dict, profile: Profile, page_ids: tuple, mode: str = "chart") -> None:
        """Build the graph and grid and size every node.

        Args:
            flow: the flow (a stitched one for a family).
            comps: every component by id.
            profile: the drawing profile.
            page_ids: (ids of drawn chart pages, ids of drawn flow pages), for a step that runs another flow.
            mode: "chart", "lanes" (one column per actor) or "bpmn" (lanes in BPMN symbols).
        """
        flow = expand_branches(flow)
        self.flow, self.comps, self.profile, self.page_ids = flow, comps, profile, page_ids
        self.graph = chart_graph(flow)
        self.lanes, self.actors, self.first_col, self.bpmn = None, [], [], mode == "bpmn"
        if mode != "chart":
            self.lanes, self.actors = lane_map(self.graph)
            self.first_col = lane_columns(len(self.actors))
        self.grid: Grid = place(self.graph, self.lanes, self.first_col or None)
        self.targets = {s["id"]: step_targets(flow["steps"], k) for k, s in enumerate(flow["steps"])}
        self.shapes = {sid: step_chart_shape(s, self.targets[sid]) for sid, s in self.graph.steps.items()}
        self.labels = {(e.src, e.dst): _branch(self.graph, e, self.targets.get(e.src, [])) for e in self.graph.edges}
        swap_branches(self.graph, self.grid)
        self.left = {} if self.lanes else left_channels(self.graph, self.grid)
        self.text, self.size = {}, {}
        for nid in self.graph.order:
            self.text[nid] = self._lines(nid)
            shape = self.shapes.get(nid, "process" if nid in self.graph.stops else "terminator")
            self.size[nid] = _size(self.text[nid], shape)
            if self.bpmn and nid not in self.graph.steps:
                self.size[nid] = (BOX_W, max(bpmn.EVENT, self.size[nid][1] * 2 if nid in self.graph.stops else 0))
        self._columns()

    def _lines(self, nid: str) -> list[str]:
        """A node's label lines.

        Args:
            nid: the node id.

        Returns:
            The lines for drawio.mxfile.label().
        """
        if nid == START:
            return [f"**Start: {self.flow['title']}**"]
        if nid == END:
            return ["**End**"]
        if nid in self.graph.stops:
            return ["**Stop**"] + self.graph.steps[self.graph.stops[nid]]["failures"]
        s = self.graph.steps[nid]
        return [short_text(s)] if self.lanes else [short_text(s), f"*{self.comps[s['actor']]['name']}*"]

    def _columns(self) -> None:
        """Each column's centre, and the channels right of the last one.

        Labelled side exits widen the column gap to fit their words.
        """
        side = [self.grid.cols[e.src] + 1 for e in self.graph.edges if e.kind == "stop" or e.index == 1]
        last = max(list(self.grid.cols.values()) + side + [c for cells in self.grid.chains.values() for _r, c in cells] + [c - 1 for c in self.first_col])
        widths = {c: 0 for c in range(last + 1)}
        for nid, c in self.grid.cols.items():
            widths[c] = max(widths[c], self.size[nid][0])
        gap = max([COL_GAP] + [mark_size(t)[0] + 40 for t in self.labels.values() if t])
        words = [mark_size(self.labels[key])[0] for key in self.left if self.labels[key]]
        self.left_x = MARGIN + len(set(self.left.values())) * CHANNEL if self.left else MARGIN   # the channels, then room for a label on the way out
        self.cx, self.col_left, x = {}, {}, self.left_x + (max(words + [0]) + 28 if self.left else 0)
        for c in range(last + 1):
            w = widths[c] or 40
            self.col_left[c], self.cx[c] = x - (GUTTER_GAP / 2 if self.lanes else gap / 2), x + w / 2
            x += w + (GUTTER_GAP if self.lanes and c % 2 else gap)
        self.channel_x, self.lane_end = x, x - gap / 2

    def port_in(self, dst: str, incoming: list) -> dict:
        """Entry x per arrow into a node: a diamond or terminator takes every arrow at its centre top, a box spreads them, left to right as they arrive.

        Args:
            dst: the node.
            incoming: [(src, arrival x)].

        Returns:
            {src: x}.
        """
        cx, w = self.cx[self.grid.cols[dst]], self.size[dst][0]
        if len(incoming) < 2 or self.shapes.get(dst, "terminator") in ("decision", "terminator"):
            return {src: cx for src, _ in incoming}
        ordered = sorted(incoming, key=lambda item: item[1])
        return {src: cx - w * 0.3 + w * 0.6 * i / (len(ordered) - 1) for i, (src, _) in enumerate(ordered)}


def _rows(chart: Chart, tracks: dict, top: float) -> dict:
    """Each row's top and height, and each gap's first track.

    Args:
        chart: the chart.
        tracks: assign_tracks()'s result.
        top: the first row's top.

    Returns:
        {"top": {row: y}, "h": {row: height}, "track": {gap row: y}}.
    """
    rows = chart.grid.rows
    last = max(rows.values())
    tops, heights, track_y, y = {}, {}, {}, top
    for r in range(last + 1):
        heights[r] = max((chart.size[n][1] for n in chart.graph.order if rows[n] == r), default=BOX_H)   # a lane can leave a row to long arrows alone
        tops[r] = y
        track_y[r] = y + heights[r] + LABEL_ROOM
        y += heights[r] + LABEL_ROOM + max(tracks["count"].get(r, 1) - 1, 0) * TRACK + HEAD_ROOM
    return {"top": tops, "h": heights, "track": track_y, "bottom": y}


def _node_rect(chart: Chart, ys: dict, nid: str) -> tuple[float, float, float, float]:
    """A node's box, centred on its cell.

    Args:
        chart: the chart.
        ys: _rows()'s result.
        nid: the node id.

    Returns:
        (x, y, width, height).
    """
    r, (w, h) = chart.grid.rows[nid], chart.size[nid]
    return chart.cx[chart.grid.cols[nid]] - w / 2, ys["top"][r] + (ys["h"][r] - h) / 2, w, h


def draw_nodes(page: Page, chart: Chart, ys: dict) -> list[str]:
    """Draw every node.

    Args:
        page: the page.
        chart: the chart.
        ys: _rows()'s result.

    Returns:
        The shapes used, for the legend.
    """
    fid, used = chart.flow["id"], []
    for n, nid in enumerate(chart.graph.order):
        x, y, w, h = _node_rect(chart, ys, nid)
        text = label(*chart.text[nid])
        if chart.bpmn and nid not in chart.graph.steps:
            kind = "error" if nid in chart.graph.stops else "start" if nid == START else "end"
            bpmn.event(page, f"{fid}-c-{nid}", kind, (x, y, w, h), chart.text[nid])
        elif nid in chart.graph.stops:
            page.box(f"{fid}-c-{nid}", text, x, y, w, h, STOP_BOX, solid=True)
        elif nid in (START, END):
            page.box(f"{fid}-c-{nid}", text, x, y, w, h, END_BOX, solid=True)
            used.append("terminator")
        else:
            s, shape = chart.graph.steps[nid], chart.shapes[nid]
            actor = chart.comps[s["actor"]]
            style = bpmn.step_style(shape) if chart.bpmn else comp_style(actor["kind"], chart.profile, "fontSize=11;" + SHAPES[shape][0])
            charts, flows = chart.page_ids
            link = f"data:page/id,chart-{s['flow']}" if s.get("flow") in charts else f"data:page/id,flow-{s['flow']}" if s.get("flow") in flows else ""
            page.box(f"{fid}-c-{nid}", text, x, y, w, h, style, link=link, tooltip=step_tip(s, str(n), actor["name"]), solid=True)
            used.append(shape)
    return used


def _edge_points(chart: Chart, ys: dict, e: object, route: tuple) -> list:
    """An arrow's polyline.

    Args:
        chart: the chart.
        ys: _rows()'s result.
        e: the arrow.
        route: (legs, entries, tracks).

    Returns:
        The points.
    """
    legs, entries, tracks = route
    key = (e.src, e.dst)
    sx, sy, sw, sh = _node_rect(chart, ys, e.src)
    if e.kind == "main" and chart.grid.rows[e.src] == chart.grid.rows[e.dst]:   # a hand-off level with its source runs sideways
        return [(sx + sw, sy + sh / 2), (_node_rect(chart, ys, e.dst)[0], sy + sh / 2)]
    if key in chart.left:
        tx, ty, _tw, th = _node_rect(chart, ys, e.dst)
        lane = chart.left_x - CHANNEL * chart.left[key]
        return [(sx, sy + sh / 2), (lane, sy + sh / 2), (lane, ty + th / 2), (tx, ty + th / 2)]
    side, x = exit_point(chart, e)
    mid = sy + sh / 2
    if e.kind == "stop" and chart.lanes:
        _dx, dy, _dw, dh = _node_rect(chart, ys, e.dst)
        return [(x, sy + sh), (x, dy + dh / 2 - bpmn.EVENT / 2 if chart.bpmn else dy)]   # a BPMN stop is a circle centred in its cell
    if e.kind == "stop":
        return [(sx + sw, mid), (_node_rect(chart, ys, e.dst)[0], mid)]
    pts = [(sx + sw, mid), (x, mid)] if side else [(x, sy + sh)]
    for gap, a, b in legs[key]:
        y = ys["track"][gap] + tracks[(key, gap, a)] * TRACK
        pts += [(a, y), (b, y)]
    return pts + [(entries[key], _node_rect(chart, ys, e.dst)[1])]


def draw_edges(page: Page, chart: Chart, ys: dict, route: tuple) -> None:
    """Draw every arrow and its label.

    Args:
        page: the page.
        chart: the chart.
        ys: _rows()'s result.
        route: (legs, entries, tracks).
    """
    fid, items = chart.flow["id"], []
    for e in chart.graph.edges:
        words = chart.labels[(e.src, e.dst)]
        pts = _edge_points(chart, ys, e, route)
        cid = f"{fid}-ce-{e.src}-{e.dst}"
        colour = COLOURS.get(words, COLOURS[""])
        style = BACK if e.kind == "back" else STOP_EDGE if e.kind == "stop" else EDGE + f"strokeColor={colour};"
        style = EDGE + "strokeColor=#000000;" if chart.bpmn else style   # BPMN: every arrow in a pool is a sequence flow
        page.route(cid, f"{fid}-c-{e.src}", f"{fid}-c-{e.dst}", pts, style, "thin", jump=JUMP)
        if e.kind == "back" and not words:
            words = "back"
        if words or e.kind == "stop":
            base = BACK_MARK if e.kind == "back" else LABEL_MARK
            items.append((cid, words or "fails", pts, base + f"fontColor={COLOURS['No'] if e.kind == 'stop' else colour};", e.index > 1))
    place_labels(page, items)


def draw_lanes(page: Page, chart: Chart, ys: dict) -> None:
    """The vertical swimlanes behind the chart: a band per actor, its name at the top, shaded by turns; the last band also holds the arrows back.

    Args:
        page: the page.
        chart: the chart.
        ys: _rows()'s result.
    """
    fid = chart.flow["id"]
    top, bottom = ys["top"][0] - LANE_HEAD - 8, ys["bottom"]
    ends = [chart.col_left[c] for c in chart.first_col[1:-1]] + [chart.channel_x + CHANNEL * len(chart.channels)]
    for k, actor in enumerate(chart.actors):
        left, right = chart.col_left[chart.first_col[k]], ends[k]
        fill, line = ("#ffffff", "#000000") if chart.bpmn else ("#eef2f6" if k % 2 == 0 else "#f8fafc", "none")
        page.box(f"{fid}-lane-{k}", "", left, top, right - left, bottom - top, f"rounded=0;html=1;fillColor={fill};strokeColor={line};")
        page.box(f"{fid}-lane-head-{k}", label(f"**{chart.comps[actor]['name']}**"), left, top, right - left, LANE_HEAD,
                 f"rounded=0;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={line};fontSize=12;fontColor=#1f3a5f;")


def chart_page(flow: dict, comps: dict, profile: Profile, page_ids: tuple, mode: str = "chart") -> Page:
    """One flowchart page: a header with the purpose and trigger, the chart (in vertical swimlanes when asked), and a legend of its symbols.

    Args:
        flow: the flow (a stitched one for a family).
        comps: every component by id.
        profile: the drawing profile.
        page_ids: (drawn chart page ids, drawn flow page ids).
        mode: "chart", "lanes" or "bpmn".

    Returns:
        The page.
    """
    fid, swimlanes = f"{mode}-{flow['id']}", mode != "chart"   # the mode in every cell id: one flow may be drawn in all three
    chart = Chart({**flow, "id": fid}, comps, profile, page_ids, mode)
    page = Page(fid, f"{TABS[mode]}: {flow['title']}"[:60])
    head = [f"**{flow['title']}** ({TABS[mode].lower()})", BLANK, flow["purpose"], BLANK, f"**Trigger:** {flow['trigger']['kind']}: {flow['trigger']['detail']}",
            BLANK, "[back to Overview]"]
    legs, entries = plan_gaps(chart)
    tracks = assign_tracks(legs)
    width = max(900.0, chart.channel_x + CHANNEL * len(chart.channels) - MARGIN)
    head_h = header_height(head, width, 80)
    page.box(f"{fid}-chart-head", label(*head), MARGIN, MARGIN, width, head_h,
             "rounded=0;whiteSpace=wrap;html=1;fillColor=#fafafa;strokeColor=#666666;align=left;verticalAlign=top;spacingLeft=8;spacingTop=4;fontSize=12;",
             link="data:page/id,overview")
    ys = _rows(chart, tracks, MARGIN + head_h + GAP + (LANE_HEAD + 8 if swimlanes else 0))
    if swimlanes:
        draw_lanes(page, chart, ys)
    used = draw_nodes(page, chart, ys)
    draw_edges(page, chart, ys, (legs, entries, tracks))
    if chart.bpmn:
        bpmn.legend(page, MARGIN, ys["bottom"] + GAP, f"{fid}-chart")
    else:
        shape_legend(page, list(dict.fromkeys(used)), MARGIN, ys["bottom"] + GAP, f"{fid}-chart")
    return page
