"""The End-to-end page: every component in tier columns and every flow drawn as a coloured path through its step actors, one draw.io layer per
flow family. Stdlib only.

flowmap.e2e_grid.E2EGrid places and plans everything; EndToEnd adds a crossing-cutting local search (swap neighbouring tracks in each channel
and corridor, and neighbouring ports in each pool, keeping a swap only when crossings drop and shared tracks stay apart), then draws: column
stripes and headings, the band below, boxes, per family its dashed connectors, step arrows and flow.step labels, and the legend.

Imported, not run: `from flowmap.e2e import end_to_end_page` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from dataclasses import replace

from drawio.mxfile import ARROW_HEAD, BLANK, HEADER_STYLE, Page, header_height, label
from drawio.route import count_crossings, oriented

from .e2e_grid import E2E_BAND_HEAD, E2E_BOX_PAD, E2E_BW, E2E_JUMP, E2E_SP, E2E_TIER_HEAD, E2EGrid, Link, e2e_box_lines, e2e_text_height
from .step_labels import label_setup, label_spot, legend_fit, legend_text, step_label, total_words
from .map_parts import flow_numbers, narrowed, shared_part
from .model import MARGIN, comp_style, status_style
from .shapes import component_shape, component_shapes_used, fit_height, person_badge, shape_legend
from .profile import Profile
from .loops import draw_loops, plan_loops
from .crossing_search import improve, swapper
from .isolate import BOX_TAG, E2E_DIMMED, LEGEND_TAG, dim_level, group_tag, isolate_link
from .tips import comp_tags, comp_tip


class EndToEnd(E2EGrid):
    """Lays out, improves and draws the End-to-end page."""

    def __init__(self, data: dict, profile: Profile, numbers: dict | None = None) -> None:
        """Place, plan and size (E2EGrid), then improve track and port orders to cut crossings.

        Args:
            data: the validated map, or one family's part of it (flowmap.e2e_family).
            profile: the project's drawing profile.
            numbers: {flow id: its number in the whole map} for a part; default the flows' order.
        """
        super().__init__(data, profile, numbers)
        self.title = "**End-to-end flow: every component, every flow**"
        self.label_font, self.step_total, self.n_steps, self.label_w, self.label_h = label_setup(self.links, data, self.number, profile)
        self._improve()
        self.loops = plan_loops(self)   # with look.e2e_loops: steps that stay in a box, as loops on it (may widen gaps and lay out again)

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
        if link.kind in ("z", "row"):   # a row link drops in its first channel and runs along the target's row
            x = self._track_x(link.exit[0], f"{link.cid}|z" if link.kind == "z" else f"{link.cid}|1")
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
        memo, shape = self.pair_memo, self.shape
        for a in cids:
            sa, (ax0, ay0, ax1, ay1), ka = self.segs[a], self.bbox[a], shape[a]
            for b, sb in self.segs.items():
                if b == a or (b in cids and b < a):
                    continue
                bx0, by0, bx1, by1 = self.bbox[b]
                if bx0 > ax1 or ax0 > bx1 or by0 > ay1 or ay0 > by1:   # boxes apart: no crossing (keeps the search fast)
                    continue
                key = (ka, shape[b])   # an undone trial redraws the same polylines, so most pairs were counted before
                c = memo.get(key)
                if c is None:
                    c = memo[key] = count_crossings(sa, sb)
                n += c
        return n

    def _refresh(self, cids: set) -> None:
        """Recompute the polylines of the given links and their vertical runs.

        Args:
            cids: the link ids.
        """
        for cid in cids:
            self.pts[cid] = self.points(self.by[cid])
            self.segs[cid] = oriented(self.pts[cid])
            xs, ys = [x for x, _y in self.pts[cid]], [y for _x, y in self.pts[cid]]
            self.bbox[cid] = (min(xs), min(ys), max(xs), max(ys))
            self.shape[cid] = self.shape_ids.setdefault(tuple(self.pts[cid]), len(self.shape_ids))   # one id per distinct polyline
            for key in self.span_keys.pop(cid, ()):   # the vertical runs _runs_ok reads, kept with the polylines (2026-10-29: 2.6 s on UNC)
                del self.spans[key]
            runs = self._verticals(self.by[cid])
            self.spans.update((key, (ch, lo, hi)) for ch, lo, hi, key in runs)
            self.span_keys[cid] = [key for _ch, _lo, _hi, key in runs]

    def _runs_ok(self, cids: set) -> bool:
        """Whether the given links' vertical runs still keep E2E_SP from every other run sharing their track (ports moved).

        Args:
            cids: the link ids whose ports moved.

        Returns:
            True when every shared track keeps its separation.
        """
        spans = self.spans   # kept current by _refresh
        for cid in cids:
            for ch, lo, hi, key in self._verticals(self.by[cid]):
                for other in self.vruns[(ch, self.vtrack[key])]:
                    if other != key and other in spans:   # a row link's second run is gone while its track stays
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
                if self._try(swapper(slots, ta, tb), cids, check_runs):
                    changed = True
                    inv = {s2: t for t, s2 in enumerate(slots)}
        return changed

    def _improve(self) -> None:
        """Cut crossings by local search (flowmap.crossing_search.improve: plain swaps, and joint port-and-track moves, best of both kept)."""
        improve(self)

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
        head = [self.title, BLANK,
                f"Generated from {self.profile.map} by `{self.profile.command}`; do not edit.", BLANK,
                "**Paths:** each flow is a path through the components that act in its steps, coloured by "
                + ("flow." if self.profile.look.get("e2e_layers", "family") == "flow" else "family."),
                (f"**Arrow labels:** {total_words(self.step_total)} = flow x, step y of its n steps (the step the arrow leads into, numbered as on the "
                 f"flow's page); {'a loop on a box' if self.loops else 'a number with no arrow'} is a step done by the same component as the step before. Hover an arrow for the step."
                 if self.step_total else
                 "**Arrow labels:** x.y = flow x, step y (the step the arrow leads into, numbered as on the flow's page). Hover an arrow for the step."),
                "**Dashed lines:** not steps; a component the flow runs on, is owned by or depends on, joined to the flow's nearest actor.",
                "**Layers panel:** hide or show each " + ("flow." if self.profile.look.get("e2e_layers", "family") == "flow" else "family."), BLANK, "[back to Overview]"]
        head_h = header_height(head, right - MARGIN, 60)   # grows upward from its old bottom, so the layout below stays put
        page.box("e2e-title", label(*head), MARGIN, MARGIN + 60 - head_h, right - MARGIN, head_h,
                 HEADER_STYLE, link="data:page/id,overview")
        last_tier_bottom = self.row_top[self.band - 1] + self.row_h[self.band - 1]
        for c, (name, _groups) in enumerate(self.profile.tiers):
            page.box(f"e2e-stripe-{c}", "", self.col_x[c] - 8, self.gap_top[-1], E2E_BW + 16, last_tier_bottom + 8 - self.gap_top[-1],
                     "rounded=0;html=1;fillColor=#f4f6f9;strokeColor=none;")
            page.box(f"e2e-tier-{c}", label(f"**{name}**"), self.col_x[c], self.gap_top[-1] + E2E_TIER_HEAD[0], E2E_BW, E2E_TIER_HEAD[1],
                     "text;html=1;align=center;verticalAlign=middle;whiteSpace=wrap;fontSize=14;")
        if self.band < self.n_rows:
            band_top = self.gap_top[self.band - 1] + self.gap_h[self.band - 1] - 8
            page.box("e2e-band", "", MARGIN - 8, band_top, right - MARGIN + 16, self.bottom - band_top - self.gap_h[self.n_rows - 1] + 16,
                     "rounded=0;html=1;fillColor=#fbf8ee;strokeColor=none;")
            page.box("e2e-band-head", label(f"**{self.profile.band_title}**"), self.col_x[0], self.gap_top[self.band - 1] + E2E_BAND_HEAD[0],
                     E2E_BW, E2E_BAND_HEAD[1],
                     "text;html=1;align=left;verticalAlign=middle;fontSize=14;")

    def _arrows(self, page: Page) -> None:
        """Per family layer: its connectors, then its step arrows; then every step arrow's label.

        Args:
            page: the page.
        """
        colour = {fam: col for fam, _n, col, _ids in self.groups}
        per_flow = self.profile.look.get("e2e_layers", "family") == "flow"
        dim, self.group_index = dim_level(self.profile.look), {g[0]: i for i, g in enumerate(self.groups)}
        for fam, name, _col, _ids in self.groups:   # locked when clicks isolate a flow: the editor runs a link on a click only there
            page.add_layer(f"e2e-L-{fam}", f"Flow {name}" if per_flow else f"Family: {name}", locked=dim is not None)
        for link in self.links:   # hover text and tags on every arrow and connector, and on each arrow's x.y label
            page.tips[link.cid], page.tags[link.cid] = link.tip.replace("(no arrow)", "(a loop on it)" if self.loops else "(no arrow)"), link.tags
            if dim is not None:   # one click shows that flow alone, a second click all flows (operator, 2026-10-26)
                page.links[link.cid] = isolate_link(self.group_index[link.family], E2E_DIMMED, group_tag(self.profile.look, link.family), dim)
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
        draw_loops(self, page, colour, dim)   # before the arrow labels, which then keep clear of loops and their labels
        for link in self.links:
            if link.klass == "thick":
                cx, cy = label_spot(link.cid, {**self.pts, **{lp.cid: lp.pts for lp in self.loops}}, page, self.label_w, self.label_h)
                page.mark(f"{link.cid}-l", step_label(link.text, self.n_steps[link.text.split('.')[0]], self.step_total), cx, cy, self.label_w, self.label_h,
                          f"text;html=1;align=center;verticalAlign=middle;fontSize={self.label_font:g};fontColor={colour[link.family]};labelBackgroundColor=#ffffff;"
                          "spacing=0;", owner=link.cid, layer=f"e2e-L-{link.family}")

    def _legend(self, page: Page, right: float) -> None:
        """The family legend under the grid: a swatch and the family's flows per family, then how to read an arrow.

        Args:
            page: the page.
            right: the right edge of the last column.
        """
        y = self.bottom + 10
        per_flow = self.profile.look.get("e2e_layers", "family") == "flow"
        total = self.step_total
        count = {f["title"]: f" ({len(f['steps'])} step{'' if len(f['steps']) == 1 else 's'})" if total else "" for f in self.data["flows"]}   # legend step counts (2026-10-26)
        page.box("e2e-leg-title", label("**Legend: flows** (one colour and layer each)" if per_flow else "**Legend: flow families** (one layer each)"),
                 MARGIN, y, 600, 24, "text;html=1;align=left;fontSize=14;")
        dim, leg = dim_level(self.profile.look), "1"
        if dim is not None:   # rows on a locked layer, so a click runs there
            leg = "e2e-L-legend"
            page.add_layer(leg, "Legend (click a row)", locked=True)
        for i, (fam, name, col, titles) in enumerate(self.groups):
            ly, gtag = y + 34 + i * 28, group_tag(self.profile.look, fam)
            iso = {} if dim is None else {"tags": (gtag, LEGEND_TAG), "link": isolate_link(i, E2E_DIMMED, gtag, dim)}
            page.box(f"e2e-leg-{fam}-s", "", MARGIN, ly + 10, 40, 3, f"rounded=0;html=1;fillColor={col};strokeColor=none;", layer=leg, **iso)
            text = f"**{name}**{count[titles[0]]}" if per_flow else f"**{name}:** " + "; ".join(t + count[t] for t in titles)
            page.box(f"e2e-leg-{fam}-t", label(text), MARGIN + 50, ly, right - MARGIN - 50, 24,
                     "text;html=1;align=left;verticalAlign=middle;fontSize=12;", layer=leg, **iso)
        ly = y + 34 + len(self.groups) * 28 + 6
        text = legend_text(self.step_total, bool(self.loops), dim is not None)
        wrap, h = legend_fit(text, right - MARGIN)
        page.box("e2e-leg-solid", label(text), MARGIN, ly, right - MARGIN, h, f"text;html=1;{wrap}align=left;verticalAlign=middle;fontSize=12;")
        used = component_shapes_used(list(self.comps.values()), self.profile)
        if used:   # the symbols the boxes use, as on a flow page
            shape_legend(page, used, MARGIN, ly + h + 16, "e2e")

    def page(self, page_id: str = "end-to-end", name: str = "") -> Page:
        """Draw the page: frame, boxes, arrows and labels per family, and the legend.

        Args:
            page_id: the diagram id (a family page passes its own).
            name: the tab name; default "<look.e2e_tab> flow".

        Returns:
            The page.
        """
        page = Page(page_id, name or f"{self.profile.look.get('e2e_tab', 'End-to-end')} flow")
        right = self.col_x[-1] + E2E_BW + (self.ch_w[-1] if self.nch >= self.ncol else 0)   # a one-column page draws its channel too
        self._frame(page, right)
        for cid, comp in self.comps.items():
            c, _r = self.cell[cid]
            top, height = self._box_span(cid)
            page.box(f"e2e-c-{cid}", label(*e2e_box_lines(comp, self.profile.look['heading_scale'])), self.col_x[c], top, E2E_BW, height,
                     comp_style(comp["kind"], self.profile, "fontSize=11;verticalAlign=middle;spacingLeft=6;spacingRight=6;" + status_style(comp)
                                + component_shape(comp, self.profile)),
                     tooltip=comp_tip(comp), solid=True,
                     tags=comp_tags(comp, self.data["flows"]) + ((BOX_TAG,) if dim_level(self.profile.look) is not None else ()))
            person_badge(page, comp, self.profile, f"e2e-c-{cid}", self.col_x[c] + E2E_BW, top + height)
        self._arrows(page)
        self._legend(page, right)
        return page


def routed_e2e(data: dict, profile: Profile, numbers: dict | None = None) -> EndToEnd:
    """An End-to-end page laid out and improved; with `look.e2e_row_search` the searched column order is kept only when its real routes
    cross less than the barycentre order's (its grid estimate made two UNC pages worse, 2026-10-29).

    Args:
        data: the validated map, or one family's part of it.
        profile: the drawing profile.
        numbers: {flow id: its number in the whole map} for a part; default the flows' order.

    Returns:
        The page model to draw.
    """
    searched = EndToEnd(data, profile, numbers)
    if not profile.look.get("e2e_row_search"):
        return searched
    plain = EndToEnd(data, replace(profile, look={**profile.look, "e2e_row_search": False}), numbers)
    plain.profile = profile   # the order was the only difference; draw with the map's own look
    return searched if searched._crossings(set(searched.segs)) < plain._crossings(set(plain.segs)) else plain


def end_to_end_page(data: dict, profile: Profile) -> Page:
    """The End-to-end page: every component in tier columns, every flow as a coloured path, one layer per family; a family with `own_page`
    is left off (flowmap.e2e_family draws it alone) and the rest are numbered among themselves (flowmap.map_parts.flow_numbers).

    Args:
        data: the validated map.
        profile: the project's drawing profile.

    Returns:
        The page.
    """
    part = shared_part(data, profile)
    if part is data:
        return routed_e2e(data, profile).page()
    numbers = flow_numbers(data, profile)
    e2e = routed_e2e(part, narrowed(profile, part["components"]), {f["id"]: numbers[f["id"]] for f in part["flows"]})   # no empty column
    e2e.title = "**End-to-end flow: every component, every shared flow** (a family with its own page is drawn only there)"
    return e2e.page()


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
