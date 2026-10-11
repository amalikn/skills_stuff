"""Offline tests for scripts/check_outside_blocks.py: managed blocks are ignored, any change outside them is reported."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_outside_blocks.py"
_spec = importlib.util.spec_from_file_location("check_outside_blocks", SCRIPT)
cob = importlib.util.module_from_spec(_spec)
sys.modules["check_outside_blocks"] = cob
_spec.loader.exec_module(cob)

BEFORE = (
    "# Agents\n\nOwn rule.\n\n<!-- BEGIN MANAGED: skill-ai-it:navigation -->\nold nav\n<!-- END MANAGED: skill-ai-it:navigation -->\n\n"
    "<!-- managed:skill-ai-it:governance-checks — regenerated -->\nold checks\n<!-- /managed:skill-ai-it:governance-checks -->\n\nTail.\n"
)


def _repo(tmp: str) -> Path:
    """A git repo holding BEFORE as AGENTS.md, committed.

    Args:
        tmp: an empty directory.

    Returns:
        The repo root.
    """
    root = Path(tmp)
    (root / "AGENTS.md").write_text(BEFORE)
    for cmd in (["init", "-q"], ["add", "."], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "x"]):
        subprocess.run(["git", "-C", tmp, *cmd], check=True)
    return root


class CheckOutsideBlocksTest(unittest.TestCase):
    """compare() and main() against a committed file."""

    def test_block_only_change_passes(self):
        """New text inside both block kinds is not a difference."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(tmp)
            (root / "AGENTS.md").write_text(BEFORE.replace("old nav", "new nav\nmore").replace("old checks", "new checks"))
            self.assertEqual(cob.compare(root, "HEAD", ["AGENTS.md"]), [])
            self.assertEqual(cob.main(["--project-root", tmp, "--files", "AGENTS.md"]), 0)

    def test_outside_change_fails(self):
        """An edit outside the blocks is reported and exits 1."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(tmp)
            (root / "AGENTS.md").write_text(BEFORE.replace("Own rule.", "Own rule, reworded."))
            diffs = cob.compare(root, "HEAD", ["AGENTS.md"])
            self.assertEqual([d[0] for d in diffs], ["AGENTS.md"])
            self.assertEqual(cob.main(["--project-root", tmp, "--files", "AGENTS.md"]), 1)

    def test_dropped_end_marker_fails(self):
        """A block whose END marker a formatter dropped is no longer a block, so its text counts as outside and fails."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(tmp)
            (root / "AGENTS.md").write_text(BEFORE.replace("<!-- END MANAGED: skill-ai-it:navigation -->\n", ""))
            self.assertEqual(cob.main(["--project-root", tmp, "--files", "AGENTS.md"]), 1)


if __name__ == "__main__":
    unittest.main()
