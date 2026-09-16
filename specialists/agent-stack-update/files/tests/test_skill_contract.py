import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "skills" / "skill-creator" / "scripts" / "quick_validate.py"


class SkillContractTests(unittest.TestCase):
    def test_all_package_skills_validate(self):
        for skill_md in sorted((ROOT / "skills").glob("*/SKILL.md")):
            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), str(skill_md.parent)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, completed.returncode, f"{skill_md.parent.name}: {completed.stdout}{completed.stderr}")

    def test_startup_business_model_resources_exist(self):
        base = ROOT / "skills" / "startup-business-models"
        expected = [
            "references/unit-economics-calculator.md",
            "references/pricing-research-guide.md",
            "references/saas-metrics-playbook.md",
            "assets/business-model-canvas.md",
            "assets/unit-economics-worksheet.md",
            "assets/pricing-tier-design.md",
            "data/sources.json",
        ]
        for rel in expected:
            self.assertTrue((base / rel).is_file(), rel)

    def test_autonomy_adaptations_are_explicit(self):
        deep = (ROOT / "skills/deep-research/SKILL.md").read_text()
        websh = (ROOT / "skills/websh/SKILL.md").read_text()
        self.assertIn("Bounded Continuation Policy (Agent Stack Adaptation)", deep)
        self.assertIn("Agent Stack Safety Adaptation", websh)
        self.assertIn("do not spawn continuation agents", deep.lower())
        self.assertIn("do not spawn background subagents", websh.lower())


if __name__ == "__main__":
    unittest.main()
