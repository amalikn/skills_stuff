"""Offline tests for pad_rewrite.py: comment type prefixes and the spec-to-commands translation. Run: python3 -m unittest test_pad_rewrite."""

import importlib.util
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location("pad_rewrite", Path(__file__).resolve().parents[1] / "scripts" / "pad_rewrite.py")
pr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pr)


class Prefix(unittest.TestCase):
  """prefixed() adds the type word once."""

  def test_after_stamp_and_idempotent(self):
    """A stamped comment gets `TYPE:` after its stamp; a second pass changes nothing; an unstamped one gets it at the start.

    Returns:
      None.
    """
    new = pr.prefixed("2026-11-10 13:20 AEDT: server check done", "FINDING")
    self.assertEqual(new, "2026-11-10 13:20 AEDT FINDING: server check done")
    self.assertIsNone(pr.prefixed(new, "FINDING"))
    self.assertEqual(pr.prefixed("box inaccessible", "RISK"), "RISK: box inaccessible")
    self.assertIsNone(pr.prefixed("CORRECTION 2026-11-10 13:05 AEDT: the 13:00 was wrong", "CORRECTION"))
    with self.assertRaises(ValueError):
      pr.prefixed("x", "NOPE")


class Commands(unittest.TestCase):
  """commands() turns a spec into guarded pad calls."""

  def test_body_needs_seq_and_is_guarded(self):
    """A body write carries --stdin and --expected-seq; one without seq is refused.

    Returns:
      None.
    """
    cmds = pr.commands({"items": [{"ref": "TASK-1", "seq": 7, "title": "T", "body": "B", "tags": ["bench"]}]}, {})
    label, argv, stdin = cmds[0]
    self.assertEqual(stdin, "B")
    self.assertEqual(argv[argv.index("--expected-seq") + 1], "7")
    self.assertIn('["bench"]', argv)
    with self.assertRaises(ValueError):
      pr.commands({"items": [{"ref": "TASK-1", "body": "B"}]}, {})

  def test_comments_notes_decides(self):
    """Comments already typed are skipped; notes and decisions carry their idempotency key; an unknown comment id is refused.

    Returns:
      None.
    """
    spec = {"comments": [{"ref": "TASK-1", "id": "a", "type": "RISK"}, {"ref": "TASK-1", "id": "b", "type": "FINDING"}],
            "notes": [{"ref": "TASK-1", "summary": "did x", "key": "k1"}],
            "decides": [{"ref": "TASK-1", "decision": "use y", "rationale": "r", "key": "k2"}]}
    cmds = pr.commands(spec, {"a": "2026-11-10 13:54 AEDT: risk", "b": "FINDING: already"})
    self.assertEqual([c[0].split()[0] for c in cmds], ["comment", "note", "decide"])
    self.assertIn("k1", cmds[1][1])
    self.assertIn("k2", cmds[2][1])
    with self.assertRaises(ValueError):
      pr.commands({"comments": [{"ref": "TASK-1", "id": "zz", "type": "RISK"}]}, {})

  def test_comment_body_replace_skips_when_equal(self):
    """A comment with `body` is replaced by that text, and skipped when it already reads so.

    Returns:
      None.
    """
    spec = {"comments": [{"ref": "TASK-1", "id": "a", "body": "new"}, {"ref": "TASK-1", "id": "b", "body": "same"}]}
    cmds = pr.commands(spec, {"a": "old", "b": "same"})
    self.assertEqual(len(cmds), 1)
    self.assertEqual(cmds[0][2], "new")


if __name__ == "__main__":
  unittest.main()
