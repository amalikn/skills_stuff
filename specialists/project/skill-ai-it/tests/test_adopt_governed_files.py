"""Offline tests for scripts/adopt_governed_files.py: it adds only what is missing and a second run changes nothing."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "adopt_governed_files.py"
_spec = importlib.util.spec_from_file_location("adopt_governed_files", SCRIPT)
adopt = importlib.util.module_from_spec(_spec)
sys.modules["adopt_governed_files"] = adopt
_spec.loader.exec_module(adopt)


class AdoptTest(unittest.TestCase):
    """Adoption on a minimal project is complete, adds no duplicate recipe, and is idempotent."""

    def test_adopt_is_complete_and_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "justfile").write_text('py := "python3"\n\ncheck:\n    @{{py}} scripts/check_governance.py\n\nstale:\n    @echo own\n')
            (root / "AGENTS.md").write_text("# AGENTS\n")
            (root / "SCRATCHPAD.md").write_text("# Scratchpad\n\n## Open items\n\n- [ ] x\n")
            self.assertEqual(adopt.main(["--project-root", tmp, "--apply"]), 0)
            first = {p: (root / p).read_text() for p in ("justfile", "AGENTS.md", "SCRATCHPAD.md")}
            self.assertEqual(first["justfile"].count("\nstale:"), 1)
            self.assertIn("doc_freshness.py", first["justfile"])
            self.assertIn("Open items tracker:", first["SCRATCHPAD.md"])
            self.assertEqual(adopt.main(["--project-root", tmp]), 0)
            self.assertEqual(adopt.main(["--project-root", tmp, "--apply"]), 0)
            self.assertEqual(first, {p: (root / p).read_text() for p in first})


if __name__ == "__main__":
    unittest.main()
