"""Offline tests for pad_done_backfill.statement: built from the item's own comments, nothing invented. Run: python3 -m unittest tests/test_pad_done_backfill.py"""

import importlib.util
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location("pad_done_backfill", Path(__file__).resolve().parents[1] / "scripts" / "pad_done_backfill.py")
pdb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pdb)


class Statement(unittest.TestCase):
  """The closing statement quotes the newest substantive comment, skips items already closed, and says what it cannot know."""

  def test_quotes_newest_substantive_comment(self) -> None:
    """The result quotes the newest comment over 40 characters, with its id and date."""
    cs = [
      {"id": "aaaaaaaa-1", "body": "short", "created_at": "2026-11-18T10:00:00Z"},
      {"id": "bbbbbbbb-2", "body": "Built and pushed 1234abc; the gate passed 11/11 on the Mac and Linux.", "created_at": "2026-11-19T10:00:00Z"},
    ]
    got = pdb.statement("Do a thing", "done", cs, "2026-11-21 19:45")
    self.assertIn("2026-11-21 19:45 AEDT DONE:", got)
    self.assertIn("comment bbbbbbbb (2026-11-19): Built and pushed 1234abc", got)
    self.assertIn("not recorded", got)

  def test_item_with_closing_statement_is_skipped(self) -> None:
    """An item that already has DONE: or CLOSED: gets nothing."""
    cs = [{"id": "c", "body": "2026-11-20 10:00 AEDT DONE:\n- **What:** x", "created_at": "2026-11-20"}]
    self.assertIsNone(pdb.statement("t", "done", cs, "s"))

  def test_no_substantive_comment_says_not_recorded(self) -> None:
    """With nothing to quote, the result and evidence read not recorded."""
    got = pdb.statement("t", "resolved", [{"id": "x", "body": "ok", "created_at": "2026-11-20"}], "s")
    self.assertIn("**Result:** not recorded", got)


class Field(unittest.TestCase):
  """Fields read from a JSON string or an object."""

  def test_fields_as_string_or_object(self) -> None:
    """Pad 0.21 returns fields as a JSON string; an object works too."""
    self.assertEqual(pdb.field({"fields": '{"status": "done"}'}, "status"), "done")
    self.assertEqual(pdb.field({"fields": {"status": "resolved"}}, "status"), "resolved")
    self.assertEqual(pdb.field({"fields": "not json"}, "status"), "?")


if __name__ == "__main__":
  unittest.main()
