"""End-to-end tests of the front ends: run each script as a subprocess and check its exit code and output.

Run: just test
Safety: read-only for the pack; assess --apply writes only into a temporary copy of examples/project_stuff. No network.
"""

import json
import os
import subprocess
import sys
import unittest

from helpers import EXAMPLES, ROOT, Workspace

TIMEOUT = 30
TASKS = str(EXAMPLES / "vikunja-tasks.json")


def run(*args: str, stdin: str = "", env: dict | None = None) -> subprocess.CompletedProcess:
  """Run one script with the test interpreter.

  Args:
    *args: script path relative to the pack, then its arguments.
    stdin: text for standard input.
    env: extra environment variables.

  Returns:
    The completed process (text output).
  """
  full_env = {**os.environ, "GG_PARTITION": "apn", **(env or {})}
  return subprocess.run(
    [sys.executable, str(ROOT / args[0]), *args[1:]], input=stdin, capture_output=True, text=True, timeout=TIMEOUT, env=full_env, check=False
  )


class FrontEnds(unittest.TestCase):
  """Exit codes: 0 success, 3 negative answer, 2 bad input."""

  def test_assess_exit_codes(self):
    """PROCEED exits 0; BLOCK exits 3."""
    with Workspace() as ws:
      ok = run("scripts/goal_guard.py", "assess", "--project", str(ws.spoke), "--proposal", str(EXAMPLES / "proposals/proceed.yaml"), "--tasks", TASKS)
      blocked = run(
        "scripts/goal_guard.py", "assess", "--project", str(ws.spoke), "--proposal", str(EXAMPLES / "proposals/block-excluded.yaml"), "--tasks", TASKS
      )
    self.assertEqual((ok.returncode, json.loads(ok.stdout)["verdict"]["verdict"]), (0, "PROCEED"))
    self.assertEqual(blocked.returncode, 3)

  def test_apply_then_hook(self):
    """Recording a PROCEED with assess --apply: the hook then passes a listed file and blocks an unlisted one."""
    with Workspace() as ws:
      run("scripts/goal_guard.py", "assess", "--project", str(ws.spoke), "--proposal", str(EXAMPLES / "proposals/proceed.yaml"), "--tasks", TASKS, "--apply")
      results = {}
      for name in ("src/collector.py", "src/other.py"):
        payload = {"hook_event_name": "PreToolUse", "tool_name": "Write", "tool_input": {"file_path": name, "content": "x"}, "cwd": str(ws.spoke)}
        results[name] = run("scripts/goal_guard_hook.py", "--mode", "blocking", stdin=json.dumps(payload)).returncode
    self.assertEqual(results, {"src/collector.py": 0, "src/other.py": 2})

  def test_bad_input_exits_2(self):
    """A missing project record is bad input."""
    with Workspace() as ws:
      out = run("scripts/goal_guard.py", "validate", "--project", str(ws.base))
    self.assertEqual(out.returncode, 2)
    self.assertIn("error:", out.stderr)

  def test_trace_and_doctor_on_fixture(self):
    """The fixture traces verified and the doctor reports no problems."""
    with Workspace() as ws:
      trace = run("scripts/goal_guard_trace.py", "--project", str(ws.spoke), "--tasks", TASKS)
      doctor = run("scripts/goal_guard_doctor.py", "--project", str(ws.spoke), env={"HOME": str(ws.base)})
    self.assertEqual((trace.returncode, doctor.returncode), (0, 0), trace.stderr + doctor.stderr)


if __name__ == "__main__":
  unittest.main()
