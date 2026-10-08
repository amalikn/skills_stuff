# Script Inventory — skill-nautobot

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
| Python  | `.venv` in the working-cache peer, built from the pin in `../.mise.toml` | `/Volumes/Data/_ai/_skills/skills-working-cache/skill-nautobot/.venv/bin/python` |

`just runtimes` prints what the recipes will actually use. `just bootstrap` rebuilds the venv; it is safe to re-run.

The venv lives in the working-cache peer, never in this repo — the repo carries source, not rebuildable runtime. Every Python recipe depends on `_require-venv`, which fails with a rebuild instruction
rather than silently falling back to the host interpreter. The one sanctioned exception is `just bootstrap` itself, which creates the venv from the mise pin.

**Do not invoke these scripts with a bare `python3`.** It resolves to whatever the host has on `PATH`, which works until the host changes and then fails in a way that reads like a code bug.

<!-- BEGIN MANAGED: skill-ai-it:scripts -->
<!-- skill-ai-it-version: 2026-10-07-snake-case-recipes-v1 -->

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

Everything below `## Task Inventory` lives outside the managed block and is maintained by hand — `nav_upgrade` never touches it.

| Task / Script | Purpose | Inputs | Outputs | Safety | Idempotent | When to use |
|---|---|---|---|---|---|---|
| `just bootstrap` | Build the working-cache venv from the mise pin; install `requirements.txt` | `.mise.toml`, `requirements.txt` | venv under the working-cache peer | `modifies-files` (outside the repo) | Yes | First run, or when `just runtimes` reports MISSING |
| `just runtimes` | Print the interpreter the recipes will actually use | — | Console output | `safe` | Yes | Before trusting any Python recipe |
| `just inventory` | List tasks and this inventory | `justfile`, `scripts/README.md` | Console output | `safe` | Yes | First check before running pack automation |
| `just audit_scripts` | Show script/catalog drift | `scripts/`, `scripts/README.md` | Console output | `safe` | Yes | During refresh/audit |
| `just helpers` | List the helpers this pack ships | `scripts/*.py` | Console output | `safe` | Yes | Before importing a helper |
| `just test` | Offline package contract + helper tests (includes the governance checker) | `tests/`, every pack file | Console output, exit status | `safe` | Yes | Before claiming any change complete |
| `just check` | Governance coherence checks alone | `scripts/check_governance.py`, governance surfaces | Console output, exit status | `safe` | Yes | After adding, moving or renaming any file |
| `just preflight` | runtimes + audit_scripts + test + check + lint_md | Pack files | Console output | `safe` | Yes | Before commit or handoff |
| `just lint_md` | Markdown lint against `.markdownlint-cli2.jsonc` | `**/*.md` | Console output | `safe` | Yes | Before commit |
| `just context-pack` | Regenerate `.ai-context/governance-pack.md` with Repomix | `repomix.config.json` | `.ai-context/governance-pack.md` | `modifies-files` | Yes | After governance or routing changes |
| `just graph` | Refresh `graphify-out/` (code graph, AST only, no LLM) | Pack source files | `graphify-out/GRAPH_REPORT.md`, `graphify-out/graph.json`, `graphify-out/graph.html` | `modifies-files` | Yes | After adding or changing helpers or tests |
| `just nav_upgrade_dry_run` | Preview the skill-ai-it navigation-layer upgrade | skill-ai-it upgrader | Console output | `safe` | Yes | Before `just nav_upgrade` |
| `just nav_upgrade` | Apply the navigation-layer upgrade | skill-ai-it upgrader | File changes | `review-required` · `modifies-files` | Yes | After reviewing the dry run |
| `just nav_validate` | Validate the navigation layer | skill-ai-it validator | Console output | `safe` | Yes | After an upgrade or periodically |
| `just nav_check_diff` | Confirm only expected governance files changed | git diff | Console output | `safe` | Yes | After an upgrade |
| `just template_sync` | Plan, or with `--apply` create, the interfaces a Device Type's templates promise but its existing Devices lack | `--device-type` (repeatable), `--manufacturer`; `NAUTOBOT_URL`, `NAUTOBOT_TOKEN` | Console; interfaces with `--apply` | `requires-credentials` · `safe` (plan) · `review-required` (apply) | Yes | After adding an interface template to a type that already has Devices |
| `just app_compat` | An app's PyPI metadata against a Nautobot and Python version | `package[==version]` ..., `--nautobot`, `--python` | Console or `--json` | `safe` · `external-network` | Yes | Before pinning an app for an image rebuild |
| `just nav_selftest` | Self-test the skill-ai-it block builders (not this pack) | skill-ai-it templates | Console output | `safe` | Yes | After skill-ai-it templates change |

## Raw Script Inventory

| Script | Purpose | Inputs | Outputs | Safety | Idempotent | When to use |
|---|---|---|---|---|---|---|
| `scripts/nautobot_paging.py` | Fail-closed traversal of a REST listing: `listing()` adds a total order, `traverse()` refuses a listing that repeats, skips or miscounts | A caller-supplied GET function and first URL | List of result rows, or `PagingError` | `safe` | Yes | Import from any reader that pages a Nautobot listing |
| `scripts/nautobot_ipam.py` | Pure IPAM rule: an address's mask is the narrowest `network` Prefix that holds it, never `/32` by default | Prefix dicts and an address | `int` mask or `str` address/mask, or `None` | `safe` | Yes | Import before writing an IP address into Nautobot |
| `scripts/nautobot_masks.py` | Plans and applies the subnet-mask fix for device addresses: each `/32` takes its narrowest network Prefix's mask; placeholder containers and mismatches are reported. Promoted from the UNC script fix_address_masks.py | One Namespace's address and Prefix REST records; for apply, a caller-supplied HTTP callable | `(fix, report)` lists; apply sends batched bulk PATCH | `safe` (plan) · `review-required` · `modifies-state` (apply, through the caller) | Yes | Before or after an address import, to stop `/32` defaults |
| `scripts/nautobot_linkage.py` | Generic hierarchy-break engine: collects what belongs to a Location and reports objects nothing links back to, by rules the caller registers. Listings fail closed through `nautobot_paging`. Promoted from the UNC script site_linkage.py | A caller-supplied GET, a Location, a `Rules` registry | Findings (severity, rule, object); site or estate summaries | `safe` (read-only) | Yes | After onboarding or link fixes, before promoting a site |
| `scripts/nautobot_template_sync.py` | Interface templates missing as interfaces on existing Devices (Nautobot instantiates templates only when a Device is created): pure `plan()` and `payloads()` copy the template's fields as `InterfaceTemplate.instantiate` does on 3.2.3, status Active; an interface that exists by name is never touched. The CLI plans unless `--apply`. Promoted from a UNC session (2026-10-08) | Device, template and interface REST dicts; CLI: `--device-type`, `NAUTOBOT_URL`, `NAUTOBOT_TOKEN` | `[(device, template)]`, POST bodies; CLI exit 1 when interfaces are missing in a plan | `safe` (plan) · `review-required` · `modifies-state` (`--apply`) · `requires-credentials` | Yes | After adding a template to a Device Type that already has Devices |
| `scripts/nautobot_app_compat.py` | App compatibility from PyPI metadata: version, release date, `requires_python`, the `nautobot` requirement in `requires_dist` (extras and `nautobot-<app>` entries skipped), and whether a Nautobot and Python version satisfy them, with a small stdlib specifier check (unparseable means unknown, never compatible) | `package[==version]` ..., `--nautobot`, `--python`; or `assess()` on recorded JSON | One line or JSON row per package; exit 0 only when all are compatible | `safe` · `external-network` | Yes | Before choosing app pins for an upgrade; the install itself is still the proof |
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
