"""Candidates, relations and decisions: conflicts preserved, supersession only on evidence, decisions append-only and revalidated.

Covers T02-T04 (handoff), INV-006-008, INV-016, cases A, C, D and the metamorphic step99 test (design).

Run: python -m unittest discover -s tests (or `just test`). Safety: files only, under temporary copies.
"""

import json
import unittest

from helpers import FIXTURES, PilotCase


class CandidatesTest(PilotCase, unittest.TestCase):
  """kc candidates."""

  def test_signals_found_and_classified_pairs_dropped(self):
    """The four seeded pairs are found with deterministic signals; after relate none is asked again (INV-011)."""
    self.pipeline("claimed")
    _, out, _ = self.kc("candidates")
    self.assertEqual(len(out["pairs"]), 4)
    self.assertTrue(all(p["signals"] for p in out["pairs"]))
    self.kc("relate", "--file", str(FIXTURES / "pilot-relations.json"), "--apply")
    _, after, _ = self.kc("candidates")
    self.assertEqual(after["pairs"], [])

  def test_newer_file_number_does_not_win(self):
    """An unsupported opposite claim in step99.md becomes a candidate, never a silent replacement (INV-008)."""
    self.pipeline("related")
    (self.root / "docs" / "step99.md").write_text("# Step 99\n\nThe provisioning transport is FTP.\n")
    self.kc("inventory", "--apply")
    rec = {
      "record": "claim",
      "subject": "provisioning transport",
      "predicate": "is",
      "object": "FTP",
      "claim_text": "The provisioning transport is FTP.",
      "kind": "observed",
      "epistemic_status": "OBSERVED",
      "primary_category": "architecture",
      "topic_key": "provisioning.transport",
      "disposition": "CURRENT",
      "evidence": [{"source_path": "docs/step99.md", "line_start": 3, "line_end": 3, "excerpt": "transport is FTP"}],
    }
    path = self.root.parent / "s99.json"
    path.write_text(json.dumps([rec]))
    self.kc("claims", "--file", str(path), "--apply")
    https = self.claim_for("The provisioning transport is HTTPS polling.")
    self.assertEqual(self.state().disposition(https), "CURRENT")
    _, out, _ = self.kc("candidates")
    self.assertTrue(any(https in p["claims"] and "same-key-different-object" in p["signals"] for p in out["pairs"]))


class RelationsTest(PilotCase, unittest.TestCase):
  """kc relate."""

  def test_supersession_conflicts_and_scope(self):
    """MQTT is superseded with its successor; two P1 conflicts open; the OS pair stays both current (cases A, scope 6.3)."""
    self.pipeline("related")
    st = self.state()
    mqtt, https = self.claim_for("The provisioning transport is MQTT over TLS."), self.claim_for("The provisioning transport is HTTPS polling.")
    self.assertEqual(st.disposition(mqtt), "SUPERSEDED")
    self.assertEqual(st.dispositions[mqtt]["successor"], https)
    self.assertEqual(len(st.open_conflicts()), 2)
    for text in ("The edge currently runs Ubuntu 22.04.", "The target image will run Ubuntu 24.04."):
      self.assertEqual(st.effective(self.claim_for(text)), "CURRENT")

  def test_conflicting_claims_both_kept_and_blocked(self):
    """Both sides of an open P1 conflict stay in the ledger and publish as REVIEW_REQUIRED (T03, INV-006)."""
    self.pipeline("related")
    st = self.state()
    for text in ("Root A/B recovery is required for the target image.", "Root A/B recovery is rejected for the target image."):
      cid = self.claim_for(text)
      self.assertEqual(st.disposition(cid), "CURRENT")
      self.assertEqual(st.effective(cid), "REVIEW_REQUIRED")

  def test_equivalent_marks_duplicate_keeping_sources(self):
    """Equivalent keeps the better-evidenced claim; the other becomes DUPLICATE with a link."""
    self.pipeline("claimed")
    a, b = self.claim_for("The controller shall support 500 sites."), self.claim_for("WireGuard is proposed for the management tunnel.")
    path = self.root.parent / "eq.json"
    path.write_text(json.dumps([{"record": "relation", "claims": [a, b], "relation": "equivalent", "reason": "test only"}]))
    self.assertEqual(self.kc("relate", "--file", str(path), "--apply")[0], 0)
    st = self.state()
    dup = next(c for c in (a, b) if st.disposition(c) == "DUPLICATE")
    self.assertIn(st.dispositions[dup]["duplicate_of"], (a, b))
    self.assertTrue(st.claims[dup]["evidence"])


class DecisionsTest(PilotCase, unittest.TestCase):
  """kc review and kc decide."""

  def test_review_exit_2_and_dry_run_decide_records_nothing(self):
    """Review exits 2 with open conflicts; decide without --apply appends nothing (no simulated consent)."""
    self.pipeline("related")
    code, text, _ = self.kc("review")
    self.assertEqual(code, 2)
    self.assertIn("Choose (recorded only when you answer)", text)
    cf = self.conflict_for("backups.schedule")
    self.kc("decide", cf, "ACCEPT_RECOMMENDATION", "--reason", "x")
    self.assertFalse((self.root / ".kc" / "decisions.jsonl").exists())

  def test_accept_then_reverse_appends(self):
    """A later decision names the earlier one; both stay (INV-016)."""
    self.pipeline("decided")
    cf = self.conflict_for("backups.schedule")
    nightly = self.claim_for("Backups run nightly at 02:00.")
    self.assertEqual(self.state().disposition(nightly), "SUPERSEDED")
    code, out, err = self.kc("decide", cf, "USE_OTHER", "--current", nightly, "--reason", "requirement withdrawn", "--apply")
    self.assertEqual(code, 0, err)
    st = self.state()
    self.assertEqual(len(st.decisions), 2)
    self.assertEqual(out["decision"]["previous_decision_id"], st.decisions[0]["decision_id"])
    self.assertEqual(st.disposition(nightly), "CURRENT")

  def test_corrected_creates_operator_claim(self):
    """CORRECTED adds an APPROVED decision claim backed by the decision ID and supersedes both sides."""
    self.pipeline("related")
    cf = self.conflict_for("recovery.ab-root")
    code, out, err = self.kc("decide", cf, "CORRECTED", "--corrected-text", "Snapshots replace root A/B for the target image.", "--reason", "owner", "--apply")
    self.assertEqual(code, 0, err)
    st = self.state()
    new = st.claims[out["new_claims"][0]]
    self.assertEqual((new["epistemic_status"], new["decision_id"]), ("APPROVED", out["decision"]["decision_id"]))
    self.assertEqual(st.effective(new["claim_id"]), "CURRENT")

  def test_defer_keeps_conflict_open(self):
    """DEFER records the answer but leaves the conflict open and both claims unsettled."""
    self.pipeline("related")
    cf = self.conflict_for("recovery.ab-root")
    self.kc("decide", cf, "DEFER", "--reason", "need the hardware test", "--apply")
    self.assertEqual(self.state().conflicts[cf]["status"], "open")

  def test_changed_evidence_blocks_decision(self):
    """Editing a cited source between review and decision stops the decision with exit 5 (design 7.8 step 1)."""
    self.pipeline("related")
    (self.root / "docs" / "requirements.md").write_text("Status: CURRENT\n\n# Requirements\n\n- Backups run weekly.\n")
    code, _, err = self.kc("decide", self.conflict_for("backups.schedule"), "ACCEPT_RECOMMENDATION", "--reason", "x", "--apply")
    self.assertEqual(code, 5, err)


if __name__ == "__main__":
  unittest.main()
