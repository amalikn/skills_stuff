---
Title: Changelog
Category: change-log
Status: current
Summary: Newest entries only; older ones rotate to docs/history (search with --find, print with --show).
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/ (`--find`, `--show`)
Last rotated: 20261010_2017
---

# Changelog — skill-ai-it

## Contents

- [20261010_2014 — Rotation fixes (explicit pins, prose units, lazy continuation); move_sections; split audit; adopter fixes](#20261010_2014--rotation-fixes-explicit-pins-prose-units-lazy-continuation-move_sections-split-audit-adopter-fixes)
- [20261010_1833 — Rotation made safe and complete; adopter; headers for every script and config](#20261010_1833--rotation-made-safe-and-complete-adopter-headers-for-every-script-and-config)
- [20261010_1805 — Governed-file tools: rotation by bullet, ticked items resolved; checker standard; slurp rotates](#20261010_1805--governed-file-tools-rotation-by-bullet-ticked-items-resolved-checker-standard-slurp-rotates)
- [20261010_1830 — feat: doc_freshness.py; Graphify disabled](#20261010_1830--feat-doc_freshnesspy-graphify-disabled)
- [20261008_2224 — feat: docstring_ratchet.py, the global docstring standard as a ratchet for any project](#20261008_2224--feat-docstring_ratchetpy-the-global-docstring-standard-as-a-ratchet-for-any-project)
- [20261007_2124 — fix: the upgrade CHANGELOG entry follows the file's order](#20261007_2124--fix-the-upgrade-changelog-entry-follows-the-files-order)
- [20261007_2102 — feat: migrate_legacy_blocks.py, the refresh step for pre-2026-09-23 blocks; the seven refused projects migrated](#20261007_2102--feat-migrate_legacy_blockspy-the-refresh-step-for-pre-2026-09-23-blocks-the-seven-refused-projects-migrated)
- [20261007_2049 — fix: nav_upgrade refuses legacy-layout blocks; context-map edited in place; recipe renames reach the docs](#20261007_2049--fix-nav_upgrade-refuses-legacy-layout-blocks-context-map-edited-in-place-recipe-renames-reach-the-docs)
- [20260529_HHMM — deterministic navigation-control automation](#20260529_hhmm--deterministic-navigation-control-automation)

## 20261010_2014 — Rotation fixes (explicit pins, prose units, lazy continuation); move_sections; split audit; adopter fixes

- `rotate_records.py`: pins only on the explicit marker (`` `PIN` `` or `<!-- PIN -->`; a bare "PIN" substring had pinned ansible-wifi entries about
  captive-portal PINs); a dated `###` subsection of prose rotates as one unit; wrapped items keep their unindented (lazy) continuation lines (before,
  heads moved and tails stayed live: 39 tails in 5 projects, repaired). Over-budget note names `move_sections.py`.
- New `move_sections.py` (+ `move-sections` recipe in justfile and template, catalogue row, tests): moves named `##` sections verbatim to an on-need
  reference doc with a pointer; refuses on loss. Promoted from a hand-written session script (operator: logic belongs in the skill).
- `audit_rotations.py`: reports SPLIT entries; counts sections moved by `move_sections.py` (provenance line) as kept.
- `adopt_governed_files.py`: adds a `check` recipe when a project has none (smc-file-writing-analysis gated nothing); `move-sections` in the recipe set;
  `ai_it` detected with aligned spacing (atar got a duplicate); new recipes reuse the project's interpreter (of-si `{{ai_py}}`) and drop `_require-venv`
  when the project lacks it.
- SKILL.md Rotation bullet and skill-slurp-chat step 7: a record left over budget is unfinished; reference goes out with `move-sections`. SKILL.md held
  to its ratchet (2,074 lines, 67 bytes smaller) by replacing the hand-written freshness bootstrap steps with the adopter call.
- Tests 14 to 22 (new: explicit pin, prose subsection, lazy continuation, move_sections x3, split audit x2, adopter x3), each negative-tested; check 229 pass.

## 20261010_1833 — Rotation made safe and complete; adopter; headers for every script and config

- `rotate_records.py`: Contents is only its link lines (a 424-line prose block was dropped in vocus-profitability, restored); whole-file verification; open items beyond the newest 3 go to a live tracker; `Keep` per section; dated sections grouped; numbered items; git-blame dates for undated entries. `audit_rotations.py`: 39 records clean.
- `adopt_governed_files.py` (slurp runs it), rule 6 `checker-size`, JSON exempt from headers, nested projects skipped. Rolled out to 25 projects.

## 20261010_1805 — Governed-file tools: rotation by bullet, ticked items resolved; checker standard; slurp rotates

- `rotate_records.py`: SCRATCHPAD units are bullets (a `###` subheading travels with its first bullet; undated bullets take its date); `- [x]` and
  `~~` count as resolved. UNC SCRATCHPAD 766 to 674 lines. skill-slurp-chat Step 7 runs `just rotate --apply` when a record is over budget.
- Standard and tools of this day: `file_headers.py`, `doc_freshness.py` rules 4-5, `move_doc.py`, `split_checker.py`, `templates/govcheck/`,
  `patterns/governance-checks.md` "Structure and growth" (reviewed). Why: UNC `docs/reports/knowledge-tooling/governance-surface-management-20261010_1745.md`.

## 20261010_1830 — feat: doc_freshness.py; Graphify disabled

- **Added** `scripts/doc_freshness.py` (operator, 2026-10-10, option B of the OKF adoption assessment in unified-network-controller
  `docs/reports/knowledge-tooling/okf-adoption-assessment-20261010_1700.md`): three rules (review due, superseded outside `archive/`, a `Depends on`
  file changed after `Last reviewed`) as a baseline ratchet. Wired into `templates/justfile` (`check` runs `--check`; new `stale` recipe), the
  embedded justfile in SKILL.md, this package's own justfile, SKILL.md "Document freshness" and the quality checklist. Negative-tested in
  unified-network-controller (each rule fails, exit 1; removal clears it). This package's own finding (`patterns/governance-checks.md`, review due
  2026-09-10) is baselined, not stamped: it needs a real review.
- **Added** `scripts/agent_usage.py` (`just agent_usage <terms>`): counts agent tool calls naming a file or command in recent Claude transcripts;
  promoted from the session that measured Graphify and wiki usage.
- **Disabled** Graphify (operator): SKILL.md step 9, the mode table, "Graphify initialization and refresh", the embedded preflight and the
  compaction-recovery step; `templates/context_preflight.sh` skips it unless `GRAPHIFY_ENABLED=1`; `templates/context-map.yaml` and
  `upgrade_navigation_control_layer.py` say not to regenerate it. Text kept for re-enabling. Measured cause: 0 graph queries in 30 days against
  thousands of rebuilds. The managed navigation block still names `graphify-out/` (changing it would put every governed project into drift); projects
  exempt those paths in `CONDITIONAL_PATHS`.

## 20261008_2224 — feat: docstring_ratchet.py, the global docstring standard as a ratchet for any project

- Operator (2026-10-08, in unified-network-controller): "create the docstrings for the code whenever you are creating or updating a script",
  "specify what are the arguments passed and what is returned", "make it as a standard for all the scripts". The standard is in the global policy
  and governance `categories/naming-and-file-summary-guide.md` (Code docstrings).
- `scripts/docstring_ratchet.py` (recipe `just docstrings`): per-file shortfalls (absent docstring, a parameter not under `Args:`, a returned value
  without `Returns:`) against `scripts/docstring-baseline.json`; `--write-baseline` adopts the standard on a project with legacy code. Same rule as
  unified-network-controller's `check_docstrings`; on that project it reports the same 1737 shortfalls in 132 files and exits 0.
- Not yet applied to this pack's own scripts (129 shortfalls in 7 files); adopting it here is a separate change.

## 20261007_2124 — fix: the upgrade CHANGELOG entry follows the file's order

- `append_changelog` appended at the end of every CHANGELOG, so newest-first files needed the entry moved to the top by hand on every refresh (skill-smc,
  skill-cambium, and four more in today's run). `changelog_is_newest_first` now reads the dates in the `##` headings (`YYYYMMDD_hhmm`, `YYYY-MM-DD`, or a
  date inside a version heading) and compares the first two that differ; `place_changelog_entry` puts the entry above the first dated section and first in
  `## Contents` for newest-first files, and appends (last in Contents) otherwise, including when the order cannot be told.
- Six new self-tests (29 in all). On the committed CHANGELOGs of the twelve projects in today's run, the detected order matches the hand judgement for each.

## 20261007_2102 — feat: migrate_legacy_blocks.py, the refresh step for pre-2026-09-23 blocks; the seven refused projects migrated

- **New `scripts/migrate_legacy_blocks.py`, recipe `nav_migrate_legacy <project> [--dry-run]`.** It rebuilds every block the skill emitted while the `2026-08-11`
  stamp was current (builders and templates of 3ab6c94, 1567158, adcbea4 and 293c42b^) plus the current ones, and classifies each section of a project's legacy
  block by comparing normalised text: skill text is dropped for the current block, project sections move outside it (above when they preceded every skill
  section), and an edited skill section is copied verbatim under `## Moved from the managed block` and the run exits 3 until it is trimmed.
- **Run on the seven refused projects:** psy-assess, islam and japan were mechanical. health and cambium-swap kept their scripts-README rules as *Project
  execution notes*; atar's no-memory-bank routing became *Project deviations from the managed block*; unified-network-controller kept 113 rule lines above its
  AGENTS block and its routing under *Project routing additions*. health and unified-network-controller registered `.ai-context/repo-pack.md` in
  `CONDITIONAL_PATHS`. All twelve projects of the snake_case run are now on `2026-10-07-snake-case-recipes-v1`.
- islam's `context-map.yaml` took the `update_rules` merge as a text edit (same data as the re-dump, comments kept), not the lossy re-dump.
- Newest-first CHANGELOGs in skill-openwisp, skill-nautobot, skill-smc and skill-eval-manager had the upgrade entry moved to the top by hand; the open item on
  the upgrader's append position stands.

## 20261007_2049 — fix: nav_upgrade refuses legacy-layout blocks; context-map edited in place; recipe renames reach the docs

Found running `nav_upgrade` across the 12 projects still on kebab-case recipes, pilot first (skill-openwisp), then the rest.

- **Data loss, caught in diff review.** Projects stamped `2026-08-11` hold their own content inside the managed blocks (the older layout). The stamp passed the provenance
  gate, so the upgrade replaced the blocks wholesale: 171 lines from cambium-swap `scripts/README.md`, 113 from unified-network-controller `AGENTS.md`, and more across seven
  projects. All seven were restored from git and given only the recipe renames. New gate 3 in `block_is_replaceable`: a block stamped before `LAYOUT_SINCE` (`2026-09-23`)
  is refused as `legacy-layout`, exit 3, with `/skill-ai-it refresh` as the way forward. Three new self-tests.
- **`context-map.yaml` lost every comment.** The upgrader re-dumped the parsed file, so a one-line stamp change churned 622 lines in skill-openwisp and dropped its 5 comments.
  The file is now edited as text; only a nested `update_rules` merge re-dumps, and that path flags the run for review.
- **Recipe renames stopped at the justfile.** `scripts/README.md` task tables kept the old names, and the project checkers failed on recipes that no longer exist. Renames now
  also apply to `RECIPE_DOCS` (root governance docs, `scripts/README.md`, `SETUP.md`, `requirements.txt`); `CHANGELOG.md` is left as history.
- Upgraded in full: skill-openwisp, skill-nautobot, skill-smc, skill-eval-manager, enterprise-strategy. Recipes renamed, blocks waiting for `refresh`: psy-assess, health,
  islam, japan, atar, unified-network-controller, cambium-swap.

## 20260529_HHMM — deterministic navigation-control automation

### Added

- `scripts/upgrade_navigation_control_layer.py` — deterministic, idempotent upgrade script for navigation/control-layer files. Upgrades old managed block markers, adds version stamps, adds missing
  context-map.yaml keys (audit_checks, promotion_rules, context_recovery, update_rules). Supports --dry-run, --report-json, and .proposed fallback for risky YAML merges.

- `scripts/validate_navigation_control_layer.py` — deterministic validation script. Checks governance file presence, managed block integrity, version consistency, YAML validity, required schema keys,
  generated-output policy, context compaction recovery, script/task governance, companion consistency, and stale claim detection.

- `scripts/check_expected_diff.py` — git-diff check that only expected governance files (AGENTS.md, AI_NAVIGATION.md, CHANGELOG.md, context-map.yaml, scripts/README.md) changed after an upgrade.
  Detects accidental modifications to source files.

- `templates/update_rules.yaml` — default companion-file update rules template (governance_navigation section with AGENTS.md, AI_NAVIGATION.md, context-map.yaml, scripts/README.md, new_script_added
  relationships).

- `patterns/navigation-control-automation.md` — explains why automation exists, when to run each script, how to interpret exit codes, how to handle .proposed files, and how this complements
  patterns/drift-audit.md and patterns/script-task-audit-checklist.md.

### Changed

- `templates/justfile` — added 4 new targets: nav-upgrade-dry-run, nav-upgrade, nav-validate, nav-check-diff.
- `templates/scripts-README.md` — added entries for the three new automation scripts in the Task Inventory table.
- `SKILL.md` — added "Deterministic Navigation-Control Automation" section with recommended 6-step refresh order, key rules, and script table.
- `README.md` — added "Deterministic navigation-control automation" section with component table and key rules.
- `ARCHITECTURE.md` — added "Deterministic navigation-control automation" section with script table and references to templates/ and patterns/.

### Notes

- Scripts are the primary mechanism for existing-project upgrade. Markdown patterns are policy/explanation.
- All scripts are idempotent and safe to rerun. --dry-run mode provides safe preview.
- Upgrade script does not create .archcore/, .ai-context/, or graphify-out/.
- Generated outputs remain support-only. No automatic promotion.
- Fallback: .proposed files written when YAML merge is too risky.
