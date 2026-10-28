"""Offline checks for rct_avr_probe.sh: it parses, prints its help, refuses bad arguments, and turns a box's answer into one line per node.

Run: python3 -m unittest test_rct_avr_probe (from scripts/probes/). No network: a stand-in `tsh` on PATH answers or fails.
"""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "rct_avr_probe.sh"


def run(*args: str, tsh: str | None = None) -> subprocess.CompletedProcess:
  """Run the script with arguments, optionally with a stand-in tsh first on PATH.

  Args:
    *args: command-line arguments.
    tsh: body of the stand-in tsh script, or None for the real PATH.

  Returns:
    The finished process.
  """
  env = dict(os.environ)
  if tsh is not None:
    d = Path(tempfile.mkdtemp())
    (d / "tsh").write_text(tsh)
    (d / "tsh").chmod(0o755)
    env["PATH"] = f"{d}:{env['PATH']}"
  return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True, timeout=30, check=False, env=env)


class RctAvrProbe(unittest.TestCase):
  """Argument handling and output shape, without reaching any SMC."""

  def test_parses(self) -> None:
    """bash -n finds no syntax error."""
    self.assertEqual(subprocess.run(["bash", "-n", str(SCRIPT)], check=False).returncode, 0)

  def test_help_and_usage_errors(self) -> None:
    """--help exits 0 with the usage line and stops at the header; no proxy, no node or an unknown option exit 2."""
    shown = run("--help")
    self.assertEqual(shown.returncode, 0)
    self.assertIn("usage: rct_avr_probe.sh", shown.stdout)
    self.assertNotIn("set -u", shown.stdout)
    self.assertEqual(run().returncode, 2)
    self.assertEqual(run("--proxy", "p").returncode, 2)
    self.assertEqual(run("--bogus", "x").returncode, 2)

  def test_answer_and_failure_lines(self) -> None:
    """A node that answers gives an AVRPROBE line named by the node; one that does not gives FAIL and exit 1."""
    answers = '#!/bin/sh\ncat >/dev/null\ncase "$*" in *root@ok-smc01*) echo "AVRPROBE|host=ok-smc01|avr=2.14|tini=|stats_age_s=12" ;; esac\n'
    ok = run("--proxy", "p", "ok-smc01", tsh=answers)
    self.assertEqual(ok.returncode, 0)
    self.assertIn("AVRPROBE|ok-smc01|host=ok-smc01|avr=2.14", ok.stdout)
    mixed = run("--proxy", "p", "ok-smc01", "down-smc01", tsh=answers)
    self.assertEqual(mixed.returncode, 1)
    self.assertIn("FAIL|down-smc01|", mixed.stdout)


if __name__ == "__main__":
  unittest.main()
