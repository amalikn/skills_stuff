#!/usr/bin/env python3
"""Build or check a project area's skills.md: the list of skills its child projects invoke.

Scans the governance files under --project-root (AGENTS.md, CLAUDE.md, AI_NAVIGATION.md, SKILL.md) for `skill-<name>` mentions, resolves each
name, and renders a skills.md with one table per kind of skill:

  shared         a folder with SKILL.md under the skills_stuff canonical root
  project-local  a folder with SKILL.md under --project-root
  installed      only an installed copy under ~/.claude/skills (no canonical source found)
  missing        mentioned, but no skill by that name exists anywhere

Names that are not skills are dropped: version markers (`skill-ai-it-version`), placeholders (`skill-name`), and names that match a folder under
--project-root which has no SKILL.md (for example `docs/skill-jdm-prep/`). Pass --ignore for any others.

Modes (stdlib only, read-only unless --write):
  --check  (default) compare the existing skills.md with what the scan finds; exit 1 on drift, 0 when in step
  --print  print the generated skills.md to stdout
  --write  write skills.md; refuses to replace an existing one unless --force, and then keeps skills.md.bak-YYYYMMDD_hhmm

The generated file is a starting point: the Use for column comes from each SKILL.md description, cut to fit. Edit it by hand afterwards and use
--check to spot skills that were added or dropped since.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys
from pathlib import Path

SKILLS_ROOT = Path("/Volumes/Data/_ai/_skills/skills_stuff")
INSTALLED_ROOT = Path.home() / ".claude" / "skills"
GOV_FILES = {"AGENTS.md", "CLAUDE.md", "AI_NAVIGATION.md", "SKILL.md"}
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "exports", ".remember", "graphify-out"}
DEFAULT_IGNORE = {"skill-ai-it-version", "skill-name"}
CONTAINERS = {"skills", ".agents", ".claude"}  # folders that hold a project's local skills, not projects themselves
# A name only counts as a skill reference when it is marked up: in backticks, bold, a link or path, or a slash command. Plain prose such as
# "the skill-package rules" is not a reference. Resolved skills keep every mention; this only filters names that resolve to nothing.
MARKED_RE = r"(?:[`*\[/]{name}\b|\b{name}[`*\]/])"
ALIAS_RE = re.compile(r"`?(skill-[a-z0-9-]+)`?[^\n]{0,12}?\b(?:aka|alias(?: for)?)\b[^\n]{0,4}?`?(skill-[a-z0-9-]+)`?")
NAME_RE = re.compile(r"\bskill-[a-z0-9]+(?:-[a-z0-9]+)*\b")
MAX_DEPTH = 4
MAX_WIDTH = 200
DESC_WIDTH = 80  # Use for: the SKILL.md description, cut to stay readable
USED_WIDTH = 70  # Used by: projects past this are summarised as "+N more"
MIN_FLEX = 40


def walk(root: Path, max_depth: int):
    """Yield (dirpath, dirnames, filenames) to max_depth, skipping caches and upstream clones."""
    base = len(root.parts)
    for dirpath, dirnames, filenames in os.walk(root):
        depth = len(Path(dirpath).parts) - base
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.endswith("-github")]
        if depth >= max_depth:
            dirnames[:] = []
        yield Path(dirpath), dirnames, filenames


def skill_dirs(root: Path, max_depth: int) -> dict[str, Path]:
    """Map skill folder name -> folder, for every folder holding a SKILL.md, or a manifest.json in a `skill-*` folder (older specialist packs)."""
    found: dict[str, Path] = {}
    if not root.is_dir():
        return found
    for dirpath, _, filenames in walk(root, max_depth):
        if "SKILL.md" in filenames or ("manifest.json" in filenames and dirpath.name.startswith("skill-")):
            found.setdefault(dirpath.name, dirpath)
    return found


def entry(folder: Path) -> Path:
    """The file that describes a skill folder: SKILL.md, else manifest.json."""
    return folder / "SKILL.md" if (folder / "SKILL.md").exists() else folder / "manifest.json"


def description(skill_md: Path) -> str:
    """The front matter `description:` of a SKILL.md (or a manifest.json's), or its first prose line."""
    try:
        text = skill_md.read_text(errors="replace")
    except OSError:
        return ""
    if skill_md.suffix == ".json":
        try:
            return " ".join(str(json.loads(text).get("description", "")).split())
        except ValueError:
            return ""
    m = re.search(r"^description:\s*(?:>-?|\|)?\s*(.*?)(?=^\S[^:\n]*:|^---)", text, re.M | re.S)
    if m:
        desc = " ".join(m.group(1).split()).strip("'\"")
        if desc:
            return desc
    for line in text.splitlines():
        s = line.strip()
        if s and not s.startswith(("#", "---", "<!--")) and ":" not in s[:20]:
            return s
    return ""


def owner(path: Path, root: Path, local_skills: dict[str, Path]) -> str:
    """The project a governance file belongs to: its folder relative to root, lifted out of any skill folder."""
    folder = path.parent
    local_paths = set(local_skills.values())
    while folder != root and (folder in local_paths or folder.name in CONTAINERS):
        folder = folder.parent
    rel = folder.relative_to(root).as_posix() if folder != root else "(this folder)"
    return rel


def scan(root: Path, also: list[Path], ignore: set[str]):
    """Every `skill-*` name mentioned in the governance files under root (plus --also files), with the projects that mention it.

    Returns (mentions, local skill folders, names seen marked up in backticks/bold/links, names introduced as aliases). Project-local skills are
    added as used by the project that holds them even when no file names them. A name matching a folder without a SKILL.md is dropped.
    """
    local = skill_dirs(root, MAX_DEPTH + 1)
    folders = {p.name for p, _, _ in walk(root, MAX_DEPTH + 1)}
    mentions: dict[str, set[str]] = {}
    marked: set[str] = set()
    aliases: set[str] = set()
    files = [p / f for p, _, fs in walk(root, MAX_DEPTH) for f in fs if f in GOV_FILES]
    for path in files + also:
        try:
            text = path.read_text(errors="replace")
        except OSError:
            continue
        who = owner(path, root, local) if path.is_relative_to(root) else path.parent.name
        for a_, b_ in ALIAS_RE.findall(text):  # "`skill-x` (alias `skill-y`)" or "`skill-x`, aka `skill-y`": the second is an alias
            aliases.add(b_)
        self_name = path.parent.name if path.name == "SKILL.md" else None
        for name in set(NAME_RE.findall(text)):
            if name in ignore or name == self_name:
                continue
            if name in folders and name not in local:
                continue  # a docs folder named like a skill, not a skill
            mentions.setdefault(name, set()).add(who)
            if re.search(MARKED_RE.format(name=re.escape(name)), text):
                marked.add(name)
    for name, path in local.items():  # a project-local skill is used by the project that holds it, named or not
        mentions.setdefault(name, set()).add(owner(path / "SKILL.md", root, local))
    return mentions, local, marked, aliases


def resolve(names, local: dict[str, Path], root: Path):
    """Classify each name: project-local, shared (skills_stuff), installed only (~/.claude/skills) or missing, with its location and entry file."""
    shared = skill_dirs(SKILLS_ROOT, 4)
    installed = skill_dirs(INSTALLED_ROOT, 1)
    out = []
    for name in sorted(names):
        if name in local:
            out.append((name, "project-local", local[name].relative_to(root).as_posix() + "/", entry(local[name])))
        elif name in shared:
            out.append((name, "shared", shared[name].parent.relative_to(SKILLS_ROOT).as_posix() + "/", entry(shared[name])))
        elif name in installed:
            out.append((name, "installed", "~/.claude/skills/", entry(installed[name])))
        else:
            out.append((name, "missing", "", None))
    for name, path in local.items():  # project-local skills nobody names in a governance file still belong on the list
        if name not in names:
            out.append((name, "project-local", path.relative_to(root).as_posix() + "/", entry(path)))
    return out


def fit(text: str, width: int) -> str:
    """Cut text to width at a word boundary and mark the cut with an ellipsis; text that fits is returned unchanged."""
    if len(text) <= width:
        return text
    cut = text[: width - 1].rsplit(" ", 1)[0].rstrip(",;:.(")
    return cut + "…"


def table(header, rows, flex: int) -> str:
    """Markdown table no wider than MAX_WIDTH; column `flex` is shortened to fit."""
    rows = [list(r) for r in rows]
    w = [max(len(str(r[i])) for r in [header] + rows) for i in range(len(header))]
    total = sum(w) + 3 * len(w) + 1
    if total > MAX_WIDTH:
        w[flex] = max(MIN_FLEX, w[flex] - (total - MAX_WIDTH))
        for r in rows:
            r[flex] = fit(r[flex], w[flex])
        w = [max(len(str(r[i])) for r in [header] + rows) for i in range(len(header))]
    line = lambda r: "| " + " | ".join(str(c).ljust(w[i]) for i, c in enumerate(r)) + " |"
    return "\n".join([line(header), "| " + " | ".join("-" * x for x in w) + " |"] + [line(r) for r in rows]) + "\n"


def render(root: Path, title: str, resolved, mentions, today: str) -> str:
    """The full skills.md text: front matter, rules, one table per kind of skill (each kept under MAX_WIDTH), and a maintenance section."""
    def used(n: str) -> str:
        """The projects that use skill n, joined with commas and summarised as `+N more` past USED_WIDTH."""
        names = sorted(mentions.get(n, set()))
        shown: list[str] = []
        for i, x in enumerate(names):
            rest = len(names) - i - 1
            if len(", ".join(shown + [x])) + (len(f", +{rest} more") if rest else 0) > USED_WIDTH:
                return ", ".join(shown) + f", +{len(names) - len(shown)} more"
            shown.append(x)
        return ", ".join(shown) or "(not named in a governance file)"
    desc = lambda md: fit(description(md), DESC_WIDTH)
    groups = {k: [r for r in resolved if r[1] == k] for k in ("shared", "project-local", "installed", "missing")}
    parts = [f"""---
Title: {title}
Category: misc-governance-guide
Status: current
Authority: local-supplement
Scope: Skills used by the projects under {root}
Source of truth: [skills.md]({root}/skills.md)
Synced from: [skills.md](/Volumes/Data/_ai/governance/skills.md)
Last reviewed: {today}
Summary: Which skills to invoke for work under this folder, where each lives, and which projects use it. Points at the skills; never copies them.
---

# skills.md

The list of skills used by the projects in this folder. Each row points at the skill; the skill's own `SKILL.md` holds the content. Project `AGENTS.md`
files keep their own invoke rules and may link here instead of repeating this list.

## Rules

- Invoke the matching skill **before** answering, planning or editing in its area; do not rediscover what a skill already records.
- Facts a skill owns go back into that skill in the same session; project docs cite the skill rather than restate it.
- Shared skills are authored in `skills_stuff`, project-local skills in their project folder. Never edit an installed copy under `~/.claude`, `~/.codex` or a
  plugin cache.
"""]
    if groups["shared"]:
        parts.append(f"## Shared skills\n\nCanonical root `{SKILLS_ROOT}/`; the **Location** column is the folder under it.\n\n")
        parts.append(table(("Skill", "Location", "Use for", "Used by"),
                           [(f"`{n}`", f"`{loc}`", desc(md), used(n)) for n, _, loc, md in groups["shared"]], 2) + "\n")
    if groups["project-local"]:
        parts.append("## Project-local skills\n\nThese live inside their project, at the path shown relative to this folder.\n\n")
        parts.append(table(("Skill", "Path", "Use for", "Used by"),
                           [(f"`{n}`", f"`{loc}`", desc(md), used(n)) for n, _, loc, md in groups["project-local"]], 2) + "\n")
    if groups["installed"]:
        parts.append("## Installed only\n\nFound under `~/.claude/skills` with no canonical source in `skills_stuff`; find or restore the source.\n\n")
        parts.append(table(("Skill", "Use for", "Used by"),
                           [(f"`{n}`", desc(md), used(n)) for n, _, _, md in groups["installed"]], 1) + "\n")
    if groups["missing"]:
        parts.append("## Referenced but not found\n\nNamed in a governance file, but no skill by that name exists. Restore it or remove the reference.\n\n")
        parts.append(table(("Skill", "Named by"), [(f"`{n}`", used(n)) for n, *_ in groups["missing"]], 1) + "\n")
    parts.append(f"""## Maintaining this list

- Add a row when a project starts invoking a skill; remove it when no project uses it. Update **Used by** in the same change as the project's `AGENTS.md`.
- Generated {today} by skill-ai-it `scripts/skills_registry.py`, then edited by hand. To spot drift:

  ```bash
  just -f {SKILLS_ROOT}/specialists/project/skill-ai-it/justfile skills_registry {root}
  ```
""")
    return "".join(parts)


def listed(skills_md: Path) -> set[str]:
    """Skill names in the first column of the existing file's tables."""
    names = set()
    for line in skills_md.read_text(errors="replace").splitlines():
        m = re.match(r"^\|\s*`(skill-[a-z0-9-]+)`", line)
        if m:
            names.add(m.group(1))
    return names


def main() -> int:
    """Parse arguments and run the chosen mode: --check (default; exit 1 on drift), --print, or --write (refuses to replace an existing
    skills.md without --force, and then keeps a timestamped backup).
    """
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project-root", required=True, type=Path, help="folder whose child projects are scanned; skills.md lives here")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="compare the existing skills.md with the scan (default)")
    mode.add_argument("--print", action="store_true", help="print the generated skills.md")
    mode.add_argument("--write", action="store_true", help="write skills.md")
    ap.add_argument("--force", action="store_true", help="with --write, replace an existing skills.md after backing it up")
    ap.add_argument("--also", type=Path, action="append", default=[], help="extra governance file outside the root, e.g. a repo that lives elsewhere")
    ap.add_argument("--ignore", action="append", default=[], help="skill-like name to drop (repeatable)")
    ap.add_argument("--keep", action="append", default=[], help="unresolved name to list anyway, under Referenced but not found (repeatable)")
    ap.add_argument("--title", help="front matter Title (default: '<Folder> Skills')")
    a = ap.parse_args()

    root = a.project_root.resolve()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    mentions, local, marked, aliases = scan(root, [p.absolute() for p in a.also], DEFAULT_IGNORE | set(a.ignore))
    keep = set(a.keep)
    everything = resolve(set(mentions), local, root)
    # unmarked: resolves to nothing and is only ever named in plain prose. It may be a real reference ("see skill-malik-ai Content Routing") or
    # a hyphenated phrase ("the skill-package rules"); a script cannot tell, so it is reported for a human and listed only with --keep.
    unmarked = sorted(r[0] for r in everything if r[1] == "missing" and r[0] not in aliases and r[0] not in marked and r[0] not in keep)
    resolved = [r for r in everything if not (r[1] == "missing" and r[0] not in keep and (r[0] in aliases or r[0] not in marked))]
    target = root / "skills.md"

    if a.print or a.write:
        text = render(root, a.title or f"{root.name.capitalize()} Skills", resolved, mentions, dt.date.today().isoformat())
        if a.print:
            sys.stdout.write(text)
            return 0
        if target.exists():
            if not a.force:
                print(f"{target} exists; use --check to compare, --print to see the generated version, or --force to replace it (a backup is kept)", file=sys.stderr)
                return 1
            backup = target.with_name(f"skills.md.bak-{dt.datetime.now():%Y%m%d_%H%M}")
            shutil.copy2(target, backup)
            print(f"backup: {backup}")
        target.write_text(text)
        print(f"wrote {target}: {len(resolved)} skills")
        if unmarked:
            print("named only in plain prose, not listed (add with --keep if real): " + ", ".join(unmarked))
        return 0

    found = {n for n, *_ in resolved}
    for n, kind, loc, _ in resolved:
        print(f"{kind:13} {n:34} {loc or '-':28} used by: {', '.join(sorted(mentions.get(n, set()))) or '-'}")
    if unmarked:
        print("\nnamed only in plain prose, not counted (check by hand; --keep NAME to list): " + ", ".join(unmarked))
    if not target.exists():
        print(f"\nno {target}; run with --write to create it")
        return 1
    have = listed(target)
    added, dropped = sorted(found - have), sorted(have - found)
    if added:
        print("\nfound by the scan but not in skills.md: " + ", ".join(added))
    if dropped:
        print("in skills.md but no longer found by the scan: " + ", ".join(dropped))
    if not added and not dropped:
        print(f"\nskills.md lists all {len(found)} skills the scan found")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
