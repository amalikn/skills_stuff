"""Deterministic route closure: repair a proposed route so it satisfies the catalogue's invariants.

WHY THIS EXISTS. Baseline v3 tested the alternative and it failed. Stating closure as a route invariant in the orchestrator prompt, and putting a derived capability
index in front of the model, moved nothing: 34/60 against v2's 33/60, with the only extra pass being a parse flake recovering. The three-way cross-model experiment
then showed the defect is model-invariant — `unsatisfied` was 7 / 6 / 7 across DeepSeek V4 Flash, V4 Pro and Claude on an identical frozen catalogue, and ten of
twenty holdout failures occurred on BOTH production models. Asking a model to reliably perform a lookup against a finite catalogue is the same mistake
`runtime_required` already taught: that flag became reliable the moment it stopped being self-reported and started being computed.

THE DIVISION OF LABOUR:
    model  -> task understanding, decision ownership, gate judgement          (genuine judgement, no lookup)
    system -> capability closure, strength closure, runtime prerequisites     (constraint satisfaction over a finite set)

WHAT THIS DOES NOT DO. It never overrules a judgement. It does not add or change `primary_owner`, does not decide which gates are true, and does not remove anything
the model selected. It only ADDS the minimum provider needed to discharge an obligation the model itself asserted — and refuses to add anything when doing so would
break the case's team cap, because a route that violates the cap to satisfy a gate has traded one hard failure for another.

SELECTION RULE, and it is deliberately boring: among providers declaring the required capability at the required strength, prefer a SKILL over a persona (a persona
is a judgement contract and carries more weight into the route than a procedure does), then prefer the provider already related to the route (a skill whose
`personas` list intersects the selected personas), then fall back to the gate's `default_persona`, then to lexicographic order so the result is reproducible.
Reproducibility matters more than cleverness here: a repair that varies run to run cannot be regression-tested.
"""
from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
ROUTING = ROOT / "routing.toml"

STRENGTH = {"supporting": 1, "primary": 2}


def load_routing(path: Path | None = None) -> dict[str, Any]:
    return tomllib.loads((path or ROUTING).read_text())


def _providers(routing: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {r["id"]: r for r in routing.get("skills", []) + routing.get("personas", [])}


def capability_strength(route: dict[str, Any], routing: dict[str, Any], capability: str) -> int:
    """Strongest declaration of `capability` anywhere in the route. Skills and personas are pooled: a gate is an obligation on the ROUTE, and which kind of
    provider discharges it does not matter."""
    by_id = _providers(routing)
    best = 0
    for rid in list(route.get("skills") or []) + list(route.get("personas") or []):
        rec = by_id.get(rid)
        if not rec:
            continue
        if capability in rec.get("primary_capabilities", []):
            best = max(best, 2)
        elif capability in rec.get("supporting_capabilities", []):
            best = max(best, 1)
    return best


def candidates(routing: dict[str, Any], capability: str, needed: int) -> list[dict[str, Any]]:
    out = []
    for rec in routing.get("skills", []) + routing.get("personas", []):
        if capability in rec.get("primary_capabilities", []):
            have = 2
        elif capability in rec.get("supporting_capabilities", []):
            have = 1
        else:
            continue
        if have >= needed:
            out.append(rec)
    return out


def choose(cands: list[dict[str, Any]], route: dict[str, Any], routing: dict[str, Any],
           default_persona: str | None, default_skill: str | None = None) -> dict[str, Any] | None:
    """Pick the narrowest sufficient provider, deterministically. See the module docstring for why the ordering is what it is."""
    if not cands:
        return None
    persona_ids = {p["id"] for p in routing.get("personas", [])}
    selected_personas = set(route.get("personas") or [])

    def rank(rec: dict[str, Any]) -> tuple[int, int, int, str]:
        is_persona = rec["id"] in persona_ids
        related = bool(set(rec.get("personas", [])) & selected_personas) if not is_persona else rec["id"] in selected_personas
        # A tool-class skill closes the capability gate and OPENS a runtime-prerequisite obligation in the same move. Prefer a provider that discharges one
        # obligation without creating another — a route that cannot execute is not a cheaper route, it is a wrong answer delivered confidently. Found by the
        # first smoke test of this module, which closed `research` on a CTO route with `github-explorer` (needs github-access) instead of `deep-research`.
        opens_prereq = 1 if (rec.get("execution") == "tool" and rec.get("requires_any")) else 0
        # skills before personas; then providers that open no prerequisite; then related before unrelated; then stable by id
        return (1 if is_persona else 0, opens_prereq, 0 if related else 1, rec["id"])

    # The gate's canonical provider wins outright when it qualifies. Ranking heuristics are for the cases the catalogue has no opinion about; where it does have
    # one, deferring to a lexicographic tiebreak instead would be inventing a preference the catalogue already states.
    if default_skill:
        for rec in cands:
            if rec["id"] == default_skill:
                return rec
    ordered = sorted(cands, key=rank)
    # The gate's own default persona wins only if no skill can do the job at all.
    if all(r["id"] in persona_ids for r in ordered) and default_persona:
        for r in ordered:
            if r["id"] == default_persona:
                return r
    return ordered[0]


def close_route(route: dict[str, Any], routing: dict[str, Any], max_personas: int | None = None,
                tags: list[str] | None = None) -> tuple[dict[str, Any], list[str]]:
    """Return (repaired_route, actions). Pure — the input route is not mutated.

    `tags` are the task's own characteristics as JUDGED by the model — `security-sensitive`, `release-readiness`, `production-change` and so on. They are the one
    input here that is genuinely a judgement, and they belong to the model for exactly that reason. What the system does with them is mechanical: where a tag
    matches a gate's `persona_mandatory_when_tags`, the gate's persona becomes required and a skill no longer discharges it. Before this, those tags existed only
    as prose in the catalogue and nothing implemented them — which is why the corpus could require `qa-bach` on a security review while the gate said any
    validation provider would do, with no way for both to be right.
    """
    out = {**route, "skills": list(route.get("skills") or []), "personas": list(route.get("personas") or [])}
    actions: list[str] = []
    persona_ids = {p["id"] for p in routing.get("personas", [])}
    cap = max_personas if max_personas is not None else 4

    for gate in routing.get("gates", []):
        flag = gate.get("flag")
        if gate.get("computed") or not out.get(flag):
            continue
        capability = gate["required_capability"]
        needed = STRENGTH[gate["minimum_strength"]]
        escalated = bool(set(tags or []) & set(gate.get("persona_mandatory_when_tags", []))) or gate.get("persona_mandatory", False)
        persona = gate.get("default_persona")
        if escalated and persona:
            # Independence is the deliverable here, so a skill does not discharge it however well it matches the capability.
            if persona in out["personas"]:
                continue
            if len(out["personas"]) + 1 > cap:
                actions.append(f"REFUSED {flag}: escalation requires persona {persona}, which would exceed max_personas={cap}")
                continue
            out["personas"].append(persona)
            actions.append(f"escalated {flag} to persona {persona} (task tags match persona_mandatory_when_tags)")
            continue
        have = capability_strength(out, routing, capability)
        if have >= needed:
            continue
        pick = choose(candidates(routing, capability, needed), out, routing, persona, gate.get("default_skill"))
        if pick is None:
            # A gate no provider can satisfy is a CATALOGUE defect, not a route defect. The validator already refuses this state, so reaching it here means the
            # catalogue changed underneath us — say so rather than silently leaving the gate open.
            actions.append(f"UNSATISFIABLE {flag}: no provider declares {capability} at {gate['minimum_strength']} strength")
            continue
        if pick["id"] in persona_ids:
            if len(out["personas"]) + 1 > cap:
                actions.append(f"REFUSED {flag}: closing it needs persona {pick['id']}, which would exceed max_personas={cap}")
                continue
            out["personas"].append(pick["id"])
            actions.append(f"closed {flag} by adding persona {pick['id']} ({capability})")
        else:
            out["skills"].append(pick["id"])
            actions.append(f"closed {flag} by adding skill {pick['id']} ({capability})")

    # runtime_required is computed, never judged: it is true exactly when a selected skill is tool-class. Recompute it AFTER repair, because a skill added above
    # may itself be tool-class — this is the one flag the repair is allowed to overwrite.
    tool_skills = {s["id"] for s in routing.get("skills", []) if s.get("execution") == "tool"}
    computed = bool(set(out["skills"]) & tool_skills)
    if bool(out.get("runtime_required")) != computed:
        actions.append(f"recomputed runtime_required {out.get('runtime_required')} -> {computed}")
        out["runtime_required"] = computed

    unmet = [f"{sid} requires any of {by_id['requires_any']}"
             for sid in out["skills"]
             if (by_id := {s["id"]: s for s in routing.get("skills", [])}.get(sid, {})) and by_id.get("execution") == "tool" and by_id.get("requires_any")]
    for note in unmet:
        actions.append(f"runtime prerequisite to confirm: {note}")
    return out, actions


def main() -> int:
    ap = argparse.ArgumentParser(description="Repair a proposed route so it satisfies the catalogue's gates. Reads a plan as JSON on stdin, writes the repaired plan to stdout.")
    ap.add_argument("--max-personas", type=int, default=None, help="team cap the repair must not exceed")
    ap.add_argument("--explain", action="store_true", help="print the repair actions to stderr")
    ap.add_argument("--tag", action="append", default=[], help="task characteristic judged by the model, e.g. security-sensitive; repeatable")
    args = ap.parse_args()
    route = json.load(sys.stdin)
    repaired, actions = close_route(route, load_routing(), args.max_personas, args.tag)
    if args.explain:
        for a in actions:
            print(f"  {a}", file=sys.stderr)
    json.dump(repaired, sys.stdout, indent=2, sort_keys=True)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
