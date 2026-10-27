"""Inventory and claim intake: accounting, idempotency, renames, symlinks, evidence verification and merge rules.

Covers T01, T06, T09 (handoff) and T-001, T-003, T-005, T-010, T-011, T-012 (design).

Run: python -m unittest discover -s tests (or `just test`). Safety: files only, under temporary copies.
"""

import json
import os
import unittest

from helpers import FIXTURES, PilotCase, lib


class InventoryTest(PilotCase, unittest.TestCase):
  """kc inventory."""

  def test_counts_duplicates_and_rerun(self):
    """Every file is accounted for, byte copies are grouped, and a rerun appends nothing (INV-002, INV-011)."""
    self.kc("init", "--apply")
    code, out, _ = self.kc("inventory", "--apply")
    self.assertEqual(code, 0)
    self.assertEqual(out["counts"]["new"], 8)
    self.assertEqual(out["duplicate_groups"], [["docs/ops-runbook-copy.md", "docs/ops-runbook.md"]])
    before = (self.root / ".kc" / "sources.jsonl").read_bytes()
    _, again, _ = self.kc("inventory", "--apply")
    self.assertEqual(again["counts"]["unchanged"], 8)
    self.assertEqual((self.root / ".kc" / "sources.jsonl").read_bytes(), before)

  def test_rename_keeps_source_id_and_change_adds_version(self):
    """A moved file keeps its source_id; an edited file gets a new version of the same source."""
    self.pipeline("inventoried")
    old = self.state().source_by_path()["docs/notes.md"]["source_id"]
    os.rename(self.root / "docs" / "notes.md", self.root / "docs" / "field-notes.md")
    (self.root / "docs" / "requirements.md").write_text("Status: CURRENT\n\n# Requirements\n\n- New line.\n")
    _, out, _ = self.kc("inventory", "--apply")
    self.assertEqual((out["counts"]["renamed"], out["counts"]["changed"]), (1, 1))
    live = self.state().source_by_path()
    self.assertEqual(live["docs/field-notes.md"]["source_id"], old)
    self.assertEqual(live["docs/field-notes.md"]["renamed_from"], "docs/notes.md")

  def test_symlink_outside_root_excluded(self):
    """A symlink leaving the root is excluded with a reason, never followed (T-012)."""
    outside = self.root.parent / "outside.md"
    outside.write_text("secret plan\n")
    os.symlink(outside, self.root / "docs" / "link.md")
    self.kc("init", "--apply")
    _, out, _ = self.kc("inventory")
    self.assertIn({"path": "docs/link.md", "reason": "symlink pointing outside root"}, out["exclusions"])

  def test_dry_run_writes_nothing(self):
    """Without --apply no .kc folder appears."""
    self.kc("inventory")
    self.assertFalse((self.root / ".kc").exists())


class ClaimsTest(PilotCase, unittest.TestCase):
  """kc claims and coverage."""

  def test_ingest_merges_restatement_and_counts_byte_copies_once(self):
    """The runbook claim from two byte-identical files is one claim with two spans but one independent source (INV-009, case F)."""
    self.pipeline("claimed")
    st = self.state()
    self.assertEqual(len(st.claims), 10)
    backup = st.claims[self.claim_for("Backups run nightly at 02:00.")]
    self.assertEqual(len(backup["evidence"]), 2)
    self.assertEqual(backup["independent_sources"], 1)
    _, again, _ = self.kc("claims", "--file", str(FIXTURES / "pilot-claims.json"), "--apply")
    self.assertEqual((again["claims"], again["skipped"]), (0, 11))

  def _one(self, **change) -> tuple[int, str]:
    """Ingest one modified fixture claim.

    Args:
      **change: fields to replace.

    Returns:
      (exit code, stderr).
    """
    rec = json.loads((FIXTURES / "pilot-claims.json").read_text())[7] | change
    path = self.root.parent / "one.json"
    path.write_text(json.dumps([rec]))
    code, _, err = self.kc("claims", "--file", str(path), "--apply")
    return code, err

  def test_bad_excerpt_rejected_whole_batch(self):
    """An excerpt absent from the cited lines rejects the batch; nothing is appended (T-011)."""
    self.pipeline("inventoried")
    code, err = self._one(evidence=[{"source_path": "docs/requirements.md", "line_start": 5, "line_end": 5, "excerpt": "supports 900 sites"}])
    self.assertEqual(code, 1)
    self.assertIn("excerpt not found", err)
    self.assertFalse((self.root / ".kc" / "claims.jsonl").exists())

  def test_current_without_evidence_refused(self):
    """CURRENT with no evidence and no decision fails INV-005."""
    self.pipeline("inventoried")
    code, err = self._one(evidence=[])
    self.assertEqual(code, 1)
    self.assertIn("INV-005", err)

  def test_unknown_subcategory_refused(self):
    """A subcategory outside the shared taxonomy and the project's extensions is refused with a hint."""
    self.pipeline("inventoried")
    code, err = self._one(subcategories=["throughput"])
    self.assertEqual(code, 1)
    self.assertIn("taxonomy_extensions", err)

  def test_changed_source_exit_5(self):
    """A source edited after inventory makes intake exit 5."""
    self.pipeline("inventoried")
    (self.root / "docs" / "requirements.md").write_text("changed\n")
    code, _ = self._one()
    self.assertEqual(code, 5)

  def test_coverage_and_worksheet(self):
    """Status lines and front matter are auto context; the injection paragraph is flagged in the worksheet (T13)."""
    self.pipeline("claimed")
    cov = lib("claims").coverage(self.state())
    self.assertEqual(cov["counts"]["context"], 7)
    _, sheet, _ = self.kc("worksheet")
    flagged = [s for s in sheet["sections"] if "imperative-text" in s["flags"]]
    self.assertEqual({s["path"] for s in flagged}, {"docs/ops-runbook.md", "docs/ops-runbook-copy.md"})
    self.mark_context()
    self.assertNotIn("pending", lib("claims").coverage(self.state())["counts"])


if __name__ == "__main__":
  unittest.main()
