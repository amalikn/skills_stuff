"""Arrow labels on a chart: the step pages' own bold labels, on the line, so every page reads alike (operator, 2026-11-02). Stdlib only.

Imported, not run: `from flowmap.flowchart.labels import place_labels` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.mxfile import Page

from ..routing import draw_label


def mark_size(text: str) -> tuple[float, float]:
    """The room a label needs beside an arrow, at most 16 characters a line, for column gaps.

    Args:
        text: the label.

    Returns:
        (width, height).
    """
    lines = max(1, -(-len(text) // 16))
    return min(len(text), 16) * 9 + 8, 18 * lines + 2


def place_labels(page: Page, items: list[tuple]) -> None:
    """Add every label, once every arrow is drawn.

    Args:
        page: the page.
        items: (edge id, text, polyline, colour) per label.
    """
    for cid, text, pts, colour in items:
        draw_label(page, cid, pts, text, colour)
