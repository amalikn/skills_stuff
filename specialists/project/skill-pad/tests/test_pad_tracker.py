"""Offline tests for pad_tracker.py: parse and render round trip, rebuild from Pad rows, hand-edit refusal. Run: python3 -m unittest test_pad_tracker."""

import importlib.util
import json
import sys
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location("pad_tracker", Path(__file__).resolve().parents[1] / "scripts" / "pad_tracker.py")
pt = importlib.util.module_from_spec(_spec)
sys.modules["pad_tracker"] = pt  # dataclasses look the module up by name while the class is built
_spec.loader.exec_module(pt)

SAMPLE = """---
Title: x
---

# Tracker

Intro text.

### Section A

Source: notes.

- [x] **N01 (P1)** first bug
  - Cause: a `thing` in [f.py](f.py).
  - Closed 20261109.
- [ ] **N02 (P2)** second bug
  - Cause: other.

### Section B

- [ ] parent feature
  - [x] child one
  - [ ] child two
    - [ ] grandchild
- [ ] lone feature
"""


def rows_from(text: str) -> list[dict]:
  """Simulate the Pad rows an import of `text` would create.

  Args:
    text: a tracker file.

  Returns:
    Rows shaped like `pad item list --full --format json`.
  """
  rows, n = [], [0]

  def add(it, section, order, parent):
    n[0] += 1
    ref = f"X-{n[0]}"
    rows.append({"ref": ref, "parent_ref": parent, "content": pt.to_body(it),
                 "fields": json.dumps({"status": "fixed" if it.done else "open", "section": section, "order": order})})
    for k, ch in enumerate(it.children, 1):
      add(ch, section, k * 10, ref)

  L = text.split("\n")
  for section, s, e in pt.runs(text):
    for k, it in enumerate(pt.parse_items(L[s:e]), 1):
      add(it, section, k * 10, None)
  return rows


class RoundTrip(unittest.TestCase):
  """The file survives import and export unchanged apart from the markers."""

  def test_parse_render_identity(self):
    """Each run renders back to its exact text.

    Returns:
      None.
    """
    L = SAMPLE.split("\n")
    found = pt.runs(SAMPLE)
    self.assertEqual([r[0] for r in found], ["Section A", "Section B"])
    for _, s, e in found:
      self.assertEqual(pt.render(pt.parse_items(L[s:e])), "\n".join(L[s:e]))

  def test_export_from_rows_matches_original(self):
    """Markers inserted, blocks filled from simulated Pad rows: stripping the markers gives the original back.

    Returns:
      None.
    """
    L = SAMPLE.split("\n")
    for section, s, e in reversed(pt.runs(SAMPLE)):
      body = "\n".join(L[s:e])
      L[s:e] = [f'<!-- pad:generated collection=bugs section="{section}" sha={pt.sha(body)}; edit in Pad, not here -->', *L[s:e], pt.END]
    new, refused = pt.export_text("\n".join(L), "bugs", pt.from_pad(rows_from(SAMPLE)))
    self.assertEqual(refused, [])
    self.assertEqual(pt.strip_markers(new), SAMPLE)

  def test_hand_edit_is_refused(self):
    """A block whose text no longer matches its marker hash is left alone and reported.

    Returns:
      None.
    """
    body = "- [ ] a"
    text = f'<!-- pad:generated collection=bugs section="S" sha={pt.sha(body)}; edit in Pad, not here -->\n- [ ] a edited\n{pt.END}'
    new, refused = pt.export_text(text, "bugs", {"S": []})
    self.assertEqual((refused, new), (["S"], text))

  def test_title(self):
    """Titles drop markup and stay within 100 characters.

    Returns:
      None.
    """
    self.assertEqual(pt.title_of("**N01 (P1)** see [f](f.py) `x`"), "N01 (P1) see f x")
    self.assertLessEqual(len(pt.title_of("word " * 40)), 100)


class Links(unittest.TestCase):
  """Relative repo links go into Pad as opener links and come back unchanged; links that cannot be opened are left alone."""

  def setUp(self):
    import tempfile
    self.tmp = tempfile.TemporaryDirectory()
    root = Path(self.tmp.name)
    (root / "lab" / "logic").mkdir(parents=True)
    (root / "lab" / "logic" / "x2.py").write_text("x\n")
    (root / "docs" / "trackers").mkdir(parents=True)
    self.base = root / "docs" / "trackers"
    self.x2 = str(root / "lab" / "logic" / "x2.py")

  def tearDown(self):
    self.tmp.cleanup()

  def test_round_trip_with_line_anchor(self):
    text = "- Cause: [x2.py:86](../../lab/logic/x2.py#L86) and [x2.py](../../lab/logic/x2.py)."
    to = pt.to_pad_links(text, self.base, 47800)
    self.assertIn("http://127.0.0.1:47800/open" + self.x2 + "?f=L86", to)
    self.assertNotIn("](../", to)
    self.assertEqual(pt.from_pad_links(to, self.base), text)

  def test_left_alone(self):
    text = "[web](https://example.com/a) [here](#section) [gone](../../lab/missing.py) [mail](mailto:a@b)"
    self.assertEqual(pt.to_pad_links(text, self.base, 47800), text)
    self.assertEqual(pt.from_pad_links(text, self.base), text)

  def test_export_turns_opener_links_back(self):
    body = pt.to_pad_links("**N09 (P1)** x\n  - Cause: [x2.py](../../lab/logic/x2.py#L5).", self.base, 47800)
    rows = [{"ref": "BUG-1", "content": pt.from_pad_links(body, self.base), "fields": {"status": "fixed", "section": "A", "order": 10}}]
    self.assertIn("](../../lab/logic/x2.py#L5)", pt.render(pt.from_pad(rows)["A"]))


if __name__ == "__main__":
  unittest.main()
