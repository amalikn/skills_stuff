"""Deterministic acceptance gates over a project's ledgers, sources and knowledge pages (design doc 13.1; handoff 7 step 8).

Imported, not run. Errors fail the run (exit 3, or 5 when the cause is a changed source); warnings are reported only. Checks:
inventory freshness, disposition vocabulary, evidence for CURRENT claims (INV-005), references between records, evidence re-hash,
promoted pages unchanged since promotion, knowledge pages matching a fresh rendering, and section coverage (INV-003).
Safety: read-only.
"""

from . import claims as claims_mod
from . import ids, inventory, render, settings
from .errors import KcError
from .evidence import Reader, recheck
from .state import State


def _inventory_checks(st: State, out: dict) -> None:
  """Live files against the inventory.

  Args:
    st: current state.
    out: result being built.
  """
  files, _ = inventory.discover(st.root, st.cfg)
  known = st.source_by_path()
  for rel in files:
    src = known.get(rel)
    if src is None:
      out["warnings"].append(f"{rel}: not inventoried (run kc inventory)")
    elif ids.sha256_bytes((st.root / rel).read_bytes()) != src["sha256"]:
      out["errors"].append(f"{rel}: changed since inventory (run kc inventory)")
      out["source_changed"] = True
  for rel in sorted(set(known) - set(files)):
    out["errors"].append(f"{rel}: in the inventory but missing on disk")
    out["source_changed"] = True


def _record_checks(st: State, out: dict) -> None:
  """Vocabulary, INV-005 and cross-record references.

  Args:
    st: current state.
    out: result being built.
  """
  for cid, ev in sorted(st.dispositions.items()):
    if cid not in st.claims:
      out["errors"].append(f"disposition for unknown claim {cid}")
    if ev["disposition"] not in settings.DISPOSITIONS:
      out["errors"].append(f"{cid}: unknown disposition {ev['disposition']}")
    for key in ("successor", "duplicate_of"):
      if ev.get(key) and ev[key] not in st.claims:
        out["errors"].append(f"{cid}: {key} {ev[key]} does not exist")
  for cid, c in sorted(st.claims.items()):
    if st.disposition(cid) == "CURRENT" and not c["evidence"] and not c.get("decision_id"):
      out["errors"].append(f"{cid}: CURRENT without evidence or decision (INV-005)")
  for cf in st.conflicts.values():
    out["errors"].extend(f"{cf['conflict_id']}: unknown claim {c}" for c in cf["claims"] if c not in st.claims)
  decided = {d["decision_id"] for d in st.decisions}
  for d in st.decisions:
    if d["conflict_id"] not in st.conflicts:
      out["errors"].append(f"{d['decision_id']}: unknown conflict {d['conflict_id']}")
    if d.get("previous_decision_id") and d["previous_decision_id"] not in decided:
      out["errors"].append(f"{d['decision_id']}: previous decision {d['previous_decision_id']} missing")


def _evidence_checks(st: State, out: dict) -> None:
  """Re-hash every evidence span of live claims.

  Args:
    st: current state.
    out: result being built.
  """
  reader = Reader(st)
  for cid, c in sorted(st.claims.items()):
    if st.disposition(cid) in ("REJECTED",):
      continue
    for ev in c["evidence"]:
      res = recheck(reader, ev)
      out["checks"]["evidence"] += 1
      if res["status"] in ("broken", "missing"):
        out["errors"].append(f"{cid}: evidence {ev['path']} L{ev['line_start']}-{ev['line_end']} is {res['status']}")
        out["source_changed"] = True
      elif res["status"] == "relocated":
        out["warnings"].append(f"{cid}: evidence {ev['path']} moved to L{res['lines'][0]}-{res['lines'][1]} (re-extract to refresh)")


def _page_checks(st: State, out: dict) -> None:
  """Promoted pages unchanged; derived pages match a fresh rendering.

  Args:
    st: current state.
    out: result being built.
  """
  for page, rec in sorted(st.promotions.items()):
    if rec["status"] != "promoted":
      continue
    disk = st.root / page
    if not disk.exists():
      out["errors"].append(f"{page}: promoted page missing")
    elif render.body_digest(disk.read_text(encoding="utf-8")) != rec["page_digest"]:
      out["errors"].append(f"{page}: promoted page changed since {rec['decision_id']} (edits must go through kc review / kc promote)")
  if not (st.root / st.cfg["knowledge_dir"]).exists():
    return
  try:
    rendered = render.render(st)
  except KcError as err:
    out["errors"].append(str(err))
    return
  for rel, text in sorted(rendered.files.items()):
    disk = st.root / rel
    if not disk.exists() or disk.read_text(encoding="utf-8") != text:
      out["warnings"].append(f"{rel}: differs from a fresh rendering (run kc render --apply)")
  out["warnings"].extend(f"{rel}: proposal pending for a promoted page" for rel in sorted(rendered.proposals))


def run(st: State) -> dict:
  """Run every check.

  Args:
    st: current state.

  Returns:
    {"ok", "errors", "warnings", "source_changed", "checks"}.
  """
  out = {"errors": [], "warnings": [], "source_changed": False, "checks": {"evidence": 0}}
  _inventory_checks(st, out)
  _record_checks(st, out)
  _evidence_checks(st, out)
  _page_checks(st, out)
  cov = claims_mod.coverage(st)["counts"]
  out["checks"]["coverage"] = cov
  if cov.get("pending") or cov.get("pending-review"):
    out["warnings"].append(f"{cov.get('pending', 0) + cov.get('pending-review', 0)} section(s) not yet accounted for (kc worksheet)")
  out["ok"] = not out["errors"]
  return out
