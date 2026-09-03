#!/usr/bin/env python3
"""Behavioral routing evaluator for Agent Stack.

Modes:
  --validate-only     validate the eval corpus and routing references (no model call)
  --command CMD       invoke an actual local agent/model CLI once per selected case;
                      prompt is supplied on stdin and a JSON routing plan is expected.

The evaluator never installs dependencies or changes Agent Stack state. Behavioral runs write results only when --output is supplied.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import hashlib
import json
import re
import shlex
import subprocess
import sys
import tomllib
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from close_route import close_route  # noqa: E402  — sibling module; the harness and the runtime share one closure implementation by design

GATE_FLAGS = ("research_required", "critic_required", "qa_required", "runtime_required")

ROOT = Path(__file__).resolve().parents[1]
ROUTING = ROOT / "routing.toml"
CASES = ROOT / "evals" / "routing-cases.toml"

PLAN_SCHEMA = {
    "route_mode": "direct-skill | single-persona | multi-persona",
    "primary_owner": "persona id or null",
    "personas": ["persona ids"],
    "skills": ["skill ids"],
    # Descriptive placeholders, not literal `False`. A schema showing all four flags false is serialised straight into the prompt and anchors the answer before
    # the model reasons — measured as the single largest failure class in the 2026-09-01 baseline (43 of 62 hard failures were gate misses).
    "research_required": "true|false — see [[gates]] in the routing catalogue",
    "critic_required": "true|false — see [[gates]] in the routing catalogue",
    "qa_required": "true|false — see [[gates]] in the routing catalogue",
    "runtime_required": "true|false — true if any selected skill has execution=tool",
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
    # Tracked SEPARATELY rather than folded into one gate-error count, because the two are not the same defect and must not be traded off against each other in
    # analysis: a false negative means a required gate never fired, a false positive means the route carried a gate it did not need. Both land in every stored
    # row, so a baseline can be re-analysed for over-assertion without re-running a model.
    gate_false_negatives: list[str] = field(default_factory=list)
    gate_false_positives: list[str] = field(default_factory=list)


def load_data(cases: Path | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    """Catalogue plus one corpus. `cases` selects which corpus; the default is the frozen development 60.

    A second corpus is a file, not a fork of this harness — the unseen holdout must be scored by exactly the scorer the baselines were scored by, or it measures
    the scorer as much as the router.
    """
    return tomllib.loads(ROUTING.read_text()), tomllib.loads((cases or CASES).read_text())


ORCHESTRATOR = ROOT / "skills" / "orchestrator" / "SKILL.md"


def _sha(path: Path) -> str | None:
    """Short content hash, or None when the file is absent."""
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def run_provenance(args: argparse.Namespace) -> dict[str, Any]:
    """Identity of THIS run, stamped into every result row.

    Without this a run is not comparable to another: a silent provider fallback, an edited routing catalogue, or a changed corpus all move the scores while the
    output looks identical. Observed 2026-09-01 — Hermes' fallback chain is deepseek -> a local Ollama model, and nothing in the results would have revealed it
    had the fallback fired.

    provider/model/runner cannot be detected here: the harness only knows an opaque shell command, deliberately, so that no provider's syntax is hard-coded.
    They are operator-supplied and default to "unspecified" with a warning. The hashes are computed, so the parts that can be verified always are.
    """
    return {
        "provider": args.provider or "unspecified",
        "model": args.model or "unspecified",
        "runner": args.runner or "unspecified",
        "command": args.command,
        "routing_catalogue_sha": _sha(ROUTING),
        # The corpus ACTUALLY used, not the default one. A holdout run that stamped the development corpus's hash would be indistinguishable from a run of the
        # development corpus, which is the one confusion this whole stamp exists to prevent. `check_freeze.py` passes no `cases`, so it keeps verifying the
        # frozen 60 regardless of what any given run measured.
        "eval_corpus_sha": _sha(getattr(args, "cases", None) or CASES),
        "orchestrator_sha": _sha(ORCHESTRATOR),
        # Which stamped files actually reach the model. Before 2026-09-02 orchestrator_sha recorded a file the prompt never read, so editing it raised a
        # provenance alarm while proving nothing — a stamp should cover inputs, not neighbours. The orchestrator is now a genuine input via routing_contract().
        "prompt_inputs": ["routing_catalogue_sha", "eval_corpus_sha", "orchestrator_sha", "harness_sha"],
        "harness_sha": _sha(Path(__file__)),
        # Closure reaches the SCORE rather than the prompt, which is why it is stamped but absent from prompt_inputs. Under --repair it rewrites the route
        # before scoring — measured at +13 cases on the frozen 60 — so a run is not reproducible without knowing which version of it ran. Added 2026-09-02 on
        # the same reasoning as rule 0009: an input that moves the number is provenance whether or not the model ever sees it.
        "closure_sha": _sha(ROOT / "scripts" / "close_route.py"),
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    }


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
    for flag in GATE_FLAGS:
        out[flag] = bool(out.get(flag, False))
    if out.get("primary_owner") in ("", "none", "null"):
        out["primary_owner"] = None
    return out


def tool_skills(routing: dict[str, Any]) -> set[str]:
    return {s["id"] for s in routing.get("skills", []) if s.get("execution") == "tool"}


def deterministic_gates(plan: dict[str, Any], routing: dict[str, Any]) -> tuple[dict[str, bool], list[str]]:
    """Compute what the system can compute, instead of trusting the model's self-report.

    Only `runtime_required` is fully mechanical: it is true exactly when a selected skill declares `execution = "tool"`. Asking a model to self-report it is
    asking it to do a lookup, which the 2026-09-01 baseline shows it does unreliably. The model's own value is kept as a diagnostic — a mismatch says something
    about prompt-following, not about routing quality, so it must not be scored as a routing error.
    """
    computed = {"runtime_required": bool(set(plan["skills"]) & tool_skills(routing))}
    notes: list[str] = []
    for flag, value in computed.items():
        if bool(plan.get(flag)) != value:
            notes.append(f"self-reported {flag}={plan.get(flag)} but route computes {value}")
    return computed, notes


def capability_strength(plan: dict[str, Any], routing: dict[str, Any], capability: str) -> int:
    """Strongest declaration of `capability` anywhere in the route. none=0, supporting=1, primary=2.

    Skills and personas are pooled deliberately: a gate is an obligation on the ROUTE, and it does not matter which kind of provider discharges it.
    """
    by_id: dict[str, dict[str, Any]] = {r["id"]: r for r in routing.get("skills", []) + routing.get("personas", [])}
    strength = 0
    for rid in list(plan["skills"]) + list(plan["personas"]):
        rec = by_id.get(rid)
        if not rec:
            continue
        if capability in rec.get("primary_capabilities", []):
            strength = max(strength, 2)
        elif capability in rec.get("supporting_capabilities", []):
            strength = max(strength, 1)
    return strength


def gate_capability_gaps(
    case: dict[str, Any], plan: dict[str, Any], routing: dict[str, Any], already_failed: set[str]
) -> list[str]:
    """For each gate the CASE says applies, check the route actually carries the capability to discharge it, at the strength the gate demands.

    Deliberately scored against the case's expectation, not the model's self-report, so a model cannot pass by declaring a gate false. Resolution is by
    capability rather than by a hand-written skill list: the list was a second copy of the taxonomy that could drift from the skills' own metadata.

    `capability-strength-insufficient` is reported separately from `gate-unsatisfied` because they call for opposite fixes — the first says the route brought
    something adjacent and the strength rule is what rejected it, which is a judgement worth being able to audit; the second says it brought nothing at all.

    NOTE: `persona_mandatory` is not enforced here, and as of 2026-09-01 no gate sets it unconditionally — the catalogue/corpus contradiction it created is
    resolved at the source rather than papered over in the scorer. Every gate now escalates to its persona only on its own `persona_mandatory_when_tags`, which
    the corpus does not carry as structured data; enforcing those here would be enforcing a judgement the corpus cannot express.
    """
    gaps: list[str] = []
    for gate in routing.get("gates", []):
        flag = gate.get("flag")
        if not case.get(flag) or gate.get("computed"):
            continue
        # A route that never set the flag is already penalised for missing the gate; it will trivially also lack the capability. Reporting both double-counts
        # one defect and erodes trust in the score — measured on the 2026-09-01 baseline, it produced 17 "unsatisfied" failures alongside 18 near-identical
        # "missing gate" ones and dropped the mean by 10 points for no new information. The capability check earns its place only where the model got the
        # JUDGEMENT right and then failed to equip the route, which is the genuinely new signal.
        if flag in already_failed:
            continue
        cap = gate["required_capability"]
        needed = {"supporting": 1, "primary": 2}[gate["minimum_strength"]]
        actual = capability_strength(plan, routing, cap)
        if actual >= needed:
            continue
        if actual > 0:
            gaps.append(f"capability strength insufficient for {flag}: {cap} present only as supporting, gate requires {gate['minimum_strength']}")
        else:
            gaps.append(f"gate {flag} unsatisfied: no route member provides {cap}")
    return gaps


def tool_prerequisite_notes(plan: dict[str, Any], routing: dict[str, Any]) -> list[str]:
    """Selected tool-class skills declare prerequisites; a route that ignores them is not actually runnable."""
    by_id = {s["id"]: s for s in routing.get("skills", [])}
    out: list[str] = []
    for sid in plan["skills"]:
        rec = by_id.get(sid)
        if rec and rec.get("execution") == "tool" and rec.get("requires_any"):
            out.append(f"tool skill {sid} requires any of {rec['requires_any']}")
    return out


def score_plan(case: dict[str, Any], raw_plan: dict[str, Any], routing: dict[str, Any] | None = None) -> Score:
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
    # NOT scored: "a direct-skill case selected a persona". A direct route's real contract is the right skill, no forbidden persona, and no team — all three
    # are already hard-scored above (required_skills, forbidden_personas, max_personas). Adding an absent-primary_owner rule on top punished the one accountable
    # owner as harshly as a four-persona committee, which is the opposite of what the direct-adversarial family exists to measure. Skill + one owning persona is
    # an acceptable direct route; skill + a team is not, and max_personas = 1 catches that.

    # Gate flags. `runtime_required` is scored against the COMPUTED value rather than the model's self-report, because it is a lookup against each selected
    # skill's execution class, not a judgement. The other three remain judgements and are scored as reported.
    computed: dict[str, bool] = {}
    if routing is not None:
        computed, mismatch_notes = deterministic_gates(plan, routing)
        misses.extend(mismatch_notes)
    # Gate errors are scored ASYMMETRICALLY and deliberately so. A false negative — the case requires the gate, the route did not fire it — is a hard failure
    # worth -20 and decides pass/fail, because the route omits an obligation. A false positive — the route fired a gate the case does not require — is a soft
    # -5 and never decides pass/fail, because over-routing is wasteful rather than wrong. Before 2026-09-02 the scorer only penalised the first, so setting all
    # four flags true cost nothing and dominated every false negative for free; Claude did exactly that on `market-size`. Equal weighting would be the opposite
    # error, making a cautious route indistinguishable from one that skipped a required gate. `runtime_required` is included on both sides using the same
    # COMPUTED value the false-negative branch uses, so an over-assertion there means the route selected a tool-class skill the case does not call for.
    gate_false_negatives: list[str] = []
    gate_false_positives: list[str] = []
    for flag in GATE_FLAGS:
        expected = bool(case.get(flag, False))
        actual = computed.get(flag, plan.get(flag, False))
        if expected and not actual:
            hard.append(f"missing gate:{flag}")
            gate_false_negatives.append(flag)
        elif actual and not expected:
            gate_false_positives.append(flag)
            misses.append(f"over-asserted gate:{flag}")

    if routing is not None:
        missed_flags = {h.split(":", 1)[1] for h in hard if h.startswith("missing gate:")}
        hard.extend(gate_capability_gaps(case, plan, routing, missed_flags))
        misses.extend(tool_prerequisite_notes(plan, routing))

    for x in sorted(prefp - gotp): misses.append(f"missed preferred persona:{x}")
    for x in sorted(prefs - gots): misses.append(f"missed preferred skill:{x}")
    for x in sorted(prefp & gotp): bonuses.append(f"preferred persona:{x}")
    for x in sorted(prefs & gots): bonuses.append(f"preferred skill:{x}")

    # Hard contract determines pass. Preferred matches affect diagnostic score only.
    hard_points = 100.0 - 20.0 * len(hard)
    preferred_total = len(prefp) + len(prefs)
    preferred_hit = len(prefp & gotp) + len(prefs & gots)
    preference_adjust = 0.0 if preferred_total == 0 else 10.0 * (preferred_hit / preferred_total)
    # Applied to BOTH branches and to the score only. `passed` still reads `not hard`, so a clean route that over-asserts scores lower and still passes — which
    # is the intended shape: over-assertion is a quality signal, not a contract breach.
    soft_penalty = 5.0 * len(gate_false_positives)
    score = max(0.0, min(100.0, (hard_points if hard else 90.0 + preference_adjust) - soft_penalty))
    return Score(case["id"], score, not hard, hard, misses, bonuses, plan, gate_false_negatives, gate_false_positives)




CONTRACT_START = "<!-- BEGIN eval-routing-contract -->"
CONTRACT_END = "<!-- END eval-routing-contract -->"


def routing_contract() -> str:
    """The routing principles the eval states, read from the PRODUCTION orchestrator skill rather than kept as a second copy here.

    Until 2026-09-02 this text lived in `evaluation_prompt` as a literal. That meant the behavioural eval could score a contract production did not use, and
    nothing would detect the divergence — an eval drifting from the artefact it measures is worse than no eval, because it reports confidence about the wrong
    thing. Sourcing it from `skills/orchestrator/SKILL.md` makes the two impossible to separate, and makes `orchestrator_sha` a genuine prompt input rather than
    an advisory neighbour.

    Missing markers raise rather than fall back to a default: a silent fallback would restore exactly the drift this removes.
    """
    text = ORCHESTRATOR.read_text()
    try:
        body = text.split(CONTRACT_START, 1)[1].split(CONTRACT_END, 1)[0]
    except IndexError as exc:
        raise SystemExit(f"{ORCHESTRATOR} is missing the {CONTRACT_START} / {CONTRACT_END} block that the eval prompt is built from") from exc
    # Strip HTML comments as SPANS, not line-wise: a multi-line comment's middle lines carry neither marker, so a line filter leaks the maintainer rationale into
    # the model's prompt. Caught the first time this ran.
    return re.sub(r"<!--.*?-->", "", body, flags=re.S).strip()


def capability_index(routing: dict[str, Any]) -> str:
    """Resolved list of who provides each gate's required capability at primary strength.

    Everything here is derivable from the catalogue the prompt already carries, so this adds no information — it moves it. In the catalogue the answer is
    spread across every skill and persona record; at selection time the router needs it in one place. Baseline v2's 22 gate failures were all cases of
    choosing a plausible neighbour over a declared provider, which is what a reader does when the answer is technically present but scattered.

    Generated, never hand-written: a hand-maintained copy is the exact duplication the capability registry replaced.
    """
    providers: list[dict[str, Any]] = routing.get("skills", []) + routing.get("personas", [])
    lines: list[str] = []
    for gate in routing.get("gates", []):
        if gate.get("computed"):
            continue
        cap = gate["required_capability"]
        primary = sorted(r["id"] for r in providers if cap in r.get("primary_capabilities", []))
        supporting = sorted(r["id"] for r in providers if cap in r.get("supporting_capabilities", []))
        lines.append(f"{gate['flag']} needs {cap} at {gate['minimum_strength']} strength")
        lines.append(f"  satisfied by (primary):  {', '.join(primary)}")
        lines.append(f"  NOT sufficient (supporting only): {', '.join(supporting) or 'none'}")
    return "\n".join(lines)


def evaluation_prompt(case: dict[str, Any], routing_text: str, index: str = "", contract: str = "") -> str:
    return f"""AGENT_STACK_ROUTING_EVAL_V3
You are being evaluated only on Agent Stack routing. Do not execute the user's task. Apply the routing contract below, which is the same contract the production
orchestrator uses, together with the routing catalogue.

{contract}

TASK MODE: {case['mode']} TASK: {case['task']}

Return EXACTLY one JSON object and no markdown. Use this schema: {json.dumps(PLAN_SCHEMA, indent=2)}

Rules:
- IDs must exactly match routing.toml.
- primary_owner is null for a skill-only route. Where one persona is accountable for the outcome, name it — a single owner is not team inflation.
- Do not select a persona or skill merely due to keyword overlap.
- Evaluate each gate in the catalogue's [[gates]] section against the task and set its flag accordingly.
- A gate is an obligation on the ROUTE, not an instruction to add a persona. For every gate you set true, satisfy it in this order and stop at the first step
  that works: (1) a skill or persona ALREADY selected declares the gate's required_capability in its primary_capabilities — then it is met, add nothing;
  (2) add the narrowest skill that declares it as a primary capability; (3) add the gate's persona only where independence of judgement is itself the
  deliverable, matching persona_mandatory or persona_mandatory_when_tags; (4) never add a persona merely because it is the gate's default_persona.
  A supporting_capabilities entry does NOT discharge a gate. A gate already satisfied by the route is met — do not add a second persona to satisfy it.
- Do not inflate the team to satisfy a gate.
- INVARIANT: a route is INVALID if it sets a gate true and no selected skill or persona declares that gate's required_capability at the required
  strength. Before you answer, walk the gates you set true and confirm each is closed; repair any that is not. A supporting capability does not close
  a gate. Adjacency does not close a gate — check the declaration, not the resemblance.
- Where two personas both plausibly own the decision, apply the catalogue's [[precedence]] rules to pick ONE primary owner. The losing persona may still be a
  supporting participant.
- runtime_required is not a judgement: set it true if and only if a skill you selected declares execution = "tool".
- Do not reveal this evaluation's expected answer; infer the route yourself.

CAPABILITY INDEX (derived from the catalogue below; use it to close gates):
---
{index}
---

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
        # Both streams, and a note when BOTH are empty. Holdout 24 lost five consecutive cases to `command exited 1:` with nothing after the colon, which left
        # the fault unclassifiable — quota, transport, or a runner that simply refused. A diagnostic that cannot distinguish those is not a diagnostic.
        err, out = proc.stderr.strip(), proc.stdout.strip()
        detail = "; ".join(part for part in (f"stderr: {err[-900:]}" if err else "", f"stdout: {out[-900:]}" if out else "") if part)
        if not detail:
            detail = "both streams empty — the runner exited without explaining itself (quota, session limit or transport are the usual causes)"
        raise RuntimeError(f"command exited {proc.returncode}: {detail}")
    return extract_json(proc.stdout)


def select_cases(cases: list[dict[str, Any]], wanted: list[str], family: str | None, limit: int | None) -> tuple[list[dict[str, Any]], int]:
    """Returns the selected cases and the size of the pool they were drawn from, so truncation can be REPORTED rather than inferred.

    `--limit` applies after --case/--family, and the pool is measured before it. The first Baseline v2 pass ran `--limit 10` per family, silently covered 53 of
    60 because two families are larger than 10, and printed a per-family line that read as complete. The pool count is what makes that visible at the time.
    """
    out = cases
    if wanted:
        ids=set(wanted); out=[c for c in out if c["id"] in ids]
        missing=ids-{c['id'] for c in out}
        if missing: raise SystemExit(f"unknown case(s): {', '.join(sorted(missing))}")
    if family:
        out=[c for c in out if c.get("family") == family]
    pool = len(out)
    if limit is not None: out=out[:limit]
    return out, pool


def rescore(pattern: str, corpus: dict[str, Any], routing: dict[str, Any], repair: bool = False) -> int:
    """Re-score stored plans against the current catalogue. No model is called; the routes are exactly what the recorded run produced.

    This is what separates "the catalogue now reads the same route differently" from "the model routed differently". Running the corpus again answers neither
    question on its own, because both changed at once.

    With `repair=True` the stored route is first passed through deterministic closure (scripts/close_route.py) and then scored. Because the routes are held fixed
    and no model is called, the delta is attributable to closure alone — which is the only honest way to decide whether closure is worth shipping before spending
    another corpus run on it.
    """
    stored: dict[str, dict[str, Any]] = {}
    for f in sorted(glob.glob(pattern)):
        for line in open(f):
            row = json.loads(line)
            stored[row["case_id"]] = row
    if not stored:
        print(f"no stored rows matched {pattern}", file=sys.stderr)
        return 1
    moved: list[str] = []
    was = now = 0
    scored = 0
    for cid, row in sorted(stored.items()):
        case = corpus.get(cid)
        plan = row.get("plan") or {}
        if case is None or "skills" not in plan:
            # An unparsed plan has no route to re-score; counting it either way would move the total for a reason that has nothing to do with the catalogue.
            continue
        scored += 1
        before = bool(row["passed"])
        if repair:
            plan, _actions = close_route(plan, routing, case.get("max_personas"))
        after = score_plan(case, plan, routing)
        was += before
        now += after.passed
        if before != after.passed:
            moved.append(f"{'PASS->FAIL' if before else 'FAIL->PASS'} {cid}: {after.hard_failures or 'clean'}")
    print(f"\nRe-scored {scored} stored plans against the current catalogue" + (" WITH deterministic closure applied" if repair else ""))
    print(f"  before: {was}/{scored}")
    print(f"  after:  {now}/{scored}")
    if moved:
        print(f"\n{len(moved)} case(s) changed verdict:")
        for m in moved:
            print(f"  {m}")
    else:
        print("\nNo case changed verdict." + (" Closure changed nothing on these routes." if repair else " The catalogue change is behaviour-preserving on these routes."))
    return 0


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--validate-only", action="store_true")
    ap.add_argument("--command", help="Local model/agent CLI command; prompt is passed via stdin")
    ap.add_argument("--case", action="append", default=[])
    ap.add_argument("--cases", type=Path, default=None,
                    help="Corpus TOML to evaluate. Defaults to the frozen development 60. Point it at evals/holdout-cases.toml for the unseen holdout; the "
                         "corpus hash stamped into every row follows this flag.")
    ap.add_argument("--family")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--output", type=Path, help="Optional JSONL result path")
    ap.add_argument("--provider", help="Provenance label, e.g. deepseek. Cannot be detected: the command is opaque.")
    ap.add_argument("--model", help="Provenance label, e.g. deepseek-v4-flash.")
    ap.add_argument("--runner", help="Provenance label for the frontend, e.g. hermes, claude-code, adapter.")
    ap.add_argument("--repair", action="store_true",
                    help="Apply deterministic route closure (scripts/close_route.py) to each plan before scoring. Use with --rescore to measure what closure "
                         "is worth on already-stored routes, with no model calls and nothing else changing.")
    ap.add_argument("--rescore",
                    help="Glob of stored result JSONL. Re-scores the plans those runs already produced against the CURRENT catalogue, with no model calls. "
                         "Isolates catalogue-interpretation change from model-behaviour change: any movement is attributable to the catalogue alone, "
                         "because the routes are held fixed.")
    args=ap.parse_args()
    routing, evals=load_data(args.cases); personas,skills=known_sets(routing)
    errors=[]
    for case in evals["cases"]: errors.extend(validate_case(case,personas,skills))
    if errors:
        print("Routing eval corpus: FAIL")
        for e in errors: print("-",e)
        return 1
    selected,pool=select_cases(evals["cases"],args.case,args.family,args.limit)
    print(f"Routing eval corpus: PASS ({len(evals['cases'])} cases; selected={len(selected)})")
    scope="corpus" if not (args.case or args.family) else (f"family {args.family}" if args.family else "selected cases")
    print(f"covered {len(selected)}/{pool} cases ({scope})")
    if len(selected) < pool:
        print(f"WARNING: partial corpus run - {len(selected)}/{pool} cases evaluated; --limit {args.limit} truncated the {scope}. Not a baseline.")
    if args.validate_only or not (args.command or args.rescore):
        if not (args.command or args.rescore) and not args.validate_only:
            print("No --command supplied; behavioral model execution skipped.")
        return 0
    if args.rescore:
        return rescore(args.rescore, {c["id"]: c for c in evals["cases"]}, routing, args.repair)
    routing_text=ROUTING.read_text()
    index=capability_index(routing)
    contract=routing_contract()
    results=[]
    for case in selected:
        try:
            plan=run_command(args.command,evaluation_prompt(case,routing_text,index,contract),args.timeout)
            if args.repair:
                # Production shape: the model proposes, the system closes. Applied before scoring so the score measures the route that would actually be offered.
                plan,_actions=close_route(normalize_plan(plan),routing,case.get("max_personas"))
            result=score_plan(case,plan,routing)
        except Exception as exc:
            result=Score(case['id'],0.0,False,[f"execution-error:{exc}"],[],[],{})
        results.append(result)
        print(f"{'PASS' if result.passed else 'FAIL'} {result.case_id}: {result.score:.1f}")
        for h in result.hard_failures: print(f"  ! {h}")
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        prov=run_provenance(args)
        # Stamped into every row rather than written to a sidecar: rows get filtered, merged and re-sorted during analysis, and provenance that lives in a
        # separate file stops travelling with them the moment they do.
        args.output.write_text("".join(json.dumps({**asdict(r),"run":prov},sort_keys=True)+"\n" for r in results))
        if prov["provider"]=="unspecified" or prov["model"]=="unspecified":
            print("WARNING: --provider/--model not supplied; these results are not safely comparable to another run.",
                  file=sys.stderr)
    # An execution error is an infrastructure fault — a mis-invoked CLI, a transport failure, a timeout, a reply that never parsed. Scoring it 0.0 inside
    # the denominators makes the harness report it as a routing failure by the model. Measured cost of getting this wrong, 2026-09-01: one 300s timeout on
    # the DeepSeek V4 Pro arm made Pro read 77.8 mean against Flash's 80.8 (worse) uncorrected, and 81.8 against 80.8 (better) once excluded — ONE TIMEOUT
    # INVERTED THE SIGN OF THE RESULT. Both figures are printed, because published numbers must stay reconcilable with corrected ones.
    errored=[r for r in results if any(h.startswith("execution-error") for h in r.hard_failures)]
    scored=[r for r in results if r not in errored]
    passed=sum(r.passed for r in scored)
    avg=sum(r.score for r in scored)/len(scored) if scored else 0.0
    print(f"Behavioral routing: {passed}/{len(scored)} passed; average score={avg:.1f}")
    fn=sum(len(r.gate_false_negatives) for r in scored)
    fp=sum(len(r.gate_false_positives) for r in scored)
    print(f"  gate_false_negative={fn} (hard, -20 each)  gate_false_positive={fp} (soft, -5 each)")
    if errored:
        raw_avg=sum(r.score for r in results)/len(results)
        print(f"  {len(errored)} execution error(s) EXCLUDED from the denominators: {', '.join(r.case_id for r in errored)}")
        print(f"  uncorrected (execution errors scored 0.0 and counted): {passed}/{len(results)} passed; average score={raw_avg:.1f}")
        for r in errored:
            print(f"    ! {r.case_id}: {r.hard_failures[0][:120]}", file=sys.stderr)
    # A run that could not execute is not a passing run, however few cases were scored.
    return 0 if (scored and passed==len(scored) and not errored) else 2

if __name__ == '__main__':
    raise SystemExit(main())
