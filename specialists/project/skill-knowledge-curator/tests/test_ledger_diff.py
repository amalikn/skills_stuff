"""ledger_diff: a rehearsal on a scratch copy is compared with the live ledger, end state only.

Run: python -m unittest discover -s tests (or `just test`). Safety: files only, under a temporary folder.
"""

import importlib
import json
import tempfile
import unittest
from pathlib import Path

import helpers

ledger_diff = importlib.import_module("ledger_diff")


def write_ledger(root: Path, claims: list[dict], conflicts: list[dict]) -> Path:
  """Write a minimal `.kc` ledger.

  Args:
    root: project root to create.
    claims: claim ledger records.
    conflicts: conflict ledger records.

  Returns:
    The project root.
  """
  kc = root / ".kc"
  kc.mkdir(parents=True)
  (kc / "claims.jsonl").write_text("".join(json.dumps(r) + "\n" for r in claims))
  (kc / "conflicts.jsonl").write_text("".join(json.dumps(r) + "\n" for r in conflicts))
  return root


def disposition(cid: str, state: str, successor: str | None = None) -> dict:
  """Build one disposition record.

  Args:
    cid: claim id.
    state: disposition.
    successor: successor claim id, when any.

  Returns:
    The record.
  """
  return {"record": "disposition", "claim_id": cid, "disposition": state, "successor": successor}


class LedgerDiffTest(unittest.TestCase):
  """The folded end state decides, not the number of records."""

  def setUp(self):
    """Create a temporary folder for two projects."""
    tmp = tempfile.TemporaryDirectory()
    self.addCleanup(tmp.cleanup)
    self.tmp = Path(tmp.name)
    self.assertTrue(helpers.ROOT.exists())

  def test_changed_successor_is_reported(self):
    """A claim superseded on both sides with another successor is a difference."""
    before = write_ledger(self.tmp / "a", [disposition("c1", "SUPERSEDED", "c2")], [{"conflict_id": "f1", "status": "open", "claims": ["c1"]}])
    after = write_ledger(self.tmp / "b", [disposition("c1", "SUPERSEDED", "c3")], [{"conflict_id": "f1", "status": "open", "claims": ["c1"]}])
    result = ledger_diff.diff(before, after)
    self.assertEqual(result["claims"], {"c1": (("SUPERSEDED", "c2"), ("SUPERSEDED", "c3"))})
    self.assertEqual(result["conflicts"], {})

  def test_extra_records_with_same_end_state_match(self):
    """A re-decision that lands where it started shows nothing."""
    before = write_ledger(self.tmp / "a", [disposition("c1", "CURRENT")], [{"conflict_id": "f1", "status": "open", "claims": ["c1"]}])
    after = write_ledger(
      self.tmp / "b",
      [disposition("c1", "CURRENT"), disposition("c1", "SUPERSEDED", "c2"), disposition("c1", "CURRENT")],
      [{"conflict_id": "f1", "status": "open", "claims": ["c1"]}, {"conflict_id": "f1", "decided_by": "d1"}],
    )
    self.assertEqual(ledger_diff.diff(before, after), {"claims": {}, "conflicts": {}})

  def test_conflict_status_and_members_are_reported(self):
    """A closed conflict and an added claim both show."""
    before = write_ledger(self.tmp / "a", [], [{"conflict_id": "f1", "status": "open", "claims": ["c1"]}])
    after = write_ledger(self.tmp / "b", [], [{"conflict_id": "f1", "status": "resolved", "claims": ["c1", "c2"]}])
    self.assertEqual(ledger_diff.diff(before, after)["conflicts"], {"f1": (("open", ("c1",)), ("resolved", ("c1", "c2")))})

  def test_missing_ledger_raises(self):
    """A project with no ledger is an error, not an empty diff."""
    with self.assertRaises(FileNotFoundError):
      ledger_diff.diff(self.tmp / "none", self.tmp / "none")


if __name__ == "__main__":
  unittest.main()
