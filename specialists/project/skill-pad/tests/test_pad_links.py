"""Offline tests for pad_links.linked(): item refs and decision ids become wiki-links, protected text is left alone. Run: python3 -m unittest test_pad_links."""

import importlib.util
import json
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location("pad_links", Path(__file__).resolve().parents[1] / "scripts" / "pad_links.py")
pl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pl)

REFS = {"TASK-12", "BUG-73", "DECIS-201", "DECIS-210"}
DECISIONS = {"DL-058": "DECIS-201", "D17": "DECIS-210"}


class Linked(unittest.TestCase):
  """linked() rewrites bare references only."""

  def test_item_refs(self):
    """A known ref is linked, an unknown one and the item's own ref are not.

    Returns:
        None.
    """
    self.assertEqual(pl.linked("See TASK-12, BUG-73 and TASK-99.", "BUG-73", REFS, DECISIONS), "See [[TASK-12]], BUG-73 and TASK-99.")

  def test_decision_log_id(self):
    """A mirrored DL id shows as the id and links to its mirror.

    Returns:
        None.
    """
    self.assertEqual(pl.linked("Per DL-058.", "TASK-1", REFS, DECISIONS), "Per [[DECIS-201|DL-058]].")

  def test_register_id(self):
    """A mirrored register id is linked; a bug id or sub-option built on it, and an unmirrored id, are not (2026-11-20).

    Returns:
        None.
    """
    body = "D17 decided; D17-03 is a bug; D17.2 is an option; D99 is unknown."
    self.assertEqual(pl.linked(body, "TASK-1", REFS, DECISIONS), "[[DECIS-210|D17]] decided; D17-03 is a bug; D17.2 is an option; D99 is unknown.")

  def test_protected(self):
    """Inline code, fenced blocks and existing links are left alone.

    Returns:
        None.
    """
    body = "`TASK-12` and [[TASK-12]] and\n```\nD17\n```\n"
    self.assertEqual(pl.linked(body, "TASK-1", REFS, DECISIONS), body)


class Comments(unittest.TestCase):
  """link_comments() edits agent comments only."""

  def test_agent_comment_linked_person_comment_kept(self):
    """An agent's status comment gains the link; the operator's own comment is never edited.

    Returns:
        None.
    """
    rows = [{"id": "c1", "created_by": "agent", "body": "Unblocked: TASK-12 answered"}, {"id": "c2", "created_by": "user", "body": "see TASK-12"}]
    calls = []

    def fake(binary, timeout, *args, stdin=None):
      calls.append((args, stdin))
      return json.dumps(rows) if args[:2] == ("item", "comments") else ""

    real, pl.pad = pl.pad, fake
    try:
      self.assertEqual(pl.link_comments("pad", 5, "TASK-20", REFS, DECISIONS, True), 0)
    finally:
      pl.pad = real
    edits = [c for c in calls if c[0][:2] == ("item", "comment-edit")]
    self.assertEqual(edits, [(("item", "comment-edit", "TASK-20", "c1", "--stdin"), "Unblocked: [[TASK-12]] answered")])


if __name__ == "__main__":
  unittest.main()
