"""Status report: counts across the ledgers, coverage, conflicts by severity and page status, for humans and closeout records.

Imported, not run. Safety: read-only.
"""

from . import claims as claims_mod
from .state import State


def build(st: State) -> dict:
  """Summarise one project.

  Args:
    st: current state.

  Returns:
    Counts keyed by area.
  """
  disp: dict[str, int] = {}
  for cid in st.claims:
    d = st.effective(cid)
    disp[d] = disp.get(d, 0) + 1
  sev: dict[str, int] = {}
  for cf in st.open_conflicts():
    sev[cf["severity"]] = sev.get(cf["severity"], 0) + 1
  live = st.source_by_path()
  return {
    "project": st.cfg["project_id"],
    "sources": {"live": len(live), "unsupported": sum(s["ingestion_state"] == "unsupported" for s in live.values())},
    "coverage": claims_mod.coverage(st)["counts"],
    "claims": {"total": len(st.claims), "by_disposition": dict(sorted(disp.items()))},
    "conflicts": {"open_by_severity": dict(sorted(sev.items())), "resolved": sum(c["status"] == "resolved" for c in st.conflicts.values())},
    "decisions": len(st.decisions),
    "promoted_pages": sorted(p for p, r in st.promotions.items() if r["status"] == "promoted"),
  }
