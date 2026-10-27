"""The GoalGuard decision rules: PROCEED / PARK / REVIEW / BLOCK for one proposal (references/decision-rules.md, Evaluation order).

Imported, not run. Pure policy: no I/O; the caller loads the project, its baseline state and the tasks. Steps run in the
reference's order and stop at the first verdict. Step 8 (semantic necessity) cannot be judged by code; it checks that the agent
recorded its necessity, smallest step and stop condition, and that the cited criterion is one this task is mapped to.
"""

import datetime as dt
from dataclasses import dataclass, field

from .mvp import Blocker
from .project import BaselineState, Project, partition_from_path, resolve_inside
from .records import APPROVAL_KEYS, Proposal, Task, Verdict
from .tasks import TaskSet


def _verdict(proposal: Proposal, verdict: str, code: str, clause: str, reason: str, revision: str, now: dt.datetime, **details) -> Verdict:
  """Build a Verdict.

  Args:
    proposal: the proposal assessed.
    verdict: PROCEED, PARK, REVIEW or BLOCK.
    code: reason code.
    clause: policy clause.
    reason: sentence naming the remedy.
    revision: contract revision or "none".
    now: decision time.
    **details: extra facts to carry.

  Returns:
    The Verdict; REVIEW and BLOCK require the owner except a missing task (the agent can fix that itself).
  """
  owner = verdict in ("REVIEW", "BLOCK") and code not in ("NO_TASK", "UNMET_DEPENDENCY", "NECESSITY_UNRECORDED")
  return Verdict(
    proposal_id=proposal.proposal_id,
    verdict=verdict,
    reason_code=code,
    clause=clause,
    reason=reason,
    contract_revision=revision,
    requires_owner_approval=owner,
    decided_at=now.isoformat(timespec="seconds"),
    task_id=proposal.task_id,
    evidence_refs=proposal.evidence_refs,
    details=details,
  )


def assess(proposal: Proposal, project: Project, baseline: BaselineState, tasks: TaskSet, authorised: str, now: dt.datetime) -> Verdict:
  """Decide one proposal.

  Args:
    proposal: the proposal.
    project: the loaded project it targets.
    baseline: project.baseline_state() for that project.
    tasks: the task source (live or snapshot).
    authorised: the partition this session may act in, or "" for the project's own.
    now: the decision time (timezone-aware).

  Returns:
    The Verdict.
  """
  ctx = _Context(proposal, project, baseline, tasks, authorised)
  revision = project.mvp.revision if project.mvp else "none"
  for step in STEPS:
    finding = step(ctx)
    if finding is not None:
      verdict, code, clause, reason, details = finding
      return _verdict(proposal, verdict, code, clause, reason, revision, now, **details)
  basis = f"registered blocker {ctx.blocker.id}" if ctx.blocker else f"criterion {ctx.cited}"
  reason = f"task {ctx.task.id} advances {basis} of {revision}; do only the smallest step"
  # The file list travels with the verdict: the hook lets edits through only to these files (second line after the semantic gate).
  return _verdict(proposal, "PROCEED", "IN_SCOPE", "MVP-002", reason, revision, now, proposed_files=list(proposal.proposed_files))


@dataclass
class _Context:
  """What the steps read, plus what earlier steps found (the task, its mapped criteria, the cited blocker).

  Args:
    proposal: the proposal.
    project: the project.
    baseline: its baseline state.
    tasks: the task source.
    authorised: the session's partition, or "".
  """

  proposal: Proposal
  project: Project
  baseline: BaselineState
  tasks: TaskSet
  authorised: str
  task: Task | None = None
  mapped: set[str] = field(default_factory=set)
  blocker: Blocker | None = None
  cited: str = ""


Finding = tuple[str, str, str, str, dict]


def _step_context(ctx: _Context) -> Finding | None:
  """Step 1: one partition, the right project, paths inside it (PORT-005, GG-404).

  Args:
    ctx: the evaluation context.

  Returns:
    A BLOCK or REVIEW finding, or None to continue.
  """
  p, proj = ctx.proposal, ctx.project
  if ctx.authorised and proj.partition != ctx.authorised:
    return ("BLOCK", "CROSS_PARTITION", "PORT-005", f"project is in {proj.partition}; this session is authorised for {ctx.authorised}", {})
  if p.project_id != proj.project_id:
    return ("BLOCK", "WRONG_PROJECT", "PORT-005", f"proposal names project {p.project_id}, not {proj.project_id}", {})
  for raw in p.proposed_files + tuple(r for r in p.evidence_refs if "/" in r and "://" not in r):
    other = partition_from_path((proj.root / raw).resolve())
    if other and other != proj.partition:
      return ("BLOCK", "CROSS_PARTITION", "PORT-005", f"{raw} is in the {other} partition", {"path": raw})
    if raw in p.proposed_files and resolve_inside(proj.root, raw) is None:
      return ("REVIEW", "PATH_UNRESOLVED", "GG-404", f"{raw} escapes the project or cannot be resolved; name a path inside it", {"path": raw})
  return None


def _step_read_only(ctx: _Context) -> Finding | None:
  """Read-only inspection fails open (pack 00 rule 4); discussion never changes scope (T12, T13).

  Args:
    ctx: the evaluation context.

  Returns:
    A PROCEED finding for inspect or discuss, else None.
  """
  if ctx.proposal.intent in ("inspect", "discuss"):
    return ("PROCEED", "READ_ONLY", "MVP-012", f"{ctx.proposal.intent}: no scope change, nothing to approve", {})
  return None


def _step_baseline(ctx: _Context) -> Finding | None:
  """Step 2: an approved baseline (MVP-001, MVP-003, MVP-012).

  Args:
    ctx: the evaluation context.

  Returns:
    A BLOCK finding when the baseline is not approved, else None.
  """
  b = ctx.baseline
  return None if b.approved else ("BLOCK", b.code, b.clause, b.reason, {})


def _step_task(ctx: _Context) -> Finding | None:
  """Step 3: a task, mapped to the MVP, open, with its prerequisites done; records the task and its criteria in ctx.

  Args:
    ctx: the evaluation context.

  Returns:
    A REVIEW or BLOCK finding, or None to continue.
  """
  p, revision = ctx.proposal, ctx.project.mvp.revision
  if p.task_id is None:
    return ("REVIEW", "NO_TASK", "GG-406", "nontrivial work needs a Vikunja task: name task_id", {})
  ctx.task = ctx.tasks.tasks.get(p.task_id)
  if ctx.task is None:
    return ("REVIEW", "TASK_NOT_FOUND", "PORT-001", f"task {p.task_id} is not in {ctx.tasks.source}", {})
  task = ctx.task
  ctx.mapped = set(ctx.project.task_map.get(task.id, ())) & ctx.project.mvp.criterion_ids()
  if not ctx.mapped:
    return ("BLOCK", "TASK_UNMAPPED", "PORT-002", f"task {task.id} maps to no accepted criterion of {revision}; map it with the owner", {})
  if task.done:
    return ("REVIEW", "TASK_CLOSED", "PORT-002", f"task {task.id} is done; reopen it or name an open task", {})
  unmet = [d for d in task.prerequisites if not (ctx.tasks.tasks.get(d) and ctx.tasks.tasks[d].done)]
  if unmet:
    return ("REVIEW", "UNMET_DEPENDENCY", "PORT-003", f"task {task.id} waits on {unmet}", {"blocked_by": unmet})
  return None


def _step_guards(ctx: _Context) -> Finding | None:
  """Steps 4-6: exclusions whatever the work is called, self-approval fields, protected changes.

  Args:
    ctx: the evaluation context.

  Returns:
    A BLOCK finding, or None to continue.
  """
  p, proj = ctx.proposal, ctx.project
  text = " ".join((p.description, p.smallest_step, ctx.task.title)).lower()
  for ex in proj.mvp.exclusions:
    if any(word and word in text for word in ex.keywords):
      return ("BLOCK", "EXCLUDED", "MVP-004", f"matches exclusion {ex.id!r}: {ex.text}", {"exclusion": ex.id})
  found = sorted(set(p.raw_keys) & set(APPROVAL_KEYS))
  if found:
    return ("BLOCK", "SELF_APPROVAL", "MVP-007", f"proposal carries approval fields {found}; only the owner approves, record it as a request", {})
  protected = set(proj.protected_paths())
  for raw in p.proposed_files:
    if (proj.root / raw).resolve() in protected:
      return ("BLOCK", "PROTECTED_CHANGE", "MVP-011", f"{raw} is protected; changes go through the owner's change request", {"path": raw})
  return None


def _step_link(ctx: _Context) -> Finding | None:
  """Steps 7-9: criterion link (an unmapped idea parks), unregistered blocker, false linkage, recorded necessity, scope growth.

  Args:
    ctx: the evaluation context.

  Returns:
    A PARK or REVIEW finding, or None for PROCEED; records the cited criterion and blocker in ctx.
  """
  p, mvp = ctx.proposal, ctx.project.mvp
  ctx.blocker = next((b for b in mvp.blockers if b.id == p.necessary_blocker_id), None)
  if not p.criterion_id and not p.necessary_blocker_id:
    return ("PARK", "NO_CRITERION", "MVP-005", "cites no accepted criterion and no registered blocker; record it in deferred ideas", {})
  if p.criterion_id and p.criterion_id not in mvp.criterion_ids():
    return ("PARK", "UNKNOWN_CRITERION", "MVP-005", f"{p.criterion_id} is not an accepted criterion of {mvp.revision}", {})
  if p.necessary_blocker_id and ctx.blocker is None:
    return ("REVIEW", "UNREGISTERED_BLOCKER", "MVP-006", f"{p.necessary_blocker_id} is not a registered blocker; ask the owner for a revision", {})
  ctx.cited = p.criterion_id or ctx.blocker.unblocks
  if ctx.cited not in ctx.mapped:
    return ("REVIEW", "FALSE_LINKAGE", "GG-007", f"task {ctx.task.id} is mapped to {sorted(ctx.mapped)}, not {ctx.cited}", {})
  missing = [f for f in ("claimed_necessity", "smallest_step", "stop_condition") if not getattr(p, f)]
  if missing:
    return ("REVIEW", "NECESSITY_UNRECORDED", "GG-412", f"record {', '.join(missing)} before work starts", {})
  if p.adds_scope:
    return ("REVIEW", "ADDS_SCOPE", "MVP-006", "adds scope: state the trade-off and wait for the owner", {})
  return None


# The evaluation order of references/decision-rules.md; the first finding wins.
STEPS = (_step_context, _step_read_only, _step_baseline, _step_task, _step_guards, _step_link)
