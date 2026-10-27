"""Tests for the Vikunja seam (goal_guard_lib.vikunja) and snapshot/restore (goal_guard_lib.snapshot) against a fake instance.

Run: just test
Safety: files only, in a temporary folder; read-only for the pack; no network (the fake is the transport).
"""

import tempfile
import unittest
from pathlib import Path

from fake_vikunja import FakeVikunja
from helpers import Workspace, lib, raw_tasks

errors = lib("errors")
snapshot = lib("snapshot")
restore = lib("restore")


class Client(unittest.TestCase):
  """Pagination, error translation and token handling."""

  def test_pagination_complete(self):
    """Five tasks over pages of two are all read and marked complete."""
    fake = FakeVikunja(per_page=2)
    for i in range(5):
      fake.tasks[i + 1] = {"id": i + 1, "project_id": 7, "title": f"t{i}", "related": {}}
    tasks, completeness = fake.client().project_tasks(7)
    self.assertEqual((len(tasks), completeness["complete"], completeness["pages"]), (5, True, 3))

  def test_auth_rejected_hides_token(self):
    """A rejected token raises VikunjaAuthRejected without the token in the message."""
    cfg = lib("settings").load({"GG_VIKUNJA_URL": "http://fake", "GG_VIKUNJA_TOKEN": "tk_wrong_token"})
    with self.assertRaises(errors.VikunjaAuthRejected) as caught:
      lib("vikunja").Client(cfg, transport=FakeVikunja()).info()
    self.assertNotIn("tk_wrong_token", str(caught.exception))

  def test_not_found(self):
    """404 maps to VikunjaNotFound."""
    with self.assertRaises(errors.VikunjaNotFound):
      FakeVikunja().client().task(999)

  def test_missing_settings(self):
    """No URL is a ConfigError naming the variable."""
    with self.assertRaises(errors.ConfigError) as caught:
      lib("vikunja").Client(lib("settings").load({}))
    self.assertIn("GG_VIKUNJA_URL", str(caught.exception))


class Snapshot(unittest.TestCase):
  """Export, verify and clean-instance restore."""

  def export(self, ws, out: Path, items=None, complete=True, apply=True) -> Path:
    """Export the example tasks of the spoke.

    Args:
      ws: the workspace.
      out: snapshot root.
      items: raw tasks (default the example project's).
      complete: completeness flag.
      apply: write.

    Returns:
      The project snapshot folder.
    """
    items = [t for t in raw_tasks() if t["project_id"] == 7] if items is None else items
    completeness = {"total": len(items), "fetched": len(items), "complete": complete}
    snapshot.export(ws.project(), items, completeness, {"instance": "test", "version": "v2.7.1"}, out, apply)
    return out / "apn" / "demo-spoke"

  def test_export_plan_writes_nothing(self):
    """Without apply nothing is written."""
    with Workspace() as ws, tempfile.TemporaryDirectory() as tmp:
      self.assertFalse(self.export(ws, Path(tmp), apply=False).exists())

  def test_partial_export_refused(self):
    """A partial read never replaces the snapshot (S04)."""
    with Workspace() as ws, tempfile.TemporaryDirectory() as tmp, self.assertRaises(errors.WriteRefused):
      self.export(ws, Path(tmp), complete=False)

  def test_verify_and_tamper(self):
    """A clean export verifies; an edited tasks.json fails its checksum."""
    with Workspace() as ws, tempfile.TemporaryDirectory() as tmp:
      folder = self.export(ws, Path(tmp))
      self.assertTrue(snapshot.verify(folder)["ok"])
      self.assertTrue(snapshot.verify_parent(folder.parent)["ok"])
      tasks_file = folder / "tasks.json"
      tasks_file.write_text(tasks_file.read_text().replace("device X", "device Y"))
      self.assertIn("tasks.json: checksum mismatch", snapshot.verify(folder)["issues"])

  def test_no_users_exported(self):
    """Assignees and creators are not in the snapshot (S07)."""
    with Workspace() as ws, tempfile.TemporaryDirectory() as tmp:
      items = [dict(t, assignees=[{"username": "someone"}], created_by={"username": "someone"}) for t in raw_tasks() if t["project_id"] == 7]
      folder = self.export(ws, Path(tmp), items=items)
      self.assertNotIn("someone", (folder / "tasks.json").read_text())

  def test_restore_round_trip_and_idempotent(self):
    """Restore creates tasks and the blocking edge, reads back equal, and a rerun creates nothing."""
    with Workspace() as ws, tempfile.TemporaryDirectory() as tmp:
      folder = self.export(ws, Path(tmp))
      fake = FakeVikunja(per_page=50)
      plan = restore.restore(folder, fake.client(), 3, apply=False)
      self.assertEqual((plan["plan"]["create_tasks"], plan["plan"]["create_relations"]), (4, 1))
      self.assertEqual(fake.tasks, {})
      done = restore.restore(folder, fake.client(), 3, apply=True)
      self.assertTrue(done["verify"]["ok"], done["verify"]["mismatches"])
      again = restore.restore(folder, fake.client(), 3, apply=True)
      self.assertEqual((again["plan"]["create_tasks"], again["plan"]["create_relations"]), (0, 0))
      self.assertEqual(len(fake.tasks), 4)

  def test_restore_refuses_dirty_target(self):
    """A target with tasks Goal Guard did not restore is not a clean instance."""
    with Workspace() as ws, tempfile.TemporaryDirectory() as tmp:
      folder = self.export(ws, Path(tmp))
      fake = FakeVikunja()
      fake.tasks[1] = {"id": 1, "project_id": 3, "title": "someone's task", "description": "", "related": {}}
      with self.assertRaises(errors.WriteRefused):
        restore.restore(folder, fake.client(), 3, apply=True)

  def test_snapshot_readable_as_task_source(self):
    """An exported tasks.json loads as an offline task source, never live."""
    with Workspace() as ws, tempfile.TemporaryDirectory() as tmp:
      folder = self.export(ws, Path(tmp))
      task_set = lib("tasks").from_file(folder / "tasks.json")
    self.assertEqual((task_set.live, task_set.tasks[102].prerequisites), (False, (101,)))
    self.assertTrue(task_set.source.startswith("snapshot:"))


if __name__ == "__main__":
  unittest.main()
