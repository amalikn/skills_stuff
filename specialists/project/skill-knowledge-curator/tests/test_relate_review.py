"""Relate and reading views after the MCP pilot: overtaken conflicts, dated order, byte copies (evaluation.md P30-P32).

Each test failed before its fix.

Run: python -m unittest discover -s tests (or `just test`). Safety: files only, under temporary copies.
"""

import json
import unittest

from helpers import COORD_A, COORD_B, FixCase, make_claim


class RelateCase(FixCase):
  """Helpers for relation files."""

  def relate(self, records: list[dict], *flags: str) -> tuple[int, dict, str]:
    """Run kc relate.

    Args:
      records: relation inputs.
      *flags: extra options.

    Returns:
      The kc result.
    """
    path = self.root.parent / "relations.json"
    path.write_text(json.dumps(records))
    return self.kc("relate", "--file", str(path), *flags)


class OvertakenTest(RelateCase, unittest.TestCase):
  """P30: opening a conflict on a claim no longer live is warned about, never refused."""

  def test_conflict_on_a_superseded_claim_warns(self):
    """A claim already superseded, or superseded earlier in the batch, draws a warning naming it."""
    self.pipeline("related")
    a, b = self.two_sources(COORD_A, COORD_B)
    path = self.add_doc("third.md", ["# Doc", "", "The coordinator runs Go. This replaces the keep-Fastify note."])
    self.ingest([make_claim(path, 3, "The coordinator runs Go.", "go service", "runs", "Go", "other.topic")], "--apply")
    c = self.claim_for("The coordinator runs Go.")
    span = {"source_path": path, "line_start": 3, "line_end": 3, "excerpt": "This replaces the keep-Fastify note."}
    evolve = {
      "record": "relation",
      "claims": [a, c],
      "relation": "time-evolution",
      "reason": "stated",
      "superseded": a,
      "successor": c,
      "supersession_evidence": span,
    }
    conflict = {"record": "relation", "claims": [a, b], "relation": "true-conflict", "severity": "P2", "reason": "they differ", "question": "which?"}
    code, out, err = self.relate([evolve, conflict])
    self.assertEqual(code, 0, err)
    self.assertTrue(any(a in w and "overtaken" in w for w in out["warnings"]))


class DatedOrderTest(RelateCase, unittest.TestCase):
  """P31: time-evolution with no stated replacement is proposed for the operator, never applied."""

  def proposal(self, a: str, b: str) -> dict:
    """A dated-order proposal.

    Args:
      a: earlier claim.
      b: later claim.

    Returns:
      The relation input.
    """
    return {
      "record": "relation",
      "claims": [a, b],
      "relation": "time-evolution",
      "basis": "dated-order",
      "reason": "step8 precedes step12",
      "superseded": a,
      "successor": b,
    }

  def test_opens_a_conflict_and_changes_no_disposition(self):
    """It needs no evidence, keeps both claims, and recommends the later claim."""
    self.pipeline("related")
    a, b = self.two_sources(COORD_A, COORD_B)
    code, _, err = self.relate([self.proposal(a, b)], "--apply")
    self.assertEqual(code, 0, err)
    st = self.state()
    self.assertEqual(st.disposition(a), "CURRENT")
    cf = next(c for c in st.conflicts.values() if a in c["claims"])
    self.assertEqual(cf["conflict_type"], "time-evolution-proposed")
    self.assertEqual(cf["recommended_current"], b)
    self.assertEqual(cf["severity"], "P2")

  def test_stated_supersession_still_needs_evidence(self):
    """Without the dated-order basis the evidence rule stands."""
    self.pipeline("related")
    a, b = self.two_sources(COORD_A, COORD_B)
    rec = self.proposal(a, b)
    del rec["basis"]
    self.assertEqual(self.relate([rec])[0], 1)


class ByteCopyViewTest(RelateCase, unittest.TestCase):
  """P32: reading views show a claim once, and name byte copies."""

  def test_copy_marked_and_listing_deduplicated(self):
    """Topics lists one path per byte group with the copies beside it; by-file repeats no claim."""
    self.pipeline("inventoried")
    text = (self.root / "docs" / "ops-runbook.md").read_text().splitlines()
    line = next(n for n, row in enumerate(text, 1) if row.strip() and not row.startswith(("#", "Status")))
    excerpt = text[line - 1].strip()
    rec = make_claim("docs/ops-runbook.md", line, excerpt, "runbook", "says", "x", "ops.run")
    rec["evidence"].append({"source_path": "docs/ops-runbook-copy.md", "line_start": line, "line_end": line, "excerpt": excerpt})
    rec["evidence"].append({"source_path": "docs/ops-runbook.md", "line_start": line, "line_end": line + 1, "excerpt": excerpt})
    self.ingest([rec], "--apply")
    row = self.kc("topics")[1]["topics"]["ops.run"][0]
    self.assertTrue(all("copy" not in line_ref for line_ref in row["lines"]))
    self.assertEqual(row["byte_copies"], ["docs/ops-runbook-copy.md"])
    listed = self.kc("topics", "--by-file")[1]["files"]["docs/ops-runbook.md"]
    self.assertEqual(len(listed), 1)


if __name__ == "__main__":
  unittest.main()
