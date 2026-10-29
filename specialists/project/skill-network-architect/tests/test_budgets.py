"""Exercise the MTU, link-budget and availability helpers through their CLI against hand-computed values.

Usage: just test (or: <venv python> -B -m unittest discover -s tests -v)
Temporary fixtures are isolated and removed by the standard library.
"""

import unittest

from test_ip_plan import run_helper


class MtuBudgetTests(unittest.TestCase):
  """Check overhead arithmetic, the shortfall finding and refusal of unknown layers."""

  def test_wireguard_and_vxlan_overheads(self):
    """WireGuard over IPv4 leaves 1440 of 1500; VXLAN plus an inner tag leaves 9162 of 9216.

    Args:
      None.
    Returns:
      None.
    """
    code, result = run_helper(
      "mtu_budget.py",
      {
        "schema_version": 1,
        "paths": [
          {"id": "wg", "underlay_mtu": 1500, "layers": ["wireguard-ipv4"], "required_payload_mtu": 1420},
          {"id": "vx", "underlay_mtu": 9216, "layers": ["vxlan-ipv4", "dot1q-inner"], "required_payload_mtu": 9000},
        ],
      },
    )
    self.assertEqual(code, 0, result)
    self.assertEqual([path["payload_mtu"] for path in result["paths"]], [1440, 9162])
    self.assertEqual((result["paths"][0]["tcp_mss_ipv4"], result["paths"][0]["tcp_mss_ipv6"]), (1400, 1380))

  def test_esp_layers(self):
    """IPsec ESP AES-GCM over IPv4 with NAT-T leaves 1500 - 65 = 1435, MSS 1395.

    Args:
      None.
    Returns:
      None.
    """
    code, result = run_helper(
      "mtu_budget.py", {"schema_version": 1, "paths": [{"id": "esp", "underlay_mtu": 1500, "layers": ["esp-gcm-ipv4-natt"], "required_payload_mtu": 1400}]}
    )
    self.assertEqual((code, result["paths"][0]["payload_mtu"], result["paths"][0]["tcp_mss_ipv4"]), (0, 1435, 1395), result)

  def test_stack_shortfall_and_custom_layer(self):
    """A stacked tunnel short of its payload is a finding naming the underlay it needs.

    Args:
      None.
    Returns:
      None.
    """
    code, result = run_helper(
      "mtu_budget.py",
      {
        "schema_version": 1,
        "paths": [{"id": "stack", "underlay_mtu": 1500, "layers": ["pppoe", {"name": "esp-gcm", "bytes": 58}, "vxlan-ipv4"], "required_payload_mtu": 1500}],
      },
    )
    self.assertEqual(code, 1, result)
    self.assertEqual(result["paths"][0]["payload_mtu"], 1384)
    self.assertIn("raise the underlay to 1616", result["findings"][0])

  def test_rejects_invalid_input(self):
    """Unknown layer names, bad numbers and duplicate ids are invalid input, not findings.

    Args:
      None.
    Returns:
      None.
    """
    for paths in (
      [{"id": "a", "underlay_mtu": 1500, "layers": ["ipsec"], "required_payload_mtu": 1400}],
      [{"id": "a", "underlay_mtu": 40, "layers": [], "required_payload_mtu": 1400}],
      [{"id": "a", "underlay_mtu": 1500, "layers": [], "required_payload_mtu": 1400}] * 2,
      [{"id": "a", "underlay_mtu": 1500, "layers": [{"name": "x", "bytes": 0}], "required_payload_mtu": 1400}],
    ):
      with self.subTest(paths=paths):
        code, result = run_helper("mtu_budget.py", {"schema_version": 1, "paths": paths})
        self.assertEqual(code, 2, result)


class LinkBudgetTests(unittest.TestCase):
  """Check path loss, Fresnel radius and earth bulge against hand calculation."""

  LINK = {
    "id": "ptp",
    "distance_km": 10,
    "freq_mhz": 5800,
    "tx_power_dbm": 20,
    "tx_gain_dbi": 23,
    "rx_gain_dbi": 23,
    "losses_db": 2,
    "rx_sensitivity_dbm": -80,
    "required_fade_margin_db": 15,
  }

  def test_hand_computed_budget(self):
    """10 km at 5.8 GHz: FSPL 127.71 dB, margin 16.29 dB, midpoint F1 11.37 m, bulge 1.47 m at k=4/3.

    Args:
      None.
    Returns:
      None.
    """
    code, result = run_helper("link_budget.py", {"schema_version": 1, "links": [dict(self.LINK, obstacles=[{"d1_km": 5, "clearance_m": 10}])]})
    self.assertEqual(code, 0, result)
    link = result["links"][0]
    self.assertEqual((link["fspl_db"], link["fade_margin_db"], link["midpoint_fresnel_m"]), (127.71, 16.29, 11.37))
    self.assertEqual(link["obstacles"][0]["effective_clearance_m"], 8.53)

  def test_margin_and_clearance_findings(self):
    """A higher margin requirement and a low obstacle both produce findings.

    Args:
      None.
    Returns:
      None.
    """
    link = dict(self.LINK, required_fade_margin_db=20, obstacles=[{"d1_km": 5, "clearance_m": 5}])
    code, result = run_helper("link_budget.py", {"schema_version": 1, "links": [link]})
    self.assertEqual(code, 1, result)
    self.assertEqual(len(result["findings"]), 2)

  def test_rejects_invalid_input(self):
    """An obstacle outside the path, a missing field or a boolean number is invalid.

    Args:
      None.
    Returns:
      None.
    """
    missing = {key: value for key, value in self.LINK.items() if key != "losses_db"}
    for link in (dict(self.LINK, obstacles=[{"d1_km": 10, "clearance_m": 5}]), missing, dict(self.LINK, distance_km=True)):
      with self.subTest(link=link):
        code, result = run_helper("link_budget.py", {"schema_version": 1, "links": [link]})
        self.assertEqual(code, 2, result)


class AvailabilityTests(unittest.TestCase):
  """Check series and parallel composition and model bounds."""

  def test_series_parallel(self):
    """0.9995 x (1 - 0.01 x 0.02) x 0.9999 = 0.99920017, which meets 0.999.

    Args:
      None.
    Returns:
      None.
    """
    model = {
      "series": [
        {"name": "power", "availability": 0.9995},
        {"parallel": [{"name": "wan1", "availability": 0.99}, {"name": "wan2", "availability": 0.98}]},
        {"name": "router", "availability": 0.9999},
      ]
    }
    code, result = run_helper("availability.py", {"schema_version": 1, "target": 0.999, "model": model})
    self.assertEqual(code, 0, result)
    self.assertEqual(result["availability"], 0.99920017)
    code, result = run_helper("availability.py", {"schema_version": 1, "target": 0.9995, "model": model})
    self.assertEqual(code, 1, result)

  def test_rejects_invalid_models(self):
    """Empty groups, unknown kinds, out-of-range values and runaway depth are invalid.

    Args:
      None.
    Returns:
      None.
    """
    deep = {"name": "leaf", "availability": 0.9}
    for _ in range(30):
      deep = {"series": [deep]}
    for model in ({"series": []}, {"mesh": [{"name": "a", "availability": 0.9}]}, {"name": "a", "availability": 1.5}, deep):
      with self.subTest(model=str(model)[:40]):
        code, result = run_helper("availability.py", {"schema_version": 1, "target": 0.99, "model": model})
        self.assertEqual(code, 2, result)


if __name__ == "__main__":
  unittest.main()
