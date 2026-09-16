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
            "attar-import", "business-research", "direct-adversarial"
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

if __name__ == "__main__": unittest.main()
