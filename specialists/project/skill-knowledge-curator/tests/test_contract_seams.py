"""Contract and seam tests: vocabularies match the schemas, and each third-party seam behaves as the code relies on.

Run: python -m unittest discover -s tests (or `just test`). Safety: no writes outside temporary folders.
"""

import unittest

from jsonschema import Draft202012Validator

from helpers import lib


class ContractTest(unittest.TestCase):
  """settings vocabularies equal the JSON schema enums (drift check)."""

  def test_enums_match_schemas(self):
    """Each vocabulary in settings equals the enum the schemas enforce."""
    settings, schema = lib("settings"), lib("schema")
    claim = schema.load("claim-input")["properties"]
    self.assertEqual(tuple(claim["primary_category"]["enum"]), settings.CATEGORIES)
    self.assertEqual(tuple(claim["kind"]["enum"]), settings.KINDS)
    self.assertEqual(tuple(claim["epistemic_status"]["enum"]), settings.EPISTEMIC)
    self.assertEqual(tuple(claim["disposition"]["enum"]), settings.DISPOSITIONS)
    rel = schema.load("relation-input")["properties"]
    self.assertEqual(tuple(rel["relation"]["enum"]), settings.RELATIONS)
    self.assertEqual(tuple(rel["severity"]["enum"]), settings.SEVERITIES)
    sec = schema.load("section-status-input")["properties"]
    self.assertEqual(tuple(sec["status"]["enum"]), settings.SECTION_STATUSES)

  def test_schemas_are_valid_draft_2020_12(self):
    """Every schema file is itself a valid Draft 2020-12 schema."""
    for name in ("claim-input", "relation-input", "section-status-input", "intake-payload"):
      Draft202012Validator.check_schema(lib("schema").load(name))

  def test_unknown_record_type_rejected(self):
    """An input without a known record type is a violation, not guessed into a record."""
    self.assertTrue(lib("schema").record_errors({"record": "fact"}))

  def test_conflict_relation_requires_severity_and_question(self):
    """A true-conflict without severity or question fails the schema."""
    errs = lib("schema").record_errors(
      {"record": "relation", "claims": ["cl-" + "a" * 12, "cl-" + "b" * 12], "relation": "true-conflict", "reason": "they disagree"}
    )
    self.assertTrue(any("severity" in e for e in errs))

  def test_supersession_needs_evidence(self):
    """time-evolution without supersession_evidence fails the schema (T04)."""
    rel = {
      "record": "relation",
      "claims": ["cl-" + "1" * 12, "cl-" + "2" * 12],
      "relation": "time-evolution",
      "reason": "newer",
      "superseded": "a",
      "successor": "b",
    }
    self.assertTrue(any("supersession_evidence" in e for e in lib("schema").record_errors(rel)))


class SeamTest(unittest.TestCase):
  """Upgrade tests for markdown-it-py, PyYAML and RapidFuzz."""

  def test_mdparse_line_spans_and_front_matter(self):
    """Front matter is cut first; blocks carry 1-based spans and heading paths; tables and fences are blocks."""
    text = "---\nTitle: x\n---\n# A\n\npara\n\n## B\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\n```\ncode\n```\n"
    blocks = lib("mdparse").parse_blocks(text)
    kinds = [(b.kind, b.line_start, b.line_end, b.heading_path) for b in blocks]
    self.assertEqual(kinds[0], ("front_matter", 1, 3, ()))
    self.assertIn(("paragraph", 6, 6, ("A",)), kinds)
    self.assertIn(("table", 10, 12, ("A", "B")), kinds)
    self.assertIn(("code", 14, 16, ("A", "B")), kinds)

  def test_declared_status(self):
    """A Status line near the top or in front matter is read; none gives None."""
    md = lib("mdparse")
    self.assertEqual(md.declared_status("Status: CURRENT AUTHORITATIVE\n\n# x\n"), "CURRENT AUTHORITATIVE")
    self.assertEqual(md.declared_status("---\nStatus: proposed\n---\n"), "proposed")
    self.assertIsNone(md.declared_status("# x\n\ntext\n"))

  def test_yaml_safe_load_refuses_python_tags(self):
    """safe_load refuses a Python object tag instead of constructing it."""
    with self.assertRaises(lib("errors").InputError):
      lib("yaml_io").load("!!python/name:builtins.print")

  def test_fuzzy_order_insensitive(self):
    """token_set_ratio ignores word order."""
    self.assertEqual(lib("fuzzy").similarity("backups run nightly", "nightly backups run"), 100.0)


if __name__ == "__main__":
  unittest.main()
