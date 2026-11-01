"""restate_byte_copies: claims and context carried onto byte-identical files, so copies need no extraction (MCP pilot, 2026-11-01).

Run: python -m unittest discover -s tests (or `just test`). Safety: files only, under temporary copies.
"""

import importlib
import json
import unittest

from helpers import FixCase, make_claim

TOOL = importlib.import_module("restate_byte_copies")


class RestateTest(FixCase, unittest.TestCase):
  """The input a copy needs, from what its original holds."""

  def test_claim_reaches_the_copy_as_one_source(self):
    """A claim on one byte copy gains evidence on the other; the pair stays one independent source and its sections close."""
    self.pipeline("inventoried")
    text = (self.root / "docs" / "ops-runbook.md").read_text().splitlines()
    line = next(n for n, row in enumerate(text, 1) if row.strip() and not row.startswith(("#", "Status")))
    self.ingest([make_claim("docs/ops-runbook.md", line, text[line - 1].strip(), "runbook", "says", "x", "ops.run")], "--apply")
    records = TOOL.build(self.state())
    self.assertTrue(records)
    path = self.root.parent / "copies.json"
    path.write_text(json.dumps(records))
    code, _, err = self.kc("claims", "--file", str(path), "--apply")
    self.assertEqual(code, 0, err)
    claim = next(c for c in self.state().claims.values() if c["subject"] == "runbook")
    self.assertEqual({e["path"] for e in claim["evidence"]}, {"docs/ops-runbook.md", "docs/ops-runbook-copy.md"})
    self.assertEqual(claim["independent_sources"], 1)

  def test_no_copies_means_no_records(self):
    """A project with nothing cited on a copy needs no records."""
    self.pipeline("related")
    self.assertEqual([r for r in TOOL.build(self.state()) if r["record"] == "claim"], [])


if __name__ == "__main__":
  unittest.main()
