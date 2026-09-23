# Script Inventory

This file describes runnable scripts, task runners, and automation entrypoints in this project.

## Contents

- [Runtimes — read this before running anything directly](#runtimes--read-this-before-running-anything-directly)
- [Execution Policy](#execution-policy)
- [Preferred Execution Order](#preferred-execution-order)
- [Maintenance Rules](#maintenance-rules)
- [Task Inventory](#task-inventory)
- [Raw Script Inventory](#raw-script-inventory)
- [Safety Labels](#safety-labels)
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
rather than silently falling back to the host interpreter. The one sanctioned exception is `just bootstrap` itself, which creates the venv from the mise pin.

**Do not invoke these scripts with a bare `python3`.** It resolves to whatever the host has on `PATH`, which works until the host changes and then fails in a way that reads like a code bug.

<!-- BEGIN MANAGED: skill-ai-it:scripts --> <!-- skill-ai-it-version: 2026-09-23-template-sourced-blocks-v1 -->

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

## Maintenance Rules

- Keep this file aligned with: `justfile`, `Taskfile.yml`, `Makefile`, `package.json`, actual files under `scripts/`
- Prefer managed block updates for generated sections.
- Preserve manually written notes unless explicitly replacing them.
- When removing a script, remove or mark its inventory entry stale.
- When adding a script, document purpose, inputs, outputs, safety, idempotency, and when to use it.

<!-- END MANAGED: skill-ai-it:scripts -->

## Task Inventory

Everything below `## Task Inventory` lives OUTSIDE the managed block above and is agent-maintained — `nav-upgrade` never touches it. Fill in the project's actual `just` recipes.

| Task / Script              | Purpose                                 | Inputs                                 | Outputs            | Safety            | Idempotent | When to use                    |
| -------------------------- | --------------------------------------- | -------------------------------------- | ------------------ | ----------------- | ---------- | ------------------------------ |
| `just inventory`           | Lists available tasks and               | `justfile`, `scripts/README.md`        | Console output     | `safe`            | Yes        | First check before running     |
|                            |   this inventory.                       |                                        |                    |                   |            |   project automation           |
| `just audit-scripts`       | Checks for obvious                      | `scripts/`, `scripts/README.md`        | Console output     | `safe`            | Yes        | During refresh/audit or before |
|                            |   script/catalog drift.                 |                                        |                    |                   |            |   agent automation             |
| `just preflight`           | Runs safe local validation checks.      | Project files                          | Console output     | `safe`            | Yes        | Before edits, commits,         |
|                            |                                         |                                        |                    |                   |            |   or handoff                   |
| `just nav-upgrade-dry-run` | Preview navigation control              | `upgrade_navigation_control_layer.py`  | Console output     | `safe`            | Yes        | Before running nav-upgrade     |
|                            |   layer upgrade.                        |                                        |                    |                   |            |                                |
| `just nav-upgrade`         | Apply navigation control                | `upgrade_navigation_control_layer.py`  | Console output,    | `review-required` | Yes        | After reviewing dry-run output |
|                            |   layer upgrades.                       |                                        |   file changes     |                   |            |                                |
| `just nav-validate`        | Validate navigation control             | `validate_navigation_control_layer.py` | Console output     | `safe`            | Yes        | After upgrade or               |
|                            |   layer coherence.                      |                                        |                    |                   |            |   periodic audit               |
| `just nav-check-diff`      | Check only expected files changed.      | `check_expected_diff.py`               | Console output     | `safe`            | Yes        | After upgrade                  |
| `just lint-md`             | Lints markdown                          | `.markdownlint-cli2.jsonc`             | Console output     | `safe`            | Yes        | Before commit; part            |
|                            |   against `.markdownlint-cli2.jsonc`.   |                                        |                    |                   |            |   of preflight                 |
| `just check`               | Governance coherence checks — asserts   | `check_governance.py`,                 | Console output,    | `safe`            | Yes        | Before claiming any durable    |
|                            |   this project's governance claims      |   governance surfaces                  |   exit status      |                   |            |   change complete; after       |
|                            |   against reality. Exit 0 required      |                                        |                    |                   |            |   adding, moving, or renaming  |
|                            |   before durable work is complete.      |                                        |                    |                   |            |   a file                       |

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

## Notes

Add project-specific caveats here.
