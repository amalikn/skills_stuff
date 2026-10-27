"""Tests for scripts/adoption/adopt_code_map.py: a code map is created only for a project with code, extended only with unlisted scripts, never changes a
decision, and what it writes loads under skill-coder's reader.

Run: `just test` (unittest).
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def load(name: str):
    """Import a script from its family folder under scripts/ by file name.

    Args:
        name: the module name without `.py`.

    Returns:
        The loaded module.
    """
    spec = importlib.util.spec_from_file_location(name, next(SCRIPTS.glob(f"*/{name}.py")))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


acm = load("adopt_code_map")


def project(files: dict[str, str]) -> Path:
    """A throwaway project folder holding the given files.

    Args:
        files: {relative path: text}.

    Returns:
        The folder (removed when the interpreter exits).
    """
    root = Path(tempfile.mkdtemp())
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text)
    return root


class AdoptCodeMap(unittest.TestCase):
    """Create, extend and leave alone."""

    def test_no_code_no_map(self) -> None:
        """A project with only documents gets no code map."""
        root = project({"README.md": "x"})
        self.assertEqual(acm.main(["--project-root", str(root), "--apply"]), 0)
        self.assertFalse((root / "code-map.toml").exists())

    def test_creates_a_map_that_loads_with_placeholders(self) -> None:
        """Scripts get unreviewed entries, shell and src/ are not listed, the pinned Python is used, and skill-coder's reader accepts it."""
        root = project({".mise.toml": '[tools]\npython = "3.14"\n', "scripts/a.py": "", "scripts/b.sh": "", "src/app/m.py": ""})
        self.assertEqual(acm.main(["--project-root", str(root), "--apply"]), 0)
        data = tomllib.loads((root / "code-map.toml").read_text())
        self.assertEqual(list(data["modules"]), ["scripts/a.py"])
        self.assertTrue(data["modules"]["scripts/a.py"]["reason"].startswith("unreviewed:"))
        self.assertEqual(data["scan"]["python"], "3.14")
        self.assertEqual(data["scan"]["roots"], ["src", "scripts"])
        self.assertNotIn("layers", data)

    def test_extends_without_touching_decisions(self) -> None:
        """A new script is appended; an existing decision and its comment are kept byte for byte; a second run changes nothing."""
        decided = '[scan]\nroots = ["scripts"]\n\n[modules."scripts/a.py"]\nstatus = "project_only"\nreason = "decided"   # kept\n'
        root = project({"scripts/a.py": "", "scripts/new.py": "", "code-map.toml": decided})
        self.assertEqual(acm.main(["--project-root", str(root), "--apply"]), 0)
        text = (root / "code-map.toml").read_text()
        self.assertTrue(text.startswith(decided))
        self.assertIn('[modules."scripts/new.py"]', text)
        acm.main(["--project-root", str(root), "--apply"])
        self.assertEqual((root / "code-map.toml").read_text(), text)

    def test_plan_writes_nothing(self) -> None:
        """Without --apply nothing is written."""
        root = project({"scripts/a.py": ""})
        self.assertEqual(acm.main(["--project-root", str(root)]), 0)
        self.assertFalse((root / "code-map.toml").exists())


if __name__ == "__main__":
    unittest.main()
