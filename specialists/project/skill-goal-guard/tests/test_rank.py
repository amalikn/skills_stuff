"""Tests for What's Next (goal_guard_lib.rank) against references/whats-next-and-portfolio.md.

Run: just test
Safety: files only, in a temporary copy of examples/project_stuff; no network.
"""

import dataclasses
import datetime as dt
import unittest

from helpers import Workspace, lib, tasks

rank = lib("rank")
TODAY = dt.date(2026, 10, 27)


def ranked(ws: Workspace, task_set=None, today=TODAY, **kw) -> dict:
  """Rank the workspace spoke.

  Args:
    ws: the workspace.
    task_set: tasks to use (default the example set).
    today: the date ranked for.
    **kw: focus or task_in_focus.

  Returns:
    The whats_next result.
  """
  proj = ws.project()
  return rank.whats_next([proj], {proj.project_id: ws.baseline(proj)}, task_set or tasks(), today, 14, **kw)


def with_task(task_set, task_id: int, **changes):
  """Return a copy of a TaskSet with one task changed.

  Args:
    task_set: the source.
    task_id: the task to change.
    **changes: Task fields to replace.

  Returns:
    A new TaskSet.
  """
  new = dict(task_set.tasks)
  new[task_id] = dataclasses.replace(new[task_id], **changes)
  return dataclasses.replace(task_set, tasks=new)


class WhatsNext(unittest.TestCase):
  """Filter, order and three levels."""

  def test_focus_is_only_eligible_task(self):
    """101 is the one mapped, open task with prerequisites done; 103 is unmapped, 102 blocked."""
    with Workspace() as ws:
      out = ranked(ws)
    self.assertEqual((out["portfolio"]["status"], out["portfolio"]["task_id"]), ("FOCUS", 101))
    reasons = {e["task_id"]: e["reason"] for e in out["projects"][0]["excluded"]}
    self.assertIn("no accepted criterion", reasons[103])
    self.assertIn("waits on [101]", reasons[102])

  def test_started_beats_higher_priority(self):
    """With 102 unblocked and higher priority, started 101 is still finished first (GG-101)."""
    with Workspace() as ws:
      t = with_task(tasks(), 102, prerequisites=())
      out = ranked(ws, t, today=dt.date(2026, 1, 1))
    self.assertEqual(out["portfolio"]["task_id"], 101)
    self.assertIn("started work", out["portfolio"]["why_first"])

  def test_owner_focus_first(self):
    """The owner's selected task outranks started work."""
    with Workspace() as ws:
      out = ranked(ws, with_task(tasks(), 102, prerequisites=()), focus=102)
    self.assertEqual(out["portfolio"]["task_id"], 102)

  def test_deadline_pressure_beats_started(self):
    """A task due inside the window beats a started task outside it."""
    with Workspace() as ws:
      t = with_task(with_task(tasks(), 102, prerequisites=(), due=dt.date(2026, 10, 30)), 101, due=None)
      ws.edit_yaml(".gg/mappings.yaml", milestones=[])
      out = ranked(ws, t)
    self.assertEqual(out["portfolio"]["task_id"], 102)

  def test_no_baseline_is_blocked(self):
    """Without an approved baseline the portfolio is BLOCKED, naming what it waits for."""
    with Workspace() as ws:
      ws.edit_yaml(".gg/mvp.yaml", status="draft")
      out = ranked(ws)
    self.assertEqual(out["portfolio"]["status"], "BLOCKED")
    self.assertTrue(out["portfolio"]["waiting"])

  def test_task_level_blocked_and_review(self):
    """Task level names the blockers, and REVIEW when no concrete next action is written (GG-106)."""
    with Workspace() as ws:
      self.assertEqual(ranked(ws, task_in_focus=102)["task"]["blocked_by"], [101])
      out = ranked(ws, with_task(tasks(), 101, description="work on controller"), task_in_focus=101)
    self.assertEqual(out["task"]["status"], "REVIEW")

  def test_alerts_and_unknown_forecast(self):
    """Past the internal target and near the commitment: both alerts, forecast unknown (DATE-003, DATE-005)."""
    with Workspace() as ws:
      out = ranked(ws, today=dt.date(2026, 12, 5))
    kinds = {a["kind"] for a in out["at_risk"]}
    self.assertTrue({"internal_target_breach", "deadline_at_risk", "not_live"} <= kinds)
    self.assertEqual(out["projects"][0]["next_milestone"]["forecast"], "unknown")

  def test_partitions_never_mixed(self):
    """Apn and me are ranked separately."""
    with Workspace() as ws:
      apn = ws.project()
      me = lib("project").load(ws.root / "me" / "demo-personal")
      with self.assertRaises(lib("errors").ConfigError):
        rank.whats_next([apn, me], {}, tasks(), TODAY, 14)


if __name__ == "__main__":
  unittest.main()
