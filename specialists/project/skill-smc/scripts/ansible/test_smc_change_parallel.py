"""Offline tests for smc_change_parallel.sh with stand-in ansible-playbook and tsh on PATH; no SMC is contacted.

Run: python3 -m unittest scripts/ansible/test_smc_change_parallel.py (from the skill-smc root), or `just smc_change_parallel_test`. <10 s.
"""

from __future__ import annotations

import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "smc_change_parallel.sh"

# Stand-in ansible-playbook: prints a recap for the -l host, exits 4 for one named to fail, sleeps for one named slow.
FAKE_PLAYBOOK = """#!/bin/sh
host=""
while [ $# -gt 0 ]; do [ "$1" = "-l" ] && host=$2; shift; done
case "$host" in slow-smc01) sleep 2 ;; esac
echo "PLAY RECAP ****"
echo "$host                  : ok=3    changed=1    unreachable=0    failed=0"
case "$host" in bad-smc01) exit 4 ;; esac
exit 0
"""
# Stand-in tsh: "tsh ssh root@<host> true" answers except for dark-smc01.
FAKE_TSH = """#!/bin/sh
case "$2" in root@dark-smc01) exit 1 ;; esac
exit 0
"""


def write_exe(folder: Path, name: str, text: str) -> None:
  """Write an executable stand-in.

  Args:
      folder: where to write it.
      name: its file name.
      text: its content.

  Returns:
      None.
  """
  path = folder / name
  path.write_text(text)
  path.chmod(path.stat().st_mode | stat.S_IXUSR)


class ParallelTest(unittest.TestCase):
  """Plan, apply, skips and exit codes of smc_change_parallel.sh."""

  def setUp(self) -> None:
    """Make a fake repo, a bin folder with the stand-ins and a log folder.

    Returns:
        None.
    """
    self.tmp = tempfile.TemporaryDirectory()
    root = Path(self.tmp.name)
    self.repo, self.bin, self.logs = root / "repo", root / "bin", root / "logs"
    (self.repo / "inventories/rct").mkdir(parents=True)
    (self.repo / "inventories/rct/prod").write_text("")
    (self.repo / "smc_change_multiple.yml").write_text("")
    self.bin.mkdir()
    write_exe(self.bin, "ansible-playbook", FAKE_PLAYBOOK)
    write_exe(self.bin, "tsh", FAKE_TSH)
    self.env = {**os.environ, "PATH": f"{self.bin}:{os.environ['PATH']}"}

  def tearDown(self) -> None:
    """Remove the temporary folders.

    Returns:
        None.
    """
    self.tmp.cleanup()

  def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
    """Run the script against the fake repo.

    Args:
        *args: its arguments after -r and -o.

    Returns:
        The finished process.
    """
    argv = [str(SCRIPT), "-r", str(self.repo), "-o", str(self.logs), "-t", "5", *args]
    return subprocess.run(argv, env=self.env, capture_output=True, text=True, timeout=60, check=False)

  def test_plan_starts_nothing(self) -> None:
    """Without --apply it lists the runs, expands short names and writes no log."""
    out = self.run_script("good", "slow-smc01")
    self.assertEqual(out.returncode, 0, out.stderr)
    self.assertIn("-l good-smc01", out.stdout)
    self.assertIn("plan only", out.stdout)
    self.assertFalse(self.logs.exists())

  def test_apply_runs_each_and_reports(self) -> None:
    """All runs start at once; a failing run gives exit 1, a dark SMC is skipped, each gets a log and a DONE line."""
    out = self.run_script("--apply", "good", "slow", "bad", "dark")
    self.assertEqual(out.returncode, 1, out.stdout + out.stderr)
    self.assertIn("SKIP     dark-smc01: no answer over Teleport", out.stdout)
    self.assertIn("DONE     good-smc01 exit 0", out.stdout)
    self.assertIn("DONE     bad-smc01 exit 4", out.stdout)
    self.assertEqual(sorted(p.name for p in self.logs.glob("*.log")), ["bad-smc01.log", "good-smc01.log", "slow-smc01.log"])
    self.assertEqual(len((self.logs / "pids.txt").read_text().splitlines()), 3)

  def test_bad_usage(self) -> None:
    """No SMC, a name twice or an unknown option is refused with exit 2."""
    self.assertEqual(self.run_script().returncode, 2)
    self.assertEqual(self.run_script("good", "good-smc01").returncode, 2)
    self.assertEqual(self.run_script("--nope", "good").returncode, 2)


if __name__ == "__main__":
  unittest.main()
