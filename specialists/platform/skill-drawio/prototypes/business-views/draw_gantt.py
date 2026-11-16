"""Prototype: draw the enterprise-strategy program-by-phase Gantt as a hand-built .drawio file (skill-drawio has no Gantt type).

Run: python3 draw_gantt.py OUT.drawio   (stdlib only; writes OUT.drawio, reads nothing)
Reads: nothing. Phases, tasks and dates are hardcoded in TASKS, taken by hand from enterprise-strategy
  docs/flows/parts/flows-program.yaml (plan-timeline files read 11 Nov 2026). Litebooth has no recorded date: its bar is a placeholder.
Output: one page, Nov 2026 to Sep 2027; red outline = late or at risk; dashed = proposed. Written 2026-11-11 (operator review pending).
Status: prototype, not a skill-drawio view. Not covered by tests; helpers lack Args/Returns docstrings (skill-coder) until promoted.
"""
import sys
from datetime import date
from xml.sax.saxutils import quoteattr

START, END = date(2026, 11, 1), date(2027, 9, 30)
PX = 3.0                      # pixels per day
LX, LW = 20, 380              # label column
GX = LX + LW                  # grid origin
ROW = 30
TOP = 134                     # first task row y

# (project, id label, start, end, state)  state: ok | risk | late | proposed
D = date
TASKS = [
    ("SMC resiliency", "R1 Resiliency plan agreed (13 Nov)", D(2026, 11, 9), D(2026, 11, 13), "late"),
    ("SMC resiliency", "R2 Pi booths update and roll back alone", D(2026, 11, 13), D(2026, 11, 30), "risk"),
    ("SMC resiliency", "R3 Wi-Fi hubs recover from a hang", D(2027, 1, 4), D(2027, 1, 29), "ok"),
    ("SMC resiliency", "R4 Hung x86 boxes reset (watchdog, 1+5 canary)", D(2027, 2, 1), D(2027, 2, 19), "ok"),
    ("SMC resiliency", "R4.3-R5 One tested image (hubs Apr, RCT Jul, x86 Sep)", D(2027, 3, 1), D(2027, 9, 30), "ok"),
    ("SMC resiliency", "R6 SMC updates from the controller (wk 24 May)", D(2027, 5, 24), D(2027, 5, 28), "ok"),
    ("UNC", "U1 Every device visible, red/amber/green (27 Nov)", D(2026, 11, 9), D(2026, 11, 27), "late"),
    ("UNC", "U2 Faults raise alerts (prototype 27 Nov, all 4 Dec)", D(2026, 11, 27), D(2026, 12, 4), "risk"),
    ("UNC", "U3 Box replacement without cnMaestro (18 Dec)", D(2026, 12, 7), D(2026, 12, 18), "risk"),
    ("UNC", "U4 Second vendor trial, TP-Link/MikroTik (wk 25 Jan)", D(2027, 1, 25), D(2027, 1, 29), "ok"),
    ("UNC", "U5 Configuration drift detection (Feb)", D(2027, 2, 1), D(2027, 2, 26), "ok"),
    ("UNC", "U7 Firmware for radios, routers, switches (Apr-May)", D(2027, 4, 1), D(2027, 5, 31), "ok"),
    ("Litebooth", "Router-only sites (proposal: no scope or date recorded)", D(2027, 3, 1), D(2027, 9, 30), "proposed"),
]
FILL = {"SMC resiliency": ("#DAE8FC", "#1F4E79"), "UNC": ("#D5E8D4", "#2E6B34"), "Litebooth": ("#FFF2CC", "#7A5C00")}
RED = "#B71C1C"

cells, nid = [], [1]


def add(xml):
    cells.append(xml)


def new():
    nid[0] += 1
    return f"c{nid[0]}"


def x_of(d):
    return GX + (d - START).days * PX


def box(x, y, w, h, value="", style="", vertex=True):
    add(f'<mxCell id="{new()}" value={quoteattr(value)} style={quoteattr(style)} vertex="1" parent="1">'
        f'<mxGeometry x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" as="geometry"/></mxCell>')


TXT = "text;html=0;whiteSpace=wrap;verticalAlign=middle;fontColor=#000000;fontSize=12;"
nrows = len(TASKS) + 3                      # + 3 project headers
H = TOP + nrows * ROW + 90
W = int(x_of(END)) + 60

box(LX, 20, 900, 30, "Program by phase: UNC, SMC resiliency, Litebooth (Gantt)", TXT + "align=left;fontStyle=1;fontSize=18;")
box(LX, 52, 1100, 20, "Dates from the plan-timeline files read 11 Nov 2026; Litebooth is a proposal. Source: docs/flows/parts/flows-program.yaml.",
    TXT + "align=left;fontSize=11;")

# phase band
p1e, p2s = D(2027, 2, 28), D(2027, 3, 1)
box(x_of(START), 78, x_of(p1e) - x_of(START), 22, "Phase 1: robust, monitored, remote updates (to about Feb 2027)",
    "rounded=0;fillColor=#EEEEEE;strokeColor=#333333;fontColor=#000000;fontSize=11;fontStyle=1;")
box(x_of(p2s), 78, x_of(END) - x_of(p2s), 22, "Phase 2: simpler sites, one controller for every vendor",
    "rounded=0;fillColor=#FFFFFF;strokeColor=#333333;fontColor=#000000;fontSize=11;fontStyle=1;")

# months + grid
m = D(2026, 11, 1)
gridtop, gridbot = TOP - 22, TOP + nrows * ROW
while m <= END:
    nxt = D(m.year + (m.month == 12), m.month % 12 + 1, 1)
    box(x_of(m), gridtop, x_of(min(nxt, END)) - x_of(m), 22, m.strftime("%b %y"),
        TXT + "align=center;fontSize=11;fillColor=#F5F5F5;strokeColor=#9E9E9E;")
    add(f'<mxCell id="{new()}" value="" style="endArrow=none;strokeColor=#BDBDBD;strokeWidth=1;" edge="1" parent="1">'
        f'<mxGeometry relative="1" as="geometry"><mxPoint x="{x_of(m):.1f}" y="{gridtop + 22}" as="sourcePoint"/>'
        f'<mxPoint x="{x_of(m):.1f}" y="{gridbot}" as="targetPoint"/></mxGeometry></mxCell>')
    m = nxt

# rows
y, last = TOP, None
for proj, label, s, e, st in TASKS:
    if proj != last:
        fill, stroke = FILL[proj]
        box(LX, y, GX - LX + (x_of(END) - GX), ROW - 4, proj, TXT + f"align=left;fontStyle=1;spacingLeft=6;fillColor={fill};strokeColor={stroke};")
        y += ROW
        last = proj
    fill, stroke = FILL[proj]
    box(LX, y, LW - 6, ROW - 4, label, TXT + "align=left;spacingLeft=6;fontSize=11;")
    w = max((e - s).days * PX, 12)
    if st in ("risk", "late"):
        style = f"rounded=0;fillColor={fill};strokeColor={RED};strokeWidth=3;"
    elif st == "proposed":
        style = f"rounded=0;fillColor=#FFFFFF;strokeColor={stroke};strokeWidth=2;dashed=1;dashPattern=6 4;"
    else:
        style = f"rounded=0;fillColor={fill};strokeColor={stroke};strokeWidth=2;"
    tag = {"late": "late", "risk": "at risk", "proposed": "proposed"}.get(st, "")
    box(x_of(s), y + 3, w, ROW - 10, "", style)
    if tag and st == "proposed":
        box(x_of(s) - 74, y + 2, 70, ROW - 8, tag, TXT + "align=right;fontSize=10;fontStyle=1;")
    elif tag:
        box(x_of(s) + w + 4, y + 2, 70, ROW - 8, tag, TXT + f"align=left;fontSize=10;fontColor={RED if st != 'proposed' else '#000000'};fontStyle=1;")
    y += ROW

# today + milestones
t = D(2026, 11, 11)
for d, text, col in [(t, "today 11 Nov", RED), (D(2026, 11, 13), "", None)]:
    if not col:
        continue
    add(f'<mxCell id="{new()}" value="" style="endArrow=none;strokeColor={col};strokeWidth=2;dashed=1;" edge="1" parent="1">'
        f'<mxGeometry relative="1" as="geometry"><mxPoint x="{x_of(d):.1f}" y="{gridtop}" as="sourcePoint"/>'
        f'<mxPoint x="{x_of(d):.1f}" y="{gridbot + 6}" as="targetPoint"/></mxGeometry></mxCell>')
    box(x_of(d) - 40, gridbot + 6, 80, 18, text, TXT + f"align=center;fontSize=10;fontColor={col};fontStyle=1;")
box(x_of(D(2026, 11, 13)) + 6, gridbot + 24, 260, 18, "strategy document due Fri 13 Nov", TXT + "align=left;fontSize=10;")

# legend
ly = gridbot + 52
box(LX, ly, 26, 14, "", f"fillColor=#DAE8FC;strokeColor=#1F4E79;strokeWidth=2;")
box(LX + 32, ly - 3, 90, 20, "on plan", TXT + "align=left;fontSize=11;")
box(LX + 130, ly, 26, 14, "", f"fillColor=#DAE8FC;strokeColor={RED};strokeWidth=3;")
box(LX + 162, ly - 3, 170, 20, "late or at risk (red outline)", TXT + "align=left;fontSize=11;")
box(LX + 340, ly, 26, 14, "", "fillColor=#FFFFFF;strokeColor=#7A5C00;strokeWidth=2;dashed=1;dashPattern=6 4;")
box(LX + 372, ly - 3, 300, 20, "proposed, no scope or date recorded", TXT + "align=left;fontSize=11;")

xml = (f'<mxfile host="app.diagrams.net"><diagram id="gantt1" name="Gantt: Program by phase">'
       f'<mxGraphModel dx="1400" dy="900" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" '
       f'pageScale="1" pageWidth="{W}" pageHeight="{ly + 50}" math="0" shadow="0"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
       + "".join(cells) + '</root></mxGraphModel></diagram></mxfile>')
open(sys.argv[1], "w").write(xml)
print("cells", len(cells), "size", W, ly + 50)
