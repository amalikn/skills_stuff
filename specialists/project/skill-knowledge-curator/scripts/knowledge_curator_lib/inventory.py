"""Read-only discovery: fingerprint every in-scope source, detect changes, renames, removals and exact duplicates, and parse sections.

Imported, not run. Produces the records `kc inventory --apply` appends to sources.jsonl and sections.jsonl; unchanged files produce
none (INV-011). A renamed file keeps its source_id when its bytes match a source whose old path vanished. Symlinks are never
followed; one pointing outside the root is an exclusion (INV-002, T-012). Safety: reads files and runs `git rev-parse HEAD` with a
timeout; writes nothing.
"""

import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from . import ids, mdparse, settings
from .state import State


@dataclass
class InventoryResult:
  """Outcome of one inventory pass.

  Attributes:
    source_records: new source_version / source_removed records.
    section_records: new section records.
    counts: new, changed, renamed, unchanged, removed, unsupported totals.
    exclusions: files or folders left out, each with its reason.
    duplicate_groups: lists of paths whose bytes are identical.
  """

  source_records: list = field(default_factory=list)
  section_records: list = field(default_factory=list)
  counts: dict = field(default_factory=dict)
  exclusions: list = field(default_factory=list)
  duplicate_groups: list = field(default_factory=list)


def git_head(root: Path) -> str | None:
  """Commit at HEAD of the repository holding root.

  Args:
    root: project root.

  Returns:
    The commit hash, or None when root is not in a git repository or git fails.
  """
  try:
    run = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=settings.GIT_TIMEOUT_S, check=False)
  except OSError, subprocess.TimeoutExpired:
    return None
  if run.returncode != 0:
    return None
  return run.stdout.strip() or None


def _included(rel: str, patterns: list[str]) -> bool:
  """Whether a project-relative path matches an include glob.

  Args:
    rel: POSIX relative path.
    patterns: globs; `**/` also matches files at the root.

  Returns:
    True when any pattern matches.
  """
  path = PurePosixPath(rel)
  return any(path.full_match(p) or (p.startswith("**/") and path.full_match(p[3:])) for p in patterns)


def discover(root: Path, cfg: dict) -> tuple[list[str], list[dict]]:
  """Walk the project and list in-scope files and exclusions.

  Args:
    root: project root.
    cfg: project config (include, exclude_dirs).

  Returns:
    (sorted relative paths, exclusions with path and reason).
  """
  base = root.resolve()
  files, excluded = [], []
  for dirpath, dirnames, filenames in os.walk(base, followlinks=False):
    rel_dir = Path(dirpath).relative_to(base)
    for name in sorted(dirnames):
      if name in cfg["exclude_dirs"]:
        excluded.append({"path": (rel_dir / name).as_posix(), "reason": "excluded directory (config exclude_dirs)"})
    dirnames[:] = sorted(d for d in dirnames if d not in cfg["exclude_dirs"])
    for name in sorted(filenames):
      rel = (rel_dir / name).as_posix()
      if not _included(rel, cfg["include"]):
        continue
      full = Path(dirpath) / name
      if full.is_symlink():
        inside = full.resolve().is_relative_to(base)
        excluded.append({"path": rel, "reason": "symlink inside root (inventory its target)" if inside else "symlink pointing outside root"})
        continue
      files.append(rel)
  return sorted(files), sorted(excluded, key=lambda e: e["path"])


def section_records(source_id: str, version_id: str, text: str) -> list[dict]:
  """Section records for one source version, with stable IDs.

  A section's ID depends on its source, heading path, kind and text, so an unchanged block keeps its ID (and its coverage) when
  other parts of the file change.

  Args:
    source_id: owning source.
    version_id: source version the line spans refer to.
    text: the document.

  Returns:
    Section records in document order.
  """
  out, seen = [], {}
  for block in mdparse.parse_blocks(text):
    text_sha = ids.sha256_text(ids.norm_ws(block.text))
    key = (source_id, list(block.heading_path), block.kind, text_sha)
    ordinal = seen.get(ids.canonical(key), 0)
    seen[ids.canonical(key)] = ordinal + 1
    rec = {
      "record": "section",
      "section_id": ids.make_id("sec", *key, ordinal),
      "source_id": source_id,
      "source_version_id": version_id,
      "heading_path": list(block.heading_path),
      "kind": block.kind,
      "line_start": block.line_start,
      "line_end": block.line_end,
      "text_sha256": text_sha,
    }
    auto = _auto_context(block)
    if auto:
      rec["auto_context"] = auto
    out.append(rec)
  return out


def _auto_context(block: mdparse.Block) -> str | None:
  """Reason a block needs no claim extraction, for the narrow cases that are certain.

  Args:
    block: parsed block.

  Returns:
    The reason, or None (the agent must decide).
  """
  if block.kind == "front_matter":
    return "front matter; the declared status is recorded on the source version"
  if block.kind == "paragraph" and block.line_start == block.line_end and mdparse.declared_status(block.text):
    return "document status line; recorded as declared_status on the source version"
  return None


def _version_record(st: State, rel: str, data: bytes, source_id: str, commit: str | None) -> tuple[dict, str | None]:
  """Build one source_version record.

  Args:
    st: current state (for project_id).
    rel: relative path.
    data: file bytes.
    source_id: stable source ID.
    commit: git HEAD or None.

  Returns:
    (record, decoded text or None when not UTF-8).
  """
  sha = ids.sha256_bytes(data)
  try:
    text = data.decode("utf-8")
    state, reason = "processed", None
  except UnicodeDecodeError:
    text, state, reason = None, "unsupported", "not UTF-8 text"
  rec = {
    "record": "source_version",
    "project_id": st.cfg["project_id"],
    "source_id": source_id,
    "source_version_id": ids.make_id("sv", source_id, sha),
    "path": rel,
    "sha256": sha,
    "size_bytes": len(data),
    "format": "markdown" if rel.endswith(".md") else "text",
    "ingestion_state": state,
    "declared_status": mdparse.declared_status(text) if text else None,
    "git_commit": commit,
  }
  if reason:
    rec["reason"] = reason
  return rec, text


def build(st: State) -> InventoryResult:
  """Compare the live tree with the ledger and produce the records to append.

  Args:
    st: current state.

  Returns:
    The inventory result.
  """
  res = InventoryResult()
  files, res.exclusions = discover(st.root, st.cfg)
  known = st.source_by_path()
  live = set(files)
  vanished = {s["sha256"]: s for p, s in known.items() if p not in live}
  commit = git_head(st.root)
  counts = dict.fromkeys(("new", "changed", "renamed", "unchanged", "removed", "unsupported"), 0)
  by_sha: dict[str, list[str]] = {}
  for rel in files:
    data = (st.root / rel).read_bytes()
    sha = ids.sha256_bytes(data)
    by_sha.setdefault(sha, []).append(rel)
    prior = known.get(rel)
    if prior and prior["sha256"] == sha:
      counts["unchanged"] += 1
      continue
    renamed = vanished.pop(sha, None) if not prior else None
    source_id = (prior or renamed or {}).get("source_id") or ids.make_id("src", st.cfg["project_id"], rel)
    rec, text = _version_record(st, rel, data, source_id, commit)
    if renamed:
      rec["renamed_from"] = renamed["path"]
    counts["renamed" if renamed else "changed" if prior else "new"] += 1
    counts["unsupported"] += rec["ingestion_state"] == "unsupported"
    res.source_records.append(rec)
    if text is not None:
      res.section_records.extend(section_records(source_id, rec["source_version_id"], text))
  for src in vanished.values():
    res.source_records.append({"record": "source_removed", "source_id": src["source_id"], "path": src["path"]})
    counts["removed"] += 1
  res.counts = counts
  res.duplicate_groups = sorted(paths for paths in by_sha.values() if len(paths) > 1)
  return res
