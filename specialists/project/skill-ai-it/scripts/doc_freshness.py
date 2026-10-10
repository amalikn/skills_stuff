#!/usr/bin/env python3
"""Find project files that have gone stale, grown past their budget or lack a header, as a ratchet that only tightens. Stdlib plus git.

Why (operator, 2026-10-10, option B of the OKF adoption assessment, then "information overload ... managed properly"): files go stale because
nothing triggers a review, superseded files stay beside current ones, a document is not told when what it describes changed, files an agent
loads whole keep growing, and a file without a header must be opened to be judged. Five rules, read through the one header parser
(`file_headers.py`, the governance "File headers" standard):

1. `review-due`: a living markdown document (`Status: current`, `draft` or `proposed`, Category not point-in-time) past `Review by`, else
   `Last reviewed` + 30 days. Reports, reviews, audits, sources and evidence describe a moment and never expire.
2. `superseded-in-place`: `Status: superseded ...` outside an `archive/` folder (move it with `move_doc.py`).
3. `dependency-changed`: a file named under `Depends on` was committed after the document's `Last reviewed`.
4. `over-budget`: a file an agent loads whole (AGENTS.md, CLAUDE.md, AI_NAVIGATION.md, SCRATCHPAD.md, CHANGELOG.md, SKILL.md, MEMORY.md, or
   any file with a `Budget` key) over 200 lines or 25 KB, one standard for every agent (operator, 2026-10-10). Rotate records with
   `rotate_records.py`; trim the others.
5. `no-header`: a tracked markdown, Python, YAML, shell, justfile or TOML file with no summary in its native header form (JSON and
   JSON-in-YAML are data and need none).
6. `checker-size`: a single-file `scripts/check_governance.py` over 800 lines (split it into the govcheck package); a ratchet like rule 4.

The baseline (JSON, {finding-key: value}) grandfathers what exists at adoption: rules 1-3 and 5 fail only on a new finding; rule 4 records
the size and fails only when the file grows past it, so an over-budget file can shrink but never grow. `--write-baseline` records today's
state; a resolved finding is reported so it can be dropped.

Usage:
    python scripts/doc_freshness.py --project-root /path/to/project               # list findings (session preflight; exit 0)
    python scripts/doc_freshness.py --project-root . --check                      # exit 1 on a new finding or a grown file
    python scripts/doc_freshness.py --project-root . --write-baseline             # adopt: record today's findings and sizes
Exit: 0 clean (or list mode), 1 on new findings under --check, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import pathlib
import re
import subprocess
import sys

_spec = importlib.util.spec_from_file_location("file_headers", pathlib.Path(__file__).resolve().parent / "file_headers.py")
file_headers = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(file_headers)

DEFAULT_BASELINE = "scripts/doc-freshness-baseline.json"
DEFAULT_WINDOW_DAYS = 30
LIVING_STATUSES = ("current", "draft", "proposed")
POINT_IN_TIME = re.compile(r"report|review|audit|sources?\b|source-index|sources-index|evidence|capture|changelog|record|prompt|handoff|archive", re.I)
BUDGET_NAMES = {"AGENTS.md", "CLAUDE.md", "AI_NAVIGATION.md", "SCRATCHPAD.md", "CHANGELOG.md", "SKILL.md", "MEMORY.md"}
DEFAULT_BUDGET = (200, 25 * 1024)
CHECKER_SPLIT_LINES = 800
DATE = re.compile(r"(\d{4})-?(\d{2})-?(\d{2})")


def parse_date(value: str) -> dt.date | None:
    """The first date in a header value.

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


def parse_budget(value: str) -> tuple[int, int]:
    """A `Budget` value such as `200 lines, 25 KB`.

    Args:
        value: the header value; empty for the default.

    Returns:
        (maximum lines, maximum bytes); a part not given keeps the default.
    """
    lines, size = DEFAULT_BUDGET
    m = re.search(r"(\d+)\s*lines", value or "")
    if m:
        lines = int(m.group(1))
    m = re.search(r"(\d+)\s*KB", value or "", re.I)
    if m:
        size = int(m.group(1)) * 1024
    return lines, size


def last_commit_date(root: pathlib.Path, rel: str) -> dt.date | None:
    """The date of the last commit touching a path.

    Args:
        root: the project root (inside a git repository).
        rel: the path relative to root.

    Returns:
        The committer date, or None when the path has no commit or git is unavailable.
    """
    try:
        out = subprocess.run(["git", "-C", str(root), "log", "-1", "--format=%cs", "--", rel], capture_output=True, text=True, check=False).stdout
    except OSError:
        return None
    return parse_date(out.strip())


def findings(root: pathlib.Path, today: dt.date, window_days: int) -> dict[str, str]:
    """Every finding under the five rules.

    Args:
        root: the project root.
        today: the date reviews are judged against.
        window_days: the review window for living documents without `Review by`.

    Returns:
        Finding key (`<rule>:<path>`, plus `:<dependency>` for rule 3) to a one-line explanation; for rule 4 the explanation starts with
        `lines=<n> bytes=<n>`, which the ratchet compares.
    """
    out: dict[str, str] = {}
    for path in file_headers.tracked(root, []):
        rel = str(path.relative_to(root))
        head = file_headers.read_header(path)
        if path.name not in file_headers.INDEX_NAMES and not head.get("summary") and not head.get("title"):
            out[f"no-header:{rel}"] = f"{rel}: no summary in its header (see the governance File headers standard)"
        if path.name in BUDGET_NAMES or "budget" in head:
            text = path.read_bytes()
            nlines, nbytes = text.count(b"\n"), len(text)
            max_lines, max_bytes = parse_budget(head.get("budget", ""))
            if nlines > max_lines or nbytes > max_bytes:
                out[f"over-budget:{rel}"] = f"lines={nlines} bytes={nbytes} {rel}: over its budget of {max_lines} lines, {max_bytes // 1024} KB"
        if path.suffix != ".md":
            continue
        status = head.get("status", "").lower()
        if not status:
            continue
        reviewed = parse_date(head.get("last reviewed", ""))
        if status.startswith("superseded") and "/archive/" not in "/" + rel:
            out[f"superseded-in-place:{rel}"] = f"{rel}: Status superseded but not under an archive/ folder"
        record = head.get("kind", "") in ("log", "state")  # running records are rotated, not reviewed
        if status.startswith(LIVING_STATUSES) and not record and not POINT_IN_TIME.search(head.get("category", "")):
            due = parse_date(head.get("review by", "")) or (reviewed + dt.timedelta(days=window_days) if reviewed else None)
            if due is None:
                out[f"review-due:{rel}"] = f"{rel}: living document with no Last reviewed or Review by date"
            elif due < today:
                out[f"review-due:{rel}"] = f"{rel}: review was due {due.isoformat()} (Last reviewed {head.get('last reviewed', '-')})"
        for dep in [d.strip() for d in head.get("depends on", "").split(",") if d.strip()]:
            changed = last_commit_date(root, dep)
            if not (root / dep).exists():
                out[f"dependency-changed:{rel}:{dep}"] = f"{rel}: Depends on {dep}, which no longer exists"
            elif changed and reviewed and changed > reviewed:
                out[f"dependency-changed:{rel}:{dep}"] = f"{rel}: {dep} changed {changed.isoformat()}, after Last reviewed {reviewed.isoformat()}"
    checker = root / "scripts" / "check_governance.py"
    if checker.is_file() and not (root / "scripts" / "govcheck").is_dir():
        n = checker.read_text(encoding="utf-8", errors="ignore").count("\n")
        if n > CHECKER_SPLIT_LINES:
            # Rule 6: a single-file checker past the split threshold (skill-ai-it patterns/governance-checks.md, "Structure and growth").
            out["checker-size:scripts/check_governance.py"] = (f"lines={n} bytes=0 scripts/check_governance.py: {n} lines in one file; split it with "
                                                                f"skill-ai-it scripts/split_checker.py (threshold {CHECKER_SPLIT_LINES})")
    return out


def sizes(value: str) -> tuple[int, int]:
    """The `lines=` and `bytes=` numbers at the start of an over-budget finding or baseline value.

    Args:
        value: the text.

    Returns:
        (lines, bytes); (0, 0) when absent.
    """
    m = re.match(r"lines=(\d+) bytes=(\d+)", value or "")
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)


def regressions(found: dict[str, str], baseline: dict[str, str]) -> dict[str, str]:
    """Findings the baseline does not excuse.

    Args:
        found: today's findings.
        baseline: the recorded findings.

    Returns:
        New findings, plus over-budget files that grew past their recorded size.
    """
    out = {}
    for key, msg in found.items():
        if key not in baseline:
            out[key] = msg
        elif key.startswith(("over-budget:", "checker-size:")):
            now, then = sizes(msg), sizes(baseline[key])
            if now[0] > then[0] or now[1] > then[1]:
                out[key] = f"{msg} (grew from {then[0]} lines, {then[1]} bytes)"
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
        kept = {k: (found[k] if k.startswith(("over-budget:", "checker-size:")) else baseline.get(k, today.isoformat())) for k in sorted(found)}
        base_path.parent.mkdir(parents=True, exist_ok=True)
        base_path.write_text(json.dumps(kept, indent=1) + "\n")
        print(f"baseline written: {len(kept)} finding(s) -> {args.baseline}")
        return 0
    bad = regressions(found, baseline)
    gone = [k for k in baseline if k not in found]
    if not args.check:
        counts: dict[str, int] = {}
        for k in found:
            counts[k.split(":", 1)[0]] = counts.get(k.split(":", 1)[0], 0) + 1
        print(f"doc freshness: {len(found)} finding(s) ({', '.join(f'{r} {n}' for r, n in sorted(counts.items())) or 'none'}), {len(bad)} new")
        for k in sorted(bad):
            print(f"  NEW {bad[k]}")
        return 0
    for k in sorted(bad):
        print(f"  ✗ doc-freshness: {bad[k]}")
    if gone:
        print(f"  note: {len(gone)} baseline finding(s) resolved; drop them with --write-baseline")
    print(f"{'FAIL' if bad else 'OK'} — doc freshness: {len(bad)} new finding(s), {len(found) - len(bad)} baselined")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
