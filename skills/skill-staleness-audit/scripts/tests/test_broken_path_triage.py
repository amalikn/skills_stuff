"""Tests for scripts/broken_path_triage.py on a temp project. Stdlib only: `python3 -m unittest discover -s scripts/tests`."""
# claim-scan:examples — every path in this file is a fixture inside a temp project, not a reference.

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
_SPEC = importlib.util.spec_from_file_location("broken_path_triage", HERE / "broken_path_triage.py")
bt = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(bt)

CLAIMS = """  BROKEN    docs/guide.md:3  app/pkg/jobs.py
  BROKEN    docs/guide.md:4  tools/old_name.py
  BROKEN    docs/guide.md:5  gone_forever.py
  BROKEN    docs/history/changelog-1.md:9  gone_forever.py
  BROKEN    docs/guide.md:6  <site>-smc01
"""


class Triage(unittest.TestCase):
  """parse_claims, classify and the command's exit status."""

  def setUp(self):
    """A project holding nautobot/app/pkg/jobs.py and scripts/moved/old_name.py.

    Returns:
      None.
    """
    self.tmp = tempfile.TemporaryDirectory()
    self.root = Path(self.tmp.name)
    for rel in ("nautobot/app/pkg/jobs.py", "scripts/moved/old_name.py", "docs/guide.md"):
      (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
      (self.root / rel).write_text("x\n")
    (self.root / "claims.txt").write_text(CLAIMS)

  def tearDown(self):
    """Remove the temp project.

    Returns:
      None.
    """
    self.tmp.cleanup()

  def test_classes(self):
    """A package-relative path is a suffix, a renamed folder is moved, a missing file is gone, a placeholder is not a path.

    Returns:
      None.
    """
    rows = bt.parse_claims(CLAIMS)
    self.assertEqual(len(rows), 5)
    idx = bt.index_files([self.root])
    self.assertEqual([bt.classify(p, idx) for _, _, p in rows], ["suffix", "moved", "gone", "gone", "not-a-path"])
    self.assertTrue(bt.is_history("docs/history/changelog-1.md"))
    self.assertFalse(bt.is_history("docs/guide.md"))

  def test_exit_status_names_only_live_gone(self):
    """Exit 1 and one GONE line: the history row with the same path is not a defect.

    Returns:
      None.
    """
    r = subprocess.run(
      [sys.executable, str(HERE / "broken_path_triage.py"), "--root", str(self.root), "--claims", str(self.root / "claims.txt")],
      capture_output=True,
      text=True,
      timeout=60,
    )
    self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
    self.assertEqual([x for x in r.stdout.splitlines() if x.startswith("GONE")], ["GONE (live) docs/guide.md:5  gone_forever.py"])

  def test_unreadable_claims_file(self):
    """A missing claims file exits 2.

    Returns:
      None.
    """
    self.assertEqual(bt.main(["--root", str(self.root), "--claims", str(self.root / "nope.txt")]), 2)


if __name__ == "__main__":
  unittest.main()
