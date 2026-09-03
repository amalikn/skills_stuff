# Script Inventory — skill-ai-it

Runnable scripts for maintaining the **navigation control layer** in target projects. These operate on a project passed via `--project-root`; they do not act on this package unless it is passed
explicitly.

<!-- BEGIN MANAGED: skill-ai-it:scripts --> <!-- skill-ai-it-version: 2026-08-11-governance-checks-layer-v1 -->

## Execution Policy

- Always run `nav-upgrade-dry-run` before `nav-upgrade`. The upgrade writes managed blocks into a project's governance files.
- Run `nav-validate` after any upgrade, and `nav-check-diff` to confirm only expected files changed.
- Do not run `nav-upgrade` against a project with uncommitted governance changes — review the dry-run diff first.
- These scripts are stdlib-only and require no virtualenv.

## Task Inventory

| Script | Purpose | Inputs | Outputs | Safety | Idempotent | When to use |
|---|---|---|---|---|---|---|
| `upgrade_navigation_control_layer.py` | Writes/refreshes managed navigation blocks in a target project's `AGENTS.md`, `AI_NAVIGATION.md`, and `scripts/README.md`, stamped with the current `VERSION`. | `--project-root`, `--dry-run`, `--report-json`, `--repair-claude-wrapper` | File changes in the target project; console diff | `review-required` | Yes | After a `VERSION` bump, or to bring a project onto the current control layer |
| `validate_navigation_control_layer.py` | Validates control-layer coherence: managed block integrity, version stamps, required governance files, `context-map.yaml` keys, task-runner references, and governance-checker presence/wiring. | `--project-root`, `--report-json` | Console pass/warn/fail; exit 0/1/2 | `safe` | Yes | After upgrade, or as a periodic audit |
| `check_expected_diff.py` | Confirms only expected files changed after an upgrade, against `DEFAULT_EXPECTED` plus `--allow` additions. Requires the target to be a git repo. | `--project-root`, `--allow`, `--report-json` | Console list of expected vs unexpected changes | `safe` | Yes | Immediately after `nav-upgrade` |

## Exit Codes

`validate_navigation_control_layer.py` returns `0` PASS, `1` FAIL, `2` WARN (critical checks passed, warnings exist). The others return `0` on success and non-zero on error.

## Coupled Constants

`VERSION` is restated in `upgrade_navigation_control_layer.py` and `validate_navigation_control_layer.py` and stamped into every managed-block template under `templates/`. The two must stay identical
— drift between them silently disables the staleness signal, because `validate` would then be checking for a stamp `upgrade` never writes. Changing the version means changing every surface in one
pass; see `patterns/navigation-control-automation.md`.

## Safety Labels

| Label | Meaning |
|---|---|
| `safe` | Read-only or low-risk repeatable operation |
| `review-required` | Needs human review before execution |
| `destructive` | Deletes, overwrites, migrates, deploys, or changes external state |

<!-- END MANAGED: skill-ai-it:scripts -->

## Related

- `patterns/navigation-control-automation.md` — when to run each script, exit codes, `.proposed` handling, version-stamp semantics
- `patterns/script-task-audit-checklist.md` — catalog completeness auditing
- `patterns/governance-checks.md` — the *target project's* own executable checker, a separate layer from these scripts
