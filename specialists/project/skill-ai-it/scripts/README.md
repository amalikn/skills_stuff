# Script Inventory — skill-ai-it

Runnable scripts for maintaining the **navigation control layer** in target projects. These operate on a project passed via `--project-root`; they do not act on this package unless it is passed
explicitly.

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

| Script | Purpose | Inputs | Outputs | Safety | Idempotent | When to use |
|---|---|---|---|---|---|---|
| `upgrade_navigation_control_layer.py` | Writes/refreshes managed navigation blocks in a target project's `AGENTS.md`, `AI_NAVIGATION.md`, and `scripts/README.md`, stamped with the current `VERSION`. | `--project-root`, `--dry-run`, `--report-json`, `--repair-claude-wrapper` | File changes in the target project; console diff | `review-required` | Yes | After a `VERSION` bump, or to bring a project onto the current control layer |
| `validate_navigation_control_layer.py` | Validates control-layer coherence: managed block integrity, version stamps, required governance files, `context-map.yaml` keys, task-runner references, and governance-checker presence/wiring. | `--project-root`, `--report-json` | Console pass/warn/fail; exit 0/1/2 | `safe` | Yes | After upgrade, or as a periodic audit |
| `agent_usage.py` | Counts tool calls in recent Claude Code transcripts that name a file, folder or command, by tool, so a navigation aid is kept or retired on evidence (Graphify: 0 queries in 30 days, 2026-10-10). Codex and Hermes sessions not read. | terms, `--days`, `--project` | safe; read-only |
| `file_headers.py` | The one header parser every skill-ai-it tool imports (markdown front matter, Python module docstring, `#` comment block in YAML/shell/justfile/TOML, JSON `_meta`), and the triage index `just docs`: one line per file (status, review date, summary) so a file is judged without being opened; `--missing` lists files with no summary. | scopes, `--project-root`, `--missing` | safe; read-only |
| `rotate_records.py` | Rotates CHANGELOG.md / SCRATCHPAD.md into `docs/history/<file>-<stamp>.md` to keep them within 200 lines / 25 KB: oldest first; never undated units, the newest per section, units with the `` `PIN` `` marker (backticked, or `<!-- PIN -->`) or "until resolved", unresolved open items or (for SCRATCHPAD) stamps a live governance file cites; verifies every removed line is in the archive before writing; `--find TERM` / `--show STAMP` recall. | record, `--apply`, `--find`, `--show`, `--keep-days`, `--min-keep` | modifies-state with `--apply` (files only) |
| `adopt_governed_files.py` | Checks a project's adoption of the governed-file standard (justfile recipes and freshness in `check`, AGENTS line, records front matter, baseline) and, with `--apply`, adds only what is missing. skill-slurp-chat runs it at every close. | `--project-root`, `--apply` | modifies-state with `--apply` (files only); idempotent |
| `audit_rotations.py` | Independent audit of rotated records: every content line of each CHANGELOG/SCRATCHPAD before its first rotation (from git) is still live or in `docs/history/`. Run after rotations; exit 1 on any loss. | roots | safe; read-only |
| `budget_plan.py` | One entry point for budgets: measures every file loaded whole; for an over-budget SCRATCHPAD/CHANGELOG runs normalise, rotate, then moves non-working-state sections out (largest first) to `docs/<record>-reference-<n>-<stamp>.md`, indexes them, audits, runs `just check`; reports what still holds a file over and why; refuses symlinked records. | `--project-root`, `--apply` | modifies-state with `--apply` (files only) |
| `normalise_records.py` | Adds only heading lines so rotation can move them: `### <date> — <lead>` above dated bold-lead paragraphs (time-only leads take the date above), `### <lead>` above undated standing facts, `## Update log ...` over a dated header-comment block (plus `Keep: Update log=0`); refuses if an original line changes. | record, `--apply` | modifies-state with `--apply` (files only) |
| `move_sections.py` | Moves named `##` sections of a governed file (AGENTS.md, SCRATCHPAD.md) verbatim into an on-need reference file when durable reference material, not history, holds it over budget; leaves a pointer section naming them, fixes Contents, refuses if a line would be lost. | `--source`, `--dest`, `--title`, `--summary`, section names, `--apply` | modifies-state with `--apply` (files only) |
| `move_doc.py` | Moves a document (default: into its folder's `archive/`) with `git mv`, rewrites every link to it in the link's own style, moves its index line, records the move in a moved-paths map; dated records keep old paths. | path, `--to`, `--moved-paths`, `--apply` | modifies-state with `--apply` (files only) |
| `split_checker.py` | Splits a single-file `scripts/check_governance.py` into the govcheck package (config, helpers, `checks/<family>.py`, the shared engine `templates/govcheck/core.py`) from a families JSON; dry run works on a temporary copy and reports whether the output is identical. | `--project-root`, `--families`, `--docs`, `--python`, `--apply` | modifies-state with `--apply` (files only) |
| `doc_freshness.py` | Lists or checks stale project markdown by three rules: a living document past its review date (`Review by`, or `Last reviewed` + 30 days), a `superseded` file outside `archive/`, a `Depends on` file committed after `Last reviewed`. Baseline ratchet: only new findings fail. Read-only except `--write-baseline`. | `--project-root`, `--check`, `--write-baseline`, `--baseline`, `--window-days` | safe; idempotent |
| `docstring_ratchet.py` | Holds a target project's Python docstrings to the global standard (module, class and function docstrings; `Args:` naming every parameter; `Returns:` when a value is returned) as a ratchet: counts shortfalls per file against a baseline JSON; a new file must be at zero, a count may not rise, a fall must be recorded. Stdlib only. | `--project-root`, `--roots`, `--baseline`, `--write-baseline`, `--list` | Console report; the baseline JSON with `--write-baseline` | `safe` (writes only the baseline when asked) | Yes | When adopting the standard (`--write-baseline`), then in the project's check or before completing work (`just docstrings`) |
| `check_expected_diff.py` | Confirms only expected files changed after an upgrade, against `DEFAULT_EXPECTED` plus `--allow` additions. Requires the target to be a git repo. | `--project-root`, `--allow`, `--report-json` | Console list of expected vs unexpected changes | `safe` | Yes | Immediately after `nav_upgrade` |
| `selftest_blocks.py` | Self-tests the managed-block builders: canonical markers, current `VERSION` stamp, no trailing whitespace or blank runs, every required navigation section present, and a loud failure when a template is unreadable. | none | Console pass/fail; exit 0/1 | `safe` | Yes | After editing any file under `templates/`, or any builder in `upgrade_navigation_control_layer.py`, before running an upgrade against a real project |
| `migrate_legacy_blocks.py` | Moves a project's managed blocks stamped before 2026-09-23 (the layout where projects wrote inside them) to the template-sourced layout. Classifies each block section against every block the skill emitted in that era and today: skill text is replaced by the current block, project sections move outside it, edited skill sections are copied verbatim under `## Moved from the managed block` for trimming by hand. | `--project-root`, `--dry-run` | Rewritten `AGENTS.md`, `AI_NAVIGATION.md`, `scripts/README.md`; console classification | `modifies-files`, `review-required` | Yes (a migrated block is current and is skipped) | `refresh` of a project whose `nav_upgrade` reports `refused-legacy-layout`; run `nav_upgrade` after it |
| `check_governance.py` | Asserts this package's own governance claims: path references resolve, every script is cataloged here, every pattern is named in `SKILL.md`, recipes address the pinned interpreter, and the managed-block `VERSION` is identical on all twelve surfaces that state it. | none | Console pass/fail with an assertion count; exit 0/1 | `safe` | Yes | Before calling any durable change to this package complete |
| `skills_registry.py` | Builds or checks a project area's skills.md: scans the area's `AGENTS.md`, `CLAUDE.md`, `AI_NAVIGATION.md` and `SKILL.md` files for `skill-*` names, resolves each to `skills_stuff`, a project-local folder, an installed-only copy, or not found, and lists which projects use it. Names seen only in plain prose and aliases are reported, not listed. | `--project-root`, `--check` (default) / `--print` / `--write`, `--force`, `--also`, `--ignore`, `--keep`, `--title` | Check: drift report, exit 0 in step / 1 drift. Print: generated file on stdout. Write: skills.md (backup skills.md.bak-YYYYMMDD_hhmm with `--force`) | `safe` (check, print); `review-required` (write) | Yes | When a project area needs its skills list created, or to spot skills added or dropped since it was written |

## Exit Codes

`validate_navigation_control_layer.py` returns `0` PASS, `1` FAIL, `2` WARN (critical checks passed, warnings exist). The others return `0` on success and non-zero on error.

## Coupled Constants

`VERSION` is restated in `upgrade_navigation_control_layer.py` and `validate_navigation_control_layer.py` and stamped into every managed-block template under `templates/`. The two must stay identical
— drift between them silently disables the staleness signal, because `validate` would then be checking for a stamp `upgrade` never writes. Changing the version means changing every surface in one
pass; see `patterns/navigation-control-automation.md`.

**Block CONTENT is not a coupled constant — it has one owner.** The managed blocks are generated by reading `templates/AI_NAVIGATION.md`, `templates/AGENTS-navigation-block.md`, and
`templates/scripts-README.md`. There is deliberately no inlined copy in `upgrade_navigation_control_layer.py`, and a missing or marker-less template stops the run rather than falling back to one.

This is not a style preference. Until 2026-09-23 the navigation block WAS inlined, and it had fallen nine sections behind its template: a project bootstrapped from `templates/AI_NAVIGATION.md` and
then upgraded lost task routing, drift handling, update rules and the answer contract, with the run reporting only `replaced-managed-block`. The other two blocks still matched theirs, so the pattern
looked maintained. Run `selftest_blocks.py` after touching a template or a builder.

## Safety Labels

| Label | Meaning |
|---|---|
| `safe` | Read-only or low-risk repeatable operation |
| `review-required` | Needs human review before execution |
| `destructive` | Deletes, overwrites, migrates, deploys, or changes external state |

## Related

- `patterns/navigation-control-automation.md` — when to run each script, exit codes, `.proposed` handling, version-stamp semantics
- `patterns/script-task-audit-checklist.md` — catalog completeness auditing
- `patterns/governance-checks.md` — the *target project's* own executable checker, a separate layer from these scripts
