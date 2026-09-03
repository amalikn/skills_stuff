"""Tests for deterministic route closure.

These are regression tests for the behaviours that were wrong in the first draft, plus the invariants the module promises. Each one corresponds to a defect that
was actually observed or to a promise made in the module docstring — none is a restatement of the implementation.
"""
import sys
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from close_route import capability_strength, close_route  # noqa: E402

ROUTING = tomllib.loads((ROOT / "routing.toml").read_text())


def route(**kw):
    base = {"personas": [], "skills": [], "research_required": False, "critic_required": False,
            "qa_required": False, "runtime_required": False}
    base.update(kw)
    return base


class CloseRouteTests(unittest.TestCase):
    def test_open_gate_is_closed_by_a_skill_not_a_persona(self):
        """A gate is an obligation on the route; a skill discharges it. Reaching for the persona first is the inflation the direct-adversarial family punishes."""
        out, actions = close_route(route(critic_required=True, personas=["cto-vogels"]), ROUTING, 3)
        self.assertIn("premortem", out["skills"])
        self.assertEqual(out["personas"], ["cto-vogels"], "closure must not add a persona when a skill suffices")
        self.assertTrue(any("closed critic_required" in a for a in actions))

    def test_already_satisfied_gate_is_left_alone(self):
        """Idempotence, and the satisfaction rule: a gate already discharged is met, not an invitation to add a second provider."""
        first, _ = close_route(route(qa_required=True, personas=["cto-vogels"]), ROUTING, 3)
        second, actions = close_route(first, ROUTING, 3)
        self.assertEqual(first["skills"], second["skills"])
        self.assertFalse([a for a in actions if a.startswith("closed")])

    def test_canonical_provider_wins_over_lexicographic_order(self):
        """Regression: closure once picked code-review-security for a generic validation need because it sorts first. The catalogue names senior-qa."""
        out, _ = close_route(route(qa_required=True), ROUTING, 3)
        self.assertIn("senior-qa", out["skills"])

    def test_closure_does_not_open_a_runtime_prerequisite_when_it_can_avoid_one(self):
        """Regression: the first draft closed `research` with github-explorer, a tool skill needing github-access, over a provider with no prerequisite."""
        out, _ = close_route(route(research_required=True, personas=["cto-vogels"]), ROUTING, 3)
        added = set(out["skills"])
        self.assertNotIn("github-explorer", added)

    def test_tags_escalate_a_gate_to_its_persona(self):
        """Independence cannot come from a skill. Where the task carries a gate's escalation tag, the persona is required and a skill no longer discharges it."""
        out, actions = close_route(route(qa_required=True, personas=["cto-vogels"]), ROUTING, 3, tags=["security-sensitive"])
        self.assertIn("qa-bach", out["personas"])
        self.assertTrue(any("escalated qa_required" in a for a in actions))

    def test_team_cap_is_never_breached_to_close_a_gate(self):
        """Trading one hard failure for another is not a repair. The refusal must be reported, not silent."""
        out, actions = close_route(route(qa_required=True, personas=["cto-vogels"]), ROUTING, 1, tags=["security-sensitive"])
        self.assertEqual(out["personas"], ["cto-vogels"])
        self.assertTrue(any(a.startswith("REFUSED") for a in actions))

    def test_runtime_required_is_recomputed_not_trusted(self):
        """The flag is a lookup against the selected skills' execution class, and closure may itself add a tool skill."""
        out, _ = close_route(route(runtime_required=True, skills=["premortem"]), ROUTING, 3)
        self.assertFalse(out["runtime_required"], "no tool-class skill is selected, so the flag must be false")

    def test_input_route_is_not_mutated(self):
        original = route(critic_required=True)
        snapshot = {k: (list(v) if isinstance(v, list) else v) for k, v in original.items()}
        close_route(original, ROUTING, 3)
        self.assertEqual(original, snapshot)

    def test_capability_strength_pools_skills_and_personas(self):
        self.assertEqual(capability_strength(route(personas=["critic-munger"]), ROUTING, "independent-challenge"), 2)
        self.assertEqual(capability_strength(route(skills=["premortem"]), ROUTING, "independent-challenge"), 2)
        self.assertEqual(capability_strength(route(skills=["devops"]), ROUTING, "validation"), 1, "devops carries validation as supporting only")


if __name__ == "__main__":
    unittest.main()
