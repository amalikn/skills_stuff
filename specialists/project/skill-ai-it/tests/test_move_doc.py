"""Offline tests for scripts/move_doc.py: repeated --keep-records flags all protect their files."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "move_doc.py"
_spec = importlib.util.spec_from_file_location("move_doc", SCRIPT)
md = importlib.util.module_from_spec(_spec)
sys.modules["move_doc"] = md
_spec.loader.exec_module(md)


class KeepRecordsTest(unittest.TestCase):
    """A move with two --keep-records flags edits neither record."""

    def test_repeated_flags_protect_every_record(self):
        root = Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        (root / "docs" / "history").mkdir(parents=True)
        (root / "docs" / "old.md").write_text("# old\n")
        link = "see [old](../old.md)\n"
        for name in ("a.md", "b.md"):
            (root / "docs" / "history" / name).write_text(link)
        (root / "README.md").write_text("[old](docs/old.md)\n")
        subprocess.run(["git", "add", "-A"], cwd=root, check=True)
        rc = md.main(["--project-root", str(root), "--keep-records", "docs/history/a.md", "--keep-records", "docs/history/b.md",
                      "--apply", "docs/old.md"])
        self.assertEqual(rc, 0)
        for name in ("a.md", "b.md"):
            self.assertEqual((root / "docs" / "history" / name).read_text(), link)
        self.assertIn("docs/archive/old.md", (root / "README.md").read_text())


if __name__ == "__main__":
    unittest.main()
