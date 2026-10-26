#!/usr/bin/env python3
"""Slurp Step 5b/6b check: are the engaged skills' write-backs committed, and what do their CHANGELOG and version say.

A write-back is done only when it is committed in the skills repo; a dirty skill file fails the self-audit, also when another session's
edits share the file (commit them together, or ask). Two slurps on 2026-10-26 reported 6b passed with skill-smc and skill-coder dirty and
the skill-smc CHANGELOG line behind its reference entries; this makes that visible instead of remembered.

Run:
    writeback_status.py skill-smc skill-coder skill-drawio          # skills by folder name, found anywhere in the skills repo
    writeback_status.py --repo /path/to/skills_stuff skill-smc

Per skill it prints: uncommitted files, the newest CHANGELOG heading or line, the manifest version, and the newest commit touching it;
then the repo's commits not yet pushed. Read-only (git status/log). Exit 1 when any named skill has uncommitted files or is not found.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

DEFAULT_REPO = Path("/Volumes/Data/_ai/_skills/skills_stuff")


def git(repo: Path, *args: str) -> str:
    """Run a read-only git command in the repo.

    Args:
        repo: the repository root.
        args: git arguments.

    Returns:
        Its stdout, stripped ("" on failure).
    """
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=30, check=False)
    return p.stdout.strip() if p.returncode == 0 else ""


def find_skill(repo: Path, name: str) -> Path | None:
    """Find a skill folder by name: a folder with that name holding a SKILL.md.

    Args:
        repo: the skills repo.
        name: the skill folder name, e.g. skill-smc.

    Returns:
        The folder, or None.
    """
    for skill_md in repo.glob(f"**/{name}/SKILL.md"):
        if ".git" not in skill_md.parts:
            return skill_md.parent
    return None


def newest_changelog(folder: Path) -> str:
    """The newest dated CHANGELOG heading or line of a skill.

    Args:
        folder: the skill folder.

    Returns:
        The first '## <date...>' heading after Contents, else the first dated '- YYYYMMDD' line, else "no CHANGELOG".
    """
    path = folder / "CHANGELOG.md"
    if not path.is_file():
        return "no CHANGELOG"
    text = path.read_text(encoding="utf-8")
    # Headings ("## 20261026_1844 ...") and dated lines ("- 20261026 ...") are both used; the newest date wins, the first written on a tie.
    entries = [(m.group(2), -m.start(), m.group(1)) for m in re.finditer(r"^(?:## |- )((\d{8})\b.*)$", text, re.M)]
    return max(entries)[2][:140] if entries else "no dated entry"


def version(folder: Path) -> str:
    """The skill's manifest version.

    Args:
        folder: the skill folder.

    Returns:
        manifest.json "version", or "-".
    """
    path = folder / "manifest.json"
    try:
        return str(json.loads(path.read_text(encoding="utf-8")).get("version", "-"))
    except (OSError, ValueError):
        return "-"


def main() -> int:
    """Print each named skill's write-back state.

    Returns:
        1 when a skill is dirty or missing, else 0.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("skills", nargs="+", help="skill folder names")
    ap.add_argument("--repo", type=Path, default=DEFAULT_REPO)
    a = ap.parse_args()
    bad = 0
    for name in a.skills:
        folder = find_skill(a.repo, name)
        if folder is None:
            print(f"{name}: NOT FOUND under {a.repo}")
            bad = 1
            continue
        rel = folder.relative_to(a.repo)
        dirty = [line for line in git(a.repo, "status", "--short", "--", str(rel)).splitlines() if line.strip()]
        last = git(a.repo, "log", "-1", "--format=%h %cs %s", "--", str(rel))[:120]
        state = "DIRTY" if dirty else "clean"
        print(f"{name} [{state}] version {version(folder)}")
        print(f"  changelog  {newest_changelog(folder)}")
        print(f"  last commit {last or '-'}")
        for line in dirty[:20]:
            print(f"  uncommitted {line}")
        bad |= bool(dirty)
    ahead = git(a.repo, "log", "--oneline", "@{u}..HEAD")
    print(f"unpushed commits: {len(ahead.splitlines()) if ahead else 0}" + (f" (push: git -C {a.repo} push)" if ahead else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
