"""Offline tests for scripts/teams_docx.py: header lines read, turns split at line breaks, one speaker's paragraphs joined, the start converted to a
time zone, wording copied unchanged, a non-transcript refused, and an existing file never replaced without --force.

Run: python3 -m unittest discover -s tests
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "teams_docx.py"
_spec = importlib.util.spec_from_file_location("commtracker_teams_docx", SCRIPT)
td = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = td
_spec.loader.exec_module(td)

NS = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'


def para(*runs: str) -> str:
  """One paragraph; a run starting with "|" is preceded by a line break, as Teams writes caption lines.

  Args:
    runs: the run texts.

  Returns:
    The paragraph XML.
  """
  out = []
  for r in runs:
    br = "<w:br/>" if r.startswith("|") else ""
    out.append(f'<w:r>{br}<w:t xml:space="preserve">{r.lstrip("|")}</w:t></w:r>')
  return f"<w:p>{''.join(out)}</w:p>"


def make_docx(folder: Path, paras: list[str]) -> Path:
  """Write a minimal .docx holding the given paragraphs.

  Args:
    folder: a temporary folder.
    paras: paragraph XML strings.

  Returns:
    The .docx path.
  """
  path = folder / "Team call.docx"
  with zipfile.ZipFile(path, "w") as z:
    z.writestr("word/document.xml", f"<w:document {NS}><w:body>{''.join(paras)}</w:body></w:document>")
  return path


SAMPLE = [
  para("Team call-20261120_003042UTC-Meeting Recording"),
  para("20 November 2026, 12:30am"),
  para("47m 6s"),
  para(" ", "|started transcription"),
  para("|Malik Ahmad   ", "0:08", "|Yep.", "|Morning, guys."),
  para("|Robert Gallesio   ", "0:14", "|Morning, how are ya? It&apos;s good."),
  para("|Robert Gallesio   ", "0:16", "|Second paragraph."),
  para("|Malik Ahmad   ", "1:02:03", "|Bye."),
]


class TeamsDocxTest(unittest.TestCase):
  """Parsing, rendering and write safety."""

  def test_parse(self) -> None:
    """Header read; one turn per speaker change; lines kept as exported."""
    with tempfile.TemporaryDirectory() as tmp:
      t = td.parse(make_docx(Path(tmp), SAMPLE))
    self.assertEqual(t.duration, "47m 6s")
    self.assertEqual(t.start_utc.strftime("%Y%m%d_%H%M%S"), "20261120_003042")
    self.assertEqual([(x.name, x.ts) for x in t.turns], [("Malik Ahmad", "0:08"), ("Robert Gallesio", "0:14"), ("Malik Ahmad", "1:02:03")])
    self.assertEqual(t.turns[0].lines, ["Yep.", "Morning, guys."])
    self.assertEqual(t.turns[1].lines, ["Morning, how are ya? It's good.", "Second paragraph."])

  def test_render_local_time(self) -> None:
    """The start shows in the given zone; labels and lines follow the turn layout."""
    with tempfile.TemporaryDirectory() as tmp:
      text = td.render(td.parse(make_docx(Path(tmp), SAMPLE)), "Australia/Sydney", "Team call.docx")
    self.assertIn("**Date:** Friday, 20 November 2026, 11:30 AM AEDT", text)
    self.assertIn("# Transcript — Team call\n", text)
    self.assertIn("## Full transcript\n\n**Malik Ahmad (0:08):**", text)
    self.assertIn("**Malik Ahmad (0:08):**\nYep.\nMorning, guys.\n\n**Robert Gallesio (0:14):**", text)
    self.assertIn("[Team call.docx](Team%20call.docx)", text)

  def test_not_a_transcript(self) -> None:
    """A document with no speaker lines is refused with exit 2."""
    with tempfile.TemporaryDirectory() as tmp:
      path = make_docx(Path(tmp), [para("Just a letter.")])
      self.assertEqual(td.main([str(path)]), 2)

  def test_preview_then_refuse_overwrite(self) -> None:
    """Preview writes nothing; --apply writes; a second --apply refuses without --force."""
    with tempfile.TemporaryDirectory() as tmp:
      path = make_docx(Path(tmp), SAMPLE)
      out = Path(tmp) / "t.md"
      self.assertEqual(td.main([str(path), "--out", str(out)]), 0)
      self.assertFalse(out.exists())
      self.assertEqual(td.main([str(path), "--out", str(out), "--apply"]), 0)
      self.assertTrue(out.exists())
      self.assertEqual(td.main([str(path), "--out", str(out), "--apply"]), 1)
      self.assertEqual(td.main([str(path), "--out", str(out), "--apply", "--force"]), 0)


if __name__ == "__main__":
  unittest.main()
