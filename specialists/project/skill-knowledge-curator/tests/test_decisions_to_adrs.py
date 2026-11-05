"""decisions_to_adrs: plan by default, refinements followed, accepted ADRs never overwritten, a rerun changes nothing.

Run: python -m unittest discover -s tests (or `just test`). Safety: files only, under a temporary folder.
"""

import contextlib
import importlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import helpers

decisions_to_adrs = importlib.import_module("decisions_to_adrs")

DECISIONS = [
  {
    "decision_id": "dr-000000000001",
    "conflict_id": "cf-aaaaaaaaaa",
    "action": "USE_OTHER",
    "answer_text": "Journal later",
    "reason": "First call.",
    "decided_at": "2026-11-01T10:00:00+11:00",
  },
  {
    "decision_id": "dr-000000000002",
    "previous_decision_id": "dr-000000000001",
    "conflict_id": "cf-aaaaaaaaaa",
    "action": "USE_OTHER",
    "answer_text": "Temporal in the first slice",
    "reason": "Refines dr-000000000001.",
    "decided_at": "2026-11-01T20:00:00+11:00",
  },
  {
    "decision_id": "dr-000000000003",
    "previous_decision_id": "dr-000000000002",
    "conflict_id": "cf-aaaaaaaaaa",
    "action": "AMEND",
    "reason": "Deferral superseded.",
    "decided_at": "2026-11-01T21:00:00+11:00",
  },
  {
    "decision_id": "dr-000000000004",
    "previous_decision_id": "dr-000000000003",
    "conflict_id": "cf-aaaaaaaaaa",
    "action": "AMEND",
    "reason": "Deferral superseded.",
    "decided_at": "2026-11-01T21:00:00+11:00",
  },
]


class DecisionsToAdrsTest(unittest.TestCase):
  """One group over a four-step refinement chain."""

  def setUp(self):
    """Write a ledger, a page and a groups file."""
    self.assertTrue(helpers.SCRIPTS.is_dir())
    tmp = tempfile.TemporaryDirectory()
    self.addCleanup(tmp.cleanup)
    self.root = Path(tmp.name)
    (self.root / ".kc").mkdir()
    (self.root / ".kc/decisions.jsonl").write_text("".join(json.dumps(d) + "\n" for d in DECISIONS))
    (self.root / "docs").mkdir()
    (self.root / "docs/engine.md").write_text("# Engine\n")
    self.groups = self.root / "groups.json"
    self.groups.write_text(json.dumps([{"slug": "engine", "title": "Engine: Temporal", "decisions": ["dr-000000000001"], "page": "docs/engine.md"}]))
    self.adr = self.root / ".archcore/adr/engine.adr.md"

  def run_tool(self, *extra: str) -> tuple[int, str]:
    """Run the script and capture its output.

    Args:
      extra: further arguments.

    Returns:
      (exit code, stdout).
    """
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
      rc = decisions_to_adrs.main(["--project", str(self.root), "--groups", str(self.groups), "--stamp", "20261105_2102", *extra])
    return rc, buf.getvalue()

  def test_plan_writes_nothing(self):
    """Without --apply the plan names the file and writes nothing."""
    rc, out = self.run_tool()
    self.assertEqual(rc, 0)
    self.assertIn("create:", out)
    self.assertFalse(self.adr.exists())

  def test_chain_followed_and_amendments_folded(self):
    """All four decisions appear; the two identical amendments share one row; the title is quoted YAML."""
    self.assertEqual(self.run_tool("--apply")[0], 0)
    text = self.adr.read_text()
    for i in range(1, 5):
      self.assertIn(f"dr-00000000000{i}", text)
    self.assertIn("| `dr-000000000003`, `dr-000000000004` |", text)
    self.assertIn('title: "Engine: Temporal"', text)
    self.assertIn("](../../docs/engine.md)", text)

  def test_rerun_unchanged_and_accepted_kept(self):
    """A second apply changes nothing; an accepted ADR is skipped, not overwritten."""
    self.run_tool("--apply")
    self.assertIn("unchanged:", self.run_tool("--apply")[1])
    accepted = self.adr.read_text().replace("status: proposed", "status: accepted") + "Operator note.\n"
    self.adr.write_text(accepted)
    self.assertIn("skipped (not proposed):", self.run_tool("--apply")[1])
    self.assertEqual(self.adr.read_text(), accepted)

  def test_unknown_decision_refused(self):
    """An unknown decision id fails closed with exit 1."""
    self.groups.write_text(json.dumps([{"slug": "x", "title": "X", "decisions": ["dr-ffffffffffff"], "page": "docs/engine.md"}]))
    with contextlib.redirect_stderr(io.StringIO()):
      self.assertEqual(self.run_tool("--apply")[0], 1)
    self.assertFalse((self.root / ".archcore/adr/x.adr.md").exists())


if __name__ == "__main__":
  unittest.main()
