"""Amendments to a conflict after the fact: reach a claim the conflict did not list, or repair a successor link (evaluation.md P19, P27).

Imported, not run. Append-only like a decision: each amendment is an AMEND decision naming the previous one, and nothing is overwritten
(INV-016). Safety: returns records for ledger.append.
"""

import datetime as dt

from . import ids, settings
from .decisions import DecideResult, revalidate
from .errors import InputError
from .state import State


def amend(st: State, conflict_id: str, claim_id: str, supersede: bool, reason: str, actor: str, now: dt.datetime) -> DecideResult:
  """Add a claim to a conflict: an operator ruling reaches a claim the conflict did not list (evaluation.md P19).

  Append-only, like decide: the conflict gains the claim, and on a decided conflict --supersede retires it under the ruling.

  Args:
    st: current state.
    conflict_id: the conflict.
    claim_id: claim to add.
    supersede: supersede it under the conflict's latest decision; False keeps its disposition.
    reason: the operator's reason (required).
    actor: who decided.
    now: decision time (timezone-aware).

  Returns:
    The decision result.

  Raises:
    InputError: unknown conflict or claim, missing reason, claim already listed, or a supersede with no ruling to apply.
    SourceChanged: the claim's evidence moved.
  """
  cf = st.conflicts.get(conflict_id)
  if cf is None:
    raise InputError(f"unknown conflict {conflict_id}")
  if claim_id not in st.claims:
    raise InputError(f"unknown claim {claim_id}")
  if claim_id in cf["claims"]:
    raise InputError(f"{claim_id} is already in {conflict_id}")
  if not reason or not reason.strip():
    raise InputError("--reason is required")
  previous = [d for d in st.decisions if d.get("conflict_id") == conflict_id]
  rulings = [d for d in previous if d["current_claims"]]
  if supersede and (cf["status"] == "open" or not rulings):
    raise InputError("--supersede needs a decided conflict; use --keep, or decide it first")
  revalidate(st, {"claims": [claim_id]})
  decided_at = now.isoformat(timespec="seconds")
  did = ids.make_id("dr", conflict_id, settings.AMEND_ACTION, claim_id, decided_at)
  current = rulings[-1]["current_claims"] if rulings else []
  res = DecideResult(
    decision={
      "record": "decision",
      "decision_id": did,
      "conflict_id": conflict_id,
      "action": settings.AMEND_ACTION,
      "actor": actor,
      "decided_at": decided_at,
      "reason": reason,
      "answer_text": None,
      "scope_note": None,
      "added_claim": claim_id,
      "current_claims": current,
      "superseded_claims": [claim_id] if supersede else [],
      "previous_decision_id": previous[-1]["decision_id"] if previous else None,
    }
  )
  evidence_ids = sorted({*cf["evidence_ids"], *(e["evidence_id"] for e in st.claims[claim_id]["evidence"])})
  res.conflicts.append({**cf, "claims": [*cf["claims"], claim_id], "evidence_ids": evidence_ids})
  if supersede:
    res.dispositions.append({"record": "disposition", "claim_id": claim_id, "disposition": "SUPERSEDED", "successor": current[0], "reason": reason, "by": did})
  return res


def set_successor(st: State, conflict_id: str, claim_id: str, successor: str, reason: str, actor: str, now: dt.datetime) -> DecideResult:
  """Repoint one superseded claim at another successor, append-only: the repair for a wrong link (evaluation.md P27).

  Args:
    st: current state.
    conflict_id: a conflict listing the claim.
    claim_id: the superseded claim.
    successor: its new successor.
    reason: the operator's reason (required).
    actor: who decided.
    now: decision time (timezone-aware).

  Returns:
    The decision result.

  Raises:
    InputError: unknown conflict or successor, missing reason, a claim off the conflict, or a claim not superseded.
  """
  cf = st.conflicts.get(conflict_id)
  if cf is None:
    raise InputError(f"unknown conflict {conflict_id}")
  if claim_id not in cf["claims"]:
    raise InputError(f"{claim_id} is not in {conflict_id}")
  if st.disposition(claim_id) != "SUPERSEDED":
    raise InputError(f"{claim_id} is not SUPERSEDED")
  if successor not in st.claims or successor == claim_id:
    raise InputError(f"unknown or invalid successor {successor}")
  if not reason or not reason.strip():
    raise InputError("--reason is required")
  decided_at = now.isoformat(timespec="seconds")
  did = ids.make_id("dr", conflict_id, settings.AMEND_ACTION, claim_id, successor, decided_at)
  previous = [d["decision_id"] for d in st.decisions if d.get("conflict_id") == conflict_id]
  old = st.dispositions[claim_id].get("successor")
  res = DecideResult(
    decision={
      "record": "decision",
      "decision_id": did,
      "conflict_id": conflict_id,
      "action": settings.AMEND_ACTION,
      "actor": actor,
      "decided_at": decided_at,
      "reason": reason,
      "answer_text": None,
      "scope_note": None,
      "successor_change": {"claim": claim_id, "from": old, "to": successor},
      "current_claims": [],
      "superseded_claims": [claim_id],
      "previous_decision_id": previous[-1] if previous else None,
    }
  )
  res.dispositions.append({"record": "disposition", "claim_id": claim_id, "disposition": "SUPERSEDED", "successor": successor, "reason": reason, "by": did})
  return res
