#!/usr/bin/env python3
"""Qualify an external runner before any corpus is measured through it.

WHY. Holdout 24 lost 5 of 24 cases — 21% of a single-use corpus — to five consecutive `claude -p` invocations that exited 1 with empty stderr. The routing
system did not fail that run; the execution pipeline failed to complete it, and the evidence could not even say why. Per spec 0006 a runner is qualified before
it carries evidence, and per spec 0007 that qualification precedes the gate-only sweep too: an execution error is EXCLUDED from the denominators, so an unstable
runner silently changes which cases a precision or recall figure is computed over, and a metric on a shifting subset cannot be judged against a pre-registered
threshold.

DISPOSABLE CALLS ONLY. Qualification exercises the same path as a real run — prompt on stdin, invoke, extract JSON, classify the outcome — using throwaway
prompts. It never touches a corpus case, so it can never spend evidence.

WHAT A PASS MEANS, AND FOR HOW LONG. That this runner completed N consecutive calls, returned parseable JSON each time, and produced a legible diagnostic when
deliberately failed. Qualification is per runner, per arm, and PERISHABLE: it expires when the runner, its credentials, its quota state or the harness changes.
It is evidence about the pipeline on a day, never a property of the project.
"""
from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate_routing import extract_json  # noqa: E402  — qualification must exercise the harness's own extractor, not a lookalike
from evaluate_routing import _sha  # noqa: E402  — the receipt binds to the harness it qualified; a harness edit invalidates it

# Two probe shapes, deliberately varied, neither containing a corpus case.
#
# PAYLOAD SIZE IS PART OF WHAT IS BEING QUALIFIED. A real evaluation prompt is ~12,000 tokens because it pastes the whole routing catalogue; a trivial probe is
# ~16. Sixty of each differ by roughly 730,000 input tokens, and quota exhaustion — the most likely cause of the five silent failures in holdout 24 — is driven
# by token volume, not call count. A qualification run on trivial probes therefore proves transport, parse, exit handling and session survivability across 60
# calls, and proves almost nothing about quota headroom for the run it is meant to authorise. `realistic` (the default) pads each probe with the same catalogue
# text a real prompt carries, so the token profile matches without any corpus case ever being sent.
INSTRUCTIONS = [
    'Reply with only this JSON and nothing else: {"ok": true, "n": %d}',
    'Return exactly this JSON object, no prose, no markdown fence: {"ok": true, "n": %d}',
]


def probe(i: int, payload: str) -> str:
    instruction = INSTRUCTIONS[i % len(INSTRUCTIONS)] % i
    if payload == "trivial":
        return instruction
    catalogue = (ROOT / "routing.toml").read_text()
    return (
        "Below is reference material you must IGNORE completely. It is present only to make this request the size of a real one.\n"
        "Do not analyse it, do not mention it, do not route anything.\n\n"
        f"--- BEGIN IGNORED MATERIAL ---\n{catalogue}\n--- END IGNORED MATERIAL ---\n\n"
        f"{instruction}"
    )


def one_call(command: str, prompt: str, timeout: int) -> dict:
    """One invocation, classified. Every failure mode gets a NAME — an unnamed failure is the defect this whole script exists to remove."""
    started = time.monotonic()
    try:
        proc = subprocess.run(command, input=prompt, text=True, shell=True, cwd=ROOT, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"outcome": "timeout", "elapsed": round(time.monotonic() - started, 2), "detail": f"exceeded {timeout}s"}
    elapsed = round(time.monotonic() - started, 2)
    if proc.returncode != 0:
        err, out = proc.stderr.strip(), proc.stdout.strip()
        if not err and not out:
            return {"outcome": "silent-failure", "exit": proc.returncode, "elapsed": elapsed,
                    "detail": "both streams empty — unclassifiable without runner-side logs"}
        return {"outcome": "nonzero-exit", "exit": proc.returncode, "elapsed": elapsed, "detail": (err or out)[-300:]}
    try:
        payload = extract_json(proc.stdout)
    except Exception as exc:
        return {"outcome": "unparseable", "exit": 0, "elapsed": elapsed, "detail": f"{type(exc).__name__}: {exc}"[:300]}
    if not isinstance(payload, dict):
        return {"outcome": "unparseable", "exit": 0, "elapsed": elapsed, "detail": f"parsed to {type(payload).__name__}, not an object"}
    return {"outcome": "ok", "exit": 0, "elapsed": elapsed}


def main() -> int:
    ap = argparse.ArgumentParser(description="Qualify a runner on disposable calls before it carries evidence.")
    ap.add_argument("--command", required=True, help="Runner CLI; the prompt arrives on stdin, exactly as in a real run")
    ap.add_argument("--calls", type=int, required=True, help="Consecutive calls required — set it to the corpus size, so quota and session limits surface HERE")
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--payload", choices=("realistic", "trivial"), default="realistic",
                    help="realistic (default) pads each probe to a real prompt's token profile so quota headroom is actually tested; trivial tests transport only")
    ap.add_argument("--provider", default="unspecified")
    ap.add_argument("--model", default="unspecified")
    ap.add_argument("--runner", default="unspecified")
    ap.add_argument("--output", type=Path, help="Where to write the qualification receipt")
    ap.add_argument("--skip-failure-probe", action="store_true",
                    help="Skip the deliberate-failure check. It costs no model call and proves the harness can NAME a failure; skip only with a reason.")
    args = ap.parse_args()

    results, longest_streak, streak = [], 0, 0
    for i in range(args.calls):
        r = one_call(args.command, probe(i, args.payload), args.timeout)
        results.append(r)
        streak = streak + 1 if r["outcome"] == "ok" else 0
        longest_streak = max(longest_streak, streak)
        print(f"  {i + 1:3}/{args.calls}  {r['outcome']:16} {r.get('elapsed', 0):6.2f}s"
              + (f"  {r.get('detail', '')[:90]}" if r["outcome"] != "ok" else ""))

    ok = sum(1 for r in results if r["outcome"] == "ok")
    by_outcome: dict[str, int] = {}
    for r in results:
        by_outcome[r["outcome"]] = by_outcome.get(r["outcome"], 0) + 1
    elapsed = [r["elapsed"] for r in results if r["outcome"] == "ok"]

    # Failure legibility, offline: a command that exits non-zero must produce a NAMED outcome, not an empty string.
    legible = None
    if not args.skip_failure_probe:
        induced = one_call("exit 7", "unused", 10)
        legible = induced["outcome"] in ("nonzero-exit", "silent-failure") and bool(induced.get("detail"))
        print(f"\nfailure legibility probe (offline, `exit 7`): outcome={induced['outcome']} detail={induced.get('detail', '')[:80]!r}")

    labelled = args.provider != "unspecified" and args.model != "unspecified"
    checks = {
        "sequence_reliability": (ok == args.calls, f"{ok}/{args.calls} calls succeeded; longest clean streak {longest_streak}"),
        "parse_reliability": (by_outcome.get("unparseable", 0) == 0, f"{by_outcome.get('unparseable', 0)} unparseable repl(ies)"),
        "failure_legibility": (legible is not False, "deliberate failure produced a named outcome" if legible else
                               ("skipped" if legible is None else "deliberate failure produced no diagnostic")),
        "timeout_behaviour": (by_outcome.get("timeout", 0) == 0, f"{by_outcome.get('timeout', 0)} timeout(s) at {args.timeout}s"),
        "labels": (labelled, f"provider={args.provider} model={args.model} runner={args.runner}"),
    }
    passed = all(good for good, _ in checks.values())

    print("\nQualification:")
    for name, (good, detail) in checks.items():
        print(f"  {'PASS' if good else 'FAIL'}  {name:22} {detail}")
    if elapsed:
        print(f"\n  latency: median {statistics.median(elapsed):.2f}s, max {max(elapsed):.2f}s over {len(elapsed)} clean call(s)")

    receipt = {
        "qualified": passed, "calls_requested": args.calls, "calls_ok": ok, "longest_clean_streak": longest_streak,
        "outcomes": by_outcome, "checks": {k: v[0] for k, v in checks.items()},
        "provider": args.provider, "model": args.model, "runner": args.runner, "command": args.command,
        "timeout": args.timeout, "median_latency": statistics.median(elapsed) if elapsed else None,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        # Perishable by construction: a receipt that does not say what it was qualified FOR invites reuse against a larger corpus it never tested.
        "qualified_for_corpus_size": args.calls if passed else 0,
        # A receipt must say what SIZE of call it qualified, not only how many. A trivial-payload receipt does not authorise a full-prompt run.
        "payload": args.payload,
        "probe_chars": len(probe(0, args.payload)),
        # Binding fields. A receipt earned with one command or one harness does not transfer: both are part of the execution path under test, so a change to
        # either means the thing that was qualified no longer exists.
        "harness_sha": _sha(ROOT / "scripts" / "evaluate_routing.py"),
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print(f"\nreceipt: {args.output}")

    if args.payload == "trivial":
        print("\n  NOTE: trivial payload — this run tested transport, parse and session survival, NOT quota headroom for full-size prompts.")
    print(f"\nRUNNER QUALIFICATION: {'PASS' if passed else 'FAIL'}"
          + ("" if passed else " — do not spend evidence through this runner"))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
