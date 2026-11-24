"""Exercise home_line.py through its CLI: public, CGNAT, double NAT and a confirming router WAN address.

Usage: just test (or: <venv python> -B -m unittest discover -s tests -v)
Uses documentation addresses (RFC 5737) plus 100.64.0.0/10 and RFC 1918; nothing touches a network.
"""

import unittest

from test_ip_plan import run_helper

TRACE = " 1  192.168.86.1  7 ms\n 2  {hop}  20 ms\n 3  *\n"


def line(hop: str, **extra) -> dict:
  """Build an input with the given second hop.

  Args:
    hop: the address of hop 2.
    **extra: more input fields.
  Returns:
    The input object.
  """
  return {"schema_version": 1, "traceroute": TRACE.format(hop=hop), "public_ipv4": "203.0.113.36", **extra}


class HomeLineTests(unittest.TestCase):
  """Check each verdict and its exit code."""

  def test_public_hop(self):
    """A public hop after the router: public-likely, exit 0.

    Args:
      None.
    Returns:
      None.
    """
    code, result = run_helper("home_line.py", line("198.51.100.1"))
    self.assertEqual((code, result["verdict"]), (0, "public-likely"), result)

  def test_cgnat_hop(self):
    """A 100.64.0.0/10 hop after the router: cgnat, exit 1, with the port-forward finding.

    Args:
      None.
    Returns:
      None.
    """
    code, result = run_helper("home_line.py", line("100.72.0.1"))
    self.assertEqual((code, result["verdict"]), (1, "cgnat"), result)
    self.assertTrue(any("port forward" in f for f in result["findings"]))

  def test_double_nat_hop(self):
    """An RFC 1918 hop after the router: double-nat, exit 1.

    Args:
      None.
    Returns:
      None.
    """
    code, result = run_helper("home_line.py", line("10.0.0.1"))
    self.assertEqual((code, result["verdict"]), (1, "double-nat"), result)

  def test_router_wan_confirms_and_overrides(self):
    """A router WAN equal to the public address confirms; one in CGNAT space overrides a public hop.

    Args:
      None.
    Returns:
      None.
    """
    code, result = run_helper("home_line.py", line("198.51.100.1", router_wan_ipv4="203.0.113.36"))
    self.assertEqual((code, result["verdict"]), (0, "public-confirmed"), result)
    code, result = run_helper("home_line.py", line("198.51.100.1", router_wan_ipv4="100.64.5.5"))
    self.assertEqual((code, result["verdict"]), (1, "cgnat"), result)

  def test_invalid(self):
    """A private public_ipv4 is refused with exit 2.

    Args:
      None.
    Returns:
      None.
    """
    code, result = run_helper("home_line.py", {"schema_version": 1, "traceroute": TRACE.format(hop="198.51.100.1"), "public_ipv4": "10.1.1.1"})
    self.assertEqual((code, result["status"]), (2, "invalid"), result)


if __name__ == "__main__":
  unittest.main()
