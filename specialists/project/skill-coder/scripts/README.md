# Script Inventory

skill-coder's helpers: stdlib-only checkers that hold any project's code to the pack's rules, plus the pack's own governance checker.

## Contents

- [How to run a helper against a project](#how-to-run-a-helper-against-a-project)
- [Runtimes](#runtimes)
- [Execution Policy](#execution-policy)
- [Preferred Execution Order](#preferred-execution-order)
- [Maintenance Rules](#maintenance-rules)
- [Task Inventory](#task-inventory)
- [Raw Script Inventory](#raw-script-inventory)
- [Baselines and the code map](#baselines-and-the-code-map)
- [Safety Labels](#safety-labels)

---

## How to run a helper against a project

Default: run it with the **target project's own pinned interpreter**, by path, from the project root. The helpers are stdlib-only, need Python 3.11 or
newer (`REQUIRES_PYTHON` in each file) and only read files, so nothing is installed into the project:

```bash
<project venv>/bin/python /Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-coder/scripts/code_size.py --project-root . --list
```

Fallback, only when the project has no Python 3.11+: run the same helper with this pack's interpreter through its recipe, pointing at the project:
`just -f <this pack>/justfile code-size --project-root /path/to/project`. Each helper reads its settings from the project's `code-map.toml` when
one is at the project root (template: `templates/code-map.toml`); command-line flags win over the map.

## Runtimes

| Runtime | Resolved by                                                                | Actual                                                              |
| ------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Python  | `.venv` in the working-cache peer, built from the pin in `../.mise.toml`    | `/Volumes/Data/_ai/_skills/skills-working-cache/skill-coder/.venv` |

`just runtimes` prints what the recipes use; `just bootstrap` rebuilds the venv (safe to re-run). The venv is only for this pack's own recipes and
tests (it adds PyYAML for the contract test); the helpers need nothing from it. `just test-matrix` runs the helper tests under every Python from 3.11
that mise has installed. Do not invoke the pack's recipes through a bare `python3`.

<!-- BEGIN MANAGED: skill-ai-it:scripts -->
<!-- skill-ai-it-version: 2026-10-14-compact-v2 -->

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

| Task                  | Purpose                                                                   | Inputs                         | Outputs                | Safety            | Idempotent | When to use                                |
| --------------------- | ------------------------------------------------------------------------- | ------------------------------ | ---------------------- | ----------------- | ---------- | ------------------------------------------ |
| `just test`           | Contract and helper tests                                                 | `tests/`, pack files           | Console, exit status   | `safe`            | Yes        | Before calling any change complete         |
| `just test-matrix`    | Helper tests under each installed Python from 3.11                        | `tests/test_helpers.py`        | One line per version   | `safe`            | Yes        | After changing a helper                    |
| `just self-check`     | The pack held to its own rules (size, timeouts, groups, suppressions, write gates, headers) | `scripts/`, `tests/`, baselines | Console, exit status  | `safe`            | Yes        | Part of `just check`                       |
| `just check`          | Governance coherence, doc freshness, roles, then `self-check`             | Governance surfaces            | Console, exit status   | `safe`            | Yes        | Before claiming durable work complete      |
| `just code-size`      | `scripts/code_size.py` against a project (fallback runtime)               | `--project-root`, code map     | Findings, exit status  | `safe`            | Yes        | Project lacks Python 3.11+                 |
| `just call-timeouts`  | `scripts/call_timeouts.py` against a project (fallback runtime)           | `--project-root`, code map     | Findings, exit status  | `safe`            | Yes        | As above                                   |
| `just suppressions`   | `scripts/suppressions.py` against a project (fallback runtime)            | `--project-root`, code map     | Findings, exit status  | `safe`            | Yes        | As above                                   |
| `just group-timeouts` | `scripts/group_timeouts.py` against a project (fallback runtime)          | `--project-root`, code map     | Findings, exit status  | `safe`            | Yes        | As above                                   |
| `just scaffold`       | `scripts/scaffold.py`: prints a new script's and its test's skeleton       | `--lang`, `--name`, `--summary` | Console               | `safe`            | Yes        | Starting a new script                      |
| `just write-gates`    | `scripts/write_gates.py` against a project (fallback runtime)             | `--project-root`, code map     | Findings, exit status  | `safe`            | Yes        | As above                                   |
| `just import-layers`  | `scripts/import_layers.py` against a project (fallback runtime)           | `--project-root`, code map     | Findings, exit status  | `safe`            | Yes        | As above                                   |
| `just script-headers` | `scripts/script_headers.py` against a project (fallback runtime)          | `--project-root`, code map     | Findings, exit status  | `safe`            | Yes        | As above                                   |
| `just naming-check`  | `scripts/naming_check.py` against a project (fallback runtime)            | `--project-root`, code map     | Findings, exit status  | `safe`            | Yes        | As above                                   |
| `just module-groups` | `scripts/module_groups.py` against a project (fallback runtime)           | `--project-root`, code map     | Candidates (warn only) | `safe`            | Yes        | Modularising code; reviews                 |
| `just write-back`    | `scripts/write_back.py`: entries a project holds for this skill, to promote | `--project-root`, `--skill`    | Pending entries        | `safe`            | Yes        | Every slurp; before closing an engagement  |
| `just naming-table`  | Re-renders the naming table from `naming.toml`                            | `naming.toml`                  | The reference's table  | `modifies-files`  | Yes        | After editing `naming.toml`                |
| `just helpers`        | Lists the helper files                                                    | `scripts/`                     | Console                | `safe`            | Yes        | Orientation                                |
| `just context-pack`   | Regenerates `.ai-context/governance-pack.md` (support only)               | `repomix.config.json`          | `.ai-context/`         | `modifies-files`  | Yes        | After large changes                        |
| `just bootstrap`      | Builds the pack's working-cache venv from the mise pin                    | `.mise.toml`, requirements     | venv outside the repo  | `modifies-files`  | Yes        | First use, or after a pin change           |
| `just inventory`      | Lists tasks and this inventory                                            | `justfile`, this file          | Console                | `safe`            | Yes        | First check before running automation      |
| `just audit-scripts`  | Script/catalog drift                                                      | `scripts/`, this file          | Console                | `safe`            | Yes        | During refresh or audit                    |
| `just preflight`      | runtimes, audit-scripts, test, self-check, check, lint-md                 | Pack files                     | Console                | `safe`            | Yes        | Before commit or handoff                   |
| `just nav-upgrade-dry-run` / `just nav-upgrade` / `just nav-validate` / `just nav-check-diff` | skill-ai-it navigation layer upgrade and validation | skill-ai-it scripts | Console, file changes on upgrade | `review-required` (upgrade) | Yes | When skill-ai-it's blocks change |

## Raw Script Inventory

| Script                       | Purpose                                                                                     | Inputs                                  | Outputs                          | Safety                       | Idempotent | When to use                                   |
| ---------------------------- | ------------------------------------------------------------------------------------------- | --------------------------------------- | -------------------------------- | ---------------------------- | ---------- | --------------------------------------------- |
| `scripts/code_size.py`       | Module and function size limits, warn and fail tiers, per language, shrink-only baseline     | Source files, code map, baseline        | Findings; baseline on request    | `safe` (`modifies-files` with `--write-baseline`) | Yes | Every check; adopting the size rule           |
| `scripts/call_timeouts.py`   | Python network and subprocess calls without a timeout, shrink-only baseline                  | Python files, code map, baseline        | Findings; baseline on request    | `safe` (`modifies-files` with `--write-baseline`) | Yes | Every check                                   |
| `scripts/suppressions.py`    | Inline linter suppressions per language (`noqa`, `type: ignore`, `shellcheck disable`, `eslint-disable`, `@ts-ignore`, `nolint`, Rust `allow`), shrink-only baseline | Code files, code map, baseline | Findings; baseline on request | `safe` (`modifies-files` with `--write-baseline`) | Yes | Every check |
| `scripts/group_timeouts.py`  | Timed `subprocess.run`-family calls whose command (ssh, scp, rsync, a shell, `shell=True`) starts children the timeout leaves running, shrink-only baseline | Python files, code map, baseline | Findings; baseline on request | `safe` (`modifies-files` with `--write-baseline`) | Yes | Every check |
| `scripts/scaffold.py`        | Prints the skeleton of a new Python or shell script and its test, meeting this pack's rules; writes nothing | `--lang`, `--name`, `--summary`, `--writes` | Console | `safe` | Yes | Starting a new script |
| `scripts/write_gates.py`     | Entry points that write without `--apply`, and stale register entries                        | Source files, code map or JSON config   | Findings                         | `safe`                       | Yes        | Every check                                   |
| `scripts/import_layers.py`   | Python import layer rules, cycles and a package import graph (`--json`; a root ending `:self` keeps its folder name) | Python files, code map or layers TOML   | Findings or a graph report       | `safe`                       | Yes        | Every check; structure reviews                |
| `scripts/script_headers.py`  | Runnable scripts whose native header lacks a summary, a run line or a safety statement       | Python and shell files, baseline        | Findings; baseline on request    | `safe` (`modifies-files` with `--write-baseline`) | Yes | Every check                                   |
| `scripts/naming_check.py`   | Code file names and `just` recipe names against `naming.toml` and the project's `[naming]` overrides, shrink-only baseline | Files, justfile, code map, baseline | Findings; baseline on request | `safe` (`modifies-files` with `--write-baseline`) | Yes | Every check |
| `scripts/naming_table.py`   | Renders the naming table in `references/naming-conventions.md` from `naming.toml`; reports drift | `naming.toml` | The table (with `--write`) | `modifies-files` with `--write`, else `safe` | Yes | After editing `naming.toml` |
| `scripts/module_groups.py`  | Folders where three or more code files share a name prefix: candidate packages (warn only; `--strict` fails) | Source files, code map | Candidates | `safe` | Yes | Modularising code; reviews |
| `scripts/write_back.py`     | Write-back entries a project parked for a skill (under a heading naming it), to promote into the skill (`--strict` fails while one is pending) | Markdown files | Pending entries | `safe` | Yes | Every slurp (skill-slurp-chat Step 5b) |
| `scripts/code_map.py`        | Loads and checks a project's `code-map.toml` (imported by the helpers)                       | `code-map.toml`                         | Settings                         | `safe`                       | Yes        | Imported, not run                             |
| `scripts/pyparse.py`         | Parses Python at the project's grammar with parser warnings silenced (imported by the helpers) | Python source                           | AST or SyntaxError               | `safe`                       | Yes        | Imported, not run                             |
| `scripts/ratchet.py`         | The shrink-only baseline every helper uses (imported)                                        | Baseline JSON                           | Verdicts                         | `safe`                       | Yes        | Imported, not run                             |
| `scripts/check_governance.py` | This pack's governance checker (from skill-ai-it's template)                                | Governance surfaces                     | Findings, exit status            | `safe`                       | Yes        | Through `just check`                          |

## Baselines and the code map

`scripts/code-size-baseline.json`, `scripts/timeout-baseline.json` and `scripts/script-headers-baseline.json` are machine-written by the helpers'
`--write-baseline` (adoption, or recording an improvement); never edit them by hand. `../code-map.toml` holds this pack's own decisions.

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

## Governance recipes (skill-ai-it)

- `just govern`: governance up to the current skill-ai-it standard (adoption, record budgets with `just check`, role findings); content fixes are `/skill-ai-it refresh`. `modifies-files`.
- `just roles`: root governance files outside their roles (front matter, README quick start, ROADMAP shape, duplicated sections). Read-only; `safe`.
- `just stale`: stale docs by rule (review due, superseded outside archive/, a Depends on file changed). Read-only; `safe`.
- `just docs [folder]`: one header line per file, to triage before opening. Read-only; `safe`.
- `just history <term>`: search rotated CHANGELOG (or SCRATCHPAD) entries in docs/history. Read-only; `safe`.
- `just history-show <stamp>`: print one rotated entry. Read-only; `safe`.
- `just rotate [--apply]`: move old CHANGELOG/SCRATCHPAD entries and done ROADMAP items to docs/history, verified. Plan by default; `modifies-files`.
- `just budget [--apply]`: bring governed files within budget (normalise, rotate, move reference sections, audit, check). Plan by default; `modifies-files`.
- `just changelog-entry --title ... --body-file ...`: add a CHANGELOG entry in this project's style, with its Contents line. Plan by default; `modifies-files`.
- `just move-sections ...`: move named sections verbatim to an on-need reference doc. Plan by default; `modifies-files`.
- `just outline <file.md>`: each heading with its line range, to read one section instead of the file. Read-only; `safe`.
- `just section <file.md> "<title>"`: print one section (exact title, `Parent > Child`, `#anchor`, `~text`). Read-only; `safe`.
