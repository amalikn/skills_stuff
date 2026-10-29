"""Exercise helpers through their CLI; no network or infrastructure access.

Usage: python3 -B -m unittest discover -s tests -v
Temporary fixtures are isolated and removed by the standard library.
"""

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


class IPPlanTests(unittest.TestCase):
  """Validate overlap semantics and reject misleading input."""

  def test_valid_edge_cases(self):
    """Accept scoped overlap, IPv6 and /31 or /32 gateway membership.

    Args:
      None.
    Returns:
      None.
    """
    cases = [
      [{"id": "a", "scope": "v", "cidr": "192.0.2.0/31", "gateway": "192.0.2.0"}],
      [{"id": "a", "scope": "v", "cidr": "192.0.2.1/32", "gateway": "192.0.2.1"}],
      [{"id": "a", "scope": "v", "cidr": "2001:db8::/64", "gateway": "2001:db8::1"}],
      [{"id": "a", "scope": "v1", "cidr": "10.0.0.0/8"}, {"id": "b", "scope": "v2", "cidr": "10.0.0.0/8"}],
    ]
    for segments in cases:
      with self.subTest(segments=segments):
        code, result = run_helper("ip_plan_check.py", {"schema_version": 1, "segments": segments})
        self.assertEqual(code, 0, result)
        self.assertEqual(result["findings"], [])

  def test_finds_overlap_and_bad_gateways(self):
    """Detect nesting, duplicate prefix and invalid gateway semantics.

    Args:
      None.
    Returns:
      None.
    """
    cases = [
      [{"id": "a", "scope": "v", "cidr": "10.0.0.0/8"}, {"id": "b", "scope": "v", "cidr": "10.1.0.0/16"}, {"id": "c", "scope": "v", "cidr": "10.2.0.0/16"}],
      [{"id": "a", "scope": "v", "cidr": "10.0.0.0/24"}, {"id": "b", "scope": "v", "cidr": "10.0.0.0/24"}],
      [{"id": "a", "scope": "v", "cidr": "10.0.0.0/24", "gateway": "10.0.0.255"}],
      [{"id": "a", "scope": "v", "cidr": "10.0.0.0/24", "gateway": "2001:db8::1"}],
      [{"id": "a", "scope": "v", "cidr": "10.0.0.0/24", "gateway": "10.0.1.1"}],
    ]
    for segments in cases:
      with self.subTest(segments=segments):
        code, result = run_helper("ip_plan_check.py", {"schema_version": 1, "segments": segments})
        self.assertEqual(code, 1, result)
        self.assertTrue(result["findings"])
        if len(segments) == 3:
          self.assertEqual(len(result["findings"]), 2)

  def test_ipv6_segment_size(self):
    """An IPv6 segment other than /64, /127 or /128 is a finding; those three pass.

    Args:
      None.
    Returns:
      None.
    """
    code, result = run_helper(
      "ip_plan_check.py",
      {
        "schema_version": 1,
        "segments": [
          {"id": "lan", "scope": "v", "cidr": "2001:db8:1::/64"},
          {"id": "p2p", "scope": "v", "cidr": "2001:db8:2::/127"},
          {"id": "lo", "scope": "v", "cidr": "2001:db8:3::1/128"},
        ],
      },
    )
    self.assertEqual(code, 0, result)
    code, result = run_helper("ip_plan_check.py", {"schema_version": 1, "segments": [{"id": "big", "scope": "v", "cidr": "2001:db8:4::/56"}]})
    self.assertEqual(code, 1, result)
    self.assertIn("use /64 per segment", result["findings"][0])

  def test_rejects_invalid_schema(self):
    """Reject host-bit CIDRs, duplicates, typos and oversized input.

    Args:
      None.
    Returns:
      None.
    """
    segment = {"id": "a", "scope": "v", "cidr": "10.0.0.0/24"}
    cases = [
      {"schema_version": 1, "segments": []},
      {"schema_version": True, "segments": [segment]},
      {"schema_version": 1, "segments": [segment, segment]},
      {"schema_version": 1, "segments": [dict(segment, cidr="10.0.0.1/24")]},
      {"schema_version": 1, "segments": [dict(segment, unexpected=1)]},
      {"schema_version": 1, "segments": [dict(segment, scope=" ")]},
      {"schema_version": 1, "segments": [dict(segment, id="x" * (1024 * 1024))]},
      {"schema_version": 1, "segments": "wrong"},
    ]
    for data in cases:
      with self.subTest(case=str(data)[:80]):
        code, result = run_helper("ip_plan_check.py", data)
        self.assertEqual(code, 2, result)
