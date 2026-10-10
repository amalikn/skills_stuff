"""Offline tests for scripts/md_sections.py: line ranges, fences, setext, exact-by-default selectors, ambiguity refusal and exit codes."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "md_sections.py"
_spec = importlib.util.spec_from_file_location("md_sections", SCRIPT)
md = importlib.util.module_from_spec(_spec)
sys.modules["md_sections"] = md
_spec.loader.exec_module(md)

DOC = """---
Title: Sample
Summary: # not a heading
---

# Plan

Intro.

## 17. Staged transition

### 17.6.1 Stage 0 — Containment

Zero.

```bash
# not a heading either
```

### 17.6.2 Stage 1 — Package skeleton

One.

### 17.9.2 Stage 10 — Clean-up

Ten.

## Rules

Setext child
------------

Body.

## Forms module

Forms.
"""


def run(*argv: str) -> tuple[int, str, str]:
    """Run main() and capture its output.

    Args:
        argv: command-line arguments.

    Returns:
        (exit code, stdout, stderr).
    """
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = md.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class MdSectionsTest(unittest.TestCase):
    """md_sections behaviour on a small document with every hard case."""

    def setUp(self) -> None:
        """Write the sample document to a temporary file."""
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "doc.md"
        self.path.write_text(DOC, encoding="utf-8")
        self.lines = DOC.split("\n")[:-1]

    def tearDown(self) -> None:
        """Remove the temporary folder."""
        self.tmp.cleanup()

    def titles(self) -> list[str]:
        """Titles scan() finds in the sample.

        Returns:
            The titles in order.
        """
        return [s.title for s in md.scan(self.lines)]

    def test_front_matter_and_fences_are_not_headings(self) -> None:
        """A `#` in front matter or fenced code is not a heading; a setext heading is."""
        self.assertEqual(self.titles(), ["Plan", "17. Staged transition", "17.6.1 Stage 0 — Containment", "17.6.2 Stage 1 — Package skeleton",
                                         "17.9.2 Stage 10 — Clean-up", "Rules", "Setext child", "Forms module"])

    def test_ranges_end_before_next_same_or_higher_heading(self) -> None:
        """A section ends on the line before the next heading of its level or above; the last runs to the end of the file."""
        secs = {s.title: s for s in md.scan(self.lines)}
        staged = secs["17. Staged transition"]
        self.assertEqual(self.lines[staged.end], "## Rules")
        self.assertEqual(secs["Forms module"].end, len(self.lines))
        self.assertEqual(self.lines[staged.body_end], "### 17.6.1 Stage 0 — Containment")

    def test_whole_word_prefix_does_not_hit_stage_10(self) -> None:
        """`Stage 1` names Stage 1 only, through the leading section number, and never Stage 10."""
        code, out, _ = run("section", str(self.path), "Stage 1")
        self.assertEqual(code, 0)
        self.assertIn("Stage 1 — Package skeleton", out)
        self.assertNotIn("Ten.", out)

    def test_number_prefix_is_exact(self) -> None:
        """`17.6` is not a heading number here, so it matches nothing (no substring hit on 17.6.1 or 17.6.2)."""
        self.assertEqual(run("section", str(self.path), "17.6")[0], 1)
        self.assertEqual(run("section", str(self.path), "17.6.2")[0], 0)

    def test_ambiguous_selector_is_refused_and_listed(self) -> None:
        """A selector naming two sections exits 3, lists both and prints no body; --all prints both."""
        code, out, err = run("section", str(self.path), "~stage")
        self.assertEqual((code, out), (3, ""))
        self.assertIn("Stage 0", err)
        self.assertIn("Stage 10", err)
        code, out, _ = run("section", str(self.path), "~stage 1", "--all")
        self.assertEqual(code, 0)
        self.assertIn("One.", out)
        self.assertIn("Ten.", out)

    def test_path_and_anchor_selectors(self) -> None:
        """`Parent > Child` and `#anchor` both name a section."""
        self.assertEqual(run("section", str(self.path), "Plan > Setext child")[0], 0)
        self.assertEqual(run("section", str(self.path), "Rules > Setext child")[0], 1)
        code, out, _ = run("section", str(self.path), "#forms-module")
        self.assertEqual(code, 0)
        self.assertIn("Forms.", out)

    def test_no_match_suggests_and_bad_file_exits_2(self) -> None:
        """No match exits 1 with the closest titles; an unreadable file exits 2."""
        code, _, err = run("section", str(self.path), "Form modul")
        self.assertEqual(code, 1)
        self.assertIn("Forms module", err)
        self.assertEqual(run("outline", str(self.path.with_name("missing.md")))[0], 2)

    def test_max_lines_and_no_children(self) -> None:
        """--max-lines truncates with the remaining range; --no-children stops before the first child heading."""
        code, out, _ = run("section", str(self.path), "Staged transition", "--max-lines", "2")
        self.assertEqual(code, 0)
        self.assertRegex(out, r"… \d+ more lines \(L\d+-\d+\)")
        code, out, _ = run("section", str(self.path), "Staged transition", "--no-children")
        self.assertNotIn("Stage 0", out)

    def test_outline_lists_every_heading_with_range(self) -> None:
        """The outline has one line per heading, each with L<start>-<end>, and honours --depth."""
        code, out, _ = run("outline", str(self.path))
        rows = out.strip().split("\n")[1:]
        self.assertEqual((code, len(rows)), (0, 8))
        self.assertTrue(all(r.startswith("L") for r in rows))
        self.assertEqual(len(run("outline", str(self.path), "--depth", "2")[1].strip().split("\n")[1:]), 5)


if __name__ == "__main__":
    unittest.main()
