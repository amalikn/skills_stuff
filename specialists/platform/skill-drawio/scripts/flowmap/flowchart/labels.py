"""Place a chart's arrow labels once every arrow is drawn: each label tries its likely spots and takes the first clear of arrows, boxes and other
labels, so a dense chart needs no hand placement. Stdlib only.

Imported, not run: `from flowmap.flowchart.labels import place_labels` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.audit import rects_overlap, seg_hits_rect, segments
from drawio.mxfile import Page


def mark_size(text: str) -> tuple[float, float]:
    """A branch label's box, at most 16 characters a line.

    Args:
        text: the label.

    Returns:
        (width, height).
    """
    lines = max(1, -(-len(text) // 16))
    return min(len(text), 16) * 6 + 8, 14 * lines + 2


def candidates(pts: list, w: float, h: float, far_first: bool) -> list[tuple[float, float]]:
    """A label's centres, best first: beside where the arrow leaves, beside where it arrives, then along each horizontal run.

    Args:
        pts: the arrow's polyline.
        w: the label's width.
        h: the label's height.
        far_first: try the arrival first (an exit shared with other arrows).

    Returns:
        The centres.
    """
    (x0, y0), (x1, _y1), (xe, ye) = pts[0], pts[1], pts[-1]
    side = 1 if x1 > x0 else -1
    near = ([(x0 + side * (w / 2 + 8), y0 - h / 2 - 2), (x0 + side * (w / 2 + 8), y0 + h / 2 + 2)] if x1 != x0
            else [(x0 + w / 2 + 4, y0 + h / 2 + 3), (x0 - w / 2 - 4, y0 + h / 2 + 3)])
    far = [(xe + w / 2 + 4, ye - h / 2 - 3), (xe - w / 2 - 4, ye - h / 2 - 3)]
    runs = [((p[0] + q[0]) / 2, p[1] + dy) for p, q in segments(pts) if abs(p[1] - q[1]) < .5 and abs(p[0] - q[0]) > w for dy in (-h / 2 - 1, h / 2 + 1)]
    return (far + near if far_first else near + far) + runs


def clear(page: Page, rect: tuple, owner: str) -> bool:
    """Whether a label's box is free of other arrows, solid boxes and placed labels.

    Args:
        page: the page, with every arrow drawn.
        rect: (x, y, width, height).
        owner: the arrow it labels.

    Returns:
        True when nothing is in the way.
    """
    if any(r.cid != owner and any(seg_hits_rect(p, q, rect, 0) for p, q in segments(r.points)) for r in page.routes):
        return False
    return not any(rects_overlap(rect, page.rects[cid]) for cid in page.solid) and not any(rects_overlap(rect, m.rect) for m in page.marks)


def place_labels(page: Page, items: list[tuple]) -> None:
    """Add every label at its first clear spot, or its best spot when none is clear (the audit then reports it).

    Args:
        page: the page, with every arrow drawn.
        items: (edge id, text, polyline, style, prefer the arrival) per label.
    """
    for cid, text, pts, style, far_first in items:
        w, h = mark_size(text)
        spots = candidates(pts, w, h, far_first)
        cx, cy = next((c for c in spots if clear(page, (c[0] - w / 2, c[1] - h / 2, w, h), cid)), spots[0])
        page.mark(f"{cid}-t", text, cx, cy, w, h, style, cid)
