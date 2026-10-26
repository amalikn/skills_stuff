"""Offline tests for writeback_status.py: a temporary git repo with a clean and a dirty skill. Run: just test (in skill-slurp-chat)."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "writeback_status.py"


def sh(repo: Path, *args: str) -> None:
    """Run git in the repo.

    Args:
        repo: the repository.
        args: git arguments.
    """
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, timeout=30)


class WritebackStatus(unittest.TestCase):
    """A dirty skill fails with its file listed; a clean one passes with its CHANGELOG line and version."""

    def test_clean_and_dirty(self) -> None:
        """Commit two skills, then edit one."""
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            sh(repo, "init", "-q")
            sh(repo, "config", "user.email", "t@example.invalid")
            sh(repo, "config", "user.name", "t")
            for name in ("skill-a", "skill-b"):
                folder = repo / "specialists" / name
                folder.mkdir(parents=True)
                (folder / "SKILL.md").write_text("x\n")
                (folder / "manifest.json").write_text('{"version": "1.2.3"}\n')
                (folder / "CHANGELOG.md").write_text("# Changelog\n\n## 20261026_1844 — entry\n")
            sh(repo, "add", "-A")
            sh(repo, "commit", "-q", "-m", "init")
            ok = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(repo), "skill-a"], capture_output=True, text=True, timeout=60, check=False)
            self.assertEqual(ok.returncode, 0)
            self.assertIn("[clean] version 1.2.3", ok.stdout)
            self.assertIn("20261026_1844", ok.stdout)
            (repo / "specialists" / "skill-b" / "SKILL.md").write_text("changed\n")
            bad = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(repo), "skill-a", "skill-b", "skill-x"],
                                 capture_output=True, text=True, timeout=60, check=False)
            self.assertEqual(bad.returncode, 1)
            self.assertIn("skill-b [DIRTY]", bad.stdout)
            self.assertIn("uncommitted", bad.stdout)
            self.assertIn("skill-x: NOT FOUND", bad.stdout)


if __name__ == "__main__":
    unittest.main()
