"""Exercise the fibre and power budget helpers through their CLI against hand-computed values.

Usage: just test (or: <venv python> -B -m unittest discover -s tests -v)
Temporary fixtures are isolated and removed by the standard library.
"""

import unittest

from test_ip_plan import run_helper

LINK = {
  "id": "sm",
  "fibre": "sm-premises",
  "length_km": 2,
  "connections": 4,
  "splices": 2,
  "tx_min_dbm": -8.2,
  "rx_sensitivity_dbm": -14.4,
  "required_margin_db": 1.0,
}


class FibreBudgetTests(unittest.TestCase):
  """TIA-568 maximum defaults, overrides and the margin finding."""

  def test_defaults_and_shortfall(self):
    """2 km x 1.0 + 4 x 0.75 + 2 x 0.3 = 5.6 dB against a 6.2 dB budget leaves 0.6 dB, short of 1.0.

    Args:
      None.
    Returns:
      None.
    """
    code, result = run_helper("fibre_budget.py", {"schema_version": 1, "links": [LINK]})
    self.assertEqual((code, result["links"][0]["plant_loss_db"], result["links"][0]["margin_db"]), (1, 5.6, 0.6), result)

  def test_measured_overrides_pass(self):
    """Measured 0.35 dB/km, 0.3 dB connectors and 0.05 dB splices give 1.6 dB loss and pass.

    Args:
      None.
    Returns:
      None.
    """
    link = dict(LINK, attenuation_db_km=0.35, connector_db=0.3, splice_db=0.05)
    code, result = run_helper("fibre_budget.py", {"schema_version": 1, "links": [link]})
    self.assertEqual((code, result["links"][0]["plant_loss_db"]), (0, 2.0), result)

  def test_rejects_invalid(self):
    """Unknown fibre type and fractional connection counts are invalid.

    Args:
      None.
    Returns:
      None.
    """
    for link in (dict(LINK, fibre="om5"), dict(LINK, connections=2.5)):
      with self.subTest(link=link):
        code, result = run_helper("fibre_budget.py", {"schema_version": 1, "links": [link]})
        self.assertEqual(code, 2, result)


class PowerBudgetTests(unittest.TestCase):
  """PoE budget, port class limits and UPS policy."""

  SITE = {
    "schema_version": 1,
    "other_loads_w": 200,
    "switches": [
      {
        "id": "sw",
        "base_w": 30,
        "poe_budget_w": 120,
        "ports": [{"device": "ap", "draw_w": 25.5, "port_class": "at"}, {"device": "radio", "draw_w": 40, "port_class": "bt3"}],
      }
    ],
    "ups": {"va": 1500, "power_factor": 0.9, "battery_wh": 864, "inverter_efficiency": 0.9, "max_load_fraction": 0.8},
  }

  def test_hand_computed_site(self):
    """Site load 30 + 65.5 + 200 = 295.5 W; 864 Wh x 0.9 / 295.5 W = 157.9 min.

    Args:
      None.
    Returns:
      None.
    """
    code, result = run_helper("power_budget.py", self.SITE)
    self.assertEqual((code, result["site_load_w"], result["ups"]["linear_runtime_min"]), (0, 295.5, 157.9), result)

  def test_class_and_budget_findings(self):
    """A 40 W device on an at (30 W) port and a PoE budget below the draw are both findings.

    Args:
      None.
    Returns:
      None.
    """
    site = dict(
      self.SITE,
      switches=[
        {"id": "sw", "base_w": 30, "poe_budget_w": 50, "ports": [{"device": "radio", "draw_w": 40, "port_class": "at"}, {"device": "ap", "draw_w": 25.5}]}
      ],
    )
    code, result = run_helper("power_budget.py", site)
    self.assertEqual((code, len(result["findings"])), (1, 2), result)


if __name__ == "__main__":
  unittest.main()
