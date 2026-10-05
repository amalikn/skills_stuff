# Script Inventory — skill-openwisp

Runnable helpers, task-runner recipes and the governance checker in this pack. Helpers in `scripts/` are tested, stdlib-only and promoted from a real engagement; the package contract fails any helper
without a test in `tests/test_helpers.py`.

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

Recipes do **not** use the host's `python3`. This pack calls no JS tool, so Node is not pinned.

| Runtime | Resolved by                                                              | Actual                             |
| ------- | ------------------------------------------------------------------------ | ---------------------------------- |
| Python  | `.venv` in the working-cache peer, built from the pin in `../.mise.toml` | `/Volumes/Data/_ai/_skills/skills-working-cache/skill-openwisp/.venv/bin/python` |

`just runtimes` prints what the recipes will actually use. `just bootstrap` rebuilds the venv; it is safe to re-run.

The venv lives in the working-cache peer, never in this repo — the repo carries source, not rebuildable runtime. Every Python recipe depends on `_require-venv`, which fails with a rebuild instruction
rather than silently falling back to the host interpreter. The one sanctioned exception is `just bootstrap` itself, which creates the venv from the mise pin.

**Do not invoke these scripts with a bare `python3`.** It resolves to whatever the host has on `PATH`, which works until the host changes and then fails in a way that reads like a code bug.

<!-- BEGIN MANAGED: skill-ai-it:scripts -->
<!-- skill-ai-it-version: 2026-09-23-template-sourced-blocks-v1 -->

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

Everything below `## Task Inventory` lives outside the managed block and is maintained by hand — `nav-upgrade` never touches it.

| Task / Script | Purpose | Inputs | Outputs | Safety | Idempotent | When to use |
|---|---|---|---|---|---|---|
| `just bootstrap` | Build the working-cache venv from the mise pin; install `requirements.txt` | `.mise.toml`, `requirements.txt` | venv under the working-cache peer | `modifies-files` (outside the repo) | Yes | First run, or when `just runtimes` reports MISSING |
| `just runtimes` | Print the interpreter the recipes will actually use | — | Console output | `safe` | Yes | Before trusting any Python recipe |
| `just inventory` | List tasks and this inventory | `justfile`, `scripts/README.md` | Console output | `safe` | Yes | First check before running pack automation |
| `just audit-scripts` | Show script/catalog drift | `scripts/`, `scripts/README.md` | Console output | `safe` | Yes | During refresh/audit |
| `just helpers` | List the helpers this pack ships | `scripts/*.py` | Console output | `safe` | Yes | Before importing a helper |
| `just test` | Offline package contract + helper tests (includes the governance checker) | `tests/`, every pack file | Console output, exit status | `safe` | Yes | Before claiming any change complete |
| `just check` | Governance coherence checks alone | `scripts/check_governance.py`, governance surfaces | Console output, exit status | `safe` | Yes | After adding, moving or renaming any file |
| `just preflight` | runtimes + audit-scripts + test + check + lint-md | Pack files | Console output | `safe` | Yes | Before commit or handoff |
| `just lint-md` | Markdown lint against `.markdownlint-cli2.jsonc` | `**/*.md` | Console output | `safe` | Yes | Before commit |
| `just context-pack` | Regenerate `.ai-context/governance-pack.md` with Repomix | `repomix.config.json` | `.ai-context/governance-pack.md` | `modifies-files` | Yes | After governance or routing changes |
| `just graph` | Refresh `graphify-out/` (code graph, AST only, no LLM) | Pack source files | `graphify-out/GRAPH_REPORT.md`, `graphify-out/graph.json`, `graphify-out/graph.html` | `modifies-files` | Yes | After adding or changing helpers or tests |
| `just nav-upgrade-dry-run` | Preview the skill-ai-it navigation-layer upgrade | skill-ai-it upgrader | Console output | `safe` | Yes | Before `just nav-upgrade` |
| `just nav-upgrade` | Apply the navigation-layer upgrade | skill-ai-it upgrader | File changes | `review-required` · `modifies-files` | Yes | After reviewing the dry run |
| `just nav-validate` | Validate the navigation layer | skill-ai-it validator | Console output | `safe` | Yes | After an upgrade or periodically |
| `just nav-check-diff` | Confirm only expected governance files changed | git diff | Console output | `safe` | Yes | After an upgrade |
| `just nav-selftest` | Self-test the skill-ai-it block builders (not this pack) | skill-ai-it templates | Console output | `safe` | Yes | After skill-ai-it templates change |
| `just probe-workers <container>` | Read-only: are the Celery workers answering (`scripts/openwisp_probe.py workers`) | Celery container name | Console findings, exit status | `safe` · `requires-credentials` | Yes | Containers Up but data stale |
| `just probe-freshness <container> [max_age]` | Read-only: age of the newest stored point (`scripts/openwisp_probe.py freshness`) | InfluxDB container name, max age seconds | Console findings, exit status | `safe` · `requires-credentials` | Yes | Graphs empty or stale |
| `just probe-settings <containers> <expected>` | Read-only: effective settings vs an expected JSON, secrets masked (`scripts/openwisp_probe.py settings`) | Container list, expected-settings JSON | Console findings, exit status | `safe` · `requires-credentials` | Yes | A custom setting seems not to apply |

## Raw Script Inventory

| Script | Purpose | Inputs | Outputs | Safety | Idempotent | When to use |
|---|---|---|---|---|---|---|
| `scripts/openwisp_identity.py` | Pure identity and time conversions: 32-hex `hardware_id` from an inventory UUID, hostname-safe device names, MAC normalisation, UTC backfill `time` format | Inventory UUID / name / MAC / aware datetime | Converted strings | `safe` | Yes | Import in any inventory-to-OpenWISP integration |
| `scripts/openwisp_probe.py` | Read-only health probe for a docker-openwisp deployment: Celery worker liveness, data freshness, effective settings. Writes nothing, prints no secret | `workers` / `freshness` / `settings` subcommand and container names | Console findings, exit status | `safe` (read-only) · `requires-credentials` (Docker access on the host) | Yes | On a host running docker-openwisp, when containers are Up but data is stale; via the three probe recipes below (`just probe-workers`, `just probe-freshness`, `just probe-settings`) |
| `scripts/openwisp_registry.py` | Reads registered devices by `hardware_id` server-side and compares each with a source-of-truth record (normalised MAC, management IP). Promoted from the UNC script check_registry_consistency.py | A Django-shell runner, a source lookup | Mismatch lines | `safe` (read-only) | Yes | After an incident that could mix identities, and after upgrades |
| `scripts/openwisp_health_mirror.py` | Plans the health mirror from OpenWISP into an inventory: write only on change, clear unregistered devices, field names passed in. Promoted from the UNC script sync_openwisp_health.py | A Django-shell runner, current mirrored values, field names | `MirrorPlan` (summary, change lines, PATCH body); applying is the caller's | `safe` (plan) · `modifies-state` (when the caller applies) | Yes | Hourly, or on demand with a dry run first |
| `scripts/openwisp_alert_policy.py` | Converges AlertSettings on a policy of per-metric defaults and per-class overrides; plans offline and generates the server-side program, which writes only when apply is passed. Promoted from the UNC script openwisp_alert_settings.py | A policy dict, a device-to-class mapping, a Django-shell runner | Planned differences; with apply, changed AlertSettings rows | `safe` (dry run) · `review-required` · `modifies-state` (apply) | Yes (only differing rows change) | After changing the alert policy file |
| `scripts/check_governance.py` | Governance coherence checker: path references resolve, catalogs complete in both directions, named recipes exist, no implicit interpreter | Governance surfaces, `references/`, `scripts/`, `justfile` | Console output, exit status | `safe` | Yes | Via `just check` or `just test` |

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

- Adding a helper: put it in `scripts/`, keep it stdlib-only, add its tests to `tests/test_helpers.py`, and catalog it here in the same pass — the contract test and the governance checker each fail
  until that is done.
- Helpers are generic product rules. Customer, site and equipment specifics stay in the engaging project.
