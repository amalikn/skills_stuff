"""Offline tests for scripts/budget_plan.py: a SCRATCHPAD of dated bold paragraphs and a reference section ends within budget, nothing lost."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "budget_plan.py"
_spec = importlib.util.spec_from_file_location("budget_plan", SCRIPT)
bp = importlib.util.module_from_spec(_spec)
sys.modules["budget_plan"] = bp
_spec.loader.exec_module(bp)


def scratchpad() -> str:
    """A SCRATCHPAD held over budget by dated bold paragraphs and an undated reference section.

    Returns:
        The file text.
    """
    lines = ["---", "Title: Scratchpad", "Kind: state", "---", "", "# Scratchpad", "", "## Current state", ""]
    for i in range(60):
        lines += [f"**Thread {i}, 2026-0{1 + i % 8}-1{i % 10} — work {i}.** detail {i}", f"more {i}", ""]
    lines += ["## Key anchors", ""] + [f"| anchor {i} | value {i} |" for i in range(220)] + [""]
    return "\n".join(lines) + "\n"


class BudgetPlanTest(unittest.TestCase):
    """Run main() on a temporary git project."""

    def test_apply_brings_the_record_within_budget_without_loss(self):
        root = Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        (root / "docs").mkdir()
        original = scratchpad()
        (root / "SCRATCHPAD.md").write_text(original)
        self.assertEqual(bp.main(["--project-root", str(root), "--apply"]), 0)
        live = (root / "SCRATCHPAD.md").read_text()
        self.assertLessEqual(live.count("\n"), 200)
        everything = Counter(l for p in root.rglob("*.md") for l in p.read_text().split("\n") if l.strip())
        missing = [l for l in original.split("\n") if l.strip() and everything[l] < 1]
        self.assertEqual(missing, [])
        self.assertTrue(list((root / "docs").glob("scratchpad-reference-1-*.md")))

    def test_symlinked_records_are_refused(self):
        root, real = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
        (real / "SCRATCHPAD.md").write_text("# s\n")
        (root / "SCRATCHPAD.md").symlink_to(real / "SCRATCHPAD.md")
        self.assertEqual(bp.main(["--project-root", str(root)]), 1)

    def test_unfittable_record_stops_after_moving_what_it_can(self):
        root = Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        (root / "docs").mkdir()
        text = "# S\n\n## Current state\n\n" + "".join(f"undated line {i}\n" for i in range(300)) + "\n## Key anchors\n\n| a | b |\n"
        (root / "SCRATCHPAD.md").write_text(text)
        self.assertEqual(bp.main(["--project-root", str(root), "--apply"]), 1)
        self.assertEqual(len(list((root / "docs").glob("scratchpad-reference-*.md"))), 1)

    def test_reference_like_sections_are_suggested_not_moved(self):
        text = ("# A\n\n## Rules\n\n" + "".join(f"- You must never do thing {i} before checking.\n" for i in range(30))
                + "\n## Hardware table\n\n" + "".join(f"| unit {i} | model {i} |\n" for i in range(30)))
        self.assertEqual([h for h, _ in bp.reference_like(text)], ["Hardware table"])

    def test_no_upgrade_hint_for_a_project_owned_block(self):
        root = Path(tempfile.mkdtemp())
        body = "".join(f"- line {i}\n" for i in range(220))
        (root / "AI_NAVIGATION.md").write_text("<!-- BEGIN skill-ai-it:navigation --> <!-- skill-ai-it:manual reason=x -->\n" + body)
        import io, contextlib
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            bp.main(["--project-root", str(root)])
        self.assertNotIn("upgrade_navigation_control_layer", out.getvalue())

    def test_pointer_clutter_is_tidied(self):
        root = Path(tempfile.mkdtemp())
        (root / "docs" / "trackers").mkdir(parents=True)
        ptr = "- Older open items are tracked in [open-items-1.md](docs/trackers/open-items-1.md)."
        (root / "SCRATCHPAD.md").write_text(f"# S\n\n## Open items\n\n{ptr}\n{ptr}\n{ptr}\n- [ ] x\n")
        (root / "docs" / "trackers" / "open-items-1.md").write_text(f"# T\n\n{ptr}\n- [ ] old\n")
        self.assertEqual(bp.main(["--project-root", str(root), "--apply"]), 0)
        self.assertEqual((root / "SCRATCHPAD.md").read_text().count(ptr), 1)
        self.assertNotIn(ptr, (root / "docs" / "trackers" / "open-items-1.md").read_text())
        self.assertIn("- [ ] old", (root / "docs" / "trackers" / "open-items-1.md").read_text())


if __name__ == "__main__":
    unittest.main()
