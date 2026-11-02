"""The bands behind a swimlane page: one per actor, its name at the top. Stdlib only.

Imported, not run: `from flowmap.flowchart.lanes import draw_lanes` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.mxfile import Page, label

from .route import CHANNEL

#: A swimlane's heading height.
LANE_HEAD = 30


def draw_lanes(page: Page, chart: object, ys: dict) -> None:
    """The vertical swimlanes behind the chart: a band per actor, its name at the top, shaded by turns; the last band also holds the arrows back.

    Args:
        page: the page.
        chart: the chart.
        ys: _rows()'s result.
    """
    fid = chart.flow["id"]
    top, bottom = ys["top"][0] - LANE_HEAD - 8, ys["bottom"]
    ends = [chart.col_left[c] for c in chart.first_col[1:-1]] + [chart.channel_x + CHANNEL * len(chart.channels)]
    for k, actor in enumerate(chart.actors):
        left, right = chart.col_left[chart.first_col[k]], ends[k]
        fill, line = ("#ffffff", "#000000") if chart.bpmn else ("#eef2f6" if k % 2 == 0 else "#f8fafc", "none")
        page.box(f"{fid}-lane-{k}", "", left, top, right - left, bottom - top, f"rounded=0;html=1;fillColor={fill};strokeColor={line};")
        page.box(f"{fid}-lane-head-{k}", label(f"**{chart.comps[actor]['name']}**"), left, top, right - left, LANE_HEAD,
                 f"rounded=0;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={line};fontSize=12;fontColor=#1f3a5f;")
