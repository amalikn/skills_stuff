"""Offline tests for scripts/adoption/repoint_paths.py: live references move to their family folder; history, dated files, local namesakes and
already-moved paths are left alone; a plan writes nothing."""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "adoption" / "repoint_paths.py"
_spec = importlib.util.spec_from_file_location("repoint_paths", SCRIPT)
rp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rp)

OLD = '@python "{{ai_it}}/scripts/rotate_records.py" --project-root .\n'
NEW = '@python "{{ai_it}}/scripts/records/rotate_records.py" --project-root .\n'


def workspace(tmp: str) -> Path:
    """Build a small workspace holding one live caller and each kind of file that must not change.

    Args:
        tmp: a temporary directory.

    Returns:
        The workspace root.
    """
    root = Path(tmp)
    (root / "map.txt").write_text("records rotate_records\nchecks doc_freshness\n")
    proj = root / "proj"
    (proj / "docs/history").mkdir(parents=True)
    (proj / "justfile").write_text(OLD)
    (proj / "CHANGELOG.md").write_text(OLD)
    (proj / "docs/history/changelog-20260101_0000.md").write_text(OLD)
    (proj / "docs/report-20261001_1200.md").write_text(OLD)
    (proj / "done.md").write_text(NEW)
    local = root / "local"
    (local / "scripts").mkdir(parents=True)
    (local / "scripts/doc_freshness.py").write_text("")
    (local / "justfile").write_text("@python scripts/doc_freshness.py\n")
    return root


class Repoint(unittest.TestCase):
    """What moves and what stays."""

    def run_tool(self, root: Path, *extra: str) -> int:
        """Run the tool over the workspace's map and root.

        Args:
            root: the workspace.
            extra: further arguments, e.g. --apply.

        Returns:
            The exit code.
        """
        return rp.main(["--map", str(root / "map.txt"), "--root", str(root), *extra])

    def test_plan_writes_nothing_and_exits_1(self) -> None:
        """A plan reports pending changes and leaves every file as it was."""
        with tempfile.TemporaryDirectory() as tmp:
            root = workspace(tmp)
            self.assertEqual(self.run_tool(root), 1)
            self.assertEqual((root / "proj/justfile").read_text(), OLD)

    def test_apply_moves_live_reference_only(self) -> None:
        """--apply rewrites the justfile; history, dated files, moved paths and local namesakes keep their text."""
        with tempfile.TemporaryDirectory() as tmp:
            root = workspace(tmp)
            self.assertEqual(self.run_tool(root, "--apply"), 0)
            proj = root / "proj"
            self.assertEqual((proj / "justfile").read_text(), NEW)
            for rel in ("CHANGELOG.md", "docs/history/changelog-20260101_0000.md", "docs/report-20261001_1200.md"):
                self.assertEqual((proj / rel).read_text(), OLD, rel)
            self.assertEqual((proj / "done.md").read_text(), NEW)
            self.assertEqual((root / "local/justfile").read_text(), "@python scripts/doc_freshness.py\n")

    def test_second_run_is_clean(self) -> None:
        """After --apply a plan finds nothing: the rewrite is idempotent."""
        with tempfile.TemporaryDirectory() as tmp:
            root = workspace(tmp)
            self.run_tool(root, "--apply")
            self.assertEqual(self.run_tool(root), 0)


if __name__ == "__main__":
    unittest.main()
