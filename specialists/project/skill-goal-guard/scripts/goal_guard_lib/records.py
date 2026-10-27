"""Goal Guard records as frozen dataclasses, with parsing and validation from plain data (YAML, JSON, Vikunja responses).

Imported, not run. Field names follow references/decision-rules.md (Record formats); the MVP contract is in mvp.py.
Consumers: mvp, project, tasks, decide, rank, trace, snapshot, excel, hook.
"""

import datetime as dt
from dataclasses import asdict, dataclass, field

from .errors import RecordError

VERDICTS = ("PROCEED", "PARK", "REVIEW", "BLOCK")
# Keys that only an owner decision may carry; on a proposal they are self-approval (decision rule 5, MVP-007).
APPROVAL_KEYS = ("approval", "approved", "approved_by", "approved_at", "owner_approval", "approval_ref")
# Vikunja relation kinds on a task that name its prerequisites. UNVERIFIED on the instance until the GG-305 round trip:
# "blocked" lists the tasks blocking this one and "follows" the tasks this one comes after (OpenAPI 2.7.1 enum, direction text).
PREREQUISITE_KINDS = ("blocked", "follows")


def text_field(data: dict, key: str, where: str, required: bool = True) -> str:
  """Read a string field.

  Args:
    data: the record.
    key: field name.
    where: record name for the error message.
    required: whether an empty or missing value is an error.

  Returns:
    The stripped string, or "" when optional and absent.

  Raises:
    RecordError: required and missing, or not a string.
  """
  value = data.get(key)
  if value is None or value == "":
    if required:
      raise RecordError(f"{where}: missing {key}")
    return ""
  if not isinstance(value, str | int | float):
    raise RecordError(f"{where}: {key} must be text")
  return str(value).strip()


def parse_date(value: object, where: str) -> dt.date | None:
  """Parse a date-only or ISO-8601 date-time value to a date.

  Args:
    value: None, a date, or text such as 2026-12-15 or 2026-12-15T00:00:00+11:00.
    where: field name for the error message.

  Returns:
    The date, or None when the value is empty or Vikunja's zero time (year 1, which it sends for an unset date).

  Raises:
    RecordError: the text is not an ISO date (the v0.1 prototype raised an uncaught ValueError here).
  """
  if value in (None, ""):
    return None
  if isinstance(value, dt.datetime):
    return value.date()
  if isinstance(value, dt.date):
    return value
  text = str(value)
  try:
    parsed = dt.datetime.fromisoformat(text.replace("Z", "+00:00")).date() if "T" in text else dt.date.fromisoformat(text)
  except ValueError as err:
    raise RecordError(f"{where}: {text!r} is not an ISO date") from err
  return None if parsed.year == 1 else parsed


@dataclass(frozen=True)
class Task:
  """A task as Goal Guard sees it, normalised from a Vikunja task.

  Args:
    id: Vikunja numeric task ID.
    title: task title.
    description: task text; a line starting "Next:" names the next physical action.
    done: Vikunja's done flag.
    priority: Vikunja priority integer (scale mapped by project config, never assumed).
    due: operational due date, or None.
    labels: label titles, lower case.
    project_id: Vikunja project ID.
    prerequisites: IDs of tasks that must be done first.
    identifier: Vikunja's textual ID such as PROJ-12, or "".
  """

  id: int
  title: str
  description: str
  done: bool
  priority: int
  due: dt.date | None
  labels: tuple[str, ...]
  project_id: int
  prerequisites: tuple[int, ...]
  identifier: str = ""

  def next_action(self) -> str:
    """Return the concrete next action written in the description.

    Returns:
      The text after the first line starting with "Next:", or "" when there is none.
    """
    for line in self.description.splitlines():
      if line.strip().lower().startswith("next:"):
        return line.strip()[5:].strip()
    return ""


def parse_vikunja_task(data: dict) -> Task:
  """Normalise one Vikunja Task object (OpenAPI 2.7.1 schema Task) to a Task.

  Args:
    data: the task JSON as Vikunja returns it.

  Returns:
    The Task.

  Raises:
    RecordError: the object has no integer id or no title, or a date is malformed.
  """
  if not isinstance(data, dict) or not isinstance(data.get("id"), int):
    raise RecordError("task: expected an object with an integer id")
  where = f"task {data['id']}"
  related = data.get("related_tasks") or {}
  prereqs = sorted({int(t["id"]) for kind in PREREQUISITE_KINDS for t in (related.get(kind) or []) if isinstance(t, dict) and "id" in t})
  labels = tuple(sorted(str(lab.get("title", "")).lower() for lab in (data.get("labels") or []) if isinstance(lab, dict)))
  return Task(
    id=data["id"],
    title=text_field(data, "title", where),
    description=str(data.get("description") or ""),
    done=bool(data.get("done")),
    priority=int(data.get("priority") or 0),
    due=parse_date(data.get("due_date"), f"{where} due_date"),
    labels=labels,
    project_id=int(data.get("project_id") or 0),
    prerequisites=tuple(prereqs),
    identifier=str(data.get("identifier") or ""),
  )


@dataclass(frozen=True)
class Proposal:
  """A proposed piece of agent work (references/decision-rules.md, Record formats).

  Args:
    proposal_id: proposal ID.
    task_id: Vikunja task ID, or None when the proposal names no task.
    project_id: Goal Guard project ID.
    criterion_id: accepted criterion it claims to advance, or "".
    necessary_blocker_id: registered blocker it claims to clear, or "".
    description: what the work is.
    adds_scope: whether the agent says it adds scope.
    claimed_necessity: the agent's necessity rationale.
    smallest_step: smallest sufficient action.
    stop_condition: when to stop.
    intent: execute (default), inspect (read-only) or discuss.
    evidence_refs: references the agent cites.
    proposed_files: files the work would touch, relative to the project.
    proposer: agent or session that wrote it.
    raw_keys: every key present, kept to detect self-approval fields.
  """

  proposal_id: str
  task_id: int | None
  project_id: str
  criterion_id: str
  necessary_blocker_id: str
  description: str
  adds_scope: bool
  claimed_necessity: str
  smallest_step: str
  stop_condition: str
  intent: str = "execute"
  evidence_refs: tuple[str, ...] = ()
  proposed_files: tuple[str, ...] = ()
  proposer: str = ""
  raw_keys: tuple[str, ...] = field(default=())


def parse_proposal(data: object) -> Proposal:
  """Build a Proposal from a parsed YAML or JSON file.

  Args:
    data: the parsed mapping.

  Returns:
    The Proposal.

  Raises:
    RecordError: not a mapping, no proposal_id or project_id, task_id not an integer, or intent unknown.
  """
  if not isinstance(data, dict):
    raise RecordError("proposal: expected a mapping")
  where = "proposal"
  task_id = data.get("task_id")
  if task_id not in (None, ""):
    try:
      task_id = int(task_id)
    except (TypeError, ValueError) as err:
      raise RecordError(f"{where}: task_id must be the numeric Vikunja task ID") from err
  else:
    task_id = None
  intent = text_field(data, "intent", where, False) or "execute"
  if intent not in ("execute", "inspect", "discuss"):
    raise RecordError(f"{where}: intent must be execute, inspect or discuss")
  return Proposal(
    proposal_id=text_field(data, "proposal_id", where),
    task_id=task_id,
    project_id=text_field(data, "project_id", where),
    criterion_id=text_field(data, "criterion_id", where, False),
    necessary_blocker_id=text_field(data, "necessary_blocker_id", where, False),
    description=text_field(data, "description", where, False),
    adds_scope=bool(data.get("adds_scope", False)),
    claimed_necessity=text_field(data, "claimed_necessity", where, False),
    smallest_step=text_field(data, "smallest_step", where, False),
    stop_condition=text_field(data, "stop_condition", where, False),
    intent=intent,
    evidence_refs=tuple(str(r) for r in data.get("evidence_refs") or []),
    proposed_files=tuple(str(f) for f in data.get("proposed_files") or []),
    proposer=text_field(data, "proposer", where, False),
    raw_keys=tuple(data.keys()),
  )


@dataclass(frozen=True)
class Verdict:
  """The outcome of assessing one proposal.

  Args:
    proposal_id: the proposal assessed.
    verdict: PROCEED, PARK, REVIEW or BLOCK.
    reason_code: short machine code, e.g. NO_BASELINE.
    clause: policy clause or test ID, e.g. MVP-001.
    reason: one sentence for the reader, naming the remedy.
    contract_revision: mvp_id@baseline_version, or "none".
    requires_owner_approval: whether only the owner can unblock it.
    decided_at: ISO-8601 time with offset.
    task_id: the task the proposal named, or None.
    evidence_refs: references carried from the proposal.
    details: extra facts (blockers, matched exclusion).
  """

  proposal_id: str
  verdict: str
  reason_code: str
  clause: str
  reason: str
  contract_revision: str
  requires_owner_approval: bool
  decided_at: str
  task_id: int | None = None
  evidence_refs: tuple[str, ...] = ()
  details: dict = field(default_factory=dict)

  def to_dict(self) -> dict:
    """Return the verdict as plain data for JSON output and decisions.jsonl.

    Returns:
      A dict with every field; tuples become lists.
    """
    out = asdict(self)
    out["evidence_refs"] = list(self.evidence_refs)
    return out
