"""Offline test for smc_change_runs_table.py. Run: python3 -m unittest test_smc_change_runs_table -v (from scripts/).

Safety: temporary files only; no SMC, no network.
"""

import contextlib
import io
import json
import runpy
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

MODULE = runpy.run_path(str(Path(__file__).resolve().parent / "smc_change_runs_table.py"))


class RunsTableTests(unittest.TestCase):
  """Assert the rows built from sample records."""

  def test_rows(self):
    """A rebooted run with a holder, a plain pass, and a refused run without an after-probe.

    Returns:
      None.
    """
    with TemporaryDirectory() as tmp:
      d = Path(tmp)
      (d / "a-smc01-x-apply-20261026_200000.json").write_text(json.dumps({
        "result": "passed", "elapsed_seconds": 900.4, "before": {"boot_id": "1"}, "after": {"boot_id": "2"},
        "phase_timings": [{"phase": "6/11 ACTIONS", "seconds": 97.2}, {"phase": "8/11 REBOOT", "seconds": 455}],
        "lower_busy": {"holders": ["123 php /usr/local/bin/kohana status:update:usage : maps /usr/bin/php8.1"]},
      }))
      (d / "b-smc01-x-apply-20261026_190000.json").write_text(json.dumps({
        "result": "passed", "elapsed_seconds": 412, "before": {"boot_id": "1"}, "after": {"boot_id": "1"},
        "phase_timings": [{"phase": "6/11 ACTIONS", "seconds": 184.3}],
      }))
      (d / "c-smc01-x-apply-20261026_210000.json").write_text(json.dumps({
        "result": "failed", "before": {"boot_id": "1"}, "failure": {"stage": "3/11 PROBE", "msg": "needs_repair: chroot"},
      }))
      (d / "c-smc01-x-check-20261026_210500.json").write_text("{}")
      rows = [MODULE["row"](str(p), json.loads(p.read_text())) for p in sorted(d.glob("*-apply-*.json"))]
      by = {r["run"][0]: r for r in rows}
      self.assertEqual((by["a"]["rebooted"], by["a"]["p8"], by["a"]["p6"]), ("yes", 455, 97))
      self.assertIn("kohana", by["a"]["busy"])
      self.assertEqual((by["b"]["rebooted"], by["b"]["p6"], by["b"]["p8"]), ("no", 184, "-"))
      self.assertEqual(by["c"]["rebooted"], "?")
      self.assertTrue(by["c"]["failure"].startswith("3/11 PROBE needs_repair"))
      out = io.StringIO()
      with contextlib.redirect_stdout(out):
        self.assertEqual(MODULE["main"]([tmp]), 0)
      lines = out.getvalue().splitlines()
      self.assertEqual([line[0] for line in lines[1:]], ["b", "a", "c"])  # by start stamp, check record left out
      self.assertEqual(MODULE["main"]([tmp + "/missing"]), 2)


if __name__ == "__main__":
  unittest.main()
