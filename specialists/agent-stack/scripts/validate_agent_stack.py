#!/usr/bin/env python3
"""Static Agent Stack contract validator. Uses only Python stdlib."""
from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PERSONA_SECTIONS = {
    "## Mandate",
    "## Use When",
    "## Do Not Use As Primary Owner",
    "## Decision Lens",
    "## Operating Method",
    "## Boundaries",
    "## Output Contract",
}
ORCHESTRATOR_REQUIRED = {
    "## Mandate",
    "## Routing Principles",
    "## Persona Selection Heuristics",
    "## Skill Selection Heuristics",
    "## Disagreement Protocol",
    "## Output Contract",
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def manifest_entries() -> dict[str, tuple[str, str]]:
    text = (ROOT / "manifest.yaml").read_text()
    out: dict[str, tuple[str, str]] = {}
    pat = re.compile(r"- \{id: ([^,]+), kind: ([^,]+), path: ([^,}]+)")
    for cap_id, kind, path in pat.findall(text):
        out[cap_id.strip()] = (kind.strip(), path.strip())
    return out


def main() -> int:
    errors: list[str] = []
    manifest = manifest_entries()
    if not manifest:
        fail(errors, "manifest.yaml: no capabilities parsed")

    for cap_id, (_, rel) in manifest.items():
        if not (ROOT / rel).exists():
            fail(errors, f"manifest capability {cap_id!r} points to missing {rel}")

    routing = tomllib.loads((ROOT / "routing.toml").read_text())
    evals_path = ROOT / "evals/routing-cases.toml"
    evals = tomllib.loads(evals_path.read_text()) if evals_path.exists() else {}
    routed_personas = {x["id"] for x in routing.get("personas", [])}
    routed_skills = {x["id"] for x in routing.get("skills", [])}
    manifest_personas = {k for k, (kind, _) in manifest.items() if kind == "persona"}
    manifest_skills = set(manifest) - manifest_personas

    for missing in sorted(manifest_personas - routed_personas):
        fail(errors, f"routing.toml missing persona: {missing}")
    for extra in sorted(routed_personas - manifest_personas):
        fail(errors, f"routing.toml unknown persona: {extra}")
    for missing in sorted(manifest_skills - routed_skills):
        fail(errors, f"routing.toml missing skill: {missing}")
    for extra in sorted(routed_skills - manifest_skills):
        fail(errors, f"routing.toml unknown skill: {extra}")

    for rec in routing.get("skills", []):
        if not rec.get("intents"):
            fail(errors, f"routing skill {rec['id']} has no intents")
        if rec.get("execution") not in {"analysis", "tool"}:
            fail(errors, f"routing skill {rec['id']} has invalid execution class")
        for persona in rec.get("personas", []):
            if persona not in manifest_personas:
                fail(errors, f"routing skill {rec['id']} references unknown persona {persona}")

    # Capability registry. Capabilities are declared once and referenced by skills, personas and gates, so every reference is a chance for a typo to create a
    # capability that exists in exactly one place and therefore satisfies nothing. All three reference sites are checked against the registry.
    capability_ids: set[str] = set()
    for rec in routing.get("capabilities", []):
        cid = rec.get("id")
        if cid in capability_ids:
            fail(errors, f"capability {cid} is declared twice")
        if not rec.get("description"):
            fail(errors, f"capability {cid} has no description")
        capability_ids.add(cid)

    primary_by_id: dict[str, set[str]] = {}
    for kind, key in (("skill", "skills"), ("persona", "personas")):
        for rec in routing.get(key, []):
            rid = rec["id"]
            prim = rec.get("primary_capabilities")
            supp = rec.get("supporting_capabilities")
            if prim is None or supp is None:
                # An un-annotated provider silently provides nothing, which reads in a failure report as a routing mistake by the model rather than a gap in the
                # catalogue. Partial annotation is therefore worse than none.
                fail(errors, f"{kind} {rid} declares no primary_capabilities/supporting_capabilities")
                continue
            primary_by_id[rid] = set(prim)
            for cap in list(prim) + list(supp):
                if cap not in capability_ids:
                    fail(errors, f"{kind} {rid} references unknown capability {cap}")
            overlap = set(prim) & set(supp)
            if overlap:
                fail(errors, f"{kind} {rid} declares {sorted(overlap)} as both primary and supporting")
            # `tool-execution` is not a judgement about a skill, it is a restatement of its execution class. Allowing the two to disagree would let the runtime
            # gate and the capability resolver give different answers about the same skill.
            if kind == "skill":
                is_tool = rec.get("execution") == "tool"
                declares = "tool-execution" in prim
                if is_tool and not declares:
                    fail(errors, f"skill {rid} has execution = \"tool\" but does not declare tool-execution")
                if declares and not is_tool:
                    fail(errors, f"skill {rid} declares tool-execution but its execution class is {rec.get('execution')!r}")
            elif "tool-execution" in set(prim) | set(supp):
                fail(errors, f"persona {rid} declares tool-execution; only tool-class skills carry it")

    # Gate definitions carry cross-references — a capability skill list, a default persona, and the flag the eval corpus asserts. None of these were checked
    # when gates were introduced, so a typo or a skill that exists globally but not in this catalogue would ship silently. (`test-driven-development` was
    # exactly that case during authoring: a real skill in the wider environment, absent from Agent Stack.)
    GATE_FLAGS = {"research_required", "critic_required", "qa_required", "runtime_required"}
    seen_flags: set[str] = set()
    for gate in routing.get("gates", []):
        gid = gate.get("id", "<unnamed>")
        flag = gate.get("flag")
        if flag not in GATE_FLAGS:
            fail(errors, f"gate {gid} declares unknown flag {flag!r}")
        elif flag in seen_flags:
            fail(errors, f"gate {gid} duplicates flag {flag!r}; one gate owns one flag")
        else:
            seen_flags.add(flag)
        cap = gate.get("required_capability")
        if cap not in capability_ids:
            fail(errors, f"gate {gid} requires unknown capability {cap!r}")
        if "satisfied_by_skills" in gate:
            # The hand-maintained list was replaced by capability resolution. Leaving one behind means two taxonomies again, and the stale one wins wherever a
            # reader trusts it — so its mere presence is the failure, not its contents.
            fail(errors, f"gate {gid} still carries satisfied_by_skills; gates resolve through required_capability now")
        strength = gate.get("minimum_strength")
        if gate.get("computed"):
            if strength is not None:
                fail(errors, f"computed gate {gid} declares minimum_strength; it resolves from the execution class, not from strength")
        elif strength not in ("primary", "supporting"):
            fail(errors, f"gate {gid} declares invalid minimum_strength {strength!r}")
        elif not any(cap in prov for prov in primary_by_id.values()):
            # A gate no provider can satisfy at primary strength is unsatisfiable by construction: every route asserting it fails, and nothing in the catalogue
            # says why.
            fail(errors, f"gate {gid} requires {cap!r} at primary strength but no skill or persona provides it")
        persona = gate.get("default_persona")
        if persona is not None and persona not in routed_personas:
            fail(errors, f"gate {gid} default_persona references unknown persona {persona}")
        # A gate the model must judge needs stated triggers; a computed gate does not.
        if not gate.get("computed") and not gate.get("set_true_when_any"):
            fail(errors, f"gate {gid} is model-judged but states no set_true_when_any conditions")
        if gate.get("persona_mandatory") and persona is None:
            fail(errors, f"gate {gid} sets persona_mandatory but names no default_persona")
    if routing.get("gates") and seen_flags != GATE_FLAGS:
        fail(errors, f"gates do not cover every eval flag; missing: {sorted(GATE_FLAGS - seen_flags)}")

    # Route invariants are the catalogue's only statements about what makes a finished route INVALID rather than merely suboptimal. An invariant that names no
    # repair is a complaint; one that names no violation label cannot be tied back to a scored failure, which is how a rule quietly stops being measurable.
    VIOLATIONS = {"gate-unsatisfied", "capability-strength-insufficient", "runtime-prerequisite-missing"}
    seen_invariants: set[str] = set()
    for inv in routing.get("route_invariants", []):
        iid = inv.get("id", "<unnamed>")
        if iid in seen_invariants:
            fail(errors, f"route invariant {iid} is declared twice")
        seen_invariants.add(iid)
        for field in ("statement", "applies_to", "repair"):
            if not inv.get(field):
                fail(errors, f"route invariant {iid} is missing {field}")
        if inv.get("violation") not in VIOLATIONS:
            fail(errors, f"route invariant {iid} names violation {inv.get('violation')!r}, which the scorer never reports")

    # Precedence rules are only useful if both branches resolve to real personas and the two branches actually differ. A rule naming the same persona twice, or
    # naming one that was renamed out of the catalogue, reads as guidance while deciding nothing — the exact failure mode precedence exists to remove.
    seen_precedence: set[str] = set()
    for rule in routing.get("precedence", []):
        rid = rule.get("id", "<unnamed>")
        if rid in seen_precedence:
            fail(errors, f"precedence rule {rid} is declared twice")
        seen_precedence.add(rid)
        owners = [rule.get("owner_a"), rule.get("owner_b")]
        for owner in owners:
            if owner not in routed_personas:
                fail(errors, f"precedence rule {rid} references unknown persona {owner}")
        if owners[0] == owners[1]:
            fail(errors, f"precedence rule {rid} names the same persona on both branches; it decides nothing")
        for field in ("applies_when", "discriminator", "owner_a_when", "owner_b_when"):
            if not rule.get(field):
                fail(errors, f"precedence rule {rid} is missing {field}")

    # ONE persona model, not two. `[[routing_rules]]` are advisory keyword hints; mandatory-ness lives in gates, precedence and invariants. A `require_personas`
    # here recreates the contradiction found on 2026-09-01 — `material-independent-challenge` requiring critic-munger while `critic-gate` said the persona was
    # optional, in the same file, both fed to the model. A `*-gate` id here recreates the name collision that hid it.
    for rule in routing.get("routing_rules", []):
        rid = rule.get("id", "<unnamed>")
        if "require_personas" in rule:
            fail(errors, f"routing rule {rid} uses require_personas; routing rules are advisory — mandatory routing lives in gates, precedence and invariants")
        if rid.endswith("-gate"):
            fail(errors, f"routing rule {rid} is named like a gate but is not one; rename it to avoid colliding with the [[gates]] table")
        for persona in rule.get("prefer_personas", []):
            if persona not in routed_personas:
                fail(errors, f"routing rule {rid} prefers unknown persona {persona}")

    # The behavioural eval builds its prompt from a marked block inside the orchestrator skill, so production and eval cannot state different routing contracts.
    # Deleting or renaming the markers would silently return the eval to scoring a contract nobody uses — the drift this arrangement exists to prevent.
    orchestrator = ROOT / "skills" / "skill-agent-stack" / "SKILL.md"
    if orchestrator.exists():
        text = orchestrator.read_text()
        if "<!-- BEGIN eval-routing-contract -->" not in text or "<!-- END eval-routing-contract -->" not in text:
            fail(errors, "skills/skill-agent-stack/SKILL.md is missing the eval-routing-contract block that scripts/evaluate_routing.py builds its prompt from")

    # `runtime_required` is COMPUTED from the selected skills' execution class, so a case asserting it true is really asserting that a tool-class skill must be
    # selected. Asserting the flag while only PREFERRING the skill that causes it is a case contradicting itself: it hard-requires an outcome whose sole cause it
    # treats as optional. Found 2026-09-01 in 4 of the 7 runtime_required cases, and it made net-dns-migration unfixable by any route the case permitted.
    tool_skills = {s["id"] for s in routing.get("skills", []) if s.get("execution") == "tool"}
    for case in evals.get("cases", []):
        if case.get("runtime_required") and not (set(case.get("required_skills", [])) & tool_skills):
            fail(errors, f"case {case['id']} asserts runtime_required but requires no tool-class skill; the assertion is unearned")

    for p in sorted((ROOT / "personas").glob("*.md")):
        # The folder's own index is navigation, not a judgement contract. Added 20260903 with personas/README.md: without it the validator demanded a Mandate
        # and an Output Contract from the index, which is the same category error as asking a table of contents to have a thesis.
        if p.name == "README.md":
            continue
        text = p.read_text()
        required = ORCHESTRATOR_REQUIRED if p.name == "orchestrator-follett.md" else REQUIRED_PERSONA_SECTIONS
        for section in required:
            if section not in text:
                fail(errors, f"{p.relative_to(ROOT)} missing {section}")
        if len(text.splitlines()) < 60:
            fail(errors, f"{p.relative_to(ROOT)} is too thin (<60 lines)")

    for p in sorted((ROOT / "skills").glob("*/SKILL.md")):
        text = p.read_text()
        if not text.startswith("---\n"):
            fail(errors, f"{p.relative_to(ROOT)} missing YAML frontmatter")
        if "name:" not in text[:1500] or "description:" not in text[:2500]:
            fail(errors, f"{p.relative_to(ROOT)} missing name/description metadata")

    # Validate only concrete local resource links outside fenced code. URLs and example placeholders are ignored.
    concrete_skills = {"startup-business-models", "deep-research"}
    for skill in concrete_skills:
        p = ROOT / "skills" / skill / "SKILL.md"
        text = re.sub(r"```.*?```", "", p.read_text(), flags=re.S)
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            bare = target.split("#", 1)[0]
            if bare and not (p.parent / bare).resolve().exists():
                fail(errors, f"{p.relative_to(ROOT)} broken local link: {target}")

    if errors:
        print("Agent Stack validation: FAIL")
        for e in errors:
            print(f"- {e}")
        return 1
    print(f"Agent Stack validation: PASS ({len(manifest)} capabilities; {len(routed_personas)} personas; {len(routed_skills)} skills)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
