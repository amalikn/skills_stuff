"""Exercise the quorum and Ceph capacity helpers through their CLI against hand-computed values.

Usage: just test (or: <venv python> -B -m unittest discover -s tests -v)
Temporary fixtures are isolated and removed by the standard library.
"""

import unittest

from test_capacity import run_helper


class QuorumTests(unittest.TestCase):
  """Votes, QDevice weighting and required scenarios."""

  def test_rack_loss_and_qdevice(self):
    """Three nodes, two in rack A: losing rack A loses quorum; two nodes plus a QDevice survive either node or the QDevice.

    Args:
      None.
    Returns:
      None.
    """
    nodes = [{"id": "a1", "domain": "a"}, {"id": "a2", "domain": "a"}, {"id": "b1", "domain": "b"}]
    code, result = run_helper("quorum_check.py", {"schema_version": 1, "nodes": nodes, "must_survive": ["node:a1", "domain:a"]})
    self.assertEqual((code, result["total_votes"], result["quorum"]), (1, 3, 2), result)
    self.assertEqual(len(result["findings"]), 1)
    pair = {
      "schema_version": 1,
      "nodes": [{"id": "n1", "domain": "a"}, {"id": "n2", "domain": "b"}],
      "qdevice": {"domain": "c"},
      "must_survive": ["node:n1", "node:n2", "qdevice"],
    }
    code, result = run_helper("quorum_check.py", pair)
    self.assertEqual((code, result["qdevice_votes"]), (0, 1), result)

  def test_combined_scenario(self):
    """Two nodes plus a QDevice survive one node or the QDevice, but not a node and the QDevice together.

    Args:
      None.
    Returns:
      None.
    """
    pair = {
      "schema_version": 1,
      "nodes": [{"id": "n1", "domain": "a"}, {"id": "n2", "domain": "b"}],
      "qdevice": {"domain": "c"},
      "must_survive": ["domain:a", "qdevice", "domain:a+qdevice"],
    }
    code, result = run_helper("quorum_check.py", pair)
    self.assertEqual(code, 1, result)
    self.assertEqual([finding.split(":")[0] + ":" + finding.split(":")[1] for finding in result["findings"]], ["domain:a+qdevice"])

  def test_odd_count_qdevice_warns(self):
    """A QDevice on three nodes holds two votes and is a warning, not a failure.

    Args:
      None.
    Returns:
      None.
    """
    nodes = [{"id": f"n{i}", "domain": f"d{i}"} for i in range(3)]
    code, result = run_helper("quorum_check.py", {"schema_version": 1, "nodes": nodes, "qdevice": {"domain": "q"}})
    self.assertEqual((code, result["status"], result["qdevice_votes"], result["total_votes"]), (0, "warnings", 2, 5), result)

  def test_rejects_invalid(self):
    """Unknown scenarios, duplicate ids and bad votes are invalid input.

    Args:
      None.
    Returns:
      None.
    """
    base = [{"id": "n1", "domain": "a"}]
    for data in (
      {"schema_version": 1, "nodes": base, "must_survive": ["node:zz"]},
      {"schema_version": 1, "nodes": base * 2},
      {"schema_version": 1, "nodes": [{"id": "n1", "domain": "a", "votes": 0}]},
    ):
      with self.subTest(data=data):
        code, result = run_helper("quorum_check.py", data)
        self.assertEqual(code, 2, result)


class CephCapacityTests(unittest.TestCase):
  """Plan capacity, self-healing and min_size rules."""

  DOMAINS = [{"id": f"h{i}", "raw_tb": 15.36} for i in range(4)]

  def test_hand_computed_plan(self):
    """4 x 15.36 TB, size 3, lose one host: (61.44 - 15.36) / 3 x 0.85 = 13.056 TB.

    Args:
      None.
    Returns:
      None.
    """
    pool = {"id": "rbd", "size": 3, "tolerate_domain_failures": 1, "demand_tb": 10}
    code, result = run_helper("ceph_capacity.py", {"schema_version": 1, "domains": self.DOMAINS, "pools": [pool]})
    self.assertEqual((code, result["pools"][0]["plan_tb"], result["pools"][0]["min_size"]), (0, 13.056, 2), result)

  def test_layout_findings(self):
    """Three hosts with size 3 cannot self-heal after a host loss; min_size 1 and an EC pool wider than the hosts are findings.

    Args:
      None.
    Returns:
      None.
    """
    pools = [
      {"id": "r3", "size": 3, "min_size": 1, "tolerate_domain_failures": 1, "demand_tb": 1},
      {"id": "ec", "ec": {"k": 4, "m": 2}, "tolerate_domain_failures": 0, "demand_tb": 1},
    ]
    code, result = run_helper("ceph_capacity.py", {"schema_version": 1, "domains": self.DOMAINS[:3], "pools": pools})
    self.assertEqual(code, 1, result)
    text = " ".join(result["findings"])
    for expected in ("stays degraded", "min_size 1", "need 6 failure domains"):
      self.assertIn(expected, text)

  def test_rejects_invalid(self):
    """Both size and ec, or too many tolerated failures, are invalid.

    Args:
      None.
    Returns:
      None.
    """
    for pool in (
      {"id": "x", "size": 3, "ec": {"k": 2, "m": 1}, "tolerate_domain_failures": 0, "demand_tb": 1},
      {"id": "x", "size": 3, "tolerate_domain_failures": 4, "demand_tb": 1},
    ):
      with self.subTest(pool=pool):
        code, result = run_helper("ceph_capacity.py", {"schema_version": 1, "domains": self.DOMAINS, "pools": [pool]})
        self.assertEqual(code, 2, result)


if __name__ == "__main__":
  unittest.main()
