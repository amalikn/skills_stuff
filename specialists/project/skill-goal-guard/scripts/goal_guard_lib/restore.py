"""Restore a verified GoalGuard snapshot into a clean Vikunja test instance (references/snapshot-and-restore.md, Restore; pilot step 8).

Imported, not run. Writes only with apply=True, through the two Vikunja seam writers (create_task, create_relation). It refuses a
target project holding tasks it did not create (not a clean instance), marks each created task with [gg:portable_id=...] so a rerun
is idempotent, creates only canonical relation kinds (Vikunja adds the inverse), and reads everything back before reporting success.
Restoring into a live instance needs conflict handling that is not built (Restore step 3).
"""

from pathlib import Path

from .errors import WriteRefused
from .records import parse_date
from .snapshot import DATE_FIELDS, verify
from .vikunja import Client

# Relation kinds created on restore; Vikunja creates the inverse of each (blocked, follows, parenttask, duplicates, copiedfrom).
CANONICAL = ("subtask", "related", "duplicateof", "blocking", "precedes", "copiedto")
# An edge seen only from its inverse side (task B "blocked" by A) is restored as the canonical edge from the other end (A "blocking" B).
INVERSE_OF = {"parenttask": "subtask", "duplicates": "duplicateof", "blocked": "blocking", "follows": "precedes", "copiedfrom": "copiedto"}
MARKER = "[gg:portable_id={}]"
WRITABLE = ("title", "description", "done", "priority", *DATE_FIELDS)


def _restore_body(record: dict) -> dict:
  """Build the create body for one task, with its portable-ID marker.

  Args:
    record: the snapshot record.

  Returns:
    Writable Task fields; unset dates are left out.
  """
  marker = MARKER.format(record["portable_id"])
  body = {k: record[k] for k in WRITABLE if record.get(k) is not None}
  body["description"] = (record.get("description") or "").rstrip() + ("\n\n" if record.get("description") else "") + marker
  return body


def _marker_of(task: dict) -> str | None:
  """Find the portable-ID marker in a restored task's description.

  Args:
    task: a raw Vikunja task.

  Returns:
    The portable ID, or None when the task carries no marker.
  """
  text = str(task.get("description") or "")
  start = text.rfind("[gg:portable_id=")
  if start < 0:
    return None
  end = text.find("]", start)
  return text[start + len("[gg:portable_id=") : end] if end > start else None


def restore(folder: Path, client: Client, target_project_id: int, apply: bool) -> dict:
  """Restore a verified snapshot into an empty (or GoalGuard-restored) project of a clean test instance.

  Args:
    folder: the project snapshot folder.
    client: a client bound to the TEST instance.
    target_project_id: the empty project to restore into.
    apply: create tasks and relations when True; plan only when False.

  Returns:
    {"applied", "plan": {"create_tasks", "create_relations", "skip_existing"}, "verify": {...} when applied, "not_restored": [...]}.

  Raises:
    WriteRefused: the snapshot fails verification, or the target holds tasks GoalGuard did not restore.
  """
  check = verify(folder)
  if not check["ok"]:
    raise WriteRefused(f"snapshot fails verification: {check['issues']}")
  records = check["tasks"]["tasks"]
  existing, _ = client.project_tasks(target_project_id)
  foreign = [t["id"] for t in existing if _marker_of(t) is None]
  if foreign:
    raise WriteRefused(f"target project {target_project_id} holds {len(foreign)} task(s) not restored by GoalGuard; restore only into a clean instance")
  new_id = {_marker_of(t): t["id"] for t in existing}
  by_provider = {r["provider_id"]: r for r in records}
  to_create = [r for r in records if r["portable_id"] not in new_id]
  pairs, seen = [], set()
  for r in records:
    for rel in r["relations"]:
      other = by_provider.get(rel["other_provider_id"])
      if other is None or (rel["kind"] not in CANONICAL and rel["kind"] not in INVERSE_OF):
        continue
      a, b, kind = r["portable_id"], other["portable_id"], rel["kind"]
      if kind in INVERSE_OF:
        a, b, kind = b, a, INVERSE_OF[kind]
      key = (kind, *sorted((a, b))) if kind == "related" else (kind, a, b)
      if key not in seen:
        seen.add(key)
        pairs.append((a, b, kind))
  existing_rel = _existing_relations(existing)
  rel_todo = [p for p in pairs if p not in existing_rel]
  plan = {"create_tasks": len(to_create), "create_relations": len(rel_todo), "skip_existing": len(records) - len(to_create)}
  not_restored = ["labels (label endpoints, not in the pilot)", "assignees and users", "attachments", "comments", "provider IDs (new IDs are mapped)"]
  if not apply:
    return {"applied": False, "plan": plan, "not_restored": not_restored}
  for r in to_create:
    created = client.create_task(target_project_id, _restore_body(r))
    new_id[r["portable_id"]] = int(created["id"])
  for a, b, kind in rel_todo:
    client.create_relation(new_id[a], new_id[b], kind)
  readback, _ = client.project_tasks(target_project_id)
  return {"applied": True, "plan": plan, "verify": _compare(records, readback, pairs), "not_restored": not_restored}


def _existing_relations(tasks: list[dict]) -> set[tuple[str, str, str]]:
  """List canonical relations already present among restored tasks.

  Args:
    tasks: raw Vikunja tasks of the target project.

  Returns:
    {(portable_a, portable_b, kind)} for relations between marked tasks.
  """
  portable = {t["id"]: _marker_of(t) for t in tasks}
  out = set()
  for t in tasks:
    for kind, others in (t.get("related_tasks") or {}).items():
      if kind not in CANONICAL:
        continue
      for other in others or []:
        a, b = portable.get(t["id"]), portable.get(other.get("id"))
        if a and b:
          out.add((a, b, kind))
          if kind == "related":
            out.add((b, a, kind))
  return out


def _compare(records: list[dict], readback: list[dict], pairs: list[tuple[str, str, str]]) -> dict:
  """Compare the restored project with the snapshot.

  Args:
    records: snapshot records.
    readback: raw tasks read back from the target.
    pairs: canonical relations that should exist.

  Returns:
    {"ok", "counts", "mismatches"}; done, priority, dates and relations are compared per task.
  """
  by_portable = {_marker_of(t): t for t in readback if _marker_of(t)}
  mismatches = []
  for r in records:
    t = by_portable.get(r["portable_id"])
    if t is None:
      mismatches.append(f"{r['portable_id']}: not found after restore")
      continue
    for f in ("title", "done", "priority"):
      if t.get(f) != r[f]:
        mismatches.append(f"{r['portable_id']}: {f} {t.get(f)!r} != {r[f]!r}")
    for f in DATE_FIELDS:
      if parse_date(t.get(f), f) != parse_date(r.get(f), f):
        mismatches.append(f"{r['portable_id']}: {f} differs")
  present = _existing_relations(readback)
  missing = [p for p in pairs if p not in present]
  mismatches += [f"relation {a} {k} {b} missing" for a, b, k in missing]
  return {
    "ok": not mismatches,
    "counts": {"snapshot": len(records), "restored": len(by_portable), "relations": len(pairs) - len(missing)},
    "mismatches": mismatches,
  }
