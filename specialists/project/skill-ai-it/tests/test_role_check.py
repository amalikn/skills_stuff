"""Offline tests for scripts/checks/role_check.py: every rule fails on a breach and passes on a project that keeps to the roles."""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "checks" / "role_check.py"
_spec = importlib.util.spec_from_file_location("role_check", SCRIPT)
rc = importlib.util.module_from_spec(_spec)
sys.modules["role_check"] = rc
_spec.loader.exec_module(rc)

TODAY = dt.date(2026, 10, 14)
FM = "---\nTitle: T\nSummary: S\n---\n\n"
GOOD = {
    "README.md": FM + "# P\n\n## Purpose\n\nWhat it is.\n\n## Quick start\n\n`just bootstrap`\n",
    "AGENTS.md": FM + "# AGENTS\n\n## Working rules\n\n- Run `just check`.\n",
    "CLAUDE.md": "@AGENTS.md\n\n## Claude-specific additions\n\nNone.\n",
    "ROADMAP.md": FM + "# Roadmap\n\n## Current phase\n\n**2026-10-14.** Building.\n\n## Area\n\n- [ ] Next thing\n\n## Completed\n\n"
                  "Done items move to `docs/history/roadmap-*.md` (`just rotate`;\nfind one with `just history <term>`).\n",
}
LONG = "This paragraph describes the managed block format in enough words to be compared, and it is long enough to pass the floor. " * 2


def project(tmp: str, files: dict[str, str]) -> Path:
    """Write a project with the given root files.

    Args:
        tmp: the directory.
        files: name to text.

    Returns:
        The project root.
    """
    root = Path(tmp)
    for name, text in files.items():
        (root / name).write_text(text)
    return root


class RoleCheckTest(unittest.TestCase):
    """Each rule can fail; a compliant project is clean; the baseline excuses only what it records."""

    def test_compliant_project_is_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(rc.findings(project(tmp, GOOD), TODAY), {})

    def test_each_rule_fails(self):
        cases = {
            "front-matter:AGENTS.md": {"AGENTS.md": "@../AGENTS.md\n\nTitle: A\nSummary: S\n\n# AGENTS\n"},
            "claude-import:CLAUDE.md": {"CLAUDE.md": "# Claude\n\n@AGENTS.md\n"},
            "readme-quick-start:README.md": {"README.md": FM + "# P\n\n## Purpose\n\nWhat it is.\n"},
            "readme-history:README.md": {"README.md": GOOD["README.md"] + "\n## Status — 2026-09-14\n\nDone a thing.\n"},
            "roadmap-phase:ROADMAP.md": {"ROADMAP.md": FM + "# Roadmap\n\n## Current phase\n\nBuilding.\n"},
            "roadmap-done:ROADMAP.md": {"ROADMAP.md": GOOD["ROADMAP.md"] + "\n### Phase 1 (2026-05-22)\n\nBuilt it.\n"},
        }
        for key, override in cases.items():
            with self.subTest(key), tempfile.TemporaryDirectory() as tmp:
                self.assertIn(key, rc.findings(project(tmp, GOOD | override), TODAY))

    def test_front_matter_must_parse_as_yaml(self):
        """2026-10-14: `Scope: ... apn: what` and `Summary: >- text` passed the key check but are not YAML."""
        for bad in ("---\nTitle: T\nScope: a: b\nSummary: S\n---\n\n# A\n", "---\nTitle: T\nSummary: >- text\n  more\n---\n\n# A\n"):
            with self.subTest(bad[:30]), tempfile.TemporaryDirectory() as tmp:
                self.assertIn("front-matter:AGENTS.md", rc.findings(project(tmp, GOOD | {"AGENTS.md": bad}), TODAY))

    def test_old_done_item_fails_and_recent_one_does_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = GOOD["ROADMAP.md"].replace("- [ ] Next thing", "- [ ] Next thing\n- [x] Shipped 2026-09-01")
            self.assertIn("roadmap-done:ROADMAP.md", rc.findings(project(tmp, GOOD | {"ROADMAP.md": old}), TODAY))
        with tempfile.TemporaryDirectory() as tmp:
            new = GOOD["ROADMAP.md"].replace("- [ ] Next thing", "- [ ] Next thing\n- [x] Shipped 2026-10-12")
            self.assertNotIn("roadmap-done:ROADMAP.md", rc.findings(project(tmp, GOOD | {"ROADMAP.md": new}), TODAY))

    def test_duplicate_section_across_root_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            files = GOOD | {"README.md": GOOD["README.md"] + f"\n## Managed block behavior\n\n{LONG}\n",
                            "ARCHITECTURE.md": FM + f"# Arch\n\n## Managed block behavior\n\n{LONG}\n"}
            self.assertTrue(any(k.startswith("duplicate-section:") for k in rc.findings(project(tmp, files), TODAY)))

    def test_context_map_must_parse_without_repeated_keys(self):
        """2026-10-14: a `: ` inside a plain scalar broke context-map.yaml and `just check` passed."""
        cases = {"broken": "a: b\n  description: x: y\n", "repeated": "audit_checks: 1\nrouting: 2\naudit_checks: 3\n"}
        for name, text in cases.items():
            with self.subTest(name), tempfile.TemporaryDirectory() as tmp:
                self.assertIn("context-map-parse:context-map.yaml", rc.findings(project(tmp, GOOD | {"context-map.yaml": text}), TODAY))
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(rc.findings(project(tmp, GOOD | {"context-map.yaml": "version: 1\nrouting:\n  a: [b]\n"}), TODAY), {})

    def test_load_cost_follows_imports_once(self):
        """The always-loaded set is CLAUDE.md, AGENTS.md, what they import (each once) and AI_NAVIGATION.md."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "proj"
            root.mkdir()
            (Path(tmp) / "AGENTS.md").write_text("parent rules\n")
            project(str(root), {"CLAUDE.md": "@AGENTS.md\n", "AGENTS.md": FM + "@../AGENTS.md\n# A\n", "AI_NAVIGATION.md": "nav\n"})
            names = [Path(p).relative_to(Path(tmp).resolve()).as_posix() for p, _ in rc.load_cost(root)]
            self.assertEqual(names, ["proj/CLAUDE.md", "proj/AGENTS.md", "AGENTS.md", "proj/AI_NAVIGATION.md"])

    def test_check_fails_only_on_unbaselined_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = project(tmp, GOOD | {"README.md": FM + "# P\n\n## Purpose\n\nWhat it is.\n"})
            self.assertEqual(rc.main(["--project-root", tmp, "--check"]), 1)
            self.assertEqual(rc.main(["--project-root", tmp, "--write-baseline"]), 0)
            self.assertEqual(rc.main(["--project-root", tmp, "--check"]), 0)
            self.assertIn("readme-quick-start:README.md", json.loads((root / rc.BASELINE).read_text()))


if __name__ == "__main__":
    unittest.main()
