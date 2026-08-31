"""Tests for the conservative Agent Stack upstream comparison workflow."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sync_auto_company.py"
SPEC = importlib.util.spec_from_file_location("sync_auto_company", SCRIPT)
assert SPEC and SPEC.loader
SYNC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNC)


class SyncAutoCompanyTests(unittest.TestCase):
    """Exercise classifications without touching a real upstream checkout."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.target = self.root / "target"
        (self.source / ".claude/agents").mkdir(parents=True)
        (self.source / ".claude/skills/example").mkdir(parents=True)
        (self.target / "personas").mkdir(parents=True)
        (self.target / "skills/example").mkdir(parents=True)
        self.original_root = SYNC.SCRIPT_ROOT
        SYNC.SCRIPT_ROOT = self.target

    def tearDown(self) -> None:
        SYNC.SCRIPT_ROOT = self.original_root
        self.temp.cleanup()

    def add_persona(self, content: str = "English persona\n") -> Path:
        path = self.source / ".claude/agents/example.md"
        path.write_text(content, encoding="utf-8")
        return path

    def state_for(self, relative: str, source_file: Path, canonical_file: Path) -> dict[str, object]:
        return {
            "tracked": {
                relative: {
                    "source_sha256": SYNC.sha256(source_file),
                    "canonical_sha256": SYNC.sha256(canonical_file),
                    "mode": "mirrored",
                }
            }
        }

    def test_unchanged_source_has_no_changes(self) -> None:
        source_file = self.add_persona()
        canonical = self.target / "personas/example.md"
        canonical.write_text(source_file.read_text(encoding="utf-8"), encoding="utf-8")

        changes, unresolved = SYNC.classify(SYNC.source_files(self.source), self.state_for("personas/example.md", source_file, canonical))

        self.assertEqual([], changes)
        self.assertEqual([], unresolved)

    def test_english_change_is_safe_when_canonical_is_unchanged(self) -> None:
        source_file = self.add_persona("First English version\n")
        canonical = self.target / "personas/example.md"
        canonical.write_text(source_file.read_text(encoding="utf-8"), encoding="utf-8")
        state = self.state_for("personas/example.md", source_file, canonical)
        source_file.write_text("Updated English source\n", encoding="utf-8")

        changes, unresolved = SYNC.classify(SYNC.source_files(self.source), state)

        self.assertEqual("safe_replace", changes[0]["classification"])
        self.assertEqual([], unresolved)

    def test_non_english_change_requires_translation(self) -> None:
        source_file = self.add_persona("First English version\n")
        canonical = self.target / "personas/example.md"
        canonical.write_text("Translated English version\n", encoding="utf-8")
        state = self.state_for("personas/example.md", source_file, canonical)
        state["tracked"]["personas/example.md"]["mode"] = "translated"
        source_file.write_text("Updated English source\n", encoding="utf-8")

        changes, unresolved = SYNC.classify(SYNC.source_files(self.source), state)

        self.assertEqual("translation_required", changes[0]["classification"])
        self.assertEqual(["personas/example.md"], unresolved)

    def test_non_latin_letters_require_translation(self) -> None:
        source_file = self.add_persona("English source\n")
        source_file.write_text(f"{chr(0x03B2)} source update\n", encoding="utf-8")

        self.assertTrue(SYNC.contains_non_english_script(source_file))

    def test_untracked_local_file_requires_manual_merge(self) -> None:
        source_file = self.add_persona("New English source\n")
        canonical = self.target / "personas/example.md"
        canonical.write_text("Local edit\n", encoding="utf-8")

        changes, unresolved = SYNC.classify(SYNC.source_files(self.source), {"tracked": {}})

        self.assertEqual("manual_merge", changes[0]["classification"])
        self.assertEqual(["personas/example.md"], unresolved)

    def test_removed_upstream_file_requires_review(self) -> None:
        canonical = self.target / "personas/example.md"
        canonical.write_text("Existing English file\n", encoding="utf-8")
        state = {
            "tracked": {
                "personas/example.md": {
                    "source_sha256": "previous-source",
                    "canonical_sha256": SYNC.sha256(canonical),
                    "mode": "mirrored",
                }
            }
        }

        changes, unresolved = SYNC.classify(SYNC.source_files(self.source), state)

        self.assertEqual("remove_review", changes[0]["classification"])
        self.assertEqual(["personas/example.md"], unresolved)

    def test_canonical_divergence_requires_manual_merge(self) -> None:
        source_file = self.add_persona("First English version\n")
        canonical = self.target / "personas/example.md"
        canonical.write_text(source_file.read_text(encoding="utf-8"), encoding="utf-8")
        state = self.state_for("personas/example.md", source_file, canonical)
        canonical.write_text("Local editorial improvement\n", encoding="utf-8")
        source_file.write_text("Updated English source\n", encoding="utf-8")

        changes, unresolved = SYNC.classify(SYNC.source_files(self.source), state)

        self.assertEqual("manual_merge", changes[0]["classification"])
        self.assertEqual(["personas/example.md"], unresolved)

    def test_apply_copies_only_safe_changes(self) -> None:
        source_file = self.add_persona("New English source\n")
        changes = [{"path": "personas/example.md", "classification": "safe_add", "upstream_sha256": SYNC.sha256(source_file)}]

        applied = SYNC.apply_safe_changes(SYNC.source_files(self.source), changes)

        self.assertEqual(["personas/example.md"], applied)
        self.assertEqual("New English source\n", (self.target / "personas/example.md").read_text(encoding="utf-8"))

    def test_state_json_is_stable(self) -> None:
        destination = self.root / "state.json"
        SYNC.write_json(destination, {"b": 2, "a": 1})

        self.assertEqual({"a": 1, "b": 2}, json.loads(destination.read_text(encoding="utf-8")))

    def test_fetch_checks_out_the_fetched_branch_revision(self) -> None:
        remote = self.root / "remote"
        mirror = self.root / "mirror"
        subprocess.run(["git", "init", "--initial-branch", "main", str(remote)], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=remote, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Agent Stack Test"], cwd=remote, check=True, capture_output=True)
        (remote / ".claude/agents").mkdir(parents=True)
        (remote / ".claude/skills/example").mkdir(parents=True)
        (remote / ".claude/agents/example.md").write_text("First version\n", encoding="utf-8")
        (remote / ".claude/skills/example/SKILL.md").write_text("First skill\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=remote, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=remote, check=True, capture_output=True)
        SYNC.prepare_mirror(mirror, str(remote), "main", fetch=True)
        (remote / ".claude/agents/example.md").write_text("Second version\n", encoding="utf-8")
        subprocess.run(["git", "commit", "-am", "update"], cwd=remote, check=True, capture_output=True)

        SYNC.prepare_mirror(mirror, str(remote), "main", fetch=True)

        self.assertEqual(SYNC.run_git(["rev-parse", "origin/main"], mirror), SYNC.run_git(["rev-parse", "HEAD"], mirror))
        self.assertEqual("Second version\n", (mirror / ".claude/agents/example.md").read_text(encoding="utf-8"))

    def test_record_current_rejects_agent_stack_as_upstream_source(self) -> None:
        with self.assertRaisesRegex(ValueError, "inside Agent Stack"):
            SYNC.record_current(self.target, {"tracked": {}})


if __name__ == "__main__":
    unittest.main()
