"""Offline tests for pad_monitor.sh against a fake pad binary: consent gate, lock dedupe, reconnect loop, missing pad. Run: python3 -m unittest test_pad_monitor."""

import os
import subprocess
import tempfile
import textwrap
import time
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pad_monitor.sh"

# The fake pad: `should-arm` succeeds while the count file holds fewer than ARMS lines; `watch --stream` prints one event and appends to the count.
FAKE = textwrap.dedent("""\
  #!/bin/sh
  d=$(dirname "$0")
  case "$1 $2" in
    "watch --help") exit 0 ;;
    "session register") echo reg >> "$d/register.log"; exit 0 ;;
    "session should-arm") n=$(cat "$d/count" 2>/dev/null | wc -l); [ "$n" -lt "${ARMS:-0}" ] ;;
    "watch --stream") echo "event $(cat "$d/count" 2>/dev/null | wc -l | tr -d ' ')"; echo x >> "$d/count"; exit 0 ;;
    *) exit 2 ;;
  esac
""")


def run(tmp, arms, sock="test-sock", pad=None, timeout=20):
  """Run the monitor once with the fake pad.

  Args:
    tmp: folder holding the fake pad and its state files.
    arms: how many stream attempts consent allows before should-arm fails.
    sock: value for CLAUDE_CODE_MESSAGING_SOCKET (the lock key).
    pad: PAD_BIN override; default the fake.
    timeout: seconds before the run is killed.

  Returns:
    subprocess.CompletedProcess with text stdout and stderr.
  """
  env = dict(os.environ, PAD_BIN=pad or str(Path(tmp) / "pad"), PAD_MONITOR_BACKOFF="0", ARMS=str(arms), TMPDIR=tmp, CLAUDE_CODE_MESSAGING_SOCKET=sock)
  return subprocess.run(["sh", str(SCRIPT)], env=env, capture_output=True, text=True, timeout=timeout)


class Monitor(unittest.TestCase):
  """pad_monitor.sh behaviour."""

  def setUp(self):
    """Create a temp folder with the executable fake pad.

    Returns:
      None.
    """
    self._td = tempfile.TemporaryDirectory()
    self.tmp = self._td.name
    fake = Path(self.tmp) / "pad"
    fake.write_text(FAKE)
    fake.chmod(0o755)

  def tearDown(self):
    """Remove the temp folder.

    Returns:
      None.
    """
    self._td.cleanup()

  def test_no_consent_exits_silently(self):
    """Without consent nothing streams, stdout stays empty, exit 0, and the session still registers.

    Returns:
      None.
    """
    r = run(self.tmp, arms=0)
    self.assertEqual((r.returncode, r.stdout), (0, ""))
    self.assertTrue((Path(self.tmp) / "register.log").exists())

  def test_reconnects_until_consent_withdrawn(self):
    """Each stream end reconnects while consent holds; the loop ends when should-arm fails, and the lock is freed.

    Returns:
      None.
    """
    r = run(self.tmp, arms=3)
    self.assertEqual(r.returncode, 0)
    self.assertEqual(r.stdout.splitlines(), ["event 0", "event 1", "event 2"])
    self.assertEqual(list(Path(self.tmp).glob("pad-monitor-*.lock")), [])

  def test_live_peer_holds_lock(self):
    """A second monitor of the same session exits 0 without streaming while a live process holds the lock.

    Returns:
      None.
    """
    first = subprocess.Popen(["sleep", "30"])
    try:
      key = subprocess.run(["sh", "-c", "printf '%s' test-sock | cksum | cut -d' ' -f1"], capture_output=True, text=True, timeout=5).stdout.strip()
      lock = Path(self.tmp) / f"pad-monitor-sess-{key}.lock"
      lock.mkdir()
      (lock / "pid").write_text(str(first.pid))
      r = run(self.tmp, arms=3)
      self.assertEqual((r.returncode, r.stdout), (0, ""))
      first.kill()
      first.wait(5)
      time.sleep(0.1)
      r = run(self.tmp, arms=1)
      self.assertEqual(r.stdout.splitlines(), ["event 0"], "a dead holder's lock is stolen")
    finally:
      if first.poll() is None:
        first.kill()

  def test_missing_pad(self):
    """A pad binary that does not exist exits 1 with one stderr line.

    Returns:
      None.
    """
    r = run(self.tmp, arms=1, pad=str(Path(self.tmp) / "nope"))
    self.assertEqual(r.returncode, 1)
    self.assertIn("pad CLI not found", r.stderr)


if __name__ == "__main__":
  unittest.main()
