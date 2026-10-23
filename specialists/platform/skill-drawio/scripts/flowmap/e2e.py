"""The End-to-end page: every component in tier columns and every flow drawn as a coloured path through its step actors, one draw.io layer per
flow family. Stdlib only.

flowmap.e2e_grid.E2EGrid places and plans everything; EndToEnd adds a crossing-cutting local search (swap neighbouring tracks in each channel
and corridor, and neighbouring ports in each pool, keeping a swap only when crossings drop and shared tracks stay apart), then draws: column
stripes and headings, the band below, boxes, per family its dashed connectors, step arrows and flow.step labels, and the legend.

Imported, not run: `from flowmap.e2e import end_to_end_page` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.audit import rects_overlap, seg_hits_rect, segments
from drawio.mxfile import ARROW_HEAD, BLANK, HEADER_STYLE, Page, Point, header_height, label
from drawio.route import count_crossings, oriented

from .e2e_grid import E2E_BOX_PAD, E2E_BW, E2E_JUMP, E2E_LABEL_H, E2E_LABEL_W, E2E_SP, E2EGrid, Link, e2e_box_lines, e2e_text_height
from .model import MARGIN, comp_style, status_style
from .shapes import component_shape, component_shapes_used, fit_height, person_badge, shape_legend
from .profile import Profile
from .tips import comp_tags, comp_tip


def _swapper(order: list, i: int, j: int) -> object:
    """A callable swapping two entries of a list (its own inverse).

    Args:
        order: the list.
        i: one index.
        j: the other.

    Returns:
        The callable.
    """
    def run() -> None:
        """Swap the entries."""
        order[i], order[j] = order[j], order[i]
    return run


class EndToEnd(E2EGrid):
    """Lays out, improves and draws the End-to-end page."""

    def __init__(self, data: dict, profile: Profile) -> None:
        """Place, plan and size (E2EGrid), then improve track and port orders to cut crossings.

        Args:
            data: the validated map.
            profile: the project's drawing profile.
        """
        super().__init__(data, profile)
        self._improve()

    def _track_x(self, ch: int, key: str) -> float:
        """A vertical run's track x.

        Args:
            ch: the channel.
            key: the run key.

        Returns:
            The x.
        """
        n = len(self.vslot[ch])
        left = self.col_x[ch] + E2E_BW
        return left + (self.ch_w[ch] - (n - 1) * E2E_SP) / 2 + self.vslot[ch][self.vtrack[key]] * E2E_SP

    def _side_x(self, comp: str, sd: str) -> float:
        """The x of a box's left or right side.

        Args:
            comp: the component id.
            sd: "L" or "R".

        Returns:
            The x.
        """
        x = self.col_x[self.cell[comp][0]]
        return x + E2E_BW if sd == "R" else x

    def points(self, link: Link) -> list:
        """A link's polyline under the current track and port orders.

        Args:
            link: the link.

        Returns:
            The points from the source's side to the target's.
        """
        sx, tx = self._side_x(link.src, link.exit[2]), self._side_x(link.dst, link.entry[2])
        if link.kind == "straight":
            y = self._port_y(link.cid, "exit")
            return [(sx, y), (tx, y)]
        ye, yi = self._port_y(link.cid, "exit"), self._port_y(link.cid, "entry")
        if link.kind == "z":
            x = self._track_x(link.exit[0], f"{link.cid}|z")
            return [(sx, ye), (x, ye), (x, yi), (tx, yi)]
        yc = self._gap_y(link.cid, link.gap)
        x1, x2 = self._track_x(link.exit[0], f"{link.cid}|1"), self._track_x(link.entry[0], f"{link.cid}|2")
        return [(sx, ye), (x1, ye), (x1, yc), (x2, yc), (x2, yi), (tx, yi)]

    def _crossings(self, cids: set) -> int:
        """How many crossings the given links have with all links (each pair inside the set counted once).

        Args:
            cids: the link ids.

        Returns:
            The count.
        """
        n = 0
        for a in cids:
            sa, (ax0, ay0, ax1, ay1) = self.segs[a], self.bbox[a]
            for b, sb in self.segs.items():
                if b == a or (b in cids and b < a):
                    continue
                bx0, by0, bx1, by1 = self.bbox[b]
                if bx0 > ax1 or ax0 > bx1 or by0 > ay1 or ay0 > by1:   # boxes apart: no crossing (keeps the search fast)
                    continue
                n += count_crossings(sa, sb)
        return n

    def _refresh(self, cids: set) -> None:
        """Recompute the polylines of the given links.

        Args:
            cids: the link ids.
        """
        for cid in cids:
            self.pts[cid] = self.points(self.by[cid])
            self.segs[cid] = oriented(self.pts[cid])
            xs, ys = [x for x, _y in self.pts[cid]], [y for _x, y in self.pts[cid]]
            self.bbox[cid] = (min(xs), min(ys), max(xs), max(ys))

    def _runs_ok(self, cids: set) -> bool:
        """Whether the given links' vertical runs still keep E2E_SP from every other run sharing their track (ports moved).

        Args:
            cids: the link ids whose ports moved.

        Returns:
            True when every shared track keeps its separation.
        """
        spans = {}
        for link in self.links:
            for ch, lo, hi, key in self._verticals(link):
                spans[key] = (ch, lo, hi)
        for cid in cids:
            for ch, lo, hi, key in self._verticals(self.by[cid]):
                for other in self.vruns[(ch, self.vtrack[key])]:
                    if other != key:
                        _c, olo, ohi = spans[other]
                        if not (hi + E2E_SP <= olo or ohi + E2E_SP <= lo):
                            return False
        return True

    def _try(self, swap: object, cids: set, check_runs: bool = False) -> bool:
        """Apply a self-inverse swap and keep it only when it cuts crossings (and, for ports, keeps shared tracks apart).

        Args:
            swap: a callable making the change; calling it again reverts it.
            cids: the links whose polylines it changes.
            check_runs: also require _runs_ok.

        Returns:
            True when kept.
        """
        before = self._crossings(cids)
        swap()
        self._refresh(cids)
        if (not check_runs or self._runs_ok(cids)) and self._crossings(cids) < before:
            return True
        swap()
        self._refresh(cids)
        return False

    def _sweep_slots(self, slots_by: dict, users: dict, check_runs: bool) -> bool:
        """Try swapping each pair of neighbouring slots in every channel (or corridor).

        Args:
            slots_by: {channel: track-to-slot list}, permuted in place.
            users: {(channel, track): link ids on it}.
            check_runs: also require shared tracks to stay apart (a corridor track moves its vertical runs' ends).

        Returns:
            True when any swap was kept.
        """
        changed = False
        for ch, slots in sorted(slots_by.items()):
            inv = {s: t for t, s in enumerate(slots)}
            for s in range(len(slots) - 1):
                ta, tb = inv[s], inv[s + 1]
                cids = users.get((ch, ta), set()) | users.get((ch, tb), set())
                if self._try(_swapper(slots, ta, tb), cids, check_runs):
                    changed = True
                    inv = {s2: t for t, s2 in enumerate(slots)}
        return changed

    def _improve(self) -> None:
        """Local search: swap neighbouring tracks in each channel and corridor, and neighbouring ports in each pool, while crossings drop."""
        self.pts, self.segs, self.bbox = {}, {}, {}
        self._refresh({link.cid for link in self.links})
        vusers = {ct: {key.split("|")[0] for key in keys} for ct, keys in self.vruns.items()}
        gusers: dict[tuple[int, int], set] = {}
        for (cid, g), t in self.gtrack.items():
            gusers.setdefault((g, t), set()).add(cid)
        for _ in range(4):
            changed = self._sweep_slots(self.vslot, vusers, False)
            changed = self._sweep_slots(self.gslot, gusers, True) or changed
            for _key, users in sorted(self.pools.items()):
                for i in range(len(users) - 1):
                    if self._try(_swapper(users, i, i + 1), {users[i][0], users[i + 1][0]}, check_runs=True):
                        changed = True
            if not changed:
                break

    def _label_spot(self, cid: str, page: Page) -> Point:
        """Where a step arrow's flow.step label goes: on one of its own runs (longest first), clear of other edges, labels and boxes.

        Args:
            cid: the link id.
            page: the page so far (boxes and placed labels).

        Returns:
            The label centre (the longest run's middle when nothing is clear; the audit then reports it).
        """
        segs = sorted(segments(self.pts[cid]), key=lambda sg: -(abs(sg[0][0] - sg[1][0]) + abs(sg[0][1] - sg[1][1])))
        w, h = E2E_LABEL_W + 4, E2E_LABEL_H + 4
        for p1, p2 in segs:
            if abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) < 2 * w:
                continue
            for fr in (0.5, 0.35, 0.65, 0.2, 0.8, 0.42, 0.58, 0.28, 0.72):
                cx, cy = p1[0] + (p2[0] - p1[0]) * fr, p1[1] + (p2[1] - p1[1]) * fr
                rect = (cx - w / 2, cy - h / 2, w, h)
                if any(seg_hits_rect(u, v, rect, 0) for o, pts in self.pts.items() if o != cid for u, v in segments(pts)):
                    continue
                if any(rects_overlap(rect, m.rect) for m in page.marks) or any(rects_overlap(rect, page.rects[b]) for b in page.solid):
                    continue
                return (cx, cy)
        p1, p2 = segs[0]
        return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

    def _box_span(self, comp: str) -> tuple[float, float]:
        """A box's top and height: it covers its own ports with E2E_BOX_PAD to spare and fits its text, centred in its row when it has few ports.

        Args:
            comp: the component id.

        Returns:
            (top, height).
        """
        r = self.cell[comp][1]
        mid = self.row_top[r] + self.row_h[r] / 2
        ys = [self._port_y(link.cid, end) for link in self.links for end, who in (("exit", link.src), ("entry", link.dst)) if who == comp]
        least = fit_height(self.comps[comp], self.profile, e2e_text_height(self.comps[comp], self.profile.look['heading_scale']))
        top = min([mid - least / 2] + [y - E2E_BOX_PAD for y in ys])
        bottom = max([mid + least / 2] + [y + E2E_BOX_PAD for y in ys])
        return top, bottom - top

    def _frame(self, page: Page, right: float) -> None:
        """The title, the column stripes and headings, and the band below the columns.

        Args:
            page: the page.
            right: the right edge of the last column.
        """
        head = ["**End-to-end flow: every component, every flow**", BLANK,
                f"Generated from {self.profile.map} by `{self.profile.command}`; do not edit.", BLANK,
                "**Paths:** each flow is a path through the components that act in its steps, coloured by "
                + ("flow." if self.profile.look.get("e2e_layers", "family") == "flow" else "family."),
                "**Arrow labels:** x.y = flow x, step y (the step the arrow leads into, numbered as on the flow's page). Hover an arrow for the step.",
                "**Dashed lines:** not steps; a component the flow runs on, is owned by or depends on, joined to the flow's nearest actor.",
                "**Layers panel:** hide or show each " + ("flow." if self.profile.look.get("e2e_layers", "family") == "flow" else "family."), BLANK, "[back to Overview]"]
        head_h = header_height(head, right - MARGIN, 60)   # grows upward from its old bottom, so the layout below stays put
        page.box("e2e-title", label(*head), MARGIN, MARGIN + 60 - head_h, right - MARGIN, head_h,
                 HEADER_STYLE, link="data:page/id,overview")
        last_tier_bottom = self.row_top[self.band - 1] + self.row_h[self.band - 1]
        for c, (name, _groups) in enumerate(self.profile.tiers):
            page.box(f"e2e-stripe-{c}", "", self.col_x[c] - 8, self.gap_top[-1], E2E_BW + 16, last_tier_bottom + 8 - self.gap_top[-1],
                     "rounded=0;html=1;fillColor=#f4f6f9;strokeColor=none;")
            page.box(f"e2e-tier-{c}", label(f"**{name}**"), self.col_x[c], self.gap_top[-1] + 4, E2E_BW, 40,
                     "text;html=1;align=center;verticalAlign=middle;whiteSpace=wrap;fontSize=14;")
        if self.band < self.n_rows:
            band_top = self.gap_top[self.band - 1] + self.gap_h[self.band - 1] - 8
            page.box("e2e-band", "", MARGIN - 8, band_top, right - MARGIN + 16, self.bottom - band_top - self.gap_h[self.n_rows - 1] + 16,
                     "rounded=0;html=1;fillColor=#fbf8ee;strokeColor=none;")
            page.box("e2e-band-head", label(f"**{self.profile.band_title}**"), self.col_x[0], self.gap_top[self.band - 1] + 6, E2E_BW, 30,
                     "text;html=1;align=left;verticalAlign=middle;fontSize=14;")

    def _arrows(self, page: Page) -> None:
        """Per family layer: its connectors, then its step arrows; then every step arrow's label.

        Args:
            page: the page.
        """
        colour = {fam: col for fam, _n, col, _ids in self.groups}
        per_flow = self.profile.look.get("e2e_layers", "family") == "flow"
        for fam, name, _col, _ids in self.groups:
            page.add_layer(f"e2e-L-{fam}", f"Flow {name}" if per_flow else f"Family: {name}")
        for link in self.links:   # hover text and tags on every arrow and connector, and on each arrow's x.y label
            page.tips[link.cid], page.tags[link.cid] = link.tip, link.tags
        width = self.profile.look.get("connector_width", 1.25)
        for fam, _name, _col, _ids in self.groups:
            for link in (x for x in self.links if x.family == fam and x.klass == "thin"):
                page.route(link.cid, f"e2e-c-{link.src}", f"e2e-c-{link.dst}", self.pts[link.cid],
                           f"edgeStyle=none;rounded=1;html=1;strokeColor={colour[fam]};strokeWidth={width:g};dashed=1;dashPattern=8 4;endArrow=oval;endFill=1;endSize=5;",
                           klass="thin", layer=f"e2e-L-{fam}")
            for link in (x for x in self.links if x.family == fam and x.klass == "thick"):
                page.route(link.cid, f"e2e-c-{link.src}", f"e2e-c-{link.dst}", self.pts[link.cid],
                           f"edgeStyle=none;rounded=1;html=1;strokeColor={colour[fam]};strokeWidth=2;{ARROW_HEAD}endSize=6;"
                           f"jumpStyle=arc;jumpSize={E2E_JUMP};", klass="thick", layer=f"e2e-L-{fam}", jump=E2E_JUMP)
        for link in self.links:
            if link.klass == "thick":
                cx, cy = self._label_spot(link.cid, page)
                page.mark(f"{link.cid}-l", label(f"**{link.text}**"), cx, cy, E2E_LABEL_W, E2E_LABEL_H,
                          f"text;html=1;align=center;verticalAlign=middle;fontSize=10;fontColor={colour[link.family]};labelBackgroundColor=#ffffff;"
                          "spacing=0;", owner=link.cid, layer=f"e2e-L-{link.family}")

    def _legend(self, page: Page, right: float) -> None:
        """The family legend under the grid: a swatch and the family's flows per family, then how to read an arrow.

        Args:
            page: the page.
            right: the right edge of the last column.
        """
        y = self.bottom + 10
        per_flow = self.profile.look.get("e2e_layers", "family") == "flow"
        page.box("e2e-leg-title", label("**Legend: flows** (one colour and layer each)" if per_flow else "**Legend: flow families** (one layer each)"),
                 MARGIN, y, 600, 24, "text;html=1;align=left;fontSize=14;")
        for i, (fam, name, col, titles) in enumerate(self.groups):
            ly = y + 34 + i * 28
            page.box(f"e2e-leg-{fam}-s", "", MARGIN, ly + 10, 40, 3, f"rounded=0;html=1;fillColor={col};strokeColor=none;")
            page.box(f"e2e-leg-{fam}-t", label(f"**{name}**" if per_flow else f"**{name}:** " + "; ".join(titles)), MARGIN + 50, ly, right - MARGIN - 50, 24,
                     "text;html=1;align=left;verticalAlign=middle;fontSize=12;")
        ly = y + 34 + len(self.groups) * 28 + 6
        page.box("e2e-leg-solid", label("**Solid arrow, label x.y:** flow x (its number on the Overview) moves to the component acting in its step y; "
                                        "x.1 starts at the component the flow runs on, and a step done by the same component as the step before has no "
                                        "arrow. **Dashed line, dot end:** not a step; the flow runs on, is owned by or depends on that component. "
                                        "Hover an arrow for what happens. Arcs mark crossings."),
                 MARGIN, ly, right - MARGIN, 24, "text;html=1;align=left;verticalAlign=middle;fontSize=12;")
        used = component_shapes_used(list(self.comps.values()), self.profile)
        if used:   # the symbols the boxes use, as on a flow page
            shape_legend(page, used, MARGIN, ly + 40, "e2e")

    def page(self) -> Page:
        """Draw the page: frame, boxes, arrows and labels per family, and the legend.

        Returns:
            The page.
        """
        page = Page("end-to-end", "End-to-end flow")
        right = self.col_x[-1] + E2E_BW + (self.ch_w[-1] if self.nch >= self.ncol else 0)   # a one-column page draws its channel too
        self._frame(page, right)
        for cid, comp in self.comps.items():
            c, _r = self.cell[cid]
            top, height = self._box_span(cid)
            page.box(f"e2e-c-{cid}", label(*e2e_box_lines(comp, self.profile.look['heading_scale'])), self.col_x[c], top, E2E_BW, height,
                     comp_style(comp["kind"], self.profile, "fontSize=11;verticalAlign=middle;spacingLeft=6;spacingRight=6;" + status_style(comp)
                                + component_shape(comp, self.profile)),
                     tooltip=comp_tip(comp), solid=True, tags=comp_tags(comp, self.data["flows"]))
            person_badge(page, comp, self.profile, f"e2e-c-{cid}", self.col_x[c] + E2E_BW, top + height)
        self._arrows(page)
        self._legend(page, right)
        return page


def end_to_end_page(data: dict, profile: Profile) -> Page:
    """The End-to-end page: every component in tier columns, every flow as a coloured path, one layer per family.

    Args:
        data: the validated map.
        profile: the project's drawing profile.

    Returns:
        The page.
    """
    return EndToEnd(data, profile).page()


def e2e_untouched(data: dict, page: Page) -> list[str]:
    """Components on the End-to-end page that no path or connector reaches (there should be none).

    Args:
        data: the validated map.
        page: the End-to-end page.

    Returns:
        Their ids, in map order.
    """
    ends = {x for r in page.routes for x in (r.src, r.dst)}
    return [c["id"] for c in data["components"] if f"e2e-c-{c['id']}" not in ends]
