"""The project's decisions.jsonl: append-only, hash-chained decision log (references/decision-rules.md, Record formats).

Imported, not run. Each line is one JSON object with decision_id, kind, actor, contract_revision_before/after, rationale, refs, at
and prev_hash (the SHA-256 of the previous line's exact text; "" for the first line). Reading verifies the chain.

Writes: append() writes only when apply=True, and only the kinds GoalGuard itself may record (verdict, park). Approvals, overrides
and revisions are the owner's lines, written through the owner's change-control path, never by this module (MVP-007).
"""

import datetime as dt
import fcntl
import hashlib
import json
import os
import uuid
from pathlib import Path

from .errors import RecordError, WriteRefused

KINDS = ("verdict", "approval", "override", "revision", "park", "completion")
WRITABLE_KINDS = ("verdict", "park")


def line_hash(line: str) -> str:
  """Hash one log line as written.

  Args:
    line: the line text without its newline.

  Returns:
    The hex SHA-256 digest.
  """
  return hashlib.sha256(line.encode("utf-8")).hexdigest()


def read(path: Path) -> tuple[list[dict], list[str]]:
  """Read and verify the log.

  Args:
    path: the decisions.jsonl file; absent means an empty log.

  Returns:
    (entries, issues): every parsed entry in order, and chain or format problems (an empty list when the chain holds).
  """
  if not path.exists():
    return [], []
  entries, issues, prev = [], [], ""
  for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
    if not line.strip():
      continue
    try:
      entry = json.loads(line)
    except json.JSONDecodeError:
      issues.append(f"line {number}: not JSON")
      prev = line_hash(line)
      continue
    if entry.get("prev_hash", "") != prev:
      issues.append(f"line {number}: prev_hash does not match line {number - 1} (edited or reordered history)")
    if entry.get("kind") not in KINDS:
      issues.append(f"line {number}: unknown kind {entry.get('kind')!r}")
    entries.append(entry)
    prev = line_hash(line)
  return entries, issues


def approvals(entries: list[dict]) -> list[dict]:
  """Return the approval entries.

  Args:
    entries: parsed log entries.

  Returns:
    Entries whose kind is approval, in log order.
  """
  return [e for e in entries if e.get("kind") == "approval"]


def latest_verdict(entries: list[dict]) -> dict | None:
  """Return the most recent verdict entry.

  Args:
    entries: parsed log entries.

  Returns:
    The last entry of kind verdict, or None when there is none.
  """
  verdicts = [e for e in entries if e.get("kind") == "verdict"]
  return verdicts[-1] if verdicts else None


def build_entry(kind: str, actor: str, revision: str, rationale: str, refs: list[str], payload: dict, prev_hash: str) -> dict:
  """Build one log entry.

  Args:
    kind: verdict or park.
    actor: the agent or session that recorded it.
    revision: the contract revision it was decided against (before and after are equal for these kinds).
    rationale: why.
    refs: evidence references.
    payload: the verdict or parked idea.
    prev_hash: hash of the last line in the log.

  Returns:
    The entry as a dict, keys in log order.
  """
  return {
    "decision_id": f"gg-{uuid.uuid4().hex[:12]}",
    "kind": kind,
    "actor": actor,
    "contract_revision_before": revision,
    "contract_revision_after": revision,
    "rationale": rationale,
    "refs": refs,
    "at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
    "prev_hash": prev_hash,
    "payload": payload,
  }


def append(path: Path, kind: str, actor: str, revision: str, rationale: str, refs: list[str], payload: dict, apply: bool) -> dict:
  """Plan, and with apply write, one appended line under an exclusive lock.

  Args:
    path: the decisions.jsonl file (its .gg/ folder must exist).
    kind: verdict or park.
    actor: the recording agent or session.
    revision: contract revision.
    rationale: why.
    refs: evidence references.
    payload: the record.
    apply: False prints the plan only; True writes.

  Returns:
    {"applied": bool, "path": str, "entry": dict}.

  Raises:
    WriteRefused: the kind is not one GoalGuard may write, the chain is already broken, or the .gg/ folder is missing.
  """
  if kind not in WRITABLE_KINDS:
    raise WriteRefused(f"GoalGuard never writes {kind!r} entries; only the owner records approvals, overrides and revisions")
  if not path.parent.is_dir():
    raise WriteRefused(f"{path.parent} does not exist: enrol the project before recording decisions")
  _, issues = read(path)
  if issues:
    raise WriteRefused(f"{path} chain is broken ({issues[0]}); repair it with the owner before appending")
  if not apply:
    last = path.read_text(encoding="utf-8").splitlines()[-1] if path.exists() and path.stat().st_size else ""
    return {"applied": False, "path": str(path), "entry": build_entry(kind, actor, revision, rationale, refs, payload, line_hash(last) if last else "")}
  fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_APPEND, 0o644)
  with os.fdopen(fd, "r+", encoding="utf-8") as handle:
    fcntl.flock(handle, fcntl.LOCK_EX)
    handle.seek(0)
    lines = [ln for ln in handle.read().splitlines() if ln.strip()]
    entry = build_entry(kind, actor, revision, rationale, refs, payload, line_hash(lines[-1]) if lines else "")
    handle.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")
    handle.flush()
    os.fsync(handle.fileno())
  entries, issues = read(path)
  if issues or not entries or entries[-1]["decision_id"] != entry["decision_id"]:
    raise RecordError(f"{path}: appended line did not read back cleanly ({issues[:1]})")
  return {"applied": True, "path": str(path), "entry": entry}
