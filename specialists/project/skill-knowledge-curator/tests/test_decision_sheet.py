"""decision_sheet: review queue to tick boxes; each position maps to one claim id; one (Recommended) per advised question.

Run: python -m unittest discover -s tests (or `just test`). Safety: files only, under a temporary folder.
"""

import importlib
import json
import tempfile
import unittest
from pathlib import Path

import helpers

decision_sheet = importlib.import_module("decision_sheet")

REVIEW = """# Review queue

### cf-aaaaaaaaaa · P2 · api-shape

**Question:** Stop verb: cancel or abort?

| | Claim | Kind / status | Disposition | Sources |
| --- | --- | --- | --- | --- |
| A | Coordinator exposes POST /cancel. | proposal / PROPOSED | CURRENT | `docs/research/bp/12.md` L125-125 |
| B | Coordinator exposes POST /abort. | proposal / PROPOSED | CURRENT | `docs/research/dp/09.md` L12-12 |

**Assessment:** Same operation, different names.

### cf-bbbbbbbbbb · P1 · scope

**Question:** Is X in scope?

| | Claim | Kind / status | Disposition | Sources |
| --- | --- | --- | --- | --- |
| A | X is in scope. | proposal / PROPOSED | CURRENT | `docs/research/mv.md` L1-1 |
| B | X is out of scope. | proposal / PROPOSED | CURRENT | `docs/research/im.md` L2-2 |

**Assessment:** Opposite scopes.
"""


class DecisionSheetTest(unittest.TestCase):
  """Sheet rendering from a two-conflict queue."""

  def setUp(self):
    """Write a ledger and a saved review queue."""
    self.assertTrue(helpers.SCRIPTS.is_dir())
    tmp = tempfile.TemporaryDirectory()
    self.addCleanup(tmp.cleanup)
    self.root = Path(tmp.name)
    kc = self.root / ".kc"
    kc.mkdir()
    texts = {
      "cl-000000000001": "Coordinator exposes POST /cancel.",
      "cl-000000000002": "Coordinator exposes POST /abort.",
      "cl-000000000003": "X is in scope.",
      "cl-000000000004": "X is out of scope.",
    }
    (kc / "claims.jsonl").write_text("".join(json.dumps({"record": "claim", "claim_id": k, "claim_text": v}) + "\n" for k, v in texts.items()))
    conflicts = [
      {"conflict_id": "cf-aaaaaaaaaa", "claims": ["cl-000000000001", "cl-000000000002"], "topic_key": "contracts.api"},
      {"conflict_id": "cf-bbbbbbbbbb", "claims": ["cl-000000000003", "cl-000000000004"], "topic_key": "scope"},
    ]
    (kc / "conflicts.jsonl").write_text("".join(json.dumps(c) + "\n" for c in conflicts))
    self.review = self.root / "review.md"
    self.review.write_text(REVIEW)
    self.out = self.root / "sheet.md"

  def run_sheet(self, *extra: str) -> int:
    """Run the script with the fixture paths.

    Args:
      extra: further arguments.

    Returns:
      The exit code.
    """
    return decision_sheet.main(["--project", str(self.root), "--review", str(self.review), "--out", str(self.out), *extra])

  def test_boxes_map_to_claim_ids(self):
    """Each position's USE_OTHER box carries its own claim id, and every question has an Other box."""
    self.assertEqual(self.run_sheet(), 0)
    text = self.out.read_text()
    self.assertIn("- [ ] A is current [USE_OTHER --current cl-000000000001]", text)
    self.assertIn("- [ ] B is current [USE_OTHER --current cl-000000000004]", text)
    self.assertEqual(text.count("- [ ] Other: "), 2)
    self.assertNotIn("**(Recommended)**", text)
    self.assertIn("## Open conflicts", text)

  def test_recommendation_and_order(self):
    """A recommendation marks exactly one option; a 'why' puts that question in Part 1."""
    recs = self.root / "recs.json"
    recs.write_text(json.dumps({"cf-bbbbbbbbbb": {"kind": "DEFER", "reason": "later", "why": "needed now"}}))
    self.assertEqual(self.run_sheet("--recs", str(recs)), 0)
    text = self.out.read_text()
    self.assertEqual(text.count("**(Recommended)**"), 2)  # the legend line plus one option
    self.assertLess(text.index("cf-bbbbbbbbbb"), text.index("cf-aaaaaaaaaa"))
    self.assertIn("[DEFER] **(Recommended)**", text)

  def test_filters_and_unmatched_position(self):
    """Severity filter keeps P1 only; an unmatched claim text exits 1 and writes nothing."""
    self.assertEqual(self.run_sheet("--severity", "P1"), 0)
    self.assertNotIn("cf-aaaaaaaaaa", self.out.read_text())
    self.out.unlink()
    self.review.write_text(REVIEW.replace("POST /abort.", "POST /stop."))
    self.assertEqual(self.run_sheet(), 1)
    self.assertFalse(self.out.exists())

  def test_bad_recommendation_kind(self):
    """A recommendation with an unknown kind is refused."""
    recs = self.root / "recs.json"
    recs.write_text(json.dumps({"cf-aaaaaaaaaa": {"kind": "MAYBE", "reason": "x"}}))
    self.assertEqual(self.run_sheet("--recs", str(recs)), 1)


if __name__ == "__main__":
  unittest.main()
