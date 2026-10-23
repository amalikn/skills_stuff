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
Exit: 0 when every colour is at least 4.5:1 on white, 1 when one is not, 2 on bad arguments.
Runtime: measuring 0.07 s; --suggest 10 1.8 s (measured 2026-10-23, the default palette).
"""

from __future__ import annotations

import argparse
import colorsys
import math
import re
import sys

from flowmap.profile import DISTINCT

#: The oldest Python this script runs on (stdlib only).
REQUIRES_PYTHON = (3, 11)
#: The neutral thin grey every secondary arrow uses (references/visual-style.md); new hues keep away from it.
THIN_GREY = "#4b5563"
#: Text-grade contrast on white, the skill's floor for every line colour.
MIN_CONTRAST = 4.5
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


def _linear(c: float) -> float:
    """One sRGB channel to linear light.

    Args:
        c: the channel, 0 to 1.

    Returns:
        Its linear value.
    """
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _rgb(hex_colour: str) -> list[float]:
    """Channels of a `#rrggbb` colour.

    Args:
        hex_colour: the colour.

    Returns:
        [r, g, b], each 0 to 1.
    """
    return [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]


def contrast(hex_colour: str) -> float:
    """WCAG 2 contrast ratio of a colour against white.

    Args:
        hex_colour: the colour as `#rrggbb`.

    Returns:
        The ratio, 1 to 21.
    """
    r, g, b = map(_linear, _rgb(hex_colour))
    return 1.05 / (0.2126 * r + 0.7152 * g + 0.0722 * b + 0.05)


def lab(hex_colour: str) -> tuple[float, float, float]:
    """CIE L*a*b* (D65) of a colour.

    Args:
        hex_colour: the colour as `#rrggbb`.

    Returns:
        (L, a, b).
    """
    r, g, b = map(_linear, _rgb(hex_colour))
    x, y, z = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047, 0.2126 * r + 0.7152 * g + 0.0722 * b, (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t: float) -> float:
        """The CIE L*a*b* companding function.

        Args:
            t: a channel ratio to the white point.

        Returns:
            Its companded value.
        """
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    return 116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))


def de2000(hex_a: str, hex_b: str) -> float:
    """CIEDE2000 colour difference (Sharma, Wu and Dalal's formulation).

    Args:
        hex_a: one colour as `#rrggbb`.
        hex_b: the other.

    Returns:
        The difference; about 2 is barely visible, above 10 reads as another colour.
    """
    (l1, a1, b1), (l2, a2, b2) = lab(hex_a), lab(hex_b)
    cm = (math.hypot(a1, b1) + math.hypot(a2, b2)) / 2
    g = 0.5 * (1 - math.sqrt(cm ** 7 / (cm ** 7 + 25 ** 7)))
    a1p, a2p = (1 + g) * a1, (1 + g) * a2
    c1p, c2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p, h2p = math.degrees(math.atan2(b1, a1p)) % 360, math.degrees(math.atan2(b2, a2p)) % 360
    dh = 0.0 if c1p * c2p == 0 else (h2p - h1p + 180) % 360 - 180
    dl, dc, dhh = l2 - l1, c2p - c1p, 2 * math.sqrt(c1p * c2p) * math.sin(math.radians(dh / 2))
    lm, cmp_ = (l1 + l2) / 2, (c1p + c2p) / 2
    if c1p * c2p == 0:
        hm = h1p + h2p
    else:
        hm = (h1p + h2p) / 2 if abs(h1p - h2p) <= 180 else (h1p + h2p + 360) / 2
    t = (1 - 0.17 * math.cos(math.radians(hm - 30)) + 0.24 * math.cos(math.radians(2 * hm)) + 0.32 * math.cos(math.radians(3 * hm + 6))
         - 0.2 * math.cos(math.radians(4 * hm - 63)))
    sl, sc, sh = 1 + 0.015 * (lm - 50) ** 2 / math.sqrt(20 + (lm - 50) ** 2), 1 + 0.045 * cmp_, 1 + 0.015 * cmp_ * t
    rt = -2 * math.sqrt(cmp_ ** 7 / (cmp_ ** 7 + 25 ** 7)) * math.sin(math.radians(60 * math.exp(-(((hm - 275) / 25) ** 2))))
    return math.sqrt((dl / sl) ** 2 + (dc / sc) ** 2 + (dhh / sh) ** 2 + rt * (dc / sc) * (dhh / sh))


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
    args = ap.parse_args(argv)
    rows = measure(args.palette, args.avoid)
    for i, (c, ratio, dist, near) in enumerate(rows, 1):
        print(f"{i:>2} {c}  {ratio:5.2f}:1{'  BELOW 4.5' if ratio < MIN_CONTRAST else ''}  nearest {near} at {dist:4.1f}")
    print(f"closest pair: {min(r[2] for r in rows):.1f} CIEDE2000; lowest contrast {min(r[1] for r in rows):.2f}:1")
    for c, dist, near in suggest(args.palette, args.avoid, args.suggest):
        print(f"+ {c}  {contrast(c):5.2f}:1  nearest {near} at {dist:4.1f}")
    return 1 if any(r[1] < MIN_CONTRAST for r in rows) else 0


if __name__ == "__main__":
    if sys.version_info < REQUIRES_PYTHON:
        sys.exit(f"palette_check.py needs Python {'.'.join(map(str, REQUIRES_PYTHON))} or later")
    sys.exit(main())
