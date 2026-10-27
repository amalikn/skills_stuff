# scripts

Runnable front ends of skill-goal-guard. Every script has a row here and a recipe in the [justfile](../justfile); run them through `just`, which uses the pinned working-cache venv.

| Script          | Status                                        | Inputs                                                    | Outputs                          | Safety    | Recipe                  |
| --------------- | --------------------------------------------- | --------------------------------------------------------- | -------------------------------- | --------- | ----------------------- |
| `goal_guard.py` | prototype (v0.1, moved byte-identical from    | `validate --state <json>`;                                | JSON on stdout; exit 1 on        | read-only | `just validate`,        |
|                 |   `docs/goal-guard/scripts/` 2026-10-27)      |   `next --state <json> [--date YYYY-MM-DD]`;              |   invalid state or               |           |   `just next`,          |
|                 |                                               |   `assess --state <json> --proposal <json>`               |   failed validation              |           |   `just assess`         |

## Known gaps (to close in the pilot rewrite, not by patching the prototype)

- No per-function Args/Returns docstrings; one-line style (skill-coder documentation-and-headers). The module header was added 2026-10-27.
- Task state is read from a local JSON; the operator decided Vikunja owns live tasks (2026-10-27).
- No MVP baseline, approval, exclusions or BLOCK verdict; a registered blocker returns PROCEED even when `adds_scope` is set; ranking is a weighted score.
- An invalid ISO date in the state raises an uncaught `ValueError` instead of a validation issue.

Details and the order of work: [../references/pilot-plan.md](../references/pilot-plan.md).

## Moved paths

| Old path                                   | New path                   | Date       |
| ------------------------------------------ | -------------------------- | ---------- |
| `docs/goal-guard/scripts/goal_guard.py`    | `scripts/goal_guard.py`    | 2026-10-27 |
| `docs/goal-guard/tests/test_goal_guard.py` | `tests/test_goal_guard.py` | 2026-10-27 |
| `docs/goal-guard/examples/*.json`          | `examples/*.json`          | 2026-10-27 |
