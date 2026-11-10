#!/usr/bin/env python3
"""Merge two blind labellers' conflict labels into one answer key, and report how far they agree.

Two labels match when both sides cite the same files within a line tolerance, in either order. The key is the union: a matched pair is kept
once (first labeller's text, the stricter severity, `found_by` both), and every label only one labeller found is kept too. Agreement is
found-by-both over the union. On the UNC pilot two careful agents agreed on 11 of 51 (2026-11-05), so a recall figure needs this number beside it.

Run: python scripts/merge_labels.py <labels-a.json> <labels-b.json> [--tolerance 8] > merged.json   (or `just merge-labels a b`).
Input: JSON arrays shaped as schemas/gold-conflict.schema.json (extra fields kept). Output: merged array on stdout, counts on stderr.
Safety: read-only; prints, writes nothing.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

SEVERITY_ORDER = ("P0", "P1", "P2", "P3")


def near(x: dict, y: dict, tolerance: int) -> bool:
  """Whether two label sides cite the same file within the tolerance.

  Args:
    x: one side ({path, line}).
    y: the other side.
    tolerance: allowed line distance.

  Returns:
    True on a match.
  """
  return x["path"] == y["path"] and abs(x["line"] - y["line"]) <= tolerance


def match(p: dict, q: dict, tolerance: int) -> bool:
  """Whether two labels name the same pair, in either order.

  Args:
    p: first label.
    q: second label.
    tolerance: allowed line distance.

  Returns:
    True on a match.
  """
  return (near(p["a"], q["a"], tolerance) and near(p["b"], q["b"], tolerance)) or (near(p["a"], q["b"], tolerance) and near(p["b"], q["a"], tolerance))


def merge(first: list[dict], second: list[dict], tolerance: int = 8, names: tuple[str, str] = ("A", "B")) -> tuple[list[dict], dict]:
  """Union of two label sets with agreement counts.

  Args:
    first: first labeller's labels.
    second: second labeller's labels.
    tolerance: allowed line distance for a match.
    names: labeller names for `found_by`.

  Returns:
    (merged labels with ids U01.., counts {first, second, both, union, agreement, by_severity, by_kind}).
  """
  out, used = [], set()
  for p in first:
    q = next((q for i, q in enumerate(second) if i not in used and match(p, q, tolerance)), None)
    row = dict(p) | {"found_by": [names[0]], "label_id": p.get("id")}
    if q is not None:
      used.add(second.index(q))
      row |= {"found_by": list(names), "also": q.get("id"), "severity": min(p["severity"], q["severity"], key=SEVERITY_ORDER.index)}
    out.append(row)
  out += [dict(q) | {"found_by": [names[1]], "label_id": q.get("id")} for i, q in enumerate(second) if i not in used]
  for n, row in enumerate(out, 1):
    row["id"] = f"U{n:02d}"
  both = sum(len(r["found_by"]) == 2 for r in out)
  counts = {
    "first": len(first),
    "second": len(second),
    "both": both,
    "union": len(out),
    "agreement": round(both / len(out), 3) if out else None,
    "by_severity": dict(sorted(Counter(r["severity"] for r in out).items())),
    "by_kind": dict(sorted(Counter(r["kind"] for r in out).items())),
  }
  return out, counts


def main(argv: list[str] | None = None) -> int:
  """Print the merged key; counts to stderr.

  Args:
    argv: arguments (sys.argv when None).

  Returns:
    Exit code (0; 1 when an input is not a JSON array).
  """
  p = argparse.ArgumentParser(description="Merge two blind label sets (read-only).")
  p.add_argument("first")
  p.add_argument("second")
  p.add_argument("--tolerance", type=int, default=8, help="line distance that still counts as the same place")
  args = p.parse_args(argv)
  sets = [json.loads(Path(f).read_text(encoding="utf-8")) for f in (args.first, args.second)]
  if not all(isinstance(s, list) for s in sets):
    print("merge_labels: each input must be a JSON array", file=sys.stderr)
    return 1
  merged, counts = merge(sets[0], sets[1], args.tolerance, (Path(args.first).stem, Path(args.second).stem))
  print(json.dumps(merged, indent=1, ensure_ascii=False))
  print(json.dumps(counts), file=sys.stderr)
  return 0


if __name__ == "__main__":
  sys.exit(main())
