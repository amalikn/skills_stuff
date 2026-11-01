#!/usr/bin/env python3
"""Carry claims onto byte-identical files, so a copy needs no extraction agent and still counts as one source.

Inventory groups byte copies; a claim cited on one member is restated on the others at the same lines, which merges evidence and leaves
independent_sources at 1. Sections of a copy with no such claim become context records. Found on the MCP pilot, 2026-11-01.

Run: python scripts/restate_byte_copies.py <project> > copies.json, then `kc claims --project <project> --file copies.json --apply`
(or `just restate-copies <project>`). Read-only: prints JSON, writes nothing.
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

from knowledge_curator_lib import claims, state

_CLAIM_FIELDS = (
  "subject",
  "predicate",
  "object",
  "claim_text",
  "kind",
  "epistemic_status",
  "primary_category",
  "subcategories",
  "labels",
  "topic_key",
  "scope",
)


def copy_groups(st: state.State) -> dict[str, list[str]]:
  """Each live file's byte-identical partners.

  Args:
    st: current state.

  Returns:
    path -> the other paths with the same bytes.
  """
  by_hash = defaultdict(list)
  for path, src in st.source_by_path().items():
    by_hash[src["sha256"]].append(path)
  return {p: [q for q in group if q != p] for group in by_hash.values() if len(group) > 1 for p in group}


def _claim_input(st: state.State, cid: str, spans: list[dict]) -> dict:
  """Claim input restating a ledger claim with new spans.

  Args:
    st: current state.
    cid: claim ID.
    spans: evidence spans on the copies.

  Returns:
    The input record.
  """
  claim, event = st.claims[cid], st.dispositions.get(cid, {})
  rec = {"record": "claim", **{k: claim[k] for k in _CLAIM_FIELDS}, "disposition": st.disposition(cid), "evidence": spans}
  if rec["disposition"] in ("HISTORICAL", "SUPERSEDED"):
    rec.update({"successor": event["successor"]} if event.get("successor") else {"historical_basis": "source-stated"})
  return rec


def build(st: state.State) -> list[dict]:
  """Records that bring every byte copy level with its partner.

  Args:
    st: current state.

  Returns:
    Claim restatements, then context records for sections still pending on a copy.
  """
  groups, out, covered = copy_groups(st), [], set()
  for cid, claim in sorted(st.claims.items()):
    cited = {e["path"] for e in claim["evidence"]}
    spans = [
      {"source_path": copy, "line_start": e["line_start"], "line_end": e["line_end"], "excerpt": e["excerpt"]}
      for e in claim["evidence"]
      for copy in groups.get(e["path"], [])
      if copy not in cited
    ]
    if spans:
      out.append(_claim_input(st, cid, spans))
      covered.update((s["source_path"], s["line_start"]) for s in spans)
  for row in claims.coverage(st)["sections"]:
    hit = any(path == row["path"] and row["lines"][0] <= line <= row["lines"][1] for path, line in covered)
    if row["status"] == "pending" and row["path"] in groups and not hit:
      out.append({"record": "section_status", "section_id": row["section_id"], "status": "context", "reason": "byte copy; the partner section holds no claim"})
  return out


def main(argv: list[str] | None = None) -> int:
  """Print the records for one project.

  Args:
    argv: arguments (sys.argv when None).

  Returns:
    Exit code: 0 ok, 1 no such folder.
  """
  parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  parser.add_argument("project")
  args = parser.parse_args(argv)
  root = Path(args.project)
  if not root.is_dir():
    print(f"not a folder: {root}", file=sys.stderr)
    return 1
  print(json.dumps(build(state.load(root)), indent=1, ensure_ascii=False))
  return 0


if __name__ == "__main__":
  sys.exit(main())
