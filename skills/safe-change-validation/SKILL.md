---
name: safe-change-validation
description: Use when planning or making edits that require disciplined validation. Identify the smallest meaningful validation before editing, document what was and was not validated, and keep rollback/recovery awareness explicit.
metadata:
  short-description: Safe change validation
---

# Safe Change Validation

## Use When
Use this skill when the task includes editing code, config, infrastructure, or automation and the validation path needs to be selected and reported clearly.

## Rules
- Inspect repo-local validation docs first when they exist and use them to choose the actual commands.
- Identify validation commands before editing.
- Separate minimal blocking checks from deeper manual validation.
- Prefer the smallest meaningful validation that proves correctness.
- Record what was validated and what remains unverified.
- Do not overclaim completeness from partial validation.
- Keep rollback or recovery thinking explicit for risky changes.

## References
- references/PROFILE.md
- references/RUNBOOK.md
- references/KNOWN_ISSUES.md
- references/CHANGELOG.md
- references/CHECKLISTS/triage.md
- references/CHECKLISTS/change.md
- references/CHECKLISTS/rollback.md
- references/CHECKLISTS/healthcheck.md
