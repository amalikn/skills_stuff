"""Offline tests for scripts/verify_quotes.py: verbatim check, speaker attribution, entry boundaries.

Run: python3 -m unittest discover -s tests
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_quotes.py"
_spec = importlib.util.spec_from_file_location("commtracker_verify_quotes", SCRIPT)
vq = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = vq
_spec.loader.exec_module(vq)

TRANSCRIPT = """# Meeting

**Martin:**
I don't want to retrofit this
later.

**Sandro (9:40 AM):**
We're running in the dark.

**End of available recording.**
"""

TRACKER = """## Meeting 1 - 20260101 - Old

- Martin: *"not in this entry"*

---

## Meeting 2 - 20260102 - New

- Martin: *"I don't want to retrofit this later."*
- Sandro: *"We're running in the dark."*

---
"""


class VerifyQuotesTest(unittest.TestCase):
  """entry_text() and check()."""

  def test_entry_bounded(self):
    entry = vq.entry_text(TRACKER, "## Meeting 2 - ")
    self.assertIn("retrofit", entry)
    self.assertNotIn("not in this entry", entry)

  def test_all_pass_across_line_wrap_and_timed_label(self):
    self.assertEqual(vq.check(vq.entry_text(TRACKER, "## Meeting 2 - "), TRANSCRIPT), [])

  def test_misattributed(self):
    probs = vq.check('- Martin: *"We\'re running in the dark."*', TRANSCRIPT)
    self.assertEqual(len(probs), 1)
    self.assertIn("said by Sandro", probs[0])

  def test_not_verbatim(self):
    probs = vq.check('*"We are running in the dark."*', TRANSCRIPT)
    self.assertTrue(probs[0].startswith("NOT VERBATIM"))

  def test_missing_heading(self):
    with self.assertRaises(ValueError):
      vq.entry_text(TRACKER, "## Meeting 9 - ")

  def test_lead_in_phrase_is_not_a_speaker(self):
    self.assertEqual(vq.check('On a later point: *"We\'re running in the dark."*', TRANSCRIPT), [])

  def test_bold_field_is_not_a_quote(self):
    self.assertEqual(vq.QUOTE.findall('**"Our Business Req" (centre):** text'), [])

  def test_emphasis_in_source_ignored(self):
    self.assertEqual(vq.check('*"a near-verbatim cleaned transcript"*', "**Note:** a near-verbatim *cleaned* transcript."), [])

  def test_ellipsis_inside_quote_is_not_verbatim(self):
    probs = vq.check('*"I don\'t want to retrofit…"*', TRANSCRIPT)
    self.assertTrue(probs and probs[0].startswith("NOT VERBATIM"))


if __name__ == "__main__":
  unittest.main()
