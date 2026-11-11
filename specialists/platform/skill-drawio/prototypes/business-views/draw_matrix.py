"""One-off: draw a requirements-by-phase roadmap matrix as a plain draw.io file, to judge whether skill-drawio needs a roadmap view.

Reads enterprise-strategy docs/flows/parts/flows-requirements.yaml (today, Phase 1, Phase 2, target per requirement) and writes one hand-made
drawing; nothing is generated afterwards. Run: python draw_matrix.py <requirements yaml> <out .drawio>

Args are positional: the requirements part and the output path.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

import yaml

COLS = [("Business requirement", 230), ("Today (perception)", 230), ("Phase 1: protect what is deployed (to Feb 2027)", 430),
        ("Phase 2: simplify each site (from Feb 2027)", 430), ("Target", 260)]
PROJECT = {"smc": ("#dae8fc", "#6c8ebf", "SMC resiliency"), "unc": ("#e1d5e7", "#9673a6", "UNC (network controller)"),
           "litebooth": ("#d5e8d4", "#82b366", "Litebooth and router-only sites"), "business": ("#fff2cc", "#d6b656", "Business decision")}
X0, Y0, HEAD_H, ITEM_H, ITEM_GAP, PAD = 20, 120, 40, 40, 6, 8


def esc(text: str) -> str:
    """XML-escape a label.

    Args:
        text: the label.

    Returns:
        The escaped text.
    """
    return html.escape(text, quote=True)


class Doc:
    """A single-page mxfile being written."""

    def __init__(self) -> None:
        """Start an empty page."""
        self.cells: list[str] = []
        self.n = 0

    def box(self, text: str, x: float, y: float, w: float, h: float, style: str) -> None:
        """Add a vertex.

        Args:
            text: its label (HTML allowed).
            x: left.
            y: top.
            w: width.
            h: height.
            style: draw.io style.
        """
        self.n += 1
        self.cells.append(f'<mxCell id="m{self.n}" value="{esc(text)}" style="{style}" vertex="1" parent="1">'
                          f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')

    def xml(self, name: str) -> str:
        """The whole file.

        Args:
            name: the page name.

        Returns:
            The mxfile text.
        """
        body = "".join(self.cells)
        return (f'<mxfile host="drawio" compressed="false"><diagram id="roadmap" name="{esc(name)}"><mxGraphModel grid="1" gridSize="10" '
                f'page="0"><root><mxCell id="0"/><mxCell id="1" parent="0"/>{body}</root></mxGraphModel></diagram></mxfile>\n')


def split(label: str) -> tuple[str, str]:
    """A step label's column and text: "Phase 1, Nov: x (U1)" -> ("p1", "Nov · x (U1)").

    Args:
        label: the step label.

    Returns:
        (column key, text for the cell).
    """
    m = re.match(r"Phase ([12])(?:-2)?(?:, ([^:]+))?: (.*)", label)   # "Phase 1-2" starts in Phase 1
    if m:
        return f"p{m.group(1)}", (f"<b>{m.group(2)}</b> · " if m.group(2) else "") + m.group(3)
    if label.startswith("Today"):
        return "today", re.sub(r"^Today( \(perception\))?: ", "", label)
    return "target", re.sub(r"^Target: ", "", label)


def main(src: Path, out: Path) -> int:
    """Draw the matrix.

    Args:
        src: flows-requirements.yaml.
        out: the drawing to write.

    Returns:
        Exit code.
    """
    flows = yaml.safe_load(src.read_text(encoding="utf-8"))
    d = Doc()
    width = sum(w for _, w in COLS)
    d.box("<b>Enterprise program: business requirements by phase</b><br>Martin, 10 Nov 2026: start from the business requirements, then what each "
          "phase delivers. Today is Martin's stated perception (\"It's all red\"). Dates: UNC and smc-resiliency plans, read 11 Nov 2026. Litebooth "
          "items are proposals. Draft for review.", X0, 20, width, 70,
          "rounded=0;whiteSpace=wrap;html=1;fillColor=#fafafa;strokeColor=#666666;align=left;verticalAlign=top;spacingLeft=8;spacingTop=4;fontSize=12;")
    x = X0
    for name, w in COLS:
        d.box(f"<b>{name}</b>", x, Y0, w, HEAD_H, "rounded=0;whiteSpace=wrap;html=1;fillColor=#333333;fontColor=#ffffff;strokeColor=#ffffff;fontSize=12;")
        x += w
    y = Y0 + HEAD_H
    for group, title in (("whiteboard", "Whiteboard requirements (10 Nov)"), ("meeting", "Also named in the meeting")):
        d.box(f"<b>{title}</b>", X0, y, width, 26, "rounded=0;whiteSpace=wrap;html=1;fillColor=#eeeeee;strokeColor=#cccccc;align=left;spacingLeft=8;fontSize=11;")
        y += 26
        for f in (f for f in flows if f["category"] == group):
            cols: dict[str, list] = {"today": [], "p1": [], "p2": [], "target": []}
            for s in f["steps"]:
                key, text = split(s["label"])
                cols[key].append((s["actor"], text))
            n = max(1, len(cols["p1"]), len(cols["p2"]))
            h = max(84, n * (ITEM_H + ITEM_GAP) + 2 * PAD - ITEM_GAP)   # room for the requirement's description
            x = X0
            d.box(f"<b>{f['title']}</b><br><font style=\"font-size:10px\">{f['purpose']}</font>", x, y, COLS[0][1], h,
                  "rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#cccccc;align=left;verticalAlign=top;spacingLeft=6;spacingTop=4;fontSize=12;")
            x += COLS[0][1]
            d.box(" ".join(t for _, t in cols["today"]), x, y, COLS[1][1], h,
                  "rounded=0;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;align=left;verticalAlign=middle;spacingLeft=6;fontSize=11;")
            x += COLS[1][1]
            for key, (_n, w) in zip(("p1", "p2"), COLS[2:4]):
                d.box("", x, y, w, h, "rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#cccccc;")
                for k, (actor, text) in enumerate(cols[key]):
                    fill, stroke, _ = PROJECT[actor]
                    dash = "dashed=1;" if actor == "litebooth" else ""
                    d.box(text, x + PAD, y + PAD + k * (ITEM_H + ITEM_GAP), w - 2 * PAD, ITEM_H,
                          f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};{dash}align=left;spacingLeft=6;fontSize=11;")
                x += w
            d.box(" ".join(t for _, t in cols["target"]), x, y, COLS[4][1], h,
                  "rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#82b366;strokeWidth=2;dashed=1;align=left;spacingLeft=6;fontSize=11;")
            y += h
    y += 16
    d.box("<b>Legend</b>", X0, y, 120, 26, "text;html=1;align=left;verticalAlign=middle;fontSize=12;")
    lx = X0 + 120
    for actor, (fill, stroke, name) in PROJECT.items():
        dash = "dashed=1;" if actor == "litebooth" else ""
        d.box(name + (" (proposal)" if actor == "litebooth" else ""), lx, y, 230, 26,
              f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};{dash}fontSize=11;")
        lx += 240
    d.box("Today: perception (red)", lx, y, 200, 26, "rounded=0;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=11;")
    d.box("Target", lx + 210, y, 120, 26, "rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#82b366;strokeWidth=2;dashed=1;fontSize=11;")
    out.write_text(d.xml("Requirements by phase"), encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]), Path(sys.argv[2])))
