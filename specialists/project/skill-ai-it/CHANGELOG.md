---
Title: Changelog
Category: change-log
Status: current
Authority: record
Scope: Dated changes to the skill-ai-it package
Last reviewed: 2026-10-14
Summary: Newest entries only; older ones rotate to docs/history (search with --find, print with --show).
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/ (`--find`, `--show`)
Last rotated: 20261022_1749
---

# Changelog — skill-ai-it

## Contents

- [20261022_1749 — Slurp: tracker linking documented; incident, a commit made on a failed check](#20261022_1749--slurp-tracker-linking-documented-incident-a-commit-made-on-a-failed-check)
- [20261022_1744 — anchor_links: --outside warn for links into other projects](#20261022_1744--anchor_links---outside-warn-for-links-into-other-projects)
- [20261022_1741 — anchor_links promoted; plan_timeline links ids to their headings](#20261022_1741--anchor_links-promoted-plan_timeline-links-ids-to-their-headings)
- [20261022_1632 — table_wrap: shared hook-compatible wrapper; target-map embeds wrap too](#20261022_1632--table_wrap-shared-hook-compatible-wrapper-target-map-embeds-wrap-too)
- [20261022_1623 — plan_timeline: the Timeline table wraps like the page's other tables](#20261022_1623--plan_timeline-the-timeline-table-wraps-like-the-pages-other-tables)
- [20261022_1646 — target map reference: summary is one short line; a missed stage heading folds its checklist into the stage above](#20261022_1646--target-map-reference-summary-is-one-short-line-a-missed-stage-heading-folds-its-checklist-into-the-stage-above)
- [20261022_1439 — audit_rotations: safety header and git timeouts; rewrap tolerance reverted](#20261022_1439--audit_rotations-safety-header-and-git-timeouts-rewrap-tolerance-reverted)
- [20261022_1209 — plan_timeline: after places unplanned rows beside their plan step](#20261022_1209--plan_timeline-after-places-unplanned-rows-beside-their-plan-step)
- [20261022_1209 — Plan timeline: extra rows before the plan rows they feed on one date](#20261022_1209--plan-timeline-extra-rows-before-the-plan-rows-they-feed-on-one-date)
- [20261021_1817 — target_map.py and plan_timeline.py promoted from unified-network-controller](#20261021_1817--target_mappy-and-plan_timelinepy-promoted-from-unified-network-controller)
- [20261021_1320 — governance-checks: a supersession banner tied to a tracker](#20261021_1320--governance-checks-a-supersession-banner-tied-to-a-tracker)
- [20261020_1753 — Template: a type check replaces the type-ignore in check_governance.py; split_checker's mirror diff](#20261020_1753--template-a-type-check-replaces-the-type-ignore-in-check_governancepy-split_checkers-mirror-diff)
- [20261020_1634 — rotate_records: project-sync outbox and inbox lines never rotate](#20261020_1634--rotate_records-project-sync-outbox-and-inbox-lines-never-rotate)
- [20261020_1632 — Template: govcheck/core.py header states it is read-only](#20261020_1632--template-govcheckcorepy-header-states-it-is-read-only)
- [20261020_1322 — pitfalls: navigation dry run exits 2 when changes are pending](#20261020_1322--pitfalls-navigation-dry-run-exits-2-when-changes-are-pending)
- [20261020_1308 — Code map in bootstrap and refresh: adopt_code_map.py, check_code_map](#20261020_1308--code-map-in-bootstrap-and-refresh-adopt_code_mappy-check_code_map)
- [20261019_1829 — pitfalls: promote leaves routing to the deleted candidates file](#20261019_1829--pitfalls-promote-leaves-routing-to-the-deleted-candidates-file)
- [20261019_1813 — Checker template: duplicated KEBAB_LEGACY block removed](#20261019_1813--checker-template-duplicated-kebab_legacy-block-removed)
- [20261019_1734 — pitfalls: hand-bootstrapped packs write accepted archcore decisions](#20261019_1734--pitfalls-hand-bootstrapped-packs-write-accepted-archcore-decisions)
- [20261019_1707 — Recipe names back to kebab-case; upgrader renames the template's snake_case recipes](#20261019_1707--recipe-names-back-to-kebab-case-upgrader-renames-the-templates-snake_case-recipes)
- [20261010_2014 — Rotation fixes (explicit pins, prose units, lazy continuation); move_sections; split audit; adopter fixes](#20261010_2014--rotation-fixes-explicit-pins-prose-units-lazy-continuation-move_sections-split-audit-adopter-fixes)

## 20261022_1749 — Slurp: tracker linking documented; incident, a commit made on a failed check

Slurp of unified-network-controller session 76e313d5. `references/target-map-and-timeline.md` gains `link_ids`, a "Linking a tracker" section
(linked nouns, one-line rows, `anchor_links.py` with `--outside warn`) and a Learned entry with its code excerpt. ROADMAP: plan_timeline.py over the
module budget (486 lines), smc-resiliency adoption of anchor_links.py. Incident: fdf90d0 was committed while `just check` failed (CHANGELOG at 206
of 200 lines); found on the check's exit code right after, fixed by rotation in 2d3665c. The commit was chained with `;`, not gated on the check.

## 20261022_1744 — anchor_links: --outside warn for links into other projects

A side agent's note on unified-network-controller (2026-10-22): its commit gate now follows links into smc-resiliency and enterprise-strategy files,
so a heading renamed by another project's session would block UNC's commits. `--outside warn` reports a broken link into a file outside the project
root as a warning that names the likely cause (the linked project's recent edits) without failing `--check`; `--outside fail` stays the default.
The root is resolved before comparing (macOS temp folders live under /private). Test: test_outside_links_warn_only_when_asked; 202 pass.

## 20261022_1741 — anchor_links promoted; plan_timeline links ids to their headings

Operator, 2026-10-22, on unified-network-controller's plan tracker: "there should be hyperlink where possible, so that there is easy
navigation", with smc-resiliency's tracker as the pattern, then "yes" to promoting what both projects now share.

- `scripts/anchor_links.py` (new, read-only): every markdown link to a `#heading` must land on a heading that exists. Same rule as the
  copies piloted that day in smc-resiliency's and unified-network-controller's govchecks, which now call this one. Recipe `just anchor-links`.
- `scripts/plan_timeline.py`: a column may declare `link_ids: {page, heading}`; plain ids in its cells link to the first heading of
  `page` matching `heading` with the id filled in (`Step {id}` finds "Step 2 — ...", not "Step 21"). Unknown ids stay text; a cell that already
  holds a link is left as written, so hand-linked data keeps rendering byte for byte.
- Tests: `tests/test_anchor_links.py` (slugs, repeats, HTML anchors, skips, exit code) and three `LinkIds` cases; 201 pass.

## 20261022_1632 — table_wrap: shared hook-compatible wrapper; target-map embeds wrap too

Operator, 2026-10-22 (unified-network-controller): "add stages to plan-tracker from target-map like smc resiliency". The table wrapper moved to
`scripts/table_wrap.py` and is shared: `target_map.py` now wraps an embedded summary table too (`embed[].wrap_width`, default 200, 0 for one line
per row; schema field added). The wrapper writes the table to a temporary file: table-reflow reads stdin with readFileSync, which failed with
EAGAIN on a pipe for unified-network-controller's 14-row summary. Tests: an embed test pins `wrap_width: 0`, a new one checks the default wraps
and reads current (194 pass). unified-network-controller: render 0.44 s; the markdown hook leaves the page unchanged.

## 20261022_1623 — plan_timeline: the Timeline table wraps like the page's other tables

Operator, 2026-10-22 (unified-network-controller): "why cant the timeline table be wrapped.. update the code to do it". `scripts/plan_timeline.py`
now passes the Timeline table through the markdown hook's own table formatter (table-reflow on a temporary file, `--width N --measure-rendered`) via
`wrap_table`; a data file's `wrap_width` sets N (default 200, 0 keeps one line per row); without Node or the tool (`TABLE_REFLOW_CLI`) the
table stays unwrapped. Measured on unified-network-controller: render 0.34 s, the hook's formatter leaves the rendered block unchanged, the page
check reads current. Tests `WrapTable` (193 pass). Learned 2026-10-22 in `references/target-map-and-timeline.md`.

## 20261022_1646 — target map reference: summary is one short line; a missed stage heading folds its checklist into the stage above

`references/target-map-and-timeline.md`: `summary` is one short line of where a target stands (operator, smc-resiliency 2026-10-22); Learned
2026-10-22: a `target_heading` pattern that misses a stage heading silently gives its checklist to the target above (smc-resiliency SM and S6).

## 20261022_1439 — audit_rotations: safety header and git timeouts; rewrap tolerance reverted

`scripts/audit_rotations.py` (smc-resiliency session, skill-coder helpers on a touched script): the header states it is read-only, and both git
calls go through `git()` with a 60 s timeout (`GIT_TIMEOUT_S`, `Raises:` documented). No behaviour change: the audit's output on smc-resiliency,
unified-network-controller and enterprise-strategy is identical before and after; `just test` 190 OK. A rewrap-tolerant match was written and
reverted the same session (operator: keep the audit strict); ROADMAP "Audit and preflight" holds the open item.

## 20261022_1209 — plan_timeline: after places unplanned rows beside their plan step

Optional `after: <stage>` in plan-timeline data (scripts/plan_timeline.py): an undated row (work not in the plan) is placed right after that
stage's row instead of last (operator, 2026-10-21, unified-network-controller: "in the logical order, not everything at the bottom"). Validated:
`after` must name a dated row's stage and only an undated row may carry it. Tests: AfterPlacement (2). Landed in 535d13f, whose message names
a different change (a same-date rule that is not in it).

## 20261022_1209 — Plan timeline: extra rows before the plan rows they feed on one date

`scripts/plan_timeline.py`: on one date an extra row (work outside the plan) comes before the plan rows it feeds, on top of the `after:` placement for undated rows (operator, smc-resiliency, 2026-10-21: unplanned work "in the logical order, not everything at the bottom"). Test `test_extra_before_plan_row_on_one_date`. Note: commit 535d13f carried only the `after:` change from the unified-network-controller session, under a message naming this rule.

## 20261021_1817 — target_map.py and plan_timeline.py promoted from unified-network-controller

- New `scripts/target_map.py` and `scripts/plan_timeline.py`, promoted from unified-network-controller (operator, 2026-10-21: "the target map is
  promoted into skill-ai-it first, then adopted in smc-resiliency for the stages"; "we haven't adapted the timeline method of UNC"), with
  `tests/test_target_map.py` (64 tests) and `tests/test_plan_timeline.py` (14). Both take `--project-root`; nothing names a project.
- Target map additions: bullet-style sources (`exit_line`, `checklist_line`: a one-line `[x] a · [ ] b` checklist is the criteria, ticks warn when
  the map disagrees), `criteria: []` for a source target whose plan writes none, `changelog.started_only`, and `embed` (the summary table rendered
  into another page between target-map markers). Plan timeline additions: `columns`, `note`, `--data`, and `parked` rows.
- Proof of no change for the pilot: UNC's tracker (70,689 bytes) and Timeline block for four dates render byte for byte as the old scripts did.
- Recipes `just target-map <project>`, `just plan-timeline <project>` (plan by default) and `just test`; catalogued in `scripts/README.md`;
  [reference](references/target-map-and-timeline.md) with a Learned entry; SKILL.md routes to it; ROADMAP: timeline idea done, target map left
  with bootstrap, the checker template, the standard and a package split (1,702 lines).
- `scripts/file_headers.py`: a tracked file deleted in the working tree is skipped (it reported "no summary in its header" for UNC's moved scripts).
- Verified: `just test` 185 tests OK; `just check` OK.

## 20261021_1320 — governance-checks: a supersession banner tied to a tracker

Learned 2026-10-21 in `patterns/governance-checks.md`: make a tracker's "not yet folded in" state executable by requiring a banner link
in each overtaken design; join hook-wrapped table rows before matching. From smc-resiliency's first staleness audit.

## 20261020_1753 — Template: a type check replaces the type-ignore in check_governance.py; split_checker's mirror diff

`templates/check_governance.py` `check_constant_sync`: `# type: ignore[union-attr]` replaced by an explicit list check (a string `surfaces`
was read character by character); found by skill-coder's new `suppressions.py` (skills_stuff b6b05fb). `patterns/governance-checks.md`:
splitting a checker in a project with a code map gives a mirror-pair difference (smc-resiliency 0f5f0f7).

## 20261020_1634 — rotate_records: project-sync outbox and inbox lines never rotate

Bug found in smc-resiliency (2026-10-20): `rotate_records.py` treated bullets inside the `<!-- project-sync:outbox|inbox:start/end -->` blocks
(apn `scripts/project_sync.py`, under `## Open items`) as open items and moved them to the open-items tracker: an unsent outbox line was never sent,
and an unanswered inbox item left the inbox, so the sync reported "inbox: 0 open". Now `parse` marks units between the markers `sync block` and
they never move nor take a "newest kept" slot. Test `test_project_sync_blocks_never_move` (red before the fix, green after; 107 tests OK).
Projects whose tracker holds moved sync lines should move them back into their blocks.

## 20261020_1632 — Template: govcheck/core.py header states it is read-only

`templates/govcheck/core.py`'s docstring gains "Read-only: it reads the project and writes nothing.": skill-coder's `script_headers.py` flagged every
copy for a missing safety statement (found in smc-resiliency, which recopied it). Other governed projects pick it up at their next refresh.

## 20261020_1322 — pitfalls: navigation dry run exits 2 when changes are pending

References: `references/pitfalls.md`, Learned 2026-10-20 (smc-resiliency refresh): `nav_upgrade_dry_run` exits 2 when changes are pending, not on
an error; `govern` needs a commit after a working session.

## 20261020_1308 — Code map in bootstrap and refresh: adopt_code_map.py, check_code_map

Operator: "coder-map to be created.. it should be part of skill-ai-it bootstrap/refresh". New `scripts/adopt_code_map.py` creates skill-coder's
`code-map.toml` when a project has code and none, and adds an `unreviewed:` `[modules]` entry for each Python script outside `src/` that the map
does not list; `govern` (template justfile) runs it after `adopt_governed_files.py`. The checker template's `check_code_map` fails on a placeholder,
a script with no entry or an entry for a gone file (side-agent finding: a placeholder must not pass as a decision). First runs: smc-resiliency
(created, then decided by hand), unified-network-controller (current, unchanged). AGENTS.md gains a Code changes section (skill-coder for any
script here, operator 2026-10-20). Reference: `references/files-support.md` (code-map.toml); catalogued in `scripts/README.md`; SKILL.md refresh bullet.

## 20261019_1829 — pitfalls: promote leaves routing to the deleted candidates file

promote deletes the candidates file but left context-map.yaml routing and repomix include naming it (skill-drawio, skill-coder);
references/pitfalls.md now lists the companion updates to make in the same pass.

## 20261019_1813 — Checker template: duplicated KEBAB_LEGACY block removed

templates/check_governance.py defined the `KEBAB_LEGACY` and `CODE_SUFFIXES` registries (and their comment) twice, so every generated checker carried the duplicate (found building skill-drawio,
2026-10-19). The second copy is removed; skill-coder's generated checker is fixed the same way, skill-drawio's was generated without it.

## 20261019_1734 — pitfalls: hand-bootstrapped packs write accepted archcore decisions

- `references/pitfalls.md` gains the 2026-10-19 skill-coder case: archcore content written outside `promote` and marked `accepted`; in bootstrap, list decisions as promotion candidates and ask.

## 20261019_1707 — Recipe names back to kebab-case; upgrader renames the template's snake_case recipes

- Recipe names are kebab-case again (operator, 2026-10-19, revising governance `coding-guide.md`: code files follow their language; names people type at
  a command line, including task-runner recipes, are kebab-case; verified mapping in skill-coder `references/naming-conventions.md`).
- `templates/justfile` and this package's `justfile`: `nav-upgrade-dry-run`, `nav-upgrade`, `nav-validate`, `nav-check-diff`, `nav-check-context-map`,
  `nav-selftest`, `audit-scripts`, `lint-md`; the package's own `nav-check-blocks`, `nav-migrate-legacy`, `roles-fleet`, `skills-registry`, `agent-usage`.
  Live references renamed (templates, scripts README, references, patterns, ARCHITECTURE, script docstrings); records (CHANGELOG, docs/history,
  reviews, dated ROADMAP and requirements notes) keep the names they had.
- `scripts/upgrade_navigation_control_layer.py` `TEMPLATE_RECIPE_RENAMES` inverted (snake_case to kebab-case) and gains `nav_check_context_map`, so a
  project bootstrapped between 2026-10-07 and 2026-10-19 converges at its next upgrade; a project's own recipes stay its own to rename when touched.
- `check_file_naming` docstring (template and this package's checker): it checks code files only; command names are kebab-case.
- Verified: 102 tests, 29 managed-block self-tests. `just check` still reports one finding that predates this change: `patterns/archcore-routing.md`
  passed its review date (2026-10-18).

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
