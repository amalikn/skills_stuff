"""Promotion of one category page from derived view to authoritative, behind the configured gates, and its revocation.

Imported, not run. Gates (operator, 2026-10-27; evidence_verified on by default): no open P0/P1 conflict on the page; an operator
approval bound to the exact page body digest; a governing file (AGENTS.md by default) that points agents at the page; every
evidence span still matching its source. The page must also equal a fresh rendering. The curator never edits governing files: it
reports the line to add. Revocation appends a new record; the earlier one stays (INV-016). Safety: returns records and texts.
"""

import datetime as dt

from . import ids, render
from .errors import InputError
from .evidence import Reader, recheck
from .state import State


def _gate_conflicts(page: dict) -> dict:
  """no_open_p0_p1 gate.

  Args:
    page: rendered page summary.

  Returns:
    Gate result.
  """
  ok = not page["open_p0_p1"]
  return {"pass": ok, "detail": "no open P0/P1 conflict" if ok else "open: " + ", ".join(page["open_p0_p1"])}


def _gate_governing(st: State, path: str) -> dict:
  """governing_files gate: a governing file names the page path.

  Args:
    st: current state.
    path: project-relative page path.

  Returns:
    Gate result with the suggested line when it fails.
  """
  for name in st.cfg["governing_files"]:
    gov = st.root / name
    if gov.exists() and path in gov.read_text(encoding="utf-8"):
      return {"pass": True, "detail": f"{name} references {path}"}
  first = st.cfg["governing_files"][0] if st.cfg["governing_files"] else "AGENTS.md"
  return {
    "pass": False,
    "detail": f"add to {first}: '- Authoritative {path.rsplit('/', 1)[-1][:-3]} knowledge: [{path}]({path})' (the curator does not edit it)",
  }


def _gate_evidence(st: State, cat: str) -> dict:
  """evidence_verified gate: every evidence span of the page's current claims still matches its source.

  Args:
    st: current state.
    cat: page category.

  Returns:
    Gate result; relocated spans pass with a note.
  """
  reader, bad, moved = Reader(st), [], []
  for cid, c in sorted(st.claims.items()):
    if c["primary_category"] != cat or st.effective(cid) != "CURRENT":
      continue
    for ev in c["evidence"]:
      status = recheck(reader, ev)["status"]
      if status in ("broken", "missing"):
        bad.append(f"{cid} {ev['path']} L{ev['line_start']}")
      elif status == "relocated":
        moved.append(cid)
  if bad:
    return {"pass": False, "detail": "evidence no longer matches: " + "; ".join(bad)}
  return {"pass": True, "detail": f"all evidence matches{'; relocated in ' + ', '.join(sorted(set(moved))) if moved else ''}"}


def evaluate(st: State, path: str, approve_digest: str | None = None) -> dict:
  """Check every gate for one page.

  Args:
    st: current state.
    path: project-relative page path, e.g. knowledge/architecture.md.
    approve_digest: the body digest the operator approved.

  Returns:
    {"page", "digest", "fresh", "gates": {name: {pass, detail}}, "ready", "next"}.

  Raises:
    InputError: not a category page, or it was never rendered.
  """
  rendered = render.render(st)
  page = next((p for p in rendered.pages if p["path"] == path), None)
  disk = st.root / path
  if page is None or not disk.exists():
    raise InputError(f"{path} is not a rendered category page (run kc render --apply)")
  text = disk.read_text(encoding="utf-8")
  digest = render.body_digest(text)
  fresh = rendered.files.get(path, text) == text
  checks = {
    "no_open_p0_p1": lambda: _gate_conflicts(page),
    "operator_decision": lambda: {
      "pass": approve_digest == digest,
      "detail": "approved digest matches" if approve_digest == digest else "pass --approve-digest " + digest,
    },
    "governing_files": lambda: _gate_governing(st, path),
    "evidence_verified": lambda: _gate_evidence(st, page["category"]),
  }
  gates = {name: checks[name]() for name in st.cfg["promotion_gates"]}
  ready = fresh and all(g["pass"] for g in gates.values())
  nxt = "ready: rerun with --apply" if ready else ("run kc render --apply first" if not fresh else "fix the failing gates")
  return {"page": path, "digest": digest, "fresh": fresh, "not_settled": page["not_settled"], "gates": gates, "ready": ready, "next": nxt}


def promotion_record(st: State, result: dict, actor: str, reason: str, now: dt.datetime, status: str = "promoted") -> dict:
  """Promotion (or revocation) record for decisions.jsonl.

  Args:
    st: current state.
    result: evaluate() output (gates are stored with the record).
    actor: who approved.
    reason: why.
    now: time (timezone-aware).
    status: promoted or revoked.

  Returns:
    The record.

  Raises:
    InputError: revoking a page that is not promoted.
  """
  prior = st.promotions.get(result["page"])
  if status == "revoked" and (not prior or prior["status"] != "promoted"):
    raise InputError(f"{result['page']} is not promoted")
  at = now.isoformat(timespec="seconds")
  return {
    "record": "promotion",
    "decision_id": ids.make_id("dp", result["page"], status, at),
    "page": result["page"],
    "page_digest": result["digest"],
    "status": status,
    "actor": actor,
    "decided_at": at,
    "reason": reason,
    "gates": result["gates"],
    "previous_decision_id": prior["decision_id"] if prior else None,
  }
