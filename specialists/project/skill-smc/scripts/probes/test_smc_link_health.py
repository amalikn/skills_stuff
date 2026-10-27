"""Offline checks for smc_link_health.sh: it parses, prints its help, and refuses bad arguments before any connection.

Run: python3 -m unittest test_smc_link_health (from scripts/). No network, no Teleport.
"""

import subprocess
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "smc_link_health.sh"


def run(*args: str) -> subprocess.CompletedProcess:
  """Run the script with arguments and capture its output.

  Args:
    *args: command-line arguments.

  Returns:
    The finished process.
  """
  return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True, timeout=20, check=False)


class LinkHealthArguments(unittest.TestCase):
  """The script's argument handling, without reaching any SMC."""

  def test_parses(self) -> None:
    """bash -n finds no syntax error."""
    self.assertEqual(subprocess.run(["bash", "-n", str(SCRIPT)], check=False).returncode, 0)

  def test_help_and_usage_errors(self) -> None:
    """--help exits 0 with the usage line; no host, an unknown option or a non-numeric --pings exit 2."""
    shown = run("--help")
    self.assertEqual(shown.returncode, 0)
    self.assertIn("usage: smc_link_health.sh", shown.stdout)
    self.assertEqual(run().returncode, 2)
    self.assertEqual(run("--bogus").returncode, 2)
    self.assertEqual(run("some-smc01", "--pings", "many").returncode, 2)


if __name__ == "__main__":
  unittest.main()
