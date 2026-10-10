"""Offline tests for scripts/adopt_governed_files.py: it adds only what is missing and a second run changes nothing."""

from __future__ import annotations

import importlib.util
import re
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


    def test_a_project_without_check_gets_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "justfile").write_text('py := "python3"\n\naudit:\n    @echo audit\n')
            self.assertIn("justfile: check recipe (nothing gates freshness)", [g for g in adopt.justfile_gaps((root / "justfile").read_text()) and
                          ["justfile: " + x for x in adopt.justfile_gaps((root / "justfile").read_text())]])
            text = adopt.fix_justfile((root / "justfile").read_text())
            self.assertRegex(text, r"(?m)^check:\n    @\{\{py\}\} \"\{\{ai_it\}\}/scripts/doc_freshness.py\" --project-root \. --check$")
            self.assertEqual(adopt.justfile_gaps(text), [])

    def test_aligned_ai_it_and_missing_require_venv(self):
        text = 'py        := "python3"\nai_it     := "/x"\n\ncheck:\n    @echo c doc_freshness.py\n'
        fixed = adopt.fix_justfile(text)
        self.assertEqual(len(re.findall(r"(?m)^ai_it\s*:=", fixed)), 1)
        self.assertNotIn("_require-venv", fixed)

    def test_new_recipes_reuse_the_projects_interpreter(self):
        text = ('ai_py := "/v/bin/python"\nai_it := "/x"\n\ncheck:\n    @{{ai_py}} "{{ai_it}}/scripts/doc_freshness.py" --check\n'
                'rotate *ARGS:\n    @{{ai_py}} "{{ai_it}}/scripts/rotate_records.py" {{ARGS}}\n')
        fixed = adopt.fix_justfile(text)
        self.assertIn('@{{ai_py}} "{{ai_it}}/scripts/move_sections.py"', fixed)
        self.assertNotIn("{{py}}", fixed)

    def test_missing_justfile_is_created_and_symlinks_refused(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as other:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("# AGENTS\n")
            self.assertEqual(adopt.main(["--project-root", tmp, "--apply"]), 0)
            self.assertEqual(adopt.justfile_gaps((root / "justfile").read_text()), [])
            (Path(other) / "SCRATCHPAD.md").write_text("# s\n")
            (root / "SCRATCHPAD.md").symlink_to(Path(other) / "SCRATCHPAD.md")
            self.assertEqual(adopt.main(["--project-root", tmp, "--apply"]), 1)

    def test_added_recipes_are_documented_in_scripts_readme(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts" / "README.md").write_text("# Scripts\n\n| `just stale` | x |\n")
            (root / "justfile").write_text('py := "python3"\n\ncheck:\n    @echo c\n')
            self.assertEqual(adopt.main(["--project-root", tmp, "--apply"]), 0)
            readme = (root / "scripts" / "README.md").read_text()
            for name in ("budget", "move-sections", "history-show", "check"):
                self.assertIn(f"just {name}", readme)
            self.assertEqual(readme.count("just stale"), 1)

    def test_free_text_recipes_take_quoted_arguments(self):
        old = ('py := "python3"\nai_it := "/x"\n\ncheck:\n    @echo c doc_freshness.py\n\n'
               'move-sections *ARGS: _require-venv\n    @{{py}} "{{ai_it}}/scripts/move_sections.py" --project-root . {{ARGS}}\n')
        self.assertIn("free-text recipes take unquoted {{ARGS}}", adopt.justfile_gaps(old))
        fixed = adopt.fix_justfile(old)
        self.assertIn('[positional-arguments]\nmove-sections *ARGS: _require-venv\n    @{{py}} "{{ai_it}}/scripts/move_sections.py" --project-root . "$@"', fixed)
        self.assertIn('[positional-arguments]\nchangelog-entry *ARGS:', fixed)
        self.assertEqual(fixed.count("[positional-arguments]"), 2)
        self.assertEqual(adopt.justfile_gaps(fixed), [])


if __name__ == "__main__":
    unittest.main()
