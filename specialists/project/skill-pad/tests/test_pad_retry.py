"""Tests for scripts/pad_retry.sh: retry on rate limiting, pass-through otherwise, stdin replayed. Run: python3 -m unittest tests.test_pad_retry"""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "pad_retry.sh"

FAKE = """#!/usr/bin/env bash
# Fake pad: refuses with 429 until the counter file reaches FAIL_TIMES, then echoes its args and stdin.
n=$(cat "$COUNTER" 2>/dev/null || echo 0); n=$((n + 1)); echo "$n" > "$COUNTER"
if [ "$n" -le "$FAIL_TIMES" ]; then echo 'Error: Too many requests. Please try again later. {"retry_after_seconds": 0}'; exit 1; fi
echo "ok args=$* stdin=$(cat)"
exit 0
"""


def run(fail_times: int, args: list[str], stdin: str | None, tries: int = 6) -> tuple[subprocess.CompletedProcess, int]:
  """Run pad_retry.sh against the fake pad.

  Args:
    fail_times: how many calls the fake refuses before succeeding.
    args: the pad arguments.
    stdin: text fed on stdin, or None for none.
    tries: PAD_RETRY_TRIES.

  Returns:
    The completed process and the number of fake calls made.
  """
  with tempfile.TemporaryDirectory() as d:
    fake = Path(d) / "pad"
    fake.write_text(FAKE)
    fake.chmod(0o755)
    counter = Path(d) / "n"
    env = dict(os.environ, PAD_BIN=str(fake), COUNTER=str(counter), FAIL_TIMES=str(fail_times), PAD_RETRY_TRIES=str(tries))
    env["PATH"] = "/usr/bin:/bin:" + env.get("PATH", "")
    proc = subprocess.run(
      ["bash", str(SCRIPT), *args],
      input=stdin if stdin is not None else "",
      capture_output=True,
      text=True,
      env=env,
      timeout=120,
    )
    return proc, int(counter.read_text().strip())


class PadRetryTest(unittest.TestCase):
  """Behaviour of the retry wrapper."""

  def test_retries_until_success_and_replays_stdin(self) -> None:
    """Two refusals, then success: three calls, stdin seen on the last one."""
    proc, calls = run(2, ["item", "comment", "TASK-1", "--stdin"], "- **What:** x")
    self.assertEqual(proc.returncode, 0, proc.stderr)
    self.assertEqual(calls, 3)
    self.assertIn("stdin=- **What:** x", proc.stdout)

  def test_gives_up_after_tries(self) -> None:
    """Always refused: stops at the try limit with the failure's exit code."""
    proc, calls = run(99, ["item", "show", "TASK-1"], None, tries=3)
    self.assertNotEqual(proc.returncode, 0)
    self.assertEqual(calls, 3)
    self.assertIn("Too many requests", proc.stdout)

  def test_no_retry_on_other_errors(self) -> None:
    """A success on the first call is passed straight through."""
    proc, calls = run(0, ["item", "show", "TASK-1"], None)
    self.assertEqual(proc.returncode, 0)
    self.assertEqual(calls, 1)

  def test_bad_usage(self) -> None:
    """No arguments is bad usage (exit 2)."""
    proc = subprocess.run(["bash", str(SCRIPT)], capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL)
    self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
  unittest.main()
