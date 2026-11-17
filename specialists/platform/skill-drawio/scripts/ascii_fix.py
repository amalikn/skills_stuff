#!/usr/bin/env python3
"""Fix an existing ASCII box diagram in place: ragged right edges, borders that do not match their box, stacked boxes of uneven width, off-centre arrows.

Why: hand-drawn and hand-edited ASCII diagrams drift at their edges, and redrawing each one from a spec (`ascii_flow_render.py`) means writing the spec
first. This takes the diagram as it is (operator, 2026-11-17: "if there is an existing diagram, we can pass that diagram to the skill and it can fix it").
What it fixes, per ```text block of a Markdown file (or a whole plain-text file):
  - each standalone `+---+` box: every row padded to one width, the right edge closed, top and bottom borders redrawn to that width;
  - an arrow between two boxes joined in one column that points past them moves to their centre; one drawn inside their width stays put;
  - with --even-widths (a style choice, off by default), boxes joined by arrows in one column take one width, the widest;
  - text right of a box (an exit `--> ...`, a box beside it) keeps its column, moved only as far as the box grew.
What it does not rewrite: grids whose cells share an edge, and boxes whose left edge drifts; what the edge checker would still find is reported
(redraw those with ascii_flow_render.py).
Every fix keeps the diagram's words in the same order and never adds an edge finding, or the block is left as it was.
Run: just ascii-fix <file> [...] [--apply] [--even-widths] (this pack), or python3 <pack>/scripts/ascii_fix.py <file> [...] [--apply].
Safety: read-only by default (prints a unified diff of each fixed block); --apply writes the fixed blocks back into the same file, nothing else.
Exit: 0 nothing left to report; 1 a block holds something it would not fix (listed); 2 bad arguments or an unreadable file.
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

REQUIRES_PYTHON = (3, 11)
BORDER = re.compile(r"\+-+\+")
GRID_BORDER = re.compile(r"\+-[-+^]*-\+")  # the edge checker's border: grids and branch lines too
ARROW = re.compile(r"^(\s*)([|v^])(\s.*)?$")
WORDS = re.compile(r"[A-Za-z0-9_.]+")
PASSES = 6


def blocks(text: str, markdown: bool) -> list[tuple[int, int]]:
  """Where the diagrams are: the ```text blocks of Markdown, or the whole file.

  Args:
    text: the file's text.
    markdown: True to look for ```text fences; False to take every line.

  Returns:
    [(first content line index, end index exclusive)], 0-based over text.split("\\n").
  """
  lines = text.split("\n")
  if not markdown:
    return [(0, len(lines))]
  out, start = [], None
  for i, line in enumerate(lines):
    if start is None and line.strip().startswith("```text"):
      start = i + 1
    elif start is not None and line.strip().startswith("```"):
      out.append((start, i))
      start = None
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


def find_box(lines: list[str], r: int, a: int, b: int) -> dict | None:
  """The box whose top border runs from (r, a) to (r, b), read row by row down to its bottom border.

  Args:
    lines: the diagram.
    r: the top border's row.
    a: column of the top-left `+`.
    b: column of the top-right `+`.

  Returns:
    {"top", "bottom", "a", "rows": [(row, content, right edge column or None)], "bottom_end"}, or None when this is not a box top
    (a branch line, the bottom of a box above).
  """
  if ch(lines, r - 1, a) in "|+" or ch(lines, r + 1, a) == "v" or ch(lines, r + 1, b) == "v":
    return None
  rows = []
  for r2 in range(r + 1, len(lines)):
    line = lines[r2]
    m = GRID_BORDER.match(line, a) if ch(lines, r2, a) == "+" else None
    if m:
      if "+" in line[a + 1 : m.end() - 1] or "^" in m.group(0):
        return None  # a divider or bottom shared with a grid: not a standalone box
      return {"top": r, "bottom": r2, "a": a, "b": b, "rows": rows, "bottom_end": m.end() - 1}
    if ch(lines, r2, a) != "|":
      return {"error": f"row {r2 + 1}: the box at column {a + 1} loses its left edge (redraw it)"}
    bars = [i for i in range(a + 1, len(line)) if line[i] == "|"]
    edge = min(bars, key=lambda i: abs(i - b)) if bars else None
    rows.append((r2, line[a + 1 : edge] if edge is not None else line[a + 1 :], edge))
  return {"error": f"row {r + 1}: the box at column {a + 1} never closes"}


def place(prefix: str, tail: str, old_end: int, delta: int) -> str:
  """Put the text that followed a box's right edge back at its own column, moved by how far the box grew.

  Args:
    prefix: the rebuilt line up to and including the box's right edge.
    tail: what followed the old right edge.
    old_end: column of the old right edge.
    delta: how far the box's right edge moved (new minus the top border's old edge).

  Returns:
    The full line, trailing spaces stripped.
  """
  text = tail.lstrip(" ")
  if not text:
    return prefix
  lead = len(tail) - len(text)
  if lead == 0:
    return (prefix + text).rstrip()  # glued to the edge (`|--->|`, `|====|`): stays glued
  col = old_end + 1 + lead + delta
  return (prefix + " " * max(1, col - len(prefix)) + text).rstrip()


def boxes(lines: list[str]) -> tuple[list[dict], list[str]]:
  """Every standalone box in a diagram, and what cannot be fixed.

  Args:
    lines: the diagram.

  Returns:
    (boxes as find_box returns them, problems as messages).
  """
  found, problems = [], []
  for r, line in enumerate(lines):
    for m in BORDER.finditer(line):
      a, b = m.start(), m.end() - 1
      if ch(lines, r, a - 1) == "-" or ch(lines, r, b + 1) == "-":
        continue  # a grid cell sharing an edge: not redrawn; edge_issues reports it if broken
      box = find_box(lines, r, a, b)
      if box is None:
        continue
      if "error" in box:
        problems.append(box["error"])
      else:
        found.append(box)
  return found, problems


def lone_arrow(line: str) -> bool:
  """Whether a line between two boxes holds one arrow and at most a label (no second arrow, no box).

  Args:
    line: one diagram line.

  Returns:
    True for a line like `     |  label`, `     v` or `     ^`.
  """
  m = ARROW.match(line)
  return bool(m) and not re.search(r"(^|\s)[|v^+](\s|$)", m.group(3) or "")


def chains(found: list[dict], lines: list[str]) -> list[list[dict]]:
  """Boxes stacked in one column and joined by an arrow (only blank or single-arrow lines between), top to bottom.

  Args:
    found: the boxes.
    lines: the diagram.

  Returns:
    Each chain as a list of boxes (a lone box is a chain of one).
  """
  out: list[list[dict]] = []
  for box in sorted(found, key=lambda x: (x["a"], x["top"])):
    last = out[-1][-1] if out else None
    between = lines[last["bottom"] + 1 : box["top"]] if last and last["a"] == box["a"] and last["bottom"] < box["top"] else None
    if between and all(not x.strip() or lone_arrow(x) for x in between) and any(x.strip() for x in between):
      out[-1].append(box)
    else:
      out.append([box])
  return out


def widths(found: list[dict], lines: list[str], even: bool = False) -> dict[tuple[int, int], int]:
  """The inner width each box gets: its widest border, or its text where the text runs past it; with `even`, the widest along its chain.

  Args:
    found: the boxes.
    lines: the diagram.
    even: give boxes joined by arrows in one column one width (a style choice, off by default).

  Returns:
    {(top row, left column): inner width}.
  """
  own = {}
  for box in found:
    text = max((len(c.rstrip()) + (len(c) > len(c.rstrip())) for _, c, _ in box["rows"]), default=1)  # text, and its padding space if it had one
    own[(box["top"], box["a"])] = max(box["b"] - box["a"] - 1, box["bottom_end"] - box["a"] - 1, text)
  if not even:
    return own
  out = {}
  for chain in chains(found, lines):
    w = max(own[(x["top"], x["a"])] for x in chain)
    out.update({(x["top"], x["a"]): w for x in chain})
  return out


def redraw(lines: list[str], box: dict, w: int) -> None:
  """Rewrite one box at inner width `w`, in place.

  Args:
    lines: the diagram (changed in place).
    box: the box from find_box.
    w: the inner width.

  Returns:
    None.
  """
  a, b = box["a"], box["b"]
  delta = a + w + 1 - b
  border = "+" + "-" * w + "+"
  for r, end in ((box["top"], b), (box["bottom"], box["bottom_end"])):
    lines[r] = place(lines[r][:a] + border, lines[r][end + 1 :], end, delta)
  for r, content, edge in box["rows"]:
    tail = lines[r][edge + 1 :] if edge is not None else ""
    lines[r] = place(lines[r][:a] + "|" + content.rstrip().ljust(w) + "|", tail, edge if edge is not None else b, delta)


def centre_arrows(lines: list[str], found: list[dict], w: dict[tuple[int, int], int]) -> None:
  """Move a lone arrow between two chained boxes that points past them (outside their width) to their centre, in place.

  Args:
    lines: the diagram (changed in place).
    found: the boxes.
    w: inner widths by (top row, left column).

  Returns:
    None.
  """
  for chain in chains(found, lines):
    for upper, lower in zip(chain, chain[1:], strict=False):
      centre = upper["a"] + 1 + w[(upper["top"], upper["a"])] // 2
      for r in range(upper["bottom"] + 1, lower["top"]):
        m = ARROW.match(lines[r])
        inside = m and upper["a"] < len(m.group(1)) <= upper["a"] + w[(upper["top"], upper["a"])]
        if m and lone_arrow(lines[r]) and not inside:
          lines[r] = (" " * centre + m.group(2) + (m.group(3) or "")).rstrip()


def edge_issues(lines: list[str]) -> list[str]:
  """What the edge checker would still report: a box (or grid) whose side edges break before its bottom edge.

  Same rule as the projects' ascii_box_check.py: a top edge is a border run with no `|` or `+` above both corners; its box runs down to the next
  row holding `+` at both corners with only `-`, `+` or `^` between; a branch line (a `v` below a corner) has no bottom.

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
      for r2 in range(r + 1, len(lines)):
        if ch(lines, r2, a) == "+" and ch(lines, r2, b) == "+" and set(lines[r2][a : b + 1]) <= set("+-^"):
          break
        if ch(lines, r2, a) not in "|+" or ch(lines, r2, b) not in "|+":
          issues.append(f"row {r2 + 1}: the box at columns {a + 1}-{b + 1} loses an edge (not fixed: redraw it with ascii_flow_render.py)")
          break
      else:
        issues.append(f"row {r + 1}: the box at columns {a + 1}-{b + 1} never closes (not fixed)")
  return issues


def fix(lines: list[str], even: bool = False) -> tuple[list[str], list[str]]:
  """Fix one diagram: boxes redrawn, stray arrows centred (with `even`, chained boxes one width); repeated until nothing moves.

  Args:
    lines: the diagram.
    even: give boxes joined by arrows in one column one width.

  Returns:
    (fixed lines, problems left as messages). The input is returned unchanged when the fix would change its words or leave more edge
    findings than the drawing had.
  """
  out = list(lines)
  for _ in range(PASSES):
    before = list(out)
    found, _ = boxes(out)
    w = widths(found, out, even)
    for box in sorted(found, key=lambda x: -x["a"]):
      redraw(out, box, w[(box["top"], box["a"])])
    found, _ = boxes(out)
    centre_arrows(out, found, widths(found, out, even))
    if out == before:
      break
  if WORDS.findall("\n".join(out)) != WORDS.findall("\n".join(lines)):
    return list(lines), edge_issues(lines) + ["the fix would change the diagram's words: left as it was"]
  if len(edge_issues(out)) > len(edge_issues(lines)):
    return list(lines), edge_issues(lines) + ["the fix would break an edge the drawing had: left as it was"]
  return out, edge_issues(out)


def fix_file(path: Path, apply: bool, even: bool = False) -> int:
  """Fix every diagram in one file; print a diff, or write with apply.

  Args:
    path: a Markdown or plain-text file.
    apply: write the fixed blocks back.
    even: give boxes joined by arrows in one column one width.

  Returns:
    The number of problems left.

  Raises:
    OSError: the file cannot be read or written.
  """
  text = path.read_text(encoding="utf-8")
  lines = text.split("\n")
  left = 0
  for start, end in reversed(blocks(text, path.suffix.lower() in (".md", ".markdown"))):
    fixed, problems = fix(lines[start:end], even)
    for msg in problems:
      print(f"{path}:{start + 1}: {msg}")
    left += len(problems)
    if fixed != lines[start:end]:
      sys.stdout.writelines(difflib.unified_diff([x + "\n" for x in lines[start:end]], [x + "\n" for x in fixed], f"{path}:{start + 1}", "fixed"))
      lines[start:end] = fixed
  if apply and "\n".join(lines) != text:
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {path}")
  return left


def main(argv: list[str] | None = None) -> int:
  """Fix the named files' ASCII diagrams.

  Args:
    argv: command-line arguments (None: sys.argv).

  Returns:
    0 nothing left to report; 1 problems left; 2 bad arguments or an unreadable file.
  """
  if sys.version_info < REQUIRES_PYTHON:
    print(f"needs Python {REQUIRES_PYTHON[0]}.{REQUIRES_PYTHON[1]} or later", file=sys.stderr)
    return 2
  ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
  ap.add_argument("files", nargs="+", type=Path, help="Markdown files (each ```text block) or plain-text diagrams")
  ap.add_argument("--apply", action="store_true", help="write the fixed blocks back (default: print a diff)")
  ap.add_argument("--even-widths", action="store_true", help="also give boxes joined by arrows in one column one width (a style choice)")
  args = ap.parse_args(argv)
  left = 0
  for path in args.files:
    try:
      left += fix_file(path, args.apply, args.even_widths)
    except OSError as e:
      print(f"{path}: {e}", file=sys.stderr)
      return 2
  return 1 if left else 0


if __name__ == "__main__":
  sys.exit(main())
