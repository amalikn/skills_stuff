#!/usr/bin/env python3
"""Append a write-back routing record. Standard library only.

The log records WHERE a finding was incorporated, never the finding's content. That boundary is the whole point: a log
you can write to and feel finished with would legitimise recording knowledge instead of incorporating it, which is the
exact failure this log exists to make visible.

So `--incorporated-in` is checked here, at write time: every path must already exist. You cannot claim a destination
before the knowledge is in it. Recording an open loop is allowed and is the honest option when the destination is not
written yet -- `--open` leaves incorporated_in empty and check_governance.py reports the row as outstanding.

The file is `write-back.jsonl`. It is deliberately not named after the other append-only record kept by
skill-walk-before-run: the estate OPA guard hard-blocks direct writes to that filename and routes them to that pack's
own writer. Avoiding the collision is correct; weakening a guard so this package could reuse a word would not be.
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "write-back.jsonl"
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
    parser.add_argument("--recorded-at", default=None, help="ISO-8601; defaults to now (UTC)")
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

    record = {
        "entry_id": str(uuid.uuid4()),
        "recorded_at": args.recorded_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_project": args.source_project,
        "kind": args.kind,
        "finding": args.finding,
        "status": "open" if args.open else "incorporated",
        "incorporated_in": list(args.incorporated_in),
        "commit": args.commit,
        "supersedes": args.supersedes,
        "notes": args.notes,
    }

    if args.dry_run:
        print(json.dumps(record, indent=2))
        return 0

    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    print(f"APPENDED: entry={record['entry_id']} status={record['status']} source={record['source_project']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
