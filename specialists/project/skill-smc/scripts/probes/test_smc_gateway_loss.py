"""Offline test for smc_gateway_loss.sh with a stand-in tsh on PATH; no SMC is contacted. Run: `just smc_gateway_loss_test`. <5 s."""

from __future__ import annotations

import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "smc_gateway_loss.sh"

# Stand-in tsh: "tsh ssh root@<host> sh -s N" reads the probe on stdin and prints a canned line; dark-smc01 does not answer.
FAKE_TSH = """#!/bin/sh
cat >/dev/null
case "$2" in
  root@dark-smc01) exit 1 ;;
  root@lossy-smc01) echo "gw=10.92.162.125 loss=25 rtt=574.8 rx=20 tx=22" ;;
  root@peer-smc01) echo "gw=10.92.162.7 loss=15 rtt=580.1 rx=10 tx=9" ;;
  *) echo "gw=10.93.67.73 loss=0 rtt=609.5 rx=46 tx=21" ;;
esac
"""


class GatewayLossTest(unittest.TestCase):
  """Table, per-/24 grouping and exit codes of smc_gateway_loss.sh."""

  def test_table_groups_and_exit(self) -> None:
    """Each SMC gets a row, a dark one NO ANSWER and exit 1; SMCs on one /24 are grouped with their average loss."""
    with tempfile.TemporaryDirectory() as folder:
      tsh = Path(folder) / "tsh"
      tsh.write_text(FAKE_TSH)
      tsh.chmod(tsh.stat().st_mode | stat.S_IXUSR)
      env = {**os.environ, "PATH": f"{folder}:{os.environ['PATH']}"}
      out = subprocess.run([str(SCRIPT), "-t", "10", "good", "lossy", "peer", "dark"], env=env, capture_output=True, text=True, timeout=60, check=False)
    self.assertEqual(out.returncode, 1, out.stdout + out.stderr)
    self.assertIn("dark-smc01                 NO ANSWER", out.stdout)
    self.assertRegex(out.stdout, r"lossy-smc01\s+10\.92\.162\.125\s+25")
    self.assertRegex(out.stdout, r"10\.92\.162\.0/24\s+2 SMC\s+avg loss\s+20\.0 %")

  def test_bad_usage(self) -> None:
    """No SMC, or a non-number for -c, is refused with exit 2."""
    self.assertEqual(subprocess.run([str(SCRIPT)], capture_output=True, timeout=30, check=False).returncode, 2)
    self.assertEqual(subprocess.run([str(SCRIPT), "-c", "x", "good"], capture_output=True, timeout=30, check=False).returncode, 2)


if __name__ == "__main__":
  unittest.main()
