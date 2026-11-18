"""Offline tests for reflow_lossless: a re-wrap is proven lossless, a changed word or cell is caught, and tables are never passed unproven.

Run: just test (stdlib unittest). The un-wrapper is injected, so no node and no table-reflow are needed.
"""

import importlib
import io
import pathlib
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
reflow_lossless = importlib.import_module("reflow_lossless")


def fake_unwrap(text: str) -> str:
  """Join continuation rows (a first cell indented by three spaces) onto the row above, standing in for the real un-wrapper.

  Args:
    text: a file's text with wrapped tables.

  Returns:
    The text with one line per table row.
  """
  out: list[str] = []
  for line in text.split("\n"):
    cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.startswith("|") else []
    if line.startswith("|   ") and out and out[-1].startswith("|"):
      prev = [c.strip() for c in out[-1].strip().strip("|").split("|")]
      out[-1] = "| " + " | ".join(f"{p} {c}".strip() for p, c in zip(prev, cells)) + " |"
    else:
      out.append(line)
  return "\n".join(out)


BEFORE = "Intro words on one long line that will wrap.\n\n| A | B |\n| - | - |\n| one two three | plain text here |\n\n> quoted line one\n> quoted line two\n"
REWRAPPED = "Intro words on one long\nline that will wrap.\n\n| A | B |\n| --- | --- |\n| one two | plain text |\n|   three | here |\n\n> quoted line one quoted line two\n"


class Lossless(unittest.TestCase):
  """A re-wrap changes line breaks only."""

  def test_rewrap_of_prose_quote_and_table_is_lossless(self):
    self.assertNotEqual(BEFORE, REWRAPPED)
    self.assertEqual(reflow_lossless.differences(BEFORE, REWRAPPED, fake_unwrap), [])

  def test_a_changed_word_is_caught(self):
    found = reflow_lossless.differences(BEFORE, BEFORE.replace("Intro words", "Intro word"), fake_unwrap)
    self.assertTrue(found and found[0].startswith("prose: 1 differing span"))

  def test_a_changed_cell_is_caught(self):
    found = reflow_lossless.differences(BEFORE, BEFORE.replace("one two three", "one two four"), fake_unwrap)
    self.assertTrue(any(line.startswith("tables: 1 differing block") for line in found))

  def test_a_cell_moved_to_another_column_is_caught(self):
    found = reflow_lossless.differences("| A | B |\n| - | - |\n| x | y |\n", "| A | B |\n| - | - |\n| y | x |\n", fake_unwrap)
    self.assertTrue(found)

  def test_tables_without_an_unwrapper_are_refused(self):
    with self.assertRaises(ValueError):
      reflow_lossless.differences(BEFORE, BEFORE, None)

  def test_prose_only_needs_no_unwrapper(self):
    self.assertEqual(reflow_lossless.differences("a b c\n", "a\nb c\n", None), [])

  def test_contents_block_is_ignored_on_request(self):
    after = "# T\n\n## Contents\n\n- [One](#one)\n\n## One\n\ntext\n"
    before = "# T\n\n## One\n\ntext\n"
    self.assertTrue(reflow_lossless.differences(before, after, None))
    self.assertEqual(reflow_lossless.differences(before, after, None, ignore_contents=True), [])


class CommandLine(unittest.TestCase):
  """Exit codes: 0 lossless, 1 different, 2 cannot prove."""

  def run_main(self, before: str, after: str, *extra: str) -> tuple[int, str]:
    """Write two files and run the command line on them.

    Args:
      before: the first file's text.
      after: the second file's text.
      extra: further arguments.

    Returns:
      The exit code and everything printed.
    """
    with tempfile.TemporaryDirectory() as tmp:
      a, b = pathlib.Path(tmp) / "a.md", pathlib.Path(tmp) / "b.md"
      a.write_text(before, encoding="utf-8")
      b.write_text(after, encoding="utf-8")
      out = io.StringIO()
      with redirect_stdout(out), redirect_stderr(out):
        code = reflow_lossless.main([str(a), str(b), *extra])
      return code, out.getvalue()

  def test_exit_codes(self):
    self.assertEqual(self.run_main("a b\n", "a\nb\n")[0], 0)
    self.assertEqual(self.run_main("a b\n", "a c\n")[0], 1)
    code, text = self.run_main(BEFORE, BEFORE)
    self.assertEqual(code, 2)
    self.assertIn("cannot prove it", text)
    self.assertEqual(self.run_main("a\n", "a\n", "--table-reflow", "/nonexistent/cli.mjs")[0], 2)


if __name__ == "__main__":
  unittest.main()
