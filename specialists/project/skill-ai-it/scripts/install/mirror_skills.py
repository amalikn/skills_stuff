#!/usr/bin/env python3
"""Mirror one agent's skill install folder into another agent's as symlinks to the canonical skill folders. Stdlib only.

Why (operator, 2026-11-03): Continue (VS Code) should see the same skills Claude Code, Codex and Hermes use, as symlinks rather than copies, so
an edit in skills_stuff reaches every agent. Each link points at the realpath of the source entry, never at another install's link.

Continue 2.0.0 follows a symlinked skill folder (its directory walker skips only entries whose VS Code type is exactly SymbolicLink, which is a
broken link; a link to a folder reports Directory|SymbolicLink), so per-skill links work there.

Usage:
    python scripts/install/mirror_skills.py                                   # plan: ~/.claude/skills -> ~/.continue/skills
    python scripts/install/mirror_skills.py --apply                           # create and repoint links
    python scripts/install/mirror_skills.py --source ~/.codex/skills --target ~/.continue/skills --apply --prune

Safety: read-only unless --apply. With --apply it creates links, repoints links that point elsewhere, and with --prune removes links whose
name is no longer in the source. It never replaces or removes a real file or folder in the target; those are reported as collisions.
Exit: 0, or 1 when a collision was found.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path


def source_skills(source: Path) -> dict[str, Path]:
  """List the skills in a source install folder.

  Args:
    source: an agent's skills folder whose entries are skill folders or links to them.

  Returns:
    Skill folder name mapped to the resolved canonical folder, for entries holding a SKILL.md; dot entries are skipped.
  """
  skills = {}
  for entry in sorted(source.iterdir()):
    if entry.name.startswith(".") or not (entry / "SKILL.md").is_file():
      continue
    skills[entry.name] = entry.resolve()
  return skills


def plan(skills: dict[str, Path], target: Path, prune: bool) -> list[tuple[str, str, Path | None]]:
  """Work out what each target entry needs.

  Args:
    skills: name to canonical folder, from source_skills.
    target: the folder the links go in.
    prune: whether links absent from the source are to be removed.

  Returns:
    (action, name, canonical) rows; action is ok, create, repoint, collision or prune.
  """
  rows: list[tuple[str, str, Path | None]] = []
  for name, canonical in skills.items():
    link = target / name
    if link.is_symlink():
      action = "ok" if Path(os.readlink(link)) == canonical else "repoint"
    elif link.exists():
      action = "collision"
    else:
      action = "create"
    rows.append((action, name, canonical))
  if prune and target.is_dir():
    for entry in sorted(target.iterdir()):
      if entry.is_symlink() and entry.name not in skills:
        rows.append(("prune", entry.name, None))
  return rows


def apply(rows: list[tuple[str, str, Path | None]], target: Path) -> None:
  """Carry out the planned link changes.

  Args:
    rows: the plan from plan().
    target: the folder the links go in; created if missing.

  Returns:
    None.
  """
  target.mkdir(parents=True, exist_ok=True)
  for action, name, canonical in rows:
    link = target / name
    if action in ("repoint", "prune"):
      link.unlink()
    if action in ("create", "repoint"):
      link.symlink_to(canonical, target_is_directory=True)


def main() -> int:
  """Parse arguments, print the plan and apply it when asked.

  Returns:
    0, or 1 when a real file or folder in the target blocks a link.
  """
  parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  parser.add_argument("--source", type=Path, default=Path.home() / ".claude" / "skills", help="install folder to mirror")
  parser.add_argument("--target", type=Path, default=Path.home() / ".continue" / "skills", help="install folder to link into")
  parser.add_argument("--prune", action="store_true", help="also remove target links whose name is not in the source")
  parser.add_argument("--apply", action="store_true", help="write the changes; without it only the plan is printed")
  args = parser.parse_args()
  started = time.monotonic()
  rows = plan(source_skills(args.source.expanduser()), args.target.expanduser(), args.prune)
  for action, name, canonical in rows:
    if action != "ok":
      print(f"{action:9} {name}" + (f" -> {canonical}" if canonical else ""))
  counts = {a: sum(1 for r in rows if r[0] == a) for a in ("ok", "create", "repoint", "prune", "collision")}
  if args.apply:
    apply([r for r in rows if r[0] in ("create", "repoint", "prune")], args.target.expanduser())
  mode = "applied" if args.apply else "plan only (pass --apply to write)"
  print(f"{mode}: " + ", ".join(f"{k} {v}" for k, v in counts.items()) + f"; {time.monotonic() - started:.2f}s")
  return 1 if counts["collision"] else 0


if __name__ == "__main__":
  sys.exit(main())
