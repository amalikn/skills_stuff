"""Offline tests for scripts/markdown/wrap_added.py: only added long prose lines wrap; old lines, tables and fences stay; words never change."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "markdown" / "wrap_added.py"
_spec = importlib.util.spec_from_file_location("wrap_added", SCRIPT)
wa = importlib.util.module_from_spec(_spec)
sys.modules["wrap_added"] = wa
_spec.loader.exec_module(wa)

OLD = "old " * 60
NEW = "- new " + "word " * 60
TABLE = "| " + "cell " * 60 + "|"
CODE = "x = '" + "y" * 250 + "'"
TEXT = f"# T\n\n{OLD}\n\n{NEW}\n\n{TABLE}\n\n```\n{CODE}\n```\n"


class WrapAddedTest(unittest.TestCase):
  """Wrapping added lines only."""

  def test_wraps_only_added_prose(self):
    """The added list item wraps with a two-space indent; the old line, table and code stay."""
    new, count = wa.wrap_text(TEXT, {NEW, TABLE, CODE}, 100)
    self.assertEqual(count, 1)
    self.assertIn(OLD, new)
    self.assertIn(TABLE, new)
    self.assertIn(CODE, new)
    self.assertTrue(all(len(line) <= 100 for line in new.split("\n") if line.startswith(("- new", "  word"))))

  def test_no_added_lines_is_a_no_op(self):
    """Nothing added means nothing wrapped."""
    new, count = wa.wrap_text(TEXT, set(), 100)
    self.assertEqual((new, count), (TEXT, 0))


if __name__ == "__main__":
  unittest.main()
