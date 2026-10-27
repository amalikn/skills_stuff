"""Project snapshot, manifests, verification and clean-instance restore (references/snapshot-and-restore.md; pilot step 8).

Imported, not run. Layout under the output folder (default: the data peer, GG_DATA_DIR/snapshots):

  <out>/<partition>/manifest.json               parent manifest: one child entry per project (path, sha256, counts)
  <out>/<partition>/<project_id>/tasks.json     provider-neutral task records (format goalguard-snapshot-tasks)
  <out>/<partition>/<project_id>/manifest.json  project manifest: time (UTC), source instance and version, completeness, checksums

Never exported: tokens, users (assignees, created_by), attachments, comments, reactions. Internal targets, baseline links and
forecasts are referenced by the hash of .gg/mappings.yaml, never copied as task fields.

Writes: export() plans by default and writes only with apply=True, atomically (temp file, fsync, os.replace); it refuses a
partial export, which would replace the last-known-good snapshot (S04). verify() writes nothing. Restore is in restore.py.
"""

import datetime as dt
import hashlib
import json
import os
import tempfile
from pathlib import Path

from .errors import RecordError, WriteRefused
from .project import Project
from .records import parse_date

FORMAT = 1
TASKS_FORMAT = "goalguard-snapshot-tasks"
PREREQ = ("blocked", "follows")
DATE_FIELDS = ("due_date", "start_date", "end_date")


def _sha(data: bytes) -> str:
  """Hash bytes.

  Args:
    data: the bytes.

  Returns:
    The hex SHA-256 digest.
  """
  return hashlib.sha256(data).hexdigest()


def _date_text(value: object) -> str | None:
  """Normalise a Vikunja date-time, turning its zero time into None.

  Args:
    value: the date-time text from Vikunja.

  Returns:
    The text unchanged, or None when unset or year 1.
  """
  return str(value) if parse_date(value, "date") else None


def to_record(task: dict, project_id: str) -> dict:
  """Convert one raw Vikunja task to a snapshot record.

  Args:
    task: the raw Task object.
    project_id: GoalGuard project ID, used in portable IDs.

  Returns:
    The provider-neutral record.
  """
  relations = []
  for kind, others in sorted((task.get("related_tasks") or {}).items()):
    for other in others or []:
      if isinstance(other, dict) and "id" in other:
        relations.append({"kind": kind, "other_provider_id": int(other["id"]), "other_provider_project_id": int(other.get("project_id") or 0)})
  return {
    "portable_id": f"{project_id}:{task['id']}",
    "provider_id": int(task["id"]),
    "provider_project_id": int(task.get("project_id") or 0),
    "identifier": str(task.get("identifier") or ""),
    "title": str(task.get("title") or ""),
    "description": str(task.get("description") or ""),
    "done": bool(task.get("done")),
    "done_at": _date_text(task.get("done_at")),
    "priority": int(task.get("priority") or 0),
    **{f: _date_text(task.get(f)) for f in DATE_FIELDS},
    "labels": sorted(str(lab.get("title", "")) for lab in task.get("labels") or [] if isinstance(lab, dict)),
    "relations": relations,
    "created": task.get("created"),
    "updated": task.get("updated"),
  }


def _atomic_write(path: Path, data: bytes) -> None:
  """Write a file atomically: temp file in the same folder, fsync, rename over the target.

  Args:
    path: destination.
    data: content.
  """
  path.parent.mkdir(parents=True, exist_ok=True)
  fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
  try:
    with os.fdopen(fd, "wb") as handle:
      handle.write(data)
      handle.flush()
      os.fsync(handle.fileno())
    os.replace(tmp, path)
  except BaseException:
    Path(tmp).unlink(missing_ok=True)
    raise


def _dump(value: object) -> bytes:
  """Serialise JSON deterministically.

  Args:
    value: plain data.

  Returns:
    Indented JSON bytes with a final newline.
  """
  return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=False) + "\n").encode("utf-8")


def export(project: Project, raw_tasks: list[dict], completeness: dict, source: dict, out: Path, apply: bool) -> dict:
  """Build a project snapshot and its manifests; write them with apply.

  Args:
    project: the project.
    raw_tasks: raw Vikunja Task objects of the project.
    completeness: {"total", "fetched", "complete"} from the read.
    source: {"instance": url or file, "version": Vikunja version or "unknown"}.
    out: snapshot root folder.
    apply: write when True; plan only when False.

  Returns:
    {"applied", "paths", "counts", "completeness"}.

  Raises:
    WriteRefused: apply requested for a partial export.
  """
  now = dt.datetime.now(dt.UTC).isoformat(timespec="seconds")
  records = [to_record(t, project.project_id) for t in sorted(raw_tasks, key=lambda t: t["id"])]
  tasks_bytes = _dump(_tasks_doc(project, records, completeness, source, now))
  counts = {"tasks": len(records), "relations": sum(len(r["relations"]) for r in records)}
  manifest = {
    "format_version": FORMAT,
    "level": "project",
    "project_id": project.project_id,
    "partition": project.partition,
    "created_at": now,
    "source": source,
    "completeness": completeness,
    "files": [{"path": "tasks.json", "sha256": _sha(tasks_bytes), "records": counts["tasks"]}],
    "counts": counts,
  }
  manifest_bytes = _dump(manifest)
  folder = out / project.partition / project.project_id
  parent_path = out / project.partition / "manifest.json"
  paths = [str(folder / "tasks.json"), str(folder / "manifest.json"), str(parent_path)]
  plan = {"applied": False, "paths": paths, "counts": counts, "completeness": completeness}
  if not apply:
    return plan
  if not completeness.get("complete"):
    raise WriteRefused(f"export is partial ({completeness}); the last-known-good snapshot is kept (S04)")
  _atomic_write(folder / "tasks.json", tasks_bytes)
  _atomic_write(folder / "manifest.json", manifest_bytes)
  _write_parent(parent_path, project, _sha(manifest_bytes), now)
  return dict(plan, applied=True)


def _tasks_doc(project: Project, records: list[dict], completeness: dict, source: dict, now: str) -> dict:
  """Assemble tasks.json; GoalGuard's own records are referenced by hash, never copied (S01).

  Args:
    project: the project.
    records: snapshot task records.
    completeness: the read's completeness.
    source: instance and version.
    now: export time (UTC).

  Returns:
    The tasks document.
  """
  mappings = project.root / ".gg" / "mappings.yaml"
  return {
    "format": TASKS_FORMAT,
    "format_version": FORMAT,
    "project_id": project.project_id,
    "partition": project.partition,
    "exported_at": now,
    "source": source,
    "completeness": completeness,
    "supplementary_refs": {"mappings": ".gg/mappings.yaml", "sha256": _sha(mappings.read_bytes()) if mappings.exists() else None},
    "tasks": records,
  }


def _write_parent(path: Path, project: Project, manifest_sha: str, now: str) -> None:
  """Add or replace this project's entry in the partition manifest, atomically.

  Args:
    path: <out>/<partition>/manifest.json.
    project: the project.
    manifest_sha: hash of the project manifest just written.
    now: export time.
  """
  empty = {"format_version": FORMAT, "level": "partition", "partition": project.partition, "children": []}
  parent = json.loads(path.read_text(encoding="utf-8")) if path.exists() else empty
  children = [c for c in parent.get("children", []) if c.get("project_id") != project.project_id]
  children.append({"project_id": project.project_id, "path": f"{project.project_id}/manifest.json", "sha256": manifest_sha, "created_at": now})
  parent.update(children=sorted(children, key=lambda c: c["project_id"]), updated_at=now)
  _atomic_write(path, _dump(parent))


def _load_json(path: Path) -> dict:
  """Read a JSON object.

  Args:
    path: the file.

  Returns:
    The parsed object.

  Raises:
    RecordError: missing, unreadable or not a JSON object.
  """
  try:
    data = json.loads(path.read_text(encoding="utf-8"))
  except (OSError, json.JSONDecodeError) as err:
    raise RecordError(f"{path}: cannot read as JSON ({err})") from err
  if not isinstance(data, dict):
    raise RecordError(f"{path}: expected a JSON object")
  return data


def verify(folder: Path) -> dict:
  """Dry-run check of a project snapshot: schema, hashes, IDs, references and the dependency graph. Writes nothing.

  Args:
    folder: <out>/<partition>/<project_id>.

  Returns:
    {"ok", "issues", "counts", "cross_project_edges", "manifest", "tasks"}; tasks is the parsed tasks document when readable.
  """
  issues = []
  manifest = _load_json(folder / "manifest.json")
  if manifest.get("format_version") != FORMAT:
    issues.append(f"manifest format_version {manifest.get('format_version')} is not {FORMAT}")
  doc = None
  for entry in manifest.get("files", []):
    path = folder / str(entry.get("path", ""))
    if not path.is_file():
      issues.append(f"{entry.get('path')}: missing")
      continue
    data = path.read_bytes()
    if _sha(data) != entry.get("sha256"):
      issues.append(f"{entry.get('path')}: checksum mismatch")
    if entry.get("path") == "tasks.json":
      doc = json.loads(data)
  if doc is None:
    return {"ok": False, "issues": issues or ["no tasks.json in manifest"], "counts": {}, "cross_project_edges": 0, "manifest": manifest, "tasks": None}
  if doc.get("format") != TASKS_FORMAT:
    issues.append("tasks.json is not a GoalGuard snapshot")
  if not doc.get("completeness", {}).get("complete"):
    issues.append("snapshot is marked partial")
  tasks = doc.get("tasks") or []
  ids = [t.get("provider_id") for t in tasks]
  portable = [t.get("portable_id") for t in tasks]
  if len(set(ids)) != len(ids) or len(set(portable)) != len(portable):
    issues.append("duplicate task IDs")
  known = set(ids)
  own_project = {t.get("provider_project_id") for t in tasks}
  cross = 0
  graph: dict[int, list[int]] = {}
  for t in tasks:
    for rel in t.get("relations") or []:
      other = rel.get("other_provider_id")
      if other not in known:
        if rel.get("other_provider_project_id") in own_project:
          issues.append(f"task {t.get('provider_id')}: {rel.get('kind')} -> {other} is missing from the snapshot")
        else:
          cross += 1
        continue
      if rel.get("kind") in PREREQ:
        graph.setdefault(t["provider_id"], []).append(other)
  if _has_cycle(graph):
    issues.append("dependency cycle among blocked/follows relations")
  if len(tasks) != manifest.get("counts", {}).get("tasks"):
    issues.append("task count differs from the manifest")
  return {"ok": not issues, "issues": issues, "counts": {"tasks": len(tasks)}, "cross_project_edges": cross, "manifest": manifest, "tasks": doc}


def _has_cycle(graph: dict[int, list[int]]) -> bool:
  """Detect a cycle in a dependency graph without recursion.

  Args:
    graph: node -> prerequisite nodes.

  Returns:
    True when any cycle exists.
  """
  state: dict[int, int] = {}
  for start in graph:
    if state.get(start):
      continue
    stack = [(start, iter(graph.get(start, ())))]
    state[start] = 1
    while stack:
      node, children = stack[-1]
      nxt = next(children, None)
      if nxt is None:
        state[node] = 2
        stack.pop()
      elif state.get(nxt) == 1:
        return True
      elif not state.get(nxt):
        state[nxt] = 1
        stack.append((nxt, iter(graph.get(nxt, ()))))
  return False


def verify_parent(partition_folder: Path) -> dict:
  """Check a partition manifest's child references and hashes.

  Args:
    partition_folder: <out>/<partition>.

  Returns:
    {"ok", "issues", "children"}.
  """
  parent = _load_json(partition_folder / "manifest.json")
  issues, seen = [], set()
  for child in parent.get("children", []):
    pid = child.get("project_id")
    if pid in seen:
      issues.append(f"{pid}: listed twice")
    seen.add(pid)
    path = (partition_folder / str(child.get("path", ""))).resolve()
    if not path.is_relative_to(partition_folder.resolve()) or not path.is_file():
      issues.append(f"{pid}: child manifest missing or outside the partition folder")
    elif _sha(path.read_bytes()) != child.get("sha256"):
      issues.append(f"{pid}: child manifest changed since the parent was written")
  return {"ok": not issues, "issues": issues, "children": sorted(seen)}
