"""The bands behind a swimlane page, and the view that turns a chart on its side. A chart is laid out one way, top to bottom with an actor per column;
horizontal lanes suit a wide screen and are the default (operator, 2026-11-02), so View swaps x and y as it draws and every layout rule holds in both
directions. An entry ending `:vertical` in `look.swimlanes` or `look.bpmn` keeps the page upright. Stdlib only.

Imported, not run: `from flowmap.flowchart.lanes import draw_lanes` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.mxfile import Page, label

from .route import CHANNEL

#: A swimlane's heading height.
LANE_HEAD = 30


class View:
    """Where a laid-out chart lands on its page."""

    def __init__(self, page: Page, turned: bool, dx: float = 0, dy: float = 0) -> None:
        """Remember the page and the turn.

        Args:
            page: the page.
            turned: swap x and y as the chart is drawn.
            dx: added to each page x when turned.
            dy: added to each page y when turned.
        """
        self.page, self.turned, self.dx, self.dy = page, turned, dx, dy

    def rect(self, x: float, y: float, w: float, h: float) -> tuple:
        """A rectangle on the page.

        Args:
            x: left in the layout.
            y: top in the layout.
            w: width in the layout.
            h: height in the layout.

        Returns:
            (x, y, width, height) on the page.
        """
        return (y + self.dx, x + self.dy, h, w) if self.turned else (x, y, w, h)

    def points(self, pts: list) -> list:
        """A polyline on the page.

        Args:
            pts: the points in the layout.

        Returns:
            The points on the page.
        """
        return [(y + self.dx, x + self.dy) for x, y in pts] if self.turned else pts

    def box(self, cid: str, text: str, rect: tuple, style: str, **kw: object) -> None:
        """Draw a box.

        Args:
            cid: the cell id.
            text: its label.
            rect: (x, y, width, height) in the layout.
            style: the draw.io style.
            **kw: passed to Page.box.
        """
        self.page.box(cid, text, *self.rect(*rect), style, **kw)


def draw_lanes(page: View, chart: object, ys: dict) -> None:
    """The swimlanes behind the chart: a band per actor, its name at the head, shaded by turns; the last band also holds the arrows back.

    Args:
        page: the view.
        chart: the chart.
        ys: _rows()'s result.
    """
    fid = chart.flow["id"]
    top, bottom = ys["top"][0] - LANE_HEAD - 8, ys["bottom"]
    ends = [chart.col_left[c] for c in chart.first_col[1:-1]] + [chart.channel_x + CHANNEL * len(chart.channels)]
    for k, actor in enumerate(chart.actors):
        left, right = chart.col_left[chart.first_col[k]], ends[k]
        fill, line = "#eef2f6" if k % 2 == 0 else "#f8fafc", "#6b7a8c" if chart.bpmn else "none"
        page.box(f"{fid}-lane-{k}", "", (left, top, right - left, bottom - top), f"rounded=0;html=1;fillColor={fill};strokeColor={line};")
        turn = "horizontal=0;" if page.turned else ""   # a heading on the left reads up its band
        page.box(f"{fid}-lane-head-{k}", label(f"**{chart.comps[actor]['name']}**"), (left, top, right - left, LANE_HEAD),
                 f"rounded=0;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={line};fontSize=12;fontColor=#1f3a5f;{turn}")
