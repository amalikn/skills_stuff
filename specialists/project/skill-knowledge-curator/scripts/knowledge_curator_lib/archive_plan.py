"""Archive plan: which sources a set of promoted pages has fully absorbed, what still links to them, and a restore rehearsal.

Imported, not run. v1 plans only (operator, 2026-10-27): it never moves, copies into the project or deletes a source. A source is a
candidate when every claim citing it sits on a promoted page or is history, no such claim awaits review, every section of it is
accounted for, and its bytes still match the inventory. The rehearsal copies candidates into a temporary folder under the archive
layout, verifies every hash, copies them back to a second temporary folder and verifies again (design doc 8 Phase F, steps 3-4).
Safety: reads the project; writes only inside a temporary directory it deletes.
"""

import posixpath
import re
import shutil
import tempfile
from pathlib import Path

from . import claims as claims_mod
from . import ids
from .state import State

_LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
_HISTORY = ("HISTORICAL", "SUPERSEDED", "DUPLICATE", "REJECTED")


def _promoted_categories(st: State) -> set[str]:
  """Categories whose page is promoted.

  Args:
    st: current state.

  Returns:
    Category names.
  """
  return {p.rsplit("/", 1)[-1][:-3] for p, rec in st.promotions.items() if rec["status"] == "promoted"}


def _blockers(st: State, src: dict, cats: set[str], cov: dict) -> list[str]:
  """Reasons a source cannot be archived yet.

  Args:
    st: current state.
    src: source record.
    cats: promoted categories.
    cov: coverage rows keyed by section ID.

  Returns:
    Messages; empty means candidate.
  """
  out = []
  citing = [cid for cid, c in st.claims.items() if any(e["source_id"] == src["source_id"] for e in c["evidence"])]
  if not citing:
    out.append("no claim cites it")
  for cid in citing:
    c, disp = st.claims[cid], st.effective(cid)
    if disp == "REVIEW_REQUIRED":
      out.append(f"{cid} awaits review")
    elif disp not in _HISTORY and c["primary_category"] not in cats:
      out.append(f"{cid} is on unpromoted page {c['primary_category']}")
  pending = [r for r in cov.values() if r["path"] == src["path"] and r["status"] in ("pending", "pending-review")]
  if pending:
    out.append(f"{len(pending)} section(s) not accounted for")
  live = st.root / src["path"]
  if not live.exists() or ids.sha256_bytes(live.read_bytes()) != src["sha256"]:
    out.append("bytes changed since inventory")
  return out


def _referrers(st: State, paths: set[str]) -> dict[str, list[str]]:
  """Markdown files outside the candidates that link to a candidate.

  Args:
    st: current state.
    paths: candidate paths.

  Returns:
    candidate path -> sorted referring paths.
  """
  out: dict[str, list[str]] = {}
  for rel in sorted(st.source_by_path()):
    if rel in paths:
      continue
    text = (st.root / rel).read_text(encoding="utf-8", errors="replace")
    for target in _LINK.findall(text):
      norm = posixpath.normpath(posixpath.join(posixpath.dirname(rel), target))
      if norm in paths:
        out.setdefault(norm, []).append(rel)
  return {k: sorted(set(v)) for k, v in sorted(out.items())}


def rehearse_restore(root: Path, entries: list[dict]) -> dict:
  """Copy candidates to a temporary archive layout and back, verifying every hash both ways.

  Args:
    root: project root.
    entries: manifest entries (path, target, sha256).

  Returns:
    {"ok": bool, "checked": n, "failures": [...]}.
  """
  failures = []
  with tempfile.TemporaryDirectory(prefix="kc-restore-") as tmp:
    arch, back = Path(tmp, "archive"), Path(tmp, "restored")
    for e in entries:
      a, b = arch / e["target"], back / e["path"]
      a.parent.mkdir(parents=True, exist_ok=True)
      b.parent.mkdir(parents=True, exist_ok=True)
      shutil.copy2(root / e["path"], a)
      shutil.copy2(a, b)
      if ids.sha256_bytes(a.read_bytes()) != e["sha256"] or ids.sha256_bytes(b.read_bytes()) != e["sha256"]:
        failures.append(e["path"])
  return {"ok": not failures, "checked": len(entries), "failures": failures}


def plan(st: State) -> dict:
  """Archive plan for the current promotions.

  Args:
    st: current state.

  Returns:
    {"batch_id", "promoted_pages", "entries", "blocked", "referrers", "restore_rehearsal", "ready"}.
  """
  cats = _promoted_categories(st)
  cov = {r["section_id"]: r for r in claims_mod.coverage(st)["sections"]}
  entries, blocked = [], {}
  for rel, src in sorted(st.source_by_path().items()):
    why = _blockers(st, src, cats, cov)
    if why:
      blocked[rel] = why
    else:
      entries.append({"source_id": src["source_id"], "path": rel, "sha256": src["sha256"], "size_bytes": src["size_bytes"]})
  batch = ids.make_id("ab", sorted(e["sha256"] for e in entries), length=10)
  for e in entries:
    e["target"] = f"{st.cfg['archive_dir']}/{batch}/{e['path']}"
  refs = _referrers(st, {e["path"] for e in entries})
  rehearsal = rehearse_restore(st.root, entries) if entries else {"ok": True, "checked": 0, "failures": []}
  return {
    "batch_id": batch,
    "promoted_pages": sorted(p for p, r in st.promotions.items() if r["status"] == "promoted"),
    "entries": entries,
    "blocked": blocked,
    "referrers": refs,
    "restore_rehearsal": rehearsal,
    "ready": bool(entries) and not refs and rehearsal["ok"],
    "note": "plan only: v1 never moves sources; a separate approved run will",
  }
