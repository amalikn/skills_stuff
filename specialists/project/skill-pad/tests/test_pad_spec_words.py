"""Offline tests for pad_spec_words.py: a relabelled body passes, a dropped sentence fails. Run: python3 -m unittest test_pad_spec_words."""

import importlib.util
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location("pad_spec_words", Path(__file__).resolve().parents[1] / "scripts" / "pad_spec_words.py")
psw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(psw)

OLD = "The run fails on a timeout.\n  - Cause: a bare TimeoutError.\n  - Fixed in `d49d2043`."


class Lost(unittest.TestCase):
  """lost() reports only words of the old body that are gone."""

  def test_relabelled_body_keeps_every_word(self):
    """Labels and filler added, bullets made sections: nothing lost.

    Returns:
        None.
    """
    new = "**Seen:** The run fails on a timeout.\n\n**Evidence:** not recorded.\n\n**Cause:** a bare TimeoutError.\n\n**Closure:** Fixed in `d49d2043`."
    self.assertEqual(psw.lost(OLD, new, set()), {})

  def test_dropped_sentence_is_reported(self):
    """A sentence left out shows as lost words.

    Returns:
        None.
    """
    new = "**Seen:** The run fails on a timeout.\n\n**Closure:** Fixed in `d49d2043`."
    self.assertEqual(set(psw.lost(OLD, new, set())), {"a", "cause", "bare", "timeouterror"})

  def test_allowed_word_may_go(self):
    """A plain label word an author folded into a bold label is allowed when named.

    Returns:
        None.
    """
    new = "**Seen:** The run fails on a timeout.\n\n**Effect:** a bare TimeoutError.\n\n**Closure:** Fixed in `d49d2043`."
    self.assertEqual(psw.lost(OLD, new, {"cause"}), {})


if __name__ == "__main__":
  unittest.main()
