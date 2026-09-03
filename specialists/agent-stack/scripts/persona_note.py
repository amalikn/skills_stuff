#!/usr/bin/env python3
"""Persist each persona's analysis as it returns, so a run that breaks halfway keeps what it already bought.

THE PROBLEM. A multi-persona route dispatches several analyses and synthesises them at the end. Each one costs real money and minutes. If the session dies, the
context compacts, or a runner hits a limit — all observed on 20260903, when a session limit killed a 60-call run at call 5 — the completed analyses go with it.
Four personas, two returned, and the two that finished are lost along with the two that never ran.

WHAT THIS IS, AND IS NOT. It writes each returned analysis to a file, and records which personas were dispatched against which have come back. It is EVIDENCE
RETENTION. It is deliberately NOT a resume mechanism: nothing here re-dispatches anything, and nothing continues a broken run on its own. Auto-continuation is
unattended work, which rule 0001 excludes and which is the whole reason this project exists as a fork. Re-running is the operator's call; the notes are simply
there when they make it.

WHY THE RAW NOTES ARE WORTH KEEPING, separately from crash safety. The synthesis compresses several analyses into one answer, and the compression is lossy in
the direction that matters: on 20260903 a CFO's postage-band arithmetic and a Critic's six-condition inversion were the most useful output of a run, and only a
paraphrase of them survived into the report. A persona's own words are better evidence than a summary of them.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BANNER = """> **This is ONE persona's analysis, not the verdict.** It was written before the synthesis existed and may be contradicted by another persona or by the final
> answer. Read the run's report for the conclusion. Kept because a persona's own words are better evidence than a summary of them.
"""


def manifest_path(run_dir: Path) -> Path:
    return run_dir / "MANIFEST.json"


def load_manifest(run_dir: Path) -> dict:
    p = manifest_path(run_dir)
    if p.is_file():
        return json.loads(p.read_text())
    return {"task": "", "dispatched": [], "returned": [], "started": datetime.now(timezone.utc).isoformat(timespec="seconds")}


def save_manifest(run_dir: Path, m: dict) -> None:
    m["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    m["complete"] = bool(m["dispatched"]) and sorted(m["dispatched"]) == sorted(m["returned"])
    manifest_path(run_dir).write_text(json.dumps(m, indent=2, sort_keys=True) + "\n")


def cmd_dispatch(args: argparse.Namespace) -> int:
    """Record intent BEFORE the work happens.

    Without this, a run that died mid-flight is indistinguishable from one that only ever wanted the personas that came back — and the difference is the whole
    point. An incomplete run must be visible as incomplete.
    """
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    m = load_manifest(run_dir)
    if args.task:
        m["task"] = args.task
    for p in args.persona:
        if p not in m["dispatched"]:
            m["dispatched"].append(p)
    save_manifest(run_dir, m)
    print(f"dispatched: {', '.join(sorted(m['dispatched']))}")
    return 0


def cmd_write(args: argparse.Namespace) -> int:
    """One returned analysis, read from stdin."""
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    body = sys.stdin.read()
    if not body.strip():
        print("refusing to write an empty note", file=sys.stderr)
        return 1
    m = load_manifest(run_dir)
    if args.persona not in m["dispatched"]:
        m["dispatched"].append(args.persona)
    if args.persona not in m["returned"]:
        m["returned"].append(args.persona)
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    note = run_dir / f"{args.persona}.md"
    note.write_text(f"# {args.persona} — analysis\n\n{BANNER}\nReturned: {stamp}\n\n---\n\n{body.rstrip()}\n")
    save_manifest(run_dir, m)
    pending = sorted(set(m["dispatched"]) - set(m["returned"]))
    tail = f"   pending: {', '.join(pending)}" if pending else "   COMPLETE"
    print(f"wrote {note}   returned {len(m['returned'])}/{len(m['dispatched'])}{tail}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir)
    if not manifest_path(run_dir).is_file():
        print(f"no run at {run_dir}")
        return 1
    m = load_manifest(run_dir)
    pending = sorted(set(m["dispatched"]) - set(m["returned"]))
    print(f"task: {m.get('task', '')[:100]}")
    print(f"returned {len(m['returned'])}/{len(m['dispatched'])}" + ("  COMPLETE" if m.get("complete") else "  INCOMPLETE"))
    for p in sorted(m["dispatched"]):
        print(f"  {'ok     ' if p in m['returned'] else 'PENDING'} {p}")
    if pending:
        # Stated plainly, because the value of the whole mechanism is that finished work survived. Re-dispatching is the operator's decision, never this tool's.
        print(f"\nThe {len(m['returned'])} completed analys(es) are on disk and do not need re-running. Re-dispatch only {', '.join(pending)} if you continue.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Persist persona analyses as they return. Evidence retention, never auto-resume.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("dispatch", help="record which personas are about to be asked, BEFORE they run")
    d.add_argument("--run-dir", required=True)
    d.add_argument("--persona", action="append", required=True)
    d.add_argument("--task")
    d.set_defaults(fn=cmd_dispatch)

    w = sub.add_parser("write", help="store one returned analysis, read from stdin")
    w.add_argument("--run-dir", required=True)
    w.add_argument("--persona", required=True)
    w.set_defaults(fn=cmd_write)

    s = sub.add_parser("status", help="what returned, what is still pending")
    s.add_argument("--run-dir", required=True)
    s.set_defaults(fn=cmd_status)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
