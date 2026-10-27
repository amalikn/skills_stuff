"""Load one project's Goal Guard records from its .gg/ folder and judge its baseline (references/project-layout-and-storage.md).

Imported, not run. Reads only; the one writer of .gg/ files is decisions_log (append) behind --apply in the front ends.

Records read (all optional except project.yaml):
  .gg/project.yaml            project_id, partition, role, vikunja_project_id, hub, ranking, protected_paths, enforcement
  .gg/mvp.yaml                the MVP contract (records.parse_mvp)
  .gg/mappings.yaml           tasks (vikunja_task_id -> acceptance_criterion_id) and milestones (trace links)
  .gg/internal-targets.yaml   the owner's internal targets per milestone, kept apart from commitments (DATE-002)
  .gg/decisions.jsonl         the append-only decision log (decisions_log)
"""

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from . import yaml_io
from .errors import RecordError
from .mvp import Mvp, parse_mvp
from .settings import PARTITIONS

GG = ".gg"
# Records an agent must never edit directly; changes go through the owner's change-control path (MVP-007, MVP-011).
PROTECTED_RECORDS = (".gg/mvp.yaml", ".gg/decisions.jsonl", ".gg/internal-targets.yaml", ".gg/project.yaml")
ROLES = ("hub", "spoke", "standalone")


@dataclass(frozen=True)
class Project:
  """One Goal Guard-registered project.

  Args:
    root: resolved project folder.
    project_id: stable Goal Guard ID.
    partition: apn or me.
    role: hub, spoke or standalone.
    vikunja_project_id: Vikunja project ID, or 0 when not linked.
    config: the whole project.yaml mapping (ranking, hub, protected_paths, enforcement).
    mvp: the contract, or None when absent.
    mvp_error: why mvp.yaml could not be read, or "".
    task_map: Vikunja task ID -> accepted criterion IDs it is mapped to.
    milestones: milestone link mappings from mappings.yaml.
    internal_targets: milestone ID -> owner's internal target (ISO date text).
  """

  root: Path
  project_id: str
  partition: str
  role: str
  vikunja_project_id: int
  config: dict
  mvp: Mvp | None
  mvp_error: str
  task_map: dict[int, tuple[str, ...]] = field(default_factory=dict)
  milestones: tuple[dict, ...] = ()
  internal_targets: dict[str, str] = field(default_factory=dict)

  @property
  def decisions_path(self) -> Path:
    """Return the path of the project's decisions.jsonl.

    Returns:
      root/.gg/decisions.jsonl (it may not exist yet).
    """
    return self.root / GG / "decisions.jsonl"

  def protected_paths(self) -> list[Path]:
    """Return every path an agent may not edit: the Goal Guard records plus any listed in project.yaml protected_paths.

    Returns:
      Resolved paths; a listed path that escapes the project is still returned resolved, so it stays protected.
    """
    listed = list(PROTECTED_RECORDS) + [str(p) for p in self.config.get("protected_paths") or []]
    return [(self.root / p).resolve() for p in listed]


def partition_from_path(path: Path) -> str:
  """Find the partition a path sits in from its folder names.

  Args:
    path: any path; it is resolved first.

  Returns:
    "apn" or "me" for the nearest ancestor folder with that name, or "" when there is none.
  """
  for part in reversed(path.resolve().parts):
    if part in PARTITIONS:
      return part
  return ""


def find_root(path: Path) -> Path | None:
  """Find the nearest folder at or above a path that holds .gg/project.yaml.

  Args:
    path: a file or folder; it need not exist yet (a file about to be written).

  Returns:
    The resolved project root, or None when no ancestor is registered.
  """
  current = path.resolve()
  for candidate in [current, *current.parents]:
    if (candidate / GG / "project.yaml").is_file():
      return candidate
  return None


def load(root: Path) -> Project:
  """Load a project's records.

  Args:
    root: the project folder (holding .gg/project.yaml).

  Returns:
    The Project; an unreadable mvp.yaml is reported in mvp_error rather than raised, so read-only work can continue (fail open
    for inspection, decision rule 2).

  Raises:
    RecordError: project.yaml is missing or invalid, its partition disagrees with the folder it sits in, or mappings.yaml is invalid.
  """
  root = root.resolve()
  config = yaml_io.load_file(root / GG / "project.yaml")
  if not isinstance(config, dict):
    raise RecordError(f"{root}/.gg/project.yaml: expected a mapping")
  project_id = str(config.get("project_id") or "")
  partition = str(config.get("partition") or "")
  role = str(config.get("role") or "standalone")
  if not project_id:
    raise RecordError(f"{root}/.gg/project.yaml: missing project_id")
  if partition not in PARTITIONS:
    raise RecordError(f"{root}/.gg/project.yaml: partition must be one of {PARTITIONS}")
  folder_partition = partition_from_path(root)
  if folder_partition and folder_partition != partition:
    raise RecordError(f"{root}: project.yaml says partition {partition} but the folder is under {folder_partition}")
  if role not in ROLES:
    raise RecordError(f"{root}/.gg/project.yaml: role must be one of {ROLES}")
  mvp, mvp_error = None, ""
  mvp_file = root / GG / "mvp.yaml"
  if mvp_file.exists():
    try:
      mvp = parse_mvp(yaml_io.load_file(mvp_file))
    except RecordError as err:
      mvp_error = str(err)
  task_map, milestones = _load_mappings(root / GG / "mappings.yaml")
  targets_file = root / GG / "internal-targets.yaml"
  targets = yaml_io.load_file(targets_file) if targets_file.exists() else {}
  if not isinstance(targets, dict):
    raise RecordError(f"{targets_file}: expected a mapping of milestone ID to date")
  return Project(
    root=root,
    project_id=project_id,
    partition=partition,
    role=role,
    vikunja_project_id=int(config.get("vikunja_project_id") or 0),
    config=config,
    mvp=mvp,
    mvp_error=mvp_error,
    task_map=task_map,
    milestones=milestones,
    internal_targets={str(k): str(v) for k, v in targets.items()},
  )


def _load_mappings(path: Path) -> tuple[dict[int, tuple[str, ...]], tuple[dict, ...]]:
  """Read mappings.yaml into a task-to-criteria map and the milestone links.

  Args:
    path: the mappings.yaml file; absent means no mappings.

  Returns:
    (task_map, milestones): task ID -> criterion IDs, and the milestone link mappings as given.

  Raises:
    RecordError: the file is not a mapping, or a task entry lacks a numeric vikunja_task_id or a criterion.
  """
  if not path.exists():
    return {}, ()
  data = yaml_io.load_file(path) or {}
  if not isinstance(data, dict):
    raise RecordError(f"{path}: expected a mapping with tasks and milestones")
  task_map: dict[int, list[str]] = {}
  for i, entry in enumerate(data.get("tasks") or []):
    try:
      task_id = int(entry["vikunja_task_id"])
      criterion = str(entry["acceptance_criterion_id"])
    except (KeyError, TypeError, ValueError) as err:
      raise RecordError(f"{path}: tasks[{i}] needs a numeric vikunja_task_id and an acceptance_criterion_id") from err
    task_map.setdefault(task_id, []).append(criterion)
  milestones = tuple(m for m in data.get("milestones") or [] if isinstance(m, dict))
  return {k: tuple(v) for k, v in task_map.items()}, milestones


@dataclass(frozen=True)
class BaselineState:
  """Whether the project has an approved, usable baseline.

  Args:
    approved: True only for an approved contract whose approval is recorded by its owner in decisions.jsonl.
    code: OK, NO_BASELINE, UNREADABLE, DRAFT, NOT_ACTIVE, UNAPPROVED or INVALID.
    clause: the policy clause the state rests on.
    reason: one sentence naming the remedy.
  """

  approved: bool
  code: str
  clause: str
  reason: str


def baseline_state(project: Project, approvals: list[dict]) -> BaselineState:
  """Judge the project's baseline (decision rule 2).

  Args:
    project: the loaded project.
    approvals: approval entries from decisions.jsonl (decisions_log.approvals).

  Returns:
    The BaselineState; approved is True only when every check passes.
  """
  mvp = project.mvp
  if project.mvp_error:
    return BaselineState(False, "UNREADABLE", "MVP-012", f"mvp.yaml cannot be read: {project.mvp_error}")
  if mvp is None:
    return BaselineState(False, "NO_BASELINE", "MVP-001", "no .gg/mvp.yaml: write the MVP contract with the owner and have it approved")
  if mvp.status == "draft":
    return BaselineState(False, "DRAFT", "MVP-003", f"{mvp.revision} is a draft: the owner approves it before scope-changing work")
  if mvp.status != "approved":
    return BaselineState(False, "NOT_ACTIVE", "MVP-011", f"{mvp.revision} is {mvp.status}: a new approved revision is needed")
  blocking = [i for i in mvp.issues if "approval" in i or "no acceptance" in i or "duplicate" in i]
  if blocking:
    return BaselineState(False, "INVALID", "MVP-001", "; ".join(blocking))
  owner_approvals = [a for a in approvals if a.get("contract_revision_after") == mvp.revision and a.get("actor") == mvp.owner]
  if not owner_approvals:
    return BaselineState(False, "UNAPPROVED", "MVP-007", f"no approval of {mvp.revision} by owner {mvp.owner} in .gg/decisions.jsonl")
  return BaselineState(True, "OK", "MVP-001", f"{mvp.revision} approved by {mvp.owner}")


def verify_approval_commit(project: Project, timeout: float) -> str:
  """Check the approval's signed commit with git (decision D3); the signing setup is still open, so this only reports.

  Args:
    project: the loaded project.
    timeout: seconds for the git subprocess.

  Returns:
    "verified", "failed: <git message>", or "unverified: <why>" when there is no git:<sha> evidence_ref or git is unavailable.
  """
  ref = str((project.mvp.approval if project.mvp else {}).get("evidence_ref", ""))
  if not ref.startswith("git:"):
    return "unverified: approval evidence_ref is not git:<commit> (decision D3 setup pending)"
  argv = ["git", "-C", str(project.root), "verify-commit", ref[4:]]
  try:
    run = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, check=False)
  except (OSError, subprocess.TimeoutExpired) as err:
    return f"unverified: git verify-commit did not run ({type(err).__name__})"
  if run.returncode == 0:
    return "verified"
  return "failed: " + (run.stderr.strip().splitlines() or ["no signature"])[-1][:200]


def resolve_inside(root: Path, relative: str) -> Path | None:
  """Resolve a path a proposal names, refusing traversal and symlink escapes (GG-404, GG-405).

  Args:
    root: the project root (resolved).
    relative: the path as written, relative to the root or absolute.

  Returns:
    The resolved path when it stays inside the root, or None when it escapes or cannot be resolved.
  """
  if any(ch in relative for ch in "*?[") or not relative.strip():
    return None
  try:
    target = (root / relative).resolve()
  except OSError, RuntimeError:
    return None
  return target if target.is_relative_to(root.resolve()) else None
