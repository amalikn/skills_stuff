"""The flow map's Overview page: groups with layered interiors, thick group-to-group arrows with counts, thin grey arrows inside groups, dots
on the boxes that feed a thick arrow, one draw.io layer per thick colour plus one for the thin arrows, the flow index and the legends. Stdlib only.

Every arrow is routed here, not by draw.io: thick arrows get their own point on each group edge (drawio.route.spread) and their own track in
every channel (drawio.route.track); thin arrows follow their slot chains with one track per arrow in each row gap, then drawio.route.untwist()
keeps their hops apart. drawio.audit.page_audit() must report nothing on the result.

Imported, not run: `from flowmap.overview import overview_page` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio import route
from drawio.mxfile import Page, Point, Rect, label

from .model import GROUP_HEAD, MARGIN, comp_style
from .overview_layout import (OV_BH, OV_BW, OV_CHANNEL, OV_HGAP, OV_JUMP, OV_LEFT, OV_MIN_HEAD, OV_MIN_THIN, OV_PAD, OV_SIDE, OV_SLOT, OV_SP,
                              OV_THIN_JUMP, OV_THIN_SP, OV_TOP, THIN_GREY, box_lines, far_channels, key_width, layout_group, side, text_height)
from .profile import DISTINCT, Profile


class Overview:
    """Lays out and draws the Overview page."""

    def __init__(self, data: dict, profile: Profile) -> None:
        """Group the components, size every group, place the grid and plan the thick arrows and their channels.

        Args:
            data: the validated map.
            profile: the project's drawing profile.
        """
        self.data, self.profile = data, profile
        self.by_id = {c["id"]: c for c in data["components"]}
        self.groups: dict[str, list[str]] = {}
        for c in data["components"]:
            self.groups.setdefault(c["group"], []).append(c["id"])
        self.gnames = list(self.groups)
        self.gof = {cid: gi for gi, ids in enumerate(self.groups.values()) for cid in ids}
        by_id, gof = self.by_id, self.gof
        self.same = {cid: [d for d in by_id[cid].get("depends_on", []) if gof[d] == gof[cid] and d != cid] for cid in by_id}
        self.far = {cid: [by_id[d]["name"] for d in by_id[cid].get("depends_on", []) if gof[d] != gof[cid]] for cid in by_id}
        self.lay = {gi: layout_group(ids, self.same) for gi, ids in enumerate(self.groups.values())}
        self._measure()
        self._plan()
        self._grid()

    def _measure(self) -> None:
        """Box, row, row-gap and group heights, and the group grid's rows and columns.

        Each box is as tall as its own text; a group row as tall as its tallest box; a row gap gives each arrow crossing it a track OV_THIN_SP
        apart (so thin hops never double up) and OV_MIN_THIN of straight run before the box below; a group as tall as its own content.
        """
        self.box_h = {k: text_height(box_lines(self.by_id[k], self.far[k])) for k in self.by_id}
        self.row_bh, self.row_gap, self.gh_of = {}, {}, {}
        for gi, gl in self.lay.items():
            self.row_bh[gi] = [max([OV_BH] + [self.box_h[k] for k in row if not k.startswith("slot:")]) for row in gl.rows]
            self.row_gap[gi] = [max(OV_HGAP + 14, 8 + OV_MIN_THIN + (n + 1) * OV_THIN_SP) if n else OV_HGAP + 14 for n in gl.gaps]
            self.gh_of[gi] = (GROUP_HEAD + sum(self.row_bh[gi][:-1]) + sum(self.row_gap[gi][:-1]) + (self.row_bh[gi][-1] if self.row_bh[gi] else 0)
                              + OV_PAD)
        self.ncol = ncol = self.profile.groups_per_row
        self.nrow = (len(self.lay) + ncol - 1) // ncol
        self.grow = {gi: gi // ncol for gi in self.lay}
        self.gcol = {gi: gi % ncol for gi in self.lay}
        self.col_w = [max([self.lay[gi].width for gi in self.lay if self.gcol[gi] == c], default=0) for c in range(ncol)]
        self.row_h = [max(self.gh_of[gi] for gi in self.lay if self.grow[gi] == r) for r in range(self.nrow)]

    def _plan(self) -> None:
        """One thick arrow plan per group pair, with the channels it uses.

        Adjacent rows drop straight or turn once in the channel between them; only arrows that skip a row use a column channel.
        """
        grow, gcol, gof = self.grow, self.gcol, self.gof
        self.pairs: dict[tuple[int, int], int] = {}
        for c in self.data["components"]:
            for d in c.get("depends_on", []):
                if gof[c["id"]] != gof[d]:
                    self.pairs[(gof[c["id"]], gof[d])] = self.pairs.get((gof[c["id"]], gof[d]), 0) + 1
        self.plans = []
        for (a, b), n in sorted(self.pairs.items()):
            if grow[a] == grow[b] and abs(gcol[a] - gcol[b]) == 1:
                kind = "side"
            elif abs(grow[a] - grow[b]) == 1:
                kind = "adjacent"
            else:
                kind = "far"
            self.plans.append({"a": a, "b": b, "n": n, "kind": kind, "pid": len(self.plans)})
        self.hchan: dict[int, list[int]] = {}
        self.vchan: dict[int, list[int]] = {}
        for p in self.plans:
            if p["kind"] == "adjacent":
                self.hchan.setdefault(min(grow[p["a"]], grow[p["b"]]), []).append(p["pid"])
            elif p["kind"] == "far":
                r1, r2, cv = far_channels(p, grow, gcol)
                self.hchan.setdefault(r1, []).append(p["pid"])
                self.hchan.setdefault(r2, []).append(p["pid"])
                self.vchan.setdefault(cv, []).append(p["pid"])

    def _grid(self) -> None:
        """Channel sizes (at least OV_CHANNEL, growing so tracks stay OV_SP apart with OV_MIN_HEAD clear at each side), group positions, and
        one thick colour per target group."""
        nrow, ncol = self.nrow, self.ncol
        self.hch = [max(OV_CHANNEL, 2 * OV_MIN_HEAD + (len(self.hchan.get(r, [])) - 1) * OV_SP) for r in range(nrow)]
        self.vch = [0] + [max(OV_CHANNEL, 2 * OV_MIN_HEAD + (len(self.vchan.get(c, [])) - 1) * OV_SP) for c in range(1, ncol)]
        self.col_left = [MARGIN + sum(self.col_w[:c]) + sum(self.vch[1:c + 1]) for c in range(ncol)]
        self.row_top = [MARGIN + OV_TOP + sum(self.row_h[:r]) + sum(self.hch[:r]) for r in range(nrow)]
        self.grid_right = self.col_left[-1] + self.col_w[-1]
        self.into = sorted({b for (_, b) in self.pairs})
        self.tcol = {b: DISTINCT[i % len(DISTINCT)] for i, b in enumerate(self.into)}

    def _groups(self, page: Page) -> None:
        """Draw each group and its boxes, recording group rectangles, box positions and row tops.

        Args:
            page: the page.
        """
        self.gpos: dict[int, Rect] = {}
        self.pos: dict[str, Point] = {}
        self.row_y: dict[int, list[float]] = {}
        for gi, gl in self.lay.items():
            gx = self.col_left[self.gcol[gi]] + (self.col_w[self.gcol[gi]] - gl.width) / 2
            gy = self.row_top[self.grow[gi]]
            page.box(f"ov-g-{gi}", label(f"**{self.gnames[gi]}**"), gx, gy, gl.width, self.gh_of[gi],
                     "rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#777777;dashed=1;verticalAlign=top;align=left;spacingLeft=8;fontSize=12;",
                     solid=True)
            self.gpos[gi] = (gx, gy, gl.width, self.gh_of[gi])   # only as tall as its content; rows stay top-aligned
            ry = gy + GROUP_HEAD
            self.row_y[gi] = []
            for ri, row in enumerate(gl.rows):
                self.row_y[gi].append(ry)
                for k in row:
                    if not k.startswith("slot:"):
                        self._box(page, k, gx + gl.x[k], ry)
                    self.pos[k] = (gx + gl.x[k], ry)
                ry += self.row_bh[gi][ri] + self.row_gap[gi][ri]

    def _box(self, page: Page, k: str, x: float, y: float) -> None:
        """Draw one component box with its tooltip.

        Args:
            page: the page.
            k: the component id.
            x: left edge.
            y: top edge.
        """
        c = self.by_id[k]
        ports = ", ".join(str(p) for p in c.get("ports", []))
        tip = "\n".join(x for x in (f"kind: {c['kind']}", f"host: {c['host']}", f"ports: {ports}" if ports else "",
                                    f"health: {c['health']}", c.get("notes", "")) if x)
        page.box(f"ov-c-{k}", label(*box_lines(c, self.far[k])), x, y, OV_BW, self.box_h[k],
                 comp_style(c["kind"], self.profile, f"fontSize=10;align=left;verticalAlign=top;spacingTop=4;spacingLeft={OV_LEFT};spacingRight={OV_SIDE};"),
                 tooltip=tip, solid=True)

    def _thin_routes(self, gi: int) -> dict:
        """One group's thin arrows along their slot chains, one track per arrow in each row gap; the last drop is at least OV_MIN_THIN.

        Args:
            gi: the group index.

        Returns:
            {(source id, target id): polyline}, untwisted.
        """
        gl, pos = self.lay[gi], self.pos
        row_of = {k: i for i, row in enumerate(gl.rows) for k in row}
        used = [0] * len(gl.rows)
        thin: dict[tuple[str, str], list] = {}
        outs: dict[str, list] = {}
        ins: dict[str, list] = {}
        for ch in gl.chains:
            outs.setdefault(ch[0], []).append(ch)
            ins.setdefault(ch[-1], []).append(ch)
        for k in outs:   # a box's arrows leave and arrive ordered by where they go, so they do not cross each other
            outs[k].sort(key=lambda ch: pos[ch[1]][0] + key_width(ch[1]) / 2)
        for k in ins:
            ins[k].sort(key=lambda ch: pos[ch[-2]][0] + key_width(ch[-2]) / 2)
        for ch in gl.chains:
            s, d = ch[0], ch[-1]
            fo = (outs[s].index(ch) + 1) / (len(outs[s]) + 1)
            fi = (ins[d].index(ch) + 1) / (len(ins[d]) + 1)
            px = pos[s][0] + OV_BW * fo
            pts = [(px, pos[s][1] + self.box_h[s])]
            for a, b in zip(ch, ch[1:]):
                ra = row_of[a]
                used[ra] += 1
                ty = self.row_y[gi][ra] + self.row_bh[gi][ra] + 8 + (self.row_gap[gi][ra] - 8 - OV_MIN_THIN) * used[ra] / (gl.gaps[ra] + 1)
                nx = (pos[b][0] + OV_SLOT / 2) if b.startswith("slot:") else (pos[b][0] + OV_BW * fi)
                pts += [(px, ty), (nx, ty)]
                px = nx
            pts.append((px, pos[d][1]))
            thin[(s, d)] = pts
        route.untwist(thin, OV_THIN_JUMP, {(s, d): (pos[s][0], pos[d][0]) for s, d in thin}, OV_BW)
        return thin

    def _thin(self, page: Page) -> None:
        """Draw every group's thin arrows.

        Args:
            page: the page.
        """
        for gi in self.lay:
            for (s, d), pts in self._thin_routes(gi).items():
                page.route(f"ov-d-{s}-{d}", f"ov-c-{s}", f"ov-c-{d}", pts,
                           f"edgeStyle=none;rounded=1;html=1;strokeColor={THIN_GREY};strokeWidth=1.5;endArrow=block;endSize=6;jumpStyle=arc;jumpSize={OV_THIN_JUMP};",
                           klass="thin", layer="ov-L-inside", ignore=(f"ov-g-{gi}",), jump=OV_THIN_JUMP)

    def _ends(self) -> dict:
        """Every thick arrow's place on each group edge it uses.

        Returns:
            {(plan id, end): fraction along the edge}.
        """
        edge_users: dict[tuple[int, str], list] = {}
        for p in self.plans:
            for end in ("a", "b"):
                g, other = (p["a"], p["b"]) if end == "a" else (p["b"], p["a"])
                sd = side(p, end, self.grow, self.gcol)
                key = (self.gpos[other][0] + self.gpos[other][2] / 2) if sd in ("top", "bottom") else self.gpos[other][1]
                edge_users.setdefault((g, sd), []).append((key, p["pid"], end))
        frac: dict[tuple[int, str], float] = {}
        for (g, sd), users in edge_users.items():
            frac.update(route.spread(users, sd))
        return frac

    def _thick_points(self, p: dict, frac: dict, row_bot: list) -> list:
        """One thick arrow's polyline.

        Args:
            p: the plan.
            frac: each end's fraction along its group edge.
            row_bot: each grid row's bottom.

        Returns:
            The full polyline, group edge to group edge.
        """
        a, b, pid, grow, gcol, gpos = p["a"], p["b"], p["pid"], self.grow, self.gcol, self.gpos
        s = route.edge_point(gpos[a], side(p, "a", grow, gcol), frac[(pid, "a")])
        e = route.edge_point(gpos[b], side(p, "b", grow, gcol), frac[(pid, "b")])
        if p["kind"] == "side":   # groups differ in height: spread over the part of the edges both groups share
            shared = min(gpos[a][3], gpos[b][3])
            s = route.edge_point(gpos[a][:3] + (shared,), side(p, "a", grow, gcol), frac[(pid, "a")])
            e = route.edge_point(gpos[b][:3] + (shared,), side(p, "b", grow, gcol), frac[(pid, "b")])
            y = (s[1] + e[1]) / 2
            s, e = (s[0], y), (e[0], y)
            pts = []
        elif p["kind"] == "adjacent":
            r = min(grow[a], grow[b])
            y = route.track(self.hchan[r], pid, row_bot[r] + self.hch[r] / 2, OV_SP)
            pts = [] if abs(s[0] - e[0]) < 1 else [(s[0], y), (e[0], y)]
        else:
            r1, r2, cv = far_channels(p, grow, gcol)
            y1 = route.track(self.hchan[r1], pid, row_bot[r1] + self.hch[r1] / 2, OV_SP)
            y2 = route.track(self.hchan[r2], pid, row_bot[r2] + self.hch[r2] / 2, OV_SP, last=True)
            xv = route.track(self.vchan[cv], pid, self.col_left[cv] - self.vch[cv] / 2, OV_SP)
            pts = [(s[0], y1), (xv, y1), (xv, y2), (e[0], y2)]
        return [s] + pts + [e]

    def _thick(self, page: Page) -> None:
        """Draw the thick arrows, then their counts (on each arrow's longest clear run, 18 pt bold in its colour).

        Args:
            page: the page.
        """
        frac = self._ends()
        row_bot = [self.row_top[r] + self.row_h[r] for r in range(self.nrow)]
        for p in self.plans:
            a, b = p["a"], p["b"]
            p["full"] = self._thick_points(p, frac, row_bot)
            page.route(f"ov-gg-{a}-{b}", f"ov-g-{a}", f"ov-g-{b}", p["full"],
                       f"edgeStyle=none;rounded=1;html=1;strokeColor={self.tcol[b]};strokeWidth=4;endArrow=block;endSize=9;jumpStyle=arc;jumpSize={OV_JUMP};",
                       klass="thick", layer=f"ov-L-into-{b}", jump=OV_JUMP)
        placed: list[Rect] = []
        for p in self.plans:
            lx, ly = route.count_spot(p["full"], [q["full"] for q in self.plans if q is not p], placed)
            placed.append((lx - 20, ly - 15, 40, 30))
            page.mark(f"ov-gl-{p['a']}-{p['b']}", label(f"**{p['n']}**"), lx, ly, 40, 30,
                      f"text;html=1;align=center;verticalAlign=middle;fontSize=18;fontColor={self.tcol[p['b']]};labelBackgroundColor=#ffffff;",
                      owner=f"ov-gg-{p['a']}-{p['b']}", layer=f"ov-L-into-{p['b']}")

    def _dots(self, page: Page) -> None:
        """A box that feeds a thick arrow carries a dot in that arrow's colour (one per target group), stacked down its right edge.

        Args:
            page: the page.
        """
        for gi, ids in enumerate(self.groups.values()):
            for cid in ids:
                targets = sorted({self.gof[d] for d in self.by_id[cid].get("depends_on", []) if self.gof[d] != gi})
                bx, by = self.pos[cid]
                for n_dot, tg in enumerate(targets):
                    page.box(f"ov-dot-{cid}-{tg}", "", bx + OV_BW - 17, by + 5 + n_dot * 15, 12, 12,
                             f"ellipse;html=1;fillColor={self.tcol[tg]};strokeColor=#ffffff;strokeWidth=1;", layer=f"ov-L-into-{tg}")

    def page(self) -> Page:
        """Draw the page: layers, title, groups and boxes, thin arrows, thick arrows and counts, dots, the flow index and the legends.

        Returns:
            The page.
        """
        page = Page("overview", "Overview")
        # Layers: one per thick colour and one for the thin arrows, so any colour can be hidden in draw.io's Layers panel.
        for b in self.into:
            page.add_layer(f"ov-L-into-{b}", f"Thick: into {self.gnames[b]}")
        page.add_layer("ov-L-inside", "Thin: inside groups")
        fx = self.grid_right + 80
        page.box("ov-title", label(f"**{self.data['title']}**",
                                   f"Generated from {self.profile.map} by `{self.profile.command}`; do not edit. Updated {self.data['updated']}.",
                                   "Thick arrows: dependencies between groups (number = how many box-to-box dependencies it stands for). Thin grey arrows: "
                                   "inside a group; a box sits above what it needs. Each box lists what it needs from other groups. Each flow box links to "
                                   "its page; hover a component for its health check. Layers panel: hide any arrow colour."),
                 MARGIN, MARGIN, fx + 340 - MARGIN, 66, "text;html=1;align=left;verticalAlign=top;whiteSpace=wrap;fontSize=13;")
        self._groups(page)
        self._thin(page)
        self._thick(page)
        self._dots(page)
        legend_y = flow_index(page, self.data, self.profile, fx, MARGIN + OV_TOP)
        colour_legend(page, fx, legend_y + 24, [(self.tcol[b], f"into {self.gnames[b]}") for b in self.into])
        return page


def overview_page(data: dict, profile: Profile) -> Page:
    """The Overview page.

    Args:
        data: the validated map.
        profile: the project's drawing profile.

    Returns:
        The page.
    """
    return Overview(data, profile).page()


def colour_legend(page: Page, x: float, y: float, thick: list) -> None:
    """The arrow colour legend, below the component kind legend on the right: one swatch per thick colour, the thin grey, and the dots.

    Args:
        page: the page.
        x: left edge.
        y: top edge.
        thick: (colour, text) per thick arrow colour.
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


def flow_index(page: Page, data: dict, profile: Profile, x: float, y: float) -> float:
    """The flow index (one clickable box per flow page, plus the End-to-end page) and the component kind legend, right of the group grid.

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
    for fi, f in enumerate(data["flows"]):
        page.box(f"ov-f-{f['id']}", label(f"**{fi + 1}. {f['title']}**", f"{f['trigger']['kind']} · runs on {f['runs_on']} · {f['category']}"),
                 x, y + 102 + fi * 62, 340, 52, "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#3d5a80;fontSize=11;align=left;spacingLeft=6;",
                 link=f"data:page/id,flow-{f['id']}", tooltip=f["purpose"])
    ly = y + 122 + len(data["flows"]) * 62
    page.box("ov-legend", label("**Legend: component kinds**"), x, ly - 18, 340, 30, "text;html=1;align=left;fontSize=12;whiteSpace=wrap;")
    for ki, kind in enumerate(profile.kind_style):
        page.box(f"ov-k-{kind}", label(kind), x + (ki % 2) * 175, ly + 20 + (ki // 2) * 34, 165, 28, comp_style(kind, profile))
    return ly + 20 + ((len(profile.kind_style) + 1) // 2) * 34
