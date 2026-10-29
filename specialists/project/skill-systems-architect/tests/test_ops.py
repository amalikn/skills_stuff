"""Exercise the restore-time and end-of-life helpers through their CLI against hand-computed values.

Usage: just test (or: <venv python> -B -m unittest discover -s tests -v)
Temporary fixtures are isolated and removed by the standard library.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_capacity import run_helper

ROOT = Path(__file__).resolve().parents[1]


class RestoreTimeTests(unittest.TestCase):
  """Transfer arithmetic, phase totals and stream scaling."""

  PLAN = {
    "id": "db",
    "data_gib": 1024,
    "throughput_mbps": 1000,
    "efficiency": 0.8,
    "detect_s": 300,
    "decide_s": 600,
    "provision_s": 900,
    "verify_s": 600,
    "rto_s": 14400,
  }

  def test_hand_computed(self):
    """1 TiB at 1 Gbit/s x 0.8 is 10,995.1 s; plus 2,400 s of phases = 13,395.1 s, inside a 4 h RTO.

    Args:
      None.
    Returns:
      None.
    """
    code, result = run_helper("restore_time.py", {"schema_version": 1, "plans": [self.PLAN]})
    self.assertEqual((code, result["plans"][0]["transfer_s"], result["plans"][0]["total_s"]), (0, 10995.1, 13395.1), result)

  def test_miss_and_streams(self):
    """A 1 h RTO is missed; four linear streams cut the transfer to a quarter.

    Args:
      None.
    Returns:
      None.
    """
    code, result = run_helper("restore_time.py", {"schema_version": 1, "plans": [dict(self.PLAN, rto_s=3600)]})
    self.assertEqual(code, 1, result)
    code, result = run_helper("restore_time.py", {"schema_version": 1, "plans": [dict(self.PLAN, parallel_streams=4, stream_scaling=1)]})
    self.assertEqual(result["plans"][0]["transfer_s"], 2748.8)


class EolTests(unittest.TestCase):
  """Past, warning and ok states measured from a fixed day."""

  def test_states(self):
    """From 2026-10-29: Debian 11 (2026-08-31) is past and fails; Server 2016 (2027-01-12) warns without a plan.

    Args:
      None.
    Returns:
      None.
    """
    register = {
      "schema_version": 1,
      "warn_days": 365,
      "entries": [
        {"id": "a", "product": "Debian", "version": "11", "end_of_support": "2026-08-31", "source": "s", "owner": "o"},
        {"id": "b", "product": "Windows Server", "version": "2016", "end_of_support": "2027-01-12", "source": "s", "owner": "o"},
      ],
    }
    with tempfile.TemporaryDirectory() as directory:
      fixture = Path(directory) / "r.json"
      fixture.write_text(json.dumps(register))
      run = subprocess.run(
        [sys.executable, "-B", str(ROOT / "scripts/eol_check.py"), str(fixture), "--today", "2026-10-29"],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
      )
    result = json.loads(run.stdout)
    self.assertEqual((run.returncode, result["counts"]), (1, {"past": 1, "warning": 1, "ok": 0}), result)
    self.assertEqual(result["entries"][0]["days_left"], -59)


if __name__ == "__main__":
  unittest.main()
