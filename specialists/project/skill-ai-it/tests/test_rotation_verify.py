"""Offline tests for records/rotation_verify.py on a throwaway git repository. Run: python3 -m unittest tests/test_rotation_verify.py"""

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location("rotation_verify", Path(__file__).resolve().parents[1] / "scripts" / "records" / "rotation_verify.py")
rv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rv)

BEFORE = "# Changelog\n\nLast rotated: 20261118\n\n- [20261119 — new](#new)\n- [20261101 — old](#old)\n\n## 20261119 — new\n\n- kept\n\n## 20261101 — old\n\n- moved line one\n- moved line two\n"
AFTER = "# Changelog\n\nLast rotated: 20261119\n\n- [20261119 — new](#new)\n\n## 20261119 — new\n\n- kept\n"


class RotationVerify(unittest.TestCase):
  """A clean rotation passes, a lost line fails, and re-wrapping in history still matches."""

  def setUp(self) -> None:
    self.tmp = tempfile.TemporaryDirectory()
    self.root = Path(self.tmp.name)
    git = ["git", "-C", str(self.root)]
    subprocess.run([*git, "init", "-q"], check=True)
    subprocess.run([*git, "config", "user.email", "t@example.invalid"], check=True)
    subprocess.run([*git, "config", "user.name", "t"], check=True)
    (self.root / "CHANGELOG.md").write_text(BEFORE)
    (self.root / "docs" / "history").mkdir(parents=True)
    subprocess.run([*git, "add", "."], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "init"], check=True)
    (self.root / "CHANGELOG.md").write_text(AFTER)

  def tearDown(self) -> None:
    self.tmp.cleanup()

  def test_a_rotation_that_moved_every_line_passes(self) -> None:
    """Every removed content line is in history (Contents links and the stamp are ignored)."""
    (self.root / "docs" / "history" / "changelog-20261119.md").write_text("## 20261101 — old\n\n- moved line one\n- moved line two\n")
    self.assertEqual(rv.main(["--project-root", str(self.root)]), 0)

  def test_a_lost_line_fails(self) -> None:
    """A removed line absent from history is reported and exits 1."""
    (self.root / "docs" / "history" / "changelog-20261119.md").write_text("## 20261101 — old\n\n- moved line one\n")
    self.assertEqual(rv.main(["--project-root", str(self.root)]), 1)

  def test_a_rewrapped_line_still_matches(self) -> None:
    """Whitespace differences (a re-wrapped paragraph) do not count as loss."""
    (self.root / "docs" / "history" / "changelog-20261119.md").write_text("## 20261101 — old\n\n- moved line\n  one\n- moved   line two\n")
    self.assertEqual(rv.main(["--project-root", str(self.root)]), 0)


if __name__ == "__main__":
  unittest.main()
