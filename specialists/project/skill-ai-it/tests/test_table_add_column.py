"""Offline tests for scripts/markdown/table_add_column.py: wrapped rows merge, the column is added, a missing key is refused, plan writes nothing."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "markdown" / "table_add_column.py"
_spec = importlib.util.spec_from_file_location("table_add_column", SCRIPT)
tac = importlib.util.module_from_spec(_spec)
sys.modules["table_add_column"] = tac
_spec.loader.exec_module(tac)

DOC = """# Report

| ID  | State | Evidence             |
| --- | ----- | -------------------- |
| F01 | Open  | first line of        |
|     |       |   the evidence       |
| F02 | Done  | short                |

| Other | x |
| ----- | - |
| a     | b |
"""


class TableAddColumnTests(unittest.TestCase):
  """The tool's behaviour on a wrapped table."""

  def run_tool(self, values: dict, *extra: str) -> tuple[int, str]:
    """Run main() on a temporary copy of DOC.

    Args:
      values: the key-to-value map.
      extra: further arguments.

    Returns:
      (exit code, resulting file text).
    """
    with tempfile.TemporaryDirectory() as tmp:
      doc, vals = Path(tmp) / "doc.md", Path(tmp) / "v.json"
      doc.write_text(DOC, encoding="utf-8")
      vals.write_text(json.dumps(values), encoding="utf-8")
      rc = tac.main([str(doc), "--header-first-cell", "ID", "--column", "Verdict", "--values", str(vals), *extra])
      return rc, doc.read_text(encoding="utf-8")

  def test_merges_wrapped_rows_and_adds_column(self):
    """A continuation row joins its row; each row gets its value; other tables are untouched."""
    rc, text = self.run_tool({"F01": "Confirmed", "F02": "Not rechecked"}, "--apply")
    self.assertEqual(rc, 0)
    self.assertIn("| F01 | Open | first line of the evidence | Confirmed |", text)
    self.assertIn("| F02 | Done | short | Not rechecked |", text)
    self.assertIn("| a     | b |", text)

  def test_missing_key_refused(self):
    """A row with no value and no default fails and writes nothing."""
    rc, text = self.run_tool({"F01": "Confirmed"}, "--apply")
    self.assertEqual(rc, 1)
    self.assertEqual(text, DOC)

  def test_default_fills_missing(self):
    """--default fills a row missing from the map."""
    rc, text = self.run_tool({"F01": "Confirmed"}, "--default", "Not rechecked", "--apply")
    self.assertEqual(rc, 0)
    self.assertIn("| F02 | Done | short | Not rechecked |", text)

  def test_plan_only_writes_nothing(self):
    """Without --apply the file is unchanged."""
    rc, text = self.run_tool({"F01": "a", "F02": "b"})
    self.assertEqual(rc, 0)
    self.assertEqual(text, DOC)

  def test_pipe_in_value_escaped(self):
    """A pipe in a value cannot split the cell."""
    _, text = self.run_tool({"F01": "a | b", "F02": "c"}, "--apply")
    self.assertIn("| a \\| b |", text)


if __name__ == "__main__":
  unittest.main()
