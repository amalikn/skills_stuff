"""Noise triage: named gates sort open conflicts into noise, proposed and needs_human (research B2; AGENTS.md, Triage).

Imported, not run. Noise needs a rule that fires with cited proof; anything else goes to a person, and P0 always does. A clearance is an
append-only conflict event naming its rule and run, and can be undone; the conflict's relation and claims stay. History rules
(superseded-section, sequential-steps) clear as documented-evolution, kept and queryable; the rest as dismissed (operator, 2026-11-05). Rule outcomes are not
yet audited, so gates are measured on a fresh sample (references/evaluation.md). Safety: returns records for ledger.append.
"""

import re

from . import ids, settings, status_map
from .candidates import compared, overlaps, situation, source_ids
from .decision_points import byte_copies
from .state import State

RULES_VERSION = 1
_LABELLED = ("superseded", "historical")
_PATH = re.compile(r"/[\w.-]+(?:/[\w.-]+)+")
_GONE = re.compile(r"\b(retired|absent|removed|deleted|gone)\b", re.IGNORECASE)
_SELF_LABEL = re.compile(r"\b(authoritative|superseded|read first)\b", re.IGNORECASE)
_PLAN = re.compile(r"\b(optional|future|suggested|next workstream|later)\b", re.IGNORECASE)
_LIVE = re.compile(r"\b(active|canonical|live|present|in use)\b", re.IGNORECASE)


def _docs(st: State, cid: str) -> list[str]:
  """Documents a claim cites, one per byte group.

  Args:
    st: current state.
    cid: claim ID.

  Returns:
    Paths.
  """
  claim = st.claims[cid]
  copies = byte_copies(st, claim)
  return sorted({e["path"] for e in claim["evidence"] if e["path"] not in copies})


def _gone_paths(text: str) -> set[str]:
  """Final names of paths a text calls gone.

  Args:
    text: claim text.

  Returns:
    Lower-case last path segments, empty when the text has no gone word.
  """
  return {p.rstrip("/").rsplit("/", 1)[-1].lower() for p in _PATH.findall(text)} if _GONE.search(text) else set()


def opposite_status(a: dict, b: dict) -> bool:
  """Whether a path called gone on one side is named on the other in anything but a gone statement: real whatever the banners say.

  Args:
    a: first claim.
    b: second claim.

  Returns:
    True on a match.
  """
  for one, two in ((a["claim_text"], b["claim_text"]), (b["claim_text"], a["claim_text"])):
    if not _GONE.search(two) and any(name in two.lower() for name in _gone_paths(one)):
      return True
  x, y = a["claim_text"], b["claim_text"]
  shared = set(_PATH.findall(x)) & set(_PATH.findall(y))
  return bool(shared) and bool((_GONE.search(x) and _LIVE.search(y)) or (_LIVE.search(x) and _GONE.search(y)))


def _unlabelled_claims(st: State, status: dict) -> dict:
  """Live claims in documents with no superseded or historical label, by subject and by topic.

  Args:
    st: current state.
    status: from status_map.files.

  Returns:
    {key: [claim IDs]}.
  """
  index: dict[tuple, list[str]] = {}
  for cid, claim in st.claims.items():
    if st.disposition(cid) in ("CURRENT", "REVIEW_REQUIRED") and not _labelled(st, cid, status):
      view = compared(st, claim)
      index.setdefault(("subject", view["subject"]), []).append(cid)
      index.setdefault(("topic", view["topic_key"]), []).append(cid)
  return index


def _labelled(st: State, cid: str, status: dict) -> list[str]:
  """Label lines of a claim whose every document is labelled superseded or historical.

  Args:
    st: current state.
    cid: claim ID.
    status: from status_map.files.

  Returns:
    "path:line quote" signals, empty when any document is not labelled.
  """
  docs = _docs(st, cid)
  rows = [(d, status.get(d, {})) for d in docs]
  if not rows or any(r.get("status") not in _LABELLED for _, r in rows):
    return []
  return [f"{d}:{r['line']} {r['quote']}" for d, r in rows]


def _replacement(st: State, cid: str, index: dict) -> str | None:
  """A later statement on the same subject or topic, which shows a labelled value was replaced, not left standing.

  Args:
    st: current state.
    cid: labelled claim.
    index: from _unlabelled_claims.

  Returns:
    The witness claim ID, or None.
  """
  view = compared(st, st.claims[cid])
  found = index.get(("subject", view["subject"]), []) or index.get(("topic", view["topic_key"]), [])
  return min(found) if found else None


def _sequential(st: State, a: str, b: str, status: dict) -> list[str]:
  """Proof that two claims sit in different places of one numbered series.

  Args:
    st: current state.
    a: first claim.
    b: second claim.
    status: from status_map.files.

  Returns:
    Signals, or empty.
  """
  left, right = _docs(st, a), _docs(st, b)
  if len(left) != 1 or len(right) != 1 or left == right:
    return []
  one, two = status[left[0]], status[right[0]]
  same_folder = left[0].rpartition("/")[0] == right[0].rpartition("/")[0]
  if not same_folder or one["order"] is None or two["order"] is None or one["order"] == two["order"]:
    return []
  return [f"{left[0]} is number {one['order']}", f"{right[0]} is number {two['order']}"]


def evaluate(st: State, cf: dict, status: dict, index: dict) -> dict:
  """Outcome for one open conflict.

  Args:
    st: current state.
    cf: the conflict.
    status: from status_map.files.
    index: from _unlabelled_claims.

  Returns:
    {conflict_id, severity, outcome, rule, guard, signals}.
  """
  row = {"conflict_id": cf["conflict_id"], "severity": cf["severity"], "outcome": "needs_human", "rule": None, "guard": None, "signals": []}
  a, b = cf["claims"][:2]
  ca, cb = st.claims[a], st.claims[b]
  if cf["severity"] == "P0":
    return row | {"guard": "p0"}
  if opposite_status(ca, cb):
    return row | {"guard": "same-identifier-opposite-status"}
  if cf.get("conflict_type") == "time-evolution-proposed":
    return row | {"outcome": "proposed", "rule": "dated-order"}
  if source_ids(ca) == source_ids(cb) and _docs(st, a) != _docs(st, b):
    return row | {"outcome": "noise", "rule": "byte-copy", "signals": _docs(st, a) + _docs(st, b)}
  if not overlaps(situation(ca["scope"]), situation(cb["scope"])):
    return row | {"outcome": "noise", "rule": "disjoint-scope", "signals": [str(ca["scope"]), str(cb["scope"])]}
  same_doc = _docs(st, a) == _docs(st, b)
  for cid in (a, b):
    labels = _labelled(st, cid, status)
    witness = _replacement(st, cid, index) if labels else None
    if witness and (not same_doc or _SELF_LABEL.search(ca["claim_text"]) or _SELF_LABEL.search(cb["claim_text"])):
      return row | {"outcome": "noise", "rule": "superseded-section", "signals": [*labels, f"replaced by {witness}"]}
  if cf["severity"] == "P2" and bool(_PLAN.search(ca["claim_text"])) != bool(_PLAN.search(cb["claim_text"])):
    return row | {"outcome": "noise", "rule": "plan-vs-state", "signals": [next(c["claim_text"][:80] for c in (ca, cb) if _PLAN.search(c["claim_text"]))]}
  order = _sequential(st, a, b, status)
  if order:
    return row | ({"outcome": "noise"} if cf["severity"] == "P2" else {"outcome": "proposed"}) | {"rule": "sequential-steps", "signals": order}
  return row


def plan(st: State, now: str) -> dict:
  """Triage every open conflict.

  Args:
    st: current state.
    now: run time.

  Returns:
    {"run_id", "rows", "counts", "events"}; events are conflict records for ledger.append.
  """
  status = status_map.files(st)
  index = _unlabelled_claims(st, status)
  rows = [evaluate(st, cf, status, index) for cf in st.open_conflicts()]
  run_id = ids.make_id("tr", now, sorted(r["conflict_id"] for r in rows))
  events = []
  for row in (r for r in rows if r["outcome"] == "noise"):
    triage = {"rule": row["rule"], "version": RULES_VERSION, "signals": row["signals"], "run_id": run_id, "at": now}
    status = "documented-evolution" if row["rule"] in settings.EVOLUTION_RULES else "dismissed"
    events.append({**st.conflicts[row["conflict_id"]], "status": status, "triage": triage})
  counts: dict[str, int] = {}
  for row in rows:
    key = row["outcome"] if row["outcome"] == "needs_human" else f"{row['outcome']}:{row['rule']}"
    counts[key] = counts.get(key, 0) + 1
  return {"run_id": run_id, "rows": rows, "counts": dict(sorted(counts.items())), "events": events}


def undo(st: State, run_id: str) -> list[dict]:
  """Events reopening what one run dismissed.

  Args:
    st: current state.
    run_id: the run.

  Returns:
    Conflict records.
  """
  hit = [c for c in st.conflicts.values() if c["status"] in settings.CLEARED_STATUSES and c.get("triage", {}).get("run_id") == run_id]
  return [{**c, "status": "open", "triage": {**c["triage"], "undone": True}} for c in hit]
