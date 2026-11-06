#!/usr/bin/env python3
"""Measure a line-colour palette: contrast on white and how far each colour is from its nearest other (CIEDE2000); optionally suggest more.
Read-only, stdlib only.

Why (2026-10-23): the operator asked to extend `flowmap.profile.DISTINCT` past ten hues. "Distinct" has to be measured, not judged by eye:
the first ten's closest pair (green and olive) sits at 13.1 CIEDE2000, so a new hue is accepted only above that bar and at 4.5:1 or better on
white (arrow counts and step numbers are text drawn in the arrow's colour). Picking farthest-first from a grid of dark hues gave ten more at
13.8 or above; the eleventh fell to 11.9, so twenty is the ceiling at that bar.

Usage:
    palette_check.py                                  # measure DISTINCT, avoiding the thin grey #4b5563
    palette_check.py --suggest 5                      # also print five farthest-first additions
    palette_check.py --palette "#1f4e9c,#1b7a3a" --avoid "#4b5563"
    palette_check.py --map docs/flows/flows.yaml      # a map's touching flow pairs: palette order against flowmap.colours' spread (needs PyYAML)
Exit: 0 when every colour is at least 4.5:1 on white, 1 when one is not, 2 on bad arguments.
Runtime: measuring 0.07 s; --suggest 10 1.8 s (measured 2026-10-23, the default palette); --map 0.1 s for 19 flows, 0.5 s for 32 (2026-11-06).
"""

from __future__ import annotations

import argparse
import colorsys
import re
import sys

from flowmap.colour_math import contrast, de2000   # moved to the package 2026-11-06
from flowmap.colours import spread_colours, touches
from flowmap.profile import DISTINCT

#: The oldest Python this script runs on (stdlib only).
REQUIRES_PYTHON = (3, 11)
#: The neutral thin grey every secondary arrow uses (references/visual-style.md); new hues keep away from it.
THIN_GREY = "#4b5563"
#: Text-grade contrast on white, the skill's floor for every line colour.
MIN_CONTRAST = 4.5
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


def measure(palette: list[str], avoid: list[str]) -> list[tuple[str, float, float, str]]:
    """Each colour's contrast and its nearest other colour.

    Args:
        palette: the colours, in order.
        avoid: colours the palette must stay away from (counted as neighbours, not measured).

    Returns:
        [(colour, contrast on white, CIEDE2000 to nearest, that nearest colour)], in palette order.
    """
    rows = []
    for c in palette:
        others = [o for o in palette + avoid if o.lower() != c.lower()]
        near = min(others, key=lambda o, c=c: de2000(c, o))
        rows.append((c, contrast(c), de2000(c, near), near))
    return rows


def candidates() -> list[str]:
    """A grid of dark hues readable on white: every 3 degrees of hue at five lightnesses and four saturations.

    Returns:
        The `#rrggbb` colours between 4.5:1 and 12:1 on white (darker reads as black).
    """
    out = []
    for hue in range(0, 360, 3):
        for light in (0.22, 0.26, 0.30, 0.34, 0.38):
            for sat in (0.55, 0.7, 0.85, 1.0):
                c = "#%02x%02x%02x" % tuple(round(v * 255) for v in colorsys.hls_to_rgb(hue / 360, light, sat))
                if MIN_CONTRAST <= contrast(c) <= 12:
                    out.append(c)
    return out


def suggest(palette: list[str], avoid: list[str], n: int) -> list[tuple[str, float, str]]:
    """Pick n more colours farthest-first: each the candidate farthest from everything chosen so far.

    Args:
        palette: the colours already in use.
        avoid: colours to keep away from as well.
        n: how many to pick.

    Returns:
        [(colour, CIEDE2000 to its nearest, that nearest colour)], in pick order; the distances fall as the palette fills.
    """
    chosen, picks, pool = list(palette) + list(avoid), [], candidates()
    for _ in range(n):
        best = max(pool, key=lambda c: min(de2000(c, x) for x in chosen))
        near = min(chosen, key=lambda x: de2000(best, x))
        picks.append((best, de2000(best, near), near))
        chosen.append(best)
    return picks


def _colours(text: str) -> list[str]:
    """Parse a comma-separated colour list.

    Args:
        text: `#rrggbb,#rrggbb,...`.

    Returns:
        The colours.

    Raises:
        argparse.ArgumentTypeError: one is not `#rrggbb`.
    """
    out = [c.strip() for c in text.split(",") if c.strip()]
    bad = [c for c in out if not HEX.match(c)]
    if bad:
        raise argparse.ArgumentTypeError(f"not #rrggbb: {', '.join(bad)}")
    return out


def map_pairs(flows: list, palette: list[str], worst: int = 5) -> dict:
    """The closest touching flow pairs of a map under palette order and under flowmap.colours' spread (2026-11-06, the 17 and 18 olive check).

    Args:
        flows: the map's flows, in drawing order (each with `id` and `steps`).
        palette: the line colours.
        worst: how many of the closest pairs to list per assignment.

    Returns:
        {"order"|"spread": [(distance, flow number, flow number), ...] closest first}; flow numbers count from 1.
    """
    pairs = touches(flows)
    spread = spread_colours(flows, tuple(palette))
    cols = {"order": [palette[i % len(palette)] for i in range(len(flows))], "spread": [spread[f["id"]] for f in flows]}
    return {k: sorted((round(de2000(c[i], c[j]), 1), i + 1, j + 1) for (i, j) in pairs)[:worst] for k, c in cols.items()}


def _load_flows(path: str) -> list:
    """A map's flows, read with PyYAML (imported here: the rest of this script is stdlib only).

    Args:
        path: the flow map file.

    Returns:
        Its `flows` list.

    Raises:
        SystemExit: PyYAML is missing (exit 2).
    """
    try:
        import yaml
    except ImportError:
        sys.exit("--map needs PyYAML: run with the project's or the pack's venv")
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh).get("flows", [])


def main(argv: list[str] | None = None) -> int:
    """Print the measurement (and suggestions) and return the exit status.

    Args:
        argv: command-line arguments; sys.argv when None.

    Returns:
        0 when every colour is at least 4.5:1 on white, 1 otherwise.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--palette", type=_colours, default=list(DISTINCT), help="comma-separated #rrggbb; default flowmap.profile.DISTINCT")
    ap.add_argument("--avoid", type=_colours, default=[THIN_GREY], help="colours to keep away from; default the thin grey")
    ap.add_argument("--suggest", type=int, default=0, help="also pick this many farthest-first additions")
    ap.add_argument("--map", help="also list a flow map's closest touching flow pairs, palette order against the spread")
    args = ap.parse_args(argv)
    rows = measure(args.palette, args.avoid)
    for i, (c, ratio, dist, near) in enumerate(rows, 1):
        print(f"{i:>2} {c}  {ratio:5.2f}:1{'  BELOW 4.5' if ratio < MIN_CONTRAST else ''}  nearest {near} at {dist:4.1f}")
    print(f"closest pair: {min(r[2] for r in rows):.1f} CIEDE2000; lowest contrast {min(r[1] for r in rows):.2f}:1")
    for c, dist, near in suggest(args.palette, args.avoid, args.suggest):
        print(f"+ {c}  {contrast(c):5.2f}:1  nearest {near} at {dist:4.1f}")
    if args.map:
        for kind, rows_ in map_pairs(_load_flows(args.map), args.palette).items():
            print(f"{args.map} {kind}: " + ", ".join(f"{a}-{b} at {d}" for d, a, b in rows_))
    return 1 if any(r[1] < MIN_CONTRAST for r in rows) else 0


if __name__ == "__main__":
    if sys.version_info < REQUIRES_PYTHON:
        sys.exit(f"palette_check.py needs Python {'.'.join(map(str, REQUIRES_PYTHON))} or later")
    sys.exit(main())
