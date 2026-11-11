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
    """Business requirements -> technical requirements -> initiatives (the whiteboard's structure).

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
    r_ids = [p.box(f"<b>{t}</b>", 20 + k * 156, 120, 146, 40, "req") for k, t in enumerate(reqs)]
    t_ids = [p.box(t, 40 + k * 220, 300, 200, 50, "chg") for k, t in enumerate(tech)]
    i_ids = [p.box(f"<b>{t}</b>", 200 + k * 420, 500, 340, 44, kind) for k, (t, kind) in enumerate(inits)]
    links = {0: [2, 6], 1: [0, 1, 4], 2: [5, 3], 3: [0, 1, 5], 4: [4, 6], 5: [1, 2], 6: [4, 6], 7: [2, 3], 8: [2, 1], 9: [3]}
    for r, ts in links.items():
        for t in ts:
            p.edge(r_ids[r], t_ids[t], "exitX=0.5;exitY=1;entryX=0.5;entryY=0;")
    for t, i_list in {0: [0], 1: [0], 2: [1], 3: [1, 2], 4: [0], 5: [2, 0], 6: [1]}.items():
        for i in i_list:
            p.edge(t_ids[t], i_ids[i], "exitX=0.5;exitY=1;entryX=0.5;entryY=0;")
    return p


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
    """Cost per site broken into its drivers, with the steps that reduce each.

    Returns:
        The page.
    """
    p = Page("cost", "Cost drivers")
    title(p, "Cost per site, its drivers, and which steps reduce each",
          "Martin: field labour, accommodation, allowances and travel are \"where the money is\". No baseline exists yet: truck rolls a month (FD-01) and time on site (FD-02) are still open questions.", 1300)
    root = p.box("<b>Cost per site</b><br>and so the bid price", 20, 330, 200, 70, "req")
    drivers = [("Truck rolls (travel)", [("R2 updates without a visit", "smc"), ("R3, R4 self-recovery", "smc"), ("U2 remote diagnosis", "unc")]),
               ("Hours on site (field labour)", [("U3 low-touch replacement", "unc"), ("Shape A: fewer boxes to install", "lb")]),
               ("Accommodation and allowances", [("follow truck rolls and hours on site", "chg")]),
               ("Penalties and NBN scrutiny", [("U2 alerting: faults found first", "unc"), ("R2 rollback: fewer failed updates", "smc")]),
               ("Hardware per site", [("Router-only sites (small saving, Malik 10 Nov)", "lb")]),
               ("Licences and vendor cloud", [("U3, U4 own controller instead of a vendor cloud", "unc")]),
               ("NOC and support time", [("U1 one record of every device", "unc"), ("R6 updates from the controller", "smc")])]
    y = 110
    for name, steps in drivers:
        h = max(60, len(steps) * 40)
        d = p.box(f"<b>{name}</b>", 320, y + (h - 44) / 2, 260, 44, "ben")
        p.edge(root, d)
        for j, (t, kind) in enumerate(steps):
            s = p.box(t, 680, y + j * 40, 360, 34, kind)
            p.edge(s, d, "dashed=1;")
        y += h + 16
    legend(p, 20, y + 10)
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
