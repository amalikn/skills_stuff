#!/usr/bin/env python3
"""Move a project's flat docs/history into the by-kind layout (history_layout.py), repoint every reference, and regenerate the index.

Why (operator, 2026-11-11): the standard layout is one subfolder per kind; projects with years of flat archives need a move that keeps every link
working. Moved files keep their names; links inside them are recomputed from their new folder (archives are "verbatim except relative links");
links and path mentions elsewhere that point at a moved file are repointed.

What is rewritten, and where:
  - Markdown links `](target)` in any text file under --refs-root that resolve to a moved file (exact path resolution, any project).
  - Path mentions `docs/history/<name>` (no link) in the project's own files, and `<project folder>/docs/history/<name>` in files elsewhere
    under --refs-root, so another project's identically named archive is never touched.
  - The project's docs/history/readme.md: hand-written intro and descriptions kept, the file list regenerated with a summary line per file.

Usage:
    python3 history_migrate.py --project-root <project>                         # plan: moves per kind, files whose references change
    python3 history_migrate.py --project-root <project> --apply                 # git mv, rewrite, regenerate the index, verify links
    options: --refs-root <dir> (default: the project's git top level), --allow-dirty (move with uncommitted changes under docs/history)
Safety: plan by default; refuses with uncommitted changes under docs/history unless --allow-dirty; verifies after the write that every link
that resolved before still resolves (exit 1 and the list when one does not).
Exit: 0 done or planned (also: nothing to move), 1 refused or a link broke, 2 bad arguments.
Budget: one read per text file under --refs-root (an apn-sized repo, about 6,000 files, in about 5 s).
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import pathlib
import re
import subprocess
import sys
import time

_spec = importlib.util.spec_from_file_location("history_layout", pathlib.Path(__file__).resolve().parent / "history_layout.py")
hl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hl)

TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".toml", ".py", ".sh", ".txt", ".json", ".j2", ""}
SKIP_PARTS = {".git", "node_modules", ".venv", "__pycache__", ".ai-context", "graphify-out", ".remember"}  # .remember: another tool's memory, never rewritten
LINK = re.compile(r"\]\(([^)\s]+)\)")
MAX_BYTES = 2_000_000


def git(root: pathlib.Path, *args: str) -> subprocess.CompletedProcess:
  """Run git in a folder.

  Args:
    root: the folder.
    args: git arguments.

  Returns:
    The finished process (text output).
  """
  return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=120)


def plan_moves(root: pathlib.Path) -> dict[pathlib.Path, pathlib.Path]:
  """The flat history files to move and where each goes.

  Args:
    root: the project root.

  Returns:
    old absolute path -> new absolute path, for every top-level file of a known kind.
  """
  top = root / hl.HISTORY
  out = {}
  for f in sorted(top.glob("*.md")):
    kind = hl.kind_of(f.name)
    if kind:
      out[f] = top / kind[1] / f.name
  return out


def text_files(base: pathlib.Path) -> list[pathlib.Path]:
  """Text files under a folder that may hold references.

  Args:
    base: the folder to walk.

  Returns:
    Paths (named `justfile` or with a text suffix), skipping VCS, caches and large files.
  """
  out = []
  for dirpath, dirs, files in os.walk(base):
    dirs[:] = [d for d in dirs if d not in SKIP_PARTS]
    for name in files:
      p = pathlib.Path(dirpath) / name
      if (p.suffix in TEXT_SUFFIXES and (p.suffix or name == "justfile")) or name == "justfile":
        try:
          if p.stat().st_size <= MAX_BYTES:
            out.append(p)
        except OSError:
          continue
  return out


def relink(text: str, old_dir: pathlib.Path, new_dir: pathlib.Path, moves: dict[pathlib.Path, pathlib.Path]) -> str:
  """Recompute relative Markdown links for a file read at old_dir and now living at new_dir, following moved targets.

  Args:
    text: the file's content.
    old_dir: the folder the links were written for.
    new_dir: the folder the file is in now.
    moves: old -> new paths of moved files.

  Returns:
    The text with each relative link that resolves (before the move) pointing at the same file from new_dir.
  """
  def fix(m: re.Match) -> str:
    """One `](target)` match, its target recomputed or left as it is.

    Args:
      m: the regex match.

    Returns:
      The replacement text.
    """
    target = m.group(1)
    if re.match(r"^([a-z][a-z0-9+.-]*:|/|#)", target, re.I):
      return m.group(0)
    path, sep, anchor = target.partition("#")
    if not path:
      return m.group(0)
    old_target = pathlib.Path(os.path.normpath(old_dir / path))
    new_target = moves.get(old_target, old_target)
    if old_dir == new_dir and new_target == old_target:
      return m.group(0)
    if not (old_target.exists() or old_target in moves):
      return m.group(0)
    rel = os.path.relpath(new_target, new_dir)
    return f"]({rel}{sep}{anchor})"

  return LINK.sub(fix, text)


def mentions(text: str, inside: bool, folder: str, moves_by_name: dict[str, str]) -> str:
  """Repoint plain path mentions of moved files (not links).

  Args:
    text: a file's content.
    inside: whether the file belongs to the migrated project.
    folder: the project's folder name.
    moves_by_name: file name -> its subfolder.

  Returns:
    The text with `docs/history/<name>` (inside) or `<folder>/docs/history/<name>` (elsewhere) gaining the subfolder.
  """
  lead = r"(?<![\w.-])" + (r"((?:[\w.-]+/)*?" if inside else r"((?:[\w.-]+/)*?" + re.escape(folder) + r"/") + r"docs/history/)"
  rx = re.compile(lead + r"([\w.-]+\.md)\b")

  def fix(m: re.Match) -> str:
    """One path mention, given its kind subfolder when the file moved.

    Args:
      m: the regex match.

    Returns:
      The replacement text.
    """
    sub = moves_by_name.get(m.group(2))
    return m.group(1) + sub + "/" + m.group(2) if sub else m.group(0)

  return rx.sub(fix, text)


def broken_links(path: pathlib.Path, text: str) -> list[str]:
  """Relative links in a file that do not resolve.

  Args:
    path: the file (its folder is the link base).
    text: its content.

  Returns:
    The targets that do not exist.
  """
  out = []
  for m in LINK.finditer(text):
    t = m.group(1).partition("#")[0]
    if t and not re.match(r"^([a-z][a-z0-9+.-]*:|/)", t, re.I) and not (path.parent / t).exists():
      out.append(t)
  return out


def main(argv: list[str] | None = None) -> int:
  """Plan or apply the migration.

  Args:
    argv: command-line arguments (None reads sys.argv).

  Returns:
    Exit code: 0 done or planned, 1 refused or a link broke, 2 bad arguments.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("--project-root", type=pathlib.Path, required=True)
  ap.add_argument("--refs-root", type=pathlib.Path)
  ap.add_argument("--apply", action="store_true")
  ap.add_argument("--allow-dirty", action="store_true")
  a = ap.parse_args(argv)
  started = time.monotonic()
  root = a.project_root.resolve()
  if not (root / hl.HISTORY).is_dir():
    print(f"no {hl.HISTORY} in {root}", file=sys.stderr)
    return 2
  top_level = git(root, "rev-parse", "--show-toplevel").stdout.strip()
  refs_root = (a.refs_root or pathlib.Path(top_level or root)).resolve()
  moves = plan_moves(root)
  by_kind: dict[str, int] = {}
  for new in moves.values():
    by_kind[new.parent.name] = by_kind.get(new.parent.name, 0) + 1
  moves_by_name = {o.name: n.parent.name for o, n in moves.items()}
  print(f"{root}: {len(moves)} file(s) to move: " + ", ".join(f"{k}/ {n}" for k, n in sorted(by_kind.items())) if moves else f"{root}: nothing to move")

  changed: dict[pathlib.Path, str] = {}
  before_broken: dict[pathlib.Path, set[str]] = {}
  for f in text_files(refs_root):
    if f in moves or f == root / hl.HISTORY / "readme.md":
      continue
    try:
      text = f.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
      continue
    if "docs/history" not in text and not any(name in text for name in moves_by_name):
      continue
    inside = root in f.parents
    new = mentions(relink(text, f.parent, f.parent, moves), inside, root.name, moves_by_name)
    if new != text:
      changed[f] = new
      before_broken[f] = set(broken_links(f, text))
  moved_text: dict[pathlib.Path, str] = {}
  for old, new in moves.items():
    text = old.read_text(encoding="utf-8")
    before_broken[new] = {t for t in broken_links(old, text)}
    moved_text[new] = mentions(relink(text, old.parent, new.parent, moves), True, root.name, moves_by_name)
  print(f"references: {len(changed)} file(s) outside the moved ones change"
        + (": " + ", ".join(str(p.relative_to(refs_root)) for p in sorted(changed)[:12]) + (" ..." if len(changed) > 12 else "") if changed else ""))
  if not moves:
    if a.apply:
      hl.write_index(root)
      print("index regenerated")
    return 0
  if not a.apply:
    print(f"plan only; --apply moves them (refs root {refs_root}) — {time.monotonic() - started:.1f} s")
    return 0
  dirty = git(root, "status", "--porcelain", "--", hl.HISTORY).stdout.strip()
  if dirty and not a.allow_dirty:
    print(f"refused: uncommitted changes under {hl.HISTORY} (commit first, or --allow-dirty):\n{dirty}", file=sys.stderr)
    return 1
  for old, new in moves.items():
    new.parent.mkdir(parents=True, exist_ok=True)
    r = git(root, "mv", str(old), str(new))
    if r.returncode != 0:
      old.rename(new)
    new.write_text(moved_text[new], encoding="utf-8")
  for f, text in changed.items():
    f.write_text(text, encoding="utf-8")
  hl.write_index(root)
  broke = []
  for f in [*changed, *moved_text, root / hl.HISTORY / "readme.md"]:
    now = set(broken_links(f, f.read_text(encoding="utf-8")))
    broke += [f"{f.relative_to(refs_root)}: {t}" for t in sorted(now - before_broken.get(f, set()))]
  print(f"moved {len(moves)}, rewrote {len(changed)} reference file(s), index regenerated — {time.monotonic() - started:.1f} s")
  if broke:
    print(f"links broken by the move ({len(broke)}):", file=sys.stderr)
    for b in broke[:20]:
      print("  " + b, file=sys.stderr)
    return 1
  return 0


if __name__ == "__main__":
  sys.exit(main())
