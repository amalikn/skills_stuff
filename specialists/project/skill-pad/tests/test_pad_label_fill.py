"""Offline tests for pad_label_fill.fill: missing required labels are added in template order, nothing is invented. Run: python3 -m unittest tests/test_pad_label_fill.py"""

import importlib.util
import unittest
from pathlib import Path

_root = Path(__file__).resolve().parents[1] / "scripts"


def _load(name: str):
  """Load a script as a module by path (scripts are run with -I, not imported as a package)."""
  spec = importlib.util.spec_from_file_location(name, _root / f"{name}.py")
  mod = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(mod)
  return mod


plf = _load("pad_label_fill")
pic = _load("pad_item_check")


class Fill(unittest.TestCase):
  """Each rule can apply, and a complete body is left alone."""

  def test_table_matches_item_check(self) -> None:
    """The required labels are the item check's, collection by collection."""
    for coll, labels in plf.REQUIRED.items():
      self.assertEqual(tuple(pic.LABELS[coll]), labels, coll)

  def test_missing_why_goes_after_serves_as_not_recorded(self) -> None:
    """A task without Why gets it after Serves; Do and the rest keep their place."""
    body = "**Serves:** X\n\n**Do:** y\n\n**Done when:** z\n\n**Writes:** repo\n\n**Refs:** r"
    want = "**Serves:** X\n\n**Why:** not recorded (template pass 2026-11-21)\n\n**Do:** y\n\n**Done when:** z\n\n**Writes:** repo\n\n**Refs:** r"
    self.assertEqual(plf.fill("tasks", "t", body, "2026-11-21"), want)

  def test_ask_question_is_the_title(self) -> None:
    """An ask without Question takes its title, the question as asked."""
    self.assertEqual(plf.fill("asks", "Who holds the keys?", "**Serves:** DL-1", "d"), "**Question:** Who holds the keys?\n\n**Serves:** DL-1")

  def test_convention_rule_labels_first_paragraph(self) -> None:
    """A convention's first unlabelled paragraph becomes its Rule, words unchanged; Source reads not recorded."""
    got = plf.fill("conventions", "c", "Never push red.\n\n**Why:** CI", "d")
    self.assertEqual(got, "**Rule:** Never push red.\n\n**Source:** not recorded (template pass d)\n\n**Why:** CI")

  def test_one_line_feature_request_and_complete_body_unchanged(self) -> None:
    """A one-line request is kept as written, and a body with every label is untouched."""
    self.assertEqual(plf.fill("feature-requests", "f", "Add dark mode", "d"), "Add dark mode")
    full = "**Serves:** a\n\n**Why:** b\n\n**Do:** c\n\n**Done when:** d"
    self.assertEqual(plf.fill("tech-debt", "t", full, "d"), full)


if __name__ == "__main__":
  unittest.main()
