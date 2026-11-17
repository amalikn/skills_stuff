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
GRID_BORDER = re.compile(r"\+-[-+v^]*-\+")  # a border run: may carry tees (`+`) and arrows (`v`, `^`) where connectors meet it
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


ARROW_ROW = re.compile(r"^(?P<lead>\s*)(?P<src>\S.*?)\s+(?P<arrow>-+(?:[^<>|\s-][^<>|]*?-{2,})?>)\s+(?P<dst>\S.*)$")


def list_row(line: str) -> re.Match | None:
  """A row that can belong to an arrow list: one `source ---label--> target` arrow, not inside a box and not a chain of arrows.

  Args:
    line: one diagram row.

  Returns:
    The match, or None for a row with a box edge (`|`) or a second arrow in its target.
  """
  m = ARROW_ROW.match(line)
  if not m or "|" in line or re.search(r"-+>", m.group("dst")):
    return None
  return m


def align_arrows(lines: list[str]) -> list[str]:
  """Line up the targets of a list of horizontal arrows, in a copy (operator, 2026-11-17: arrowheads in one column).

  A list is two or more consecutive rows with the same indent, each `source ---label--> target`. Every target moves to the list's rightmost target column by
  lengthening the arrow's last dash run; arrows never shrink and words never change.

  Args:
    lines: the diagram.

  Returns:
    The diagram with each arrow list's targets in one column.
  """
  out = list(lines)
  r = 0
  while r < len(out):
    group = []
    while r < len(out) and (m := list_row(out[r])) and (not group or m.group("lead") == group[0][1].group("lead")):
      group.append((r, m))
      r += 1
    if len(group) < 2 or any(m.group("dst").rstrip().endswith(".") for _, m in group):
      r += 0 if group else 1
      continue  # one row is not a list; rows that end in full stops are sentences (pseudologic), not a diagram
    target = max(m.start("dst") for _, m in group)
    for row, m in group:
      grow = target - m.start("dst")
      if not grow:
        continue  # already in place: left exactly as drawn
      arrow = m.group("arrow")
      out[row] = (
        f"{m.group('lead')}{m.group('src')} {arrow[:-1]}{'-' * (grow + m.start('arrow') - len(m.group('lead') + m.group('src')) - 1)}> {m.group('dst')}"
      )
  return out


def ch(lines: list[str], r: int, c: int) -> str:
  """The character at a row and column, a space beyond the text.

  Args:
    lines: the diagram.
    r: row.
    c: column.

  Returns:
    One character.
  """
  return lines[r][c] if 0 <= r < len(lines) and 0 <= c < len(lines[r]) else " "


def edge_issues(lines: list[str]) -> list[str]:
  """What the edge checker would still report: a box (or grid) whose side edges break before its bottom edge.

  Same rule as the projects' ascii_box_check.py: a top edge is a border run with no `|` or `+` above both corners; its box runs down to the next
  row holding `+` at both corners with only `-`, `+` or `^` between; a branch line (a `v` below a corner) has no bottom. Unlike that checker, edges
  that end having held nothing between them are a fan-out branch (`+---+---+` with bare `|` legs), not a broken box.

  Args:
    lines: the diagram.

  Returns:
    One message per broken box.
  """
  issues = []
  for r, line in enumerate(lines):
    for m in GRID_BORDER.finditer(line):
      a, b = m.start(), m.end() - 1
      if ch(lines, r - 1, a) in "|+" and ch(lines, r - 1, b) in "|+" or "v" in (ch(lines, r + 1, a), ch(lines, r + 1, b)):
        continue
      held = False  # whether anything stood between the edges: a fan-out branch (`+---+---+` with bare `|` legs) holds nothing
      for r2 in range(r + 1, len(lines)):
        if ch(lines, r2, a) == "+" and ch(lines, r2, b) == "+" and set(lines[r2][a : b + 1]) <= set("+-^v"):
          break
        if ch(lines, r2, a) not in "|+" or ch(lines, r2, b) not in "|+":
          if held:
            issues.append(f"row {r2 + 1}: the box at columns {a + 1}-{b + 1} loses an edge (not fixed: redraw it with ascii_flow_render.py)")
          break
        held = held or bool(lines[r2][a + 1 : b].strip())
      else:
        issues.append(f"row {r + 1}: the box at columns {a + 1}-{b + 1} never closes (not fixed)")
  return issues
