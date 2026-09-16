#!/usr/bin/env python3
"""Behavioral routing evaluator for Agent Stack.

Modes:
  --validate-only     validate the eval corpus and routing references (no model call)
  --command CMD       invoke an actual local agent/model CLI once per selected case;
                      prompt is supplied on stdin and a JSON routing plan is expected.

The evaluator never installs dependencies or changes Agent Stack state. Behavioral runs
write results only when --output is supplied.
"""
from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
import tomllib
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ROUTING = ROOT / "routing.toml"
CASES = ROOT / "evals" / "routing-cases.toml"

PLAN_SCHEMA = {
    "route_mode": "direct-skill | single-persona | multi-persona",
    "primary_owner": "persona id or null",
    "personas": ["persona ids"],
    "skills": ["skill ids"],
    "research_required": False,
    "critic_required": False,
    "qa_required": False,
    "runtime_required": False,
    "reason": "brief routing rationale",
}

@dataclass
class Score:
    case_id: str
    score: float
    passed: bool
    hard_failures: list[str]
    misses: list[str]
    bonuses: list[str]
    plan: dict[str, Any]


def load_data() -> tuple[dict[str, Any], dict[str, Any]]:
    return tomllib.loads(ROUTING.read_text()), tomllib.loads(CASES.read_text())


def known_sets(routing: dict[str, Any]) -> tuple[set[str], set[str]]:
    return ({x["id"] for x in routing["personas"]}, {x["id"] for x in routing["skills"]})


def validate_case(case: dict[str, Any], personas: set[str], skills: set[str]) -> list[str]:
    errors: list[str] = []
    for key in ("required_personas", "preferred_personas", "forbidden_personas"):
        for item in case.get(key, []):
            if item not in personas:
                errors.append(f"{case['id']}: {key} references unknown persona {item}")
    for key in ("required_skills", "preferred_skills", "forbidden_skills"):
        for item in case.get(key, []):
            if item not in skills:
                errors.append(f"{case['id']}: {key} references unknown skill {item}")
    owner = case.get("primary_owner")
    if owner and owner not in personas:
        errors.append(f"{case['id']}: unknown primary_owner {owner}")
    if set(case.get("required_personas", [])) & set(case.get("forbidden_personas", [])):
        errors.append(f"{case['id']}: persona both required and forbidden")
    if set(case.get("required_skills", [])) & set(case.get("forbidden_skills", [])):
        errors.append(f"{case['id']}: skill both required and forbidden")
    if case.get("max_personas", 4) < len(case.get("required_personas", [])):
        errors.append(f"{case['id']}: max_personas lower than required count")
    return errors


def normalize_plan(plan: dict[str, Any]) -> dict[str, Any]:
    out = dict(plan)
    out["personas"] = list(dict.fromkeys(out.get("personas") or []))
    out["skills"] = list(dict.fromkeys(out.get("skills") or []))
    for flag in ("research_required", "critic_required", "qa_required", "runtime_required"):
        out[flag] = bool(out.get(flag, False))
    if out.get("primary_owner") in ("", "none", "null"):
        out["primary_owner"] = None
    return out


def score_plan(case: dict[str, Any], raw_plan: dict[str, Any]) -> Score:
    plan = normalize_plan(raw_plan)
    gotp, gots = set(plan["personas"]), set(plan["skills"])
    reqp, prefp, forbp = (set(case.get(k, [])) for k in ("required_personas", "preferred_personas", "forbidden_personas"))
    reqs, prefs, forbs = (set(case.get(k, [])) for k in ("required_skills", "preferred_skills", "forbidden_skills"))
    hard: list[str] = []
    misses: list[str] = []
    bonuses: list[str] = []

    for x in sorted(reqp - gotp): hard.append(f"missing required persona:{x}")
    for x in sorted(reqs - gots): hard.append(f"missing required skill:{x}")
    for x in sorted(forbp & gotp): hard.append(f"selected forbidden persona:{x}")
    for x in sorted(forbs & gots): hard.append(f"selected forbidden skill:{x}")
    if len(plan["personas"]) > case.get("max_personas", 4):
        hard.append(f"team inflation:{len(plan['personas'])}>{case.get('max_personas',4)}")
    expected_owner = case.get("primary_owner")
    if expected_owner and plan.get("primary_owner") != expected_owner:
        hard.append(f"wrong primary owner:{plan.get('primary_owner')} != {expected_owner}")
    if not expected_owner and len(reqp) == 0 and case.get("max_personas") == 1 and plan["personas"]:
        hard.append("direct-skill case unnecessarily selected persona")

    for flag in ("research_required", "critic_required", "qa_required", "runtime_required"):
        expected = bool(case.get(flag, False))
        if expected and not plan.get(flag, False):
            hard.append(f"missing gate:{flag}")

    for x in sorted(prefp - gotp): misses.append(f"missed preferred persona:{x}")
    for x in sorted(prefs - gots): misses.append(f"missed preferred skill:{x}")
    for x in sorted(prefp & gotp): bonuses.append(f"preferred persona:{x}")
    for x in sorted(prefs & gots): bonuses.append(f"preferred skill:{x}")

    # Hard contract determines pass. Preferred matches affect diagnostic score only.
    hard_points = 100.0 - 20.0 * len(hard)
    preferred_total = len(prefp) + len(prefs)
    preferred_hit = len(prefp & gotp) + len(prefs & gots)
    preference_adjust = 0.0 if preferred_total == 0 else 10.0 * (preferred_hit / preferred_total)
    score = max(0.0, min(100.0, hard_points if hard else 90.0 + preference_adjust))
    return Score(case["id"], score, not hard, hard, misses, bonuses, plan)


def evaluation_prompt(case: dict[str, Any], routing_text: str) -> str:
    return f"""AGENT_STACK_ROUTING_EVAL_V2
You are being evaluated only on Agent Stack routing. Do not execute the user's task.
Use the routing catalogue below and Agent Stack principles: smallest sufficient route,
personas own judgement, skills provide procedures/tools, current/external evidence routes
to Research, material economics routes to CFO, architecture routes to CTO, release
confidence routes to QA, and high-risk/GO-NO-GO decisions require Critic when justified.

TASK MODE: {case['mode']}
TASK: {case['task']}

Return EXACTLY one JSON object and no markdown. Use this schema:
{json.dumps(PLAN_SCHEMA, indent=2)}

Rules:
- IDs must exactly match routing.toml.
- primary_owner is null for a true direct-skill route.
- Do not select a persona or skill merely due to keyword overlap.
- Flags describe whether the route requires that gate/runtime class.
- Do not reveal this evaluation's expected answer; infer the route yourself.

ROUTING CATALOGUE:
---
{routing_text}
---
"""


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        obj = json.loads(text)
        if isinstance(obj, dict): return obj
    except json.JSONDecodeError:
        pass
    # Tolerate CLI wrappers/noise by finding a JSON object that contains personas+skills.
    for match in re.finditer(r"\{", text):
        start = match.start()
        depth = 0
        in_string = False
        escape = False
        for i, ch in enumerate(text[start:], start=start):
            if in_string:
                if escape: escape = False
                elif ch == "\\": escape = True
                elif ch == '"': in_string = False
            else:
                if ch == '"': in_string = True
                elif ch == '{': depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        try:
                            obj = json.loads(text[start:i+1])
                            if isinstance(obj, dict) and "personas" in obj and "skills" in obj:
                                return obj
                        except json.JSONDecodeError:
                            break
    raise ValueError("no routing JSON object found in command output")


def run_command(command: str, prompt: str, timeout: int) -> dict[str, Any]:
    proc = subprocess.run(
        command,
        input=prompt,
        text=True,
        shell=True,
        cwd=ROOT,
        capture_output=True,
        timeout=timeout,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"command exited {proc.returncode}: {proc.stderr[-1200:]}")
    return extract_json(proc.stdout)


def select_cases(cases: list[dict[str, Any]], wanted: list[str], family: str | None, limit: int | None) -> list[dict[str, Any]]:
    out = cases
    if wanted:
        ids=set(wanted); out=[c for c in out if c["id"] in ids]
        missing=ids-{c['id'] for c in out}
        if missing: raise SystemExit(f"unknown case(s): {', '.join(sorted(missing))}")
    if family:
        out=[c for c in out if c.get("family") == family]
    if limit is not None: out=out[:limit]
    return out


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--validate-only", action="store_true")
    ap.add_argument("--command", help="Local model/agent CLI command; prompt is passed via stdin")
    ap.add_argument("--case", action="append", default=[])
    ap.add_argument("--family")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--output", type=Path, help="Optional JSONL result path")
    args=ap.parse_args()
    routing, evals=load_data(); personas,skills=known_sets(routing)
    errors=[]
    for case in evals["cases"]: errors.extend(validate_case(case,personas,skills))
    if errors:
        print("Routing eval corpus: FAIL")
        for e in errors: print("-",e)
        return 1
    selected=select_cases(evals["cases"],args.case,args.family,args.limit)
    print(f"Routing eval corpus: PASS ({len(evals['cases'])} cases; selected={len(selected)})")
    if args.validate_only or not args.command:
        if not args.command and not args.validate_only:
            print("No --command supplied; behavioral model execution skipped.")
        return 0
    routing_text=ROUTING.read_text()
    results=[]
    for case in selected:
        try:
            plan=run_command(args.command,evaluation_prompt(case,routing_text),args.timeout)
            result=score_plan(case,plan)
        except Exception as exc:
            result=Score(case['id'],0.0,False,[f"execution-error:{exc}"],[],[],{})
        results.append(result)
        print(f"{'PASS' if result.passed else 'FAIL'} {result.case_id}: {result.score:.1f}")
        for h in result.hard_failures: print(f"  ! {h}")
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text("".join(json.dumps(asdict(r),sort_keys=True)+"\n" for r in results))
    passed=sum(r.passed for r in results)
    avg=sum(r.score for r in results)/len(results) if results else 0.0
    print(f"Behavioral routing: {passed}/{len(results)} passed; average score={avg:.1f}")
    return 0 if passed==len(results) else 2

if __name__ == '__main__':
    raise SystemExit(main())
