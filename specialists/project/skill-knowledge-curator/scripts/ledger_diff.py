#!/usr/bin/env python3
"""Diff two curator ledgers: which claim dispositions, successors and conflicts differ.

Rehearse a sequence of `decide`/`amend` steps on a scratch copy of a project, then compare it with the live project before
applying. One dry run shows one step; only a diff of the end state shows a later step undoing an earlier one (Continuum,
2026-11-01: a CORRECTED decision rewrote a successor set by the step before it).

Run: python scripts/ledger_diff.py <before project> <after project> (or `just ledger-diff <before> <after>`). Read-only.
Standard library only, so it runs on any interpreter. Exit 0 when the ledgers match, 1 when they differ, 2 on a missing ledger.
"""

import argparse
import json
import sys
from pathlib import Path


def read_jsonl(path: Path) -> list[dict]:
  """Read one ledger file.

  Args:
    path: a JSONL file.

  Returns:
    Its records, in file order.
  """
  with path.open(encoding="utf-8") as handle:
    return [json.loads(line) for line in handle if line.strip()]


def dispositions(project: Path) -> dict[str, tuple]:
  """Fold the claim ledger to each claim's latest disposition.

  Args:
    project: project root holding `.kc/`.

  Returns:
    Claim id to (disposition, successor).
  """
  out = {}
  for rec in read_jsonl(project / ".kc" / "claims.jsonl"):
    if rec.get("record") == "disposition":
      out[rec["claim_id"]] = (rec["disposition"], rec.get("successor"))
  return out


def conflicts(project: Path) -> dict[str, tuple]:
  """Fold the conflict ledger to each conflict's latest state.

  Args:
    project: project root holding `.kc/`.

  Returns:
    Conflict id to (status, member claims).
  """
  merged: dict[str, dict] = {}
  for rec in read_jsonl(project / ".kc" / "conflicts.jsonl"):
    merged[rec["conflict_id"]] = {**merged.get(rec["conflict_id"], {}), **rec}
  return {cid: (rec.get("status", "open"), tuple(rec.get("claims", []))) for cid, rec in merged.items()}


def changed(before: dict, after: dict) -> dict[str, tuple]:
  """Keys whose values differ between two folded ledgers.

  Args:
    before: folded state of the first project.
    after: folded state of the second project.

  Returns:
    Key to (before value, after value); a side without the key gives None.
  """
  return {key: (before.get(key), after.get(key)) for key in sorted(before.keys() | after.keys()) if before.get(key) != after.get(key)}


def diff(before: Path, after: Path) -> dict:
  """Compare two projects' ledgers.

  Args:
    before: first project root.
    after: second project root.

  Returns:
    Dict with `claims` and `conflicts`, each from changed().
  """
  return {
    "claims": changed(dispositions(before), dispositions(after)),
    "conflicts": changed(conflicts(before), conflicts(after)),
  }


def main() -> int:
  """Print the diff as JSON.

  Returns:
    0 when the ledgers match, 1 when they differ, 2 when a ledger file is missing.
  """
  parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  parser.add_argument("before", type=Path)
  parser.add_argument("after", type=Path)
  args = parser.parse_args()
  try:
    result = diff(args.before, args.after)
  except FileNotFoundError as err:
    print(f"ledger_diff: {err}", file=sys.stderr)
    return 2
  print(json.dumps(result, indent=2, sort_keys=True))
  return 1 if result["claims"] or result["conflicts"] else 0


if __name__ == "__main__":
  sys.exit(main())
