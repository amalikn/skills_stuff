"""Continuum pilot regressions: retrieval flags, cross-source recall and ranking (P1-P3, P12, P13, P20).

Each test failed before its fix (references/evaluation.md).

Run: python -m unittest discover -s tests (or `just test`). Safety: files only, under temporary copies.
"""

import unittest

from helpers import COORD_A, COORD_B, FixCase, make_claim


class RetrievalTest(FixCase, unittest.TestCase):
  """P20, P3: a disputed or unreviewed claim never reads as settled."""

  def test_p2_conflict_is_not_settled(self):
    """A P2 conflict leaves the claim CURRENT but query says settled false (conflicts-and-review.md)."""
    self.pipeline("related")
    a, b = self.two_sources(COORD_A, COORD_B)
    self.conflict(a, b, "P2")
    _, out, _ = self.kc("query", "coordinator")
    row = next(r for r in out["results"] if r["claim_id"] == a)
    self.assertEqual(row["disposition"], "CURRENT")
    self.assertFalse(row["settled"])

  def test_unreviewed_pairs_shown_and_warned(self):
    """Same-key claims from two sources with no classification show a count in query and a validate warning (P3)."""
    self.pipeline("related")
    self.two_sources(
      {"text": "The gateway is Caddy.", "subject": "gateway", "predicate": "is", "object": "Caddy", "topic": "gateway.main"},
      {"text": "The gateway is Traefik.", "subject": "gateway", "predicate": "is", "object": "Traefik", "topic": "gateway.main"},
    )
    _, out, _ = self.kc("query", "gateway")
    self.assertTrue(all(r["unreviewed_pairs"] == 1 for r in out["results"] if "gateway is" in r["text"]))
    _, val, _ = self.kc("validate")
    self.assertTrue(any("unreviewed" in w for w in val["warnings"]))


class RecallTest(FixCase, unittest.TestCase):
  """P1, P12: cross-source disagreement does not depend on identical wording."""

  def test_different_predicate_pairs_across_sources(self):
    """The Continuum deciding probe: same subject, different predicate wording, two sources."""
    self.pipeline("related")
    a, b = self.two_sources(COORD_A, COORD_B)
    _, out, _ = self.kc("candidates")
    self.assertTrue(any(set(p["claims"]) == {a, b} for p in out["pairs"]))

  def test_near_subject_pairs_across_sources(self):
    """A subject worded with an extra word still pairs when the topic is shared."""
    self.pipeline("related")
    a, b = self.two_sources(COORD_A, {**COORD_B, "subject": "coordinator"})
    _, out, _ = self.kc("candidates")
    self.assertTrue(any(set(p["claims"]) == {a, b} for p in out["pairs"]))

  def test_reworded_subject_and_predicate_pair_across_sources(self):
    """Both subject and predicate reworded: a shared subject word within one topic still pairs (the real Continuum wording)."""
    self.pipeline("related")
    a, b = self.two_sources(COORD_A, {**COORD_B, "subject": "coordinator implementation", "predicate": "is implemented with"})
    _, out, _ = self.kc("candidates")
    self.assertTrue(any(set(p["claims"]) == {a, b} for p in out["pairs"]))

  def test_provenance_scope_does_not_hide_conflict(self):
    """A source key in scope no longer makes a cross-source pair non-overlapping (P12)."""
    self.pipeline("related")
    a, b = self.two_sources(
      {
        "text": "The gateway is Caddy.",
        "subject": "gateway",
        "predicate": "is",
        "object": "Caddy",
        "topic": "gateway.main",
        "extra": {"scope": {"source": "left"}},
      },
      {
        "text": "The gateway is Traefik.",
        "subject": "gateway",
        "predicate": "is",
        "object": "Traefik",
        "topic": "gateway.main",
        "extra": {"scope": {"source": "right"}},
      },
    )
    _, out, _ = self.kc("candidates")
    row = next(p for p in out["pairs"] if set(p["claims"]) == {a, b})
    self.assertIn("same-key-different-object", row["signals"])

  def test_real_scope_still_separates(self):
    """A situational scope key still separates claims."""
    self.pipeline("related")
    a, b = self.two_sources(
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
        "extra": {"scope": {"environment": "prod"}},
      },
    )
    _, out, _ = self.kc("candidates")
    row = next(p for p in out["pairs"] if set(p["claims"]) == {a, b})
    self.assertEqual(row["signals"], ["same-key-different-scope"])

  def test_claims_warns_on_provenance_scope_and_near_subject(self):
    """Dry run warns on a provenance scope key and on a near match of an existing subject; nothing is refused (P1, P12)."""
    self.pipeline("related")
    self.two_sources(COORD_A, COORD_B)
    path = self.add_doc("third.md", ["# Doc", "", "The coordinators run Go."])
    code, out, err = self.ingest(
      [make_claim(path, 3, "The coordinators run Go.", "continuum coordinators", "uses frameworks", "Go", "x.y", scope={"source": "third"})]
    )
    self.assertEqual(code, 0, err)
    self.assertTrue(any("'source'" in w for w in out["warnings"]))
    self.assertTrue(any("continuum coordinator" in w for w in out["warnings"]))

  def test_vocabulary_lists_terms_and_worksheet_serves_it(self):
    """Kc vocabulary counts terms; each worksheet batch carries the most used ones (P1)."""
    self.pipeline("related")
    self.two_sources(COORD_A, COORD_B)
    _, voc, _ = self.kc("vocabulary")
    self.assertEqual(voc["subjects"]["continuum coordinator"], 2)
    self.assertIn("system.coordinator", voc["topic_keys"])
    self.add_doc("pending.md", ["# Pending", "", "Some text to extract."])
    _, ws, _ = self.kc("worksheet")
    self.assertIn("continuum coordinator", ws["vocabulary"]["subjects"])


class RankingTest(FixCase, unittest.TestCase):
  """P2, P13: review works on cross-source units first."""

  def test_same_source_enumeration_suppressed_and_counted(self):
    """Parallel rows in one source with different subjects are not pairs; counts report the split (P2)."""
    self.pipeline("related")
    path = self.add_doc("phases.md", ["# Phases", "", "Phase P6 takes 5 to 9 weeks of work.", "", "Phase P8 takes 3 to 4 weeks of work."])
    self.ingest(
      [
        make_claim(path, 3, "Phase P6 takes 5 to 9 weeks of work.", "phase p6", "takes", "5 to 9 weeks", "phases.one"),
        make_claim(path, 5, "Phase P8 takes 3 to 4 weeks of work.", "phase p8", "takes", "3 to 4 weeks", "phases.two"),
      ],
      "--apply",
    )
    _, out, _ = self.kc("candidates")
    self.assertFalse(
      any("phase P6" in " ".join(p["texts"]).replace("Phase", "phase") and "phase P8" in " ".join(p["texts"]).replace("Phase", "phase") for p in out["pairs"])
    )
    self.assertGreaterEqual(out["counts"]["suppressed_same_source"], 1)
    self.assertEqual(out["counts"]["cross_source"] + out["counts"]["same_source"], len(out["pairs"]))

  def test_cross_source_ranked_first(self):
    """A cross-source pair with a signal outranks a same-source pair with one (P2)."""
    self.pipeline("related")
    self.two_sources(COORD_A, COORD_B)
    _, out, _ = self.kc("candidates")
    flags = [p["cross_source"] for p in out["pairs"] if p["signals"]]
    self.assertEqual(flags, sorted(flags, reverse=True))

  def test_decision_points_group_sources(self):
    """Claims on one key from two sources with differing objects form one group, which disappears when classified (P13)."""
    self.pipeline("related")
    a, b = self.two_sources(
      {"text": "The gateway is Caddy.", "subject": "gateway", "predicate": "is", "object": "Caddy", "topic": "gateway.main"},
      {"text": "The gateway is Traefik.", "subject": "gateway", "predicate": "is", "object": "Traefik", "topic": "gateway.main"},
    )
    _, out, _ = self.kc("decision-points")
    group = next(g for g in out["groups"] if g["subject"] == "gateway")
    self.assertEqual({c["claim_id"] for c in group["claims"]}, {a, b})
    self.assertEqual(group["sources"], 2)
    self.assertEqual(group["unclassified_pairs"], 1)
    self.conflict(a, b)
    _, after, _ = self.kc("decision-points")
    self.assertFalse(any(g["subject"] == "gateway" for g in after["groups"]))


if __name__ == "__main__":
  unittest.main()
