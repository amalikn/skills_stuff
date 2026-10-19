#!/usr/bin/env python3
"""Render the naming table in references/naming-conventions.md from the pack's naming.toml, or report when the table is out of step. Writes only
the table between its markers, and only with --write. Stdlib only.

Why (operator, 2026-10-19): the mapping is data first, like a flow map; the reference shows it to readers and must never drift from what
naming_check.py enforces, so the table is generated, never edited by hand.

Usage:
    naming_table.py            # exit 1 when the table differs from what naming.toml renders
    naming_table.py --write    # rewrite the table between the markers
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import naming_check

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)
PACK = Path(__file__).resolve().parent.parent
REFERENCE = PACK / "references" / "naming-conventions.md"
BEGIN = "<!-- BEGIN GENERATED: naming table (scripts/naming_table.py from naming.toml; do not edit) -->"
END = "<!-- END GENERATED: naming table -->"
HEAD = ("Language", "Element", "Convention", "Checked by", "Source (capture)")


def render(mapping: dict) -> str:
    """The table, one row per rule, columns padded so the raw markdown reads as a table.

    Args:
        mapping: naming_check.load_mapping()'s result.

    Returns:
        The markdown table, newline-terminated.
    """
    rows = []
    for r in mapping["rule"]:
        checked = {"file": "`naming_check.py` (file names)", "recipe": "`naming_check.py` (recipes)"}.get(r["check"], r.get("tool", ""))
        source = r["source"] + (f" (`{r['capture']}`)" if r.get("capture") else "")
        rows.append((r["language"], r["element"], r["convention"], checked, source))
    width = [max(len(x[i]) for x in [HEAD, *rows]) for i in range(len(HEAD))]
    return "\n".join(_row(cells, width) for cells in [HEAD, tuple("-" * w for w in width), *rows]) + "\n"


def _row(cells: tuple, width: list[int]) -> str:
    """One table row, each cell padded to its column's width.

    Args:
        cells: the row's cells.
        width: each column's width.

    Returns:
        The markdown row.
    """
    return "| " + " | ".join(c.ljust(w) for c, w in zip(cells, width)) + " |"


def splice(text: str, table: str) -> str:
    """The reference with the table between the markers replaced.

    Args:
        text: the reference's text.
        table: render()'s output.

    Returns:
        The new text.

    Raises:
        ValueError: when the markers are missing.
    """
    if BEGIN not in text or END not in text:
        raise ValueError(f"{REFERENCE.name} lacks the generated-table markers")
    head, rest = text.split(BEGIN, 1)
    return f"{head}{BEGIN}\n\n{table}\n{END}{rest.split(END, 1)[1]}"


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 when current (or written), 1 on drift, 2 on a bad mapping or missing markers.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--write", action="store_true", help="rewrite the table")
    args = ap.parse_args(argv)
    try:
        current = REFERENCE.read_text(encoding="utf-8")
        wanted = splice(current, render(naming_check.load_mapping()))
    except (OSError, ValueError) as exc:
        print(f"naming_table: {exc}", file=sys.stderr)
        return 2
    if args.write:
        REFERENCE.write_text(wanted, encoding="utf-8")
        print(f"naming_table: wrote {REFERENCE.relative_to(PACK)}")
        return 0
    if wanted != current:
        print(f"naming_table: {REFERENCE.relative_to(PACK)} is out of step with naming.toml; run `just naming-table`")
        return 1
    print("naming_table: OK, the table matches naming.toml")
    return 0


if __name__ == "__main__":
    sys.exit(main())
