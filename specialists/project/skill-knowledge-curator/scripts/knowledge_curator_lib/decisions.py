"""Human review: render conflict review cards and turn an operator's answer into an append-only decision (design doc 7.5-7.8).

Imported, not run. A decision is recorded only from an explicit answer; no answer leaves the conflict open (no simulated consent).
Before applying, the evidence of every claim in the conflict is re-checked; a changed source stops the decision (exit 5). A later
decision on the same conflict names the earlier one in previous_decision_id; nothing is overwritten (INV-016). Safety: returns
records for ledger.append.
"""

import datetime as dt
from dataclasses import dataclass, field

from . import ids
from .errors import InputError, SourceChanged
from .evidence import Reader, recheck
from .state import State


@dataclass
class DecideResult:
  """Records produced by one decision.

  Attributes:
    decision: the decision record.
    conflicts: conflict events.
    dispositions: disposition events.
    claims: new claim versions (CORRECTED only).
  """

  decision: dict
  conflicts: list = field(default_factory=list)
  dispositions: list = field(default_factory=list)
  claims: list = field(default_factory=list)


def _claim_row(st: State, label: str, cid: str) -> str:
  """One table row of a review card.

  Args:
    st: current state.
    label: "A" or "B".
    cid: claim ID.

  Returns:
    Markdown table row.
  """
  c = st.claims[cid]
  srcs = "; ".join(f"`{e['path']}` L{e['line_start']}-{e['line_end']}" for e in c["evidence"]) or "decision only"
  return f"| {label} | {c['claim_text']} | {c['kind']} / {c['epistemic_status']} | {st.disposition(cid)} | {srcs} |"


def _card(st: State, cf: dict) -> list[str]:
  """Markdown lines of one review card.

  Args:
    st: current state.
    cf: open conflict.

  Returns:
    Lines.
  """
  a, b = cf["claims"]
  rec = cf.get("recommended_current")
  lines = [
    f"### {cf['conflict_id']} · {cf['severity']} · {cf['conflict_type']}",
    "",
    f"**Question:** {cf['question']}",
    "",
    "| | Claim | Kind / status | Disposition | Sources |",
    "| --- | --- | --- | --- | --- |",
    _claim_row(st, "A", a),
    _claim_row(st, "B", b),
    "",
    f"**Assessment:** {cf['reason']}",
  ]
  if cf.get("hypotheses"):
    lines.append("**Hypotheses:** " + "; ".join(cf["hypotheses"]))
  lines.append(f"**Recommendation:** current = {'A' if rec == a else 'B'} (`{rec}`)" if rec else "**Recommendation:** none; evidence does not settle it.")
  cid = cf["conflict_id"]
  lines += [
    "",
    "Choose (recorded only when you answer):",
    "",
    f"1. Accept recommendation: `kc decide --project <dir> {cid} ACCEPT_RECOMMENDATION --reason ...`" if rec else "1. (no recommendation to accept)",
    f"2. The other claim is current: `kc decide --project <dir> {cid} USE_OTHER --current <claim> --reason ...`",
    f"3. Both apply in different scopes: `kc decide --project <dir> {cid} BOTH_APPLY_SCOPED --scope-note ... --reason ...`",
    f"4. Neither; corrected statement: `kc decide --project <dir> {cid} CORRECTED --corrected-text ... --reason ...`",
    f"5. Defer; publish neither as settled: `kc decide --project <dir> {cid} DEFER --reason ...`",
    "",
  ]
  return lines


def review_markdown(st: State) -> str:
  """Review queue: open conflicts grouped by topic, P0 first, one decision per concept.

  Args:
    st: current state.

  Returns:
    Markdown text (empty queue says so).
  """
  open_cf = st.open_conflicts()
  out = ["# Review queue", "", f"Project `{st.cfg['project_id']}`: {len(open_cf)} open conflict(s). Unanswered items stay REVIEW_REQUIRED.", ""]
  topics: dict[str, list[dict]] = {}
  for cf in open_cf:
    topics.setdefault(cf["topic_key"], []).append(cf)
  for topic in sorted(topics, key=lambda t: (min(c["severity"] for c in topics[t]), t)):
    out += [f"## Topic `{topic}`", ""]
    for cf in topics[topic]:
      out += _card(st, cf)
  return "\n".join(out).rstrip() + "\n"


def _revalidate(st: State, cf: dict) -> None:
  """Re-check the evidence behind every claim in a conflict.

  Args:
    st: current state.
    cf: the conflict.

  Raises:
    SourceChanged: any evidence is broken or missing.
  """
  reader = Reader(st)
  bad = [f"{e['path']} L{e['line_start']}" for c in cf["claims"] for e in st.claims[c]["evidence"] if recheck(reader, e)["status"] in ("broken", "missing")]
  if bad:
    raise SourceChanged("evidence no longer matches its source: " + ", ".join(bad) + " (run kc inventory, re-extract, then decide)")


def _corrected_claim(st: State, cf: dict, text: str, decision_id: str) -> dict:
  """Operator-authored claim for a CORRECTED decision.

  Args:
    st: current state.
    cf: the conflict.
    text: the corrected statement.
    decision_id: decision that authorises it.

  Returns:
    A claim version record (no evidence; decision_id instead, INV-005).
  """
  base = st.claims[cf["claims"][0]]
  body = {k: base.get(k) for k in ("subject", "predicate", "primary_category", "subcategories", "labels", "topic_key", "scope", "valid_time")}
  body.update(object=text, claim_text=text, kind="decision", epistemic_status="APPROVED", recorded_time=None, confidence="high", inference=False)
  body["decision_id"] = decision_id
  cid = ids.make_id("cl", st.cfg["project_id"], ids.norm(body["subject"]), ids.norm(body["predicate"]), ids.norm(text), body["scope"] or {})
  return {"record": "claim", "claim_id": cid, **body, "evidence": [], "independent_sources": 0, "version_id": ids.make_id("cv", cid, body, [])}


def _targets(st: State, cf: dict, action: str, current: str | None, scope_note: str | None) -> tuple[list[str], list[str]]:
  """Claims made current and superseded by an action (CORRECTED handled by the caller).

  Args:
    st: current state.
    cf: the conflict.
    action: decision action.
    current: claim chosen for USE_OTHER.
    scope_note: required for BOTH_APPLY_SCOPED.

  Returns:
    (current claim IDs, superseded claim IDs).

  Raises:
    InputError: the action's required argument is missing or invalid.
  """
  claims = cf["claims"]
  if action == "ACCEPT_RECOMMENDATION":
    if not cf.get("recommended_current"):
      raise InputError("this conflict has no recommendation; choose USE_OTHER, BOTH_APPLY_SCOPED, CORRECTED or DEFER")
    current = cf["recommended_current"]
  if action in ("ACCEPT_RECOMMENDATION", "USE_OTHER"):
    if current not in claims:
      raise InputError(f"--current must be one of {', '.join(claims)}")
    return [current], [c for c in claims if c != current]
  if action == "BOTH_APPLY_SCOPED":
    if not scope_note:
      raise InputError("BOTH_APPLY_SCOPED needs --scope-note naming the condition that separates them")
    return list(claims), []
  return [], []


def decide(st: State, conflict_id: str, action: str, reason: str, actor: str, now: dt.datetime, **opts) -> DecideResult:
  """Build the records for one operator decision.

  Args:
    st: current state.
    conflict_id: the conflict answered.
    action: one of settings.ACTIONS.
    reason: the operator's reason (required).
    actor: who decided.
    now: decision time (timezone-aware).
    **opts: current, scope_note, corrected_text, answer_text.

  Returns:
    The decision result.

  Raises:
    InputError: unknown conflict, missing reason or argument.
    SourceChanged: the evidence moved under the decision.
  """
  cf = st.conflicts.get(conflict_id)
  if cf is None:
    raise InputError(f"unknown conflict {conflict_id}")
  if not reason or not reason.strip():
    raise InputError("--reason is required")
  _revalidate(st, cf)
  decided_at = now.isoformat(timespec="seconds")
  did = ids.make_id("dr", conflict_id, action, decided_at)
  previous = [d["decision_id"] for d in st.decisions if d.get("conflict_id") == conflict_id]
  res = DecideResult(decision={})
  if action == "CORRECTED":
    if not opts.get("corrected_text"):
      raise InputError("CORRECTED needs --corrected-text")
    new = _corrected_claim(st, cf, opts["corrected_text"], did)
    res.claims.append(new)
    current, superseded = [new["claim_id"]], list(cf["claims"])
  else:
    current, superseded = _targets(st, cf, action, opts.get("current"), opts.get("scope_note"))
  res.decision = {
    "record": "decision",
    "decision_id": did,
    "conflict_id": conflict_id,
    "action": action,
    "actor": actor,
    "decided_at": decided_at,
    "reason": reason,
    "answer_text": opts.get("answer_text"),
    "scope_note": opts.get("scope_note"),
    "current_claims": current,
    "superseded_claims": superseded,
    "previous_decision_id": previous[-1] if previous else None,
  }
  status = "open" if action == "DEFER" else "resolved"
  res.conflicts.append({**cf, "status": status, "decided_by": did})
  for cid in current:
    res.dispositions.append({"record": "disposition", "claim_id": cid, "disposition": "CURRENT", "reason": reason, "by": did})
  for cid in superseded:
    res.dispositions.append(
      {"record": "disposition", "claim_id": cid, "disposition": "SUPERSEDED", "successor": current[0] if current else None, "reason": reason, "by": did}
    )
  return res
