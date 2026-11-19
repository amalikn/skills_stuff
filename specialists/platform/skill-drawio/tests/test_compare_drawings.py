"""Offline tests for compare_drawings: a geometry or style change alone exits 0, a changed or added label exits 1, a compressed page is read.

Run: `just test`. The scripts folder is put on sys.path, as a consuming project does.
"""

from __future__ import annotations

import contextlib
import importlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
compare_drawings = importlib.import_module("compare_drawings")
read = importlib.import_module("drawio.read")


def drawing(label: str, x: str = "10", style: str = "rounded=1;", compressed: bool = False) -> str:
  """A one-page drawing with one labelled box.

  Args:
    label: the box's label.
    x: its x position.
    style: its style.
    compressed: store the page compressed, as draw.io desktop does.

  Returns:
    The .drawio file text.
  """
  model = (
    f'<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/><mxCell id="b" value="{label}" style="{style}" vertex="1" parent="1">'
    f'<mxGeometry x="{x}" y="20" width="80" height="40" as="geometry"/></mxCell></root></mxGraphModel>'
  )
  body = read.encode_page(model) if compressed else model
  return f'<mxfile><diagram name="Page-1" id="p">{body}</diagram></mxfile>'


class Diff(unittest.TestCase):
  """Label changes are told apart from layout and style changes."""

  def run_diff(self, old: str, new: str) -> tuple[int, str]:
    """Write two drawings and diff them.

    Args:
      old: the first file's text.
      new: the second file's text.

    Returns:
      (exit code, printed output).
    """
    with tempfile.TemporaryDirectory() as tmp:
      a, b = Path(tmp) / "a.drawio", Path(tmp) / "b.drawio"
      a.write_text(old)
      b.write_text(new)
      out = io.StringIO()
      with contextlib.redirect_stdout(out):
        rc = compare_drawings.main([str(a), str(b)])
      return rc, out.getvalue()

  def test_geometry_and_style_only_exit_0(self):
    rc, out = self.run_diff(drawing("Start"), drawing("Start", x="30", style="rounded=1;locked=1;"))
    self.assertEqual(rc, 0)
    self.assertIn("label 0, style 1, geometry 1", out)

  def test_label_change_exits_1(self):
    rc, out = self.run_diff(drawing("Start"), drawing("Begin"))
    self.assertEqual(rc, 1)
    self.assertIn("'Start' -> 'Begin'", out)

  def test_compressed_page_is_read(self):
    rc, out = self.run_diff(drawing("Start", compressed=True), drawing("Start"))
    self.assertEqual(rc, 0)
    self.assertIn("cells 3 -> 3", out)

  def test_unreadable_file_exits_2(self):
    with tempfile.TemporaryDirectory() as tmp:
      bad = Path(tmp) / "bad.drawio"
      bad.write_text("not xml")
      with contextlib.redirect_stderr(io.StringIO()):
        self.assertEqual(compare_drawings.main([str(bad), str(bad)]), 2)


if __name__ == "__main__":
  unittest.main()
