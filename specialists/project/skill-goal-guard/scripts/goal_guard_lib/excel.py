"""The openpyxl seam: build the one management workbook sample from milestone links (pilot feature 34; hub-management-and-dates).

Imported, not run. Upgrade test: tests/test_trace_excel_yaml.py (Seams). The workbook is a generated export, labelled with its generation time and
baseline revision, never the authority: the issued workbook stays the historical snapshot (handoff §25.1). Columns default to
commitment, status, forecast, risk and evidence; the owner's internal target is left out unless asked (DATE-006). Forecast is
always "unknown": no durations are invented (DATE-003). A milestone is delivered only with evidence for each criterion (DATE-007).
"""

import datetime as dt
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font

from .project import Project
from .records import parse_date

COLUMNS = ("milestone_id", "milestone_revision", "commitment", "status", "forecast", "risk", "evidence", "baseline_revision")


def rows(project: Project, today: dt.date, include_internal: bool) -> list[dict]:
  """Build one row per milestone link.

  Args:
    project: the spoke project.
    today: the date risk is judged on.
    include_internal: add the owner's internal target column.

  Returns:
    Row mappings in milestone order.
  """
  out = []
  for m in project.milestones:
    mid = str(m.get("milestone_id", ""))
    commitment = parse_date(m.get("commitment_date"), f"milestone {mid} commitment_date")
    criteria = [str(c) for c in m.get("acceptance_criterion_ids") or []]
    evidence = m.get("acceptance_evidence") or {}
    delivered = bool(criteria) and all(evidence.get(c) for c in criteria)
    if delivered:
      risk = "none"
    elif commitment and commitment < today:
      risk = "missed commitment"
    elif commitment and (commitment - today).days <= 14:
      risk = "deadline at risk"
    else:
      risk = "unknown" if not commitment else "none known"
    row = {
      "milestone_id": mid,
      "milestone_revision": str(m.get("milestone_revision", "")),
      "commitment": commitment.isoformat() if commitment else "",
      "status": "delivered" if delivered else "open",
      "forecast": "unknown",
      "risk": risk,
      "evidence": "; ".join(f"{c}: {evidence[c]}" for c in criteria if evidence.get(c)) or "none",
      "baseline_revision": str((m.get("plan_baseline") or {}).get("revision", "")),
    }
    if include_internal:
      row["internal_target"] = project.internal_targets.get(mid, "")
    out.append(row)
  return out


def write(path: Path, project: Project, table: list[dict], generated_at: str) -> None:
  """Write the workbook: a Milestones sheet and an About sheet with provenance.

  Args:
    path: the .xlsx to write (the caller holds the --apply gate).
    project: the project, for the About sheet.
    table: rows from rows().
    generated_at: ISO-8601 generation time.
  """
  book = Workbook()
  sheet = book.active
  sheet.title = "Milestones"
  columns = list(COLUMNS) + (["internal_target"] if table and "internal_target" in table[0] else [])
  sheet.append(columns)
  for cell in sheet[1]:
    cell.font = Font(bold=True)
  for row in table:
    sheet.append([row.get(c, "") for c in columns])
  about = book.create_sheet("About")
  for line in (
    ("generated_by", "skill-goal-guard goal_guard_excel.py"),
    ("generated_at", generated_at),
    ("project_id", project.project_id),
    ("mvp_revision", project.mvp.revision if project.mvp else "none"),
    ("authority", "generated export; the issued workbook and the hub plan remain the authority"),
  ):
    about.append(line)
  path.parent.mkdir(parents=True, exist_ok=True)
  book.save(path)
