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
            self.assertIn("\ngovern:", first["justfile"])  # 2026-10-14: one-step governance reaches every adopted project
            self.assertIn("Open items tracker:", first["SCRATCHPAD.md"])
            self.assertEqual(adopt.main(["--project-root", tmp]), 0)
            self.assertEqual(adopt.main(["--project-root", tmp, "--apply"]), 0)
            self.assertEqual(first, {p: (root / p).read_text() for p in first})


    def test_roadmap_gets_budget_and_rotate_trims_it(self):
        # 2026-10-14: ROADMAP had no budget and only UNC trimmed it; a project with ROADMAP.md gets both, once.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "justfile").write_text('py := "python3"\nai_it := "/x"\n\ncheck:\n    @{{py}} "{{ai_it}}/scripts/doc_freshness.py" --check\n\n'
                                           'rotate *ARGS:\n    @{{py}} "{{ai_it}}/scripts/rotate_records.py" --project-root . {{ARGS}} CHANGELOG.md\n')
            (root / "AGENTS.md").write_text("# AGENTS\n")
            (root / "ROADMAP.md").write_text("# Roadmap\n\n## Current phase\n\n- [ ] x\n")
            self.assertIn("rotate does not trim ROADMAP", adopt.justfile_gaps((root / "justfile").read_text(), roadmap=True))
            self.assertEqual(adopt.main(["--project-root", tmp, "--apply"]), 0)
            just, roadmap = (root / "justfile").read_text(), (root / "ROADMAP.md").read_text()
            self.assertEqual(just.count("roadmap_trim.py"), 1)
            self.assertIn('    @{{py}} "{{ai_it}}/scripts/roadmap_trim.py" --project-root . {{ARGS}}', just)
            for key in ("Kind: roadmap", "Budget: 200 lines", "Archive:", "Last reviewed:"):
                self.assertIn(key, roadmap)
            self.assertEqual(adopt.main(["--project-root", tmp, "--apply"]), 0)
            self.assertEqual((just, roadmap), ((root / "justfile").read_text(), (root / "ROADMAP.md").read_text()))

    def test_no_roadmap_no_roadmap_gap(self):
        text = 'rotate *ARGS:\n    @{{py}} "{{ai_it}}/scripts/rotate_records.py" {{ARGS}}\n'
        self.assertNotIn("rotate does not trim ROADMAP", adopt.justfile_gaps(text))
        self.assertNotIn("roadmap_trim", adopt.fix_justfile(text))

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
        self.assertEqual(fixed.count("[positional-arguments]"), 4)  # changelog-entry, move-sections, outline, section
        self.assertEqual(adopt.justfile_gaps(fixed), [])

    def test_added_recipes_keep_their_comment_and_attribute(self):
        """A recipe copied from the template keeps its comment and `[positional-arguments]` (lost before 2026-10-11, so `"$@"` was empty)."""
        recipes = adopt.split_recipes(adopt.template_recipes())
        for name in ("outline", "section", "changelog-entry"):
            self.assertRegex(recipes[name], rf"^# .+\n\[positional-arguments\]\n{name} \*ARGS:")
        fixed = adopt.fix_justfile('py := "python3"\nai_it := "/x"\n\ncheck:\n    @echo c doc_freshness.py\n')
        self.assertIn('[positional-arguments]\noutline *ARGS:', fixed)
        self.assertEqual(fixed.count("[positional-arguments]\n[positional-arguments]"), 0)

    def test_root_files_get_front_matter_and_roles_gate(self):
        """2026-10-14: 12 of 13 governed projects had root files without `---` front matter, AGENTS.md's legacy block unfenced under an import."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "justfile").write_text('py := "python3"\n\ncheck:\n    @{{py}} scripts/check_governance.py\n')
            (root / "AGENTS.md").write_text("@../AGENTS.md\n\nTitle: P Agent Policy\nCategory: agent-governance-guide\nSummary: Rules.\n\n# AGENTS.md\n\n- rule\n")
            (root / "README.md").write_text("# Proj\n\nWhat this project does, in one paragraph.\n\n## Folder index\n\n- docs/\n")
            self.assertEqual(adopt.main(["--project-root", tmp, "--apply"]), 0)
            agents = (root / "AGENTS.md").read_text()
            self.assertTrue(agents.startswith("---\nTitle: P Agent Policy\n"))
            self.assertIn("\n---\n\n@../AGENTS.md\n\n# AGENTS.md", agents)
            readme = (root / "README.md").read_text()
            self.assertIn("Summary: What this project does, in one paragraph.", readme)
            self.assertIn("Budget: 200 lines", readme)
            self.assertIn("Review by:", readme)
            self.assertIn("role_check.py", (root / "justfile").read_text())
            self.assertTrue((root / "scripts" / "role-check-baseline.json").is_file())
            first = {p: (root / p).read_text() for p in ("AGENTS.md", "README.md", "justfile")}
            self.assertEqual(adopt.main(["--project-root", tmp, "--apply"]), 0)
            self.assertEqual(first, {p: (root / p).read_text() for p in first})

    def test_header_growth_does_not_fail_the_budget_ratchet(self):
        """cambium-swap, 2026-10-14: fencing an over-budget AGENTS.md added two lines and failed `just check` until adoption re-recorded its size."""
        import json
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", tmp], check=True)
            (root / "justfile").write_text('py := "python3"\n\ncheck:\n    @echo c\n')
            (root / "AGENTS.md").write_text("@../AGENTS.md\n\nTitle: P\nSummary: Rules.\n\n# AGENTS.md\n\n" + "- rule\n" * 210)
            subprocess.run(["git", "-C", tmp, "add", "-A"], check=True)
            freshness = [sys.executable, str(SCRIPT.parent / "doc_freshness.py"), "--project-root", tmp]
            subprocess.run(freshness + ["--write-baseline"], check=True, capture_output=True)
            self.assertEqual(adopt.main(["--project-root", tmp, "--apply"]), 0)
            self.assertTrue((root / "AGENTS.md").read_text().startswith("---\n"))
            self.assertEqual(subprocess.run(freshness + ["--check"], capture_output=True).returncode, 0)
            self.assertIn("over-budget:AGENTS.md", json.loads((root / "scripts" / "doc-freshness-baseline.json").read_text()))

    def test_outdated_govern_copy_is_refreshed_and_skill_form_left_alone(self):
        """cambium-swap, 2026-10-14: an older `govern` copy printed a blank reason; adoption refreshes the project form only."""
        old = 'py := "python3"\nai_it := "/x"\n\ncheck:\n    @echo c doc_freshness.py role_check.py\n\n# old\ngovern:\n    @echo old\n'
        self.assertIn("recipe govern outdated", adopt.justfile_gaps(old))
        fixed = adopt.fix_justfile(old)
        self.assertNotIn("@echo old", fixed)
        self.assertIn("audit: (LOST", fixed)
        self.assertEqual(adopt.outdated_recipes(fixed), [])
        skill_form = 'py := "python3"\n\ngovern project=".":\n    @echo mine\n'
        self.assertEqual(adopt.outdated_recipes(skill_form), [])

    def test_written_header_is_valid_yaml(self):
        """A summary taken from prose may hold `: `; the written header must still parse (smc-resiliency, 2026-10-14)."""
        import yaml
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Proj\n\nThis project does one thing: it routes # packets.\n\n## Folder index\n")
            adopt.fix_header(root, "README.md")
            text = (root / "README.md").read_text()
            head = yaml.safe_load(text[4:text.index("\n---", 4)])
            self.assertEqual(head["Summary"], "This project does one thing: it routes # packets.")

    def test_prose_key_lines_are_not_a_legacy_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SETUP.md").write_text("Note: read this first.\n\n# Setup\n\nInstall the tools.\n")
            adopt.fix_header(root, "SETUP.md")
            text = (root / "SETUP.md").read_text()
            self.assertIn("\n---\n\nNote: read this first.\n", text)
            self.assertIn("Title: Setup", text)

    def test_legacy_folded_value_stays_inside_the_fence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("@../AGENTS.md\n\nTitle: Policy\nSummary: >- First line\n  second line.\n\n# AGENTS.md\n\nRules.\n")
            adopt.fix_header(root, "AGENTS.md")
            text = (root / "AGENTS.md").read_text()
            self.assertIn("Summary: >- First line\n  second line.\n", text.split("\n---\n", 1)[0])
            self.assertIn("\n---\n\n@../AGENTS.md\n\n# AGENTS.md\n", text)

    def test_future_deadline_is_not_the_review_date(self):
        # 2026-10-14: enterprise-strategy SCRATCHPAD got its 25 Oct deadline as Last reviewed; only dates up to today count.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SCRATCHPAD.md"
            path.write_text("# Scratchpad\n\n- done 2020-01-02\n- due 2099-12-31\n")
            adopt.fix_record(path, "state", "20200102_0000")
            self.assertIn("Last reviewed: 2020-01-02", path.read_text())


if __name__ == "__main__":
    unittest.main()
