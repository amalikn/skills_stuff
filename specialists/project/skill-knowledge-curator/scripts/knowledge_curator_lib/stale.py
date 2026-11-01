"""Stale conflicts: open conflicts overtaken by a ruling elsewhere, so a reviewer does not answer a question already moved (evaluation.md P21).

Imported, not run. Deterministic: it reads dispositions and recommendations only and cannot see semantic narrowing, so an unflagged
conflict is not proven fresh. Safety: reads state only.
"""

from .state import State

_LIVE = ("CURRENT", "REVIEW_REQUIRED")


def reasons(st: State, cf: dict) -> list[str]:
  """Why one open conflict looks overtaken.

  Args:
    st: current state.
    cf: an open conflict.

  Returns:
    Reasons, empty when none.
  """
  out = [f"member {c} is {st.disposition(c)} (by {st.dispositions[c]['by']})" for c in cf["claims"] if st.disposition(c) not in _LIVE]
  rec = cf.get("recommended_current")
  if rec and st.disposition(rec) not in _LIVE:
    out.append(f"recommendation {rec} is {st.disposition(rec)}")
  return out


def stale_conflicts(st: State) -> list[dict]:
  """Open conflicts that look overtaken.

  Args:
    st: current state.

  Returns:
    [{conflict_id, severity, reasons}] for each one.
  """
  rows = ((cf, reasons(st, cf)) for cf in st.open_conflicts())
  return [{"conflict_id": cf["conflict_id"], "severity": cf["severity"], "reasons": why} for cf, why in rows if why]
