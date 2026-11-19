"""Offline tests for pad_format_spec.reformat: layout changes, words never do. Run: python3 -m unittest tests/test_pad_format_spec.py"""

import importlib.util
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location("pad_format_spec", Path(__file__).resolve().parents[1] / "scripts" / "pad_format_spec.py")
pfs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pfs)


class Reformat(unittest.TestCase):
  """Each layout rule can apply, and a body already in the standard is left alone."""

  def test_plain_labels_become_bold_paragraphs(self) -> None:
    """Single-newline plain labels (an old Ask) become bold labels separated by blank lines."""
    body = "Serves: DL-011\nQuestion: who holds the keys?\nOptions to weigh: (a) one; (b) two\nRepo: /x"
    want = "**Serves:** DL-011\n\n**Question:** who holds the keys?\n\n**Options to weigh:** (a) one; (b) two\n\n**Repo:** /x"
    self.assertEqual(pfs.reformat(body), want)

  def test_hard_wrapped_sentence_is_joined(self) -> None:
    """A line broken mid-sentence by a formatter is joined back to its sentence."""
    body = "**Do:** sign with step-up\n(acr) plus a CSR\n\n**Writes:** repo"
    self.assertEqual(pfs.reformat(body), "**Do:** sign with step-up (acr) plus a CSR\n\n**Writes:** repo")

  def test_numbered_question_labels(self) -> None:
    """`Question 1 (contract):` counts as a label."""
    self.assertEqual(pfs.reformat("Question 1 (contract): how?"), "**Question 1 (contract):** how?")

  def test_lists_tables_and_code_are_kept(self) -> None:
    """List items, table rows and fenced code keep their lines; a label word inside code is not touched."""
    body = "**Do:**\n\n1. first\n2. second\n\n| a | b |\n| - | - |\n\n```\nWhy: not a label here\n```"
    self.assertEqual(pfs.reformat(body), body)

  def test_standard_body_is_unchanged(self) -> None:
    """A body already in the standard comes back identical, so a rerun writes nothing."""
    body = "**Serves:** S1\n\n**Why:** a finding\n\n**Done when:** check passes"
    self.assertEqual(pfs.reformat(body), body)

  def test_words_are_preserved(self) -> None:
    """Reformatting never adds, drops or reorders a word."""
    body = "Serves: a b\nWhy: c\nd e\nAgent advice: f"
    self.assertEqual(pfs.words(pfs.reformat(body)), pfs.words(body))

  def test_label_mid_line_is_not_split(self) -> None:
    """`Agent advice:` inside an Options paragraph stays where it is."""
    body = "**Options to weigh:** (a); (b). Agent advice: (a)."
    self.assertEqual(pfs.reformat(body), body)


if __name__ == "__main__":
  unittest.main()
