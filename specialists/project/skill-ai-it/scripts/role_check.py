#!/usr/bin/env python3
"""Check that a project's root governance files keep to their roles, as a ratchet that only tightens. Stdlib only.

Why (operator, 2026-10-14: "ensure that all the definitions of the files ... are actually going to be defined for the projects in that way and it
will adhere to that"): the roles in skill-ai-it `references/governed-file-roles.md` were prose; a survey of the 13 governed projects that day found
every one outside them (no front matter on 12, no README quick start on 11, ROADMAP without a dated phase on 8 of 10). These rules are the part of
the role check a script can decide; the rest stays with the agent's audit (drift-audit section 14).

Rules (key `<rule>:<file>`):
1. `front-matter`: a root governance file (README, AGENTS, AI_NAVIGATION, ARCHITECTURE, CONVENTIONS, SETUP, ROADMAP, CHANGELOG, SCRATCHPAD) does
   not open with a `---` fenced block carrying Title and Summary. CLAUDE.md is exempt: its import line must stay first.
2. `claude-import`: CLAUDE.md's first line is not `@AGENTS.md`.
3. `readme-quick-start`: README.md has no quick start (a heading such as Quick start, Getting started, Setup, Usage) and no SETUP.md link.
4. `readme-history`: README.md has a history or status heading (History, Changelog, Progress, Status, Current state, Recent, a dated heading).
5. `roadmap-phase`: ROADMAP.md has no `## Current phase` section with a bold date (`**YYYY-MM-DD.**`).
6. `roadmap-done`: ROADMAP.md keeps done items past the 7-day window (`roadmap_trim.py` would move them), or narrative under `## Completed`.
7. `duplicate-section`: two root files carry the same `##`/`###` section (same title, bodies at least 80% alike); one fact has one home.

A baseline (`scripts/role-check-baseline.json`) records the findings on the day a project adopts the check; `--check` fails only on a finding
the baseline does not hold, so existing breaches shrink without blocking work and new ones fail. `adopt_governed_files.py` writes it.

Usage:
    python scripts/role_check.py --project-root P                    # list findings
    python scripts/role_check.py --project-root P --check            # exit 1 on a finding the baseline does not hold
    python scripts/role_check.py --project-root P --write-baseline   # record today's findings
Exit: 0 clean (or baselined), 1 new findings in --check mode, 2 bad arguments.
"""

from __future__ import annotations

import argparse
import datetime as dt
import difflib
import importlib.util
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent


def _load(name: str):
    """Import a sibling script as a module.

    Args:
        name: the script's file stem.

    Returns:
        The loaded module.
    """
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(name, mod)
    spec.loader.exec_module(mod)
    return mod


md_sections = _load("md_sections")
roadmap_trim = _load("roadmap_trim")

ROLE_FILES = ("README.md", "AGENTS.md", "AI_NAVIGATION.md", "ARCHITECTURE.md", "CONVENTIONS.md", "SETUP.md", "ROADMAP.md", "CHANGELOG.md",
              "SCRATCHPAD.md")
BASELINE = "scripts/role-check-baseline.json"
QUICK = re.compile(r"quick ?start|getting started|\bsetup\b|\bset up\b|\binstall|\busage\b|how to (run|use)|\brunning\b|\bbootstrap", re.I)
HISTORY = re.compile(r"\b(history|change ?log|progress|status|current state|recent|session|updates?)\b|20\d\d-[01]\d-[0-3]\d", re.I)
PHASE_DATE = re.compile(r"\*\*20\d\d-[01]\d-[0-3]\d\.?\*\*")
DONE_POINTER = re.compile(r"^Done items move to", re.I)
SKIP_DUP = {"contents", "table of contents"}
KEEP_DAYS = 7


def has_front_matter(text: str) -> bool:
    """Whether the text opens with a fenced block that names a Title and a Summary.

    Args:
        text: the file.

    Returns:
        True when the block is there with both keys.
    """
    lines = text.splitlines()
    end = md_sections.front_matter_end(lines)
    head = "\n".join(lines[:end])
    return end > 0 and bool(re.search(r"(?m)^Title:", head)) and bool(re.search(r"(?m)^Summary:", head))


def sections(text: str) -> list[tuple[int, str, str]]:
    """The file's level-2 and level-3 sections with their own bodies (children excluded).

    Args:
        text: the file.

    Returns:
        (level, title, body) per section, in document order.
    """
    lines = text.splitlines()
    return [(s.level, s.title.strip(), "\n".join(lines[s.start:s.body_end])) for s in md_sections.scan(lines) if s.level in (2, 3)]


def norm(body: str) -> str:
    """A section body with markup and whitespace folded, for comparison.

    Args:
        body: the text.

    Returns:
        The folded text.
    """
    return re.sub(r"\s+", " ", re.sub(r"[`*_>|#-]", " ", body)).strip().lower()


def readme_findings(text: str) -> dict[str, str]:
    """README rules: a quick start or SETUP.md link, and no history or status heading.

    Args:
        text: README.md.

    Returns:
        Findings keyed by rule.
    """
    out = {}
    heads = [t for _, t, _ in sections(text)]
    if not any(QUICK.search(h) for h in heads) and "SETUP.md" not in text:
        out["readme-quick-start"] = "no quick start heading and no SETUP.md link"
    hist = [h for h in heads if HISTORY.search(h)]
    if hist:
        out["readme-history"] = "history or status heading(s): " + ", ".join(repr(h) for h in hist[:3]) + " (belongs in CHANGELOG, ROADMAP or SCRATCHPAD)"
    return out


def roadmap_findings(text: str, today: dt.date) -> dict[str, str]:
    """ROADMAP rules: a dated current phase, and no done items or narrative left past the window.

    Args:
        text: ROADMAP.md.
        today: the date the 7-day window counts back from.

    Returns:
        Findings keyed by rule.
    """
    out = {}
    secs = sections(text)
    phase = [b for lvl, t, b in secs if lvl == 2 and t.lower() == "current phase"]
    if not phase or not PHASE_DATE.search(phase[0]):
        out["roadmap-phase"] = "no `## Current phase` with a bold date (`**YYYY-MM-DD.**`)"
    _, moved = roadmap_trim.split(text, today - dt.timedelta(days=KEEP_DAYS))
    narrative, under_done = [], False
    for lvl, title, body in secs:
        if lvl == 2:
            under_done = title.lower().startswith(("completed", "done"))
        if under_done:
            narrative += [title] if lvl == 3 else []
            # paragraphs: the pointer paragraph may wrap (UNC, 2026-10-14); items and their indented continuations are roadmap-trim's business
            for para in re.split(r"\n\s*\n", "\n".join(body.splitlines()[1:])):
                if para.strip() and not DONE_POINTER.match(para.strip()):
                    narrative += [ln for ln in para.splitlines() if ln.strip() and not ln.startswith(("- ", "  "))]
    if moved or narrative:
        out["roadmap-done"] = (f"{len(moved)} done item(s) older than {KEEP_DAYS} days (`just rotate --apply`)" if moved else "") + \
                              ("; " if moved and narrative else "") + (f"{len(narrative)} line(s) of narrative under Completed" if narrative else "")
    return out


def duplicate_findings(texts: dict[str, str]) -> dict[str, str]:
    """Sections two root files both carry.

    Args:
        texts: root file name to its text.

    Returns:
        Findings keyed `duplicate-section:<a>+<b>:<title>`.
    """
    out = {}
    seen: list[tuple[str, str, str]] = []
    for name, text in texts.items():
        for _, title, body in sections(text):
            key, folded = title.lower(), norm("\n".join(body.splitlines()[1:]))
            if key in SKIP_DUP or len(folded) < 120:
                continue
            for other, otitle, obody in seen:
                if other != name and otitle == key and difflib.SequenceMatcher(None, folded, obody).ratio() >= 0.8:
                    out[f"duplicate-section:{other}+{name}:{title}"] = f"`{title}` is in both {other} and {name}; keep it in one, link from the other"
            seen.append((name, key, folded))
    return out


def findings(root: pathlib.Path, today: dt.date) -> dict[str, str]:
    """Every role finding for one project.

    Args:
        root: the project root.
        today: the date for the ROADMAP window.

    Returns:
        Message per finding key.
    """
    out: dict[str, str] = {}
    texts = {n: (root / n).read_text(encoding="utf-8") for n in ROLE_FILES if (root / n).is_file()}
    for name, text in texts.items():
        if not has_front_matter(text):
            out[f"front-matter:{name}"] = f"{name}: no `---` front matter with Title and Summary"
    claude = root / "CLAUDE.md"
    if claude.is_file():
        first = next((ln.strip() for ln in claude.read_text(encoding="utf-8").splitlines() if ln.strip()), "")
        if first != "@AGENTS.md":
            out["claude-import:CLAUDE.md"] = f"CLAUDE.md: first line is {first[:60]!r}, not `@AGENTS.md`"
    if "README.md" in texts:
        out |= {f"{k}:README.md": f"README.md: {v}" for k, v in readme_findings(texts["README.md"]).items()}
    if "ROADMAP.md" in texts:
        out |= {f"{k}:ROADMAP.md": f"ROADMAP.md: {v}" for k, v in roadmap_findings(texts["ROADMAP.md"], today).items()}
    out |= duplicate_findings(texts)
    return out


def main(argv: list[str] | None = None) -> int:
    """List, check or baseline the role findings of one project.

    Args:
        argv: arguments without the program name; None reads sys.argv.

    Returns:
        0 clean or baselined, 1 new findings under --check, 2 bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--project-root", default=".")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write-baseline", action="store_true")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.project_root).resolve()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    found = findings(root, dt.date.today())
    base_path = root / BASELINE
    if args.write_baseline:
        base_path.parent.mkdir(parents=True, exist_ok=True)
        base_path.write_text(json.dumps(dict(sorted(found.items())), indent=1) + "\n", encoding="utf-8")
        print(f"role baseline written: {len(found)} finding(s) -> {BASELINE}")
        return 0
    baseline = json.loads(base_path.read_text(encoding="utf-8")) if base_path.is_file() else {}
    new = {k: v for k, v in found.items() if k not in baseline}
    if not args.check:
        for k, v in sorted(found.items()):
            print(f"{'  ' if k in baseline else '✗ '}{v}{'  (baselined)' if k in baseline else ''}")
        print(f"{len(found)} role finding(s), {len(new)} not in the baseline; roles: skill-ai-it references/governed-file-roles.md")
        return 0
    for v in new.values():
        print(f"  ✗ role: {v}")
    gone = [k for k in baseline if k not in found]
    if gone:
        print(f"  note: {len(gone)} baselined role finding(s) resolved; drop them with --write-baseline")
    print(f"{'FAIL' if new else 'OK'} — file roles: {len(new)} new finding(s), {len(found) - len(new)} baselined")
    return 1 if new else 0


if __name__ == "__main__":
    sys.exit(main())
