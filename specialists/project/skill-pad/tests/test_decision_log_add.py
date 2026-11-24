"""Tests for scripts/decision_log_add.py: next id, row form (one point per <br>), refusals, and that pad_decisions reads the row back."""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

_dir = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(_dir))
_spec = importlib.util.spec_from_file_location("decision_log_add", _dir / "decision_log_add.py")
dla = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dla)
_spec2 = importlib.util.spec_from_file_location("pad_decisions", _dir / "pad_decisions.py")
pdm = importlib.util.module_from_spec(_spec2)
_spec2.loader.exec_module(pdm)

LOG = "| ID | Date | Kind | Decision | Reason | Who |\n| --- | --- | --- | --- | --- | --- |\n| DL-009 | 2026-11-01 | process | Old. | Why. | Op. |\n"


class DecisionLogAdd(unittest.TestCase):
  """The row is the next id, six columns, one point per <br>, and mirrors back through pad_decisions."""

  def test_next_id_and_round_trip(self):
    """A planned row is not written; an applied one is DL-010 and pad_decisions shows its points one per line.

    Returns:
        None.
    """
    with tempfile.TemporaryDirectory() as tmp:
      log = Path(tmp) / "DECISION-LOG.md"
      log.write_text(LOG)
      args = [
        "--log",
        str(log),
        "--kind",
        "architecture",
        "--intro",
        "Two answers:",
        "--point",
        "one: A.",
        "--point",
        "- two: B.",
        "--closing",
        "Advice followed.",
        "--reason",
        "Because.",
        "--date",
        "2026-11-24",
      ]
      self.assertEqual(dla.main(args), 0)
      self.assertEqual(log.read_text(), LOG, "plan writes nothing")
      self.assertEqual(dla.main([*args, "--apply"]), 0)
      last = log.read_text().splitlines()[-1]
      self.assertEqual(last, "| DL-010 | 2026-11-24 | architecture | Two answers:<br>- one: A.<br>- two: B.<br>Advice followed. | Because. | Operator. |")
      item = [i for i in pdm.log_items(log) if i["ref"] == "DL-010"][0]
      self.assertIn("- one: A.\n- two: B.", item["body"])

  def test_refusals(self):
    """A pipe or a line break in the text, or nothing to decide, is refused with exit 1.

    Returns:
        None.
    """
    with tempfile.TemporaryDirectory() as tmp:
      log = Path(tmp) / "DECISION-LOG.md"
      log.write_text(LOG)
      base = ["--log", str(log), "--kind", "process", "--reason", "R"]
      self.assertEqual(dla.main([*base, "--point", "a | b"]), 1)
      self.assertEqual(dla.main([*base, "--point", "a\nb"]), 1)
      self.assertEqual(dla.main(base), 1)
      self.assertEqual(log.read_text(), LOG)


if __name__ == "__main__":
  unittest.main()
