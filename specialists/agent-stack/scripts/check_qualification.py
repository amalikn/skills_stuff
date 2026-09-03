#!/usr/bin/env python3
"""Refuse a corpus-spending run unless a receipt qualified THIS execution path.

A receipt is not a general certificate. It records that one command, driving one runner, against one harness, completed N consecutive disposable calls. Any of
those three changing means the thing that was qualified no longer exists — most sharply the harness, which is part of the execution path under test rather than
a neutral observer of it. The size check is the same idea in the other dimension: quota and session limits surface at sequence length, so a receipt earned over
5 calls says nothing about 60.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate_routing import _sha  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify a runner-qualification receipt covers the run being attempted.")
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--size", type=int, required=True)
    ap.add_argument("--command", required=True)
    args = ap.parse_args()

    if not args.receipt.is_file():
        print(f"no qualification receipt at {args.receipt} — run `just qualify-runner` first", file=sys.stderr)
        return 1
    r = json.loads(args.receipt.read_text())

    live_harness = _sha(ROOT / "scripts" / "evaluate_routing.py")
    problems = []
    if not r.get("qualified"):
        problems.append(f"receipt records a FAILED qualification ({r.get('calls_ok')}/{r.get('calls_requested')} calls ok)")
    if r.get("qualified_for_corpus_size", 0) < args.size:
        problems.append(f"receipt covers {r.get('qualified_for_corpus_size')} calls, this run needs {args.size}")
    if r.get("command") != args.command:
        problems.append(f"receipt qualified command {r.get('command')!r}, this run uses {args.command!r}")
    if r.get("harness_sha") and r["harness_sha"] != live_harness:
        problems.append(f"receipt qualified harness {r['harness_sha']}, this checkout is {live_harness} — requalify")
    if not r.get("harness_sha"):
        problems.append("receipt predates harness binding and cannot be trusted for this run — requalify")
    if r.get("payload") != "realistic":
        problems.append(f"receipt was earned on {r.get('payload', 'unrecorded')!r} probes — a real prompt is ~761x larger, so quota headroom was never tested; requalify with --payload realistic")

    if problems:
        for p in problems:
            print(f"REFUSED: {p}", file=sys.stderr)
        return 1
    print(f"runner qualified: {r['calls_ok']}/{r['calls_requested']} calls, {r['model']} via {r['runner']}, {r['timestamp']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
