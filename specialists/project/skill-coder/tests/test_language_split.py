"""Offline tests for scripts/language_split.py: budget report, a split that keeps every word, and a refused split.

Run: just test (unittest). Writes only under a temporary folder standing in for languages/.
"""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SPEC = importlib.util.spec_from_file_location("language_split", Path(__file__).resolve().parents[1] / "scripts" / "language_split.py")
ls = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ls)

DOC = """---
Title: demo
---

# Demo override

## Contents

- [Tools](#tools)
- [Notes](#notes)

## Tools

ruff and friends.

## Notes

A plain paragraph about notes.

> **Learned 2026-11-07** · timeout · VERIFIED_PRIMARY
> a timeout fact

> **Learned 2026-11-08** · other · VERIFIED_PRIMARY
> something else entirely
"""


class LanguageSplit(unittest.TestCase):
  """language_split keeps entry essentials, routes Learned blocks by topic, and never loses a word."""

  def setUp(self) -> None:
    """A temporary languages folder with one file and its topic map."""
    self.tmp = tempfile.TemporaryDirectory()
    self.langs = Path(self.tmp.name)
    (self.langs / "demo.md").write_text(DOC, encoding="utf-8")
    (self.langs / "demo").mkdir()
    (self.langs / "demo" / "topics.toml").write_text('[topics]\nlearned-timeouts = ["timeout"]\n', encoding="utf-8")
    self.patch = mock.patch.object(ls, "LANGS", self.langs)
    self.patch.start()

  def tearDown(self) -> None:
    """Remove the temporary folder."""
    self.patch.stop()
    self.tmp.cleanup()

  def test_split_routes_blocks_and_keeps_words(self) -> None:
    """Tools stays; the paragraph goes to notes.md; each Learned block goes to its topic file; the entry indexes them."""
    with mock.patch("builtins.print"):
      self.assertEqual(ls.split("demo", apply=True), 0)
    entry = (self.langs / "demo.md").read_text()
    self.assertIn("## Tools", entry)
    self.assertIn("## Topic files", entry)
    self.assertNotIn("A plain paragraph", entry)
    self.assertIn("a timeout fact", (self.langs / "demo" / "learned-timeouts.md").read_text())
    self.assertIn("something else", (self.langs / "demo" / "learned-other.md").read_text())
    self.assertIn("A plain paragraph", (self.langs / "demo" / "notes.md").read_text())

  def test_plan_only_writes_nothing(self) -> None:
    """Without --apply the file and folder are unchanged."""
    with mock.patch("builtins.print"):
      ls.split("demo", apply=False)
    self.assertEqual((self.langs / "demo.md").read_text(), DOC)
    self.assertFalse((self.langs / "demo" / "notes.md").exists())

  def test_a_lossy_split_is_refused(self) -> None:
    """If the words would not survive (blocks dropped), nothing is written and the exit code is 1."""
    with mock.patch.object(ls, "blocks", return_value=[]), mock.patch("builtins.print"):
      self.assertEqual(ls.split("demo", apply=True), 1)
    self.assertEqual((self.langs / "demo.md").read_text(), DOC)

  def test_over_budget(self) -> None:
    """A file past 200 lines is reported; a small one is not."""
    big = self.langs / "big.md"
    big.write_text("x\n" * 250, encoding="utf-8")
    self.assertTrue(ls.over(big))
    self.assertEqual(ls.over(self.langs / "demo.md"), "")


if __name__ == "__main__":
  unittest.main()
