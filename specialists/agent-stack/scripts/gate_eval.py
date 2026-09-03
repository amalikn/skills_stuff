#!/usr/bin/env python3
"""Gate-only evaluation — the A / B1 / B2 experiment of spec 0007.

WHAT IT SEPARATES. Every scored route since the gates were defined sets all four gates true, on every model tier. Two causes produce identical output today: the
gate SEMANTICS make "true" defensible for almost any task, or gate judgement is fine alone and degrades under the instruction load of judging ownership, skills,
closure and an invariant at the same time. The integrated harness cannot tell them apart, because it only ever sees gates as a by-product of a full route.

  A   task -> three booleans. No personas, no skills, no owner, no closure, no invariant paragraph.
  B1  route given A's gates as fact.
  B2  route given the CORPUS's gates as fact — the counterfactual the normal harness can never produce.

`runtime_required` is excluded from A by construction: it is computed from the selected skills, and stage A selects none. Asking for it would measure a guess at
a value the system never wants.

WHY IT IMPORTS RATHER THAN REIMPLEMENTS. Stages B1 and B2 are scored by `evaluate_routing.score_plan` and repaired by the same `close_route` production uses. A
second scorer here would measure this script as much as the router. Nothing in this file modifies the harness, so the freeze is untouched.

SCORING. Precision, recall, F1 and specificity per gate, plus PREDICTED-POSITIVE RATE, which is the number class imbalance cannot flatter: an always-true
classifier scores recall 1.0 and looks fine on any single metric, and is caught immediately by a predicted-positive rate of 1.00. Thresholds are pre-registered
in spec 0007 and are checked here rather than eyeballed.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import evaluate_routing as er  # noqa: E402  — one scorer, one closure, one prompt builder
from close_route import close_route  # noqa: E402

JUDGED = ("research_required", "critic_required", "qa_required")

# Pre-registered in spec 0007 on 20260902_1225, BEFORE any run. Moving one requires a dated, reasoned amendment recorded before the next run.
THRESHOLDS = {"recall": 0.80, "precision": 0.75, "specificity": 0.80, "macro_f1": 0.78}
PPR_BOUNDS = (0.05, 0.95)


def gate_definitions(routing: dict[str, Any]) -> str:
    """Only the judged gates, and only what a classifier needs: the obligation, when it applies, and nothing about who would discharge it.

    Deliberately omits required_capability, minimum_strength, default_skill and default_persona. Those describe how a gate is SATISFIED, which is stage B's
    problem — including them here would reintroduce the team-construction context this stage exists to remove.
    """
    out = []
    for gate in routing.get("gates", []):
        if gate.get("flag") not in JUDGED:
            continue
        out.append(f"{gate['flag']}\n  {gate.get('description', '').strip()}")
        for key in ("set_true_when_any", "set_false_when_any", "notes"):
            value = gate.get(key)
            if isinstance(value, list):
                out.extend(f"  {key}: {v}" for v in value)
            elif value:
                out.append(f"  {key}: {value}")
    return "\n".join(out)


def prompt_a(case: dict[str, Any], gates_text: str) -> str:
    return f"""AGENT_STACK_GATE_ONLY_EVAL
You are judging THREE obligations for one task. You are not routing it, not choosing a team, and not executing it.

GATE DEFINITIONS
{gates_text}

TASK MODE: {case['mode']} TASK: {case['task']}

Return EXACTLY one JSON object and no markdown:
{{"research_required": true|false, "critic_required": true|false, "qa_required": true|false, "reason": "one sentence"}}

Judge each gate on its own definition and this task alone. A gate is true when the task genuinely carries that obligation, false when it does not. Do not set a
gate true merely because it could conceivably help, and do not set one false merely to keep the answer small."""


def prompt_b(case: dict[str, Any], gates: dict[str, bool], routing_text: str, index: str, contract: str) -> str:
    """Production routing prompt, with the gate judgement REMOVED and supplied as fact instead."""
    base = er.evaluation_prompt(case, routing_text, index, contract)
    decided = "\n".join(f"  {flag} = {str(bool(gates.get(flag))).lower()}" for flag in JUDGED)
    return (
        f"{base}\n\n"
        "GATES ALREADY DECIDED — do not re-judge them:\n"
        f"{decided}\n"
        "Echo these three values back unchanged in your JSON. Your task is the ROUTE: primary owner, personas and skills, satisfying the gates that are true.\n"
        "runtime_required remains yours to compute from the skills you select."
    )


def confusion(rows: list[dict[str, Any]], cases: dict[str, dict[str, Any]]) -> dict[str, dict[str, float]]:
    stats: dict[str, dict[str, float]] = {}
    for flag in JUDGED:
        tp = fp = tn = fn = 0
        for r in rows:
            if r.get("outcome") != "ok":
                continue
            expected, actual = bool(cases[r["case_id"]].get(flag)), bool(r["gates"].get(flag))
            tp += expected and actual
            fp += (not expected) and actual
            tn += (not expected) and (not actual)
            fn += expected and (not actual)
        n = tp + fp + tn + fn
        recall = tp / (tp + fn) if tp + fn else float("nan")
        precision = tp / (tp + fp) if tp + fp else float("nan")
        specificity = tn / (tn + fp) if tn + fp else float("nan")
        f1 = (2 * precision * recall / (precision + recall)) if precision and recall and precision + recall else 0.0
        stats[flag] = {"tp": tp, "fp": fp, "tn": tn, "fn": fn, "recall": recall, "precision": precision,
                       "specificity": specificity, "f1": f1,
                       "predicted_positive_rate": (tp + fp) / n if n else float("nan"),
                       "base_rate": (tp + fn) / n if n else float("nan")}
    return stats


def report(stats: dict[str, dict[str, float]]) -> bool:
    def fmt(v: float) -> str:
        return "  n/a" if v != v else f"{v:5.2f}"

    print(f"\n{'gate':20} {'TP':>3} {'FP':>3} {'TN':>3} {'FN':>3}  {'recall':>6} {'prec':>6} {'spec':>6} {'F1':>6} {'PPR':>6} {'base':>6}", flush=True)
    for flag, s in stats.items():
        print(f"{flag:20} {s['tp']:3.0f} {s['fp']:3.0f} {s['tn']:3.0f} {s['fn']:3.0f}  "
              f"{fmt(s['recall'])} {fmt(s['precision'])} {fmt(s['specificity'])} {fmt(s['f1'])} "
              f"{fmt(s['predicted_positive_rate'])} {fmt(s['base_rate'])}")

    macro_f1 = sum(s["f1"] for s in stats.values()) / len(stats)
    failures = []
    for flag, s in stats.items():
        for metric, floor in (("recall", THRESHOLDS["recall"]), ("precision", THRESHOLDS["precision"]),
                              ("specificity", THRESHOLDS["specificity"])):
            if not (s[metric] >= floor):
                failures.append(f"{flag}.{metric} = {s[metric]:.2f} < {floor}")
        ppr = s["predicted_positive_rate"]
        if not (PPR_BOUNDS[0] < ppr < PPR_BOUNDS[1]):
            failures.append(f"{flag}.predicted_positive_rate = {ppr:.2f} outside {PPR_BOUNDS} — DEGENERATE")
    if not (macro_f1 >= THRESHOLDS["macro_f1"]):
        failures.append(f"macro_f1 = {macro_f1:.2f} < {THRESHOLDS['macro_f1']}")

    print(f"\nmacro F1 = {macro_f1:.3f}   (pre-registered floor {THRESHOLDS['macro_f1']})", flush=True)
    if failures:
        print("\nAgainst the pre-registered thresholds: FAIL", flush=True)
        for f in failures:
            print(f"  ✗ {f}", flush=True)
    else:
        print("\nAgainst the pre-registered thresholds: PASS", flush=True)
    return not failures


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate-only evaluation (spec 0007): stage A, B1 or B2.")
    ap.add_argument("--stage", choices=("A", "B1", "B2"), required=True)
    ap.add_argument("--command", required=True)
    ap.add_argument("--cases", type=Path, default=None)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--case", action="append", default=[],
                    help="Rerun only these case ids. Use with --merge-into to repair a sweep that lost cases to a runner or parse fault.")
    ap.add_argument("--merge-into", type=Path,
                    help="Merge this run's rows into an existing artifact, replacing the rows for the same case ids and recording the repair in its provenance. "
                         "Only valid when the freeze, qualification state, command and model are unchanged — a repair is a completion of one measurement, not "
                         "a blend of two.")
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--gates-from", type=Path, help="B1 only: the stage-A result file supplying each case's gates")
    ap.add_argument("--provider", default="unspecified")
    ap.add_argument("--model", default="unspecified")
    ap.add_argument("--runner", default="unspecified")
    args = ap.parse_args()

    routing, evals = er.load_data(args.cases)
    selected, pool = er.select_cases(evals["cases"], args.case, None, args.limit)
    cases = {c["id"]: c for c in evals["cases"]}
    print(f"covered {len(selected)}/{pool} cases", flush=True)
    if len(selected) < pool:
        print(f"WARNING: partial run - {len(selected)}/{pool}. Not a measurement.", flush=True)

    supplied: dict[str, dict[str, bool]] = {}
    if args.stage == "B1":
        if not args.gates_from:
            raise SystemExit("B1 requires --gates-from pointing at a stage-A result file")
        for row in json.loads(args.gates_from.read_text())["rows"]:
            if row.get("outcome") == "ok":
                supplied[row["case_id"]] = row["gates"]

    gates_text = gate_definitions(routing)
    routing_text, index, contract = er.ROUTING.read_text(), er.capability_index(routing), er.routing_contract()

    rows, prompt_sizes, errors = [], [], 0
    for case in selected:
        if args.stage == "A":
            prompt = prompt_a(case, gates_text)
        else:
            gates = supplied.get(case["id"]) if args.stage == "B1" else {f: bool(case.get(f)) for f in JUDGED}
            if gates is None:
                # A case stage A could not answer has no gates to route against. Recording it as an error keeps B1's denominator honest rather than silently
                # substituting ground truth, which would quietly turn B1 into B2 for that case.
                rows.append({"case_id": case["id"], "outcome": "no-stage-a-result"})
                errors += 1
                continue
            prompt = prompt_b(case, gates, routing_text, index, contract)
        prompt_sizes.append(len(prompt))

        try:
            reply = er.run_command(args.command, prompt, args.timeout)
        except Exception as exc:
            rows.append({"case_id": case["id"], "outcome": "execution-error", "detail": str(exc)[:400]})
            errors += 1
            print(f"  ! {case['id']}: {str(exc)[:110]}", flush=True)
            continue

        if args.stage == "A":
            gates = {f: bool(reply.get(f)) for f in JUDGED}
            rows.append({"case_id": case["id"], "outcome": "ok", "gates": gates, "reason": str(reply.get("reason", ""))[:300]})
            expected = {f: bool(case.get(f)) for f in JUDGED}
            mark = "=" if gates == expected else "x"
            print(f"  {mark} {case['id']:32} got {[f[0] for f in JUDGED if gates[f]] or '-'}  want {[f[0] for f in JUDGED if expected[f]] or '-'}", flush=True)
        else:
            plan = er.normalize_plan(reply)
            for flag, value in gates.items():
                plan[flag] = value  # the supplied judgement is authoritative; the model was asked to echo it, not revise it
            plan, _ = close_route(plan, routing, case.get("max_personas"))
            score = er.score_plan(case, plan, routing)
            rows.append({"case_id": case["id"], "outcome": "ok", "gates": gates, "passed": score.passed,
                         "score": score.score, "hard_failures": score.hard_failures, "plan": score.plan})
            print(f"  {'PASS' if score.passed else 'FAIL'} {case['id']}: {score.score:.1f}", flush=True)

    prov = {"provider": args.provider, "model": args.model, "runner": args.runner, "command": args.command,
            "stage": args.stage, "routing_catalogue_sha": er._sha(er.ROUTING), "harness_sha": er._sha(Path(er.__file__)),
            "closure_sha": er._sha(ROOT / "scripts" / "close_route.py"),
            "eval_corpus_sha": er._sha(args.cases or er.CASES),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            # Recorded per stage so a later reader knows whether stage A's clean run said anything about stage B's load profile. It does not: B is ~10x larger.
            "prompt_chars_median": sorted(prompt_sizes)[len(prompt_sizes) // 2] if prompt_sizes else 0,
            "prompt_chars_max": max(prompt_sizes) if prompt_sizes else 0,
            "qualification_class": "transport-qualified (development sweep; realistic-payload qualification is required only for a single-use holdout)"}

    payload = {"run": prov, "rows": rows, "errors": errors, "selected": len(selected), "pool": pool}
    if args.stage == "A":
        stats = confusion(rows, cases)
        payload["metrics"] = stats
        payload["thresholds_met"] = report(stats)
    else:
        ok = [r for r in rows if r["outcome"] == "ok"]
        passed = sum(1 for r in ok if r["passed"])
        payload["passes"], payload["scored"] = passed, len(ok)
        payload["mean_score"] = round(sum(r["score"] for r in ok) / len(ok), 2) if ok else 0.0
        print(f"\nStage {args.stage}: {passed}/{len(ok)} passed; mean {payload['mean_score']}", flush=True)

    if errors:
        # Any runner failure invalidates the sweep as a measurement. Recorded in the artifact so a partial run cannot later be mistaken for a complete one.
        payload["complete"] = False
        print(f"\nINCOMPLETE: {errors} runner failure(s). This sweep is not a measurement — rerun the affected stage once the runner recovers.", flush=True)
    else:
        payload["complete"] = True

    if args.merge_into:
        base = json.loads(args.merge_into.read_text())
        repaired = {r["case_id"] for r in rows}
        kept = [r for r in base["rows"] if r["case_id"] not in repaired]
        merged = kept + rows
        base["rows"] = sorted(merged, key=lambda r: r["case_id"])
        base["errors"] = sum(1 for r in base["rows"] if r["outcome"] != "ok")
        base["complete"] = base["errors"] == 0
        # The repair is recorded, never invisible: which cases, when, and under which provenance. A merged artifact that cannot say it was merged is worse than
        # an incomplete one, because it looks like a single clean sweep.
        base.setdefault("repairs", []).append({"cases": sorted(repaired), "timestamp": prov["timestamp"], "run": prov})
        ok = [r for r in base["rows"] if r["outcome"] == "ok"]
        if args.stage != "A":
            base["passes"] = sum(1 for r in ok if r.get("passed"))
            base["scored"] = len(ok)
            base["mean_score"] = round(sum(r["score"] for r in ok) / len(ok), 2) if ok else 0.0
            print(f"\nMERGED into {args.merge_into.name}: {base['passes']}/{base['scored']} passed; mean {base['mean_score']}; "
                  f"complete={base['complete']}", flush=True)
        args.merge_into.write_text(json.dumps(base, indent=2, sort_keys=True, default=str) + "\n")
        return 0 if base["complete"] else 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n")
    print(f"\nwrote {args.output}", flush=True)
    print(f"prompt size: median {prov['prompt_chars_median']:,} chars, max {prov['prompt_chars_max']:,}")
    return 0 if payload["complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
