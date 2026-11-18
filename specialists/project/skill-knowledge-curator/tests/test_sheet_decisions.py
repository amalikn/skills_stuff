"""sheet_decisions: one tick per question becomes one kc decide call; unticked stays open; two ticks are refused; contract gaps are listed only.

Run: python -m unittest discover -s tests (or `just test`). Safety: read-only; in-memory text only, writes nothing.
"""

import importlib
import unittest

import helpers

sheet_decisions = importlib.import_module("sheet_decisions")

SHEET = """# Operator decision sheet

### 1. cf-aaaaaaaaaa (P2, api, api-shape)

- [ ] A is current [USE_OTHER --current cl-111111111111]
- [x] B is current [USE_OTHER --current cl-222222222222] **(Recommended)**
- [ ] Defer; keep it open, publish neither as settled [DEFER]. Reason:

**Notes:**

Answered in chat; followed the recommendation.

### 2. cf-bbbbbbbbbb (P2, scope)

- [x] Both apply, in different scopes [BOTH_APPLY_SCOPED] **(Recommended)**. Scope: strict mode blocks;
  degraded mode is opt-in.

**Notes:**

### 3. Contract gap: Error payload

- [x] RFC 9457 Problem Details **(Recommended)**

**Notes:**

### 4. cf-cccccccccc (P2, scope)

- [ ] A is current [USE_OTHER --current cl-333333333333]

**Notes:**

### 5. cf-dddddddddd (P2, scope)

- [x] Other: S3-compatible storage from day one.

**Notes:**
"""


class SheetDecisionsTest(unittest.TestCase):
  """Reading ticks into calls."""

  def test_scripts_on_path(self):
    """The helpers module puts scripts/ on sys.path."""
    self.assertTrue(helpers.SCRIPTS.is_dir())

  def test_calls_and_notes(self):
    """Ticked conflicts become calls with the right action, claim and detail; others are listed."""
    calls, notes = sheet_decisions.plan(SHEET, "Operator", " (chat)")
    by_q = {c["q"]: c["args"] for c in calls}
    self.assertEqual(sorted(by_q), [1, 2, 5])
    self.assertEqual(by_q[1][:2], ["cf-aaaaaaaaaa", "USE_OTHER"])
    self.assertIn("cl-222222222222", by_q[1])
    self.assertEqual(by_q[1][by_q[1].index("--reason") + 1], "Answered in chat; followed the recommendation.")
    self.assertEqual(by_q[2][by_q[2].index("--scope-note") + 1], "strict mode blocks; degraded mode is opt-in.")
    self.assertEqual(by_q[5][1], "CORRECTED")
    self.assertEqual(by_q[5][by_q[5].index("--corrected-text") + 1], "S3-compatible storage from day one.")
    self.assertTrue(any(n.startswith("Q3: contract gap") for n in notes))
    self.assertIn("Q4: unticked, stays open", notes)

  def test_two_ticks_refused(self):
    """A question with two ticks stops the run."""
    bad = SHEET.replace("- [ ] A is current [USE_OTHER --current cl-111111111111]", "- [x] A is current [USE_OTHER --current cl-111111111111]")
    with self.assertRaises(ValueError):
      sheet_decisions.plan(bad, "Operator", "")


if __name__ == "__main__":
  unittest.main()
