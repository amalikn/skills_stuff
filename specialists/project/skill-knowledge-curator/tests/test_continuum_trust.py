"""Continuum pilot regressions: review prompts that mean something, claim drift, stale conflicts (P18, P21, P25, P28).

Each test failed before its fix (references/evaluation.md).

Run: python -m unittest discover -s tests (or `just test`). Safety: files only, under temporary copies.
"""

import unittest

from helpers import COORD_A, COORD_B, FixCase, lib, make_claim

RULE_A = {"text": "The portal must log every login.", "subject": "portal", "predicate": "must", "object": "log every login", "topic": "portal.rules"}
RULE_B = {"text": "The portal must rotate keys.", "subject": "portal", "predicate": "must", "object": "rotate keys", "topic": "portal.rules"}
GATE_A = {"text": "The gateway is Caddy.", "subject": "gateway", "predicate": "is", "object": "Caddy", "topic": "gateway.main"}
GATE_B = {"text": "The gateway is Traefik.", "subject": "gateway", "predicate": "is", "object": "Traefik", "topic": "gateway.main"}


class MultiValuedTest(FixCase, unittest.TestCase):
  """P25: a differing object alone is no signal on a predicate that holds many values."""

  def test_differing_rules_are_not_prompts(self):
    """Two different `must` rules across sources: no pair, no group, no count."""
    self.pipeline("related")
    a, b = self.two_sources(RULE_A, RULE_B)
    _, out, _ = self.kc("candidates")
    self.assertFalse(any(set(p["claims"]) == {a, b} for p in out["pairs"]))
    _, dp, _ = self.kc("decision-points")
    self.assertFalse(any(g["subject"] == "portal" for g in dp["groups"]))
    _, q, _ = self.kc("query", "portal")
    self.assertTrue(all(r["unreviewed_pairs"] == 0 for r in q["results"]))

  def test_multi_valued_still_detects_negation(self):
    """A `must` pair with a negation signal stays a candidate: not exempt from conflict detection."""
    self.pipeline("related")
    a, b = self.two_sources(
      {**RULE_A, "text": "The portal must store passwords in the vault."},
      {**RULE_A, "text": "The portal must not store passwords in the vault.", "object": "not store passwords"},
    )
    _, out, _ = self.kc("candidates")
    row = next(p for p in out["pairs"] if set(p["claims"]) == {a, b})
    self.assertIn("negation-asymmetry", row["signals"])

  def test_project_can_change_the_list(self):
    """A project's config replaces the default list."""
    self.pipeline("related")
    cfg = self.root / ".kc" / "config.yaml"
    data = lib("yaml_io").load(cfg.read_text())
    data["candidates"]["multi_valued_predicates"] = []
    cfg.write_text(lib("yaml_io").dump(data))
    self.two_sources(RULE_A, RULE_B)
    _, dp, _ = self.kc("decision-points")
    self.assertTrue(any(g["subject"] == "portal" for g in dp["groups"]))


class GroupReviewTest(FixCase, unittest.TestCase):
  """P25: a reviewed group counts as classified, and a new claim reopens only itself."""

  def test_group_review_clears_and_new_claim_reopens(self):
    """Dry run writes nothing; apply clears the group; a later claim brings it back with its own pairs only."""
    self.pipeline("related")
    self.two_sources(GATE_A, GATE_B)
    _, dp, _ = self.kc("decision-points")
    gid = next(g["group_id"] for g in dp["groups"] if g["subject"] == "gateway")
    self.assertEqual(self.kc("group-review", gid, "--reason", "same topic read")[0], 0)
    self.assertTrue(any(g["group_id"] == gid for g in self.kc("decision-points")[1]["groups"]))
    code, _, err = self.kc("group-review", gid, "--reason", "same topic read", "--apply")
    self.assertEqual(code, 0, err)
    self.assertFalse(any(g["group_id"] == gid for g in self.kc("decision-points")[1]["groups"]))
    self.assertFalse(any(w for w in self.kc("validate")[1]["warnings"] if "pairs" in w))
    path = self.add_doc("third.md", ["# Doc", "", "The gateway is Nginx."])
    self.ingest([make_claim(path, 3, "The gateway is Nginx.", "gateway", "is", "Nginx", "gateway.main")], "--apply")
    group = next(g for g in self.kc("decision-points")[1]["groups"] if g["subject"] == "gateway")
    self.assertEqual(group["unclassified_pairs"], 2)

  def test_unknown_group_refused(self):
    """An unknown group exits 1."""
    self.pipeline("related")
    self.assertEqual(self.kc("group-review", "dp-nope", "--reason", "r")[0], 1)


SHIM_A = {"text": "The voicemode shims are retained.", "subject": "voicemode shims", "predicate": "status", "object": "retained", "topic": "voicemode.step8"}
SHIM_B = {
  "text": "The voicemode compatibility links are retired.",
  "subject": "voicemode compatibility links",
  "predicate": "ended as",
  "object": "retired",
  "topic": "shims.final",
}


class SubjectWordTest(FixCase, unittest.TestCase):
  """P28: agents working apart share no topic; a rare subject word still groups their claims, without adding raw pairs."""

  def word_group(self, word: str) -> dict | None:
    """The subject-word group for a word.

    Args:
      word: the word.

    Returns:
      The group, or None.
    """
    return next((g for g in self.kc("decision-points")[1]["word_groups"] if g["word"] == word), None)

  def test_different_topics_group_on_a_rare_word(self):
    """Different topic, subject and predicate across sources form a group; candidates stays as it was."""
    self.pipeline("related")
    a, b = self.two_sources(SHIM_A, SHIM_B)
    group = self.word_group("voicemode")
    self.assertEqual({c["claim_id"] for c in group["claims"]}, {a, b})
    self.assertEqual(group["unclassified_pairs"], 1)
    self.assertFalse(any(set(p["claims"]) == {a, b} for p in self.kc("candidates")[1]["pairs"]))

  def test_group_review_clears_a_word_group(self):
    """A word group can be reviewed whole."""
    self.pipeline("related")
    self.two_sources(SHIM_A, SHIM_B)
    gid = self.word_group("voicemode")["group_id"]
    self.assertEqual(self.kc("group-review", gid, "--reason", "read both", "--apply")[0], 0)
    self.assertIsNone(self.word_group("voicemode"))

  def test_same_source_and_multi_valued_stay_out(self):
    """One source, or two claims on a multi-valued predicate, make no word group."""
    self.pipeline("related")
    self.two_sources({**SHIM_A, "predicate": "must"}, {**SHIM_B, "predicate": "must"})
    self.assertIsNone(self.word_group("voicemode"))

  def test_common_word_is_not_a_group(self):
    """A word on more claims than the rarity limit makes no group."""
    self.pipeline("related")
    cfg = self.root / ".kc" / "config.yaml"
    data = lib("yaml_io").load(cfg.read_text())
    data["candidates"]["subject_word_floor"] = 5
    cfg.write_text(lib("yaml_io").dump(data))
    self.two_sources(SHIM_A, SHIM_B)
    path = self.add_doc("many.md", ["# Doc", ""] + [f"Fact {n} of voicemode here." for n in range(8)])
    rows = [make_claim(path, 3 + n, f"Fact {n} of voicemode here.", f"voicemode item {n}", "is", f"thing {n}", "many.rows") for n in range(8)]
    self.ingest(rows, "--apply")
    self.assertIsNone(self.word_group("voicemode"))


class DriftTest(FixCase, unittest.TestCase):
  """P18: claim text is checked against its own excerpt, flagged and never refused."""

  def drifted(self, text: str, excerpt: str) -> dict:
    """Ingest one claim whose text differs from its excerpt.

    Args:
      text: claim text.
      excerpt: the excerpt, which is the source line.

    Returns:
      The kc claims dry-run result.
    """
    path = self.add_doc("drift.md", ["# Doc", "", excerpt])
    code, out, err = self.ingest([make_claim(path, 3, excerpt, "backup", "keeps", "x", "backup.keep", claim_text=text)])
    self.assertEqual(code, 0, err)
    return out

  def test_changed_number_flagged(self):
    """A number absent from the excerpt is flagged."""
    self.pipeline("related")
    self.assertTrue(any("number 30" in w for w in self.drifted("Backups last 30 days.", "Backups last 14 days.")["warnings"]))

  def test_dropped_negation_flagged(self):
    """A negation in the excerpt but not the text is flagged."""
    self.pipeline("related")
    self.assertTrue(any("negation" in w for w in self.drifted("Backups run nightly.", "Backups never run nightly.")["warnings"]))

  def test_new_name_flagged(self):
    """A name the excerpt does not hold is flagged."""
    self.pipeline("related")
    self.assertTrue(any("Restic" in w for w in self.drifted("Backups use Restic nightly.", "Backups run nightly.")["warnings"]))

  def test_faithful_text_quiet(self):
    """A faithful claim gives no drift warning, and kc drift lists only the bad claim."""
    self.pipeline("related")
    self.assertFalse(any("cited lines" in w or "excerpt" in w for w in self.drifted("Backups run nightly.", "Backups run nightly.")["warnings"]))
    _, out, _ = self.kc("drift")
    self.assertEqual(out["counts"]["flagged"], 0)
    path = self.add_doc("bad.md", ["# Doc", "", "Backups last 14 days."])
    self.ingest([make_claim(path, 3, "Backups last 14 days.", "backup", "lasts", "x", "backup.last", claim_text="Backups last 30 days.")], "--apply")
    _, after, _ = self.kc("drift")
    self.assertEqual(after["counts"]["flagged"], 1)
    self.assertEqual(self.kc("drift", "--path", "docs/none*")[1]["counts"]["flagged"], 0)


class StaleConflictTest(FixCase, unittest.TestCase):
  """P21: an open conflict overtaken by a ruling elsewhere says so."""

  def test_superseded_member_and_recommendation_flagged(self):
    """A member superseded elsewhere shows in review, report and validate; so does a recommendation naming it."""
    self.pipeline("related")
    a, b = self.two_sources(COORD_A, COORD_B)
    cf = self.conflict(a, b)
    self.assertEqual(self.kc("decide", cf, "USE_OTHER", "--current", b, "--reason", "r", "--apply")[0], 0)
    path = self.add_doc("third.md", ["# Doc", "", "The coordinator runs Go."])
    self.ingest([make_claim(path, 3, "The coordinator runs Go.", "go service", "runs", "Go", "other.topic")], "--apply")
    other = self.claim_for("The coordinator runs Go.")
    second = self.conflict(a, other, recommended=a)
    _, report, _ = self.kc("report")
    row = next(s for s in report["stale_conflicts"] if s["conflict_id"] == second)
    self.assertTrue(any(a in r and "SUPERSEDED" in r for r in row["reasons"]))
    self.assertTrue(any("recommendation" in r for r in row["reasons"]))
    _, text, _ = self.kc("review")
    self.assertIn("**Stale:**", text)
    self.assertTrue(any("overtaken" in w for w in self.kc("validate")[1]["warnings"]))

  def test_fresh_conflict_not_flagged(self):
    """An open conflict on two live claims is not stale."""
    self.pipeline("related")
    self.conflict(*self.two_sources(COORD_A, COORD_B))
    self.assertEqual(self.kc("report")[1]["stale_conflicts"], [])


if __name__ == "__main__":
  unittest.main()
