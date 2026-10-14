"""Offline tests for scripts/yaml_key_diff.py: key changes are found by content, and lost comments are listed and fail."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "yaml_key_diff.py"
_spec = importlib.util.spec_from_file_location("yaml_key_diff", SCRIPT)
ykd = importlib.util.module_from_spec(_spec)
sys.modules["yaml_key_diff"] = ykd
_spec.loader.exec_module(ykd)

OLD = "# Purpose header.\nversion: 1\nupdate_rules:\n  a:\n    update: [\"X.md\"]\n  # Why b exists.\n  b:\n    update: [\"Y.md\"]\n"
NEW = "version: 1\nskill_ai_it_version: v2\nupdate_rules:\n  a:\n    update:\n    - X.md\n  b:\n    update:\n    - Y.md\n  c:\n    update:\n    - Z.md\n"


class KeyChanges(unittest.TestCase):
    """A re-serialised file differs only where its content does."""

    def test_reformatting_is_not_a_change(self) -> None:
        """Quoting and flow style alone change nothing; the added keys are named."""
        out = ykd.key_changes(ykd.load_yaml(OLD), ykd.load_yaml(NEW))
        self.assertEqual(out, ["added: skill_ai_it_version", "added: update_rules.c"])

    def test_lost_comments(self) -> None:
        """Both comments of the old file are reported with their old line numbers."""
        self.assertEqual(ykd.lost_comments(OLD, NEW), ["1: # Purpose header.", "6: # Why b exists."])
        self.assertEqual(ykd.lost_comments(OLD, OLD), [])


class Cli(unittest.TestCase):
    """End to end against a git repo."""

    def test_exit_codes(self) -> None:
        """Exit 1 while a comment is lost, 0 once it is restored."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "context-map.yaml").write_text(OLD, encoding="utf-8")
            for cmd in (["git", "init", "-q"], ["git", "add", "."], ["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"]):
                subprocess.run(cmd, cwd=root, check=True)

            def run() -> subprocess.CompletedProcess:
                """Run the script against the temporary repo.

                Returns:
                    The completed process.
                """
                return subprocess.run([sys.executable, str(SCRIPT), "--project-root", tmp], capture_output=True, text=True)

            (root / "context-map.yaml").write_text(NEW, encoding="utf-8")
            self.assertEqual(run().returncode, 1)
            (root / "context-map.yaml").write_text("# Purpose header.\n" + NEW.replace("  c:", "  # Why b exists.\n  c:"), encoding="utf-8")
            self.assertEqual(run().returncode, 0)


if __name__ == "__main__":
    unittest.main()
