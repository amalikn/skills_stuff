"""citation_audit: every cited id is checked against the ledger; superseded claims shown as current are flagged; moved excerpts fail.

Run: python -m unittest discover -s tests (or `just test`). Safety: files only, under a temporary folder.
"""

import contextlib
import importlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import helpers

citation_audit = importlib.import_module("citation_audit")

OK = "cl-aaaaaaaaaaaa"
OLD = "cl-bbbbbbbbbbbb"
MISSING = "cl-cccccccccccc"


def claim(cid: str, text: str, excerpt: str, line: int) -> dict:
  """Build one claim record with one evidence excerpt.

  Args:
    cid: claim id.
    text: claim text.
    excerpt: evidence excerpt.
    line: source line of the excerpt.

  Returns:
    The record.
  """
  return {
    "record": "claim",
    "claim_id": cid,
    "claim_text": text,
    "evidence": [{"path": "docs/src.md", "line_start": line, "line_end": line, "excerpt": excerpt}],
  }


class CitationAuditTest(unittest.TestCase):
  """Audit, excerpt check and review over a two-claim ledger."""

  def setUp(self):
    """Write a project with a source, a ledger and one page."""
    self.assertTrue(helpers.SCRIPTS.is_dir())
    tmp = tempfile.TemporaryDirectory()
    self.addCleanup(tmp.cleanup)
    self.root = Path(tmp.name)
    (self.root / "docs").mkdir()
    (self.root / "docs/src.md").write_text("Handoff fences the source before activation.\nThe old journal is used first.\n")
    records = [
      claim(OK, "Handoff fences the source before activation.", "Handoff fences the source before activation.", 1),
      claim(OLD, "Workflow engine uses a journal first.", "The old journal is used first.", 2),
      {"record": "disposition", "claim_id": OLD, "disposition": "SUPERSEDED", "successor": OK},
    ]
    (self.root / ".kc").mkdir()
    (self.root / ".kc/claims.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))
    (self.root / "page.md").write_text(
      f"The handoff fences the source before activation [{OK}].\nThe engine uses a journal first [{OLD}].\nUnknown [{MISSING}].\n"
      f"Historical: the journal was superseded [{OLD}].\n"
    )
    self.rows = self.root / "rows.json"

  def verdicts(self) -> list[str]:
    """Run the audit and return the verdicts in page order.

    Args:
      None.

    Returns:
      Verdict strings.
    """
    self.assertEqual(citation_audit.main(["audit", "--root", str(self.root), "--out", str(self.rows), "page.md"]), 0)
    return [r["verdict"] for r in json.loads(self.rows.read_text())]

  def test_verdicts(self):
    """Supported, superseded-as-current, wrong id, and a superseded claim marked historical."""
    self.assertEqual(self.verdicts(), ["SUPPORTED-BY-SCRIPT", "SUPERSEDED-CANDIDATE", "WRONG-ID", "REVIEW"])

  def test_excerpts_pass_then_fail_when_source_moves(self):
    """A source edit that moves an excerpt off its lines makes `excerpts` exit 1."""
    self.verdicts()
    self.assertEqual(citation_audit.main(["excerpts", "--root", str(self.root), "--rows", str(self.rows)]), 0)
    (self.root / "docs/src.md").write_text("\n\n\nHandoff fences the source before activation.\nThe old journal is used first.\n")
    self.assertEqual(citation_audit.main(["excerpts", "--root", str(self.root), "--rows", str(self.rows)]), 1)

  def test_review_prints_flagged_rows_only(self):
    """Review lists the flagged rows, not the supported one."""
    self.verdicts()
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
      citation_audit.main(["review", "--rows", str(self.rows)])
    out = buf.getvalue()
    self.assertIn(OLD, out)
    self.assertIn(MISSING, out)
    self.assertNotIn(f"{OK} SUPPORTED", out)


if __name__ == "__main__":
  unittest.main()
