#!/usr/bin/env python3
"""Derive the evaluation-run index from the stored result rows, and verify it has not gone stale.

WHY THIS EXISTS. Executing holdout 24 produced evidence while MEMORY.md and SCRATCHPAD.md still said it was unexecuted. Nothing was lying; the status was
restated by hand in three places and one of them was not updated. That is the same defect class as a stale constant — a claim nothing verifies — and the fix is
the same: derive it, then check the derivation against the evidence.

DIVISION OF LABOUR. Every metric here is COMPUTED from the rows: counts, pass rate, mean, gate error classes, failure-class histogram, and the provenance the
rows already stamp. Nothing computed is ever hand-edited. The judgement fields — `purpose`, `status`, `interpretation`, `supersedes`, `notes` — are authored by
a person and preserved across regeneration, because no amount of row-scanning knows why a run was made or what it turned out to mean.

WHAT `--check` PROVES, AND WHAT IT CANNOT. It re-derives every computed field and compares. A mismatch means the index no longer describes its evidence. Result
files live in the working cache and are rebuildable, so a run whose JSONL is absent is reported as UNVERIFIABLE rather than failed — an index entry outliving
its evidence is normal and is not a defect. Silence about a missing file would be the defect.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "evals" / "runs.toml"
RESULTS = Path(os.environ.get("AGENT_STACK_RESULTS", "/Volumes/Data/_ai/_skills/skills-working-cache/agent-stack/routing-results"))

# Hard-failure strings are the harness's own vocabulary; this maps them to the failure classes an analyst actually reasons in. Anything unmatched is counted
# under `other` rather than dropped — a class silently disappearing from a histogram is how a defect stops being visible.
FAILURE_CLASSES: tuple[tuple[str, str], ...] = (
    ("wrong_owner", r"^wrong primary owner:"),
    ("missing_persona", r"^missing required persona:"),
    ("missing_skill", r"^missing required skill:"),
    ("forbidden_picks", r"^selected forbidden "),
    ("team_inflation", r"^team inflation:"),
    ("missing_gate", r"^missing gate:"),
    ("gate_unsatisfied", r"^gate \w+ unsatisfied:"),
    ("strength_insufficient", r"^capability strength insufficient"),
)
GATE_FLAGS = ("research_required", "critic_required", "qa_required", "runtime_required")
CORPUS_NAMES: dict[str, str] = {}
AUTHORED_FIELDS = ("purpose", "status", "interpretation", "supersedes", "notes")


def classify(hard: list[str]) -> dict[str, int]:
    counts = {name: 0 for name, _ in FAILURE_CLASSES}
    counts["other"] = 0
    for h in hard:
        if h.startswith("execution-error"):
            continue
        for name, pattern in FAILURE_CLASSES:
            if re.match(pattern, h):
                counts[name] += 1
                break
        else:
            counts["other"] += 1
    return counts


def derive(path: Path, corpus_cases: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Everything computable about one result file. Execution errors are excluded from the quality denominators, per rule 0008."""
    rows = []
    for line in path.read_text().splitlines():
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    errored = [r for r in rows if any(h.startswith("execution-error") for h in r.get("hard_failures", []))]
    scored = [r for r in rows if r not in errored]
    passes = sum(1 for r in scored if r.get("passed"))
    prov = next((r.get("run") or {} for r in rows if r.get("run")), {})

    classes = {name: 0 for name, _ in FAILURE_CLASSES}
    classes["other"] = 0
    fp = fn = all_true = 0
    for r in scored:
        for k, v in classify(r.get("hard_failures", [])).items():
            classes[k] += v
        # Older rows predate the two gate-error fields; recompute from the plan so historical runs are comparable to new ones.
        case = corpus_cases.get(r.get("case_id"), {})
        plan = r.get("plan") or {}
        got = [f for f in GATE_FLAGS if plan.get(f)]
        fp += len(r["gate_false_positives"]) if "gate_false_positives" in r else sum(1 for f in got if not case.get(f))
        fn += len(r["gate_false_negatives"]) if "gate_false_negatives" in r else sum(1 for f in GATE_FLAGS if case.get(f) and not plan.get(f))
        all_true += len(got) == 4

    stem = path.stem
    return {
        "run_id": stem,
        "timestamp": prov.get("timestamp", ""),
        "corpus": CORPUS_NAMES.get(prov.get("eval_corpus_sha", ""), "unresolved — corpus edited since this run"),
        "corpus_sha": prov.get("eval_corpus_sha", ""),
        "provider": prov.get("provider", "unspecified"),
        "model": prov.get("model", "unspecified"),
        "runner": prov.get("runner", "unspecified"),
        "routing_sha": prov.get("routing_catalogue_sha", ""),
        "orchestrator_sha": prov.get("orchestrator_sha", ""),
        "harness_sha": prov.get("harness_sha", ""),
        "closure_sha": prov.get("closure_sha", ""),
        "selected_cases": len(rows),
        "scored_cases": len(scored),
        "execution_errors": len(errored),
        "passes": passes,
        "pass_rate": round(passes / len(scored), 4) if scored else 0.0,
        "mean_score": round(sum(r.get("score", 0.0) for r in scored) / len(scored), 2) if scored else 0.0,
        "gate_false_negatives": fn,
        "gate_false_positives": fp,
        "all_gates_true_routes": all_true,
        "failures": {k: v for k, v in classes.items() if v},
        "evidence_jsonl": str(path),
    }


def scalar(v: Any) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, dict):
        return "{ " + ", ".join(f"{k} = {scalar(x)}" for k, x in sorted(v.items())) + " }"
    return '"' + str(v).replace('"', '\\"') + '"'


def render(records: list[dict[str, Any]]) -> str:
    head = (
        "# GENERATED by scripts/index_runs.py — do not hand-edit the computed fields.\n"
        "#\n"
        "# Every numeric field here is derived from the stored result rows and re-verified by `just runs-check`. The authored fields — purpose, status,\n"
        "# interpretation, supersedes, notes — are yours and survive regeneration. Status vocabulary: complete | partial | invalid | spent.\n"
        "#\n"
        "# This file exists because executing holdout 24 produced evidence while three hand-maintained surfaces still called it unexecuted.\n\n"
    )
    out = [head]
    for rec in records:
        out.append("[[runs]]\n")
        for key in ("run_id", "timestamp", "purpose", "status", "corpus", "corpus_sha", "provider", "model", "runner",
                    "routing_sha", "orchestrator_sha", "harness_sha", "closure_sha",
                    "selected_cases", "scored_cases", "execution_errors", "passes", "pass_rate", "mean_score",
                    "gate_false_negatives", "gate_false_positives", "all_gates_true_routes", "failures",
                    "evidence_jsonl", "evidence_log", "evidence_freeze_receipt", "interpretation", "supersedes", "notes"):
            if key in rec and rec[key] not in ("", {}, None):
                out.append(f"{key} = {scalar(rec[key])}\n")
        out.append("\n")
    return "".join(out)


def load_index() -> dict[str, dict[str, Any]]:
    if not INDEX.is_file():
        return {}
    return {r["run_id"]: r for r in tomllib.loads(INDEX.read_text()).get("runs", [])}


def corpus_names() -> dict[str, str]:
    """eval_corpus_sha -> filename, for the corpora present now.

    The rows stamp a hash, not a name, which is correct — a name is not identity. But an index a person reads needs to say WHICH corpus, and a hash that no
    longer resolves is itself information: the corpus has been edited since, so the run is not reproducible against the file in the tree today.
    """
    import hashlib
    out = {}
    for path in sorted((ROOT / "evals").glob("*-cases.toml")):
        out[hashlib.sha256(path.read_bytes()).hexdigest()[:16]] = path.name
    return out


def corpora() -> dict[str, dict[str, Any]]:
    """Every case from every corpus, keyed by id, so historical rows can be re-derived whichever corpus they came from."""
    cases: dict[str, dict[str, Any]] = {}
    for name in ("routing-cases.toml", "holdout-cases.toml"):
        path = ROOT / "evals" / name
        if path.is_file():
            for c in tomllib.loads(path.read_text()).get("cases", []):
                cases[c["id"]] = c
    return cases


def main() -> int:
    ap = argparse.ArgumentParser(description="Derive or verify the evaluation-run index.")
    ap.add_argument("--check", action="store_true", help="verify recorded metrics still match the evidence; write nothing")
    ap.add_argument("--list", action="store_true", help="print the index as a table")
    args = ap.parse_args()

    global CORPUS_NAMES
    CORPUS_NAMES = corpus_names()
    existing = load_index()
    cases = corpora()

    if args.list:
        if not existing:
            print("no runs indexed")
            return 0
        print(f"{'run_id':44} {'status':9} {'model':22} {'pass':>9} {'mean':>6} {'FP':>4} {'all4':>5}")
        for rec in sorted(existing.values(), key=lambda r: (r.get("timestamp") or "", r["run_id"])):
            rate = f"{rec.get('passes',0)}/{rec.get('scored_cases',0)}"
            print(f"{rec['run_id']:44} {rec.get('status','?'):9} {rec.get('model','?'):22} {rate:>9} "
                  f"{rec.get('mean_score',0):6.1f} {rec.get('gate_false_positives',0):4} {rec.get('all_gates_true_routes',0):5}")
        return 0

    found = {Path(p).stem: Path(p) for p in glob.glob(str(RESULTS / "*.jsonl"))}

    if args.check:
        drift, unverifiable = [], []
        for run_id, rec in sorted(existing.items()):
            path = found.get(run_id)
            if path is None:
                unverifiable.append(run_id)
                continue
            fresh = derive(path, cases)
            for key, value in fresh.items():
                if key in AUTHORED_FIELDS or key == "evidence_jsonl":
                    continue
                if rec.get(key, value) != value:
                    drift.append(f"{run_id}.{key}: index says {rec.get(key)!r}, evidence says {value!r}")
        for run_id in sorted(found):
            if run_id not in existing:
                drift.append(f"{run_id}: result file exists but is not indexed")
        if unverifiable:
            print(f"UNVERIFIABLE (evidence absent from {RESULTS}, rebuildable — not a failure): {', '.join(unverifiable)}")
        if drift:
            print("\nRUN INDEX: DRIFT")
            for d in drift:
                print(f"  ✗ {d}")
            return 1
        print(f"RUN INDEX: OK ({len(existing)} indexed, {len(existing) - len(unverifiable)} verified against evidence)")
        return 0

    records = []
    for run_id, path in sorted(found.items()):
        rec = derive(path, cases)
        prior = existing.get(run_id, {})
        for field in AUTHORED_FIELDS:
            if prior.get(field):
                rec[field] = prior[field]
        for extra in ("evidence_log", "evidence_freeze_receipt"):
            if prior.get(extra):
                rec[extra] = prior[extra]
            else:
                sidecar = path.with_suffix(".log" if extra == "evidence_log" else ".freeze.txt")
                if extra == "evidence_freeze_receipt":
                    sidecar = path.parent / f"{run_id}.freeze.txt"
                if sidecar.is_file():
                    rec[extra] = str(sidecar)
        rec.setdefault("status", "complete" if rec["execution_errors"] == 0 else "partial")
        records.append(rec)
    for run_id, rec in existing.items():
        if run_id not in found:
            records.append(rec)
    records.sort(key=lambda r: (r.get("timestamp") or "", r["run_id"]))
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(render(records))
    print(f"wrote {INDEX.relative_to(ROOT)} — {len(records)} run(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
