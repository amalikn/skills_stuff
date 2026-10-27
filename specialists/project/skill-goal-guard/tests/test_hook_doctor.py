"""Tests for the PreToolUse adapter (goal_guard_lib.hook) and the doctor's hook detection (goal_guard_lib.doctor).

Run: just test
Safety: files only, in temporary folders; no network.
"""

import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path

from helpers import NOW, Workspace, lib

hook = lib("hook")
doctor = lib("doctor")
CFG = lib("settings").load({})


def payload(ws: Workspace, file_path: str, tool: str = "Write") -> dict:
  """Build a documented PreToolUse payload for a write in the spoke.

  Args:
    ws: the workspace.
    file_path: path relative to the spoke.
    tool: tool name.

  Returns:
    The payload mapping.
  """
  key = "notebook_path" if tool == "NotebookEdit" else "file_path"
  return {
    "session_id": "s",
    "transcript_path": "/t",
    "cwd": str(ws.spoke),
    "permission_mode": "default",
    "hook_event_name": "PreToolUse",
    "tool_name": tool,
    "tool_input": {key: file_path, "content": "x"},
  }


def record_proceed(ws: Workspace, at: dt.datetime = NOW, revision: str = "DEMO-MVP-001@1") -> None:
  """Append a PROCEED verdict to the spoke's log, dated at a given time.

  Args:
    ws: the workspace.
    at: the verdict time written into the entry.
    revision: the contract revision it names.
  """
  log = lib("decisions_log")
  path = ws.spoke / ".gg/decisions.jsonl"
  last = path.read_text().splitlines()[-1]
  verdict = {"verdict": "PROCEED", "proposal_id": "P-1", "task_id": 101, "contract_revision": revision, "details": {"proposed_files": ["src/a.py"]}}
  entry = log.build_entry("verdict", "agent", revision, "r", [], verdict, log.line_hash(last))
  entry["at"] = at.isoformat()
  with path.open("a") as handle:
    handle.write(json.dumps(entry, separators=(",", ":")) + "\n")


class Hook(unittest.TestCase):
  """Deny, warn and pass rules."""

  def test_blocking_without_verdict(self):
    """No PROCEED on record: blocking exits 2 with a reason on stderr."""
    with Workspace() as ws:
      out = hook.evaluate(payload(ws, "src/a.py"), CFG, "blocking", NOW)
    self.assertEqual((out.exit_code, out.decision), (2, "deny"))
    self.assertIn("assess", out.stderr)

  def test_advisory_never_blocks(self):
    """Advisory mode exits 0 and puts the warning in additionalContext."""
    with Workspace() as ws:
      out = hook.evaluate(payload(ws, "src/a.py"), CFG, "advisory", NOW)
    self.assertEqual(out.exit_code, 0)
    self.assertIn("additionalContext", json.loads(out.stdout)["hookSpecificOutput"])

  def test_fresh_proceed_passes_silently(self):
    """With a fresh PROCEED the hook prints nothing (no 'allow', which would skip permission prompts)."""
    with Workspace() as ws:
      record_proceed(ws)
      out = hook.evaluate(payload(ws, "src/a.py"), CFG, "blocking", NOW + dt.timedelta(minutes=30))
    self.assertEqual((out.exit_code, out.stdout, out.stderr), (0, "", ""))

  def test_stale_proceed_denied(self):
    """A verdict older than the limit no longer covers edits."""
    with Workspace() as ws:
      record_proceed(ws)
      self.assertEqual(hook.evaluate(payload(ws, "src/a.py"), CFG, "blocking", NOW + dt.timedelta(hours=3)).exit_code, 2)

  def test_file_outside_verdict_denied(self):
    """One PROCEED covers the files its proposal named, not the whole project."""
    with Workspace() as ws:
      record_proceed(ws)
      out = hook.evaluate(payload(ws, "src/other.py"), CFG, "blocking", NOW)
    self.assertEqual(out.exit_code, 2)
    self.assertIn("not in the files of PROCEED", out.stderr)

  def test_verdict_for_other_revision_denied(self):
    """A PROCEED against another contract revision does not count."""
    with Workspace() as ws:
      record_proceed(ws, revision="DEMO-MVP-001@0")
      self.assertEqual(hook.evaluate(payload(ws, "src/a.py"), CFG, "blocking", NOW).exit_code, 2)

  def test_protected_record_denied_even_with_proceed(self):
    """An agent never edits the MVP contract or the hub plan directly."""
    with Workspace() as ws:
      record_proceed(ws)
      for target in (".gg/mvp.yaml", "../demo-hub/plan.md"):
        self.assertEqual(hook.evaluate(payload(ws, target, "Edit"), CFG, "blocking", NOW).exit_code, 2, target)

  def test_outside_projects_and_other_tools_pass(self):
    """Unregistered folders and non-write tools are not gated."""
    with Workspace() as ws, tempfile.TemporaryDirectory() as tmp:
      self.assertEqual(hook.evaluate(payload(ws, str(Path(tmp) / "a.py")), CFG, "blocking", NOW).decision, "allow")
      bash = dict(payload(ws, "x"), tool_name="Bash", tool_input={"command": "ls"})
      self.assertEqual(hook.evaluate(bash, CFG, "blocking", NOW).decision, "ignore")

  def test_unrecognised_payload_fails_closed(self):
    """A payload the adapter does not recognise is denied in blocking mode."""
    with Workspace() as ws:
      broken = dict(payload(ws, "x"), tool_input={"path": "src/a.py"})
      for item in ("garbage", {"tool_name": "Write"}, broken):
        self.assertEqual(hook.evaluate(item, CFG, "blocking", NOW).exit_code, 2, item)

  def test_capture_redacts_content(self):
    """Captures keep the shape and drop long contents."""
    with Workspace() as ws, tempfile.TemporaryDirectory() as tmp:
      p = payload(ws, "src/a.py")
      p["tool_input"]["content"] = "x" * 500
      path = hook.capture(p, hook.evaluate(p, CFG, "advisory", NOW), Path(tmp), NOW)
      saved = json.loads(path.read_text())
    self.assertEqual(saved["payload"]["tool_input"]["content"], "<500 chars>")


class Doctor(unittest.TestCase):
  """Hook wiring detection and honest status."""

  def test_wired_blocking_is_not_enforced_without_observation(self):
    """A blocking hook with no observed block is reported as not yet enforced."""
    with Workspace() as ws, tempfile.TemporaryDirectory() as home:
      (ws.spoke / ".claude").mkdir()
      entry = {"matcher": "Edit|Write", "hooks": [{"type": "command", "command": "py goal_guard_hook.py --mode blocking"}]}
      (ws.spoke / ".claude/settings.json").write_text(json.dumps({"hooks": {"PreToolUse": [entry]}}))
      report = doctor.report(ws.spoke, CFG, False, Path(home))
    status = {p["path"]: p["status"] for p in report["paths"]}
    self.assertIn("NOT yet observed", status["Edit tool"])
    self.assertTrue(status["MultiEdit tool"].startswith("advisory: no hook"))
    self.assertTrue(status["Bash and other shell writes"].startswith("unsupported"))


if __name__ == "__main__":
  unittest.main()
