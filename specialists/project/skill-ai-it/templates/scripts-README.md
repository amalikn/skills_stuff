# Script Inventory

This file describes runnable scripts, task runners, and automation entrypoints in this project.

<!-- BEGIN MANAGED: skill-ai-it:scripts --> <!-- skill-ai-it-version: 2026-08-11-governance-checks-layer-v1 -->

## Contents

- [Runtimes — read this before running anything directly](#runtimes-read-this-before-running-anything-directly)
- [Execution Policy](#execution-policy)
- [Preferred Execution Order](#preferred-execution-order)
- [Task Inventory](#task-inventory)
- [Raw Script Inventory](#raw-script-inventory)
- [Safety Labels](#safety-labels)
- [Maintenance Rules](#maintenance-rules)
- [Notes](#notes)

---

## Runtimes — read this before running anything directly

Recipes do **not** use the host's `python3` or `node`. Fill this table in for the project:

| Runtime | Resolved by                                                              | Actual                             |
| ------- | ------------------------------------------------------------------------ | ---------------------------------- |
| Python  | `.venv` in the working-cache peer, built from the pin in `../.mise.toml` | `<working-cache>/.venv/bin/python` |
| Node    | `mise exec -- node`, pinned in `../.mise.toml`                           | `<version>`                        |

`just runtimes` prints what the recipes will actually use. `just bootstrap` rebuilds the venv; it is safe to re-run.

The venv lives in the working-cache peer, never in this repo — the repo carries source, not rebuildable runtime. Every Python recipe depends on `_require-venv`, which fails with a rebuild instruction
rather than silently falling back to the host interpreter.

**Do not invoke these scripts with a bare `python3`.** It resolves to whatever the host has on `PATH`, which works until the host changes and then fails in a way that reads like a code bug.

## Execution Policy

- Prefer the existing canonical task runner for this project.
- Prefer `just <task>` when a `justfile` is present.
- Do not run scripts marked `destructive`, `review-required`, or `unknown` without review.
- Do not assume arbitrary files under `scripts/` are safe.
- If a script is missing from this inventory, inspect it before use and update or propose an inventory entry.
- Secrets must not be documented here as values. Document only secret names and where they are expected to come from.

## Preferred Execution Order

1. Existing canonical task runner (whichever is established for this project)
2. `just --list` / `just <task>`
3. `scripts/README.md`
4. Other task runners: `Taskfile.yml`, `Makefile`, `package.json`
5. Raw scripts under `scripts/` after inspection

## Task Inventory

| Task / Script | Purpose | Inputs | Outputs | Safety | Idempotent | When to use |
| -------------------------- | ---------------------------------- | -------------------------------------- | ---------------------------- | ----------------- | --- | -------------------------------- |
| `just inventory`           | Lists available tasks and this     | `justfile`, `scripts/README.md`        | Console output               | `safe`            | Yes | First check before running       |
|                            |   inventory.                       |                                        |                              |                   |     |   project automation             |
| `just audit-scripts`       | Checks for obvious script/catalog  | `scripts/`, `scripts/README.md`        | Console output               | `safe`            | Yes | During refresh/audit or before   |
|                            |   drift.                           |                                        |                              |                   |     |   agent automation               |
| `just preflight`           | Runs safe local validation checks. | Project files                          | Console output               | `safe`            | Yes | Before edits, commits, or        |
|                            |                                    |                                        |                              |                   |     |   handoff                        |
| `just nav-upgrade-dry-run` | Preview navigation control layer   | `upgrade_navigation_control_layer.py`  | Console output               | `safe`            | Yes | Before running nav-upgrade       |
|                            |   upgrade.                         |                                        |                              |                   |     |                                  |
| `just nav-upgrade`         | Apply navigation control layer     | `upgrade_navigation_control_layer.py`  | Console output, file changes | `review-required` | Yes | After reviewing dry-run output   |
|                            |   upgrades.                        |                                        |                              |                   |     |                                  |
| `just nav-validate`        | Validate navigation control layer  | `validate_navigation_control_layer.py` | Console output               | `safe`            | Yes | After upgrade or periodic audit  |
|                            |   coherence.                       |                                        |                              |                   |     |                                  |
| `just nav-check-diff`      | Check only expected files changed. | `check_expected_diff.py`               | Console output               | `safe`            | Yes | After upgrade                    |
| `just check`               | Governance coherence checks —      | `check_governance.py`, governance      | Console output, exit status  | `safe`            | Yes | Before claiming any durable      |
|                            |   asserts this project's           |   surfaces                             |                              |                   |     |   change complete; after adding, |
|                            |   governance claims against        |                                        |                              |                   |     |   moving, or renaming a file     |
|                            |   reality. Exit 0 required before  |                                        |                              |                   |     |                                  |
|                            |   durable work is complete.        |                                        |                              |                   |     |                                  |

## Raw Script Inventory

| Script  | Purpose | Inputs  | Outputs | Safety    | Idempotent | When to use        |
| ------- | ------- | ------- | ------- | --------- | ---------- | ------------------ |
| `_TBD_` | `_TBD_` | `_TBD_` | `_TBD_` | `unknown` | `_TBD_`    | Inspect before use |

## Safety Labels

| Label                  | Meaning                                                           |
| ---------------------- | ----------------------------------------------------------------- |
| `safe`                 | Read-only or low-risk repeatable operation                        |
| `review-required`      | Needs human review before execution                               |
| `destructive`          | Deletes, overwrites, migrates, deploys, or changes external state |
| `external-network`     | Calls external services or APIs                                   |
| `modifies-files`       | Writes to repo/project files                                      |
| `requires-secrets`     | Requires secret values                                            |
| `requires-credentials` | Requires authenticated local/session credentials                  |
| `long-running`         | May take significant time                                         |
| `unknown`              | Not yet classified; do not run without inspection                 |

## Maintenance Rules

- Keep this file aligned with:
  - `justfile`
  - `Taskfile.yml`
  - `Makefile`
  - `package.json`
  - actual files under `scripts/`
- Prefer managed block updates for generated sections.
- Preserve manually written notes unless explicitly replacing them.
- When removing a script, remove or mark its inventory entry stale.
- When adding a script, document purpose, inputs, outputs, safety, idempotency, and when to use it.

## Notes

Add project-specific caveats here.

<!-- END MANAGED: skill-ai-it:scripts -->
