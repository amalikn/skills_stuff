"""Offline tests for import_layers.py's graph report: `:self` roots, edge counts per import statement, name-ordered fan-in ties and --json
(added 2026-10-19 so unified-network-controller's scripts/checks/import_graph.py could retire; its report is reproduced field for field).

Run: `just test` (unittest, the pack's venv). The scripts folder is put on sys.path, as a consuming project does.
"""

from __future__ import annotations

import contextlib
import importlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import_layers = importlib.import_module("import_layers")


def _tree(files: dict[str, str]) -> Path:
    """Write files into a temporary folder, removed at exit.

    Args:
        files: {relative path: content}.

    Returns:
        The folder.
    """
    tmp = tempfile.TemporaryDirectory()
    unittest.addModuleCleanup(tmp.cleanup)
    root = Path(tmp.name)
    for rel, body in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(body, encoding="utf-8")
    return root


class GraphReport(unittest.TestCase):
    """The package-level import report."""

    def test_self_root_keeps_its_folder_name(self) -> None:
        """A root ending :self names its modules from the project root, so a folder of loose scripts is one package."""
        root = _tree({"tools/a.py": "", "tools/sub/b.py": "", "lib/pkg/c.py": ""})
        self.assertEqual(sorted(import_layers.module_map(root, ["lib", "tools:self"])), ["pkg.c", "tools.a", "tools.sub.b"])

    def test_graph_report_counts_statements_and_orders_ties(self) -> None:
        """Cross-package edges count each import statement; equal fan-in is ordered by name; --json gives the same data."""
        root = _tree({
            "lib/core/__init__.py": "", "lib/core/m.py": "", "lib/core/n.py": "",
            "lib/web/__init__.py": "",
            "lib/web/v.py": "import core.n\nimport core.m\ndef f():\n    import core.m\n",
            "tools/run.py": "import sys\nsys.path.insert(0, 'lib')\nimport core.n\nif __name__ == \"__main__\":\n    pass\n",
        })
        mods = import_layers.module_map(root, ["lib", "tools:self"])
        result = import_layers.analyse(root, mods, import_layers.graph(mods))
        self.assertEqual(result["edges"], [{"from": "tools", "to": "core", "count": 1}, {"from": "web", "to": "core", "count": 3}])
        self.assertEqual(result["fan_in"], [["core.n", 2], ["core.m", 1]])
        self.assertEqual((result["entry_points"], result["sys_path"]), ({"tools": 1}, ["tools/run.py"]))
        args = ["--project-root", str(root), "--graph", "--roots", "lib,tools:self"]
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(import_layers.main(args + ["--json"]), 0)
        self.assertEqual(json.loads(out.getvalue())["edges"], result["edges"])
        with contextlib.redirect_stdout(io.StringIO()) as out:
            import_layers.main(args)
        self.assertIn("  web -> core: 3", out.getvalue())



if __name__ == "__main__":
    unittest.main()
