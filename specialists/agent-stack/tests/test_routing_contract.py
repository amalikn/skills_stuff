import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RoutingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.routing = tomllib.loads((ROOT / "routing.toml").read_text())
        cls.evals = tomllib.loads((ROOT / "evals" / "routing-cases.toml").read_text())
        cls.personas = {x["id"] for x in cls.routing["personas"]}
        cls.skills = {x["id"] for x in cls.routing["skills"]}

    def test_every_eval_reference_exists(self):
        for case in self.evals["cases"]:
            for key in ("required_personas", "preferred_personas", "forbidden_personas"):
                for item in case.get(key, []):
                    self.assertIn(item, self.personas, (case["id"], key, item))
            for key in ("required_skills", "preferred_skills", "forbidden_skills"):
                for item in case.get(key, []):
                    self.assertIn(item, self.skills, (case["id"], key, item))

    def test_no_case_requires_and_forbids_same_persona(self):
        for case in self.evals["cases"]:
            required = set(case.get("required_personas", []))
            forbidden = set(case.get("forbidden_personas", []))
            self.assertFalse(required & forbidden, case["id"])

    def test_material_rules_exist(self):
        rules = {x["id"] for x in self.routing["routing_rules"]}
        self.assertIn("economics-owner", rules)
        self.assertIn("architecture-owner", rules)
        self.assertIn("material-independent-challenge", rules)
        self.assertIn("research-first", rules)
        self.assertIn("network-technical-owner", rules)
        self.assertIn("import-evidence-first", rules)
        self.assertIn("import-economics-owner", rules)
        self.assertIn("current-facts-research", rules)

    def test_tool_skills_declare_requirements_or_safety(self):
        for skill in self.routing["skills"]:
            if skill["execution"] == "tool":
                self.assertTrue(skill.get("requires_any") or skill.get("safety_notes"), skill["id"])


if __name__ == "__main__":
    unittest.main()
