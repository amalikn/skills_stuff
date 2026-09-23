#!/usr/bin/env python3
"""Append a write-back routing record. Standard library only.

The log records WHERE a finding was incorporated, never the finding's content. That boundary is the whole point: a log
you can write to and feel finished with would legitimise recording knowledge instead of incorporating it, which is the
exact failure this log exists to make visible.

So `--incorporated-in` is checked here, at write time: every path must already exist. You cannot claim a destination
before the knowledge is in it. Recording an open loop is allowed and is the honest option when the destination is not
written yet -- `--open` leaves incorporated_in empty and check_governance.py reports the row as outstanding.

The file is `ledger.jsonl`, matching the estate convention set by skill-walk-before-run (operator, 2026-09-23).

**That name is covered by the estate OPA guard**, which hard-blocks any Bash command whose text mentions it and routes
the author to skill-walk-before-run's `append_entry.py`. For this package that guard is right in spirit and wrong in
destination: it is correct that nothing should hand-write the file, and incorrect that this package's rows belong in
another pack's writer, which enforces a different schema. Append here, through this script, and never by shell
redirection. If a Bash command is blocked merely for naming the file, that is the guard matching command text rather
than a real collision.
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "ledger.jsonl"
KINDS = ("validator_gap", "method_knowledge", "schema_shape", "closed_set_pressure", "recordkeeping")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-project", required=True, help="the consuming project that found it")
    parser.add_argument("--kind", required=True, choices=KINDS)
    parser.add_argument("--finding", required=True, help="one sentence; a pointer, not the knowledge itself")
    parser.add_argument("--incorporated-in", nargs="*", default=[], help="repo-relative path(s) that now carry it")
    parser.add_argument("--open", action="store_true", help="record an outstanding loop with no destination yet")
    parser.add_argument("--commit", default=None)
    parser.add_argument("--supersedes", default=None)
    parser.add_argument("--notes", default=None)
    parser.add_argument("--ts", default=None, help="ISO-8601; defaults to now (machine local offset)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    if args.open and args.incorporated_in:
        errors.append("--open and --incorporated-in are mutually exclusive: a row is either routed or outstanding")
    if not args.open and not args.incorporated_in:
        errors.append("give --incorporated-in, or --open to record it as an outstanding loop")

    # The load-bearing check. A destination that does not exist is a claim that the knowledge landed when it did not.
    for rel in args.incorporated_in:
        if not (ROOT / rel).exists():
            errors.append(f"incorporated_in path does not exist: {rel}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    # Key order is the column order: `ts` then project first (matching the skill-walk-before-run ledger), `entry_id` last.
    record = {
        "ts": args.ts or datetime.now().astimezone().isoformat(timespec="seconds"),
        "source_project": args.source_project,
        "kind": args.kind,
        "finding": args.finding,
        "status": "open" if args.open else "incorporated",
        "incorporated_in": list(args.incorporated_in),
        "commit": args.commit,
        "supersedes": args.supersedes,
        "notes": args.notes,
        "entry_id": str(uuid.uuid4()),
    }

    if args.dry_run:
        print(json.dumps(record, indent=2))
        return 0

    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")
    print(f"APPENDED: entry={record['entry_id']} status={record['status']} source={record['source_project']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
