"""Offline tests for scripts/validate_navigation_control_layer.py: the shipped AI_NAVIGATION template must pass the validator's content checks."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_navigation_control_layer.py"
_spec = importlib.util.spec_from_file_location("validate_navigation_control_layer", SCRIPT)
vnav = importlib.util.module_from_spec(_spec)
sys.modules["validate_navigation_control_layer"] = vnav
_spec.loader.exec_module(vnav)


def _messages(ai_nav: str, key: str) -> list[str]:
    """Run validate_ai_navigation and return the messages under one result key.

    Args:
        ai_nav: AI_NAVIGATION.md text to validate.
        key: "passed", "warnings" or "failures".

    Returns:
        The messages the validator recorded under that key.
    """
    results = {"passed": [], "warnings": [], "failures": []}
    vnav.validate_ai_navigation(ai_nav, results)
    return results[key]


class TemplatePassesValidator(unittest.TestCase):
    """The template is the source of truth for block wording; the validator must accept it."""

    def test_template_has_support_only_policy(self) -> None:
        """The compact template's "never a source of truth" wording satisfies the generated-output check."""
        text = (ROOT / "templates" / "AI_NAVIGATION.md").read_text(encoding="utf-8")
        self.assertFalse([m for m in _messages(text, "failures") if "support-only" in m])

    def test_missing_policy_still_fails(self) -> None:
        """Text with no generated-output policy at all is still reported."""
        self.assertTrue([m for m in _messages("# Nav\n\nNothing here.\n", "failures") if "support-only" in m])


if __name__ == "__main__":
    unittest.main()
