#!/usr/bin/env python3
"""Append one decision row to a project's Markdown decision log, in the form pad_decisions.py mirrors into Pad.

Written after continuum 2026-11-24, where nine rows were appended by hand: one had four columns instead of six (the mirror skipped it), one packed
four answers into a run-on sentence (operator: "each point should be on a separate line at least"). The row is
`| DL-nnn | YYYY-MM-DD | architecture or process | <intro><br>- point<br>- point<br><closing> | reason | who |`: the next free number, one
decision per row, its points separated by `<br>` so the table row stays on one line and Pad shows one point per line.

Usage:
    python3 decision_log_add.py --log docs/architecture-review/DECISION-LOG.md --kind architecture \\
        --intro "Operator, in chat (topic):" --point "Region: ... Not taken: ..." --point "..." --closing "Agent advice followed." \\
        --reason "Why." [--who "Operator."] [--date 2026-11-24]            # plan: prints the row
    ... --apply                                                             # appends it, prints its DL id
Then mirror: `just pad-decisions --apply` in the project.
Safety: plan by default; --apply appends one line and touches nothing else. Exit codes: 0 done; 1 bad input (a `|` in the text, no point, an
unreadable log). Runtime budget: under 1 s.
"""

from __future__ import annotations

import argparse
import datetime
import re
import sys
from pathlib import Path

ROW = re.compile(r"^\| DL-(\d{3,}) \|")


def next_id(lines: list[str]) -> str:
    """The next free DL id of a log.

    Args:
        lines: the log's lines.

    Returns:
        "DL-nnn", one above the highest present (DL-001 for an empty log).
    """
    ids = [int(m.group(1)) for line in lines if (m := ROW.match(line))]
    return f"DL-{(max(ids) + 1 if ids else 1):03d}"


def build_row(dl: str, date: str, kind: str, parts: tuple[str, list[str], str], reason: str, who: str) -> str:
    """One decision-log row.

    Args:
        dl: its id.
        date: YYYY-MM-DD.
        kind: architecture or process.
        parts: (intro, points, closing); points become "- point" lines, empty intro or closing are left out.
        reason: the reason column.
        who: the decider column.

    Returns:
        The table row.

    Raises:
        ValueError: a `|` or a line break in any text, or no point and no intro.
    """
    intro, points, closing = parts
    texts = [intro, closing, reason, who, *points]
    if any("|" in t or "\n" in t for t in texts):
        raise ValueError("a `|` or a line break in the text would break the table row; reword it")
    if not points and not intro:
        raise ValueError("a decision needs an intro or at least one point")
    pieces = [intro] if intro else []
    pieces += [p if p.startswith("- ") else f"- {p}" for p in points]
    pieces += [closing] if closing else []
    return f"| {dl} | {date} | {kind} | {'<br>'.join(pieces)} | {reason} | {who} |"


def main(argv: list[str] | None = None) -> int:
    """Plan or append the row.

    Args:
        argv: command-line arguments; None uses sys.argv.

    Returns:
        0 when planned or appended; 1 on bad input.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--log", type=Path, default=Path("docs/architecture-review/DECISION-LOG.md"))
    ap.add_argument("--kind", choices=["architecture", "process"], required=True)
    ap.add_argument("--intro", default="")
    ap.add_argument("--point", action="append", default=[])
    ap.add_argument("--closing", default="")
    ap.add_argument("--reason", required=True)
    ap.add_argument("--who", default="Operator.")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    try:
        text = a.log.read_text()
        dl = next_id(text.splitlines())
        row = build_row(dl, a.date, a.kind, (a.intro, a.point, a.closing), a.reason, a.who)
    except (OSError, ValueError) as e:
        print(f"decision_log_add: {e}", file=sys.stderr)
        return 1
    print(row)
    if not a.apply:
        print(f"plan only: {dl} would be appended to {a.log}; --apply writes")
        return 0
    with a.log.open("a") as f:
        f.write(("" if text.endswith("\n") else "\n") + row + "\n")
    print(f"appended {dl} to {a.log}; mirror with `just pad-decisions --apply`")
    return 0


if __name__ == "__main__":
    sys.exit(main())
