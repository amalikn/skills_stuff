"""outer_channels: how many vertical channels an End-to-end page has, and which outer ones, so links inside one column run on the page's free side.

Moved out of flowmap.e2e_grid on 2026-11-07 (that module passed 400 lines when the left channel came in). Channel k sits right of column k; the last
column gets one on its right when it has in-column links (operator, 2026-10-26), and the first one on its left (operator review 2026-11-07,
smc-resiliency Testing E2E: "use the free area on the left side"). The left channel takes the last index, never -1, so ch_w[ch] and col_x stay
plain list reads. Stdlib only.

Imported, not run: `from flowmap.side_channels import outer_channels` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations


def outer_channels(ncol: int, cell: dict, links: list, look: dict) -> tuple[int, bool, int | None]:
    """The channel count and the outer channels of an End-to-end page.

    Args:
        ncol: the column count.
        cell: {component id: (column, row)}.
        links: the page's links (each has .src and .dst).
        look: the drawing look (`e2e_left_channel`: "on" by default, "off" keeps first-column links in the channel to the next column).

    Returns:
        (channel count, whether the last column has a channel on its right, the left channel's index or None).
    """
    inside = {cell[x.src][0] for x in links if cell[x.src][0] == cell[x.dst][0]}
    # Channels sit between columns; a one-column page keeps one on its right, so links inside the column still have a track (2026-10-19).
    # Links inside the last column used its left channel, shared with every arrow from the column before, while its right side stayed empty.
    nch = ncol if ncol > 1 and ncol - 1 in inside else max(ncol - 1, 1)
    right_outer = nch >= ncol
    if ncol > 1 and 0 in inside and look.get("e2e_left_channel", "on") != "off":
        return nch + 1, right_outer, nch
    return nch, right_outer, None
