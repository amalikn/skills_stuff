"""End-to-end step arrow labels: their text (x.y, and the flow's step count with `look.e2e_step_total`), their size, and the spots tried on a
run. Stdlib only.

Why (operator, 2026-10-26): a reader tracing one flow on the End-to-end page could not tell how many steps it has, nor that a skipped number is
a step done by the same component (no arrow). The count is written after x.y as a subscript (`sub`, the default form), a superscript (`sup`)
or `/n` (`slash`); the label font is `look.e2e_label_font`. A label must touch no other run and tracks are 24 px apart, so labels are sized
from the font's advance widths and wider ones get a finer scan along every run.

Imported, not run: `from flowmap.step_labels import step_label` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

from drawio.audit import rects_overlap, seg_hits_rect, segments
from drawio.mxfile import Page, Point, label

from .e2e_grid import E2E_LABEL_H, E2E_LABEL_W, Link
from .profile import Profile

#: How `look.e2e_step_total` writes a flow's step count n after x.y: "sub" (x.y with n as a subscript), "sup" (superscript), "slash" (x.y/n).
STEP_TOTAL_STYLES = ("sub", "sup", "slash")
#: A subscript or superscript is drawn at about this fraction of the label font.
SCRIPT_SCALE = 0.75
#: Space added to a label's text width: 2 px a side keeps a label that fits between two tracks 24 apart (E2E_SP) clear of both.
LABEL_PAD = 4


def em_width(text: str) -> float:
    """A bold label's width in em: Helvetica bold advance widths, a digit 0.556, "." and "/" 0.278 (any other character counts as a digit).

    Args:
        text: the label text.

    Returns:
        The width in em.
    """
    return sum(0.278 if ch in "./" else 0.556 for ch in text)


def e2e_label_size(texts: list[tuple[str, str]], font: float, total: str | None) -> tuple[float, float]:
    """The size of every step arrow's label on a page: wide enough for the longest one at this font, never under the defaults.

    Args:
        texts: (x.y, n) per label; n is ignored when total is None.
        font: the label font size in points.
        total: how n is written (STEP_TOTAL_STYLES), or None for x.y alone.

    Returns:
        (width, height); the defaults (38, 16) at font 10 with x.y labels, so a drawing without the new keys stays byte-identical.
    """
    longest = max((label_width(xy, n, font, total) for xy, n in texts), default=0.0)
    return max(E2E_LABEL_W, round(longest) + LABEL_PAD), max(E2E_LABEL_H, font + 6)


def label_width(xy: str, n: str, font: float, total: str | None) -> float:
    """One step arrow label's text width in points.

    Args:
        xy: the x.y text.
        n: the flow's step count.
        font: the label font size in points.
        total: how n is written (STEP_TOTAL_STYLES), or None for x.y alone.

    Returns:
        The width.
    """
    if total == "slash":
        return em_width(f"{xy}/{n}") * font
    return (em_width(xy) + (em_width(n) * SCRIPT_SCALE if total else 0)) * font


def label_spots(p1: Point, p2: Point, w: float, fine: bool) -> list[Point]:
    """Candidate label centres on one run, middle first.

    Args:
        p1: the run's start.
        p2: the run's end.
        w: the label width with its margin.
        fine: False for the nine fixed fractions on runs at least two labels long; True for every few pixels on any run that holds
            the label with a little to spare at each end (only tried when no fixed spot was clear).

    Returns:
        The centres, nearest the run's middle first.
    """
    length = abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
    if not fine:
        fracs = (0.5, 0.35, 0.65, 0.2, 0.8, 0.42, 0.58, 0.28, 0.72) if length >= 2 * w else ()
    else:
        room = (length - w - 16) / 2   # how far the centre can move from the middle and keep 8 px of run at each end
        if room < 0:
            return []
        offs = sorted({0.0} | {s * d for d in range(6, int(room) + 1, 6) for s in (1, -1)}, key=abs)
        fracs = tuple(0.5 + o / length for o in offs)
    return [(p1[0] + (p2[0] - p1[0]) * fr, p1[1] + (p2[1] - p1[1]) * fr) for fr in fracs]


def total_words(style: str) -> str:
    """How the header and legend name the label form when step counts are on.

    Args:
        style: one of STEP_TOTAL_STYLES.

    Returns:
        "x.y/n", or x.y with n written as a subscript or superscript.
    """
    return {"slash": "x.y/n (4.3/20: flow 4, step 3 of 20)", "sup": "x.y with n raised after it (4.3²⁰: flow 4, step 3 of 20)",
            "sub": "x.y with n lowered after it (4.3₂₀: flow 4, step 3 of 20)"}[style]


def step_label(xy: str, n: str, style: str | None) -> str:
    """A step arrow's label HTML: x.y in bold, then the flow's step count as `look.e2e_step_total` asks (subscript, superscript or /n).

    Args:
        xy: the x.y text.
        n: the flow's step count.
        style: one of STEP_TOTAL_STYLES, or None for x.y alone.

    Returns:
        The label HTML.
    """
    if style == "slash":
        return label(f"**{xy}/{n}**")
    if style in ("sub", "sup"):
        return f"<b>{xy}<{style}>{n}</{style}></b>"
    return label(f"**{xy}**")


def label_setup(links: list[Link], data: dict, number: dict, profile: Profile) -> tuple[float, str | None, dict, float, float]:
    """A page's label settings from `drawing.look`: font, step-count form, each flow's step count and the label size.

    Args:
        links: the page's links (step arrows are the "thick" ones).
        data: the validated map, or one family's part of it.
        number: {flow id: its number in the whole map}.
        profile: the drawing profile.

    Returns:
        (font, form or None, {flow number as text: step count as text}, label width, label height).
    """
    font = profile.look.get("e2e_label_font", 10)
    total = profile.look.get("e2e_step_total") or None
    style = STEP_TOTAL_STYLES[0] if total is True else total   # true means the default form, a subscript
    n_steps = {str(number[f["id"]]): str(len(f["steps"])) for f in data["flows"]}
    w, h = e2e_label_size([(x.text, n_steps[x.text.split(".")[0]]) for x in links if x.klass == "thick"], font, style)
    return font, style, n_steps, w, h


def label_spot(cid: str, pts: dict, page: Page, label_w: float, label_h: float) -> Point:
    """Where a step arrow's label goes: on one of its own runs (longest first), clear of other edges, labels and boxes.

    Args:
        cid: the link id.
        pts: {link id: its polyline} for every link on the page.
        page: the page so far (boxes and placed labels).
        label_w: the label width.
        label_h: the label height.

    Returns:
        The label centre (the longest run's middle when nothing is clear; the audit then reports it).
    """
    segs = sorted(segments(pts[cid]), key=lambda sg: -(abs(sg[0][0] - sg[1][0]) + abs(sg[0][1] - sg[1][1])))
    w, h = label_w + 4, label_h + 4
    # the nine fixed spots first (the drawing every map had before), then a finer scan and shorter runs for wider labels (2026-10-26)
    for fine in (False, True):
        for p1, p2 in segs:
            for cx, cy in label_spots(p1, p2, w, fine):
                rect = (cx - w / 2, cy - h / 2, w, h)
                if any(seg_hits_rect(u, v, rect, 0) for o, line in pts.items() if o != cid for u, v in segments(line)):
                    continue
                if any(rects_overlap(rect, m.rect) for m in page.marks) or any(rects_overlap(rect, page.rects[b]) for b in page.solid):
                    continue
                return (cx, cy)
    p1, p2 = segs[0]
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
