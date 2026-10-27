"""Relation intake: record pair classifications and apply only the automatic dispositions policy allows.

Records the agent's classification of candidate pairs and applies only the dispositions policy allows without a
human (design doc 7.2).

Imported, not run. Automatic: equivalent (the weaker-evidenced claim becomes DUPLICATE of the keeper, its sources kept), and
time-evolution backed by a verified supersession excerpt (the older claim becomes SUPERSEDED, successor linked). true-conflict and
uncertain open a conflict for review; nothing is promoted. Everything else is recorded only. Safety: returns records for
ledger.append.
"""

from dataclasses import dataclass, field

from . import ids, schema
from .evidence import Reader, verify_span
from .state import State


@dataclass
class RelateResult:
  """Records produced from one relations input file.

  Attributes:
    relations: relation records.
    conflicts: conflict events (status open).
    dispositions: disposition events.
    errors: messages; non-empty means nothing may be appended.
    skipped: inputs already recorded.
    source_changed: True when a supersession excerpt's source changed.
  """

  relations: list = field(default_factory=list)
  conflicts: list = field(default_factory=list)
  dispositions: list = field(default_factory=list)
  errors: list = field(default_factory=list)
  skipped: int = 0
  source_changed: bool = False


def conflict_id_for(claims: list[str]) -> str:
  """Conflict ID for a claim pair, order-independent.

  Args:
    claims: the two claim IDs.

  Returns:
    "cf-" plus 10 hex digits.
  """
  return ids.make_id("cf", sorted(claims), length=10)


def _keeper(st: State, a: str, b: str) -> str:
  """Which of two equivalent claims stays: more independent sources, then the lower ID.

  Args:
    st: current state.
    a: first claim ID.
    b: second claim ID.

  Returns:
    The keeper's ID.
  """
  return min((a, b), key=lambda c: (-st.claims[c]["independent_sources"], c))


def _conflict(st: State, rec: dict, rel_id: str) -> dict:
  """Open-conflict event for a true-conflict or uncertain relation.

  Args:
    st: current state.
    rec: relation input.
    rel_id: relation ID.

  Returns:
    The conflict event.
  """
  a, b = (st.claims[c] for c in rec["claims"])
  return {
    "record": "conflict",
    "conflict_id": conflict_id_for(rec["claims"]),
    "status": "open",
    "claims": sorted(rec["claims"]),
    "topic_key": a["topic_key"],
    "categories": sorted({a["primary_category"], b["primary_category"]}),
    "severity": rec["severity"],
    "conflict_type": rec.get("conflict_type") or rec["relation"],
    "question": rec["question"],
    "hypotheses": rec.get("hypotheses", []),
    "recommended_current": rec.get("recommended_current"),
    "reason": rec["reason"],
    "evidence_ids": sorted({e["evidence_id"] for c in (a, b) for e in c["evidence"]}),
    "relation_id": rel_id,
  }


def _check(st: State, rec: dict) -> list[str]:
  """Reference checks beyond the schema.

  Args:
    st: current state.
    rec: relation input.

  Returns:
    Messages.
  """
  out = [f"unknown claim {c}" for c in rec["claims"] if c not in st.claims]
  if rec.get("recommended_current") and rec["recommended_current"] not in rec["claims"]:
    out.append("recommended_current must be one of the two claims")
  if rec["relation"] == "time-evolution" and {rec["superseded"], rec["successor"]} != set(rec["claims"]):
    out.append("superseded and successor must be the two claims")
  return out


def _apply_one(st: State, rec: dict, rel_id: str, reader: Reader, res: RelateResult) -> list[str]:
  """Turn one valid relation into records.

  Args:
    st: current state.
    rec: relation input.
    rel_id: relation ID.
    reader: file reader.
    res: result being built.

  Returns:
    Error messages (empty on success).
  """
  out = {"record": "relation", "relation_id": rel_id, **{k: v for k, v in rec.items() if k not in ("record", "supersession_evidence")}}
  out["claims"] = sorted(rec["claims"])
  kind = rec["relation"]
  if kind == "time-evolution":
    ev, err, changed = verify_span(reader, rec["supersession_evidence"])
    res.source_changed |= changed
    if err:
      return [err]
    out["supersession_evidence"] = ev
    res.dispositions.append(
      {
        "record": "disposition",
        "claim_id": rec["superseded"],
        "disposition": "SUPERSEDED",
        "successor": rec["successor"],
        "reason": rec["reason"],
        "by": rel_id,
      }
    )
  elif kind == "equivalent":
    keep = _keeper(st, *rec["claims"])
    dup = next(c for c in rec["claims"] if c != keep)
    res.dispositions.append({"record": "disposition", "claim_id": dup, "disposition": "DUPLICATE", "duplicate_of": keep, "reason": rec["reason"], "by": rel_id})
  elif kind in ("true-conflict", "uncertain"):
    cf = _conflict(st, rec, rel_id)
    if st.conflicts.get(cf["conflict_id"], {}).get("status") != "open":
      res.conflicts.append(cf)
  res.relations.append(out)
  return []


def ingest(st: State, records: list[dict]) -> RelateResult:
  """Validate and convert one batch of relation inputs.

  Args:
    st: current state.
    records: relation inputs.

  Returns:
    The result (check errors before appending anything).
  """
  res, reader = RelateResult(), Reader(st)
  for n, rec in enumerate(records, 1):
    problems = schema.record_errors(rec) if isinstance(rec, dict) and rec.get("record") == "relation" else ["record: expected 'relation'"]
    problems = problems or _check(st, rec)
    if problems:
      res.errors.extend(f"#{n}: {p}" for p in problems)
      continue
    rel_id = ids.make_id("rel", sorted(rec["claims"]), rec["relation"])
    if rel_id in st.relations or any(r["relation_id"] == rel_id for r in res.relations):
      res.skipped += 1
      continue
    res.errors.extend(f"#{n}: {p}" for p in _apply_one(st, rec, rel_id, reader, res))
  return res
