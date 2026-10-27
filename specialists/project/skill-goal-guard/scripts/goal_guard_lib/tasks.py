"""Task sources: live Vikunja, a saved Vikunja response, or a Goal Guard snapshot, all normalised to records.Task.

Imported, not run. Read-only. Vikunja owns live tasks (PORT-001); a file or snapshot source is labelled so a reader knows the
answer is not live (references/snapshot-and-restore.md, Offline use).
"""

import datetime as dt
from dataclasses import dataclass
from pathlib import Path

from . import yaml_io
from .errors import RecordError
from .records import PREREQUISITE_KINDS, Task, parse_date, parse_vikunja_task
from .vikunja import Client


@dataclass(frozen=True)
class TaskSet:
  """Tasks from one source.

  Args:
    tasks: Vikunja task ID -> Task.
    source: "vikunja:<url>", "file:<path>" or "snapshot:<path>".
    live: True only for a live Vikunja read.
    complete: False when pagination or the snapshot says data is missing.
    read_at: ISO-8601 time the data was read or exported.
  """

  tasks: dict[int, Task]
  source: str
  live: bool
  complete: bool
  read_at: str


def from_vikunja(client: Client, project_ids: list[int], url: str) -> TaskSet:
  """Read the tasks of one or more Vikunja projects.

  Args:
    client: a bound Vikunja client.
    project_ids: Vikunja project IDs to read.
    url: base URL, for the source label.

  Returns:
    The TaskSet; complete is False if any project's pagination fell short.
  """
  tasks, complete = {}, True
  for pid in project_ids:
    raw, completeness = client.project_tasks(pid)
    complete = complete and completeness["complete"]
    for item in raw:
      task = parse_vikunja_task(item)
      tasks[task.id] = task
  return TaskSet(tasks, f"vikunja:{url}", True, complete, dt.datetime.now().astimezone().isoformat(timespec="seconds"))


def parse_snapshot_task(data: dict) -> Task:
  """Normalise one task from a Goal Guard snapshot (snapshot.export format) to a Task.

  Args:
    data: the snapshot task object (provider_id, title, relations, ...).

  Returns:
    The Task.

  Raises:
    RecordError: no integer provider_id, or a malformed date.
  """
  if not isinstance(data.get("provider_id"), int):
    raise RecordError(f"snapshot task {data.get('portable_id')!r}: missing integer provider_id")
  prereqs = sorted({int(r["other_provider_id"]) for r in data.get("relations") or [] if r.get("kind") in PREREQUISITE_KINDS})
  return Task(
    id=data["provider_id"],
    title=str(data.get("title") or ""),
    description=str(data.get("description") or ""),
    done=bool(data.get("done")),
    priority=int(data.get("priority") or 0),
    due=parse_date(data.get("due_date"), f"snapshot task {data['provider_id']} due_date"),
    labels=tuple(sorted(str(lab).lower() for lab in data.get("labels") or [])),
    project_id=int(data.get("provider_project_id") or 0),
    prerequisites=tuple(prereqs),
    identifier=str(data.get("identifier") or ""),
  )


def from_file(path: Path) -> TaskSet:
  """Read tasks from a saved file: a JSON list of Vikunja tasks, a PaginatedTask object, or a snapshot tasks.json.

  Args:
    path: the file.

  Returns:
    The TaskSet, labelled file: or snapshot: and never live.

  Raises:
    RecordError: the file cannot be parsed or holds no recognisable task list.
  """
  data = yaml_io.load_file(path)
  if isinstance(data, dict) and data.get("format") == "goalguard-snapshot-tasks":
    tasks = {t.id: t for t in (parse_snapshot_task(x) for x in data.get("tasks") or [])}
    complete = bool(data.get("completeness", {}).get("complete", False))
    return TaskSet(tasks, f"snapshot:{path}", False, complete, str(data.get("exported_at", "")))
  items = data.get("items") if isinstance(data, dict) else data
  if not isinstance(items, list):
    raise RecordError(f"{path}: expected a list of Vikunja tasks, a PaginatedTask object or a Goal Guard snapshot")
  tasks = {t.id: t for t in (parse_vikunja_task(x) for x in items)}
  stamp = dt.datetime.fromtimestamp(path.stat().st_mtime).astimezone().isoformat(timespec="seconds")
  return TaskSet(tasks, f"file:{path}", False, True, stamp)
