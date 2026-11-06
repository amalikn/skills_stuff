#!/usr/bin/env python3
"""Colour maths for the flow map: WCAG contrast on white and CIEDE2000 distance between two `#rrggbb` colours. Stdlib only.

Moved here from scripts/palette_check.py (2026-11-06) so flowmap.colours can measure flow colours without importing a command-line script;
palette_check.py imports these names back and behaves as before.

Imported, not run: `from flowmap.colour_math import de2000` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

import math


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
