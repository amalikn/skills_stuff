#!/usr/bin/env python3
"""Append one decision row to a project's Markdown decision log, in the form pad_decisions.py mirrors into Pad.

Written after continuum 2026-11-24, where nine rows were appended by hand: one had four columns instead of six (the mirror skipped it), one packed
four answers into a run-on sentence (operator: "each point should be on a separate line at least"). The row is
`| DL-nnn | YYYY-MM-DD | architecture or process | <intro><br>- point<br>- point<br><closing> | reason | who |`: the next free number, one
decision per row, its points separated by `<br>` so the table row stays on one line and Pad shows one point per line.
The row follows the log's own header (smc-resiliency 2026-11-25: its log has seven columns, `| ID | Date | Kind | Decision | Reason | Stamp and
source | Status |`, and a six-column row went in misaligned): a `Who`/`Decider` column takes --who, a `Stamp and source` column needs --stamp (and the
reason column then carries "reason; who"), a `Status` column takes --status; a header with any other column is refused.

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
#: Header names (lower case) this script fills, by the value each takes.
KNOWN = {
  "id": "dl",
  "date": "date",
  "kind": "kind",
  "decision": "decision",
  "reason": "reason",
  "who": "who",
  "decider": "who",
  "stamp and source": "stamp",
  "status": "status",
}


def header(lines: list[str]) -> list[str]:
  """The decision table's column names, lower case.

  Args:
      lines: the log's lines.

  Returns:
      The names of the first table row whose first cell is ID, or the six-column default when the log has none yet.
  """
  for line in lines:
    cells = [c.strip().lower() for c in line.strip().strip("|").split("|")]
    if line.startswith("|") and cells and cells[0] == "id":
      return cells
  return ["id", "date", "kind", "decision", "reason", "who"]


def next_id(lines: list[str]) -> str:
  """The next free DL id of a log.

  Args:
      lines: the log's lines.

  Returns:
      "DL-nnn", one above the highest present (DL-001 for an empty log).
  """
  ids = [int(m.group(1)) for line in lines if (m := ROW.match(line))]
  return f"DL-{(max(ids) + 1 if ids else 1):03d}"


def build_row(
  dl: str,
  date: str,
  kind: str,
  parts: tuple[str, list[str], str],
  reason: str,
  who: str,
  cols: list[str] | None = None,
  stamp: str = "",
  status: str = "accepted",
) -> str:
  """One decision-log row.

  Args:
      dl: its id.
      date: YYYY-MM-DD.
      kind: architecture or process.
      parts: (intro, points, closing); points become "- point" lines, empty intro or closing are left out.
      reason: the reason column.
      who: the decider column.
      cols: the log's header (header()); None is the six-column default.
      stamp: the "Stamp and source" cell, required when the header has that column.
      status: the Status cell.

  Returns:
      The table row, its cells in the header's order.

  Raises:
      ValueError: a `|` or a line break in any text, no point and no intro, an unknown header column, or a missing stamp.
  """
  intro, points, closing = parts
  cols = cols or ["id", "date", "kind", "decision", "reason", "who"]
  unknown = [c for c in cols if c not in KNOWN]
  if unknown:
    raise ValueError(f"the log's header has columns this script does not fill: {', '.join(unknown)}")
  if "stamp and source" in cols and not stamp:
    raise ValueError('the log has a `Stamp and source` column: pass --stamp (e.g. "20261125_2017: [SCRATCHPAD.md](../../SCRATCHPAD.md)")')
  texts = [intro, closing, reason, who, stamp, status, *points]
  if any("|" in t or "\n" in t for t in texts):
    raise ValueError("a `|` or a line break in the text would break the table row; reword it")
  if not points and not intro:
    raise ValueError("a decision needs an intro or at least one point")
  pieces = [intro] if intro else []
  pieces += [p if p.startswith("- ") else f"- {p}" for p in points]
  pieces += [closing] if closing else []
  has_who = any(KNOWN[c] == "who" for c in cols)
  value = {
    "dl": dl,
    "date": date,
    "kind": kind,
    "decision": "<br>".join(pieces),
    "reason": reason if has_who else f"{reason}; {who}",
    "who": who,
    "stamp": stamp,
    "status": status,
  }
  return "| " + " | ".join(value[KNOWN[c]] for c in cols) + " |"


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
  ap.add_argument("--stamp", default="", help="the Stamp and source cell, for a log that has that column")
  ap.add_argument("--status", default="accepted", help="the Status cell, for a log that has that column")
  ap.add_argument("--apply", action="store_true")
  a = ap.parse_args(argv)
  try:
    text = a.log.read_text()
    lines = text.splitlines()
    dl = next_id(lines)
    row = build_row(dl, a.date, a.kind, (a.intro, a.point, a.closing), a.reason, a.who, header(lines), a.stamp, a.status)
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
