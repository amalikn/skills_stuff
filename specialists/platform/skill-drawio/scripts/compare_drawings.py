#!/usr/bin/env python3
"""Compare two draw.io files cell by cell: what a re-render would change before it overwrites a drawing. Read-only.

Why (operator, 2026-11-19: "Diff first, then decide" before re-rendering two drifted consumer drawings): a drift check only says the drawing differs from
what its map renders; a re-render over a hand-edited drawing loses the edits. This reports per page the cells added and removed and, for cells in both,
label, style and geometry changes, so label changes (likely hand edits) can be told from geometry and style changes (likely a renderer upgrade).

Usage:
    compare_drawings.py OLD.drawio NEW.drawio [--list N]
    (render the map to a scratch copy with render_flowmap.py --root <copy> --write, then diff the committed file against it)
Exit: 0 when no label differs, 1 when a label was added, removed or changed (look before re-rendering), 2 on bad arguments or unreadable files.
Runtime: under 0.1 s for a 200-cell drawing.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from drawio import read

#: The oldest Python this script runs on (stdlib only).
REQUIRES_PYTHON = (3, 11)


def page_cells(path: Path) -> dict[tuple[str, str], tuple[str, str, tuple]]:
  """Every cell of every page: label, style and geometry.

  Args:
    path: a .drawio file.

  Returns:
    {(page name, cell id): (label text, style string, (x, y, width, height))}.

  Raises:
    ValueError: the file is not a readable draw.io file.
  """
  out = {}
  for name, model in read.models(path.read_text(encoding="utf-8")):
    for cid, (cell, label) in read.cells(model).items():
      g = cell.find("mxGeometry")
      geo = tuple(g.get(k) for k in ("x", "y", "width", "height")) if g is not None else ()
      out[(name, cid)] = (label, cell.get("style") or "", geo)
  return out


def diff(old: dict, new: dict) -> dict[str, list]:
  """The differences between two cell maps.

  Args:
    old: page_cells() of the current drawing.
    new: page_cells() of the candidate.

  Returns:
    {"removed", "added", "label", "style", "geometry"}: lists of keys; removed and added cells that carry a label are also in "label".
  """
  common = old.keys() & new.keys()
  out = {
    "removed": sorted(old.keys() - new.keys()),
    "added": sorted(new.keys() - old.keys()),
    "label": sorted(k for k in common if old[k][0] != new[k][0]),
    "style": sorted(k for k in common if old[k][1] != new[k][1]),
    "geometry": sorted(k for k in common if old[k][2] != new[k][2]),
  }
  old_labels = sorted(v[0] for k, v in old.items() if v[0])
  new_labels = sorted(v[0] for k, v in new.items() if v[0])
  out["label_text"] = sorted(set(old_labels) ^ set(new_labels))
  return out


def main(argv: list[str] | None = None) -> int:
  """Print a summary and the first N differences of each kind.

  Args:
    argv: command-line arguments.

  Returns:
    0 when no label text differs, 1 when one does, 2 when a file cannot be read.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("old", type=Path)
  ap.add_argument("new", type=Path)
  ap.add_argument("--list", type=int, default=3, metavar="N", help="differences to print per kind (default 3)")
  args = ap.parse_args(argv)
  try:
    old, new = page_cells(args.old), page_cells(args.new)
  except (OSError, ValueError) as exc:
    print(f"compare_drawings: {exc}", file=sys.stderr)
    return 2
  d = diff(old, new)
  print(
    f"cells {len(old)} -> {len(new)}; removed {len(d['removed'])}, added {len(d['added'])}; label {len(d['label'])},"
    f" style {len(d['style'])}, geometry {len(d['geometry'])}; label text only on one side {len(d['label_text'])}"
  )
  for kind in ("label", "style"):
    for key in d[kind][: args.list]:
      print(f"  {kind:5} {key[0]}/{key[1]}: {old[key][0 if kind == 'label' else 1][:60]!r} -> {new[key][0 if kind == 'label' else 1][:60]!r}")
  for text in d["label_text"][: args.list]:
    print(f"  text  {text[:80]!r}")
  return 1 if d["label"] or d["label_text"] else 0


if __name__ == "__main__":
  if sys.version_info < REQUIRES_PYTHON:
    sys.exit(f"needs Python {'.'.join(map(str, REQUIRES_PYTHON))}+")
  sys.exit(main())
