#!/usr/bin/env python3
"""Find project markdown that has gone stale by rule, as a ratchet that only tightens. Stdlib plus git.

Why (operator, 2026-10-10, adopting option B of the OKF adoption assessment): docs go stale because nothing triggers a review, superseded files stay
beside current ones, and a document is not told when what it describes has changed. Metadata alone does not fix that; a failing check and a list the
agent sees at session start do. Three rules, read from each file's front matter (the governance standard, `categories/naming-and-file-summary-guide.md`):

1. `review-due`: a living document (`Status: current`, `draft` or `proposed`, Category not point-in-time) whose review date has passed. The date is
   `Review by` when given, else `Last reviewed` plus the window for its kind (30 days by default). Point-in-time records (reports, reviews, audits,
   sources, evidence, captures) never expire: they describe a moment.
2. `superseded-in-place`: `Status: superseded ...` outside an `archive/` folder. A label does not keep a reader or a search away; the folder does.
3. `dependency-changed`: a file named under `Depends on` (comma-separated, project-relative) was committed after the document's `Last reviewed`.

Nothing is hand-kept: windows come from Category, the baseline (JSON, {finding-key: first-seen date}) is written by `--write-baseline`, and existing
findings are grandfathered so adoption never fails a project on day one. A new finding fails `--check`; a baseline entry whose finding is gone is
reported so it can be dropped with `--write-baseline`.

Usage:
    python scripts/doc_freshness.py --project-root /path/to/project               # list findings (session preflight; exit 0)
    python scripts/doc_freshness.py --project-root . --check                      # exit 1 on any finding not in the baseline
    python scripts/doc_freshness.py --project-root . --write-baseline             # adopt: record today's findings
    python scripts/doc_freshness.py --project-root . --window-days 45 --baseline scripts/doc-freshness-baseline.json
Exit: 0 clean (or list mode), 1 on new findings under --check, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import subprocess
import sys

DEFAULT_BASELINE = "scripts/doc-freshness-baseline.json"
DEFAULT_WINDOW_DAYS = 30
LIVING_STATUSES = ("current", "draft", "proposed")
POINT_IN_TIME = re.compile(r"report|review|audit|sources?\b|source-index|sources-index|evidence|capture|changelog|record|prompt|handoff", re.I)
SKIP_PARTS = ("/node_modules/", "/.git/", "/archive/", "-sources-", "/captures/", "/backups/", "/.venv/", "/vendor-sources/")
KEY = re.compile(r"^(Title|Category|Status|Last reviewed|Review by|Depends on):\s*(.*)$")
DATE = re.compile(r"(\d{4})-?(\d{2})-?(\d{2})")


def front_matter(text: str) -> dict[str, str]:
    """The governance front-matter keys this check reads, from the top of a markdown file.

    Accepts `---`-fenced YAML-style blocks and the bare `Key: value` header used by AGENTS.md files; a folded `>-` value is joined from its
    indented lines.

    Args:
        text: the file's content.

    Returns:
        Lower-cased key to value for Title, Category, Status, Last reviewed, Review by and Depends on; empty when none are found in the first 40 lines.
    """
    out: dict[str, str] = {}
    lines = text.splitlines()[:40]
    i = 0
    while i < len(lines):
        m = KEY.match(lines[i])
        if m:
            key, val = m.group(1).lower(), m.group(2).strip()
            if val in (">-", ">", "|"):
                parts = []
                while i + 1 < len(lines) and lines[i + 1].startswith((" ", "\t")):
                    i += 1
                    parts.append(lines[i].strip())
                val = " ".join(parts)
            out[key] = val
        i += 1
    return out


def parse_date(value: str) -> dt.date | None:
    """The first date in a front-matter value.

    Args:
        value: text such as `2026-10-10`, `20261010_1700` or `2026-10-10 (operator)`.

    Returns:
        The date, or None when the value holds no valid date.
    """
    m = DATE.search(value or "")
    if not m:
        return None
    try:
        return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def last_commit_date(root: pathlib.Path, rel: str) -> dt.date | None:
    """The date of the last commit touching a path.

    Args:
        root: the project root (inside a git repository).
        rel: the path relative to root.

    Returns:
        The committer date, or None when the path has no commit or git is unavailable.
    """
    try:
        out = subprocess.run(["git", "-C", str(root), "log", "-1", "--format=%cs", "--", rel], capture_output=True, text=True, check=False).stdout.strip()
    except OSError:
        return None
    return parse_date(out)


def markdown_files(root: pathlib.Path) -> list[pathlib.Path]:
    """The markdown files git tracks under root, minus folders that hold history or verbatim captures.

    Args:
        root: the project root.

    Returns:
        Sorted paths; falls back to a filesystem walk when root is not a git work tree.
    """
    res = subprocess.run(["git", "-C", str(root), "ls-files", "*.md"], capture_output=True, text=True, check=False)
    rels = res.stdout.split("\n") if res.returncode == 0 else [str(p.relative_to(root)) for p in root.rglob("*.md")]
    keep = [r for r in rels if r and not any(s in "/" + r for s in SKIP_PARTS)]
    return sorted(root / r for r in keep if (root / r).is_file())


def findings(root: pathlib.Path, today: dt.date, window_days: int) -> dict[str, str]:
    """Every finding under the three rules.

    Args:
        root: the project root.
        today: the date reviews are judged against.
        window_days: the review window for living documents without `Review by`.

    Returns:
        Finding key (`<rule>:<path>`, plus `:<dependency>` for rule 3) to a one-line explanation.
    """
    out: dict[str, str] = {}
    for path in markdown_files(root):
        rel = str(path.relative_to(root))
        fm = front_matter(path.read_text(errors="ignore"))
        status = fm.get("status", "").lower()
        if not status:
            continue
        reviewed = parse_date(fm.get("last reviewed", ""))
        if status.startswith("superseded") and "/archive/" not in "/" + rel:
            out[f"superseded-in-place:{rel}"] = f"{rel}: Status superseded but not under an archive/ folder"
        living = status.startswith(LIVING_STATUSES) and not POINT_IN_TIME.search(fm.get("category", ""))
        if living:
            due = parse_date(fm.get("review by", "")) or (reviewed + dt.timedelta(days=window_days) if reviewed else None)
            if due is None:
                out[f"review-due:{rel}"] = f"{rel}: living document with no Last reviewed or Review by date"
            elif due < today:
                out[f"review-due:{rel}"] = f"{rel}: review was due {due.isoformat()} (Last reviewed {fm.get('last reviewed', '-')})"
        for dep in [d.strip() for d in fm.get("depends on", "").split(",") if d.strip()]:
            changed = last_commit_date(root, dep)
            if not (root / dep).exists():
                out[f"dependency-changed:{rel}:{dep}"] = f"{rel}: Depends on {dep}, which no longer exists"
            elif changed and reviewed and changed > reviewed:
                out[f"dependency-changed:{rel}:{dep}"] = f"{rel}: {dep} changed {changed.isoformat()}, after Last reviewed {reviewed.isoformat()}"
    return out


def main(argv: list[str] | None = None) -> int:
    """Run the check from the command line.

    Args:
        argv: arguments without the program name; None reads sys.argv.

    Returns:
        The exit code: 0 clean or list mode, 1 new findings under --check, 2 bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--baseline", default=DEFAULT_BASELINE)
    ap.add_argument("--window-days", type=int, default=DEFAULT_WINDOW_DAYS)
    ap.add_argument("--today", help="YYYY-MM-DD; default the machine's date (tests)")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write-baseline", action="store_true")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.project_root).resolve()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    today = parse_date(args.today) if args.today else dt.date.today()
    found = findings(root, today, args.window_days)
    base_path = root / args.baseline
    baseline: dict[str, str] = json.loads(base_path.read_text()) if base_path.exists() else {}
    if args.write_baseline:
        kept = {k: baseline.get(k, today.isoformat()) for k in sorted(found)}
        base_path.parent.mkdir(parents=True, exist_ok=True)
        base_path.write_text(json.dumps(kept, indent=1) + "\n")
        print(f"baseline written: {len(kept)} finding(s) -> {args.baseline}")
        return 0
    new = {k: v for k, v in found.items() if k not in baseline}
    gone = [k for k in baseline if k not in found]
    if not args.check:
        print(f"doc freshness: {len(found)} finding(s), {len(new)} new since the baseline")
        for k in sorted(found):
            print(("  NEW " if k in new else "      ") + found[k])
        return 0
    for k in sorted(new):
        print(f"  ✗ doc-freshness: {found[k]}")
    if gone:
        print(f"  note: {len(gone)} baseline finding(s) resolved; drop them with --write-baseline")
    print(f"{'FAIL' if new else 'OK'} — doc freshness: {len(new)} new finding(s), {len(found) - len(new)} baselined")
    return 1 if new else 0


if __name__ == "__main__":
    sys.exit(main())
