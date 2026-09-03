import importlib.util
import sys
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("evaluate_routing", ROOT / "scripts" / "evaluate_routing.py")
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

class RoutingBehaviorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.routing = tomllib.loads((ROOT / "routing.toml").read_text())
        cls.evals = tomllib.loads((ROOT / "evals" / "routing-cases.toml").read_text())

    def test_corpus_has_60_cases(self):
        self.assertEqual(len(self.evals["cases"]), 60)

    def test_expected_workload_families_exist(self):
        families = {c["family"] for c in self.evals["cases"]}
        self.assertEqual(families, {
            "networking-infrastructure", "software-ai-engineering", "jdm-import",
            "atar-import", "business-research", "direct-adversarial"
        })

    def test_behavioral_contract_references_are_valid(self):
        personas, skills = mod.known_sets(self.routing)
        errors=[]
        for case in self.evals["cases"]:
            errors += mod.validate_case(case, personas, skills)
        self.assertEqual(errors, [])

    def test_scorer_passes_exact_hard_contract(self):
        case = next(c for c in self.evals["cases"] if c["id"] == "jdm-landed-cost")
        plan = {
            "route_mode":"multi-persona", "primary_owner":"cfo-campbell",
            "personas":["cfo-campbell","research-thompson","operations-pg","critic-munger"],
            "skills":["financial-unit-economics","deep-research","premortem"],
            "research_required":True,"critic_required":True,"qa_required":False,"runtime_required":False
        }
        self.assertTrue(mod.score_plan(case, plan).passed)

    def test_scorer_rejects_team_inflation_and_forbidden_route(self):
        case = next(c for c in self.evals["cases"] if c["id"] == "direct-seo")
        plan = {
            "route_mode":"multi-persona", "primary_owner":"cto-vogels",
            "personas":["cto-vogels","cfo-campbell"], "skills":["seo-audit"],
            "research_required":False,"critic_required":False,"qa_required":False,"runtime_required":False
        }
        score=mod.score_plan(case,plan)
        self.assertFalse(score.passed)
        self.assertTrue(any("forbidden persona" in x or "team inflation" in x for x in score.hard_failures))

    # --- Gate scoring is asymmetric ---------------------------------------------------------------------------------------------------------------------
    # Each of these three fails on the pre-2026-09-02 scorer, which had no false-positive branch at all: over-assertion scored identically to an honest route,
    # so "set every gate true" was a free strategy that beat cautious routing on every case with a required gate.

    def test_gate_over_assertion_costs_five_points_each(self):
        """A route that fires gates the case does not require scores lower — by exactly 5 per surplus gate."""
        case = next(c for c in self.evals["cases"] if c["id"] == "market-size")
        base = {
            "route_mode": "single-persona", "primary_owner": case.get("primary_owner"),
            "personas": list(case.get("required_personas", [])), "skills": list(case.get("required_skills", [])),
            "research_required": False, "critic_required": False, "qa_required": False, "runtime_required": False,
        }
        honest = dict(base, **{f: bool(case.get(f, False)) for f in mod.GATE_FLAGS})
        greedy = dict(base, **{f: True for f in mod.GATE_FLAGS})
        honest_score, greedy_score = mod.score_plan(case, honest, self.routing), mod.score_plan(case, greedy, self.routing)
        self.assertEqual(honest_score.gate_false_positives, [])
        self.assertEqual(greedy_score.gate_false_positives, ["critic_required", "qa_required"])
        self.assertAlmostEqual(greedy_score.score, honest_score.score - 10.0)

    def test_gate_over_assertion_never_decides_the_verdict(self):
        """Over-routing is wasteful, not a contract breach: the score drops, `passed` does not."""
        case = next(c for c in self.evals["cases"] if c["id"] == "market-size")
        greedy = {
            "route_mode": "single-persona", "primary_owner": case.get("primary_owner"),
            "personas": list(case.get("required_personas", [])), "skills": list(case.get("required_skills", [])),
            **{f: True for f in mod.GATE_FLAGS},
        }
        score = mod.score_plan(case, greedy, self.routing)
        self.assertTrue(score.passed)
        self.assertTrue(score.gate_false_positives)
        self.assertLess(score.score, 90.0)

    def test_missing_gate_stays_a_hard_failure(self):
        """The asymmetry is the point: a false negative still fails the case outright while a false positive does not."""
        case = next(c for c in self.evals["cases"] if c["id"] == "market-size")
        silent = {
            "route_mode": "single-persona", "primary_owner": case.get("primary_owner"),
            "personas": list(case.get("required_personas", [])), "skills": list(case.get("required_skills", [])),
            **{f: False for f in mod.GATE_FLAGS},
        }
        score = mod.score_plan(case, silent, self.routing)
        self.assertFalse(score.passed)
        self.assertEqual(score.gate_false_negatives, ["research_required"])

    # --- Coverage is reported, not inferred -------------------------------------------------------------------------------------------------------------

    def test_select_cases_reports_the_pool_it_drew_from(self):
        """`--limit 10` on a 12-case family must be visibly partial. This is the 53-of-60 Baseline v2 truncation, as a test."""
        cases = self.evals["cases"]
        selected, pool = mod.select_cases(cases, [], "jdm-import", 10)
        self.assertEqual((len(selected), pool), (10, 12))
        self.assertLess(len(selected), pool)
        full, full_pool = mod.select_cases(cases, [], "jdm-import", None)
        self.assertEqual(len(full), full_pool)

    # --- The freeze record is parseable ---------------------------------------------------------------------------------------------------------------
    # Tests the RECORD, never the verdict. Asserting that the checkout currently matches the freeze would put a drift failure inside `just preflight`, which is
    # exactly the coupling `check_freeze.py` exists to avoid: a legitimate catalogue change must be able to pass preflight while failing freeze-check.

    def test_freeze_record_is_wellformed(self):
        """MEMORY.md states one 16-hex hash for every artifact the freeze covers, and the parser survives the table formatter's alignment padding."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("check_freeze", ROOT / "scripts" / "check_freeze.py")
        cf = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cf
        spec.loader.exec_module(cf)
        rec = cf.recorded()
        self.assertEqual(set(rec), set(cf.ALL_KEYS))
        for stamp, sha in rec.items():
            self.assertRegex(sha, r"^[0-9a-f]{16}$", f"{stamp} is not a 16-character hash")

    def test_freeze_stamps_match_what_the_harness_produces(self):
        """Every RUN-stamped key in the record is one the harness actually writes. Locally hashed artifacts are exempt: no run stamps them by default."""
        import argparse, importlib.util
        spec = importlib.util.spec_from_file_location("check_freeze", ROOT / "scripts" / "check_freeze.py")
        cf = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cf
        spec.loader.exec_module(cf)
        prov = mod.run_provenance(argparse.Namespace(provider=None, model=None, runner=None, command=None))
        for stamp in cf.STAMPS:
            self.assertIn(stamp, prov)

    # --- The unseen holdout ---------------------------------------------------------------------------------------------------------------------------

    def test_holdout_is_the_declared_shape(self):
        """24 cases in the declared family split, unique ids, and every reference resolvable against the catalogue."""
        holdout = tomllib.loads((ROOT / "evals" / "holdout-cases.toml").read_text())["cases"]
        self.assertEqual(len(holdout), 24)
        self.assertEqual(len({c["id"] for c in holdout}), 24)
        from collections import Counter
        self.assertEqual(Counter(c["family"] for c in holdout), Counter({
            "networking-infrastructure": 5, "jdm-import": 5, "software-ai-engineering": 4,
            "atar-import": 4, "business-research": 3, "direct-adversarial": 3,
        }))
        personas, skills = mod.known_sets(self.routing)
        errors = []
        for case in holdout:
            errors += mod.validate_case(case, personas, skills)
        self.assertEqual(errors, [])

    def test_holdout_runtime_assertions_are_earned_in_both_directions(self):
        """`runtime_required` is computed from the selected skills, so a case must neither over- nor under-state it.

        Under-stating became a defect only on 2026-09-02: a case asserting false while expecting a tool-class provider now costs the route 5 points for an
        over-assertion the case itself caused.
        """
        holdout = tomllib.loads((ROOT / "evals" / "holdout-cases.toml").read_text())["cases"]
        tool = {s["id"] for s in self.routing["skills"] if s.get("execution") == "tool"}
        for case in holdout:
            required_tool = tool & set(case.get("required_skills", []))
            self.assertEqual(bool(case.get("runtime_required")), bool(required_tool),
                             f"{case['id']}: runtime_required disagrees with its required skills {sorted(required_tool)}")

    def test_holdout_asserted_gates_are_satisfiable_by_the_case_itself(self):
        """A case asserting a gate its own required + preferred contract cannot close is contradicting itself, not testing the router."""
        holdout = tomllib.loads((ROOT / "evals" / "holdout-cases.toml").read_text())["cases"]
        for case in holdout:
            plan = mod.normalize_plan({
                "personas": list(case.get("required_personas", [])) + list(case.get("preferred_personas", []))
                            + ([case["primary_owner"]] if case.get("primary_owner") else []),
                "skills": list(case.get("required_skills", [])) + list(case.get("preferred_skills", [])),
            })
            for gate in self.routing["gates"]:
                if gate.get("computed") or not case.get(gate["flag"]):
                    continue
                need = {"supporting": 1, "primary": 2}[gate["minimum_strength"]]
                got = mod.capability_strength(plan, self.routing, gate["required_capability"])
                self.assertGreaterEqual(got, need,
                                        f"{case['id']} asserts {gate['flag']} but cannot provide {gate['required_capability']}")

    # --- Field log: the override statistic -----------------------------------------------------------------------------------------------------------

    def test_field_log_does_not_count_a_stated_non_override(self):
        """A recorder asked "what did you override?" answers "nothing" in prose rather than omitting the flag.

        Counting that as an override corrupts the one statistic the field log exists to produce, silently and in the flattering direction — every clean route
        would inflate the override rate. Observed on the first real entry ever logged: `--overrode "none - direct route, no gates true (read-only)"`.
        """
        import importlib.util
        spec = importlib.util.spec_from_file_location("field_log", ROOT / "scripts" / "field_log.py")
        fl = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = fl
        spec.loader.exec_module(fl)
        for value in ("none - direct route, no gates true (read-only)", "N/A", "nothing to change", "-", "no override", "no-override-needed", "", "   ", None):
            self.assertFalse(fl.is_override(value), f"{value!r} should not count as an override")

    def test_field_log_counts_a_real_departure_even_when_it_starts_with_a_negation(self):
        """A leading "none" must not hide a stated change — a prefix rule alone gets this wrong in both directions."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("field_log", ROOT / "scripts" / "field_log.py")
        fl = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = fl
        spec.loader.exec_module(fl)
        for value in ("none of the skills fit so I swapped owner to devops-hightower",
                      "Ran the CTO review inline instead of dispatching cto-vogels",
                      "swapped owner to devops-hightower",
                      "Corrects the prior entry - critic gate was dispatched after all"):
            self.assertTrue(fl.is_override(value), f"{value!r} should count as an override")

if __name__ == "__main__": unittest.main()
