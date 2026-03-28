# RUNBOOK

## Use When
The task includes making edits, planning edits, validating risk, or explaining how a change should be verified and bounded.

## Workflow
1. Inspect repo-local validation guidance first when it exists, then use it to choose the actual commands.
2. Identify relevant validation commands before editing.
3. Separate minimal blocking checks from deeper manual validation.
4. Choose the smallest meaningful validation that proves correctness.
5. Run safe validation where possible.
6. Record what was and was not validated.
7. Keep rollback or recovery considerations explicit when the change is operationally risky.
