#!/usr/bin/env python3
"""Step 4 stale-reference sweep: find old values, and classify every hit so history is excluded by rule, not by eye.

WHY THIS EXISTS
---------------
Step 4 used to be a raw `grep -rn OLD . | grep -v archive/`. It excluded only `archive/`, so every run the agent filtered
CHANGELOG entries, dated session logs and dated findings out by eye, and a count of "hits" said nothing about how many
were live. On 2026-09-27 ("seven sites" -> "nine sites") the grep also never looked inside skill-smc, the sibling skill
package that restated the old count in five files, because it lives in another repo.

So every hit lands in exactly one class, counted separately:

  active          a live statement of the old value. Fix it. The only class that fails the run (exit 1).
  history-path    CHANGELOG*, archive/, .remember/, snapshots, source-captures, backups: history by location
  history-dated   under a dated heading (`## 2026-09-20 session`), on a line that starts with a date, or on a line
                  carrying an as-at / historical marker: history by marker
  history-superseded  a document carrying a supersession note near its top (Step 3 rule 7): its old figures are
                  the record of what it said, and the note tells the reader so
  generated       .ai-context/, graphify-out/, repomix output: regenerate, never edit

`--also PATH` sweeps another root with the same rules: each sibling skill or repo that restates this project's facts.

The dated-section rule matches skill-staleness-audit's claim_scan.py (2026-09-27), so the two skills agree on what
counts as history.

Usage:
    stale_refs.py --old "seven sites" [--old "7 sites" ...] [--root .] [--also ../skill-smc ...] [-i] [--json]

Exit codes: 0 no active hits · 1 active hits · 2 usage error
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TEXT_EXT = {".md", ".rst", ".txt", ".py", ".sh", ".yaml", ".yml", ".json", ".toml", ".j2", ".cfg", ".ini"}
SKIP_PARTS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".pytest_cache", ".serena"}
HISTORY_PATH = ("CHANGELOG", "/archive/", "/.remember/", "-snapshots/", "/snapshots/", "source-captures/",
                "/backups/", "-update-backups/", ".staleness-audit")
GENERATED = ("/.ai-context/", "/graphify-out/", "repomix-output")
HISTORICAL_MARKERS = ("count:asat", "as-at", "as at", "historical", "<!-- asat", "superseded", "previously", " was ")
DATE_TOKEN = re.compile(r"\b(?:20\d\d-[01]\d-[0-3]\d|20\d\d[01]\d[0-3]\d(?:_\d{4})?)\b")
DATED_LINE = re.compile(r"^\s*(?:[-*+]\s+|\|\s*|\d+\.\s+)?(?:\*\*|`)?(?:20\d\d-[01]\d-[0-3]\d|20\d{6}(?:_\d{4})?)")
HEADING = re.compile(r"^(#{1,6})\s+(.*)")
# A supersession BANNER about this document ("> **Superseded 2026-09-27** by ...", "Status: superseded"), not prose that
# mentions superseding: "This plan supersedes the earlier one" is a live document, and its hits must stay active.
BANNER = re.compile(r"^\s*(?:>\s*)?(?:[*_]{1,2}|⚠️\s*)*\s*(?:status:\s*)?superseded\b", re.I)


def files_under(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*")
                  if p.is_file() and p.suffix.lower() in TEXT_EXT
                  and not any(part in SKIP_PARTS for part in p.relative_to(root).parts))


def sweep(root: Path, pattern: re.Pattern) -> list[dict]:
    hits = []
    for fp in files_under(root):
        rel = fp.relative_to(root).as_posix()
        slashed = "/" + rel
        try:
            text = fp.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if not pattern.search(text):
            continue
        is_md = fp.suffix.lower() in {".md", ".rst"}
        superseded = is_md and any(BANNER.match(ln) for ln in text.splitlines()[:20])
        heads: list[tuple[int, bool]] = []
        fence = False
        for i, line in enumerate(text.splitlines(), 1):
            if is_md and line.lstrip().startswith(("```", "~~~")):
                fence = not fence
            h = HEADING.match(line) if is_md and not fence else None
            if h:
                lvl = len(h.group(1))
                heads = [x for x in heads if x[0] < lvl] + [(lvl, bool(DATE_TOKEN.search(h.group(2))))]
            if not pattern.search(line):
                continue
            if any(g in slashed for g in GENERATED):
                cls = "generated"
            elif any(hp in slashed for hp in HISTORY_PATH):
                cls = "history-path"
            elif superseded:
                cls = "history-superseded"
            elif (is_md and (any(d for _, d in heads) or DATED_LINE.match(line))) or \
                    any(m in line.lower() for m in HISTORICAL_MARKERS):
                cls = "history-dated"
            else:
                cls = "active"
            hits.append({"root": str(root), "file": rel, "line": i, "class": cls, "text": line.strip()[:160]})
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--old", action="append", required=True, help="an old value, matched literally. Repeatable")
    ap.add_argument("--root", default=".")
    ap.add_argument("--also", action="append", default=[], help="another root to sweep (a sibling skill or repo)")
    ap.add_argument("-i", "--ignore-case", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    pattern = re.compile("|".join(re.escape(v) for v in a.old), re.I if a.ignore_case else 0)
    roots = [Path(a.root).resolve()] + [Path(x).resolve() for x in a.also]
    for r in roots:
        if not r.is_dir():
            sys.stderr.write(f"ERROR: {r} is not a directory\n")
            return 2
    hits = [h for r in roots for h in sweep(r, pattern)]
    classes = ("active", "history-path", "history-dated", "history-superseded", "generated")
    counts = {c: sum(h["class"] == c for h in hits) for c in classes}

    if a.json:
        print(json.dumps({"old": a.old, "roots": [str(r) for r in roots], "counts": counts, "hits": hits}, indent=2))
    else:
        print(f"Stale-reference sweep for {a.old} across {len(roots)} root(s)")
        for c, n in counts.items():
            print(f"  {c:18s} {n:5d}")
        active = [h for h in hits if h["class"] == "active"]
        if active:
            print("\nACTIVE — fix each, or mark it as history if it is a dated record:")
            for h in active:
                where = h["file"] if h["root"] == str(roots[0]) else f"{h['root']}/{h['file']}"
                print(f"  {where}:{h['line']}  {h['text']}")
        dated = [h for h in hits if h["class"] == "history-dated"]
        if dated:
            print(f"\n{len(dated)} history-dated hit(s) excluded by marker. Spot-check a few: a live sentence that merely"
                  " mentions a date is still live.")
    return 1 if counts["active"] else 0


if __name__ == "__main__":
    sys.exit(main())
