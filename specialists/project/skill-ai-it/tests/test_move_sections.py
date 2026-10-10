"""Offline tests for scripts/move_sections.py: sections move verbatim, Contents and pointer are right, nothing is written without --apply."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "move_sections.py"
_spec = importlib.util.spec_from_file_location("move_sections", SCRIPT)
ms = importlib.util.module_from_spec(_spec)
sys.modules["move_sections"] = ms
_spec.loader.exec_module(ms)

SOURCE = """# Agents

## Contents

- [Rules](#rules)
- [Key anchors](#key-anchors)
- [Memory pointers (navigation only — content is above)](#memory-pointers-navigation-only--content-is-above)
- [Preflight](#preflight)

## Rules

Keep this rule.

## Key anchors

| Anchor | Value |
| --- | --- |
| venv | `.venv` |
| plan | [plan](docs/plan.md) |

```bash
## not a heading inside a fence
```

## Memory pointers (navigation only — content is above)

- pointer one

## Preflight

Read AI_NAVIGATION.md.
"""


class MoveSectionsTest(unittest.TestCase):
    """Run main() on a temporary project."""

    def run_move(self, apply: bool) -> tuple[int, Path]:
        """Move two sections out of a sample file.

        Args:
            apply: pass --apply.

        Returns:
            (exit status, project root).
        """
        root = Path(tempfile.mkdtemp())
        (root / "AGENTS.md").write_text(SOURCE)
        argv = ["--project-root", str(root), "--source", "AGENTS.md", "--dest", "docs/ref.md", "--title", "Ref", "--summary", "s",
                "Key anchors", "Memory pointers (navigation only — content is above)"] + (["--apply"] if apply else [])
        return ms.main(argv), root

    def test_plan_writes_nothing(self):
        rc, root = self.run_move(False)
        self.assertEqual(rc, 0)
        self.assertEqual((root / "AGENTS.md").read_text(), SOURCE)
        self.assertFalse((root / "docs/ref.md").exists())

    def test_apply_moves_verbatim_and_fixes_contents(self):
        rc, root = self.run_move(True)
        self.assertEqual(rc, 0)
        src, ref = (root / "AGENTS.md").read_text(), (root / "docs/ref.md").read_text()
        for line in ["| venv | `.venv` |", "## not a heading inside a fence", "- pointer one"]:
            self.assertIn(line, ref)
            self.assertNotIn(line, src)
        self.assertIn("Keep this rule.", src)
        self.assertIn("## Reference loaded on need", src)
        self.assertIn("- [Reference loaded on need](#reference-loaded-on-need)", src)
        self.assertNotIn("](#key-anchors)", src)
        self.assertNotIn("content-is-above)", src)
        self.assertLess(src.index("## Reference loaded on need"), src.index("## Preflight"))

    def test_missing_section_and_existing_dest_refuse(self):
        root = Path(tempfile.mkdtemp())
        (root / "AGENTS.md").write_text(SOURCE)
        base = ["--project-root", str(root), "--source", "AGENTS.md", "--dest", "docs/ref.md", "--title", "t", "--summary", "s"]
        self.assertEqual(ms.main(base + ["No such section"]), 1)
        (root / "docs").mkdir()
        (root / "docs/ref.md").write_text("x")
        self.assertEqual(ms.main(base + ["Rules"]), 1)

    def test_relative_links_resolve_from_the_destination(self):
        root = Path(tempfile.mkdtemp())
        (root / "AGENTS.md").write_text(SOURCE)
        (root / "docs").mkdir()
        (root / "docs" / "plan.md").write_text("# plan\n")  # a real target, so the link is relinked
        ms.main(["--project-root", str(root), "--source", "AGENTS.md", "--dest", "docs/ref.md", "--title", "t", "--summary", "s",
                 "--apply", "Key anchors"])
        self.assertIn("| plan | [plan](plan.md) |", (root / "docs/ref.md").read_text())

    def test_nested_sections_and_pointer_line(self):
        text = "# S\n\n## Phase 4\n\nIntro.\n\n### Big part\n\n#### A\n\nalpha\n\n#### B\n\nbeta\n\n### Small part\n\nkeep\n"
        new, moved = ms.plan(text.split("\n"), ["Big part"], "references/big.md", "x", pointer_line=True)
        self.assertEqual(moved[0][0], "### Big part")
        self.assertIn("beta", moved[0])
        joined = "\n".join(new)
        self.assertIn("- Read [references/big.md](references/big.md) before that work (moved verbatim from here): Big part.", joined)
        self.assertIn("### Small part", joined)
        self.assertNotIn("alpha", joined)

    def test_example_links_are_not_relinked(self):
        root = Path(tempfile.mkdtemp())
        (root / "AGENTS.md").write_text("# A\n\n## Example\n\nWrite [parent](../AGENTS.md) in the child README.\n")
        ms.main(["--project-root", str(root), "--source", "AGENTS.md", "--dest", "docs/ex.md", "--title", "t", "--summary", "s", "--apply", "Example"])
        self.assertIn("[parent](../AGENTS.md)", (root / "docs/ex.md").read_text())

class PointerAndLinkTest(unittest.TestCase):
    """One shared pointer section, legacy pointer merge, and links that cross a move."""

    DOC = ("# A\n\n## Contents\n\n- [Rules](#rules)\n- [Anchors](#anchors)\n- [Hardware](#hardware)\n\n## Rules\n\nSee [anchors](#anchors) and"
           " [hardware](#hardware).\n\n## Anchors\n\n| a | b |\n\nBack to [rules](#rules).\n\n## Hardware\n\n| unit | model |\n")

    def project(self) -> Path:
        """A temporary project holding DOC as AGENTS.md and a README that links into it.

        Returns:
            The project root.
        """
        root = Path(tempfile.mkdtemp())
        (root / "AGENTS.md").write_text(self.DOC)
        (root / "README.md").write_text("Read [the anchors](AGENTS.md#anchors) and [rules](AGENTS.md#rules).\n")
        return root

    def move(self, root: Path, name: str, dest: str) -> int:
        """Move one section into the shared pointer section.

        Args:
            root: the project root.
            name: the heading to move.
            dest: the destination, project-relative.

        Returns:
            The exit status.
        """
        return ms.main(["--project-root", str(root), "--source", "AGENTS.md", "--dest", dest, "--title", "t", "--summary", "s",
                        "--pointer-into", "Reference moved out", "--apply", name])

    def test_two_moves_share_one_pointer_section(self):
        root = self.project()
        self.assertEqual(self.move(root, "Anchors", "docs/a.md"), 0)
        self.assertEqual(self.move(root, "Hardware", "docs/h.md"), 0)
        text = (root / "AGENTS.md").read_text()
        self.assertEqual(text.count("## Reference moved out"), 1)
        self.assertIn("- [docs/a.md](docs/a.md): Anchors.", text)
        self.assertIn("- [docs/h.md](docs/h.md): Hardware.", text)
        self.assertEqual(text.count("- [Reference moved out](#reference-moved-out)"), 1)

    def test_in_page_links_cross_the_move_both_ways(self):
        root = self.project()
        self.move(root, "Anchors", "docs/a.md")
        self.assertIn("See [anchors](docs/a.md#anchors)", (root / "AGENTS.md").read_text())
        self.assertIn("Back to [rules](../AGENTS.md#rules).", (root / "docs/a.md").read_text())

    def test_other_files_follow_the_moved_section(self):
        root = self.project()
        self.move(root, "Anchors", "docs/a.md")
        readme = (root / "README.md").read_text()
        self.assertIn("[the anchors](docs/a.md#anchors)", readme)
        self.assertIn("[rules](AGENTS.md#rules)", readme)

    def test_legacy_numbered_pointers_merge(self):
        lines = ["# S", "", "## Contents", "", "- [Reference moved out (1)](#reference-moved-out-1)", "- [Reference moved out (2)](#reference-moved-out-2)",
                 "", "## Reference moved out (1)", "", "Read [docs/x.md](docs/x.md) before the work it covers. It holds these sections, moved verbatim",
                 "from this file (a citation of a section", "by name resolves there): Key anchors.", "", "## Current state", "", "now", "",
                 "## Reference moved out (2)", "", "Read [docs/y.md](docs/y.md) before the work it covers. It holds these sections, moved verbatim",
                 "from this file (a citation of a section", "by name resolves there): Residual risk.", ""]
        new, n = ms.consolidate(lines)
        self.assertEqual(n, 2)
        text = "\n".join(new)
        self.assertEqual(text.count("## Reference moved out"), 1)
        self.assertIn("- [docs/x.md](docs/x.md): Key anchors.", text)
        self.assertIn("- [docs/y.md](docs/y.md): Residual risk.", text)
        self.assertNotIn("(#reference-moved-out-1)", text)
        self.assertIn("- [Reference moved out](#reference-moved-out)", text)


if __name__ == "__main__":
    unittest.main()
