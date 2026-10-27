"""What's Next at three levels with the deterministic ranking pipeline (references/whats-next-and-portfolio.md).

Imported, not run. Pure policy: no I/O. Replaces the v0.1 weighted score. Pipeline: filter (approved mapping, open, prerequisites
done) -> owner first (human-selected focus, incident label) -> deadline pressure (committed milestone or due date inside the window,
and the tasks that unblock them) -> started work (GG-101: a started task beats a slightly higher-ranked switch) -> Vikunja priority
through the project's configured mapping -> due date -> task ID. Every factor is logged so the ranking can be replayed (PORT-006).
No durations, forecasts or percent complete are invented: forecast is always "unknown" (DATE-003).
"""

import datetime as dt
from dataclasses import dataclass, field

from .errors import ConfigError
from .project import BaselineState, Project
from .records import Task, parse_date
from .tasks import TaskSet

FAR = dt.date.max


def _ranking_config(project: Project) -> tuple[dict[int, int], str, str]:
  """Read the project's ranking rules from project.yaml.

  Args:
    project: the project.

  Returns:
    (priority_rank, started_label, incident_label): Vikunja priority -> rank (0 first; unmapped sorts last), and the label titles
    that mark started work and authorised incidents (lower case; "" when not configured).
  """
  cfg = project.config.get("ranking") or {}
  ranks = {int(k): int(v) for k, v in (cfg.get("priority_rank") or {}).items()}
  return ranks, str(cfg.get("started_label") or "").lower(), str(cfg.get("incident_label") or "").lower()


def _pressured(project: Project, tasks: TaskSet, today: dt.date, window: int) -> set[int]:
  """Find tasks under deadline pressure: tasks of a committed milestone inside the window, and their open prerequisites.

  Args:
    project: the project.
    tasks: the task source.
    today: the date ranked for.
    window: days ahead that count.

  Returns:
    Task IDs under pressure.
  """
  horizon = today + dt.timedelta(days=window)
  seeds = set()
  for m in project.milestones:
    due = parse_date(m.get("commitment_date"), f"milestone {m.get('milestone_id')} commitment_date")
    if due and due <= horizon:
      seeds.update(int(t) for t in m.get("vikunja_task_ids") or [])
  seeds.update(t.id for t in tasks.tasks.values() if t.project_id == project.vikunja_project_id and t.due and t.due <= horizon)
  out, stack = set(), list(seeds)
  while stack:
    tid = stack.pop()
    if tid in out:
      continue
    out.add(tid)
    task = tasks.tasks.get(tid)
    if task:
      stack.extend(d for d in task.prerequisites if not (tasks.tasks.get(d) and tasks.tasks[d].done))
  return out


def _candidates(project: Project, tasks: TaskSet) -> tuple[list[Task], list[dict]]:
  """Filter a project's tasks to the eligible ones.

  Args:
    project: the project (its baseline must already be approved).
    tasks: the task source.

  Returns:
    (eligible, excluded): eligible Tasks, and {task_id, reason} for each open task left out.
  """
  accepted = project.mvp.criterion_ids() if project.mvp else set()
  eligible, excluded = [], []
  own = sorted((t for t in tasks.tasks.values() if t.project_id == project.vikunja_project_id or t.id in project.task_map), key=lambda t: t.id)
  for task in own:
    if task.done:
      continue
    if not set(project.task_map.get(task.id, ())) & accepted:
      excluded.append({"task_id": task.id, "reason": "maps to no accepted criterion (PORT-002)"})
      continue
    unmet = [d for d in task.prerequisites if not (tasks.tasks.get(d) and tasks.tasks[d].done)]
    if unmet:
      excluded.append({"task_id": task.id, "reason": f"waits on {unmet} (PORT-003)", "blocked_by": unmet})
      continue
    eligible.append(task)
  return eligible, excluded


def _key(task: Task, project: Project, focus: int | None, pressured: set[int]) -> tuple:
  """Build the sort key and its logged factors.

  Args:
    task: an eligible task.
    project: its project.
    focus: the owner's selected task ID, or None.
    pressured: task IDs under deadline pressure.

  Returns:
    A tuple: (owner_tier, deadline_tier, started_tier, priority_rank, due, id); lower sorts first.
  """
  ranks, started, incident = _ranking_config(project)
  owner = 0 if task.id == focus or (incident and incident in task.labels) else 1
  return (
    owner,
    0 if task.id in pressured else 1,
    0 if started and started in task.labels else 1,
    ranks.get(task.priority, len(ranks) + 1),
    task.due or FAR,
    task.id,
  )


def _factors(key: tuple) -> dict:
  """Name the parts of a sort key for the replay log.

  Args:
    key: a _key() tuple.

  Returns:
    The factors as a mapping.
  """
  return {
    "owner_first": key[0] == 0,
    "deadline_pressure": key[1] == 0,
    "started": key[2] == 0,
    "priority_rank": key[3],
    "due": None if key[4] == FAR else key[4].isoformat(),
  }


def _why_first(top: tuple, runner: tuple | None) -> str:
  """Say which factor puts the top task ahead of the runner-up.

  Args:
    top: the first task's key.
    runner: the second task's key, or None.

  Returns:
    One sentence.
  """
  if runner is None:
    return "the only eligible task"
  names = (
    "owner-selected or incident",
    "deadline pressure",
    "started work is finished first",
    "higher Vikunja priority",
    "earlier due date",
    "lower task ID (tie-break)",
  )
  for i, name in enumerate(names):
    if top[i] != runner[i]:
      return f"outranks task {runner[5]}: {name}"
  return "identical keys"


def _milestone_alerts(project: Project, today: dt.date, window: int) -> tuple[dict | None, list[dict]]:
  """Find the next milestone and the date alerts (DATE-005: internal-target breach, deadline at risk, missed commitment).

  Args:
    project: the project.
    today: the date ranked for.
    window: days ahead counted as at risk.

  Returns:
    (next_milestone, alerts). A milestone is delivered only with acceptance evidence for each of its criteria (DATE-007), never
    from task closure.
  """
  upcoming, alerts = [], []
  for m in project.milestones:
    mid = str(m.get("milestone_id", ""))
    commitment = parse_date(m.get("commitment_date"), f"milestone {mid} commitment_date")
    criteria = [str(c) for c in m.get("acceptance_criterion_ids") or []]
    evidence = m.get("acceptance_evidence") or {}
    delivered = bool(criteria) and all(evidence.get(c) for c in criteria)
    if delivered:
      continue
    internal = parse_date(project.internal_targets.get(mid), f"internal target {mid}")
    if commitment:
      upcoming.append((commitment, mid))
      if commitment < today:
        alerts.append({"kind": "missed_commitment", "milestone_id": mid, "commitment": commitment.isoformat()})
      elif commitment <= today + dt.timedelta(days=window):
        alerts.append({"kind": "deadline_at_risk", "milestone_id": mid, "commitment": commitment.isoformat(), "forecast": "unknown"})
    if internal and internal < today:
      alerts.append({"kind": "internal_target_breach", "milestone_id": mid})
  upcoming.sort()
  nxt = {"milestone_id": upcoming[0][1], "commitment": upcoming[0][0].isoformat(), "forecast": "unknown"} if upcoming else None
  return nxt, alerts


def whats_next(
  projects: list[Project],
  baselines: dict[str, BaselineState],
  tasks: TaskSet,
  today: dt.date,
  window: int,
  focus: int | None = None,
  task_in_focus: int | None = None,
) -> dict:
  """Compute task, project and portfolio next actions.

  Args:
    projects: the projects of one partition.
    baselines: project_id -> BaselineState.
    tasks: the task source.
    today: the date ranked for.
    window: deadline-pressure window in days.
    focus: the owner's selected task ID (owner first), or None.
    task_in_focus: a task to give the task-level answer for, or None.

  Returns:
    {"source", "portfolio", "projects", "task", "at_risk", "ranking"}; the portfolio status is FOCUS, NO_ACTION or BLOCKED.

  Raises:
    ConfigError: the projects span more than one partition (apn and me are never ranked together).
  """
  partitions = {p.partition for p in projects}
  if len(partitions) > 1:
    raise ConfigError(f"projects span partitions {sorted(partitions)}; rank apn and me separately")
  acc = _Accumulator()
  if not tasks.live:
    acc.at_risk.append({"kind": "not_live", "detail": f"tasks from {tasks.source}, read {tasks.read_at}; no completion or reprioritisation from it"})
  if not tasks.complete:
    acc.at_risk.append({"kind": "partial_data", "detail": "the task source reports missing pages or records"})
  for project in projects:
    _rank_project(project, baselines[project.project_id], tasks, today, window, focus, acc)
  return {
    "source": {"tasks": tasks.source, "live": tasks.live, "complete": tasks.complete, "read_at": tasks.read_at},
    "portfolio": _portfolio(acc),
    "projects": acc.per_project,
    "task": _task_level(task_in_focus, tasks) if task_in_focus is not None else None,
    "at_risk": acc.at_risk,
    "ranking": acc.ranking,
  }


@dataclass
class _Accumulator:
  """Results gathered across projects while ranking.

  Args:
    pool: (key, task, project) for every eligible task.
    per_project: one answer per project.
    at_risk: alerts.
    ranking: the replay log of factors.
    waiting: projects blocked on an owner decision.
  """

  pool: list[tuple] = field(default_factory=list)
  per_project: list[dict] = field(default_factory=list)
  at_risk: list[dict] = field(default_factory=list)
  ranking: list[dict] = field(default_factory=list)
  waiting: list[dict] = field(default_factory=list)


def _rank_project(project: Project, state: BaselineState, tasks: TaskSet, today: dt.date, window: int, focus: int | None, acc: _Accumulator) -> None:
  """Rank one project's eligible tasks and add its answer, alerts and pool entries to the accumulator.

  Args:
    project: the project.
    state: its baseline state.
    tasks: the task source.
    today: the date ranked for.
    window: deadline-pressure window in days.
    focus: the owner's selected task ID, or None.
    acc: where results go.
  """
  pid = project.project_id
  nxt_milestone, alerts = _milestone_alerts(project, today, window)
  acc.at_risk.extend(dict(a, project_id=pid) for a in alerts)
  if not state.approved:
    acc.per_project.append({"project_id": pid, "status": "BLOCKED", "reason": state.reason, "next_milestone": nxt_milestone})
    acc.waiting.append({"project_id": pid, "needs": state.reason})
    return
  eligible, excluded = _candidates(project, tasks)
  pressured = _pressured(project, tasks, today, window)
  keyed = sorted((_key(t, project, focus, pressured), t) for t in eligible)
  for k, t in keyed:
    acc.ranking.append({"project_id": pid, "task_id": t.id, **_factors(k)})
    acc.pool.append((k, t, project))
  started = [t for _, t in keyed if _key(t, project, None, set())[2] == 0]
  if len(started) > 1:
    acc.at_risk.append({"kind": "wip", "project_id": pid, "detail": f"{len(started)} started tasks; one operator focus (PORT-004)"})
  row = {"project_id": pid, "next_milestone": nxt_milestone, "excluded": excluded}
  if keyed:
    top = keyed[0][1]
    row.update(status="READY", next_task=top.id, title=top.title, next_action=top.next_action() or None)
  elif excluded:
    row.update(status="BLOCKED", reason="every open task is excluded")
  else:
    row.update(status="NO_ACTION", reason="no open mapped task")
  acc.per_project.append(row)


def _portfolio(acc: _Accumulator) -> dict:
  """Pick the one portfolio focus, or say why there is none.

  Args:
    acc: the ranked results of every project.

  Returns:
    {"status": FOCUS, ...} with the task and why it is first, or {"status": BLOCKED | NO_ACTION, "waiting": [...]}.
  """
  pool = sorted(acc.pool, key=lambda x: x[0])
  if not pool:
    blocked = acc.waiting or any(p["status"] == "BLOCKED" for p in acc.per_project)
    return {"status": "BLOCKED" if blocked else "NO_ACTION", "waiting": acc.waiting}
  k, t, project = pool[0]
  return {
    "status": "FOCUS",
    "task_id": t.id,
    "title": t.title,
    "project_id": project.project_id,
    "eligible_because": "mapped to an accepted criterion, open, prerequisites done",
    "why_first": _why_first(k, pool[1][0] if len(pool) > 1 else None),
    "next_action": t.next_action() or "REVIEW: the task names no concrete next action; add a 'Next:' line (GG-106)",
  }


def _task_level(task_id: int, tasks: TaskSet) -> dict:
  """Answer for one task: its next action, its blockers, or the next dependent task once it is done.

  Args:
    task_id: Vikunja task ID.
    tasks: the task source.

  Returns:
    {"task_id", "status", ...}; a vague or missing next action is REVIEW (GG-106).
  """
  task = tasks.tasks.get(task_id)
  if task is None:
    return {"task_id": task_id, "status": "UNKNOWN", "reason": f"not in {tasks.source}"}
  if task.done:
    dependents = sorted(t.id for t in tasks.tasks.values() if task_id in t.prerequisites and not t.done)
    return {"task_id": task_id, "status": "DONE", "next_dependent_tasks": dependents}
  unmet = [d for d in task.prerequisites if not (tasks.tasks.get(d) and tasks.tasks[d].done)]
  if unmet:
    return {"task_id": task_id, "status": "BLOCKED", "blocked_by": unmet}
  action = task.next_action()
  if not action:
    return {"task_id": task_id, "status": "REVIEW", "reason": "no 'Next:' line names a concrete physical action (GG-106)"}
  return {"task_id": task_id, "status": "READY", "next_action": action}
