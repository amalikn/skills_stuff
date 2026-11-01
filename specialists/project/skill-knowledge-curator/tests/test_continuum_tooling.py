"""Continuum pilot regressions: decision reach, agent tooling and silent passes (P4, P8-P10, P14-P16, P19).

Each test failed before its fix (references/evaluation.md).

Run: python -m unittest discover -s tests (or `just test`). Safety: files only, under temporary copies.
"""

import unittest

from helpers import COORD_A, COORD_B, FixCase, lib, make_claim


class DecisionReachTest(FixCase, unittest.TestCase):
  """P14, P19: one ruling makes one claim and can reach related claims."""

  def test_corrected_reuses_identical_operator_claim(self):
    """The same corrected wording on a second conflict reuses the first operator claim, whatever its scope (P14)."""
    self.pipeline("related")
    a, b = self.two_sources(COORD_A, COORD_B)
    first = self.conflict(a, b)
    self.kc("decide", first, "CORRECTED", "--corrected-text", "Decided by the spike.", "--reason", "r", "--apply")
    c, d = self.two_sources(
      {
        "text": "The gateway is Caddy.",
        "subject": "gateway",
        "predicate": "is",
        "object": "Caddy",
        "topic": "gateway.main",
        "extra": {"scope": {"environment": "lab"}},
      },
      {
        "text": "The gateway is Traefik.",
        "subject": "gateway",
        "predicate": "is",
        "object": "Traefik",
        "topic": "gateway.main",
        "extra": {"scope": {"environment": "lab"}},
      },
    )
    second = self.conflict(c, d)
    code, out, err = self.kc("decide", second, "CORRECTED", "--corrected-text", "Decided by the spike.", "--reason", "r", "--apply")
    self.assertEqual(code, 0, err)
    self.assertEqual(out["new_claims"], [])
    same = [cid for cid, x in self.state().claims.items() if x["claim_text"] == "Decided by the spike."]
    self.assertEqual(len(same), 1)
    self.assertEqual(self.state().disposition(c), "SUPERSEDED")

  def decided(self) -> tuple[str, str, str]:
    """A decided conflict and an unrelated current claim.

    Returns:
      (conflict ID, winning claim, third claim).
    """
    self.pipeline("related")
    a, b = self.two_sources(COORD_A, COORD_B)
    cf = self.conflict(a, b)
    self.kc("decide", cf, "USE_OTHER", "--current", a, "--reason", "r", "--apply")
    path = self.add_doc("third.md", ["# Doc", "", "The coordinator runs Go."])
    self.ingest([make_claim(path, 3, "The coordinator runs Go.", "go service", "runs", "Go", "other.topic")], "--apply")
    return cf, a, self.claim_for("The coordinator runs Go.")

  def test_amend_supersedes_extra_claim(self):
    """Kc amend adds a claim to a decided conflict and supersedes it, linked to the earlier decision (P19)."""
    cf, winner, extra = self.decided()
    code, plan, err = self.kc("amend", cf, "--add-claim", extra, "--supersede", "--reason", "the ruling covers it too")
    self.assertEqual(code, 0, err)
    self.assertEqual(self.state().disposition(extra), "CURRENT")
    code, _, err = self.kc("amend", cf, "--add-claim", extra, "--supersede", "--reason", "the ruling covers it too", "--apply")
    self.assertEqual(code, 0, err)
    st = self.state()
    self.assertEqual(st.disposition(extra), "SUPERSEDED")
    self.assertEqual(st.dispositions[extra]["successor"], winner)
    self.assertIn(extra, st.conflicts[cf]["claims"])
    self.assertEqual(st.decisions[-1]["action"], "AMEND")
    self.assertEqual(st.decisions[-1]["previous_decision_id"], st.decisions[-2]["decision_id"])
    self.assertEqual(plan["decision"]["added_claim"], extra)
    _, val, _ = self.kc("validate")
    self.assertTrue(val["ok"], val["errors"])

  def test_amend_keep_on_open_conflict_renders_a_card(self):
    """A third claim on an open conflict stays current and the review card still prints it."""
    self.pipeline("related")
    a, b = self.two_sources(COORD_A, COORD_B)
    cf = self.conflict(a, b)
    path = self.add_doc("third.md", ["# Doc", "", "The coordinator runs Go."])
    self.ingest([make_claim(path, 3, "The coordinator runs Go.", "go service", "runs", "Go", "other.topic")], "--apply")
    extra = self.claim_for("The coordinator runs Go.")
    code, _, err = self.kc("amend", cf, "--add-claim", extra, "--keep", "--reason", "same question", "--apply")
    self.assertEqual(code, 0, err)
    code, text, _ = self.kc("review")
    self.assertEqual(code, 2)
    self.assertIn("| C | The coordinator runs Go.", text)

  def test_amend_refusals(self):
    """Supersede on an open conflict, a duplicate add, or an unknown claim are refused (exit 1)."""
    cf, winner, _ = self.decided()
    self.assertEqual(self.kc("amend", cf, "--add-claim", winner, "--keep", "--reason", "r")[0], 1)
    self.assertEqual(self.kc("amend", cf, "--add-claim", "cl-nope", "--keep", "--reason", "r")[0], 1)
    a, b = next((c, d) for c, d in [tuple(x["claims"]) for x in self.state().conflicts.values() if x["status"] == "open"])
    opened = lib("relations").conflict_id_for([a, b])
    extra = self.claim_for("The coordinator runs Go.")
    self.assertEqual(self.kc("amend", opened, "--add-claim", extra, "--supersede", "--reason", "r")[0], 1)


class AgentToolingTest(FixCase, unittest.TestCase):
  """P9, P10, P16: parallel agents need no helper scripts."""

  def test_dry_run_reports_sections_closed(self):
    """A dry run names the sections the batch would close, and --coverage gives each file's remainder (P9, P16)."""
    self.pipeline("related")
    path = self.add_doc("gap.md", ["# One", "", "First fact.", "", "# Two", "", "Second fact."])
    code, out, err = self.ingest([make_claim(path, 3, "First fact.", "fact", "is", "first", "gap.one")], "--coverage")
    self.assertEqual(code, 0, err)
    self.assertEqual(len(out["sections_closed"]), 1)
    self.assertEqual(out["coverage"][path]["pending_after"], 1)

  def test_worksheet_path_and_sections_listing(self):
    """Worksheet --path narrows to one file; kc sections lists ids, status and claim ids by file (P16)."""
    self.pipeline("related")
    path = self.add_doc("gap.md", ["# One", "", "First fact."])
    self.add_doc("gap2.md", ["# One", "", "Other fact."])
    _, ws, _ = self.kc("worksheet", "--path", "docs/gap.md")
    self.assertEqual({s["path"] for s in ws["sections"]}, {path})
    _, secs, _ = self.kc("sections", "--path", "docs/design-2026*")
    self.assertTrue(secs["sections"])
    self.assertTrue(all(s["path"] == "docs/design-2026.md" for s in secs["sections"]))
    self.assertTrue(any(s["claim_ids"] for s in secs["sections"]))

  def test_evidence_error_quotes_lines_and_nearest_match(self):
    """A wrong line range shows what those lines hold and where the excerpt really is (P10)."""
    self.pipeline("related")
    path = self.add_doc("gap.md", ["# One", "", "", "First fact is here."])
    code, _, err = self.ingest([make_claim(path, 3, "First fact is here.", "fact", "is", "first", "gap.one")])
    self.assertEqual(code, 1)
    self.assertIn("cited lines hold", err)
    self.assertIn("found at line 4", err)


class SilentPassTest(FixCase, unittest.TestCase):
  """P4, P8, P15: gaps are reported, not passed over."""

  def test_historical_needs_a_basis(self):
    """HISTORICAL with neither successor nor historical_basis is refused; a successor is recorded and linked both ways (P4)."""
    self.pipeline("related")
    path = self.add_doc("old.md", ["# Old", "", "In v0.2 the portal used Rails."])
    bare = make_claim(path, 3, "In v0.2 the portal used Rails.", "portal", "used", "Rails", "portal.stack", disposition="HISTORICAL")
    self.assertEqual(self.ingest([bare])[0], 1)
    https = self.claim_for("The provisioning transport is HTTPS polling.")
    code, _, err = self.ingest([{**bare, "successor": https}], "--apply")
    self.assertEqual(code, 0, err)
    st = self.state()
    old = self.claim_for("In v0.2 the portal used Rails.")
    self.assertEqual(st.dispositions[old]["successor"], https)
    self.kc("render", "--apply")
    page = (self.root / "knowledge" / "architecture.md").read_text()
    self.assertIn(f"replaces `{old}`", page)

  def test_historical_source_stated_basis_accepted(self):
    """A source-stated basis is accepted when no successor claim exists (P4)."""
    self.pipeline("related")
    path = self.add_doc("old.md", ["# Old", "", "In v0.2 the portal used Rails."])
    rec = make_claim(
      path, 3, "In v0.2 the portal used Rails.", "portal", "used", "Rails", "portal.stack", disposition="HISTORICAL", historical_basis="source-stated"
    )
    self.assertEqual(self.ingest([rec])[0], 0)

  def test_validate_strict_fails_on_pending(self):
    """Plain validate passes with pending sections; --strict exits 3 (P8)."""
    self.pipeline("inventoried")
    self.assertEqual(self.kc("validate")[0], 0)
    self.assertEqual(self.kc("validate", "--strict")[0], 3)

  def test_archive_folder_is_inventoried_but_archive_dir_is_not(self):
    """A source pack's archive/ is read; the curator's own archive_dir stays out (P15)."""
    (self.root / "pack" / "archive").mkdir(parents=True)
    (self.root / "pack" / "archive" / "old.md").write_text("# Old\n")
    (self.root / "archive" / "originals").mkdir(parents=True)
    (self.root / "archive" / "originals" / "kept.md").write_text("# Kept\n")
    self.kc("init", "--apply")
    _, out, _ = self.kc("inventory", "--apply")
    live = self.state().source_by_path()
    self.assertIn("pack/archive/old.md", live)
    self.assertNotIn("archive/originals/kept.md", live)
    self.assertEqual(out["warnings"], [])

  def test_excluded_folder_holding_markdown_warns(self):
    """A project-excluded folder with Markdown is named in warnings (P15)."""
    (self.root / "legacy").mkdir()
    (self.root / "legacy" / "old.md").write_text("# Old\n")
    self.kc("init", "--apply")
    cfg = self.root / ".kc" / "config.yaml"
    cfg.write_text(cfg.read_text().replace("- .git\n", "- .git\n- legacy\n"))
    _, out, _ = self.kc("inventory")
    self.assertTrue(any("legacy" in w and "1 Markdown" in w for w in out["warnings"]))


if __name__ == "__main__":
  unittest.main()
