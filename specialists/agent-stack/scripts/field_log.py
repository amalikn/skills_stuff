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
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "evals" / "field-log.jsonl"

HELPED = ("better", "neutral", "worse")  # operator-supplied only
FOLLOWED = ("full", "partial", "no")

# A recorder asked "what did you override?" tends to answer "nothing" in prose rather than leave the flag off. Observed on the first real entry:
# `--overrode "none - direct route, no gates true (read-only)"`. Counting that as an override corrupts the ONE statistic this log exists to produce, and it does
# so silently and in the flattering direction — every clean route inflating the override rate. Normalised on read as well as refused on write, because the log
# already contains such an entry and future recorders include agents that will not have read this file.
NOT_AN_OVERRIDE = re.compile(r"^\s*(none|n/?a|nothing|no[\s_-]override|did not override|-{1,3})(?!\w)", re.I)

# Checked FIRST, because a prefix rule alone gets it wrong in both directions. "none - direct route, no gates true" is not an override; "none of the skills fit
# so I swapped owner to devops-hightower" is one, and both start with "none". A stated change beats a leading negation.
CHANGED = re.compile(r"\b(swap\w*|replac\w*|instead|dropp?e?d|added|skipp?e?d|chose|switch\w*|substitut\w*)\b", re.I)


def is_override(value: str | None) -> bool:
    """True only when the text describes a real departure from the route.

    Exists because a recorder asked "what did you override?" answers "nothing" in prose rather than leaving the flag off. Observed on the first real entry:
    `--overrode "none - direct route, no gates true (read-only)"`. Counting that as an override corrupts the ONE statistic this log exists to produce, silently
    and in the flattering direction, since every clean route would inflate the override rate.

    Normalised on read as well as refused on write: the file already contains such an entry, and future recorders include agents that will not have read this.
    """
    if not value or not value.strip():
        return False
    if CHANGED.search(value):
        return True
    return not NOT_AN_OVERRIDE.match(value)


def add(args: argparse.Namespace) -> int:
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "project": args.project,
        "task": args.task,
        "owner": args.owner,
        "personas": args.persona,
        "skills": args.skill,
        "followed": args.followed,
        # Stored only when it describes a real departure, so the field means one thing. A stated non-override is MOVED to `note`, never discarded: correcting
        # a statistic is not a licence to destroy an observation, and "direct route, no gates true (read-only)" is genuinely worth knowing.
        "overrode": args.overrode if is_override(args.overrode) else None,
        "helped": args.helped,
        "gates_useful": args.gates_useful,
        # route_mode is the dominant cost lever and one word. `gates` is the ONLY way to measure over-assertion in real use — the eval corpus can measure it
        # because it has expected values, and the field cannot, so recording what fired is the closest available signal. `closure_changed` is free: it is what
        # close_route.py printed, and it is the direct measure of whether the repair wired in on 20260903 is doing anything outside the harness.
        "route_mode": args.route_mode,
        "gates": args.gate,
        "closure_changed": args.closure_changed,
        # Cost, recorded two ways on purpose. `tokens` is the agent's ESTIMATE and is unverifiable; `dispatched` is a COUNT of subagents actually spawned and
        # is a fact. The count is also the dominant cost driver, since each subagent is a fresh context doing real work — so when the two disagree, believe the
        # count. Recording only the estimate would give a number nothing can check; recording only the count would lose the magnitude.
        "tokens_estimated": args.tokens,
        "dispatched": args.dispatched,
        # `returned` against `dispatched` is the incomplete marker. Recorded as two counts rather than a boolean because "2 of 4 came back" and "the run broke"
        # are different facts, and only the first says how much was salvaged. This is the measurement that decides whether a resume mechanism is ever worth
        # building — deliberately gathered before building one.
        "returned": args.returned,
        # The path to this run's persona notes. It is what lets the evolution proposer reach the raw analyses and the gaps the personas declared while working;
        # without it the notes sit in a project directory nothing knows to look in.
        "run_dir": args.run_dir,
        "note": args.note or (f"no override: {args.overrode}" if args.overrode and not is_override(args.overrode) else None),
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

    # Coverage first, because every figure below is computed over whatever subset happens to carry the field. An entry written against an older template, or by
    # an agent that skipped a flag, is silently absent from its statistic — and a rate over 2 of 9 entries reads exactly like a rate over 9 unless this is shown.
    FIELDS = ("route_mode", "owner", "personas", "skills", "gates", "closure_changed", "dispatched", "tokens_estimated", "followed", "overrode", "helped")
    cov = {f: sum(1 for r in rows if r.get(f) not in (None, "", [])) for f in FIELDS}
    thin = [f for f, n in cov.items() if n == 0]
    print("field coverage: " + "  ".join(f"{f}={n}/{len(rows)}" for f, n in cov.items() if n))
    if thin:
        print(f"  NEVER RECORDED: {', '.join(thin)} — every statistic below that needs one of these is absent, not zero")
    print()

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

    gated = [r for r in rows if r.get("gates") is not None]
    if gated:
        from collections import Counter as _C
        fired = _C(g for r in gated for g in (r.get("gates") or []))
        print(f"\ngates fired in the field ({len(gated)} entries recording them):")
        for g in ("research", "critic", "qa", "runtime"):
            n = fired.get(g, 0)
            print(f"  {g:9} {n:3}/{len(gated)}  ({n / len(gated):.0%})")
        allfour = sum(1 for r in gated if len(r.get("gates") or []) == 4)
        # The eval measures over-assertion against expected values; the field has none, so a high rate here is suggestive, not proof.
        print(f"  all four   {allfour:3}/{len(gated)}  <- compare 19/19 in holdout 24; a high rate here is suggestive, not proof")

    modes = Counter(r.get("route_mode") for r in rows if r.get("route_mode"))
    if modes:
        print("\nroute shape: " + "  ".join(f"{k}={v}" for k, v in modes.most_common()))

    closed = [r for r in rows if r.get("closure_changed") is not None]
    if closed:
        did = sum(1 for r in closed if r["closure_changed"].strip())
        print(f"\nclosure ran on {len(closed)} entr(ies); it changed the route in {did}")

    # Incompleteness, which is the question that decides whether a resume mechanism earns its complexity.
    both = [r for r in rows if isinstance(r.get("dispatched"), int) and isinstance(r.get("returned"), int)]
    if both:
        broke = [r for r in both if r["returned"] < r["dispatched"]]
        print(f"\nrun completeness: {len(both) - len(broke)}/{len(both)} complete")
        if broke:
            lost = sum(r["dispatched"] - r["returned"] for r in broke)
            print(f"  {len(broke)} incomplete run(s), {lost} persona analys(es) not returned")
            for r in broke[-5:]:
                print(f"    {r['ts'][:10]}  {r.get('owner', '?'):20} {r['returned']}/{r['dispatched']}  {r['task'][:60]}")
        else:
            print("  no incomplete runs recorded — the resume mechanism has not yet been shown to be needed")

    # Cost. Split by whether personas were dispatched, because that is where the money goes and it is the decision the operator actually makes.
    costed = [r for r in rows if isinstance(r.get("tokens_estimated"), int)]
    if costed:
        def med(xs):
            xs = sorted(xs)
            return xs[len(xs) // 2] if xs else 0
        inline = [r["tokens_estimated"] for r in costed if not r.get("dispatched")]
        team = [r["tokens_estimated"] for r in costed if r.get("dispatched")]
        print(f"\ncost (estimated tokens, {len(costed)}/{len(rows)} entries rated):")
        if inline:
            print(f"  no dispatch      n={len(inline):2}  median {med(inline):>8,}")
        if team:
            disp = [r.get("dispatched", 0) for r in costed if r.get("dispatched")]
            print(f"  with dispatch    n={len(team):2}  median {med(team):>8,}   median subagents {med(disp)}")
        if inline and team:
            print(f"  dispatching multiplies the routed cost by about {med(team) / max(med(inline), 1):.1f}x on this sample")

    # The signal worth having. An override repeated is a defect; an override once is a preference.
    overrides = [r for r in rows if is_override(r.get("overrode"))]
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
    a.add_argument("--overrode",
                   help="WHAT you changed about the route and why. The most valuable field here — a repeated override is a defect. OMIT IT ENTIRELY if you "
                        "followed the route; do not pass \"none\", which would count as an override and inflate the very statistic this log exists to produce.")
    a.add_argument("--helped", choices=HELPED,
                   help="OPERATOR judgement, and optional. An agent must not fill this in about its own work: self-assessed helpfulness is the one field "
                        "where the recorder has an interest in the answer. Absent is the honest default.")
    a.add_argument("--gates-useful", choices=("yes", "no", "ignored"), help="were the research/critic/qa flags worth anything")
    a.add_argument("--route-mode", choices=("direct-skill", "single-persona", "multi-persona"),
                   help="The route's shape. One word, and the dominant cost lever.")
    a.add_argument("--gate", action="append", default=[], choices=("research", "critic", "qa", "runtime"),
                   help="Each gate the route set TRUE. Repeatable. The only way to see over-assertion outside the eval corpus.")
    a.add_argument("--closure-changed",
                   help="What close_route.py altered, from its --explain output. Empty means it changed nothing, which is itself worth recording.")
    a.add_argument("--tokens", type=int,
                   help="ESTIMATE of tokens the routed work consumed, including subagents. Unverifiable by construction — record your best estimate, or omit it.")
    a.add_argument("--run-dir", help="The persona-notes directory for this run, if it was a multi-persona route. Links the entry to the raw analyses.")
    a.add_argument("--returned", type=int,
                   help="How many dispatched personas actually came back. Below --dispatched means the run was incomplete; the difference is what was lost.")
    a.add_argument("--dispatched", type=int,
                   help="How many subagents you actually spawned. A COUNT, not an estimate, and the dominant cost driver. Record 0 when you did the work inline.")
    a.add_argument("--note")
    a.set_defaults(fn=add)

    r = sub.add_parser("report", help="summarise the log")
    r.set_defaults(fn=report)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
