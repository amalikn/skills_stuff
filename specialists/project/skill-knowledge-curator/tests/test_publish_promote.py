"""Render, promotion, archive plan, retrieval, intake and write safety.

Covers T05, T07-T14 (handoff), T-006, T-007, T-009, T-010, T-012, case E (design).

Run: python -m unittest discover -s tests (or `just test`). Safety: files only, under temporary copies.
"""

import json
import threading
import unittest

from helpers import PilotCase, lib

PAGE = "knowledge/operations.md"
GOV_LINE = "\n- Authoritative operations knowledge: [knowledge/operations.md](knowledge/operations.md)\n"


class RenderTest(PilotCase, unittest.TestCase):
  """kc render."""

  def test_deterministic_and_blocked_section_marked(self):
    """Two renders give identical bytes; the architecture page flags its open P1 and lists both sides as not settled (T09, INV-006)."""
    self.pipeline("decided")
    self.kc("render", "--apply")
    first = {p.name: p.read_bytes() for p in (self.root / "knowledge").iterdir()}
    _, out, _ = self.kc("render", "--apply")
    self.assertEqual(out["changed"], [])
    self.assertEqual({p.name: p.read_bytes() for p in (self.root / "knowledge").iterdir()}, first)
    arch = (self.root / "knowledge" / "architecture.md").read_text()
    self.assertIn("**Not settled:**", arch)
    self.assertIn("## Not settled (REVIEW_REQUIRED)", arch)
    self.assertNotIn("MQTT", arch.split("Not settled (REVIEW_REQUIRED)")[0])
    self.assertIn("MQTT", (self.root / "knowledge" / "history.md").read_text())

  def test_human_navigation_reaches_sources(self):
    """index.md links the page; the page links the source line (T08)."""
    self.pipeline("decided")
    self.kc("render", "--apply")
    self.assertIn("[operations.md](operations.md)", (self.root / "knowledge" / "index.md").read_text())
    self.assertIn("](../docs/requirements.md#L6)", (self.root / PAGE).read_text())

  def test_secret_like_text_refused(self):
    """A secret-like claim makes render refuse to write anything (T13)."""
    self.pipeline("claimed")
    st = self.state()
    cid = next(iter(st.claims))
    st.claims[cid]["claim_text"] = "password: hunter2hunter2"
    with self.assertRaises(lib("errors").ValidationFailed):
      lib("render").render(st)


class PromoteTest(PilotCase, unittest.TestCase):
  """kc promote and kc validate on promoted pages."""

  def _ready(self) -> str:
    """Bring the operations page to promotable state.

    Returns:
      The approved digest.
    """
    self.pipeline("decided")
    self.kc("render", "--apply")
    with (self.root / "AGENTS.md").open("a") as fh:
      fh.write(GOV_LINE)
    self.kc("inventory", "--apply")
    return self.kc("promote", "--page", PAGE)[1]["digest"]

  def test_gates_block_until_met(self):
    """Without approval and the governing line the gates fail; an open P1 page cannot promote (exit 4)."""
    self.pipeline("decided")
    self.kc("render", "--apply")
    _, out, _ = self.kc("promote", "--page", PAGE)
    self.assertFalse(out["gates"]["governing_files"]["pass"])
    self.assertFalse(out["gates"]["operator_decision"]["pass"])
    self.assertTrue(out["gates"]["evidence_verified"]["pass"])
    _, arch, _ = self.kc("promote", "--page", "knowledge/architecture.md")
    code, _, _ = self.kc("promote", "--page", "knowledge/architecture.md", "--approve-digest", arch["digest"], "--reason", "x", "--apply")
    self.assertEqual(code, 4)

  def test_wrong_digest_refused(self):
    """Approval is bound to the exact body digest (T-007)."""
    self._ready()
    code, _, _ = self.kc("promote", "--page", PAGE, "--approve-digest", "0" * 64, "--reason", "x", "--apply")
    self.assertEqual(code, 3)

  def test_promote_then_edit_detected_then_revoke(self):
    """Promotion records the gates; a hand edit fails validate; render leaves the page and writes a proposal; revoke reverts."""
    digest = self._ready()
    code, out, err = self.kc("promote", "--page", PAGE, "--approve-digest", digest, "--reason", "reviewed", "--apply")
    self.assertEqual(code, 0, err)
    self.assertIn("Status: promoted", (self.root / PAGE).read_text())
    self.assertEqual(self.kc("validate")[0], 0)
    with (self.root / PAGE).open("a") as fh:
      fh.write("- hand edit\n")
    self.assertEqual(self.kc("validate")[0], 3)
    _, rendered, _ = self.kc("render", "--apply")
    self.assertEqual(rendered["proposals"], [f".kc/proposals/{PAGE}"])
    self.assertIn("hand edit", (self.root / PAGE).read_text())
    code, _, err = self.kc("promote", "--page", PAGE, "--revoke", "--reason", "undo", "--apply")
    self.assertEqual(code, 0, err)
    self.assertEqual(self.state().promotions[PAGE]["status"], "revoked")

  def test_evidence_gate_catches_edited_source(self):
    """A cited source edited after render fails evidence_verified (side-agent review, 2026-10-27)."""
    self._ready()
    (self.root / "docs" / "requirements.md").write_text("Status: CURRENT\n\n# Requirements\n\n- Backups run weekly.\n")
    _, out, _ = self.kc("promote", "--page", PAGE)
    self.assertFalse(out["gates"]["evidence_verified"]["pass"])


class ArchivePlanTest(PilotCase, unittest.TestCase):
  """kc archive-plan."""

  def test_plan_only_rehearsal_and_referrers(self):
    """Only sources absorbed by promoted pages are candidates; a linking file is reported; the rehearsal verifies bytes; nothing moves."""
    digest = PromoteTest._ready(self)
    self.kc("promote", "--page", PAGE, "--approve-digest", digest, "--reason", "ok", "--apply")
    self.mark_context()
    _, out, _ = self.kc("archive-plan", "--apply")
    self.assertEqual([e["path"] for e in out["entries"]], ["docs/ops-runbook-copy.md", "docs/ops-runbook.md"])
    self.assertEqual(out["referrers"], {"docs/ops-runbook.md": ["docs/notes.md"]})
    self.assertTrue(out["restore_rehearsal"]["ok"])
    self.assertFalse(out["ready"])
    self.assertTrue((self.root / "docs" / "ops-runbook.md").exists())
    self.assertTrue((self.root / ".kc" / "archive-plans" / f"{out['batch_id']}.json").exists())


class RetrievalIntakeTest(PilotCase, unittest.TestCase):
  """kc query and kc intake."""

  def test_query_reports_settlement_and_hides_history(self):
    """A disputed topic answers settled=False with the conflict; superseded claims only with --history (T07, INV-013)."""
    self.pipeline("related")
    _, out, _ = self.kc("query", "A/B recovery")
    self.assertTrue(out["results"])
    self.assertTrue(all(not r["settled"] and r["conflicts"] for r in out["results"]))
    _, plain, _ = self.kc("query", "MQTT transport")
    self.assertNotIn("MQTT", json.dumps([r["text"] for r in plain["results"]]))
    _, hist, _ = self.kc("query", "MQTT transport", "--history")
    self.assertTrue(any(r["disposition"] == "SUPERSEDED" for r in hist["results"]))

  def test_intake_trace_is_one_to_one(self):
    """Every item gets exactly one outcome; routine items skip; a disputed match routes to review (T10-T12)."""
    self.pipeline("related")
    payload = {
      "schema_version": "1.0",
      "mode": "slurp",
      "read_only": True,
      "items": [
        {"item_id": "s1", "type": "operator decision", "text": "Root A/B recovery is rejected for the target image."},
        {"item_id": "s2", "type": "progress", "text": "ran the tests"},
        {"item_id": "s3", "type": "fact", "text": "The NOC rota changes in March."},
      ],
    }
    path = self.root.parent / "payload.json"
    path.write_text(json.dumps(payload))
    _, out, _ = self.kc("intake", "--payload", str(path))
    self.assertEqual([t["item_id"] for t in out["trace"]], ["s1", "s2", "s3"])
    self.assertEqual([t["outcome"] for t in out["trace"]], ["conflict", "skipped", "new_knowledge"])
    path.write_text(json.dumps({**payload, "read_only": False}))
    self.assertEqual(self.kc("intake", "--payload", str(path))[1]["status"], "rejected")


class SafetyTest(PilotCase, unittest.TestCase):
  """Write lock, containment, exit codes, source ownership."""

  def test_path_escape_refused(self):
    """ledger.contained refuses .. and absolute escapes (T-012)."""
    with self.assertRaises(lib("errors").InputError):
      lib("ledger").contained(self.root, "../outside.md")

  def test_second_writer_refused(self):
    """While one writer holds the lock, another fails closed (T-012)."""
    ledger, errors = lib("ledger"), lib("errors")
    hold, done, seen = threading.Event(), threading.Event(), []

    def holder():
      """Hold the lock until told to stop."""
      with ledger.write_lock(self.root):
        hold.set()
        done.wait(5)

    t = threading.Thread(target=holder)
    t.start()
    hold.wait(5)
    try:
      with ledger.write_lock(self.root):
        seen.append("acquired")
    except errors.WriteFailed:
      seen.append("refused")
    done.set()
    t.join(5)
    self.assertEqual(seen, ["refused"])

  def test_usage_error_exit_1_and_sources_untouched(self):
    """Usage errors exit 1; a full run never edits a source document (T14)."""
    self.assertEqual(self.kc("decide")[0], 1)
    before = {p: p.read_bytes() for p in (self.root / "docs").iterdir()}
    self.pipeline("decided")
    self.kc("render", "--apply")
    self.assertEqual({p: p.read_bytes() for p in (self.root / "docs").iterdir()}, before)


if __name__ == "__main__":
  unittest.main()
