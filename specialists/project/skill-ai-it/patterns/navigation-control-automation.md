# Navigation Control Automation

This document explains the deterministic automation scripts for upgrading, validating, and verifying the AI navigation/control layer in existing projects.

## Contents

- [Why automation exists](#why-automation-exists)
- [When to run each script](#when-to-run-each-script)
- [How to interpret exit codes](#how-to-interpret-exit-codes)
- [How to handle .proposed files](#how-to-handle-proposed-files)
- [Relationship to patterns/governance-checks.md](#relationship-to-patternsgovernance-checksmd)
- [Relationship to patterns/drift-audit.md](#relationship-to-patternsdrift-auditmd)
- [Relationship to patterns/script-task-audit-checklist.md](#relationship-to-patternsscript-task-audit-checklistmd)

---

## Why automation exists

The managed-block and context-map.yaml schema changes in the navigation control layer are deterministic — they follow well-defined rules for marker format, version stamping, and key presence. Rather
than relying only on agents to interpret Markdown instructions, these scripts provide:

- Deterministic, idempotent behavior
- Machine-parseable JSON reports
- Clear exit codes for CI/automation
- Dry-run mode for safe preview
- .proposed fallback for risky YAML merges

## When to run each script

| Script | When to run |
|---|---|
| `scripts/upgrade_navigation_control_layer.py` | First pass against an existing project. Upgrades managed blocks, fixes markers, adds missing context-map.yaml keys. Use `--dry-run` first. |
| `scripts/validate_navigation_control_layer.py` | After upgrade or whenever governance coherence needs checking. Pass/fail/warn output with actionable messages. |
| `scripts/check_expected_diff.py` | After upgrade, to verify only expected governance files changed. Detects accidental modifications to source files. |

## How to interpret exit codes

### upgrade_navigation_control_layer.py

| Code | Meaning |
|---|---|
| 0 | Success, no changes required |
| 1 | Fatal error (e.g. invalid path) |
| 2 | Success, changes applied (or would apply in dry-run) |
| 3 | Manual review required (e.g. YAML parse failure, .proposed written) |

### validate_navigation_control_layer.py

| Code | Meaning |
|---|---|
| 0 | PASS — all checks passed |
| 1 | FAIL — one or more checks failed |
| 2 | WARN — all critical checks passed, but warnings exist |

### check_expected_diff.py

| Code | Meaning |
|---|---|
| 0 | Only expected/allowed files changed |
| 1 | Unexpected changes found |
| 2 | Not a git repo or git unavailable |

## How to handle .proposed files

When `upgrade_navigation_control_layer.py` encounters a YAML file it cannot safely merge (parse error, unexpected structure), it writes `context-map.yaml.proposed` instead of overwriting the live
file. To resolve:

1. Review the .proposed file alongside the original.
2. Merge acceptable changes manually.
3. Remove the .proposed file when resolved.

## Relationship to patterns/governance-checks.md

`patterns/governance-checks.md` covers the target project's own executable checker (`scripts/check_governance.py`). The distinction is which repo is being asserted about: the automation scripts here
validate that the **navigation control layer** was installed correctly, while the generated checker asserts that the **project's governance claims** are true.

`validate_navigation_control_layer.py` reports on the checker advisorily — present, wired into a task runner, and referenced from `AGENTS.md`. Absence is a `warn`, not a `fail`, because the checker is
a capability projects adopt during a refresh rather than a precondition of the control layer; failing on it would mark every project bootstrapped before the capability existed as broken. A checker
that is present but unwired is still flagged.

### Version stamp and re-upgrade

`VERSION` is restated in `upgrade_navigation_control_layer.py` and `validate_navigation_control_layer.py` and must stay identical — drift between them silently disables the staleness signal. Bumping
it is the mechanism that tells already-upgraded projects to re-run the upgrade: their managed blocks carry the previous stamp and `validate` reports "missing current version stamp". That report is the
intended signal, not a defect in the project. Remediation is one `just nav-upgrade` per project.

Current stamp: `2026-08-11-governance-checks-layer-v1` (previous: `2026-05-29-ai-navigation-control-layer-v1`). Projects still on the previous stamp lack the emitted governance-checks guidance.

## Relationship to patterns/drift-audit.md

`patterns/drift-audit.md` is the broader governance coherence audit pattern. It validates managed block integrity, companion updates, stale references, and promotion gates. The automation scripts
implement a subset of those checks deterministically, while the pattern document explains the full manual audit procedure.

Run order:
1. `scripts/validate_navigation_control_layer.py` (deterministic check)
2. `patterns/drift-audit.md` manual checkpoints (if deeper inspection needed)

## Relationship to patterns/script-task-audit-checklist.md

`patterns/script-task-audit-checklist.md` handles detailed script inventory validation (catalog entries, safety labels, inputs/outputs). The automation scripts check whether `scripts/README.md` exists
and has a managed block, but do not validate individual script entries.

Run the automation scripts first for structural integrity, then the script-task-audit-checklist for catalog completeness.
