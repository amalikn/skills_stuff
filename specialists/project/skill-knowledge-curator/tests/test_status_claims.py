"""status_claims: Status-line and banner claims, and the status-line-vs-banner conflict (UNC pilot, 2026-11-05).

Run: python -m unittest discover -s tests (or `just test`). Safety: files only, under temporary copies.
"""

import importlib
import json
import unittest

from helpers import FixCase

TOOL = importlib.import_module("status_claims")


class StatusClaimsTest(FixCase, unittest.TestCase):
  """What a document says about itself, made comparable."""

  def ingest_file(self, records: list[dict], command: str) -> dict:
    """Run kc claims or relate on records with --apply.

    Args:
      records: input records.
      command: "claims" or "relate".

    Returns:
      The kc output.
    """
    path = self.root.parent / f"{command}.json"
    path.write_text(json.dumps(records))
    code, out, err = self.kc(command, "--file", str(path), "--apply")
    self.assertEqual(code, 0, err)
    return out

  def test_current_status_under_a_banner_conflicts(self):
    """A current-like Status line under a superseded banner becomes two claims and one P2 conflict; a plain file gives one claim, no conflict."""
    self.pipeline("inventoried")
    self.add_doc(
      "old-plan.md", ["---", "Title: Old plan", "Status: adoption-ready", "---", "", "> **SUPERSEDED 2026-09-26.** Kept as history only.", "", "Body."]
    )
    self.add_doc("new-plan.md", ["---", "Title: New plan", "Status: current", "---", "", "Body."])
    st = self.state()
    recs = TOOL.claims(TOOL.scan(st))
    mine = {(r["evidence"][0]["source_path"], r["predicate"]) for r in recs}
    self.assertIn(("docs/old-plan.md", "declares status"), mine)
    self.assertIn(("docs/old-plan.md", "banner says"), mine)
    self.assertNotIn(("docs/new-plan.md", "banner says"), mine)
    self.ingest_file(recs, "claims")
    rels = TOOL.relations(self.state(), TOOL.scan(self.state()))
    self.assertEqual(len(rels), 1)
    self.assertEqual((rels[0]["severity"], rels[0]["conflict_type"]), ("P2", "status-line-vs-banner"))
    self.ingest_file(rels, "relate")
    self.assertTrue(any(c["conflict_type"] == "status-line-vs-banner" for c in self.state().open_conflicts()))

  def test_mentions_and_partial_supersession_are_not_banners(self):
    """A list item naming superseded files, a line about other files, and 'superseded in part' are not whole-file banners."""
    self.pipeline("inventoried")
    self.add_doc(
      "index.md",
      [
        "---",
        "Status: current",
        "---",
        "",
        "- [archive/](archive/readme.md) Superseded documents kept as history.",
        "Adopted 2026-09-26; superseded revisions live in archive/.",
      ],
    )
    self.add_doc("part.md", ["---", "Status: current", "---", "", "**Superseded in part 2026-09-28.** One section changed."])
    found = {f["path"]: f["banner"] for f in TOOL.scan(self.state())}
    self.assertIsNone(found["docs/index.md"])
    self.assertIsNone(found["docs/part.md"])


if __name__ == "__main__":
  unittest.main()
