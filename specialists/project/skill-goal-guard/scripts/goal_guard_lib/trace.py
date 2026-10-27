"""Trace a management milestone to its plan baseline, MVP criteria, target-map target and Vikunja tasks (pilot step 7).

Imported, not run. Read-only: it hashes and reads files in place and asks git whether a commit exists; it never edits the hub,
the target map or Vikunja (references/hub-management-and-dates.md, references/project-layout-and-storage.md Existing maps).
A link is "verified" only when every check passes; any failed or unknown check makes it REVIEW, never a silent fix.

Revisions are written as sha256:<hex> (content hash of the file) or git:<commit> (a commit that must exist in the file's repo).
"""

import hashlib
import subprocess
from pathlib import Path

from . import yaml_io
from .errors import RecordError
from .project import Project
from .records import parse_date
from .tasks import TaskSet


def file_revision(path: Path) -> str:
  """Hash a file's content.

  Args:
    path: the file.

  Returns:
    "sha256:<hex>".
  """
  return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def check_revision(path: Path, revision: str, timeout: float) -> tuple[bool, str]:
  """Compare a file with the revision a link pins.

  Args:
    path: the file (must exist).
    revision: sha256:<hex> or git:<commit>.
    timeout: seconds for the git subprocess.

  Returns:
    (ok, detail): ok when the hash matches or the commit exists and contains the file.
  """
  if revision.startswith("sha256:"):
    actual = file_revision(path)
    return actual == revision, "content matches" if actual == revision else f"content changed: now {actual[:19]}..."
  if revision.startswith("git:"):
    argv = ["git", "-C", str(path.parent), "cat-file", "-e", f"{revision[4:]}:./{path.name}"]
    try:
      run = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as err:
      return False, f"git did not answer ({type(err).__name__})"
    return run.returncode == 0, "file present at that commit" if run.returncode == 0 else "commit or file not found in git"
  return False, f"revision {revision!r} is neither sha256:<hex> nor git:<commit>"


def _target_ids(data: object) -> set[str]:
  """Collect every id value in a parsed target map, at any depth.

  Args:
    data: the parsed YAML.

  Returns:
    The set of id values (as text) and of mapping keys under a targets mapping.
  """
  found: set[str] = set()
  stack = [data]
  while stack:
    item = stack.pop()
    if isinstance(item, dict):
      if "id" in item and isinstance(item["id"], str | int):
        found.add(str(item["id"]))
      if isinstance(item.get("targets"), dict):
        found.update(str(k) for k in item["targets"])
      stack.extend(item.values())
    elif isinstance(item, list):
      stack.extend(item)
  return found


def _check(name: str, ok: bool, detail: str) -> dict:
  """Build one check record.

  Args:
    name: check name.
    ok: whether it passed.
    detail: what was found.

  Returns:
    {"check", "ok", "detail"}.
  """
  return {"check": name, "ok": ok, "detail": detail}


def _plan_checks(project: Project, link: dict, timeout: float) -> list[dict]:
  """Check the hub plan document: present, at the pinned revision, and naming the milestone.

  Args:
    project: the spoke project.
    link: the milestone mapping.
    timeout: seconds per git call.

  Returns:
    Check records.
  """
  plan = link.get("plan_baseline") or {}
  doc = str(plan.get("document_ref") or "")
  if not doc:
    return [_check("plan_baseline", False, "no document_ref")]
  path = (project.root / doc).resolve()
  if not path.is_file():
    return [_check("plan_baseline", False, f"{doc} not found")]
  ok, detail = check_revision(path, str(plan.get("revision") or ""), timeout)
  mid = str(link.get("milestone_id", ""))
  named = bool(mid) and mid in path.read_text(encoding="utf-8", errors="replace")
  return [
    _check("plan_baseline", ok, f"{doc}: {detail}"),
    _check("milestone_in_plan", named, f"{mid or 'milestone ID'} {'named' if named else 'not found'} in {doc}"),
  ]


def _criteria_check(project: Project, criteria: list[str]) -> dict:
  """Check that the milestone's criteria are accepted criteria of the MVP.

  Args:
    project: the spoke project.
    criteria: criterion IDs the link lists.

  Returns:
    One check record.
  """
  if project.mvp is None:
    return _check("mvp_criteria", False, "no MVP contract")
  unknown = sorted(set(criteria) - project.mvp.criterion_ids())
  if unknown:
    return _check("mvp_criteria", False, f"unknown {unknown}")
  return _check("mvp_criteria", bool(criteria), f"{criteria} in {project.mvp.revision}" if criteria else "none listed")


def _target_checks(project: Project, link: dict, timeout: float) -> list[dict]:
  """Check the target map: present, at the pinned revision, and holding the target ID (none is invented when the map has none).

  Args:
    project: the spoke project.
    link: the milestone mapping.
    timeout: seconds per git call.

  Returns:
    Check records; none when the link names no target map.
  """
  ref = str(link.get("target_source_ref") or "")
  if not ref:
    return []
  path = (project.root / ref).resolve()
  if not path.is_file():
    return [_check("target_map", False, f"{ref} not found")]
  ok, detail = check_revision(path, str(link.get("target_source_revision") or ""), timeout)
  checks = [_check("target_map_revision", ok, detail)]
  target_id = str(link.get("target_id") or "")
  if not target_id:
    return checks + [_check("target_id", True, "the map provides no ID; none invented (propose an ID strategy to the owner)")]
  try:
    found = target_id in _target_ids(yaml_io.load_file(path))
    detail = f"{target_id} {'found' if found else 'not found'} in {ref}"
  except RecordError as err:
    found, detail = False, str(err)
  return checks + [_check("target_id", found, detail)]


def _task_checks(project: Project, link: dict, tasks: TaskSet, criteria: list[str]) -> list[dict]:
  """Check the linked Vikunja tasks exist and map to the milestone's criteria.

  Args:
    project: the spoke project.
    link: the milestone mapping.
    tasks: the task source.
    criteria: the milestone's criterion IDs.

  Returns:
    Check records.
  """
  task_ids = [int(t) for t in link.get("vikunja_task_ids") or []]
  missing = [t for t in task_ids if t not in tasks.tasks]
  present = f"missing {missing} in {tasks.source}" if missing else f"{task_ids} present" if task_ids else "none linked"
  unmapped = [t for t in task_ids if not set(project.task_map.get(t, ())) & set(criteria)]
  mapped = f"tasks {unmapped} not mapped to this milestone's criteria" if unmapped else "every task maps to a listed criterion"
  return [_check("vikunja_tasks", bool(task_ids) and not missing, present), _check("tasks_mapped_to_criteria", not unmapped, mapped)]


def trace_milestone(project: Project, link: dict, tasks: TaskSet, timeout: float) -> dict:
  """Check one milestone link.

  Args:
    project: the spoke project holding the link in mappings.yaml.
    link: the milestone mapping.
    tasks: the task source.
    timeout: seconds per git call.

  Returns:
    {"milestone_id", "result": verified | REVIEW, "checks": [{check, ok, detail}], "commitment", "internal_target"}.
  """
  criteria = [str(c) for c in link.get("acceptance_criterion_ids") or []]
  checks = _plan_checks(project, link, timeout) + [_criteria_check(project, criteria)]
  checks += _target_checks(project, link, timeout) + _task_checks(project, link, tasks, criteria)
  mid = str(link.get("milestone_id", ""))
  commitment = parse_date(link.get("commitment_date"), f"milestone {mid} commitment_date")
  internal = parse_date(project.internal_targets.get(mid), f"internal target {mid}")
  if commitment and internal and internal > commitment:
    checks.append(_check("internal_target_order", False, "internal target is after the commitment"))
  return {
    "milestone_id": mid,
    "result": "verified" if all(c["ok"] for c in checks) else "REVIEW",
    "mapping_status": link.get("mapping_status", "proposed"),
    "commitment": commitment.isoformat() if commitment else None,
    "internal_target": internal.isoformat() if internal else None,
    "forecast": "unknown",
    "checks": checks,
  }
