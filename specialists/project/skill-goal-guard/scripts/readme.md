# scripts

Runnable front ends of skill-goal-guard over the `goal_guard_lib` package. Every script has a row here and a recipe in the [justfile](../justfile); run them through `just`, which uses the pinned working-cache venv
(`just bootstrap` installs [../requirements.txt](../requirements.txt): PyYAML 6.0.3, openpyxl 3.1.5, ruff 0.17.3). Written under skill-coder on 2026-10-27 (pilot step 4 and the tools for steps 6-8). The v0.1 prototype is in
git history (commit 1dff9c8); its fixtures are kept in [../examples/v0.1/](../examples/v0.1/).

## Contents

- [Front ends](#front-ends)
- [Library](#library)
- [Exit codes and settings](#exit-codes-and-settings)
- [Measured runtime](#measured-runtime)
- [Open checks before trusting live results](#open-checks-before-trusting-live-results)
- [Moved paths](#moved-paths)

## Front ends

| Script                   | What it does                                                             | Safety                                                | Recipes                                |
| ------------------------ | ------------------------------------------------------------------------ | ----------------------------------------------------- | -------------------------------------- |
| `goal_guard.py`          | `validate` records and baseline; `assess` a proposal                     | read-only; `assess --apply` appends one line          | `validate`, `assess`, `assess-apply`,  |
|                          |   (PROCEED/PARK/REVIEW/BLOCK); `next`: task, project and portfolio       |   to `.gg/decisions.jsonl`                            |   `next`, `next-live`                  |
|                          |   What's Next                                                            |                                                       |                                        |
| `goal_guard_vikunja.py`  | Vikunja `info`, one project's `tasks` (`--raw` for an offline file),     | read-only, GET only                                   | `vikunja-info`, `vikunja-tasks`        |
|                          |   one `task`                                                             |                                                       |                                        |
| `goal_guard_trace.py`    | Milestone → hub plan revision → MVP criteria → target-map target →       | read-only; mismatches are REVIEW                      | `trace`                                |
|                          |   Vikunja tasks                                                          |                                                       |                                        |
| `goal_guard_snapshot.py` | `export` a project snapshot with manifests; `verify` it; `restore` into  | plans by default; `--apply` writes snapshot files or  | `snapshot-export[-apply]`,             |
|                          |   a clean test instance                                                  |   creates tasks on the TEST instance                  |   `snapshot-verify`,                   |
|                          |                                                                          |                                                       |   `snapshot-restore[-apply]`           |
| `goal_guard_excel.py`    | The management workbook sample (.xlsx), internal targets left out        | prints rows; `--apply` writes one new file            | `excel`, `excel-apply`                 |
|                          |   by default                                                             |                                                       |                                        |
| `goal_guard_doctor.py`   | Which write paths are enforced, advisory or unsupported; records, hook   | read-only                                             | `doctor`                               |
|                          |   wiring, captures                                                       |                                                       |                                        |
| `goal_guard_hook.py`     | Claude Code PreToolUse adapter, DRAFT: advisory by                       | reads `.gg/`; `--capture` writes a redacted payload   | `hook-test`                            |
|                          |   default, `--mode blocking`                                             |   to the runtime peer                                 |                                        |

## Library

`goal_guard_lib/` is a regular package; its `__init__.py` lists the layers (a module imports only those above it; `import_layers.py --graph`: no cycles).

| Module                           | Holds                                                                                                              |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `errors`, `settings`             | Error types; settings from the environment only (no URL or token in code)                                          |
| `yaml_io`                        | The PyYAML seam (`safe_load` only)                                                                                 |
| `records`, `mvp`                 | Task, Proposal, Verdict; the MVP contract with its criteria, exclusions, blockers and approval                     |
| `project`, `decisions_log`       | `.gg/` loading, partition check, baseline state, path safety; the hash-chained, append-only decision log           |
| `vikunja`, `tasks`               | The Vikunja API v2 seam (timeouts, error translation, pagination); live or offline task sources                    |
| `decide`, `rank`                 | The decision order of references/decision-rules.md; the ranking pipeline of references/whats-next-and-portfolio.md |
| `trace`, `snapshot`, `restore`   | Milestone trace; snapshot export and verify; clean-instance restore                                                |
| `excel`, `doctor`, `hook`, `cli` | The openpyxl seam; the enforcement report; the hook decision; shared front-end plumbing                            |

## Exit codes and settings

Every front end: 0 success; 3 a negative answer to act on (PARK, REVIEW, BLOCK, invalid records, failed trace or verify); 2 bad input; 1 Vikunja failure or refused write. The hook exits 0 (pass or
advisory) or 2 (blocked); an internal error is turned into a denial, because Claude Code treats other exit codes as non-blocking.

Settings (environment): `GG_VIKUNJA_URL`, `GG_VIKUNJA_TOKEN` (a read-only token from KeePassXC, never an argument), `GG_HTTP_TIMEOUT` (10 s), `GG_GIT_TIMEOUT` (10 s), `GG_PARTITION` (`apn` or `me`),
`GG_DEADLINE_DAYS` (14), `GG_VERDICT_MAX_HOURS` (2), `GG_DATA_DIR`, `GG_RUNTIME_DIR`. Full list: `goal_guard_lib/settings.py`.

## Measured runtime

Measured 2026-10-27 on this Mac, Python 3.14.5, against the example fixture:

| What                                                        | Budget                                  | Measured                             |
| ----------------------------------------------------------- | --------------------------------------- | ------------------------------------ |
| `goal_guard_hook.py`, one call                              | under 1 s (it runs on every gated edit) | median 58 ms, max 63 ms over 10 runs |
| `just check` (lint, 71 tests, skill-coder helpers, fixture) | under 30 s                              | 1.3 s wall                           |

Live Vikunja reads are one request per page (the instance pages at 50); not yet measured on real data.

## Open checks before trusting live results

These cannot be settled by the tests, because the fixtures share the assumptions. Each needs the owner's token on the local instance:

1. **Relation direction (GG-305).** `records.PREREQUISITE_KINDS` treats a task's `related_tasks.blocked` and `related_tasks.follows` as its prerequisites, from the OpenAPI 2.7.1 description. Check: in
   Vikunja, mark task A as blocking task B; run `just vikunja-tasks <project>`; B must list A under `prerequisites` and A must list none. If it is reversed, What's Next would offer a waiting task.
2. **Hook payloads.** Run the hook with `--capture` in advisory mode for one session; compare the captures with the documented fields; then observe one blocked edit in blocking mode and record it as
   `enforcement.observed_block_ref` in the project's `.gg/project.yaml`. Until then doctor reports the hook as advisory.
3. **Restore on a clean instance.** `create_task` sends `done` and dates on create; that Vikunja accepts them on POST is UNVERIFIED until the step-8 restore reads them back.
4. **Approval signatures (D3).** `project.verify_approval_commit` only reports; the signing setup is decided before pilot step 5.

The agent writes its own proposal and runs `assess --apply`, so the hook limits it to an approved baseline, a mapped open task and the files that proposal listed, for 2 hours; it does not stop the
agent proposing. REVIEW and BLOCK still need the owner.

## Moved paths

| Old path                                   | New path                                               | Date       |
| ------------------------------------------ | ------------------------------------------------------ | ---------- |
| `docs/goal-guard/scripts/goal_guard.py`    | `scripts/goal_guard.py` (v0.1, rewritten the same day) | 2026-10-27 |
| `docs/goal-guard/tests/test_goal_guard.py` | removed with the rewrite (in git history)              | 2026-10-27 |
| `examples/portfolio.json`, `proposal.json` | `examples/v0.1/`                                       | 2026-10-27 |
