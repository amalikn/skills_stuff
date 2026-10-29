"""Exercise helpers through their CLI; no network or infrastructure access.

Usage: python3 -B -m unittest discover -s tests -v
Temporary fixtures are isolated and removed by the standard library.
"""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_helper(script, data):
  """Invoke a helper with an isolated JSON fixture.

  Args:
    script: Helper filename under scripts.
    data: Object to serialize into a temporary file.
  Returns:
    Pair of exit code and parsed JSON output.
  Raises:
    subprocess.TimeoutExpired: If the helper exceeds five seconds.
    ValueError: If output is not valid JSON.
  """
  with tempfile.TemporaryDirectory() as directory:
    fixture = Path(directory) / "input.json"
    fixture.write_text(json.dumps(data), encoding="utf-8")
    result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts" / script), str(fixture)], capture_output=True, text=True, timeout=5, check=False)
  return result.returncode, json.loads(result.stdout)


class CapacityTests(unittest.TestCase):
  """Exercise correlated failure and recovery-budget calculations."""

  def test_rack_failure_and_transfer_floor(self):
    """Detect the independent RAM and RTO shortfalls with exact units.

    Args:
      None.
    Returns:
      None.
    """
    plan = json.loads((ROOT / "examples/capacity-plan.json").read_text())
    code, result = run_helper("capacity_check.py", plan)
    self.assertEqual(code, 1, result)
    self.assertEqual(result["scenarios"][0]["effective_memory_gib"], 208)
    self.assertEqual(result["scenarios"][2]["effective_memory_gib"], 48)
    self.assertEqual(result["scenarios"][2]["deficit_gib"], 92)
    self.assertAlmostEqual(result["restore"]["estimated_seconds"], 8796.093022208)
    self.assertTrue(result["restore"]["exceeds_rto"])

  def test_passing_model_and_headroom(self):
    """Accept a viable pooled model and honor explicit headroom.

    Args:
      None.
    Returns:
      None.
    """
    plan = json.loads((ROOT / "examples/capacity-plan-pass.json").read_text())
    code, result = run_helper("capacity_check.py", plan)
    self.assertEqual(code, 0, result)
    plan["headroom_fraction"] = 0.2
    code, result = run_helper("capacity_check.py", plan)
    self.assertEqual(code, 1, result)
    self.assertAlmostEqual(result["scenarios"][2]["effective_memory_gib"], 128)

  def test_rejects_bad_numbers_and_references(self):
    """Reject nonfinite numbers, booleans and invalid domain references.

    Args:
      None.
    Returns:
      None.
    """
    baseline = json.loads((ROOT / "examples/capacity-plan.json").read_text())
    for value in (True, -1, float("nan"), float("inf"), "140"):
      plan = copy.deepcopy(baseline)
      plan["demand_gib"] = value
      with self.subTest(demand=value):
        code, result = run_helper("capacity_check.py", plan)
        self.assertEqual(code, 2, result)
    changes = [
      ("nodes", []),
      ("headroom_fraction", 1),
      ("scenarios", []),
      ("scenarios", [{"id": "bad", "failed_nodes": [], "failed_domains": ["missing"]}]),
    ]
    for key, value in changes:
      plan = copy.deepcopy(baseline)
      plan[key] = value
      with self.subTest(field=key):
        code, result = run_helper("capacity_check.py", plan)
        self.assertEqual(code, 2, result)

  def test_restore_efficiency_and_fixed_time(self):
    """Apply effective throughput and serialized fixed recovery work.

    Args:
      None.
    Returns:
      None.
    """
    plan = json.loads((ROOT / "examples/capacity-plan-pass.json").read_text())
    plan["restore"].update(data_gib=1, throughput_mbps=1000, efficiency=0.5, fixed_seconds=20, rto_seconds=100)
    code, result = run_helper("capacity_check.py", plan)
    self.assertEqual(code, 0, result)
    self.assertAlmostEqual(result["restore"]["estimated_seconds"], 37.179869184)
