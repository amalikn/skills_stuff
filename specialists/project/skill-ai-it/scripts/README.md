---
Title: Script Inventory — skill-ai-it
Category: script-catalog
Status: current
Authority: canonical
Scope: Every script and task in this package: purpose, inputs, outputs, safety label, idempotency
Last reviewed: 2026-10-14
Summary: >-
  Catalog of the package's scripts and just recipes, the execution policy and the coupled constants (including the managed-block version stamp).
---

# Script Inventory — skill-ai-it

Runnable scripts for maintaining the **navigation control layer** in target projects. These operate on a project passed via `--project-root`; they do not act on this package unless it is passed
explicitly.

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

| Script | Purpose | Inputs | Outputs | Safety | Idempotent | When to use |
|---|---|---|---|---|---|---|
| `upgrade_navigation_control_layer.py` | Writes/refreshes managed navigation blocks in a target project's `AGENTS.md`, `AI_NAVIGATION.md`, and `scripts/README.md`, stamped with the current `VERSION`. | `--project-root`, `--dry-run`, `--report-json`, `--repair-claude-wrapper` | File changes in the target project; console diff | `review-required` | Yes | After a `VERSION` bump, or to bring a project onto the current control layer |
| `validate_navigation_control_layer.py` | Validates control-layer coherence: managed block integrity, version stamps, required governance files, `context-map.yaml` keys, task-runner references, and governance-checker presence/wiring. | `--project-root`, `--report-json` | Console pass/warn/fail; exit 0/1/2 | `safe` | Yes | After upgrade, or as a periodic audit |
| `agent_usage.py` | Counts tool calls in recent Claude Code transcripts that name a file, folder or command, by tool, so a navigation aid is kept or retired on evidence (Graphify: 0 queries in 30 days, 2026-10-10). `--md-reads` counts how large Markdown is read (hand-built outline greps, `just outline`/`just section` calls, whole and ranged Reads, subagent transcripts included) for the md_sections trial. Codex and Hermes sessions not read. | terms, `--days`, `--project`, `--md-reads` | safe; read-only |
| `file_headers.py` | The one header parser every skill-ai-it tool imports (markdown front matter, Python module docstring, `#` comment block in YAML/shell/justfile/TOML, JSON `_meta`), and the triage index `just docs`: one line per file (status, review date, summary) so a file is judged without being opened; `--missing` lists files with no summary. | scopes, `--project-root`, `--missing` | safe; read-only |
| `rotate_records.py` | Rotates CHANGELOG.md / SCRATCHPAD.md into `docs/history/<file>-<stamp>.md` to keep them within 200 lines / 25 KB: oldest first; never undated units, the newest per section, units with the `` `PIN` `` marker (backticked, or `<!-- PIN -->`) or "until resolved", unresolved open items or (for SCRATCHPAD) stamps a live governance file cites; verifies every removed line is in the archive before writing; `--find TERM` / `--show STAMP` recall. | record, `--apply`, `--find`, `--show`, `--keep-days`, `--min-keep` | modifies-state with `--apply` (files only) |
| `roadmap_trim.py` | Moves ROADMAP.md's done items (`- [x]`, and the `## Completed` section) verbatim to `docs/history/roadmap-<stamp>.md` under their section headings and indexes it; keeps open, `` `PIN` ``, undated and recent (`--keep-days`, default 7) items; no ROADMAP, no change. Promoted from unified-network-controller 2026-10-14. Run by a project's `just rotate`. Plan unless `--apply`; `modifies-files` | | |
| `adopt_governed_files.py` | Checks a project's adoption of the governed-file standard (justfile recipes, freshness and file roles in `check`, AGENTS line, `---` front matter on root files and records, README's `Budget`, both baselines; over-budget sizes it grows are re-recorded) and, with `--apply`, adds only what is missing. skill-slurp-chat runs it at every close. | `--project-root`, `--apply` | modifies-state with `--apply` (files only); idempotent |
| `adopt_code_map.py` | Creates a project's `code-map.toml` from skill-coder's template when it has code and none (scan roots, pinned Python, no example layers), and adds a `[modules]` entry for every Python script not listed yet (outside `src/`), each marked `unreviewed:` so the project's check stays red until someone decides; never changes an existing decision, reports entries for files that are gone. Run by `govern` after `adopt_governed_files.py`. Under 1 s. | `--project-root`, `--apply` | modifies-state with `--apply` (one file); idempotent | <!-- path:example -->
| `audit_rotations.py` | Independent audit of rotated records: every content line of each CHANGELOG/SCRATCHPAD before its first rotation (from git) is still live or in `docs/history/`. Run after rotations; exit 1 on any loss. Lines edited on purpose are accepted in each project's own rotation-audit baseline, docs/history/rotation-audit-baseline.txt in that project (`<record>\t<line>`, `#` reason); stale rows are reported. | roots | safe; read-only |
| `add_changelog_entry.py` | Adds one CHANGELOG entry in the project's own heading style (dash, bracket, dated with label, plain date, bare stamp) and order (newest or oldest first), with its Contents line; reads the clock; verifies only lines were added; warns on body lines over 200 columns and on an over-budget file. | `--title`, `--body`/`--body-file`, `--label`, `--stamp`, `--apply` | modifies-state with `--apply` (files only) |
| `budget_plan.py` | One entry point for budgets: measures every file loaded whole; for an over-budget SCRATCHPAD/CHANGELOG first tidies pointer clutter (duplicate tracker pointers, numbered pointer sections), runs normalise, rotate, then moves non-working-state sections out (largest first) into one shared pointer section, to `docs/<record>-reference-<n>-<stamp>.md`, indexes them, audits, runs `just check`; reports what still holds a file over and why; refuses symlinked records. | `--project-root`, `--apply` | modifies-state with `--apply` (files only) |
| `normalise_records.py` | Adds only heading lines so rotation can move them: `### <date> — <lead>` above dated bold-lead paragraphs (time-only leads take the date above), `### <lead>` above undated standing facts, `## Update log ...` over a dated header-comment block (plus `Keep: Update log=0`); refuses if an original line changes. | record, `--apply` | modifies-state with `--apply` (files only) |
| `move_sections.py` | Moves named `##`/`###`/`####` sections of a governed file verbatim into an on-need reference file; leaves a pointer (section, one line, or a bullet in one shared section with `--pointer-into`); fixes Contents; relinks real relative links; repoints `#anchor` links that cross the move, in both files and in other project markdown; refuses if a line would be lost. | `--source`, `--dest`, `--title`, `--summary`, section names, `--apply` | modifies-state with `--apply` (files only) |
| `md_sections.py` | Reads a large Markdown file by section: `outline` lists each heading with its line range and size; `section` prints one section by exact title (leading section number optional), `Parent > Child` path, `#anchor` or `~substring`, and refuses an ambiguous selector by listing every match (exit 3; `--all` prints them). Skips front matter and fenced code; ATX and one-line setext headings. Recipes `just outline`, `just section`. | `outline <file> [--depth N] [--json]`, `section <file> <selector> [--max-lines N] [--no-children] [--all]` | read-only |
| `move_doc.py` | Moves a document (default: into its folder's `archive/`) with `git mv`, rewrites every link to it in the link's own style, moves its index line, records the move in a moved-paths map; dated records keep old paths. | path, `--to`, `--moved-paths`, `--apply` | modifies-state with `--apply` (files only) |
| `split_checker.py` | Splits a single-file `scripts/check_governance.py` into the govcheck package (config, helpers, `checks/<family>.py`, the shared engine `templates/govcheck/core.py`) from a families JSON; dry run works on a temporary copy and reports whether the output is identical. | `--project-root`, `--families`, `--docs`, `--python`, `--apply` | modifies-state with `--apply` (files only) |
| `doc_freshness.py` | Lists or checks stale project markdown by three rules: a living document past its review date (`Review by`, or `Last reviewed` + 30 days), a `superseded` file outside `archive/`, a `Depends on` file committed after `Last reviewed`. Baseline ratchet: only new findings fail. Read-only except `--write-baseline`. | `--project-root`, `--check`, `--write-baseline`, `--prune-baseline` (drops resolved entries only, keeps recorded sizes; govern runs it), `--baseline`, `--window-days` | safe; idempotent |
| `role_check.py` | Checks a project's root governance files against their roles (`references/governed-file-roles.md`): `---` front matter with Title and Summary on README, AGENTS, AI_NAVIGATION, ARCHITECTURE, CONVENTIONS, SETUP, ROADMAP, CHANGELOG, SCRATCHPAD; CLAUDE.md opens with `@AGENTS.md`; README has a quick start or SETUP.md link and no status/history heading; ROADMAP has a dated current phase and no done items past 7 days or Completed narrative; no `##`/`###` section duplicated across root files; context-map.yaml parses with no repeated key (PyYAML; skipped, not passed, without it). Baseline ratchet (`scripts/role-check-baseline.json`, written by `adopt_governed_files.py`): only new findings fail. Run by `just check` and `just roles`. Read-only except `--write-baseline` and `--prune-baseline` (drops resolved entries only; govern runs it). | `--project-root`, `--check`, `--write-baseline`, `--prune-baseline` | safe; idempotent |
| `govern_guard.py` | First step of `just govern`: lists the governed paths (root governance files, `justfile`, `scripts/README.md`, baselines, `docs/history/`, `docs/trackers/`) holding uncommitted work and exits 1, so govern's edits never mix with the operator's (enterprise-strategy, 2026-10-14). Passes a clean tree or a folder outside git; `GOVERN_ALLOW_DIRTY=1` skips it. | `--project-root` | safe; read-only |
| `doc-freshness-baseline.json`, `role-check-baseline.json` | This package's own baselines for `doc_freshness.py` and `role_check.py` (findings excused when recorded; only new ones fail). Written with `--write-baseline`, never by hand. | | data; machine-written |
| `docstring_ratchet.py` | Holds a target project's Python docstrings to the global standard (module, class and function docstrings; `Args:` naming every parameter; `Returns:` when a value is returned) as a ratchet: counts shortfalls per file against a baseline JSON; a new file must be at zero, a count may not rise, a fall must be recorded. Stdlib only. | `--project-root`, `--roots`, `--baseline`, `--write-baseline`, `--list` | Console report; the baseline JSON with `--write-baseline` | `safe` (writes only the baseline when asked) | Yes | When adopting the standard (`--write-baseline`), then in the project's check or before completing work (`just docstrings`) |
| `check_expected_diff.py` | Confirms only expected files changed after an upgrade, against `DEFAULT_EXPECTED` plus `--allow` additions. Requires the target to be a git repo. | `--project-root`, `--allow`, `--report-json` | Console list of expected vs unexpected changes | `safe` | Yes | Immediately after `nav-upgrade` |
| `check_outside_blocks.py` | Confirms an upgrade changed only text inside the managed blocks: each file with its blocks removed must match a git ref (default HEAD). Found needed on enterprise-strategy 2026-10-12, where a formatter joined two marker lines. | `--project-root`, `--ref`, `--files` | One OK/DIFFERS line per file, a short diff; exit 0/1 | `safe` | Yes | After `nav-upgrade`, before committing (`just nav-check-blocks`) |
| `yaml_key_diff.py` | Compares a YAML file (default `context-map.yaml`) with a git ref by key, and lists the comments the working copy lost. The upgrader's `update_rules` merge re-serialises the file and drops every comment, the purpose header included (smc-resiliency, 2026-10-14). Needs PyYAML (venv python). | `--project-root`, `--file`, `--ref` | Key changes (`added`/`removed`/`changed`), lost comments with old line numbers; exit 0 none lost, 1 lost, 2 read error | `safe` | Yes | After `nav-upgrade` when it warns of a re-serialised context map (`just nav-check-context-map`) |
| `selftest_blocks.py` | Self-tests the managed-block builders: canonical markers, current `VERSION` stamp, no trailing whitespace or blank runs, every required navigation section present, and a loud failure when a template is unreadable. | none | Console pass/fail; exit 0/1 | `safe` | Yes | After editing any file under `templates/`, or any builder in `upgrade_navigation_control_layer.py`, before running an upgrade against a real project |
| `migrate_legacy_blocks.py` | Moves a project's managed blocks stamped before 2026-09-23 (the layout where projects wrote inside them) to the template-sourced layout. Classifies each block section against every block the skill emitted in that era and today: skill text is replaced by the current block, project sections move outside it, edited skill sections are copied verbatim under `## Moved from the managed block` for trimming by hand. | `--project-root`, `--dry-run` | Rewritten `AGENTS.md`, `AI_NAVIGATION.md`, `scripts/README.md`; console classification | `modifies-files`, `review-required` | Yes (a migrated block is current and is skipped) | `refresh` of a project whose `nav-upgrade` reports `refused-legacy-layout`; run `nav-upgrade` after it |
| `check_governance.py` | Asserts this package's own governance claims: path references resolve, every script is cataloged here, every pattern is named in `SKILL.md`, recipes address the pinned interpreter, and the managed-block `VERSION` is identical on all twelve surfaces that state it. | none | Console pass/fail with an assertion count; exit 0/1 | `safe` | Yes | Before calling any durable change to this package complete |
| `target_map.py` | Validates a project's target-map.yaml (goals, targets, per-criterion verdicts with evidence and dates; `--schema` lists every field's level and reason) and renders its tracker, plus the summary table into `embed` pages between the target-map markers. Sources may be numbered criteria sections or bullet plans (`exit_line`, `checklist_line`); `changelog.started_only` limits the change-log rule to started targets. `--init` prints a starter map, `--sync` shows (with `--write` appends) missing targets, `--show [ID]` reads one. Promoted from unified-network-controller 2026-10-21 ([reference](../references/target-map-and-timeline.md)). | `--project-root`, `--write`, `--schema`, `--init` options, `--sync`, `--show`, `--today` | the tracker at `render_to`, embed blocks; console report | `safe` without `--write`; `review-required` with `--sync --write` (appends to the map) | Yes | `just target-map <project>`; a project's own `just target-map` and govcheck |
| `table_wrap.py` | Wraps a generated markdown table the way the markdown hook does (table-reflow on a temporary file, `--width N --measure-rendered`) so a generated block and the hook agree; used by `plan_timeline.py` and `target_map.py` (`wrap_width`, default 200, 0 for one line per row). Imported, not run. Added 2026-10-22. | a table, a width | the wrapped table | `safe` (no writes) | Yes | imported by the two renderers |
| `plan_timeline.py` | Renders a page's Timeline block from dated rows (`due`, `week`, `done`, `flag`, `kind` plan/fixed/extra/parked; `columns` and `note` as data) with each row's schedule worked out for today: LATE with days, DUE TODAY, Done, Not yet due, Parked; a passed date beats a flag. Writes only between the plan-timeline markers and only with `--write`. Promoted from unified-network-controller 2026-10-21. | `--project-root`, `--data`, `--write`, `--today` | the Timeline block in `render_to`; console report | `safe` (docs only, writes with `--write`) | Yes | `just plan-timeline <project>`; a project's `just plan-timeline` and commit gate |
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

## Governance recipes (skill-ai-it)

- `just target-map <project> [--write]`, `just plan-timeline <project> [--write]`: a project's generated trackers; plan by default. `just test`: this package's offline tests. `safe`.
- `just stale`: stale docs by rule (review due, superseded outside archive/, a Depends on file changed). Read-only; `safe`.
- `just govern [project]`: one-step governance of a project (default this package): `govern_guard.py` (stops on uncommitted governed files; `GOVERN_ALLOW_DIRTY=1` to override), the navigation-block upgrade when its dry run is clean (else: run refresh), `adopt_governed_files.py --apply`, `adopt_code_map.py --apply`, `budget_plan.py --apply` (runs the project's `just check`), `--prune-baseline` on both baselines, `role_check.py`; prints one summary line naming what still needs attention; under 60 s (about 1 s measured 2026-10-14). Projects get their own `just govern` from the template. `modifies-files`.
- `just roles-fleet`: one role-check summary line per governed project, to track the role-check rollout. Read-only; `safe`.
- `just roles`: root governance files outside their roles (front matter, README quick start, ROADMAP shape, duplicated sections). Read-only; `safe`.
- `just history <term>`: search rotated CHANGELOG (or SCRATCHPAD) entries in docs/history. Read-only; `safe`.
- `just history-show <stamp>`: print one rotated entry. Read-only; `safe`.
- `just rotate [--apply]`: move old CHANGELOG/SCRATCHPAD entries to docs/history, verified. Plan by default; `modifies-files`.
- `just budget [--apply]`: bring governed files within budget (normalise, rotate, move reference sections, audit, check). Plan by default; `modifies-files`.
- `just changelog-entry --title ... --body-file ...`: add a CHANGELOG entry in this project's style, with its Contents line. Plan by default; `modifies-files`.
- `just move-sections ...`: move named sections verbatim to an on-need reference doc. Plan by default; `modifies-files`.
