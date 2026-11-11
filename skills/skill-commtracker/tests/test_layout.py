"""Offline tests for the standard communications/ layout: extract.py's default attachments folder and reconcile.py's .eml discovery, in both layouts.

Run: python3 -m unittest discover -s tests
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def _load(name: str):
  """Load a script as a module without running its CLI.

  Args:
    name: Script file stem in scripts/.

  Returns:
    The loaded module.
  """
  spec = importlib.util.spec_from_file_location(f"commtracker_{name}", SCRIPTS / f"{name}.py")
  mod = importlib.util.module_from_spec(spec)
  sys.modules[spec.name] = mod
  spec.loader.exec_module(mod)
  return mod


ex = _load("extract")
rc = _load("reconcile")

EML = (
  "From: A Sender <a@example.com>\nTo: B Person <b@example.com>\nSubject: Test\n"
  "Date: Sun, 11 Oct 2026 23:01:00 +0000\nContent-Type: multipart/mixed; boundary=XX\n\n"
  "--XX\nContent-Type: text/plain; charset=utf-8\n\nHello.\n"
  "--XX\nContent-Type: application/pdf; name=\"doc.pdf\"\nContent-Disposition: attachment; filename=\"doc.pdf\"\n"
  "Content-Transfer-Encoding: base64\n\nJVBERi0xLjQKJSVFT0YK\n--XX--\n"
)


class DefaultAttachmentsDirTest(unittest.TestCase):
  """default_attachments_dir() and extract() placement."""

  def test_emails_subfolder_goes_up(self):
    self.assertEqual(ex.default_attachments_dir(Path("/c/emails/m.eml")), Path("/c/attachments"))

  def test_teams_subfolder_goes_up(self):
    self.assertEqual(ex.default_attachments_dir(Path("/c/teams/m.eml")), Path("/c/attachments"))

  def test_flat_layout_unchanged(self):
    self.assertEqual(ex.default_attachments_dir(Path("/c/m.eml")), Path("/c/attachments"))

  def test_other_subfolder_not_promoted(self):
    self.assertEqual(ex.default_attachments_dir(Path("/c/vendor/m.eml")), Path("/c/vendor/attachments"))

  def test_extract_saves_beside_tracker(self):
    with tempfile.TemporaryDirectory() as tmp:
      emails = Path(tmp) / "emails"
      emails.mkdir()
      (emails / "m.eml").write_text(EML)
      ex.extract(str(emails / "m.eml"))
      self.assertTrue(any((Path(tmp) / "attachments").glob("*doc.pdf")))
      self.assertFalse((emails / "attachments").exists())


class FindEmlFilesTest(unittest.TestCase):
  """find_eml_files() reads both layouts."""

  def test_both_layouts(self):
    with tempfile.TemporaryDirectory() as tmp:
      root = Path(tmp)
      for rel in ("flat.eml", "emails/a.eml", "teams/t.eml", "transcripts/x.eml", "attachments/y.eml"):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(EML)
      got = [str(p.relative_to(root)) for p in rc.find_eml_files(root)]
      self.assertEqual(got, ["emails/a.eml", "flat.eml", "teams/t.eml"])


if __name__ == "__main__":
  unittest.main()
