#!/usr/bin/env python3
"""Draw ASCII flow diagrams for Markdown from a JSON spec: vertical chains of boxes with side exits, grids of cells, and parts placed side by side.

Why: ASCII is this pack's immediate documentation diagram; draw.io drawings are generated only when explicitly asked (operator 2026-11-16). UNC's
`ascii_box_render.py` draws grids only, and hand-drawn flows drifted at their edges; this pads every box to its width so an edge checker stays clean. Spec: a JSON list of parts, each one of
  {"chain": {"width": 50, "indent": 2, "steps": [{"lines": ["..."], "exit": "fails: ...", "label": "arrow label"}, ...]}}
  {"grid": {"title": "...", "rows": [[[width, ["line", ...]], ...], ...]}}
  {"box": {"width": 40, "lines": ["..."]}}
  {"text": ["verbatim line", ...]}
  {"columns": {"gap": 4, "parts": [<part>, ...]}}
Parts are stacked top to bottom; `columns` places its parts side by side.
Run: just ascii-flow-render <spec.json> (this pack), or <project venv>/bin/python <pack>/scripts/ascii_flow_render.py <spec.json>; read-only, prints the
diagram to stdout, writes nothing. Promoted from smc-resiliency 2026-11-16 (operator: a higher level than one project).
Exit: 0 drawn; 1 the spec does not fit (a line wider than its box, grid rows of unequal span); 2 bad arguments or unreadable spec.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRES_PYTHON = (3, 11)


def box(lines: list[str], width: int) -> list[str]:
  """A box whose inner width is `width`, each line padded after one leading space.

  Args:
    lines: text lines inside the box.
    width: inner width in columns (text holds width - 2).

  Returns:
    The box, every line the same length (width + 2).

  Raises:
    ValueError: a line is wider than the box holds.
  """
  out = ["+" + "-" * width + "+"]
  for text in lines:
    if len(text) > width - 2:
      raise ValueError(f"box line is {len(text)} wide, the box holds {width - 2}: {text!r}")
    out.append("| " + text.ljust(width - 2) + " |")
  out.append("+" + "-" * width + "+")
  return out


def chain(steps: list[dict], width: int, indent: int = 2) -> list[str]:
  """Boxes stacked top to bottom, joined by arrows, each with an optional exit to its right.

  Args:
    steps: dicts with `lines` (box text), optional `exit` (text after ` --> ` on the box's first line) and optional `label` (beside the arrow below).
    width: inner width of every box.
    indent: spaces before each box.

  Returns:
    The diagram lines, trailing spaces stripped.

  Raises:
    ValueError: from box().
  """
  out: list[str] = []
  mid = indent + 1 + width // 2
  for i, step in enumerate(steps):
    for j, row in enumerate(box(step["lines"], width)):
      line = " " * indent + row
      if step.get("exit") and j == 1:
        line += " --> " + step["exit"]
      out.append(line.rstrip())
    if i < len(steps) - 1:
      label = step.get("label")
      out.append(" " * mid + "|" + ("  " + label if label else ""))
      out.append(" " * mid + "v")
  return out


def grid(rows: list[list], title: str | None = None) -> list[str]:
  """Rows of side-by-side cells with shared edges; every row spans the same width.

  Args:
    rows: each row a list of [width, [lines]] cells.
    title: an optional line above the grid.

  Returns:
    The diagram lines.

  Raises:
    ValueError: rows of unequal span, or a cell line wider than its cell.
  """
  out = [title] if title else []
  total = None
  for row in rows:
    widths = [w for w, _ in row]
    span = sum(widths) + len(widths) - 1
    if total is None:
      total = span
    elif span != total:
      raise ValueError(f"grid row spans {span} columns, the first spans {total}")
    out.append("+" + "+".join("-" * w for w in widths) + "+")
    for i in range(max(len(lines) for _, lines in row)):
      cells = []
      for w, lines in row:
        text = lines[i] if i < len(lines) else ""
        if len(text) > w - 2:
          raise ValueError(f"cell line is {len(text)} wide, the cell holds {w - 2}: {text!r}")
        cells.append(" " + text.ljust(w - 1))
      out.append("|" + "|".join(cells) + "|")
  out.append("+" + "+".join("-" * w for w, _ in rows[-1]) + "+")
  return out


def side_by_side(parts: list[list[str]], gap: int = 4) -> list[str]:
  """Place drawn parts next to each other, top-aligned.

  Args:
    parts: each a list of lines.
    gap: spaces between parts.

  Returns:
    The joined lines, trailing spaces stripped.

  Raises:
    Nothing.
  """
  widths = [max((len(x) for x in p), default=0) for p in parts]
  out = []
  for i in range(max(len(p) for p in parts)):
    cells = [(p[i] if i < len(p) else "").ljust(w) for p, w in zip(parts, widths, strict=True)]
    out.append((" " * gap).join(cells).rstrip())
  return out


def draw(part: dict) -> list[str]:
  """Draw one spec part.

  Args:
    part: one of the part kinds in the module docstring.

  Returns:
    Its lines.

  Raises:
    ValueError: an unknown part kind, or a part that does not fit.
  """
  if "chain" in part:
    c = part["chain"]
    return chain(c["steps"], c["width"], c.get("indent", 2))
  if "grid" in part:
    return grid(part["grid"]["rows"], part["grid"].get("title"))
  if "box" in part:
    return box(part["box"]["lines"], part["box"]["width"])
  if "text" in part:
    return list(part["text"])
  if "columns" in part:
    c = part["columns"]
    return side_by_side([render(p if isinstance(p, list) else [p]) for p in c["parts"]], c.get("gap", 4))
  raise ValueError(f"unknown part: {sorted(part)}")


def render(spec: list[dict]) -> list[str]:
  """Draw a whole spec, parts stacked top to bottom.

  Args:
    spec: the list of parts.

  Returns:
    The diagram lines.

  Raises:
    ValueError: from draw().
  """
  out: list[str] = []
  for part in spec:
    out.extend(draw(part))
  return out


def main(argv: list[str] | None = None) -> int:
  """Print the diagram for a spec file.

  Args:
    argv: command-line arguments (the spec path); None reads sys.argv.

  Returns:
    0 drawn, 1 the spec does not fit, 2 bad arguments or an unreadable spec.

  Raises:
    Nothing: errors are printed to stderr with the exit code.
  """
  if sys.version_info < REQUIRES_PYTHON:
    print(f"needs Python {REQUIRES_PYTHON[0]}.{REQUIRES_PYTHON[1]} or later", file=sys.stderr)
    return 2
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("spec", type=Path, help="JSON spec file (see the module docstring)")
  args = ap.parse_args(argv)
  try:
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
  except (OSError, json.JSONDecodeError) as exc:
    print(f"cannot read {args.spec}: {exc}", file=sys.stderr)
    return 2
  try:
    print("\n".join(render(spec)))
  except (ValueError, KeyError, TypeError) as exc:
    print(f"does not fit: {exc}", file=sys.stderr)
    return 1
  return 0


if __name__ == "__main__":
  sys.exit(main())
