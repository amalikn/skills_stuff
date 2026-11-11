"""One-off: draw five business views of the enterprise program as one hand-made draw.io file, to judge which skill-drawio should learn.

Pages: benefit dependency network, solution scorecard, requirement tree, site shapes, cost driver tree. Content is the hub's reading of
the UNC and smc-resiliency plans (read 11 Nov 2026), Martin's 10 Nov requirements and the simplified target sketch; ratings and links are
proposals for review. Nothing is generated afterwards. Run: python draw_views.py <out .drawio>
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

C = {"smc": ("#dae8fc", "#6c8ebf"), "unc": ("#e1d5e7", "#9673a6"), "lb": ("#d5e8d4", "#82b366"), "biz": ("#fff2cc", "#d6b656"),
     "chg": ("#ffffff", "#666666"), "ben": ("#f5f5f5", "#666666"), "req": ("#fff2cc", "#d6b656"), "red": ("#f8cecc", "#b85450"),
     "amb": ("#ffe6cc", "#d79b00"), "grn": ("#d5e8d4", "#82b366"), "gry": ("#eeeeee", "#999999")}
NOTE = "Draft for review: the hub's reading of the UNC and smc-resiliency plans (read 11 Nov 2026) and Martin's 10 Nov requirements."


class Page:
    """One diagram page."""

    def __init__(self, pid: str, name: str) -> None:
        """Start a page.

        Args:
            pid: page id.
            name: tab name.
        """
        self.pid, self.name, self.cells, self.n = pid, name, [], 0

    def box(self, text: str, x: float, y: float, w: float, h: float, kind: str = "chg", extra: str = "") -> str:
        """Add a box.

        Args:
            text: label, HTML allowed.
            x: left.
            y: top.
            w: width.
            h: height.
            kind: colour key in C, or "text" for a plain label.
            extra: more style.

        Returns:
            The cell id.
        """
        self.n += 1
        cid = f"{self.pid}-{self.n}"
        if kind == "text":
            style = "text;html=1;whiteSpace=wrap;align=left;verticalAlign=top;fontSize=12;"
        else:
            fill, stroke = C[kind]
            style = f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};fontSize=11;arcSize=12;"
        self.cells.append(f'<mxCell id="{cid}" value="{html.escape(text, quote=True)}" style="{style}{extra}" vertex="1" parent="1">'
                          f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return cid

    def edge(self, a: str, b: str, extra: str = "") -> None:
        """Add an arrow between two boxes; draw.io routes it.

        Args:
            a: source id.
            b: target id.
            extra: more style.
        """
        self.n += 1
        self.cells.append(f'<mxCell id="{self.pid}-{self.n}" style="edgeStyle=none;html=1;endArrow=block;endFill=1;endSize=5;strokeColor=#777777;'
                          f'{extra or "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"}" edge="1" parent="1" source="{a}" target="{b}"><mxGeometry relative="1" as="geometry"/></mxCell>')

    def route(self, a: str, b: str, pts: list, extra: str = "") -> None:
        """Add an arrow through explicit waypoints, square corners and a jump arc where it crosses another (skill-drawio's flow pages).

        Args:
            a: source id.
            b: target id.
            pts: the waypoints between the two ports, [(x, y), ...].
            extra: the port fractions and any other style.
        """
        self.n += 1
        points = "".join(f'<mxPoint x="{x:.1f}" y="{y:.1f}"/>' for x, y in pts)
        self.cells.append(f'<mxCell id="{self.pid}-{self.n}" style="edgeStyle=none;html=1;endArrow=block;endFill=1;endSize=5;strokeColor=#777777;'
                          f'jumpStyle=arc;jumpSize=8;{extra}" edge="1" parent="1" source="{a}" target="{b}"><mxGeometry relative="1" as="geometry">'
                          f'<Array as="points">{points}</Array></mxGeometry></mxCell>')

    def xml(self) -> str:
        """The page as a diagram element.

        Returns:
            XML text.
        """
        return (f'<diagram id="{self.pid}" name="{html.escape(self.name, quote=True)}"><mxGraphModel grid="1" gridSize="10" page="0"><root>'
                f'<mxCell id="0"/><mxCell id="1" parent="0"/>{"".join(self.cells)}</root></mxGraphModel></diagram>')


def title(p: Page, head: str, body: str, w: float) -> None:
    """A page title box.

    Args:
        p: the page.
        head: bold first line.
        body: the rest.
        w: width.
    """
    p.box(f"<b>{head}</b><br>{body}<br><i>{NOTE}</i>", 20, 20, w, 66, "ben", "align=left;verticalAlign=top;spacingLeft=8;fontSize=12;rounded=0;")


def benefit_network() -> Page:
    """Enablers (program steps) -> business changes -> benefits -> business requirements.

    Returns:
        The page.
    """
    p = Page("bdn", "Benefit network")
    title(p, "Benefit dependency network: program steps to business requirements",
          "Read left to right: a step enables a change in how the business works, the change brings a benefit, the benefit serves a requirement.", 1600)
    cols = [("Program steps (enablers)", 20), ("Business changes", 460), ("Benefits", 880), ("Business requirements", 1300)]
    for name, x in cols:
        p.box(f"<b>{name}</b>", x, 100, 320, 26, "text", "align=center;")
    steps = [("R2 · Nov · Pi booths: read-only image, A/B, rollback", "smc"), ("R3, R4 · Jan-Feb · hubs and x86 recover from a hang", "smc"),
             ("U1 · Nov · every device at every site visible", "unc"), ("U2 · Dec · monitoring and alerting", "unc"),
             ("U3 · Dec · box replacement without cnMaestro", "unc"), ("U4 · Jan · a second vendor in the controller", "unc"),
             ("U5-U7 · Feb-May · drift detection and firmware", "unc"), ("R4.3-R5 · Mar-Sep · one tested image per platform", "smc"),
             ("R6 · May · SMC updates from the controller", "smc"), ("Router-only sites, Litebooth (proposal)", "lb")]
    changes = ["Updates without a site visit", "Boxes recover on their own", "The NOC sees a fault before the customer calls",
               "One record of every device", "A box replaced without a vendor cloud", "Each site carries only what it needs",
               "Every box on a known, signed release"]
    benefits = ["Fewer truck rolls and field days", "Shorter outages", "Faults fixed remotely, first time", "Lower cost per site, lower bid price",
                "No lock-in to one vendor", "No drift, fewer surprises", "Less to learn, support and secure"]
    reqs = ["Performance benefits", "Robust", "Simple", "Cost savings / Competitive", "Integrity", "Availability", "Confidentiality / Security",
            "Manageable", "Proactive managed service", "Vendor-agnostic management"]
    s_ids = [p.box(t, 20, 140 + k * 56, 320, 44, kind) for k, (t, kind) in enumerate(steps)]
    c_ids = [p.box(t, 460, 160 + k * 76, 300, 44, "chg") for k, t in enumerate(changes)]
    b_ids = [p.box(t, 880, 160 + k * 76, 300, 44, "ben") for k, t in enumerate(benefits)]
    r_ids = [p.box(f"<b>{t}</b>", 1300, 140 + k * 56, 320, 44, "req") for k, t in enumerate(reqs)]
    for s, c in [(0, 0), (0, 6), (1, 1), (2, 3), (3, 2), (4, 4), (5, 4), (6, 6), (7, 6), (7, 5), (8, 0), (9, 5)]:
        p.edge(s_ids[s], c_ids[c])
    for c, b in [(0, 0), (1, 1), (1, 0), (2, 2), (2, 1), (3, 2), (3, 6), (4, 4), (4, 0), (5, 3), (5, 6), (6, 5)]:
        p.edge(c_ids[c], b_ids[b])
    for b, r in [(0, 3), (1, 5), (1, 1), (2, 8), (2, 0), (3, 3), (4, 9), (5, 4), (5, 6), (6, 2), (6, 7)]:
        p.edge(b_ids[b], r_ids[r])
    legend(p, 20, 720)
    return p


def legend(p: Page, x: float, y: float) -> None:
    """Project colour legend.

    Args:
        p: the page.
        x: left.
        y: top.
    """
    for k, (name, kind) in enumerate([("SMC resiliency", "smc"), ("UNC (network controller)", "unc"), ("Litebooth and router-only sites (proposal)", "lb"),
                                      ("Business requirement", "req")]):
        p.box(name, x + k * 250, y, 240, 26, kind)


def scorecard() -> Page:
    """Solutions x requirements, red/amber/green, today, after Phase 1, after Phase 2.

    Returns:
        The page.
    """
    p = Page("score", "Solution scorecard")
    title(p, "Every requirement for every solution: today, after Phase 1, after Phase 2",
          "Martin: \"It's not enough for one solution to deliver just some of those objectives.\" G green, A amber, R red, ? not scoped. Ratings are proposals, not measured.", 1500)
    reqs = ["Perf", "Robust", "Simple", "Cost", "Integrity", "Avail", "Security", "Manage", "Proactive", "Vendor"]
    sols = ["Raspberry Pi booths (RCT)", "Community Wi-Fi (SMC sites)", "Litebooth (new)"]
    stages = {"Today (perception)": ["RRRRRRRRRR", "RRRRRRRRRR", "??????????"],
              "After Phase 1 (Feb 2027)": ["AGRAGGAAAA", "AARRRAAAAA", "??????????"],
              "After Phase 2": ["GGAAGGGGGG", "GGGAGGGGGG", "??GG?????G"]}
    colour = {"G": "grn", "A": "amb", "R": "red", "?": "gry"}
    y = 110
    for stage, rows in stages.items():
        p.box(f"<b>{stage}</b>", 20, y, 300, 26, "text")
        for k, r in enumerate(reqs):
            p.box(f"<b>{r}</b>", 320 + k * 110, y, 106, 26, "ben", "fontSize=10;")
        y += 30
        for sol, row in zip(sols, rows):
            p.box(sol, 20, y, 296, 32, "ben", "align=left;spacingLeft=6;")
            for k, v in enumerate(row):
                p.box(f"<b>{v}</b>", 320 + k * 110, y, 106, 32, colour[v], "fontSize=12;")
            y += 36
        y += 20
    p.box("<b>Reading the ratings (proposal)</b><br>Pi booths after Phase 1: R2 brings remote updates, rollback and signed releases (Robust, Integrity, "
          "Availability green); Simple stays red until Phase 2. Community Wi-Fi after Phase 1: hubs and x86 boxes recover on their own (R3, R4) "
          "but stay edited in place until the new image (R4.3-R5), so Integrity and Simple stay red. Litebooth has no recorded scope, so only "
          "the gains it exists for (Simple, Cost, Vendor) are marked, as targets.", 20, y, 1400, 70, "text", "fontSize=11;")
    return p


def requirement_tree() -> Page:
    """Business requirements -> technical requirements -> initiatives (the whiteboard's structure), in Martin's order.

    Routing follows skill-drawio's flow pages: each line has its own port on both boxes, ordered by where its other end sits; it runs down, across on
    a horizontal track of its own in the gap, and down into its target; runs whose spans overlap never share a track. Track choice is measured, not
    first fit: a local search moves each line to the track that gives the fewest crossings (the engine's "try it, score it, keep the better"), then
    each gap is sized so tracks sit TRACK_GAP apart. A crossing that remains is drawn with a jump arc.

    Returns:
        The page.
    """
    p = Page("tree", "Requirement tree")
    title(p, "Business requirements, the technical requirements under them, and the initiatives that meet them",
          "The structure Martin drew on 10 Nov: \"Our Business Req\" on top, \"Tech Req\" underneath, then the programs.", 1560)
    reqs = ["Performance", "Robust", "Simple", "Cost / Competitive", "Integrity", "Availability", "Security", "Manageable", "Proactive", "Vendor-agnostic"]
    tech = ["T1 Remote, safe updates with rollback", "T2 Boxes recover on their own", "T3 Central visibility and alerting",
            "T4 Own controller, any vendor", "T5 One signed image per platform", "T6 Each site only what it needs", "T7 Drift and firmware under control"]
    inits = [("SMC resiliency (R1-R6)", "smc"), ("UNC (U1-U8)", "unc"), ("Litebooth and router-only sites", "lb")]
    links = {0: [2, 6], 1: [0, 1, 4], 2: [5, 3], 3: [0, 1, 5], 4: [4, 6], 5: [1, 2], 6: [4, 6], 7: [2, 3], 8: [2, 1], 9: [3]}
    impl = {0: [0], 1: [0], 2: [1], 3: [1, 2], 4: [0], 5: [2, 0], 6: [1]}
    size = {"r": (40, 146), "t": (50, 200), "i": (44, 340)}   # height, width per row
    xs = {"r": [20 + k * 156 for k in range(len(reqs))], "t": [40 + k * 220 for k in range(len(tech))], "i": [200 + k * 420 for k in range(len(inits))]}
    upper = plan_layer(xs, size, "r", "t", [(r, t) for r, ts in links.items() for t in ts])
    lower = plan_layer(xs, size, "t", "i", [(t, i) for t, il in impl.items() for i in il])
    y = {"r": 120}
    y["t"] = y["r"] + size["r"][0] + (upper[1] + 1) * TRACK_GAP
    y["i"] = y["t"] + size["t"][0] + (lower[1] + 1) * TRACK_GAP
    ids = {"r": [p.box(f"<b>{t}</b>", xs["r"][k], y["r"], size["r"][1], size["r"][0], "req") for k, t in enumerate(reqs)],
           "t": [p.box(t, xs["t"][k], y["t"], size["t"][1], size["t"][0], "chg") for k, t in enumerate(tech)],
           "i": [p.box(f"<b>{t}</b>", xs["i"][k], y["i"], size["i"][1], size["i"][0], kind) for k, (t, kind) in enumerate(inits)]}
    for (lines, _n), up, down in ((upper, "r", "t"), (lower, "t", "i")):
        gap_top = y[up] + size[up][0]
        for a, b, fo, fi, x0, x1, k in lines:
            ty = gap_top + TRACK_GAP * (k + 1)
            p.route(ids[up][a], ids[down][b], [(x0, ty), (x1, ty)], f"exitX={fo:.3f};exitY=1;entryX={fi:.3f};entryY=0;")
    return p


#: Space between two horizontal tracks in a gap, px.
TRACK_GAP = 14


def crossings(lines: list, slot: dict) -> int:
    """Crossings among square lines in one gap: a line's horizontal run against another's vertical legs.

    Args:
        lines: (a, b, fo, fi, x0, x1) per line.
        slot: track index per (a, b); a larger index is lower.

    Returns:
        The count.
    """
    n = 0
    for la in lines:
        ya, lo, hi = slot[la[:2]], min(la[4], la[5]), max(la[4], la[5])
        for lb in lines:
            if lb is la:
                continue
            yb = slot[lb[:2]]
            if lo < lb[4] < hi and yb > ya:   # b's first leg runs from the top down to its track, past a's run
                n += 1
            if lo < lb[5] < hi and yb < ya:   # b's last leg runs from its track down to the bottom, past a's run
                n += 1
    return n


def plan_layer(xs: dict, size: dict, up: str, down: str, pairs: list) -> tuple[list, int]:
    """Ports and tracks for every line between two rows of boxes.

    Args:
        xs: box left edges per row key.
        size: (height, width) per row key.
        up: the upper row's key.
        down: the lower row's key.
        pairs: (upper index, lower index) per line.

    Returns:
        ([(a, b, exit fraction, entry fraction, x0, x1, track)], tracks used).
    """
    centre = lambda row, k: xs[row][k] + size[row][1] / 2
    outs = {a: sorted((b for a2, b in pairs if a2 == a), key=lambda b: centre(down, b)) for a, _ in pairs}
    ins = {b: sorted((a for a, b2 in pairs if b2 == b), key=lambda a: centre(up, a)) for _, b in pairs}
    frac = lambda n, k: (k + 1) / (n + 1)
    lines = []
    for a, b in pairs:
        fo, fi = frac(len(outs[a]), outs[a].index(b)), frac(len(ins[b]), ins[b].index(a))
        lines.append((a, b, fo, fi, xs[up][a] + size[up][1] * fo, xs[down][b] + size[down][1] * fi))
    span = {ln[:2]: (min(ln[4], ln[5]) - 6, max(ln[4], ln[5]) + 6) for ln in lines}
    slot = {ln[:2]: k for k, ln in enumerate(lines)}   # start: one track each, then compact
    def free(key: tuple, k: int) -> bool:
        lo, hi = span[key]
        return all(slot[o] != k or hi < span[o][0] or lo > span[o][1] for o in slot if o != key)
    for _ in range(40):
        moved = False
        for ln in lines:
            key = ln[:2]
            best, best_k = (crossings(lines, slot), len(set(slot.values()))), slot[key]
            for k in range(len(lines)):
                if k == slot[key] or not free(key, k):
                    continue
                old, slot[key] = slot[key], k
                score = (crossings(lines, slot), len(set(slot.values())))
                slot[key] = old
                if score < best:
                    best, best_k = score, k
            if best_k != slot[key]:
                slot[key], moved = best_k, True
        if not moved:
            break
    used = sorted(set(slot.values()))
    rank = {k: n for n, k in enumerate(used)}
    return [ln + (rank[slot[ln[:2]]],) for ln in lines], len(used)


def site_shapes() -> Page:
    """Today's site against the two Phase 2 shapes of the simplified target sketch.

    Returns:
        The page.
    """
    p = Page("shapes", "Site shapes")
    title(p, "A site today and the two Phase 2 shapes: one box in the user's path",
          "From the simplified target sketch (6 Oct 2026; a discussion aid, every element UNVERIFIED). Which shape a product gets is decided by the router feasibility tests.", 1260)
    panels = [("Today", [("Backhaul: Sky Muster or Starlink", "ben"), ("SMC (Raspberry Pi or x86): portal, filtering, capture; edited in place, updated by visit", "red"),
                         ("Site switch", "ben"), ("Radios and APs (mostly one vendor)", "ben"), ("Users", "ben")],
               "Managed through: a vendor cloud (cnMaestro), ping bots, several consoles; a hang needs a site visit"),
              ("Shape A: router only", [("Backhaul: Sky Muster or Starlink", "ben"), ("Standard router; portal and filtering run centrally", "lb"),
                                         ("Site switch", "ben"), ("Radios and APs (any vendor by function)", "ben"), ("Users", "ben")],
               "Managed through: our own controller; remote power-cycle or watchdog. Fits when every SMC function is native or central"),
              ("Shape C: one simplified SMC", [("Backhaul: Sky Muster or Starlink", "ben"), ("One SMC image: A/B updates, rollback, watchdog", "smc"),
                                                ("Site switch", "ben"), ("Radios and APs (any vendor by function)", "ben"), ("Users", "ben")],
               "Managed through: our own controller. Fits when a required function cannot run on a router or centrally")]
    for k, (head, items, foot) in enumerate(panels):
        x = 20 + k * 420
        p.box(f"<b>{head}</b>", x, 110, 400, 30, "text", "align=center;fontSize=14;")
        ids = [p.box(t, x + 40, 150 + j * 80, 320, 54, kind) for j, (t, kind) in enumerate(items)]
        for a, b in zip(ids, ids[1:]):
            p.edge(a, b, "exitX=0.5;exitY=1;entryX=0.5;entryY=0;")
        p.box(foot, x, 560, 400, 60, "text", "fontSize=11;")
    return p


def cost_tree() -> Page:
    """Cost per site broken into its drivers, with the steps that reduce each. The root spans every driver and each driver spans its steps, so every
    line runs straight across and none meets another at an end point.

    Returns:
        The page.
    """
    p = Page("cost", "Cost drivers")
    title(p, "Cost per site, its drivers, and which steps reduce each",
          "Martin: field labour, accommodation, allowances and travel are \"where the money is\". No baseline exists yet: truck rolls a month (FD-01) and time on site (FD-02) are still open questions.", 1300)
    drivers = [("Truck rolls (travel)", [("R2 updates without a visit", "smc"), ("R3, R4 self-recovery", "smc"), ("U2 remote diagnosis", "unc")]),
               ("Hours on site (field labour)", [("U3 low-touch replacement", "unc"), ("Shape A: fewer boxes to install", "lb")]),
               ("Accommodation and allowances", [("follow truck rolls and hours on site", "chg")]),
               ("Penalties and NBN scrutiny", [("U2 alerting: faults found first", "unc"), ("R2 rollback: fewer failed updates", "smc")]),
               ("Hardware per site", [("Router-only sites (small saving, Malik 10 Nov)", "lb")]),
               ("Licences and vendor cloud", [("U3, U4 own controller instead of a vendor cloud", "unc")]),
               ("NOC and support time", [("U1 one record of every device", "unc"), ("R6 updates from the controller", "smc")])]
    top, step_h, step_gap, group_gap = 110, 34, 8, 22
    spans, y = [], top
    for _name, steps in drivers:
        h = len(steps) * (step_h + step_gap) - step_gap
        spans.append((y, h))
        y += h + group_gap
    bottom = y - group_gap
    root = p.box("<b>Cost per site</b><br>and so the bid price", 20, top, 200, bottom - top, "req")
    for (name, steps), (gy, gh) in zip(drivers, spans):
        d = p.box(f"<b>{name}</b>", 320, gy, 260, gh, "ben")
        p.edge(root, d, f"exitX=1;exitY={(gy + gh / 2 - top) / (bottom - top):.3f};entryX=0;entryY=0.5;")
        for j, (t, kind) in enumerate(steps):
            sy = gy + j * (step_h + step_gap)
            s = p.box(t, 680, sy, 360, step_h, kind)
            p.edge(s, d, f"dashed=1;exitX=0;exitY=0.5;entryX=1;entryY={(sy + step_h / 2 - gy) / gh:.3f};")
    legend(p, 20, bottom + 30)
    return p


def main(out: Path) -> int:
    """Write the five pages.

    Args:
        out: the drawing to write.

    Returns:
        Exit code.
    """
    pages = [benefit_network(), scorecard(), requirement_tree(), site_shapes(), cost_tree()]
    out.write_text('<mxfile host="drawio" compressed="false">' + "".join(p.xml() for p in pages) + "</mxfile>\n", encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
