---
Title: Changelog
Category: change-log
Status: current
Summary: Newest entries only; older ones rotate to docs/history (search with --find, print with --show).
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/ (`--find`, `--show`)
Last rotated: 20261014_0931
---

# Changelog — skill-ai-it

## Contents

- [20261014_0931 — ROADMAP contract, budget and trim (roadmap_trim.py promoted from UNC)](#20261014_0931--roadmap-contract-budget-and-trim-roadmap_trimpy-promoted-from-unc)
- [20261013_2241 — Pitfall: enforce skill invocation with a hook, not a rule](#20261013_2241--pitfall-enforce-skill-invocation-with-a-hook-not-a-rule)
- [20261013_2230 — Pitfall: the wrap hook runs on Write and Edit and reflows the whole file](#20261013_2230--pitfall-the-wrap-hook-runs-on-write-and-edit-and-reflows-the-whole-file)
- [20261012_0958 — check_outside_blocks.py; upgrader Python floor; adopter and the outline trial](#20261012_0958--check_outside_blockspy-upgrader-python-floor-adopter-and-the-outline-trial)
- [20261012_0952 — Upgrader CHANGELOG heading uses the YYYYMMDD_hhmm stamp](#20261012_0952--upgrader-changelog-heading-uses-the-yyyymmdd_hhmm-stamp)
- [20261011_0525 — Section-level Markdown reads (outline, section) and adopter attribute fix](#20261011_0525--section-level-markdown-reads-outline-section-and-adopter-attribute-fix)
- [20261010_2346 — move_sections link repointing and shared pointer; budget tidy step; add_changelog_entry](#20261010_2346--move_sections-link-repointing-and-shared-pointer-budget-tidy-step-add_changelog_entry)
- [20261010_2332 — Reference reads measured (not split); tracker pointer no longer duplicates](#20261010_2332--reference-reads-measured-not-split-tracker-pointer-no-longer-duplicates)
- [20261010_2227 — Memory pointers rotate; no upgrade hint for project-owned blocks; jdm within budget](#20261010_2227--memory-pointers-rotate-no-upgrade-hint-for-project-owned-blocks-jdm-within-budget)
- [20261010_2207 — SKILL.md restructured: 2,074 to 198 lines, detail in references/ by topic](#20261010_2207--skillmd-restructured-2074-to-198-lines-detail-in-references-by-topic)
- [20261010_2156 — Compact navigation template; reference split by topic; adopter documents recipes; budget suggestions](#20261010_2156--compact-navigation-template-reference-split-by-topic-adopter-documents-recipes-budget-suggestions)
- [20261010_2135 — budget_plan and normalise_records; heading dates and time grouping; runaway incident and fix](#20261010_2135--budget_plan-and-normalise_records-heading-dates-and-time-grouping-runaway-incident-and-fix)
- [20261010_2014 — Rotation fixes (explicit pins, prose units, lazy continuation); move_sections; split audit; adopter fixes](#20261010_2014--rotation-fixes-explicit-pins-prose-units-lazy-continuation-move_sections-split-audit-adopter-fixes)
- [20261010_1833 — Rotation made safe and complete; adopter; headers for every script and config](#20261010_1833--rotation-made-safe-and-complete-adopter-headers-for-every-script-and-config)
- [20261010_1805 — Governed-file tools: rotation by bullet, ticked items resolved; checker standard; slurp rotates](#20261010_1805--governed-file-tools-rotation-by-bullet-ticked-items-resolved-checker-standard-slurp-rotates)
- [20261010_1830 — feat: doc_freshness.py; Graphify disabled](#20261010_1830--feat-doc_freshnesspy-graphify-disabled)

## 20261014_0931 — ROADMAP contract, budget and trim (roadmap_trim.py promoted from UNC)

- **ROADMAP has a contract and a budget** (operator, 2026-10-14: "Roadmap budget is not defined ... make sure that the skill-ai-it has proper use defined
  for roadmap and the projects are aware of it"). `references/files-architecture-conventions-roadmap.md` now says what ROADMAP is for (dated current phase,
  open milestones by area; not a log, not session state, not decisions), its header (`Kind: roadmap`, `Budget: 200 lines, 25 KB`, `Archive:`), and how done
  items leave it. SKILL.md's Budget and Rotation bullets name it.
- **`scripts/roadmap_trim.py`**, promoted from unified-network-controller (dry runs identical on UNC's ROADMAP, 0 and 5 items), now takes `--project-root`,
  creates `docs/history/` and its index when missing, and leaves a project without ROADMAP alone; `tests/test_roadmap_trim.py` (5 tests).
- **`doc_freshness.py`** counts ROADMAP.md as a whole-read file with the default 200-line, 25 KB budget.
- **`templates/justfile`** `rotate` runs the trim; **`adopt_governed_files.py`** adds the ROADMAP header keys and the trim line in `rotate` to any project
  with a ROADMAP.md (2 new tests), so slurp's adoption run reaches every project.
- **Template fix:** `templates/AI_NAVIGATION.md` gains front matter with a summary and a date; without it every new project's first commit failed
  `doc_freshness.py` (found bootstrapping smc-resiliency). The adopt step also dates a ROADMAP it gives a header to (from its newest date, else today).

## 20261013_2241 — Pitfall: enforce skill invocation with a hook, not a rule

- `references/pitfalls.md`: enforce "invoke skill X before Y work" with a PreToolUse hook (transcript Skill calls, owned-path map, Bash only when it writes,
  fail open, off switch); a project `.claude/settings.json` created mid-session took effect at once. From unified-network-controller 2026-10-13.

## 20261013_2230 — Pitfall: the wrap hook runs on Write and Edit and reflows the whole file

- `references/pitfalls.md`: the Markdown wrap and contents hook runs on Write and Edit only and reflows the whole file (tables, split paths, joined
  managed-block markers); shell edits bypass it. From unified-network-controller 2026-10-10/11, written back late after a write-back audit (2026-10-13).

## 20261012_0958 — check_outside_blocks.py; upgrader Python floor; adopter and the outline trial

- `scripts/check_outside_blocks.py` (promoted from an enterprise-strategy upgrade check): each file with its managed blocks removed must match a git ref (default HEAD);
  `just nav_check_blocks [REF]`; catalogued in scripts/README.md; three offline tests (block-only change passes, outside edit fails, dropped END marker fails); smoke on
  enterprise-strategy at a5f2c33~1: AI_NAVIGATION.md identical, AGENTS.md and scripts/README.md differ by their deliberate outside-block edits. 66 tests pass.
- Finding: the upgrader needs Python 3.10 or later (`str | None` in a signature); the host `python3` crashes on import. Use the project venv (`just nav_upgrade`) or python3.14.
- Open, proposed not decided: `adopt_governed_files.py` adds the `outline` and `section` recipes to every project, which undoes the hold on them until the
  unified-network-controller trial is re-measured (2026-10-25). A skip list or a trial flag would keep the hold.

## 20261012_0952 — Upgrader CHANGELOG heading uses the YYYYMMDD_hhmm stamp

- `scripts/upgrade_navigation_control_layer.py`: the CHANGELOG entry heading now carries the `YYYYMMDD_hhmm` stamp (local time), as `add_changelog_entry.py`
  writes it, instead of an ISO date (`2026-10-12 — ...`), which broke the heading convention in every project it upgraded (found on enterprise-strategy, operator 12 Oct 2026).
- `tests/test_upgrade_navigation_control_layer.py`: the heading is stamped and first in a newest-first log; a second run is idempotent. Red against the old code, green now; 63 tests pass.
- Existing date-only upgrade headings in projects stay as written (history); rotation and order detection already read both forms.

## 20261011_0525 — Section-level Markdown reads (outline, section) and adopter attribute fix

- New `scripts/md_sections.py` with recipes `just outline` (each heading with its line range and size) and `just section` (one section by exact
  title, leading section number optional, `Parent > Child`, `#anchor` or `~substring`; an ambiguous selector exits 3 and lists every match). Idea
  from lilmd (molefrog/lilmd), no code taken (it has no licence); exact by default because 44 of 123 numbered UNC headings collide under substring
  matching. Read-only, stdlib only. Evidence: UNC `docs/reports/knowledge-tooling/lilmd-assessment-20261011_0517.md`.
- `agent_usage.py --md-reads`: counts hand-built outline greps, recipe calls and whole/ranged Markdown Reads, subagent transcripts included.
  UNC baseline (30 days): 182 transcripts, 748 outline greps in 99.
- Fixed `adopt_governed_files.py` `split_recipes`: attribute lines (`[positional-arguments]`) and the comment above them were dropped when a
  recipe was copied, so `"$@"` arrived empty (found when `just outline` got no file). Adopter now ships `outline` and `section` and names them in
  the AGENTS line for new projects.
- Tests 50 to 61 (md_sections 9, adopter regression 1, md_reads 1); `just check` 308 pass. Adopted here and in UNC (trial to 2026-10-25).

## 20261010_2346 — move_sections link repointing and shared pointer; budget tidy step; add_changelog_entry

- move_sections.py: `--pointer-into HEADING` adds a bullet to one shared pointer section (created when missing); in-page `#anchor` links that cross the
  move are repointed in both files, and links from other project markdown to a moved section follow it; `consolidate()` merges legacy numbered pointer
  sections. Replaces the hand-written link fixers and pointer merges of 2026-10-10.
- budget_plan.py: a tidy step first (duplicate tracker pointers kept once, tracker pointers removed from trackers, numbered pointer sections merged);
  moves go into one shared "Reference moved out" section.
- New add_changelog_entry.py (`just changelog-entry`): the project's own heading style and order, Contents line, clock-read stamp, additions-only check.
  Replaces the scratch entry helper used about 25 times. Smoke-tested in plan mode on all 23 governed CHANGELOGs (five styles, one oldest-first).
- Adopter adds and documents the `changelog-entry` recipe; skill-slurp-chat step 7 names it. Tests 39 to 49, each new behaviour negative-tested.
- Free-text recipes (`changelog-entry`, `move-sections`) take quoted positional arguments (`[positional-arguments]`, `"$@"`): `{{ARGS}}` is
  substituted unquoted, and a title containing semicolons ran its fragments as shell commands (harmless here; caught on the first real use). The adopter
  rewrites the unsafe form in adopted projects.

## 20261010_2332 — Reference reads measured (not split); tracker pointer no longer duplicates

- Reference reads measured (scripts/agent_usage.py, 30 days, 3,068 sessions): files-context-map, files-ai-navigation and script-task-inventory each had 0 real
  reads (they date from today; skill-ai-it itself was invoked 13 times). Not split; re-measure on 2026-11-10 (SCRATCHPAD open item), split if read in more than 5 sessions.
- rotate_records.py: the "Older open items are tracked in" pointer was treated as an open item on the next run, moved to the tracker and written again,
  so pointers piled up (2 to 3 copies in 7 SCRATCHPADs, one stray in cambium-swap's tracker). It now stays in place, and the presence check compares
  lines. Test added, negative-tested; this SCRATCHPAD deduplicated. The other projects' duplicates are left for the operator's per-project run.

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
