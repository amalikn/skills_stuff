"""Tests for the hash-chained decisions.jsonl writer (goal_guard_lib.decisions_log).

Run: just test
Safety: files only, in a temporary copy of examples/project_stuff.
"""

import unittest

from helpers import Workspace, lib

log = lib("decisions_log")
errors = lib("errors")


class DecisionLog(unittest.TestCase):
  """Plan versus apply, chain checks and refused kinds."""

  def test_plan_writes_nothing(self):
    """Without apply the file is unchanged."""
    with Workspace() as ws:
      path = ws.spoke / ".gg/decisions.jsonl"
      before = path.read_text()
      result = log.append(path, "verdict", "agent", "DEMO-MVP-001@1", "r", [], {"verdict": "PROCEED"}, apply=False)
      self.assertFalse(result["applied"])
      self.assertEqual(path.read_text(), before)

  def test_apply_appends_and_chains(self):
    """Two applied lines chain to the approval line and read back clean."""
    with Workspace() as ws:
      path = ws.spoke / ".gg/decisions.jsonl"
      log.append(path, "verdict", "agent", "R", "r", [], {"verdict": "PROCEED"}, apply=True)
      log.append(path, "park", "agent", "R", "r", [], {"idea": "x"}, apply=True)
      entries, issues = log.read(path)
    self.assertEqual((len(entries), issues), (3, []))
    self.assertEqual(log.latest_verdict(entries)["payload"]["verdict"], "PROCEED")

  def test_edited_history_detected(self):
    """Changing an earlier line breaks the chain, and appending is refused."""
    with Workspace() as ws:
      path = ws.spoke / ".gg/decisions.jsonl"
      log.append(path, "verdict", "agent", "R", "r", [], {}, apply=True)
      path.write_text(path.read_text().replace("Fixture approval", "Edited approval"))
      _, issues = log.read(path)
      self.assertTrue(issues)
      with self.assertRaises(errors.WriteRefused):
        log.append(path, "verdict", "agent", "R", "r", [], {}, apply=True)

  def test_approval_kind_refused(self):
    """GoalGuard never writes an approval (MVP-007)."""
    with Workspace() as ws, self.assertRaises(errors.WriteRefused):
      log.append(ws.spoke / ".gg/decisions.jsonl", "approval", "agent", "R", "r", [], {}, apply=True)


if __name__ == "__main__":
  unittest.main()
