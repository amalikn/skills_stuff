"""Checks and connector snapping for ASCII diagrams, used by ascii_fix.py (stage 1 of the ASCII plan, operator 2026-11-17: staged, snap then graph).

What it adds to ascii_fix's box repair:
  - wide characters (emoji, CJK) and tabs, which break monospace alignment: reported, never changed;
  - a connector of single-arrow rows (`|`, `v`, `^`, one per row, an optional label) that jumps a column or two between rows: snapped back into the
    column of its first row (asciiflow's idea that a glyph must line up with what it connects to, applied to plain ASCII);
  - an arrowhead `v` whose next row is a box border but not inside the box's corners: reported (it misses the box).
Ported ideas, not code: the wide-character and tab checks follow ilia-pluzhnikov/box-diagram skills/box-diagram/validate.py (MIT License, Copyright (c)
2026 Ilya P); the snap follows lewish/asciiflow client/snap.ts (MIT). Verbatim copies: documents/ascii-sources-20261117/.
Run: imported by scripts/ascii_fix.py as `ascii.checks` (`just ascii-fix`); it has no command line of its own and writes nothing.
"""

from __future__ import annotations

import re
import unicodedata

ARROW = re.compile(r"^(\s*)([|v^])(\s.*)?$")
SNAP_REACH = 2  # columns a connector row may stray from its first row and still be the same connector


def single_arrow(line: str) -> int | None:
  """The column of a row's only arrow glyph, when the row holds one arrow and at most a label.

  Args:
    line: one diagram row.

  Returns:
    The glyph's column, or None.
  """
  m = ARROW.match(line)
  if not m or re.search(r"(^|\s)[|v^+](\s|$)", m.group(3) or ""):
    return None
  return len(m.group(1))


def text_issues(lines: list[str]) -> list[str]:
  """Wide characters and tabs, which no fix can line up.

  Args:
    lines: the diagram.

  Returns:
    One message per offending row.
  """
  issues = []
  for r, line in enumerate(lines):
    wide = [c for c in line if unicodedata.east_asian_width(c) in ("W", "F")]
    if wide:
      issues.append(f"row {r + 1}: double-width character {wide[0]!r} breaks the alignment (not fixed)")
    if "\t" in line:
      issues.append(f"row {r + 1}: a tab breaks the alignment (not fixed: use spaces)")
  return issues


def snap_connectors(lines: list[str]) -> list[str]:
  """Line up a connector whose rows stray a column or two from its first row, in a copy.

  Args:
    lines: the diagram.

  Returns:
    The diagram with each straying connector row moved under the first row of its run.
  """
  out = list(lines)
  anchor = None
  for r, line in enumerate(out):
    col = single_arrow(line)
    if col is None:
      anchor = None
      continue
    if anchor is None:
      anchor = col
    elif col != anchor and abs(col - anchor) <= SNAP_REACH:
      out[r] = (" " * anchor + line.lstrip(" ")).rstrip()
    else:
      anchor = col
  return out


def arrow_issues(lines: list[str]) -> list[str]:
  """Arrowheads that point at a box border outside the box's corners.

  Args:
    lines: the diagram.

  Returns:
    One message per arrow that misses.
  """
  issues = []
  for r, line in enumerate(lines[:-1]):
    col = single_arrow(line)
    if col is None or line[col] != "v":
      continue
    below = lines[r + 1]
    runs = [m.span() for m in re.finditer(r"\+-[-+^]*-\+", below)]
    if runs and not any(a < col < b - 1 for a, b in runs):
      issues.append(f"row {r + 1}: the arrow at column {col + 1} misses the box below it (not fixed)")
  return issues
