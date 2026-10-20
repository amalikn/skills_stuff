"""Offline tests for skill-coder's quality helpers: suppressions, group_timeouts and scaffold, each shown passing on good input and failing on bad.

Run: `just test` (unittest, the project's pinned interpreter). The helpers are imported from scripts/ by name. Split from test_helpers.py
(2026-10-20) to keep each test module inside the pack's size budget.
"""

from __future__ import annotations

import importlib
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

call_timeouts, group_timeouts, scaffold, script_headers, suppressions = (
    importlib.import_module(n) for n in ("call_timeouts", "group_timeouts", "scaffold", "script_headers", "suppressions"))


def _tree(files: dict[str, str]) -> Path:
    """A temporary project tree.

    Args:
        files: {relative path: content}.

    Returns:
        The root (left for the OS to clear).
    """
    root = Path(tempfile.mkdtemp())
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(textwrap.dedent(text), encoding="utf-8")
    return root


class Suppressions(unittest.TestCase):
    """Inline linter suppressions are counted per language; a marker in a string or outside a comment is not one."""

    def test_python_comments_only(self) -> None:
        """noqa and type: ignore in comments count; the same words in a string do not."""
        src = 'import x  # noqa: E402\ny = 1  # type: ignore[assignment]\ns = "# noqa"\n# plain comment\n'
        self.assertEqual([n for n, _t in suppressions.python_suppressions(src)], [1, 2])

    def test_other_languages(self) -> None:
        """shellcheck, eslint, nolint and Rust allow count after their comment opener; an echoed word does not."""
        self.assertEqual(len(suppressions.line_suppressions("# shellcheck disable=SC2086\necho 'shellcheck disable=x'\n", ".sh")), 1)
        self.assertEqual(len(suppressions.line_suppressions("// eslint-disable-next-line\nconst a = 1; // @ts-ignore\n", ".ts")), 2)
        self.assertEqual(len(suppressions.line_suppressions("x := 1 //nolint:errcheck\n", ".go")), 1)
        self.assertEqual(len(suppressions.line_suppressions("#[allow(dead_code)]\nfn a() {}\n", ".rs")), 1)
        self.assertEqual(suppressions.line_suppressions("anything\n", ".txt"), [])

    def test_cli_ratchet(self) -> None:
        """A new suppression fails; at its baseline the run passes."""
        root = _tree({"src/a.py": "import os  # noqa\n"})
        self.assertEqual(suppressions.main(["--project-root", str(root), "--roots", "src"]), 1)
        suppressions.main(["--project-root", str(root), "--roots", "src", "--write-baseline"])
        self.assertEqual(suppressions.main(["--project-root", str(root), "--roots", "src"]), 0)


class GroupTimeouts(unittest.TestCase):
    """A timed run() of a command that starts children (ssh, a shell) is found; other timed calls are not."""

    def test_spawners_found(self) -> None:
        """ssh, bash -c, shell=True and a tsh(...) builder count; ls, an untimed ssh and **kwargs do not."""
        src = textwrap.dedent('''
            import subprocess
            subprocess.run(["ssh", "-o", "x", "host", "true"], timeout=5)
            subprocess.check_output(["/bin/bash", "-c", "a | b"], timeout=5)
            subprocess.run("a | b", shell=True, timeout=5)
            subprocess.run(teleport.tsh("ssh", proxy, "root@n"), timeout=9)
            subprocess.run(["ls"], timeout=5)
            subprocess.run(["ssh", "h"])
            subprocess.run(["ssh", "h"], **opts)
            s = "subprocess.run(['ssh'], timeout=1)"
        ''')
        self.assertEqual([line for line, _t in group_timeouts.group_unsafe_calls(src)], [3, 4, 5, 6])

    def test_cli_ratchet(self) -> None:
        """A new call fails; at its baseline the run passes."""
        root = _tree({"src/a.py": "import subprocess\nsubprocess.run(['ssh', 'h'], timeout=5)\n"})
        self.assertEqual(group_timeouts.main(["--project-root", str(root), "--roots", "src"]), 1)
        group_timeouts.main(["--project-root", str(root), "--roots", "src", "--write-baseline"])
        self.assertEqual(group_timeouts.main(["--project-root", str(root), "--roots", "src"]), 0)


class Scaffold(unittest.TestCase):
    """The skeletons meet the pack's own checks and carry the --apply gate only when asked."""

    def test_python_skeleton_passes_the_checks(self) -> None:
        """A writing Python skeleton parses, has a complete header, timed calls, no suppression and an --apply gate; its test runs."""
        files = scaffold.python_files("sync_x", "Sync X", True, "sync_x.py [--apply]")
        module = files["sync_x.py"]
        self.assertEqual(script_headers.missing_parts(module, ".py"), [])
        self.assertEqual(call_timeouts.untimed_calls(module), [])
        self.assertEqual(suppressions.python_suppressions(module), [])
        self.assertIn('"--apply"', module)
        root = _tree({"sync_x.py": module, "test_sync_x.py": files["test_sync_x.py"]})
        sys.path.insert(0, str(root))
        try:
            result = unittest.TextTestRunner(stream=open(root / "out.txt", "w", encoding="utf-8")).run(
                unittest.defaultTestLoader.loadTestsFromName("test_sync_x"))
        finally:
            sys.path.remove(str(root))
            for name in ("sync_x", "test_sync_x"):
                sys.modules.pop(name, None)
        self.assertTrue(result.wasSuccessful())

    def test_read_only_has_no_gate_and_shell_header(self) -> None:
        """Without --writes there is no --apply; the shell skeleton has a complete header."""
        self.assertNotIn("--apply", scaffold.python_files("read_x", "Read X", False, "read_x.py")["read_x.py"])
        script = scaffold.shell_files("read_x", "Read X", False, "read_x.sh")["read_x.sh"]
        self.assertEqual(script_headers.missing_parts(script, ".sh"), [])
        self.assertIn("shift", script)

    def test_bad_name_refused(self) -> None:
        """A name that is not snake_case exits 2."""
        self.assertEqual(scaffold.main(["--lang", "python", "--name", "Bad-Name", "--summary", "x"]), 2)


if __name__ == "__main__":
    unittest.main()
