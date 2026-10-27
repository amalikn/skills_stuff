"""The only writer: append-only JSONL ledgers under .kc/ and whole-file writes of derived outputs, behind a write lock.

Imported, not run. Every write needs apply=True from the caller and a held lock (write_lock); without apply the functions return
what they would do and touch nothing. Appends are flushed and fsynced; file writes go to a temporary file then os.replace, so an
interruption leaves the old file (INV-012). Paths are checked to stay inside the project root (no traversal, no symlink escape).
Safety: writes only below the project root passed in.
"""

import contextlib
import json
import os
from pathlib import Path

from . import settings
from .errors import InputError, ValidationFailed, WriteFailed

_held: set[str] = set()


def contained(root: Path, rel: str | Path) -> Path:
  """Resolve a project-relative path and refuse anything outside the root.

  Args:
    root: project root.
    rel: path relative to the root.

  Returns:
    The resolved absolute path.

  Raises:
    InputError: the path escapes the root (.., absolute path or symlink).
  """
  base = root.resolve()
  target = (base / rel).resolve()
  if not target.is_relative_to(base):
    raise InputError(f"path escapes the project root: {rel}")
  return target


def read_jsonl(path: Path) -> list[dict]:
  """Read a JSONL file.

  Args:
    path: the file; a missing file reads as empty.

  Returns:
    The records in file order.

  Raises:
    ValidationFailed: a line is not a JSON object.
  """
  if not path.exists():
    return []
  out = []
  for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
    if not line.strip():
      continue
    try:
      rec = json.loads(line)
    except json.JSONDecodeError as err:
      raise ValidationFailed(f"{path}:{n}: not JSON: {err.msg}") from err
    if not isinstance(rec, dict):
      raise ValidationFailed(f"{path}:{n}: not a JSON object")
    out.append(rec)
  return out


@contextlib.contextmanager
def write_lock(root: Path):
  """Hold the project's single write lock (.kc/locks/write.lock) for the duration of the block.

  Args:
    root: project root.

  Yields:
    None.

  Raises:
    WriteFailed: another writer holds the lock (remove the file only after checking no curator run is active).
  """
  lock = settings.kc_path(root, "locks", "write.lock")
  lock.parent.mkdir(parents=True, exist_ok=True)
  try:
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
  except FileExistsError as err:
    raise WriteFailed(f"another curator run holds {lock}") from err
  key = str(root.resolve())
  try:
    os.write(fd, str(os.getpid()).encode())
    os.close(fd)
    _held.add(key)
    yield
  finally:
    _held.discard(key)
    lock.unlink(missing_ok=True)


def _require_lock(root: Path) -> None:
  """Refuse a write made outside write_lock.

  Args:
    root: project root.

  Raises:
    WriteFailed: the lock is not held by this process.
  """
  if str(root.resolve()) not in _held:
    raise WriteFailed("write attempted without holding the write lock")


def append(root: Path, name: str, records: list[dict], apply: bool) -> int:
  """Append records to one ledger.

  Args:
    root: project root.
    name: ledger name (settings.LEDGERS).
    records: records to append, in order.
    apply: False reports the count only.

  Returns:
    Number of records appended (or that would be).

  Raises:
    WriteFailed: lock not held or the write failed.
  """
  if not records or not apply:
    return len(records)
  _require_lock(root)
  path = settings.ledger_path(root, name)
  path.parent.mkdir(parents=True, exist_ok=True)
  try:
    with path.open("a", encoding="utf-8") as fh:
      for rec in records:
        fh.write(json.dumps(rec, sort_keys=True, ensure_ascii=False) + "\n")
      fh.flush()
      os.fsync(fh.fileno())
  except OSError as err:
    raise WriteFailed(f"append to {path} failed: {err}") from err
  return len(records)


def write_text(root: Path, rel: str | Path, text: str, apply: bool) -> bool:
  """Replace one file inside the project atomically when its content differs.

  Args:
    root: project root.
    rel: project-relative path.
    text: new content.
    apply: False reports whether it would change only.

  Returns:
    True when the content differs from what is on disk.

  Raises:
    InputError: the path escapes the root.
    WriteFailed: lock not held or the write failed.
  """
  target = contained(root, rel)
  current = target.read_text(encoding="utf-8") if target.exists() else None
  if current == text:
    return False
  if not apply:
    return True
  _require_lock(root)
  target.parent.mkdir(parents=True, exist_ok=True)
  tmp = target.with_name(f".{target.name}.kc-tmp")
  try:
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, target)
  except OSError as err:
    tmp.unlink(missing_ok=True)
    raise WriteFailed(f"write {target} failed: {err}") from err
  return True
