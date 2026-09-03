#!/usr/bin/env python3
"""Field log — what happened when the router was used on real work.

WHY THIS EXISTS. Every measurement this project has made tests whether the router picks what a corpus says it should. That is a NECESSARY property and not a
sufficient one: a route can be perfectly corpus-correct and still not make the work better. No corpus can close that gap, because the corpus is the thing being
agreed with. Only real use can.

WHAT IT IS, HONESTLY. Observational, self-reported, small-n, and confounded by everything — mood, task difficulty, whether the operator was going to do it that
way anyway. It cannot establish causation and must never be reported as if it could. What it CAN do is surface a pattern too consistent to be noise: the same
owner overridden the same way six times is a routing defect regardless of how soft each individual data point is.

THE FIELD IT EXISTS FOR IS `overrode`. A route that was followed tells you the operator did not disagree, which is weak. A route that was CHANGED, and how,
is the shadow-mode signal — collected during real work instead of in a separate exercise nobody has time to run.

Kept in the repo rather than the working cache: a re-run regenerates an eval, and nothing regenerates a day of real use.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "evals" / "field-log.jsonl"

HELPED = ("better", "neutral", "worse")  # operator-supplied only
FOLLOWED = ("full", "partial", "no")


def add(args: argparse.Namespace) -> int:
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "project": args.project,
        "task": args.task,
        "owner": args.owner,
        "personas": args.persona,
        "skills": args.skill,
        "followed": args.followed,
        "overrode": args.overrode,
        "helped": args.helped,
        "gates_useful": args.gates_useful,
        "note": args.note,
    }
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as fh:
        fh.write(json.dumps({k: v for k, v in entry.items() if v not in (None, [], "")}, sort_keys=True) + "\n")
    print(f"logged: {args.task[:70]}  [{args.followed}/{args.helped}]")
    return 0


def report(args: argparse.Namespace) -> int:
    if not LOG.is_file():
        print("no field entries yet")
        return 0
    rows = [json.loads(line) for line in LOG.read_text().splitlines() if line.strip()]
    if not rows:
        print("no field entries yet")
        return 0

    print(f"field entries: {len(rows)}   projects: {', '.join(sorted({r.get('project', '?') for r in rows}))}\n")

    for field, values in (("followed", FOLLOWED), ("helped", HELPED)):
        counts = Counter(r.get(field) for r in rows if r.get(field))
        n = sum(counts.values())
        if n:
            line = "  ".join(f"{v}={counts.get(v, 0)} ({counts.get(v, 0) / n:.0%})" for v in values)
            print(f"{field:9} {line}" + (f"   [{len(rows) - n} unrated]" if n < len(rows) else ""))
        elif field == "helped":
            # Said explicitly rather than left as a blank line: an agent logging its own routes cannot supply this, so an empty column is expected, not missing data.
            print(f"{field:9} none rated — this field is operator-supplied and an agent must not fill it in about its own work")

    gates = Counter(r.get("gates_useful") for r in rows if r.get("gates_useful"))
    if gates:
        print(f"{'gates':9} " + "  ".join(f"{k}={v}" for k, v in sorted(gates.items())))

    # The signal worth having. An override repeated is a defect; an override once is a preference.
    overrides = [r for r in rows if r.get("overrode")]
    print(f"\noverridden on {len(overrides)}/{len(rows)} uses")
    if overrides:
        by_owner = Counter(r.get("owner") for r in overrides if r.get("owner"))
        for owner, count in by_owner.most_common():
            total = sum(1 for r in rows if r.get("owner") == owner)
            flag = "  <-- repeated, look at this" if count >= 3 else ""
            print(f"  {owner:22} overridden {count}/{total}{flag}")
        print("\n  what was changed:")
        for r in overrides[-8:]:
            print(f"    {r['ts'][:10]}  {r.get('owner', '?'):20} {r['overrode'][:90]}")

    if len(rows) < 10:
        print(f"\n  n={len(rows)}. Too few to read as anything but anecdote — collect more before drawing a conclusion.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Record and read what the router did on real work.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="log one real use")
    a.add_argument("task", help="one line: what you were actually doing")
    a.add_argument("--project", required=True)
    a.add_argument("--owner", help="primary_owner the route named")
    a.add_argument("--persona", action="append", default=[])
    a.add_argument("--skill", action="append", default=[])
    a.add_argument("--followed", choices=FOLLOWED, required=True)
    a.add_argument("--overrode", help="WHAT you changed and why. The most valuable field here — a repeated override is a defect.")
    a.add_argument("--helped", choices=HELPED,
                   help="OPERATOR judgement, and optional. An agent must not fill this in about its own work: self-assessed helpfulness is the one field "
                        "where the recorder has an interest in the answer. Absent is the honest default.")
    a.add_argument("--gates-useful", choices=("yes", "no", "ignored"), help="were the research/critic/qa flags worth anything")
    a.add_argument("--note")
    a.set_defaults(fn=add)

    r = sub.add_parser("report", help="summarise the log")
    r.set_defaults(fn=report)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
