"""Failure matrix for a routing-eval run: family x failure class, plus a root-cause split of the gate-unsatisfied cases.

A pass rate says how much is wrong; it does not say where the next fix belongs. This reads the JSONL rows `evaluate_routing.py` writes and separates defects that
look identical in the score but need opposite fixes — most importantly, a gate left unsatisfied because the route selected NO skills (an omission, fixable with a
must-select rule) from one left unsatisfied because the route selected skills that are absent from the gate's `satisfied_by_skills` list (a capability-visibility
problem, which a must-select rule would not touch). On the 2026-09-01 Baseline v2 that split was 5 against 15, and it moved the next fix out of the orchestrator
and into `routing.toml`.

Read-only. Stdlib only, so it runs without `just bootstrap`.
"""
import argparse
import collections
import glob
import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "evals/routing-cases.toml"
ROUTING = ROOT / "routing.toml"
DEFAULT_GLOB = "/Volumes/Data/_ai/_skills/skills-working-cache/agent-stack/routing-results/baseline2-*.jsonl"


def load_rows(pattern: str) -> list[dict]:
    """Newest row per case id. A family that was re-run, or filled in case-by-case, otherwise double-counts every one of its failures."""
    by_case: dict[str, dict] = {}
    for f in sorted(glob.glob(pattern)):
        for line in open(f):
            row = json.loads(line)
            by_case[row["case_id"]] = row
    return list(by_case.values())


def failure_class(h: str) -> str:
    """Collapse a hard-failure string to its class, keeping the gate name where there is one — `unsatisfied:critic_required` and `unsatisfied:qa_required` are
    different findings and merging them hides which gate is actually failing."""
    if h.startswith("gate ") and "unsatisfied" in h:
        return f"unsatisfied:{h.split()[1]}"
    if h.startswith("capability strength insufficient for "):
        return f"strength-insufficient:{h.split()[4].rstrip(':')}"
    if h.startswith("missing gate:"):
        return f"missing-gate:{h.split(':')[1]}"
    for prefix, label in (
        ("missing required persona", "missing-persona"),
        ("missing required skill", "missing-skill"),
        ("selected forbidden persona", "forbidden-persona"),
        ("selected forbidden skill", "forbidden-skill"),
        ("team inflation", "team-inflation"),
        ("wrong primary owner", "wrong-owner"),
    ):
        if h.startswith(prefix):
            return label
    return h.split(":")[0]


def catalogue() -> tuple[dict, dict, set[str]]:
    """Gate requirements, provider capability declarations, and the tool-class skill set."""
    routing = tomllib.load(open(ROUTING, "rb"))
    gates = {g["flag"]: (g.get("required_capability"), g.get("minimum_strength")) for g in routing.get("gates", [])}
    providers = {
        r["id"]: (set(r.get("primary_capabilities", [])), set(r.get("supporting_capabilities", [])))
        for r in routing.get("skills", []) + routing.get("personas", [])
    }
    return gates, providers, {s["id"] for s in routing["skills"] if s.get("execution") == "tool"}


def main(pattern: str) -> int:
    corpus = {c["id"]: c for c in tomllib.load(open(CASES, "rb"))["cases"]}
    rows = load_rows(pattern)
    if not rows:
        print(f"no result rows matched {pattern}", file=sys.stderr)
        return 1
    gate_req, providers, tool_skills = catalogue()

    fam: dict[str, dict] = collections.defaultdict(lambda: {"n": 0, "pass": 0, "score": 0.0})
    matrix: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    causes: collections.Counter = collections.Counter()
    cause_cases: dict[str, list[str]] = collections.defaultdict(list)
    skill_free: list[tuple[str, str, bool]] = []
    personas_total = skills_total = over_max = extra_skills = routes_with_extra = 0
    extra_by_skill: collections.Counter = collections.Counter()
    unparsed: list[tuple[str, str]] = []
    orphans: list[str] = []

    for r in rows:
        case = corpus.get(r["case_id"])
        if case is None:
            # A row whose case id is no longer in the corpus — renamed, retired, or from a different branch. Report it rather than crash: the run is still
            # evidence, and a silent KeyError here would look like the analysis simply had nothing to say.
            orphans.append(r["case_id"])
            continue
        f = case["family"]
        fam[f]["n"] += 1
        fam[f]["pass"] += bool(r["passed"])
        fam[f]["score"] += r["score"]

        # A plan with no `skills` key never parsed into the schema at all. That is a model-side or transport failure, not an empty route, and counting the two
        # together overstates capability omission by one case per flake.
        plan = r.get("plan") or {}
        malformed = "skills" not in plan
        plan_skills = set(plan.get("skills") or [])
        if malformed:
            unparsed.append((f, r["case_id"]))
        elif not plan_skills:
            skill_free.append((f, r["case_id"], bool(r["passed"])))
        if not malformed:
            plan_personas = set(plan.get("personas") or [])
            personas_total += len(plan_personas)
            skills_total += len(plan_skills)
            if len(plan_personas) > case.get("max_personas", 4):
                over_max += 1
            # "Beyond contract" is not automatically wrong — the corpus names what a route MUST and SHOULD carry, not everything it MAY. It is a trend measure:
            # a rise here alongside a fall in unsatisfied is the signature of closing gates by accumulation.
            contract = set(case.get("required_skills", [])) | set(case.get("preferred_skills", []))
            extra = plan_skills - contract
            if extra:
                extra_skills += len(extra)
                routes_with_extra += 1
                extra_by_skill.update(extra)

        for h in r["hard_failures"]:
            cls = failure_class(h)
            matrix[f][cls] += 1
            key = None
            if cls.startswith("unsatisfied:") or cls == "capability-strength":
                flag = cls.split(":")[1] if ":" in cls else "capability-strength"
                cap, _min = gate_req.get(flag, (None, None))
                # Strength is resolved over the whole route, skills and personas alike, because that is how the scorer resolves it. Splitting the two here would
                # report a "no provider" cause for a route whose persona was in fact carrying the capability.
                members = plan_skills | set(plan.get("personas") or [])
                carriers = {m for m in members if cap in providers.get(m, (set(), set()))[0]}
                if not plan_skills:
                    key = f"{flag}: no skills selected at all"
                elif carriers:
                    # Cannot happen if the scorer and this script read the same catalogue. If it does, one of them is wrong — say so loudly rather than fold it
                    # into a plausible-looking bucket.
                    key = f"{flag}: primary provider present but still scored (BUG)"
                else:
                    key = f"{flag}: skills selected but none provide {cap}"
            elif cls == "missing-gate:runtime_required":
                key = "runtime: no tool-class skill selected" if not (plan_skills & tool_skills) else "runtime: tool skill present (BUG)"
            elif cls in ("wrong-owner", "missing-persona", "team-inflation"):
                key = f"ownership: {cls}"
            if key:
                causes[key] += 1
                if r["case_id"] not in cause_cases[key]:
                    cause_cases[key].append(r["case_id"])

    scored = sum(d["n"] for d in fam.values())
    passed = sum(d["pass"] for d in fam.values())
    mean = sum(d["score"] for d in fam.values()) / scored
    print(f"\nOVERALL  {passed}/{scored} ({100 * passed / scored:.1f}%)  mean {mean:.1f}")
    print(f"corpus has {len(corpus)} cases; {len(corpus) - scored} not present in these results\n")

    print(f"{'family':28} {'pass':>7}  {'mean':>5}")
    for f in sorted(fam):
        d = fam[f]
        print(f"{f:28} {d['pass']:3}/{d['n']:<3} {d['score'] / d['n']:5.1f}")

    classes = sorted({c for counter in matrix.values() for c in counter})
    print(f"\n{'failure class':38}" + "".join(f"{f[:9]:>10}" for f in sorted(matrix)) + f"{'tot':>6}")
    for c in classes:
        row = [matrix[f][c] for f in sorted(matrix)]
        print(f"{c:38}" + "".join(f"{v or '.':>10}" for v in row) + f"{sum(row):>6}")

    print("\nROOT CAUSE")
    for k, v in causes.most_common():
        print(f"  {v:3}  {k}")
        print(f"       {', '.join(sorted(cause_cases[k]))}")

    if unparsed:
        print(f"\nUNPARSED MODEL OUTPUT (no plan schema): {len(unparsed)}")
        for f, cid in sorted(unparsed):
            print(f"  {f:28} {cid}")
    if orphans:
        print(f"\nROWS WITH NO MATCHING CORPUS CASE: {len(orphans)}")
        for cid in sorted(orphans):
            print(f"  {cid}")

    # Over-routing. A closure rule that makes an unsatisfied gate invalid invites the opposite defect: the router closes every gate by adding providers until the
    # team is bloated. `unsatisfied` collapsing while these rise is not a win, it is the same problem moved, so they are reported side by side rather than in
    # separate passes where the trade would be easy to miss.
    print("\nOVER-ROUTING (watch alongside unsatisfied — a closure fix can simply move the defect here)")
    print(f"  mean personas/route: {personas_total / scored:.2f}   mean skills/route: {skills_total / scored:.2f}")
    print(f"  routes over the case's max_personas: {over_max}")
    print(f"  skills selected beyond the case's required+preferred set: {extra_skills} across {routes_with_extra} route(s)")
    if extra_by_skill:
        top = ", ".join(f"{k}x{v}" for k, v in extra_by_skill.most_common(6))
        print(f"  most-added beyond contract: {top}")

    print(f"\nROUTES WITH NO SKILLS AT ALL: {len(skill_free)}/{scored}")
    for f, cid, p in sorted(skill_free):
        print(f"  {'PASS' if p else 'FAIL'}  {f:28} {cid}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pattern", nargs="?", default=DEFAULT_GLOB, help="glob of routing-eval JSONL result files")
    sys.exit(main(ap.parse_args().pattern))
