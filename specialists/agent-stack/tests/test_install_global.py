"""Tests for Agent Stack's symlink-only global installer."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "install_global.py"
SPEC = importlib.util.spec_from_file_location("install_global", SCRIPT)
assert SPEC and SPEC.loader
INSTALL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSTALL)


class GlobalInstallTests(unittest.TestCase):
    """Verify the global installer preserves existing client content."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.home = Path(self.temp.name) / "home"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def installed_links(self) -> dict[Path, Path]:
        return INSTALL.selected_links(self.home, clients={"claude", "codex", "agents"})

    def test_inventory_includes_orchestrator_persona_and_skill(self) -> None:
        targets = INSTALL.expected_links(self.home)

        self.assertIn(self.home / ".claude/agents/orchestrator-follett.md", targets)
        self.assertIn(self.home / ".claude/skills/orchestrator", targets)
        self.assertIn(self.home / ".codex/skills/orchestrator", targets)
        self.assertIn(self.home / ".agents/skills/orchestrator", targets)
        self.assertIn(self.home / ".claude/skills/skill-slurp-chat", targets)
        self.assertIn(self.home / ".codex/skills/skill-project-coherence", targets)

    def test_dry_run_changes_nothing(self) -> None:
        expected = self.installed_links()

        result = INSTALL.install(self.home, clients={"claude", "codex", "agents"}, dry_run=True)

        self.assertEqual(set(expected), set(result["would_create"]))
        self.assertFalse(any(path.exists() or path.is_symlink() for path in expected))

    def test_install_creates_only_expected_symlinks(self) -> None:
        expected = self.installed_links()

        result = INSTALL.install(self.home, clients={"claude", "codex", "agents"})

        self.assertTrue(all(path.is_symlink() for path in expected))
        self.assertEqual({path.resolve() for path in expected}, {source.resolve() for source in expected.values()})
        self.assertEqual(set(expected), set(result["created"]))
        self.assertEqual([], result["would_create"])

    def test_install_is_idempotent(self) -> None:
        INSTALL.install(self.home, clients={"claude", "codex", "agents"})

        result = INSTALL.install(self.home, clients={"claude", "codex", "agents"})

        self.assertEqual([], result["created"])
        self.assertEqual([], result["collisions"])

    def test_collision_blocks_all_selected_targets(self) -> None:
        expected = self.installed_links()
        collision = next(iter(expected))
        collision.parent.mkdir(parents=True)
        collision.write_text("keep", encoding="utf-8")

        with self.assertRaisesRegex(INSTALL.CollisionError, str(collision)):
            INSTALL.install(self.home, clients={"claude", "codex", "agents"})

        self.assertFalse(any(path.is_symlink() for path in expected))
        self.assertEqual("keep", collision.read_text(encoding="utf-8"))

    def test_uninstall_removes_only_owned_symlinks(self) -> None:
        expected = self.installed_links()
        INSTALL.install(self.home, clients={"claude", "codex", "agents"})

        result = INSTALL.uninstall(self.home, clients={"claude", "codex", "agents"})

        self.assertEqual(set(expected), set(result["removed"]))
        self.assertFalse(any(path.exists() or path.is_symlink() for path in expected))

    def test_uninstall_preserves_unexpected_target(self) -> None:
        expected = INSTALL.expected_links(self.home)
        target = next(iter(expected))
        target.parent.mkdir(parents=True)
        target.write_text("keep", encoding="utf-8")

        result = INSTALL.uninstall(self.home, clients={"claude", "codex", "agents"})

        self.assertIn(target, result["preserved"])
        self.assertEqual("keep", target.read_text(encoding="utf-8"))

    def test_existing_global_skill_creator_can_be_excluded(self) -> None:
        existing = self.home / ".codex/skills/skill-creator"
        existing.parent.mkdir(parents=True)
        existing.write_text("keep", encoding="utf-8")

        INSTALL.install(self.home, clients={"claude", "codex", "agents"})

        self.assertEqual("keep", existing.read_text(encoding="utf-8"))
        self.assertTrue((self.home / ".codex/skills/orchestrator").is_symlink())
        self.assertTrue((self.home / ".agents/skills/orchestrator").is_symlink())

    def test_explicit_include_restores_a_default_exclusion(self) -> None:
        skill_creator = self.home / ".codex/skills/skill-creator"

        INSTALL.install(self.home, clients={"codex"}, include={"skill-creator"})

        self.assertTrue(skill_creator.is_symlink())

    def test_install_refuses_a_noncanonical_worktree(self) -> None:
        canonical = Path("/canonical/specialists/agent-stack")

        with mock.patch.object(INSTALL, "canonical_install_root", return_value=canonical):
            with self.assertRaisesRegex(ValueError, "canonical checkout"):
                INSTALL.require_canonical_checkout()

    def test_cli_dry_run_refuses_a_noncanonical_worktree(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--dry-run", "--home", str(self.home)],
            cwd=SCRIPT.parent.parent,
            check=False,
            capture_output=True,
            text=True,
        )

        is_secondary_worktree = SCRIPT.parent.parent.resolve() != INSTALL.canonical_install_root()
        self.assertEqual(2 if is_secondary_worktree else 0, completed.returncode)
        if is_secondary_worktree:
            self.assertIn("canonical checkout", completed.stderr)
        else:
            self.assertIn("would_create", completed.stdout)

    def test_cli_requires_an_explicit_action(self) -> None:
        with mock.patch.object(sys, "argv", [str(SCRIPT)]):
            with mock.patch.object(INSTALL, "install") as install:
                with self.assertRaisesRegex(ValueError, "Choose one action"):
                    INSTALL.main()
        install.assert_not_called()

    def test_frontend_adapter_directory_collision_blocks_all_targets(self) -> None:
        expected = self.installed_links()
        adapter = self.home / ".claude/skills/frontend-design"
        adapter.mkdir(parents=True)
        (adapter / "local.md").write_text("keep", encoding="utf-8")

        with self.assertRaisesRegex(INSTALL.CollisionError, str(adapter)):
            INSTALL.install(self.home, clients={"claude", "codex", "agents"})

        self.assertFalse(any(path.is_symlink() for path in expected))
        self.assertEqual("keep", (adapter / "local.md").read_text(encoding="utf-8"))

    def test_empty_frontend_adapter_directory_is_reused(self) -> None:
        adapter = self.home / ".claude/skills/frontend-design"
        adapter.mkdir(parents=True)

        INSTALL.install(self.home, clients={"claude"})

        self.assertTrue((adapter / "SKILL.md").is_symlink())


if __name__ == "__main__":
    unittest.main()
