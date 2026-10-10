#!/usr/bin/env python3
"""Bring a project's governed files within budget, or say exactly what keeps one over. Stdlib plus git.

Why (operator, 2026-10-10): after the first rollout, records stayed over 200 lines / 25 KB and the work to find out why (a size table per
section, then a hand-written script) was done by hand each time. This plans and, with `--apply`, runs the whole sequence with the skill's tools:
1. Measure every file loaded whole (CHANGELOG.md, SCRATCHPAD.md, AGENTS.md, CLAUDE.md, AI_NAVIGATION.md) against its budget.
2. For an over-budget SCRATCHPAD: `normalise_records.py` (headings so dated paragraphs rotate), then for both records `rotate_records.py`.
3. Still over: move whole sections that are not working state (anything but Contents, Current state, Open items, Next actions, Recent decisions,
   Session history, Memory pointers), largest first, verbatim to `docs/<record>-reference-<stamp>.md` with `move_sections.py`, until it fits.
4. Audit with `audit_rotations.py` (nothing lost, nothing split), then run the project's `just check`.
5. Report each file that is still over budget, with the section that holds it. AGENTS.md, CLAUDE.md, AI_NAVIGATION.md and SKILL.md are only
   reported, with suggested `move-sections` commands for reference-like sections: what is a rule needs a reader.

Usage:
    python scripts/budget_plan.py --project-root .            # plan
    python scripts/budget_plan.py --project-root . --apply    # do it
Exit: 0 when every file fits (or the plan is printed), 1 when a file is still over budget after --apply or a step failed.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("rotate_records", HERE / "rotate_records.py")
rr = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("rotate_records", rr)
_spec.loader.exec_module(rr)

BUDGET = (200, 25 * 1024)
MAX_MOVES = 8
RECORDS = ("SCRATCHPAD.md", "CHANGELOG.md")
REPORT_ONLY = ("AGENTS.md", "CLAUDE.md", "AI_NAVIGATION.md", "SKILL.md")
re_check = re.compile(r"(?m)^check\b")
WORKING = re.compile(r"^## (Contents|Current state|Open items|Next actions|Recent decisions|Session history|Memory pointers|Reference loaded on need|Reference moved out|Key anchors and memory pointers)", re.I)


def size(path: pathlib.Path) -> tuple[int, int]:
    """Lines and bytes of a file.

    Args:
        path: the file.

    Returns:
        (lines, bytes).
    """
    data = path.read_bytes()
    return data.count(b"\n"), len(data)


def over(lines_bytes: tuple[int, int]) -> bool:
    """Whether a size is over the budget.

    Args:
        lines_bytes: (lines, bytes).

    Returns:
        True when either is over.
    """
    return lines_bytes[0] > BUDGET[0] or lines_bytes[1] > BUDGET[1]


def sections(text: str) -> list[tuple[str, int]]:
    """Level-2 sections and their line counts, outside fenced code.

    Args:
        text: the file's text.

    Returns:
        [(heading line, lines)] in file order.
    """
    out: list[list] = []
    fence = False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            fence = not fence
        if not fence and line.startswith("## "):
            out.append([line, 0])
        if out:
            out[-1][1] += 1
    return [(h, n) for h, n in out]


def run(args: list[str]) -> tuple[int, str]:
    """Run one of this skill's scripts.

    Args:
        args: the script name and its arguments.

    Returns:
        (exit status, combined output).
    """
    r = subprocess.run([sys.executable, str(HERE / args[0]), *args[1:]], capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def movable(text: str) -> list[tuple[str, int]]:
    """Sections that are not working state, largest first.

    Args:
        text: the record's text.

    Returns:
        [(heading text without '## ', lines)].
    """
    return sorted(((h[3:], n) for h, n in sections(text) if not WORKING.match(h)), key=lambda x: -x[1])


def index_line(root: pathlib.Path, dest: str, summary: str) -> None:
    """Add a moved-out reference file to its folder's `readme.md` index when the folder has one and lacks the line.

    Args:
        root: the project root.
        dest: the file, project-relative.
        summary: the index line's description.

    Returns:
        None.
    """
    index = (root / dest).parent / "readme.md"
    name = pathlib.Path(dest).name
    if index.is_file() and f"]({name})" not in index.read_text():
        index.write_text(index.read_text().rstrip("\n") + f"\n- [{name}]({name}) {summary}\n")


RULE_WORDS = re.compile(r"\b(must|never|always|do not|don't|only|before|required?|forbidden|stop)\b", re.I)


def reference_like(text: str, min_lines: int = 20) -> list[tuple[str, int]]:
    """Sections of an instruction file that read as reference rather than rules: long, and mostly tables, code or plain facts.

    A heuristic for a reader to confirm, never applied automatically: what is a rule needs judgment (operator, 2026-10-10).

    Args:
        text: the file's text.
        min_lines: smallest section worth suggesting.

    Returns:
        [(heading text without '## ', lines)], largest first.
    """
    out = []
    managed = re.search(r"<!-- BEGIN MANAGED: skill-ai-it:\w+ -->.*?<!-- END MANAGED: skill-ai-it:\w+ -->", text, re.S)
    for head, n in sections(text):
        if managed and managed.start() < text.find(head) < managed.end():
            continue  # the managed block is refreshed by upgrade_navigation_control_layer.py, never moved
        if n < min_lines or WORKING.match(head) or head.startswith("## AI navigation"):
            continue
        start = text.index(head)
        nxt = text.find("\n## ", start + 1)
        body = [l for l in text[start:nxt if nxt != -1 else len(text)].split("\n")[1:] if l.strip()]
        ruled = sum(1 for l in body if RULE_WORDS.search(l))
        if body and ruled / len(body) < 0.25:
            out.append((head[3:], n))
    return sorted(out, key=lambda x: -x[1])


def handle_record(root: pathlib.Path, name: str, apply: bool, stamp: str) -> tuple[bool, list[str]]:
    """Plan or apply normalise, rotate and section moves for one record.

    Args:
        root: the project root.
        name: `SCRATCHPAD.md` or `CHANGELOG.md`.
        apply: run the steps.
        stamp: `YYYYMMDD_hhmm` for a reference file's name.

    Returns:
        (still over budget, report lines).
    """
    path = root / name
    lines = [f"{name}: {size(path)[0]} lines, {size(path)[1] // 1024} KB (budget {BUDGET[0]} lines, 25 KB)"]
    if not over(size(path)):
        return False, lines + ["  within budget"]
    steps = ([["normalise_records.py", "--project-root", str(root), name]] if name == "SCRATCHPAD.md" else []) + \
            [["rotate_records.py", "--project-root", str(root), name]]
    for step in steps:
        rc, out = run(step + (["--apply"] if apply else []))
        lines.append(f"  {step[0]}: " + (out.splitlines()[0] if out else f"exit {rc}"))
        if rc != 0:
            return True, lines + [f"  step failed: {out[-300:]}"]
    if not apply:
        cands = movable(path.read_text())
        lines.append("  then, if still over: move sections out (largest first): " + (", ".join(f"{h} ({n})" for h, n in cands[:6]) or "none"))
        return over(size(path)), lines
    moved = 0
    while over(size(path)) and moved < MAX_MOVES:
        cands = movable(path.read_text())
        if not cands:
            break
        before = size(path)
        head, n = cands[0]
        dest = f"docs/{name[:-3].lower()}-reference-{moved + 1}-{stamp}.md"
        rc, out = run(["move_sections.py", "--project-root", str(root), "--source", name, "--dest", dest,
                       "--title", f"{root.name} {name[:-3].lower()} reference {moved + 1}",
                       "--summary", f"A section moved verbatim from {name} to keep it within budget; durable reference, not working state.",
                       "--pointer", f"Reference moved out ({moved + 1})", "--apply", head])
        lines.append(f"  move_sections: {head!r} ({n} lines) -> {dest}" + ("" if rc == 0 else f" REFUSED: {out[-200:]}"))
        if rc != 0:
            break
        index_line(root, dest, f"Section `{head}` moved verbatim from {name} to keep it within budget.")
        moved += 1
        if size(path)[0] >= before[0]:
            # a move that does not shrink the file is a pointer moving itself: stop (jdm, 2026-10-10: ~10,000 files before it was killed)
            lines.append("  stopped: the last move did not shrink the file")
            break
    still = over(size(path))
    after = size(path)
    lines.append(f"  now {after[0]} lines, {after[1] // 1024} KB")
    if still:
        biggest = max(sections(path.read_text()), key=lambda x: x[1], default=("", 0))
        lines.append(f"  STILL OVER: held by working-state section {biggest[0]!r} ({biggest[1]} lines): undated prose a reader must date, split or close")
    return still, lines


def main(argv: list[str] | None = None) -> int:
    """Plan or apply the budget sequence for one project.

    Args:
        argv: command-line arguments (default: sys.argv).

    Returns:
        The exit status.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.project_root).resolve()
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M")
    links = [n for n in RECORDS + REPORT_ONLY if (root / n).is_symlink()]
    if links:
        print(f"refused: {', '.join(links)} are symlinks (into {(root / links[0]).resolve().parent}); run there with --project-root")
        return 1
    unfinished = []
    for name in RECORDS:
        if (root / name).is_file():
            still, report = handle_record(root, name, args.apply, stamp)
            print("\n".join(report))
            if still:
                unfinished.append(name)
    for name in REPORT_ONLY:
        p = root / name
        if p.is_file() and over(size(p)):
            top = sorted(sections(p.read_text()), key=lambda x: -x[1])[:4]
            print(f"{name}: {size(p)[0]} lines, {size(p)[1] // 1024} KB: OVER; largest sections: " + ", ".join(f"{h[3:]} ({n})" for h, n in top)
                  + ". Rules stay; move reference with move_sections.py.")
            text = p.read_text()
            if ("skill-ai-it:navigation" in text and "skill-ai-it-version: 2026-10-10-compact" not in text
                    and "skill-ai-it:manual" not in text):  # a project-owned block is never replaced (jdm, 2026-10-10)
                print("  first: python <skill-ai-it>/scripts/upgrade_navigation_control_layer.py --project-root . (the managed block is now compact)")
            for k, (head, n) in enumerate(reference_like(text)[:3], 1):
                slug = name[:-3].lower().replace("_", "-")
                print(f"  suggest (confirm it is reference, not rules): just move-sections --source {name} "
                      f"--dest docs/{slug}-reference-{k}-{stamp}.md --title \"{root.name} {name[:-3]} reference {k}\" "
                      f"--summary \"Reference moved verbatim from {name}\" \"{head}\"   # {n} lines")
            unfinished.append(name)
    if args.apply and (root / "docs" / "history" / "readme.md").exists():
        rc, out = run(["audit_rotations.py", str(root)])
        print("audit: " + (out.splitlines()[-1] if out else f"exit {rc}"))
        if rc != 0:
            return 1
    if args.apply and (root / "justfile").is_file() and re_check.search((root / "justfile").read_text()):
        # moved sections can carry a fact a project guard expects in the record (of-si's count claim, atar's constant surfaces, 2026-10-10)
        r = subprocess.run(["just", "check"], cwd=root, capture_output=True, text=True)
        print(f"project check: {'OK' if r.returncode == 0 else 'FAILED, update the guard or registry that names the moved text'}")
        if r.returncode != 0:
            return 1
    if unfinished:
        print(f"{'UNFINISHED' if args.apply else 'over budget'}: {', '.join(unfinished)}")
    return 1 if (args.apply and unfinished) else 0


if __name__ == "__main__":
    sys.exit(main())
