"""Offline tests for govern's two safety steps: scripts/govern_guard.py (dirty governed files stop the run) and `--prune-baseline` in
scripts/doc_freshness.py and scripts/role_check.py (resolved entries leave the baseline; nothing is ever added)."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def load(name: str):
    """Import a script from scripts/ by file name.

    Args:
        name: the module name without `.py`.

    Returns:
        The loaded module.
    """
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


guard, df, rc = load("govern_guard"), load("doc_freshness"), load("role_check")


def git(root: Path, *args: str) -> None:
    """Run git quietly in `root`.

    Args:
        root: the repository.
        args: git arguments.
    """
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *args], check=True, capture_output=True)


class GuardTest(unittest.TestCase):
    """The guard passes a clean tree and a non-git folder, and stops on a dirty governed file only."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "proj"
        self.root.mkdir()
        (self.root / "CHANGELOG.md").write_text("# Changelog\n")
        (self.root / "notes.md").write_text("x\n")
        git(self.root, "init", "-q")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "init")

    def tearDown(self):
        self.tmp.cleanup()

    def test_clean_tree_passes(self):
        self.assertEqual(guard.main(["--project-root", str(self.root)]), 0)

    def test_dirty_governed_file_stops_the_run(self):
        # enterprise-strategy, 2026-10-14: govern rotated an uncommitted CHANGELOG and the two could not be split afterwards
        (self.root / "CHANGELOG.md").write_text("# Changelog\n\n- unsaved\n")
        (self.root / "docs" / "history").mkdir(parents=True)
        (self.root / "docs" / "history" / "changelog-x.md").write_text("x\n")
        self.assertEqual(guard.dirty_governed(self.root), ["CHANGELOG.md", "docs/history/changelog-x.md"])
        self.assertEqual(guard.main(["--project-root", str(self.root)]), 1)

    def test_other_dirty_files_do_not_block(self):
        (self.root / "notes.md").write_text("changed\n")
        self.assertEqual(guard.main(["--project-root", str(self.root)]), 0)

    def test_not_a_git_tree_passes(self):
        plain = Path(self.tmp.name) / "plain"
        plain.mkdir()
        self.assertIsNone(guard.dirty_governed(plain))
        self.assertEqual(guard.main(["--project-root", str(plain)]), 0)


class PruneTest(unittest.TestCase):
    """`--prune-baseline` drops resolved entries, keeps a live entry's recorded value, and never adds a finding."""

    def project(self, tmp: str) -> Path:
        """A project whose README has no front matter, so role_check has a live finding.

        Args:
            tmp: a temporary directory.

        Returns:
            The project root.
        """
        root = Path(tmp)
        (root / "scripts").mkdir()
        (root / "README.md").write_text("# Project\n\nNo header here.\n")
        return root

    def test_role_baseline_prune(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.project(tmp)
            live = sorted(rc.findings(root, __import__("datetime").date.today()))
            self.assertTrue(live)
            base = root / rc.BASELINE
            base.write_text(json.dumps({live[0]: "RECORDED", "gone:finding": "old"}))
            self.assertEqual(rc.main(["--project-root", tmp, "--prune-baseline"]), 0)
            self.assertEqual(json.loads(base.read_text()), {live[0]: "RECORDED"})

    def test_freshness_baseline_prune_never_adds(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.project(tmp)
            base = root / df.DEFAULT_BASELINE
            base.write_text(json.dumps({"stale:gone.md": "2026-01-01"}))
            self.assertEqual(df.main(["--project-root", tmp, "--prune-baseline"]), 0)
            self.assertEqual(json.loads(base.read_text()), {})


if __name__ == "__main__":
    unittest.main()
