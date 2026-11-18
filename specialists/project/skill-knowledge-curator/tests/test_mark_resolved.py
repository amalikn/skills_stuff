"""mark_resolved: rows, list items (id anywhere in the block) and conflict sections get one note each; a second run changes nothing; open prose is reported.

Run: python -m unittest discover -s tests (or `just test`). Safety: read-only; in-memory text only, writes nothing.
"""

import importlib
import unittest

import helpers

mark_resolved = importlib.import_module("mark_resolved")

DEC = {"cf-aaaaaaaaaa": ("dr-111111111111", "USE_OTHER", "2026-11-18"), "cf-bbbbbbbbbb": ("dr-222222222222", "DEFER", "2026-11-18")}
SUMM = {"cf-aaaaaaaaaa": "abort", "cf-bbbbbbbbbb": "deferred to parking"}
PAGE = """# Page

| cf-aaaaaaaaaa (P2) | cancel vs abort | bp vs dp | Which verb? |

- A long item that mentions the parking endpoint question somewhere after the sixtieth column, cf-bbbbbbbbbb, and goes on.
  It continues here.

The stop verb stays open (cf-aaaaaaaaaa).

### cf-aaaaaaaaaa (P2, api-shape)

Question: which verb?

Status: open; registered 2026-11-05.
"""


class MarkResolvedTest(unittest.TestCase):
  """Marking decided conflicts."""

  def test_scripts_on_path(self):
    """The helpers module puts scripts/ on sys.path."""
    self.assertTrue(helpers.SCRIPTS.is_dir())

  def test_marks_each_place_once(self):
    """One row, one item (id past column 60) and one section are marked; a second run is a no-op."""
    new, counts = mark_resolved.mark_text(PAGE, DEC, SUMM, None, 200)
    self.assertEqual(counts, {"row": 1, "item": 1, "section": 1})
    self.assertIn("Resolved 2026-11-18: `dr-111111111111` (abort). |", new)
    self.assertIn("Deferred 2026-11-18: `dr-222222222222` (deferred to parking).", " ".join(new.split()))
    self.assertNotIn("Status: open", new)
    again, counts2 = mark_resolved.mark_text(new, DEC, SUMM, None, 200)
    self.assertEqual(again, new)
    self.assertEqual(counts2, {"row": 0, "item": 0, "section": 0})

  def test_reports_open_prose(self):
    """A prose sentence that still calls a decided conflict open is reported for a hand edit."""
    new, _ = mark_resolved.mark_text(PAGE, DEC, SUMM, None, 200)
    hits = mark_resolved.open_prose(new, SUMM)
    self.assertTrue(any("stays open" in h for h in hits))


if __name__ == "__main__":
  unittest.main()
