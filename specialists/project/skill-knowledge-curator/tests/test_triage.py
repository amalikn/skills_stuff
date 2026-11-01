"""Noise triage: the status map, named gates, reversibility and sampling (research B0-B2, evaluation.md P33).

Each test failed before its feature existed.

Run: python -m unittest discover -s tests (or `just test`). Safety: files only, under temporary copies.
"""

import json
import unittest

from helpers import FixCase, make_claim


class TriageCase(FixCase):
  """Two ordered reports with helpers for claims and conflicts."""

  def docs(self, old: list[str], new: list[str]) -> tuple[str, str]:
    """Write an earlier and a later report.

    Args:
      old: lines of step1.md.
      new: lines of step2.md.

    Returns:
      Their paths.
    """
    return self.add_doc("step1.md", old), self.add_doc("step2.md", new)

  def pair(self, left: tuple, right: tuple, severity: str = "P2") -> tuple[str, str, str]:
    """Ingest two claims and open a conflict.

    Args:
      left: make_claim arguments.
      right: make_claim arguments.
      severity: conflict severity.

    Returns:
      (claim a, claim b, conflict ID).
    """
    self.ingest([make_claim(*left), make_claim(*right)], "--apply")
    a, b = self.claim_for(left[2]), self.claim_for(right[2])
    return a, b, self.conflict(a, b, severity)

  def run_triage(self, *flags: str) -> dict:
    """Run kc triage.

    Args:
      *flags: extra options.

    Returns:
      Its output.
    """
    code, out, err = self.kc("triage", *flags)
    self.assertEqual(code, 0, err)
    return out

  def row(self, out: dict, conflict: str) -> dict:
    """One conflict's triage row.

    Args:
      out: triage output.
      conflict: conflict ID.

    Returns:
      The row.
    """
    return next(r for r in out["rows"] if r["conflict_id"] == conflict)


class StatusMapTest(TriageCase, unittest.TestCase):
  """What each document says about itself, with the line that proves it."""

  def test_banner_status_and_order(self):
    """A banner gives status and line; a plain file is unknown, never current."""
    self.pipeline("inventoried")
    self.docs(["# Old", "SUPERSEDED by step2.md", "", "Body."], ["# New", "", "Body."])
    files = self.kc("status-map")[1]["files"]
    self.assertEqual(files["docs/step1.md"]["status"], "superseded")
    self.assertEqual(files["docs/step1.md"]["line"], 2)
    self.assertEqual(files["docs/step1.md"]["order"], 1)
    self.assertIn("docs/step2.md", files["docs/step1.md"]["replaced_by"])
    self.assertEqual(files["docs/step2.md"]["status"], "unknown")

  def test_later_mention_is_not_a_banner(self):
    """The word deep in a body sets no status."""
    self.pipeline("inventoried")
    self.add_doc("deep.md", ["# Doc"] + ["Line."] * 20 + ["This was superseded once."])
    self.assertEqual(self.kc("status-map")[1]["files"]["docs/deep.md"]["status"], "unknown")


class GateTest(TriageCase, unittest.TestCase):
  """Named gates: noise needs proof, and everything else goes to a person."""

  def test_superseded_value_replaced_later_is_noise(self):
    """A labelled old value with a later statement on the subject clears, citing the banner line."""
    self.pipeline("related")
    p1, p2 = self.docs(["# Old", "SUPERSEDED by step2.md", "", "The cache size is 10."], ["# New", "", "The cache size is 20."])
    _, _, cf = self.pair((p1, 4, "The cache size is 10.", "cache size", "is", "10", "c.s"), (p2, 3, "The cache size is 20.", "cache size", "is", "20", "c.s"))
    row = self.row(self.run_triage(), cf)
    self.assertEqual(row["outcome"], "noise")
    self.assertEqual(row["rule"], "superseded-section")
    self.assertIn("docs/step1.md:2", row["signals"][0])

  def test_still_current_value_under_a_banner_goes_to_a_person(self):
    """Banner over a value no later source replaces: not cleared (operator, 2026-11-01)."""
    self.pipeline("related")
    p1 = self.add_doc("step1.md", ["# Old", "SUPERSEDED by step2.md", "", "The cache size is 10.", "", "The queue size is 30."])
    self.add_doc("step2.md", ["# New", "", "Nothing about that."])
    _, _, cf = self.pair((p1, 4, "The cache size is 10.", "cache size", "is", "10", "c.s"), (p1, 6, "The queue size is 30.", "queue size", "is", "30", "q.s"))
    self.assertEqual(self.row(self.run_triage(), cf)["outcome"], "needs_human")

  def test_disjoint_scope_is_noise(self):
    """Claims in different situations clear."""
    self.pipeline("related")
    p1, p2 = self.docs(["# A", "", "Lab uses Caddy."], ["# B", "", "Prod uses Traefik."])
    left = (p1, 3, "Lab uses Caddy.", "gateway", "is", "Caddy", "g.g")
    right = (p2, 3, "Prod uses Traefik.", "gateway", "is", "Traefik", "g.g")
    self.ingest([make_claim(*left, scope={"environment": "lab"}), make_claim(*right, scope={"environment": "prod"})], "--apply")
    cf = self.conflict(self.claim_for(left[2]), self.claim_for(right[2]))
    self.assertEqual(self.row(self.run_triage(), cf)["rule"], "disjoint-scope")

  def test_same_identifier_opposite_status_never_clears(self):
    """One path called retired and active stays with a person, even under a banner."""
    self.pipeline("related")
    path = "/data/mcp-root"
    p1, p2 = self.docs(["# Old", "SUPERSEDED by step2.md", "", f"{path} is retired."], ["# New", "", f"{path} is the active root."])
    _, _, cf = self.pair((p1, 4, f"{path} is retired.", "root", "is", "retired", "r.r"), (p2, 3, f"{path} is the active root.", "root", "is", "active", "r.r"))
    row = self.row(self.run_triage(), cf)
    self.assertEqual(row["outcome"], "needs_human")
    self.assertEqual(row["guard"], "same-identifier-opposite-status")

  def test_p0_never_clears(self):
    """P0 stays open whatever the gates say."""
    self.pipeline("related")
    p1, p2 = self.docs(["# Old", "SUPERSEDED by step2.md", "", "The cache size is 10."], ["# New", "", "The cache size is 20."])
    _, _, cf = self.pair(
      (p1, 4, "The cache size is 10.", "cache size", "is", "10", "c.s"), (p2, 3, "The cache size is 20.", "cache size", "is", "20", "c.s"), "P0"
    )
    self.assertEqual(self.row(self.run_triage(), cf)["outcome"], "needs_human")

  def test_dated_order_proposal_stays_proposed(self):
    """A dated-order conflict is a proposal for one-word confirmation."""
    self.pipeline("related")
    p1, p2 = self.docs(["# A", "", "Mode is one."], ["# B", "", "Mode is two."])
    self.ingest([make_claim(p1, 3, "Mode is one.", "mode", "is", "one", "m.m"), make_claim(p2, 3, "Mode is two.", "mode", "is", "two", "m.m")], "--apply")
    a, b = self.claim_for("Mode is one."), self.claim_for("Mode is two.")
    path = self.root.parent / "rel.json"
    path.write_text(
      json.dumps(
        [
          {
            "record": "relation",
            "claims": [a, b],
            "relation": "time-evolution",
            "basis": "dated-order",
            "reason": "ordered steps",
            "superseded": a,
            "successor": b,
          }
        ]
      )
    )
    self.kc("relate", "--file", str(path), "--apply")
    out = self.run_triage()
    self.assertTrue(any(r["outcome"] == "proposed" for r in out["rows"]))


class GuardTest(TriageCase, unittest.TestCase):
  """Gates must not hide a real conflict: tuned on the seeded sample, where they first cleared 7 of 11 real ones."""

  def test_gone_path_with_live_child_never_clears(self):
    """A path called retired against something still living under it stays with a person."""
    self.pipeline("related")
    p1, p2 = self.docs(
      ["# Old", "SUPERSEDED by step2.md", "", "The /data/mcp-root path is retired."], ["# New", "", "Links under mcp-root/voicemode stay in use."]
    )
    _, _, cf = self.pair(
      (p1, 4, "The /data/mcp-root path is retired.", "root", "is", "retired", "r.r"),
      (p2, 3, "Links under mcp-root/voicemode stay in use.", "links", "stay", "in use", "r.r"),
    )
    self.assertEqual(self.row(self.run_triage(), cf)["guard"], "same-identifier-opposite-status")

  def test_two_body_lines_in_one_labelled_file_do_not_clear(self):
    """A banner does not explain two body lines disagreeing with each other."""
    self.pipeline("related")
    p1 = self.add_doc("step1.md", ["# Old", "SUPERSEDED by step2.md", "", "The cache size is 10.", "", "The cache size is 12."])
    self.add_doc("step2.md", ["# New", "", "The cache size is 20."])
    self.ingest([make_claim("docs/step2.md", 3, "The cache size is 20.", "cache size", "is", "20", "c.s")], "--apply")
    _, _, cf = self.pair((p1, 4, "The cache size is 10.", "cache size", "is", "10", "c.s"), (p1, 6, "The cache size is 12.", "cache size", "is", "12", "c.s"))
    self.assertEqual(self.row(self.run_triage(), cf)["outcome"], "needs_human")

  def test_self_label_under_a_banner_clears(self):
    """A body line calling the file authoritative, under a superseded banner, is what the banner explains."""
    self.pipeline("related")
    p1 = self.add_doc("step1.md", ["# Old", "SUPERSEDED by step2.md", "", "This report is CURRENT AUTHORITATIVE.", "", "This report is superseded by step2."])
    self.add_doc("step2.md", ["# New", "", "This report is the current one."])
    self.ingest([make_claim("docs/step2.md", 3, "This report is the current one.", "report status", "is", "current", "r.s")], "--apply")
    _, _, cf = self.pair(
      (p1, 4, "This report is CURRENT AUTHORITATIVE.", "report status", "is", "authoritative", "r.s"),
      (p1, 6, "This report is superseded by step2.", "report status", "is", "superseded", "r.s"),
    )
    self.assertEqual(self.row(self.run_triage(), cf)["rule"], "superseded-section")

  def test_plan_against_state_clears_at_p2(self):
    """An optional future item against a statement of today clears at P2 and stays proposed at P1."""
    self.pipeline("related")
    p1, p2 = self.docs(["# A", "", "Only the shim work is left open."], ["# B", "", "Optional future hardening: add a compliance check."])
    _, _, cf = self.pair(
      (p1, 3, "Only the shim work is left open.", "open work", "is", "shim", "o.w"),
      (p2, 3, "Optional future hardening: add a compliance check.", "hardening", "may", "check", "h.h"),
    )
    self.assertEqual(self.row(self.run_triage(), cf)["rule"], "plan-vs-state")


class ApplyTest(TriageCase, unittest.TestCase):
  """Dismissal is append-only, reversible and honest in recall."""

  def cleared(self) -> tuple[str, str, str]:
    """A conflict that clears.

    Returns:
      (claim a, claim b, conflict ID).
    """
    self.pipeline("related")
    p1, p2 = self.docs(["# Old", "SUPERSEDED by step2.md", "", "The cache size is 10."], ["# New", "", "The cache size is 20."])
    return self.pair((p1, 4, "The cache size is 10.", "cache size", "is", "10", "c.s"), (p2, 3, "The cache size is 20.", "cache size", "is", "20", "c.s"))

  def test_dry_run_writes_nothing_and_apply_can_be_undone(self):
    """Dry run leaves it open; apply dismisses with rule and run; undo reopens; claims never change."""
    _, _, cf = self.cleared()
    claims = (self.root / ".kc" / "claims.jsonl").read_bytes()
    run = self.run_triage()["run_id"]
    self.assertEqual(self.state().conflicts[cf]["status"], "open")
    run = self.run_triage("--apply")["run_id"]
    st = self.state()
    self.assertEqual(st.conflicts[cf]["status"], "dismissed")
    self.assertEqual(st.conflicts[cf]["triage"]["rule"], "superseded-section")
    self.assertNotIn(cf, [c["conflict_id"] for c in st.open_conflicts()])
    self.assertEqual((self.root / ".kc" / "claims.jsonl").read_bytes(), claims)
    self.assertGreaterEqual(self.kc("report")[1]["conflicts"]["dismissed"], 1)
    self.run_triage("--undo", run, "--apply")
    self.assertEqual(self.state().conflicts[cf]["status"], "open")

  def test_dismissed_pair_does_not_count_as_reached(self):
    """A label whose pair was dismissed no longer reaches review."""
    self.cleared()
    self.run_triage("--apply")
    side = {"line": 4, "quote": "x"}
    other = {"line": 3, "quote": "x"}
    gold = [{"id": "G1", "kind": "cross-file", "severity": "P2", "a": {"path": "docs/step1.md", **side}, "b": {"path": "docs/step2.md", **other}}]
    path = self.root.parent / "gold.json"
    path.write_text(json.dumps(gold))
    self.assertEqual(self.kc("recall", "--labels", str(path))[1]["labels"][0]["status"], "dismissed")


class SampleTest(TriageCase, unittest.TestCase):
  """kc sample: seeded cards and Wilson intervals."""

  def test_wilson_interval_matches_the_published_figure(self):
    """11 of 40 gives 16.1 to 42.8 percent."""
    self.pipeline("related")
    path = self.root.parent / "verdicts.json"
    path.write_text(json.dumps([{"conflict_id": f"c{n}", "verdict": "real" if n < 11 else "noise", "reason": "r"} for n in range(40)]))
    out = self.kc("sample", "--score", str(path))[1]
    self.assertEqual(out["precision"], 0.275)
    self.assertEqual(out["interval"], [0.161, 0.428])

  def test_seeded_cards_are_repeatable_and_exclude_listed(self):
    """A seed gives the same cards; --exclude keeps a used sample out; status picks dismissed ones."""
    self.pipeline("related")
    one, two = self.kc("sample", "--size", "1", "--seed", "3")[1], self.kc("sample", "--size", "1", "--seed", "3")[1]
    self.assertEqual(one["cards"], two["cards"])
    path = self.root.parent / "used.json"
    path.write_text(json.dumps([{"conflict_id": c["conflict_id"]} for c in self.kc("sample", "--size", "9")[1]["cards"]]))
    self.assertEqual(self.kc("sample", "--exclude", str(path))[1]["cards"], [])


if __name__ == "__main__":
  unittest.main()
