---
Title: Changelog
Category: change-log
Status: current
Summary: Newest entries only; older ones rotate to docs/history (search with --find, print with --show).
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/ (`--find`, `--show`)
Last rotated: 20261010_2207
---

# Changelog — skill-ai-it

## Contents

- [20261010_2227 — Memory pointers rotate; no upgrade hint for project-owned blocks; jdm within budget](#20261010_2227--memory-pointers-rotate-no-upgrade-hint-for-project-owned-blocks-jdm-within-budget)
- [20261010_2207 — SKILL.md restructured: 2,074 to 198 lines, detail in references/ by topic](#20261010_2207--skillmd-restructured-2074-to-198-lines-detail-in-references-by-topic)
- [20261010_2156 — Compact navigation template; reference split by topic; adopter documents recipes; budget suggestions](#20261010_2156--compact-navigation-template-reference-split-by-topic-adopter-documents-recipes-budget-suggestions)
- [2026-10-10 — deterministic navigation-control upgrade](#2026-10-10--deterministic-navigation-control-upgrade)
- [20261010_2135 — budget_plan and normalise_records; heading dates and time grouping; runaway incident and fix](#20261010_2135--budget_plan-and-normalise_records-heading-dates-and-time-grouping-runaway-incident-and-fix)
- [20261010_2014 — Rotation fixes (explicit pins, prose units, lazy continuation); move_sections; split audit; adopter fixes](#20261010_2014--rotation-fixes-explicit-pins-prose-units-lazy-continuation-move_sections-split-audit-adopter-fixes)
- [20261010_1833 — Rotation made safe and complete; adopter; headers for every script and config](#20261010_1833--rotation-made-safe-and-complete-adopter-headers-for-every-script-and-config)
- [20261010_1805 — Governed-file tools: rotation by bullet, ticked items resolved; checker standard; slurp rotates](#20261010_1805--governed-file-tools-rotation-by-bullet-ticked-items-resolved-checker-standard-slurp-rotates)
- [20261010_1830 — feat: doc_freshness.py; Graphify disabled](#20261010_1830--feat-doc_freshnesspy-graphify-disabled)
- [20261008_2224 — feat: docstring_ratchet.py, the global docstring standard as a ratchet for any project](#20261008_2224--feat-docstring_ratchetpy-the-global-docstring-standard-as-a-ratchet-for-any-project)
- [20261007_2124 — fix: the upgrade CHANGELOG entry follows the file's order](#20261007_2124--fix-the-upgrade-changelog-entry-follows-the-files-order)
- [20261007_2102 — feat: migrate_legacy_blocks.py, the refresh step for pre-2026-09-23 blocks; the seven refused projects migrated](#20261007_2102--feat-migrate_legacy_blockspy-the-refresh-step-for-pre-2026-09-23-blocks-the-seven-refused-projects-migrated)
- [20261007_2049 — fix: nav_upgrade refuses legacy-layout blocks; context-map edited in place; recipe renames reach the docs](#20261007_2049--fix-nav_upgrade-refuses-legacy-layout-blocks-context-map-edited-in-place-recipe-renames-reach-the-docs)

## 20261010_2227 — Memory pointers rotate; no upgrade hint for project-owned blocks; jdm within budget

- normalise_records.py: Memory pointers are a dated log of memory keys, so their dated blocks get headings and rotate (jdm: 198 lines held its
  SCRATCHPAD over budget). budget_plan.py: no "run the upgrade first" hint for a block carrying skill-ai-it:manual (the upgrader never replaces it).
  Tests 37 to 38 plus a normaliser case, each negative-tested.
- jdm brought within budget by hand on top of the tools: guard registries (gate surface, model-count skip) follow moved text; a blockquote is not a heading, so
  the resolved readiness block was moved with a one-off verified cut; three pointer sections merged into one.

## 20261010_2207 — SKILL.md restructured: 2,074 to 198 lines, detail in references/ by topic

- SKILL.md restructured for progressive disclosure: 2,074 to 198 lines (112 KB to 16 KB), within the 200-line / 25 KB budget. Detail moved
  verbatim with move_sections.py into 18 topic files under references/ (46 to 319 lines; index references/readme.md), each linked by one line at the
  step that needs it; SKILL.md keeps use-when, inputs, modes, repeat-safety, the governed-file and freshness rules, workflow and a template and
  pattern catalogue. Verified: all 13,844 words of the old file present (only the moved sections' Contents links dropped); in-page links repointed;
  install symlink is whole-folder, so references/ resolves.
- move_sections.py: moves `###` and `####` sections (to the next heading at their level); `--pointer-line` leaves one linked line instead of a
  pointer section; relinks only links whose target exists (example links stay as written; 10 example lines restored after an over-eager relink);
  Contents anchors keep double hyphens as GitHub and VS Code render them. Tests 35 to 37.
- Larger references (files-context-map 319, files-ai-navigation 228, script-task-inventory 224 lines) are read on need; split them if they are often opened.

## 20261010_2156 — Compact navigation template; reference split by topic; adopter documents recipes; budget suggestions

- Navigation template compacted (version `2026-10-10-compact-v1`): templates/AI_NAVIGATION.md 279 to 96 lines, all 13 required sections kept,
  each a few lines linking to its topic file; the original text moved verbatim to `patterns/navigation/` (four files of 59 to 95 lines plus an index,
  split so a reader opens only the topic it needs; operator). Graphify steps dropped from the block. Version restated in templates, SKILL.md,
  context-map.yaml, patterns and the checker registry. Canary: skill-ai-it AI_NAVIGATION.md 254 to 79 lines; UNC 355 to 155, outside-block text identical.
- upgrade_navigation_control_layer.py no longer renames recipe names inside SCRATCHPAD.md (it made a historical sentence false).
- adopt_governed_files.py documents every recipe it adds in scripts/README.md (jdm requires it); budget_plan.py reports SKILL.md too, says to
  run the navigation upgrade first, and prints `move-sections` suggestions for reference-like sections (outside managed blocks), never applied.
- Tests 33 to 35, each negative-tested; selftest 29 pass.

## 2026-10-10 — deterministic navigation-control upgrade

<!-- skill-ai-it-upgrade: 2026-10-10-compact-v1 -->

- Applied `skill-ai-it` deterministic navigation-control upgrade.
- Upgraded managed navigation/scripts blocks to version `2026-10-10-compact-v1`.
- Ensured `context-map.yaml` contains `skill_ai_it_version`, `audit_checks`, `promotion_rules`, `context_recovery`, and `update_rules`.
- Preserved user-authored content outside managed blocks.
- Generated outputs remain support-only; no `.archcore/` promotion was performed.

Applied to: AI_NAVIGATION.md, AGENTS.md, SCRATCHPAD.md

## 20261010_2135 — budget_plan and normalise_records; heading dates and time grouping; runaway incident and fix

- New scripts/budget_plan.py (one entry point: measure, normalise, rotate, move non-working-state sections, index, audit, project check; reports what
  still holds a file over; refuses symlinked records) and scripts/normalise_records.py (adds dated headings above bold-lead paragraphs, standing-fact
  headings, an Update log heading over dated header comments; refuses if a line changes). `budget` recipe in justfile, template and adopter.
- rotate_records.py: written dates in headings ("21 September 2026") date and group sections; time suffixes ("~1:35p") no longer split a group.
- move_sections.py relinks relative links for the destination; adopt_governed_files.py refuses symlinked governed files and creates a missing
  justfile; move_doc.py --keep-records can be repeated. Tests 22 to 33, each negative-tested.
- Incident: an in-session loop over 23 projects (operator stopped it: "stop running batches"). In jdm the planner moved its own pointer section each
  pass and wrote about 10,000 docs/scratchpad-reference-* files; jdm restored from git (clean before the run). Fixed: pointer headings are working
  state, a move that does not shrink the file stops the loop, MAX_MOVES 8; test added. Canary of nine projects: eight within budget, audits clean;
  jdm reverted (its guards need registry updates; a 199-line Memory pointers section holds it).
- Operator rule: canary, then hand the operator per-project commands; never batch in-session.

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
