# Agent Stack Orchestrator and Global Install Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the Follett Orchestrator and install the complete Agent Stack globally through safe, symlink-only client links.

**Architecture:** Canonical material lives only under `specialists/agent-stack`. A standard-library installer derives its targets from the canonical directories, verifies them against
`manifest.yaml`, preflights all paths, and creates or removes only verifiable Agent Stack symlinks. The Orchestrator is a new skill/persona pair that reuses the manifest and `team` procedure
without autonomous looping or persistent cross-project state.

**Tech Stack:** Markdown, YAML manifest, Python 3.14 standard library, `unittest`, `just`.

---

## Contents

- [Task 1: Define the Orchestrator](#task-1-define-the-orchestrator)
- [Task 2: Implement a symlink-only global installer](#task-2-implement-a-symlink-only-global-installer)
- [Task 3: Document, validate, and install](#task-3-document-validate-and-install)

### Task 1: Define the Orchestrator

**Files:**
- Create: `specialists/agent-stack/personas/orchestrator-follett.md`
- Create: `specialists/agent-stack/skills/orchestrator/SKILL.md`
- Modify: `specialists/agent-stack/manifest.yaml`
- Test: `specialists/agent-stack/tests/test_install_global.py`

- [x] **Step 1: Write the failing inventory test**

```python
def test_inventory_includes_orchestrator_persona_and_skill(self):
    targets = INSTALL.expected_links(self.home)
    self.assertIn(self.home / ".claude/agents/orchestrator-follett.md", targets)
    self.assertIn(self.home / ".claude/skills/orchestrator", targets)
    self.assertIn(self.home / ".codex/skills/orchestrator", targets)
    self.assertIn(self.home / ".agents/skills/orchestrator", targets)
```

- [x] **Step 2: Run the test to verify it fails**

Run: `mise exec -- python -m unittest tests.test_install_global.GlobalInstallTests.test_inventory_includes_orchestrator_persona_and_skill -v`

Expected: FAIL because the global installer module does not yet exist.

- [x] **Step 3: Add the persona, skill, and manifest capabilities**

The persona sets a neutral, human-governed Follett coordination posture. The skill requires task framing, smallest-team selection, bounded passes, evidence labels, disagreement handling, a blocker
check, and one synthesis. Add `orchestrator-follett` as a `persona` and `orchestrator` as a general `package` capability.

- [x] **Step 4: Re-run the focused test**

Run: `mise exec -- python -m unittest tests.test_install_global.GlobalInstallTests.test_inventory_includes_orchestrator_persona_and_skill -v`

Expected: still FAIL because the installer is not yet implemented.

### Task 2: Implement a symlink-only global installer

**Files:**
- Create: `specialists/agent-stack/scripts/install_global.py`
- Create: `specialists/agent-stack/tests/test_install_global.py`
- Modify: `specialists/agent-stack/justfile`

- [x] **Step 1: Write failing safety tests**

```python
def test_dry_run_changes_nothing(self):
    expected = INSTALL.expected_links(self.home)
    result = INSTALL.install(self.home, clients={"claude", "codex"}, dry_run=True)
    self.assertEqual(set(expected), set(result["would_create"]))
    self.assertFalse(any(path.exists() or path.is_symlink() for path in expected))

def test_install_creates_only_expected_symlinks(self):
    expected = INSTALL.expected_links(self.home)
    INSTALL.install(self.home, clients={"claude", "codex"})
    self.assertTrue(all(path.is_symlink() for path in expected))
    self.assertEqual({path.resolve() for path in expected}, set(expected.values()))

def test_collision_blocks_all_selected_targets(self):
    expected = INSTALL.expected_links(self.home)
    collision = next(iter(expected))
    collision.parent.mkdir(parents=True)
    collision.write_text("keep", encoding="utf-8")
    with self.assertRaisesRegex(INSTALL.CollisionError, str(collision)):
        INSTALL.install(self.home, clients={"claude", "codex"})
    self.assertFalse(any(path.is_symlink() for path in expected))

def test_uninstall_removes_only_owned_symlinks(self):
    expected = INSTALL.expected_links(self.home)
    INSTALL.install(self.home, clients={"claude", "codex"})
    INSTALL.uninstall(self.home, clients={"claude", "codex"})
    self.assertFalse(any(path.exists() or path.is_symlink() for path in expected))

def test_uninstall_preserves_unexpected_target(self):
    expected = INSTALL.expected_links(self.home)
    target = next(iter(expected))
    target.parent.mkdir(parents=True)
    target.write_text("keep", encoding="utf-8")
    result = INSTALL.uninstall(self.home, clients={"claude", "codex"})
    self.assertIn(target, result["preserved"])
    self.assertEqual("keep", target.read_text(encoding="utf-8"))
```

Use a temporary `home` directory and assert every destination resolves to its canonical source. Create a regular file at one destination for the collision test and assert no other target was created.

- [x] **Step 2: Run the test module to verify it fails**

Run: `mise exec -- python -m unittest tests.test_install_global -v`

Expected: FAIL with module-not-found for `install_global.py`.

- [x] **Step 3: Implement expected-target derivation and preflight**

`install_global.py` derives entries from the canonical directories: each persona Markdown file maps to `.claude/agents`; each skill directory containing `SKILL.md` maps to `.claude/skills`,
`.codex/skills`, and `.agents/skills`; and the single `frontend-design.md` source maps to a client `frontend-design/SKILL.md` symlink. It validates entries against manifest capability paths, rejects a secondary Git
worktree, supports `--status`, `--dry-run`, `--install`, `--uninstall`, `--client`, and a test-only `--home` override, and creates no content copies.

- [x] **Step 4: Implement atomic install, verification, and owned-link-only uninstall**

Preflight all selected paths before writing. A correct existing symlink is idempotent; any other existing target, including a nonempty frontend adapter directory, is a collision. An empty adapter
directory may be reused. Verify each created link resolves exactly to the canonical source. Uninstall only symlinks whose resolved target equals the expected source, retaining unexpected files and
directories.

- [x] **Step 5: Re-run the test module**

Run: `mise exec -- python -m unittest tests.test_install_global -v`

Expected: PASS.

- [x] **Step 6: Expose guarded `just` commands**

Add `global-status`, `global-dry-run`, `global-install confirm=""`, and `global-uninstall confirm=""`. Install/uninstall recipes reject missing explicit confirmation.

### Task 3: Document, validate, and install

**Files:**
- Modify: `specialists/agent-stack/README.md`
- Modify: `specialists/agent-stack/justfile`
- Modify: `docs/superpowers/specs/2026-09-01-agent-stack-global-install-design.md`
- Create: `docs/superpowers/outcomes/2026-09-01-agent-stack-orchestrator-global-install.md`

- [x] **Step 1: Document global, symlink-only use and Orchestrator invocation**

Replace per-project installation as the default with global `just` commands. State that `orchestrator` is opt-in, does not run in the background, and project-local governance wins.

- [ ] **Step 2: Run the complete suite and non-mutating real-home preview**

Run: `just test` and `just global-dry-run` from `specialists/agent-stack`.

Expected: all tests pass; preview reports either a fully installable inventory or collisions without changes.

- [ ] **Step 3: Apply only after successful preflight**

Run: `just global-install install`.

Expected: every non-colliding selected path becomes a verified symlink, or the command exits before changing anything and reports collisions.

- [ ] **Step 4: Record the outcome and commit**

Record installed/skipped targets, exact validation, and any unresolved collisions. Commit only Agent Stack files from the isolated worktree.
