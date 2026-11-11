"""Offline tests for scripts/compact_turns.py: one block per speaker turn, wording unchanged, field labels and already-compact turns left alone.

Run: python3 -m unittest discover -s tests
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "compact_turns.py"
_spec = importlib.util.spec_from_file_location("commtracker_compact_turns", SCRIPT)
ct = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = ct
_spec.loader.exec_module(ct)

SRC = """# Meeting

**Participants:**
- A
- B

---

## 1. Start

**Martin:**

First line.

Second line.

> "Quoted one."

> "Quoted two."

After the quote.

**Malik:**

Yes.

## 2. Next
"""

WANT = """# Meeting

**Participants:**
- A
- B

---

## 1. Start

**Martin:**
First line.
Second line.

> "Quoted one."
> "Quoted two."

After the quote.

**Malik:**
Yes.

## 2. Next
"""


class CompactTest(unittest.TestCase):
  """compact() layout and safety."""

  def test_layout(self):
    got, turns = ct.compact(SRC)
    self.assertEqual(got, WANT)
    self.assertEqual(turns, 2)

  def test_wording_kept(self):
    got, _ = ct.compact(SRC)
    self.assertEqual(ct.wording(got), ct.wording(SRC))

  def test_idempotent(self):
    once, _ = ct.compact(SRC)
    twice, turns = ct.compact(once)
    self.assertEqual(once, twice)
    self.assertEqual(turns, 0)

  def test_list_only_label_untouched(self):
    src = "**Items:**\n\n- one\n- two\n"
    self.assertEqual(ct.compact(src)[0], src)

  def test_old_hard_breaks_removed(self):
    src = "**Stu (2:15 PM):**\\\nHi.\\\nThere.\n\n---\n"
    self.assertEqual(ct.compact(src), ("**Stu (2:15 PM):**\nHi.\nThere.\n\n---\n", 1))

  def test_list_inside_turn(self):
    src = "**Malik:**\n\nWe have:\n\n1. One.\n2. Two.\n\nDone.\n"
    want = "**Malik:**\nWe have:\n\n1. One.\n2. Two.\n\nDone.\n"
    self.assertEqual(ct.compact(src)[0], want)


if __name__ == "__main__":
  unittest.main()
