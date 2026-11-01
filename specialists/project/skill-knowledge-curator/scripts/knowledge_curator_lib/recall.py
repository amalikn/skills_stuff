"""Recall harness: scores a labelled conflict set against what reaches review (evaluation.md, Gate 0).

Imported, not run. A label reaches review when a candidate pair, a classified pair or a decision-point group holds claims citing both of
its sides. A side no claim cites is not_extracted: an extraction miss, not a pairing miss. Safety: reads state only.
"""

from collections import Counter
from itertools import combinations
from pathlib import Path

from . import candidates, claims, decision_points, schema
from .errors import InputError
from .state import State

GATE_OVERALL = 0.8
GATE_BLOCKING = ("P0", "P1")


def _citing(st: State, side: dict) -> set[str]:
  """Claims whose evidence cites one line of a label.

  Args:
    st: current state.
    side: {path, line}.

  Returns:
    Claim IDs.
  """
  return {cid for cid, c in st.claims.items() if any(e["path"] == side["path"] and e["line_start"] <= side["line"] <= e["line_end"] for e in c["evidence"])}


def status(label: dict, st: State, reached: set[frozenset], dismissed: set[frozenset]) -> str:
  """Outcome for one label.

  Args:
    label: the gold conflict.
    st: current state.
    reached: pairs that reach review.
    dismissed: pairs triage cleared.

  Returns:
    reached, dismissed, missed, same_claim or not_extracted.
  """
  left, right = _citing(st, label["a"]), _citing(st, label["b"])
  if not left or not right:
    return "not_extracted"
  if left & right:
    return "same_claim"
  pairs = {frozenset((a, b)) for a in left for b in right}
  if pairs & reached:
    return "reached"
  return "dismissed" if pairs & dismissed else "missed"


def _rate(rows: list[dict]) -> float:
  """Share of labels reaching review.

  Args:
    rows: scored labels.

  Returns:
    The share, 0 when empty.
  """
  return round(sum(r["status"] == "reached" for r in rows) / len(rows), 3) if rows else 0.0


def score(st: State, path: Path) -> dict:
  """Score a labels file.

  Args:
    st: current state.
    path: JSON array of gold conflicts.

  Returns:
    {"labels": [...], "summary": {...}}; excluded labels are listed and uncounted.

  Raises:
    InputError: a label breaks the schema.
  """
  labels = claims.load_input(path)
  bad = [f"{r.get('id', n)}: {e}" for n, r in enumerate(labels, 1) for e in schema.errors("gold-conflict", r)]
  if bad:
    raise InputError("labels rejected:\n  " + "\n  ".join(bad))
  reached = {frozenset(p["claims"]) for p in candidates.pairs(st)["pairs"]} | candidates.classified(st) | decision_points.review_pairs(st)
  dismissed = {frozenset(p) for c in st.conflicts.values() if c["status"] == "dismissed" for p in combinations(c["claims"], 2)}
  live = {frozenset(p) for c in st.open_conflicts() for p in combinations(c["claims"], 2)}
  reached = (reached - dismissed) | live
  rows = [{"id": r["id"], "kind": r["kind"], "severity": r["severity"], "status": status(r, st, reached, dismissed)} for r in labels if not r.get("excluded")]
  blocking = [r for r in rows if r["severity"] in GATE_BLOCKING]
  summary = {
    "total": len(rows),
    "excluded": len(labels) - len(rows),
    "by_status": dict(sorted(Counter(r["status"] for r in rows).items())),
    "recall": _rate(rows),
    "recall_blocking": _rate(blocking),
    "recall_by_kind": {k: _rate([r for r in rows if r["kind"] == k]) for k in sorted({r["kind"] for r in rows})},
    "gate_pass": _rate(rows) >= GATE_OVERALL and all(r["status"] == "reached" for r in blocking),
  }
  return {"labels": rows, "summary": summary}
