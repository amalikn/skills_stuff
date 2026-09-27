#!/usr/bin/env python3
"""Fixture tests for stale_refs.py. Stdlib only: `python3 -m unittest discover -s scripts/tests`."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "stale_refs.py"


def write(root: Path, rel: str, text: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


class StaleRefs(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "proj"
        write(self.root, "README.md", "The low-touch group has seven sites.\n")
        write(self.root, "CHANGELOG.md", "## 20260920_1100\n\n- seven sites seeded\n")
        write(self.root, "docs/archive/old.md", "seven sites\n")
        write(self.root, "SCRATCHPAD.md", "# Scratch\n\n## 2026-09-20 session\n\n- seven sites checked\n\n"
                                          "## Current\n\n- nine sites\n")
        write(self.root, "docs/log.md", "- 2026-09-19 — seven sites, as at that day\n")
        write(self.root, ".ai-context/pack.md", "seven sites\n")
        self.sib = Path(self._tmp.name) / "skill-smc"
        write(self.sib, "references/01_overview.md", "smc_ltp: seven sites\n")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def run_it(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, timeout=60)

    def test_classes_and_exit(self) -> None:
        r = self.run_it("--root", str(self.root), "--old", "seven sites", "--json")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        d = json.loads(r.stdout)
        by = {h["file"]: h["class"] for h in d["hits"]}
        self.assertEqual(by["README.md"], "active")
        self.assertEqual(by["CHANGELOG.md"], "history-path")
        self.assertEqual(by["docs/archive/old.md"], "history-path")
        self.assertEqual(by["SCRATCHPAD.md"], "history-dated")
        self.assertEqual(by["docs/log.md"], "history-dated")
        self.assertEqual(by[".ai-context/pack.md"], "generated")
        self.assertEqual(d["counts"]["active"], 1)

    def test_superseded_dated_report_is_history(self) -> None:
        write(self.root, "README.md", "nine sites\n")
        write(self.root, "docs/reports/r-20260920_1100.md",
              "# Report\n\n> **Superseded 2026-09-27** by the nine-site seeding; the count below is history.\n\nWe have seven sites.\n")
        r = self.run_it("--root", str(self.root), "--old", "seven sites", "--json")
        by = {h["file"]: h["class"] for h in json.loads(r.stdout)["hits"]}
        self.assertEqual(by["docs/reports/r-20260920_1100.md"], "history-superseded")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_live_doc_that_supersedes_another_stays_active(self) -> None:
        write(self.root, "README.md", "nine sites\n")
        write(self.root, "docs/plan.md", "# Plan\n\nThis plan supersedes the earlier one.\n\nWe have seven sites.\n")
        r = self.run_it("--root", str(self.root), "--old", "seven sites", "--json")
        by = {h["file"]: h["class"] for h in json.loads(r.stdout)["hits"]}
        self.assertEqual(by["docs/plan.md"], "active")

    def test_sibling_root_is_swept(self) -> None:
        write(self.root, "README.md", "nine sites\n")
        r = self.run_it("--root", str(self.root), "--also", str(self.sib), "--old", "seven sites", "--json")
        d = json.loads(r.stdout)
        active = [h for h in d["hits"] if h["class"] == "active"]
        self.assertEqual([h["root"] for h in active], [str(self.sib.resolve())])
        self.assertEqual(r.returncode, 1)

    def test_clean_when_only_history(self) -> None:
        write(self.root, "README.md", "nine sites\n")
        r = self.run_it("--root", str(self.root), "--old", "seven sites")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("history-path", r.stdout)


if __name__ == "__main__":
    unittest.main()
