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

from . import bpmn
from .lanes import LANE_HEAD, View, draw_lanes
from .labels import mark_size, place_labels
from .branches import expand_branches
from .graph import END, START, Graph, Grid, chart_graph, is_decision, lane_columns, lane_map, place, swap_branches
from .order import improve_branches, improve_tracks
from .route import CHANNEL, TRACK, assign_tracks, exit_point, left_channels, node_rect, plan_gaps, row_spans
from ..model import GAP, MARGIN, comp_style, step_targets
from ..profile import Profile
from ..shapes import SHAPES, diamond_inset, diamond_size, inscribed, shape_legend
from ..tips import step_tip

#: Box width, characters a line at that width (font 11), line height, least box height and the widest a decision grows to.
BOX_W, BOX_CHARS, LINE_H, BOX_H, DECISION_MAX = 240, 34, 15, 56, 440
#: The space after a lane's gutter.
GUTTER_GAP = 16
TABS = {"chart": "Chart", "lanes": "Lanes", "bpmn": "BPMN"}
#: More room in the gaps when a diamond has three ways out.
THREE_WAY_ROOM = 40
#: The same room on a page turned on its side.
TURNED_LABEL_ROOM, TURNED_GAP = 100, 60
#: Space between columns; in a gap between rows, the room under a box for a label.
COL_GAP, LABEL_ROOM = 70, 44
#: Where a step with no `label` is cut, in characters.
CUT = 64
JUMP = 4
EDGE = "edgeStyle=none;rounded=1;html=1;" + ARROW_HEAD + f"jumpStyle=arc;jumpSize={JUMP};"
COLOURS = {"Yes": "#1b7a3a", "No": "#b3261e", "": "#333333"}
BACK = EDGE + "dashed=1;strokeColor=#6a3fa0;"
STOP_EDGE = EDGE + "dashed=1;strokeColor=#b3261e;"
STOP_BOX = ("rounded=1;absoluteArcSize=1;arcSize=30;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=10;align=left;"
            "verticalAlign=middle;spacingLeft=10;spacingRight=8;")
END_BOX = ("rounded=1;absoluteArcSize=1;arcSize=30;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#333333;strokeWidth=2;fontSize=11;"
           "fontStyle=1;spacingLeft=10;spacingRight=10;")


def short_text(step: dict) -> str:
    """A box's words: the `label` whole, else a gate's question, else the action, those two cut at a word.

    A `label` is the box's words by contract (schema: up to 80 characters), so it is never cut; the box wraps it. Only text the engine picks
    for the box is cut at CUT (2026-11-11: enterprise-strategy's lane page lost the end of 65 to 80 character labels to " ...").

    Args:
        step: the step from the map.

    Returns:
        The text.
    """
    if step.get("label"):
        return step["label"]
    text = step.get("gate") or step["action"].split("; ")[0].split(". ")[0]
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


def _size(lines: list[str], shape: str, look: dict) -> tuple[int, int]:
    """A box's size for its text; a diamond fits its text's inscribed rectangle (shapes.diamond_size), or with `look.decision_fit` "widen"
    widens until it is no taller than 0.6 of its width.

    Args:
        lines: the label lines.
        shape: the flowmap.shapes key.
        look: the drawing's look.

    Returns:
        (width, height).
    """
    if shape == "decision" and inscribed(look):
        return diamond_size(lines, (BOX_W - 4) / BOX_CHARS, LINE_H, look)
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
        self.turned = mode != "chart" and not flow.get("_vertical")
        self.label_room = TURNED_LABEL_ROOM if self.turned else LABEL_ROOM   # on a turned page this gap is sideways, and words need more of it
        self.label_room += THREE_WAY_ROOM if any(e.index > 1 for e in self.graph.edges) else 0   # three labels share a three-way diamond's gap
        if mode != "chart":
            self.lanes, self.actors = lane_map(self.graph)
            self.first_col = lane_columns(len(self.actors))
        self.grid: Grid = place(self.graph, self.lanes, self.first_col or None)
        self.targets = {s["id"]: step_targets(flow["steps"], k) for k, s in enumerate(flow["steps"])}
        self.shapes = {sid: step_chart_shape(s, self.targets[sid]) for sid, s in self.graph.steps.items()}
        self.labels = {(e.src, e.dst): _branch(self.graph, e, self.targets.get(e.src, [])) for e in self.graph.edges}
        swap_branches(self.graph, self.grid)
        self.left = {} if self.lanes else left_channels(self.graph, self.grid)
        self.reversed_gaps: frozenset = frozenset()   # gaps whose track order improve_tracks reversed
        self.text, self.size = {}, {}
        for nid in self.graph.order:
            self.text[nid] = self._lines(nid)
            shape = self.shapes.get(nid, "process" if nid in self.graph.stops else "terminator")
            self.size[nid] = _size(self.text[nid], shape, {**profile.look, "decision_fit": "widen"} if self.bpmn else profile.look)   # BPMN keeps its gateway
            if self.bpmn and nid not in self.graph.steps:
                self.size[nid] = (BOX_W, max(bpmn.EVENT, self.size[nid][1] * 2 if nid in self.graph.stops else 0))
                if self.turned:
                    self.size[nid] = (bpmn.EVENT, bpmn.EVENT) if nid == START else (bpmn.EVENT + 4 + bpmn.EVENT_TEXT, self.size[nid][1])
            if self.turned:
                self.size[nid] = self.size[nid][::-1]   # laid out on its side
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
        gap = TURNED_GAP if self.turned else max([COL_GAP] + [mark_size(t)[0] + 40 for t in self.labels.values() if t])   # words run across a turned gap, not along it
        lefts = [v for v in self.left.values() if v[0] == "left"]
        rights = [v for v in self.left.values() if v[0] == "right"]
        words = [mark_size(self.labels[key])[0] for key in self.left if self.labels[key]]
        room = max(words + [0]) + 28
        third = any(e.kind == "main" and e.index > 1 and self.grid.cols[e.src] == 0 for e in self.graph.edges) and not self.lanes
        self.third_x = MARGIN   # the outermost channel, for a third way out of a diamond
        self.left_x = MARGIN + (len(set(lefts)) + third) * CHANNEL if lefts or third else MARGIN   # the channels, then room for a label on the way out
        self.right_gap = len(set(rights)) * CHANNEL + room if rights else 0
        self.cx, self.col_left, x = {}, {}, self.left_x + (room if lefts or third else 0)
        for c in range(last + 1):
            w = widths[c] or 40
            self.col_left[c], self.cx[c] = x - (GUTTER_GAP / 2 if self.lanes else gap / 2), x + w / 2
            x += w + (GUTTER_GAP if self.lanes and c % 2 else gap) + (self.right_gap if c == 0 else 0)
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


def draw_nodes(page: View, chart: Chart, ys: dict) -> list[str]:
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
        rect = node_rect(chart, ys, nid)
        text = label(*chart.text[nid])
        if chart.bpmn and nid not in chart.graph.steps:
            kind = "error" if nid in chart.graph.stops else "start" if nid == START else "end"
            bpmn.event(page.page, f"{fid}-c-{nid}", kind, page.rect(*rect), chart.text[nid], chart.turned)
        elif nid in chart.graph.stops:
            page.box(f"{fid}-c-{nid}", text, rect, STOP_BOX, solid=True)
        elif nid in (START, END):
            page.box(f"{fid}-c-{nid}", text, rect, END_BOX, solid=True)
            used.append("terminator")
        else:
            s, shape = chart.graph.steps[nid], chart.shapes[nid]
            actor = chart.comps[s["actor"]]
            style = bpmn.step_style(shape, *chart.profile.style(actor["kind"])) if chart.bpmn else comp_style(actor["kind"], chart.profile, "fontSize=11;" + SHAPES[shape][0]
                                                                                                                + (diamond_inset(rect[2]) if shape == "decision" and inscribed(chart.profile.look) else ""))
            charts, flows = chart.page_ids
            link = f"data:page/id,chart-{s['flow']}" if s.get("flow") in charts else f"data:page/id,flow-{s['flow']}" if s.get("flow") in flows else ""
            page.box(f"{fid}-c-{nid}", text, rect, style, link=link, tooltip=step_tip(s, str(n), actor["name"]), solid=True)
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
    sx, sy, sw, sh = node_rect(chart, ys, e.src)
    if e.kind == "main" and chart.grid.rows[e.src] == chart.grid.rows[e.dst]:   # a hand-off level with its source runs sideways
        return [(sx + sw, sy + sh / 2), (node_rect(chart, ys, e.dst)[0], sy + sh / 2)]
    if key in chart.left:
        tx, ty, tw, th = node_rect(chart, ys, e.dst)
        side, k = chart.left[key]
        if side == "right":
            lane = max(sx + sw, tx + tw) + chart.right_gap - CHANNEL * (k + 1)
            return [(sx + sw, sy + sh / 2), (lane, sy + sh / 2), (lane, ty + th / 2), (tx + tw, ty + th / 2)]
        lane = chart.left_x - CHANNEL * k
        return [(sx, sy + sh / 2), (lane, sy + sh / 2), (lane, ty + th / 2), (tx, ty + th / 2)]
    side, x = exit_point(chart, e)
    mid = sy + sh / 2
    if e.kind == "stop" and chart.lanes:
        _dx, dy, _dw, dh = node_rect(chart, ys, e.dst)
        return [(x, sy + sh), (x, dy + dh / 2 - bpmn.EVENT / 2 if chart.bpmn and not chart.turned else dy)]   # an upright BPMN stop is a circle centred in its cell
    if e.kind == "stop":
        return [(sx + sw, mid), (node_rect(chart, ys, e.dst)[0], mid)]
    pts = [(sx + sw if x > sx else sx, mid), (x, mid)] if side else [(x, sy + sh)]
    for gap, a, b in legs[key]:
        y = ys["track"][gap] + tracks[(key, gap, a)] * TRACK
        pts += [(a, y), (b, y)]
    return pts + [(entries[key], node_rect(chart, ys, e.dst)[1])]


def _polylines(chart: Chart) -> list:
    """Every arrow's polyline as the graph stands, for comparing two ways of drawing it.

    Args:
        chart: the chart.

    Returns:
        The polylines.
    """
    legs, entries = plan_gaps(chart)
    tracks = assign_tracks(legs, chart.reversed_gaps)
    ys = row_spans(chart, tracks, 0)
    return [_edge_points(chart, ys, e, (legs, entries, tracks)) for e in chart.graph.edges]


def draw_edges(page: View, chart: Chart, ys: dict, route: tuple) -> None:
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
        pts = page.points(_edge_points(chart, ys, e, route))
        cid = f"{fid}-ce-{e.src}-{e.dst}"
        colour = COLOURS.get(words, COLOURS[""])
        style = BACK if e.kind == "back" else STOP_EDGE if e.kind == "stop" else EDGE + f"strokeColor={colour};"
        style = EDGE + f"strokeColor={COLOURS['No'] if e.kind == 'stop' else colour};" if chart.bpmn else style   # BPMN: all sequence flows, so all solid
        page.page.route(cid, f"{fid}-c-{e.src}", f"{fid}-c-{e.dst}", pts, style, "thin", jump=JUMP)
        if e.kind == "back" and not words:
            words = "back"
        says_itself = e.index > 1 and "-stop" in e.dst   # a third way out into a stop box: the box already says it, and its gap has no room for a label
        if (words or e.kind == "stop") and not says_itself:
            items.append((cid, words or "fails", pts, COLOURS["No"] if e.kind == "stop" else "#6a3fa0" if e.kind == "back" else colour))
    place_labels(page.page, items)


def chart_page(flow: dict, comps: dict, profile: Profile, page_ids: tuple, mode: str = "chart") -> Page:
    """One flowchart page: a header with the purpose and trigger, the chart (in swimlanes when asked, left to right unless the entry says vertical), and a legend of its symbols.

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
    tab = profile.look.get("chart_tab", TABS["chart"]) if mode == "chart" else TABS[mode]   # `look.chart_tab` names chart tabs (2026-11-06)
    page = Page(fid, f"{tab}: {flow['title']}"[:60])
    page.label_clearance, page.run_spacing = profile.look.get("label_clearance", 0), profile.look.get("run_spacing", 0)
    head = [f"**{flow['title']}** ({tab.lower()})", BLANK, flow["purpose"], BLANK, f"**Trigger:** {flow['trigger']['kind']}: {flow['trigger']['detail']}",
            BLANK, "[back to Overview]"]
    if swimlanes:
        improve_branches(chart.graph, lambda: _polylines(chart))
        improve_tracks(chart, lambda: _polylines(chart))
    legs, entries = plan_gaps(chart)
    tracks = assign_tracks(legs, chart.reversed_gaps)
    span = chart.channel_x + CHANNEL * len(chart.channels)
    width = max(900.0, (row_spans(chart, tracks, LANE_HEAD + 8)["bottom"] if chart.turned else span - MARGIN))
    head_h = header_height(head, width, 80)
    page.box(f"{fid}-chart-head", label(*head), MARGIN, MARGIN, width, head_h,
             "rounded=0;whiteSpace=wrap;html=1;fillColor=#fafafa;strokeColor=#666666;align=left;verticalAlign=top;spacingLeft=8;spacingTop=4;fontSize=12;",
             link="data:page/id,overview")
    below = MARGIN + head_h + GAP
    ys = row_spans(chart, tracks, LANE_HEAD + 8 if chart.turned else below + (LANE_HEAD + 8 if swimlanes else 0))
    view = View(page, chart.turned, MARGIN, below - MARGIN + 8)
    if swimlanes:
        draw_lanes(view, chart, ys)
    used = draw_nodes(view, chart, ys)
    draw_edges(view, chart, ys, (legs, entries, tracks))
    legend_y = (span + view.dy if chart.turned else ys["bottom"]) + GAP
    if chart.bpmn:
        bpmn.legend(page, MARGIN, legend_y, f"{fid}-chart")
    else:
        shape_legend(page, list(dict.fromkeys(used)), MARGIN, legend_y, f"{fid}-chart")
    return page
