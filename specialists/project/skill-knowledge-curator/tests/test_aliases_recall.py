"""Consolidation aliases and the recall harness (references/evaluation.md P28).

Each test failed before its feature existed.

Run: python -m unittest discover -s tests (or `just test`). Safety: files only, under temporary copies.
"""

import json
import unittest

from helpers import FixCase, make_claim

A = {"text": "The shims are retained.", "subject": "voicemode shims", "predicate": "status", "object": "retained", "topic": "voicemode.step8"}
B = {"text": "The links are retired.", "subject": "compat links", "predicate": "ended as", "object": "retired", "topic": "final.links"}


def alias(field: str, term: str, canonical: str, **extra) -> dict:
  """Build one alias input.

  Args:
    field: subject, predicate or topic_key.
    term: the term.
    canonical: its canonical form.
    **extra: other fields.

  Returns:
    The input.
  """
  return {"record": "alias", "field": field, "term": term, "canonical": canonical, "reason": "same thing", **extra}


class AliasCase(FixCase):
  """Helpers for alias files."""

  def aliases(self, records: list[dict], *flags: str) -> tuple[int, dict, str]:
    """Run kc aliases.

    Args:
      records: alias inputs.
      *flags: extra options.

    Returns:
      The kc result.
    """
    path = self.root.parent / "aliases.json"
    path.write_text(json.dumps(records))
    return self.kc("aliases", "--file", str(path), *flags)


class AliasTest(AliasCase, unittest.TestCase):
  """Aliases change comparison only, never claims."""

  def merged(self) -> tuple[str, str]:
    """Two claims with different wording, then aliases joining them.

    Returns:
      Both claim IDs.
    """
    self.pipeline("related")
    a, b = self.two_sources(A, B)
    recs = [alias("subject", "compat links", "voicemode shims"), alias("predicate", "ended as", "status"), alias("topic_key", "final.links", "voicemode.step8")]
    code, _, err = self.aliases(recs, "--apply")
    self.assertEqual(code, 0, err)
    return a, b

  def test_merged_terms_form_a_key_group_and_pair(self):
    """After aliasing, the two claims share a key: one key group, and a same-key candidate pair."""
    a, b = self.merged()
    groups = self.kc("decision-points")[1]["groups"]
    self.assertTrue(any({c["claim_id"] for c in g["claims"]} == {a, b} for g in groups))
    row = next(p for p in self.kc("candidates")[1]["pairs"] if set(p["claims"]) == {a, b})
    self.assertIn("same-key-different-object", row["signals"])

  def test_claims_untouched_and_dry_run_writes_nothing(self):
    """Dry run changes nothing; apply leaves the claims ledger byte-identical."""
    self.pipeline("related")
    self.two_sources(A, B)
    before = (self.root / ".kc" / "claims.jsonl").read_bytes()
    self.assertEqual(self.aliases([alias("subject", "compat links", "voicemode shims")])[0], 0)
    self.assertFalse((self.root / ".kc" / "aliases.jsonl").exists())
    self.aliases([alias("subject", "compat links", "voicemode shims")], "--apply")
    self.assertEqual((self.root / ".kc" / "claims.jsonl").read_bytes(), before)

  def test_revoke_undoes_a_merge(self):
    """A revoked alias stops applying."""
    a, b = self.merged()
    self.aliases([alias("subject", "compat links", "voicemode shims", revoked=True)], "--apply")
    groups = self.kc("decision-points")[1]["groups"]
    self.assertFalse(any({c["claim_id"] for c in g["claims"]} == {a, b} for g in groups))

  def test_refusals(self):
    """A self alias, a chain and an unknown term are refused whole (exit 1)."""
    self.pipeline("related")
    self.two_sources(A, B)
    self.assertEqual(self.aliases([alias("subject", "compat links", "compat links")])[0], 1)
    self.assertEqual(self.aliases([alias("subject", "no such subject", "voicemode shims")])[0], 1)
    chain = [alias("subject", "compat links", "voicemode shims"), alias("subject", "voicemode shims", "shims")]
    self.assertEqual(self.aliases(chain)[0], 1)


class RecallTest(AliasCase, unittest.TestCase):
  """kc recall scores a labelled set against what reaches review."""

  def labels(self, rows: list[dict]) -> str:
    """Write a labels file.

    Args:
      rows: gold conflicts.

    Returns:
      Its path.
    """
    path = self.root.parent / "gold.json"
    path.write_text(json.dumps(rows))
    return str(path)

  def gold(self, gid: str, severity: str, b_path: str = "docs/right.md") -> dict:
    """One gold conflict between the two test documents.

    Args:
      gid: label ID.
      severity: severity.
      b_path: second side's path.

    Returns:
      The label.
    """
    side = {"line": 3, "quote": "x"}
    return {
      "id": gid,
      "kind": "cross-file",
      "severity": severity,
      "topic": "t",
      "a": {"path": "docs/left.md", **side},
      "b": {"path": b_path, **side},
      "why": "w",
      "confidence": "high",
    }

  def test_reached_and_missed(self):
    """A pair in a group counts as reached; without one it is missed; an unextracted side is reported apart."""
    self.pipeline("related")
    self.two_sources(A, B)
    path = self.add_doc("other.md", ["# Doc", "", "Nothing alike at all."])
    self.ingest([make_claim(path, 3, "Nothing alike at all.", "zzz", "qqq", "yyy", "t.t")], "--apply")
    rows = [self.gold("G1", "P2"), self.gold("G2", "P1", "docs/other.md"), self.gold("G3", "P2", "docs/absent.md")]
    code, out, err = self.kc("recall", "--labels", self.labels(rows))
    self.assertEqual(code, 0, err)
    by = {r["id"]: r["status"] for r in out["labels"]}
    self.assertEqual(by, {"G1": "missed", "G2": "missed", "G3": "not_extracted"})
    self.assertEqual(out["summary"]["total"], 3)
    self.assertFalse(out["summary"]["gate_pass"])
    self.aliases([alias("subject", "compat links", "voicemode shims"), alias("predicate", "ended as", "status")], "--apply")
    self.assertEqual({r["id"]: r["status"] for r in self.kc("recall", "--labels", self.labels(rows))[1]["labels"]}["G1"], "reached")

  def test_bad_labels_refused(self):
    """A label file that breaks the schema exits 1."""
    self.pipeline("related")
    self.assertEqual(self.kc("recall", "--labels", self.labels([{"id": "G1"}]))[0], 1)


if __name__ == "__main__":
  unittest.main()
