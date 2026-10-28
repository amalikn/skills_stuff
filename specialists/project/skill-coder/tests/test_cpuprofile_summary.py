"""Offline tests for scripts/cpuprofile_summary.py on a hand-built profile: attribution by extension, stacks of the studied extension, CLI exit codes.

Run: `just test` (unittest, the project's pinned interpreter).
"""

from __future__ import annotations

import importlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

cps = importlib.import_module("cpuprofile_summary")

FOAM = "file:///x/.vscode/extensions/foam.foam-vscode-0.46.0/out/bundles/extension-node.js"
CORE = "file:///Applications/Code.app/out/vs/workbench/api/node/extensionHostProcess.js"


def _profile() -> dict:
    """A profile where root -> getUris (foam) -> find (foam) holds 90 ms and a core frame holds 10 ms.

    Returns:
        The parsed-JSON shape of a .cpuprofile.
    """
    def node(i: int, fn: str, url: str, kids: list[int]) -> dict:
        """One profile node.

        Args:
            i: node id.
            fn: function name.
            url: script URL.
            kids: child node ids.

        Returns:
            The node dict.
        """
        return {"id": i, "callFrame": {"functionName": fn, "url": url, "lineNumber": 5}, "children": kids}

    nodes = [node(1, "(root)", "", [2, 4]), node(2, "getUris", FOAM, [3]), node(3, "find", FOAM, []), node(4, "kd", CORE, [])]
    return {"nodes": nodes, "samples": [3] * 9 + [4], "timeDeltas": [10_000] * 10}


class CpuprofileSummary(unittest.TestCase):
    """The summary attributes time correctly and the CLI reports unreadable files."""

    def test_attribution(self) -> None:
        """Self time lands on the right extension and function; the stack follows the busiest extension."""
        s = cps.summarise(_profile())
        self.assertEqual(s["total_ms"], 100)
        self.assertEqual(s["ext"], "foam.foam-vscode-0.46.0")
        self.assertEqual(s["by_ext"][0], ("foam.foam-vscode-0.46.0", 90.0))
        self.assertIn(("core", 10.0), s["by_ext"])
        self.assertEqual(s["by_stack"], [("find:5 <- getUris:5", 90.0)])

    def test_ext_override(self) -> None:
        """--ext picks the studied extension; one with no frames gives no stacks."""
        self.assertEqual(cps.summarise(_profile(), ext="no.such-ext")["by_stack"], [])

    def test_cli(self) -> None:
        """Exit 0 on a good profile, 1 when a file is missing or not JSON."""
        tmp = Path(tempfile.mkdtemp())
        good, bad = tmp / "good.cpuprofile", tmp / "bad.cpuprofile"
        good.write_text(json.dumps(_profile()), encoding="utf-8")
        bad.write_text("not json", encoding="utf-8")
        self.assertEqual(cps.main([str(good)]), 0)
        self.assertEqual(cps.main([str(good), str(bad)]), 1)
        self.assertEqual(cps.main([str(tmp / "missing.cpuprofile")]), 1)


if __name__ == "__main__":
    unittest.main()
