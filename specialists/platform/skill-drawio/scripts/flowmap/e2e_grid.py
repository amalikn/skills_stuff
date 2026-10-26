"""The End-to-end page's grid: every component placed in a tier column and a row, every flow step planned as a link with its sides, channels and
corridor, and every coordinate (row heights, ports, channel and corridor tracks) derived from those plans. Stdlib only.

Boxes sit on one grid of rows shared by all columns, so arrows between columns run in the channels between columns and, when they skip a
column, along the corridors between rows; every arrow has its own port on each box side and its own track in every channel and corridor
(drawio.route.interval_tracks), so no arrow crosses a box or shares a run with another, and every head has a straight final run.
flowmap.e2e.EndToEnd adds the crossing-cutting local search and the drawing.

Imported, not run: `from flowmap.e2e_grid import E2EGrid, Link` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from dataclasses import dataclass

from drawio.cell import tag
from drawio.mxfile import heading, wrapped_lines
from drawio.route import interval_tracks

from .model import MARGIN, e2e_tier, flow_extras, flow_family
from .profile import Profile
from .shapes import fit_height
from .tips import connector_tip, e2e_groups, step_arrow_tip

#: Box width and least height; port spacing on a box side; distance of the first and last track from a channel's or corridor's border (the
#: head room); track spacing; least channel width and corridor height; the arcs drawn at crossings.
E2E_BW, E2E_MIN_H, E2E_PORT_SP, E2E_EDGE, E2E_SP, E2E_MIN_CH, E2E_MIN_CORR, E2E_JUMP = 210, 60, 24, 34, 24, 100, 48, 6
#: Height above the first row (tier headings) and least height of the corridor above the band below the columns (its heading).
E2E_HEAD, E2E_BAND_GAP = 56, 96
#: How far a box reaches past its outermost port; box text (font 11) characters per line in 198 px (conservative) and line height.
E2E_BOX_PAD, E2E_CHARS, E2E_LINE_H = 18, 27, 14
#: A flow.step label's size.
E2E_LABEL_W, E2E_LABEL_H = 38, 16


def e2e_box_lines(comp: dict, scale: int = 100) -> list[str]:
    """An End-to-end box's text: the bold name and, on its own line, the kind.

    Args:
        comp: the component.
        scale: the name's size, percent of the box font (`look.heading_scale`).

    Returns:
        Label lines for drawio.mxfile.label().
    """
    return [heading(f"**{comp['name']}**", scale), comp["kind"]]


def e2e_text_height(comp: dict, scale: int = 100) -> float:
    """How tall an End-to-end box must be for its text (wrapped at E2E_CHARS, plus padding), at least E2E_MIN_H.

    Args:
        comp: the component.
        scale: the name's size, percent of the box font.

    Returns:
        The height.
    """
    return max(E2E_MIN_H, 12 + sum(wrapped_lines(x.replace("*", ""), E2E_CHARS) for x in e2e_box_lines(comp, scale)) * E2E_LINE_H)


@dataclass
class Link:
    """One End-to-end arrow (a flow step) or dashed connector (a component the flow needs), with its route plan.

    Args:
        cid: the edge cell id.
        src: the source component id.
        dst: the target component id.
        klass: "thick" for a step arrow, "thin" for a connector.
        family: the flow family id.
        text: the flow.step label (empty for a connector).
        kind: "straight", "z" (one channel) or "far" (two channels and a corridor).
        exit: (channel, row, side) of the source port.
        entry: (channel, row, side) of the target port.
        gap: the corridor (the row gap below that row; -1 is above the first row) a far link runs along.
        tip: the hover text: what the step does, or why the flow needs the component.
        tags: its draw.io tags (flow, family, step-arrow or connector).
    """

    cid: str
    src: str
    dst: str
    klass: str
    family: str
    text: str = ""
    kind: str = ""
    exit: tuple = ()
    entry: tuple = ()
    gap: int = 0
    tip: str = ""
    tags: tuple = ()


class E2EGrid:
    """Places, plans and sizes the End-to-end page (flowmap.e2e.EndToEnd turns the plans into polylines)."""

    def __init__(self, data: dict, profile: Profile, numbers: dict | None = None) -> None:
        """Place every component, plan every link and size the grid.

        Args:
            data: the validated map (or one family's part of it, flowmap.e2e_family).
            profile: the project's drawing profile (tiers, band, families).
            numbers: {flow id: its number in the whole map}, so a part keeps the whole map's x of x.y; default the flows' order here.
        """
        self.data, self.profile = data, profile
        self.number = numbers or {f["id"]: i for i, f in enumerate(data["flows"], 1)}
        self.loop_reserve: dict[int, tuple[float, float]] = {}   # {gap: (room at its top, at its bottom)} kept clear for loops (flowmap.loops)
        self.comps = {c["id"]: c for c in data["components"]}
        self.ncol = len(profile.tiers)
        # Channels sit between columns; a one-column page keeps one on its right, so links inside the column still have a track (2026-10-19).
        self.nch = max(self.ncol - 1, 1)
        self.cell, self.band = self._place()
        self.groups, self.group_of = e2e_groups(data, profile, numbers)
        self.links = self._links()
        for link in self.links:
            self._plan(link)
        self._size()

    def _neighbours(self) -> dict:
        """Who each component meets in the flows (step to step, and each extra with the flow's actors), for ordering rows.

        Returns:
            {component id: neighbour ids, repeated per meeting}.
        """
        nbr: dict[str, list[str]] = {cid: [] for cid in self.comps}
        for f in self.data["flows"]:
            acts = [s["actor"] for s in f["steps"]]
            for a, b in zip(acts, acts[1:]):
                if a != b:
                    nbr[a].append(b)
                    nbr[b].append(a)
            for o in flow_extras(f):
                nbr[o] += list(dict.fromkeys(acts))
        return nbr

    def _place(self) -> tuple[dict, int]:
        """Put each component on the grid: its tier column, a row ordered by barycentre of its neighbours; the band's components below.

        Returns:
            ({component id: (column, row)}, the first band row).
        """
        tier = {cid: e2e_tier(c, self.profile) for cid, c in self.comps.items()}
        cols = [[cid for cid in self.comps if tier[cid] == k] for k in range(self.ncol)]
        nbr = self._neighbours()
        n_rows = max(len(col) for col in cols)
        row = {cid: i for col in cols for i, cid in enumerate(col)}
        colof = {cid: k for k, col in enumerate(cols) for cid in col}
        for sweep in range(6):
            for k in (range(self.ncol) if sweep % 2 == 0 else range(self.ncol - 1, -1, -1)):
                col = cols[k]
                bary = {}
                for cid in col:
                    rs = [row[n] for n in nbr[cid] if n in row and colof[n] != k]
                    bary[cid] = sum(rs) / len(rs) if rs else row[cid]
                col.sort(key=lambda cid, bary=bary: (bary[cid], row[cid]))
                prev = -1
                for i, cid in enumerate(col):
                    r = max(prev + 1, min(int(bary[cid] + 0.5), n_rows - (len(col) - i)))
                    row[cid], prev = r, r
        cell = {cid: (colof[cid], row[cid]) for cid in colof}
        return self._place_band(cell, tier, nbr, colof, n_rows), n_rows

    def _place_band(self, cell: dict, tier: dict, nbr: dict, colof: dict, n_rows: int) -> dict:
        """Put the band's components below the columns, each in the free column nearest its neighbours' mean column.

        Args:
            cell: the placed components, extended in place.
            tier: each component's tier (None for the band).
            nbr: each component's neighbours.
            colof: each placed component's column.
            n_rows: the first band row.

        Returns:
            The cell map.
        """
        taken: set = set()
        for cid in (c for c in self.comps if tier[c] is None):
            cs = [colof[n] for n in nbr[cid] if n in colof]
            pref = int(sum(cs) / len(cs) + 0.5) if cs else 1
            band_row = n_rows
            while True:
                free = sorted((c for c in range(self.ncol) if (c, band_row) not in taken), key=lambda c, pref=pref: (abs(c - pref), c))
                if free:
                    cell[cid] = (free[0], band_row)
                    taken.add(cell[cid])
                    break
                band_row += 1
        return cell

    def _links(self) -> list:
        """Every step arrow (consecutive distinct actors, labelled flow.step) and every connector (from the flow's nearest actor to each extra;
        one per family, actor and component).

        Returns:
            The links, in map order.
        """
        links, seen, name = [], set(), {c: self.comps[c]["name"] for c in self.comps}
        for f in self.data["flows"]:
            fi = self.number[f["id"]]
            fam = self.group_of[f["id"]]
            steps = f["steps"]
            acts = [s["actor"] for s in steps]
            # x.1: the flow starts where it runs, so step 1 gets an arrow from that component (operator, 2026-10-23)
            path = ([f["runs_on"]] if f["runs_on"] != acts[0] else [acts[0]]) + acts
            stayed: list[str] = []
            for k in range(len(steps)):
                a, b, s = path[k], path[k + 1], steps[k]
                if a == b:   # same actor as the step before: no arrow (nothing moves); the next arrow's hover text names the step
                    stayed.append(f"**{fi}.{k + 1} {s['id']}:** {s['action']}")
                    continue
                tip, stayed = step_arrow_tip(f, fi, k, (name[a], name[b]), stayed), []
                links.append(Link(f"e2e-a-{f['id']}-{k + 1}", a, b, "thick", fam, f"{fi}.{k + 1}", tip=tip,
                                  tags=(tag("flow", f["id"]), tag("family", flow_family(f, self.profile)), "step-arrow")))
            for o in (x for x in flow_extras(f) if not (x == f["runs_on"] and f["runs_on"] != acts[0])):
                oc, orow = self.cell[o]
                near = min(dict.fromkeys(acts), key=lambda a, oc=oc, orow=orow: 4 * abs(self.cell[a][0] - oc) + abs(self.cell[a][1] - orow))
                if (fam, near, o) not in seen:
                    seen.add((fam, near, o))
                    users = [g for g in self.data["flows"] if self.group_of[g["id"]] == fam and o in flow_extras(g)]
                    links.append(Link(f"e2e-c-{fam}-{near}-{o}", near, o, "thin", fam, tip=connector_tip(users, name[near], name[o], o),
                                      tags=(*(tag("flow", g["id"]) for g in users), tag("family", flow_family(f, self.profile)), "connector")))
        return links

    def _plan(self, link: Link) -> None:
        """Choose a link's sides, channels and corridor.

        A link to a column on the right leaves its box's right side and enters the target's left side (the mirror for one on the left); a link
        inside one column uses the channel on its right (on its left for the last column). One channel only: straight when both boxes share a
        row, else a "z" with one track; two channels: "far", along the corridor next to the source row on the target's side.

        Args:
            link: the link; its kind, exit, entry and gap are set.
        """
        (cs, rs), (ct, rt) = self.cell[link.src], self.cell[link.dst]
        if cs == ct:
            ch = cs if cs < self.nch else cs - 1
            sd = "R" if ch == cs else "L"
            link.exit, link.entry = (ch, rs, sd), (ch, rt, sd)
        elif cs < ct:
            link.exit, link.entry = (cs, rs, "R"), (ct - 1, rt, "L")
        else:
            link.exit, link.entry = (cs - 1, rs, "L"), (ct, rt, "R")
        if link.exit[0] == link.entry[0]:
            link.kind = "straight" if rs == rt else "z"
        else:
            link.kind, link.gap = "far", (rs if rt >= rs else rs - 1)

    def _toward(self, link: Link, end: str) -> float:
        """Which row a port's arrow heads for after its stub, to order ports (arrows going up take the upper ports).

        Args:
            link: the link.
            end: "exit", "entry" or "both" (a straight link's one port).

        Returns:
            A row position (a corridor counts as half a row below its row).
        """
        if end == "both":
            return link.exit[1]
        if link.kind == "far":
            return link.gap + 0.5
        return link.entry[1] if end == "exit" else link.exit[1]

    def _pools(self) -> None:
        """The ports per (channel, row), ordered by where each arrow heads, and the row heights they need."""
        self.pools: dict[tuple[int, int], list] = {}
        for link in self.links:
            if link.kind == "straight":
                self.pools.setdefault(link.exit[:2], []).append((link.cid, "both"))
            else:
                self.pools.setdefault(link.exit[:2], []).append((link.cid, "exit"))
                self.pools.setdefault(link.entry[:2], []).append((link.cid, "entry"))
        self.by = {link.cid: link for link in self.links}
        for _key, users in self.pools.items():
            users.sort(key=lambda u: (self._toward(self.by[u[0]], u[1]), u[0]))
        self.n_rows = n_rows = max(r for _c, r in self.cell.values()) + 1
        # Ports sit E2E_PORT_SP apart around the row's middle; a row is as tall as its largest pool (each box then covers only its own ports).
        self.row_h = [max([E2E_MIN_H] + [(len(u) - 1) * E2E_PORT_SP + 2 * E2E_BOX_PAD for (c, r), u in self.pools.items() if r == row]
                          + [fit_height(self.comps[cid], self.profile, e2e_text_height(self.comps[cid], self.profile.look['heading_scale'])) for cid, (c, r) in self.cell.items() if r == row]) for row in range(n_rows)]

    def _corridors(self) -> dict:
        """Corridor tracks: a far link's horizontal run spans its two channels; links share a track when their spans leave a column between them.

        Returns:
            {corridor: track count}.
        """
        spans: dict[int, list] = {}
        for link in self.links:
            if link.kind == "far":
                lo, hi = sorted((link.exit[0], link.entry[0]))
                spans.setdefault(link.gap, []).append((lo, hi, link.cid))
        self.gtrack = {}
        gcount = {}
        for g, sp in spans.items():
            got = interval_tracks([(lo, hi + 0.5, cid) for lo, hi, cid in sp], 0.5)
            self.gtrack.update({(cid, g): t for cid, t in got.items()})
            gcount[g] = max(got.values()) + 1
        self.gslot = {g: list(range(n)) for g, n in gcount.items()}   # track -> slot, permuted by the local search
        return gcount

    def _size(self) -> None:
        """Ports per channel and row, row heights, corridor tracks and heights, channel tracks and widths, and every coordinate."""
        self._pools()
        gcount = self._corridors()
        gap_h = {}
        for g in range(-1, self.n_rows):
            need = 2 * E2E_EDGE + (gcount[g] - 1) * E2E_SP if g in gcount else 0
            least = E2E_HEAD if g == -1 else (E2E_BAND_GAP if g == self.band - 1 else E2E_MIN_CORR)
            gap_h[g] = max(least, need) + sum(self.loop_reserve.get(g, (0, 0)))
        self.gap_h = gap_h
        y = MARGIN + 70
        self.gap_top, self.row_top = {-1: y}, []
        y += gap_h[-1]
        for r in range(self.n_rows):
            self.row_top.append(y)
            y += self.row_h[r]
            self.gap_top[r] = y
            y += gap_h[r]
        self.bottom = y
        self._channels()

    def _port_y(self, cid: str, end: str) -> float:
        """A port's y: E2E_PORT_SP apart around its row's middle, in its pool's order.

        Args:
            cid: the link id.
            end: "exit" or "entry" (a straight link's port answers both).

        Returns:
            The y.
        """
        link = self.by[cid]
        key = link.exit[:2] if end == "exit" else link.entry[:2]
        users = self.pools[key]
        i = next(i for i, u in enumerate(users) if u[0] == cid and (u[1] == end or u[1] == "both"))
        r = key[1]
        return self.row_top[r] + self.row_h[r] / 2 + (i - (len(users) - 1) / 2) * E2E_PORT_SP

    def _gap_y(self, cid: str, g: int) -> float:
        """A far link's corridor track y.

        Args:
            cid: the link id.
            g: the corridor.

        Returns:
            The y.
        """
        n, (rt, rb) = len(self.gslot[g]), self.loop_reserve.get(g, (0, 0))
        slot = self.gslot[g][self.gtrack[(cid, g)]]
        return self.gap_top[g] + rt + (self.gap_h[g] - rt - rb - (n - 1) * E2E_SP) / 2 + slot * E2E_SP

    def _verticals(self, link: Link) -> list[tuple[int, float, float, str]]:
        """A link's vertical runs in channels.

        Args:
            link: the link.

        Returns:
            (channel, low y, high y, run key) per run; none for a straight link.
        """
        if link.kind == "straight":
            return []
        ye, yi = self._port_y(link.cid, "exit"), self._port_y(link.cid, "entry")
        if link.kind == "z":
            return [(link.exit[0], min(ye, yi), max(ye, yi), f"{link.cid}|z")]
        yc = self._gap_y(link.cid, link.gap)
        return [(link.exit[0], min(ye, yc), max(ye, yc), f"{link.cid}|1"), (link.entry[0], min(yc, yi), max(yc, yi), f"{link.cid}|2")]

    def _channels(self) -> None:
        """Give each vertical run a track in its channel (runs share one when E2E_SP or more apart), then size the channels and place columns."""
        runs: dict[int, list] = {}
        for link in self.links:
            for ch, lo, hi, key in self._verticals(link):
                runs.setdefault(ch, []).append((lo, hi, key))
        self.vtrack = {}
        self.vruns: dict[tuple[int, int], list] = {}
        count = {}
        for ch, sp in runs.items():
            got = interval_tracks(sp, E2E_SP)
            self.vtrack.update(got)
            count[ch] = max(got.values()) + 1
            for _lo, _hi, key in sp:
                self.vruns.setdefault((ch, got[key]), []).append(key)
        self.vslot = {ch: list(range(n)) for ch, n in count.items()}
        self.ch_w = [max(E2E_MIN_CH, 2 * E2E_EDGE + (count.get(ch, 1) - 1) * E2E_SP) for ch in range(self.nch)]
        self.col_x = [MARGIN + sum(E2E_BW + w for w in self.ch_w[:c]) for c in range(self.ncol)]
