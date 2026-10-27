"""Caller intake (direct audit or skill-slurp-chat Step 4b): map each submitted item to a finding with a one-to-one trace.

Imported, not run. Every input item_id appears exactly once in the response: a finding, a no-finding or an intentional skip, so the
caller's coverage audit (slurp Step 6b) can account for it. The curator advises routing; it writes nothing and never marks a
disputed claim settled (references/invocation-contract.md). Safety: read-only.
"""

from . import fuzzy, schema
from .state import State

ROUTINE_TYPES = ("progress", "status", "operation", "command", "routine")
MATCH_AT = 85.0


def _best_match(st: State, text: str) -> tuple[str | None, float]:
  """Most similar existing claim.

  Args:
    st: current state.
    text: item text.

  Returns:
    (claim ID or None, similarity).
  """
  best, score = None, 0.0
  for cid in sorted(st.claims):
    s = fuzzy.similarity(text, st.claims[cid]["claim_text"])
    if s > score:
      best, score = cid, s
  return best, score


def _finding(st: State, item: dict, n: int) -> dict:
  """Finding for one item.

  Args:
    st: current state.
    item: payload item.
    n: 1-based position (for the finding ID).

  Returns:
    The finding.
  """
  base = {"finding_id": f"finding-{n:03d}", "item_ids": [item["item_id"]], "sources": [item["source_ref"]] if item.get("source_ref") else []}
  if item["type"].lower() in ROUTINE_TYPES:
    return {**base, "type": "skipped", "disposition": "no_curation_needed", "reason": f"routine item type {item['type']!r}"}
  cid, score = _best_match(st, item["text"])
  if cid is None or score < MATCH_AT:
    return {**base, "type": "new_knowledge", "disposition": "extract", "reason": "no matching claim; extract claims with kc worksheet / kc claims"}
  conflicts = st.open_conflicts(cid)
  if conflicts:
    return {
      **base,
      "type": "conflict",
      "disposition": "review_required",
      "claim_ids": [cid],
      "conflict_ids": [c["conflict_id"] for c in conflicts],
      "reason": "matches a disputed claim",
    }
  disp = st.effective(cid)
  kind = "matches_current" if disp == "CURRENT" else "matches_history" if disp in ("SUPERSEDED", "HISTORICAL") else "matches_unsettled"
  return {
    **base,
    "type": kind,
    "disposition": "no_change" if disp == "CURRENT" else "review_required",
    "claim_ids": [cid],
    "similarity": score,
    "reason": f"existing claim is {disp}",
  }


def respond(st: State, payload: dict) -> dict:
  """Response for one caller payload.

  Args:
    st: current state.
    payload: the request (schemas/intake-payload.schema.json).

  Returns:
    {"schema_version", "status", "findings", "proposed_records", "routing_hints", "trace", "errors"}.
  """
  problems = schema.errors("intake-payload", payload)
  if problems:
    return {"schema_version": "1.0", "status": "rejected", "findings": [], "proposed_records": [], "routing_hints": [], "trace": [], "errors": problems}
  findings = [_finding(st, item, n) for n, item in enumerate(payload["items"], 1)]
  hints = sorted({f"route {f['item_ids'][0]} to the review queue" for f in findings if f["disposition"] == "review_required"})
  trace = [{"item_id": f["item_ids"][0], "outcome": f["type"], "finding_id": f["finding_id"]} for f in findings]
  return {"schema_version": "1.0", "status": "completed", "findings": findings, "proposed_records": [], "routing_hints": hints, "trace": trace, "errors": []}
