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
Last rotated: 20261110_2029
---

# Changelog — skill-ai-it

## Contents

- [Unreleased](#unreleased)
- [20261105_2139 — promote: quoted front matter, Last reviewed, decisions_to_adrs](#20261105_2139--promote-quoted-front-matter-last-reviewed-decisions_to_adrs)
- [20261105_2047 — adopt_governed_files: check recipe matched by exact name](#20261105_2047--adopt_governed_files-check-recipe-matched-by-exact-name)
- [20261105_1725 — agents_chain check: AGENTS.md chains for Claude Code and Codex](#20261105_1725--agents_chain-check-agentsmd-chains-for-claude-code-and-codex)
- [20261103_1741 — mirror_skills: one client's skills linked into another](#20261103_1741--mirror_skills-one-clients-skills-linked-into-another)
- [20261029_2015 — Pitfalls: one route for cross-project messages; route facts by class](#20261029_2015--pitfalls-one-route-for-cross-project-messages-route-facts-by-class)
- [20261027_2055 — Slurp close: callers-check, write-backs, coherence](#20261027_2055--slurp-close-callers-check-write-backs-coherence)
- [20261027_2048 — Scripts in family folders; callers repointed; skill-coder gates in check](#20261027_2048--scripts-in-family-folders-callers-repointed-skill-coder-gates-in-check)
- [20261027_2024 — Staleness audit: dependency claim derived, stale KEEP lines superseded](#20261027_2024--staleness-audit-dependency-claim-derived-stale-keep-lines-superseded)
- [20261027_1941 — Open-items tracker reviewed](#20261027_1941--open-items-tracker-reviewed)
- [20261027_1922 — Quoted code excerpts restored after a markdown hook bug](#20261027_1922--quoted-code-excerpts-restored-after-a-markdown-hook-bug)
- [20261027_1840 — Pitfalls from the skill-goal-guard bootstrap; upgrader placement idea](#20261027_1840--pitfalls-from-the-skill-goal-guard-bootstrap-upgrader-placement-idea)
- [20261026_1525 — Line-only budgets reverted: the 25 KB limit is back](#20261026_1525--line-only-budgets-reverted-the-25-kb-limit-is-back)
- [20261022_2132 — plan_tracker: What next gets a detail block per item](#20261022_2132--plan_tracker-what-next-gets-a-detail-block-per-item)
- [20261022_1819 — plan_tracker: plan tracker page setup and upkeep promoted from smc-resiliency and unified-network-controller](#20261022_1819--plan_tracker-plan-tracker-page-setup-and-upkeep-promoted-from-smc-resiliency-and-unified-network-controller)
- [20261022_1749 — Slurp: tracker linking documented; incident, a commit made on a failed check](#20261022_1749--slurp-tracker-linking-documented-incident-a-commit-made-on-a-failed-check)
- [20261022_1744 — anchor_links: --outside warn for links into other projects](#20261022_1744--anchor_links---outside-warn-for-links-into-other-projects)
- [20261022_1741 — anchor_links promoted; plan_timeline links ids to their headings](#20261022_1741--anchor_links-promoted-plan_timeline-links-ids-to-their-headings)
- [20261010_2014 — Rotation fixes (explicit pins, prose units, lazy continuation); move_sections; split audit; adopter fixes](#20261010_2014--rotation-fixes-explicit-pins-prose-units-lazy-continuation-move_sections-split-audit-adopter-fixes)

## Unreleased

- 20261110 references/pitfalls.md: Learned 2026-11-10 (skill-pad bootstrap): walk the generation-policy table (archcore, markdownlint, repomix); the markdown hook re-wraps whole files, so edit budgeted or hash-guarded files from Bash.

- scripts/adoption/adopt_governed_files.py: a legacy-header value hard-wrapped onto an unindented line now stays in the fenced value (`wrapped_continuation`, previous line 100+ characters; operator, 2026-11-09: "Fix with a test"); 2 tests, red on the old code; references/pitfalls.md entry updated.
- ROADMAP idea (2026-11-09, unified-network-controller): the target-map change-log rule counts a target ID mentioned only as a date anchor as work on that target
- 2026-11-09 write-back from skill-vagrant refresh: references/pitfalls.md (govern skips code-map; quoted Summary; wrapped CHANGELOG lines; GOVERN_ALLOW_DIRTY refused; CATALOGS per research folder)
- 2026-11-09 write-back from skill-proxmox refresh: references/pitfalls.md (unindented legacy-header continuation lost on adoption; docs/history and docs/trackers need CONDITIONAL_PATHS; govern baselines are a ratchet; accepted archcore leaves the review clock; candidates file owed)
- scripts/markdown/table_add_column.py (+ tests/test_table_add_column.py, `just table-add-column`): add a column to markdown tables keyed by the first cell; wrapped continuation rows merged to one line per row; a missing key refused unless `--default`; a `|` in a value escaped (an unescaped one split cells even inside backticks, and the markdown hook then mangled the row: found 2026-11-09 in unified-network-controller's audit verdict column); plan without `--apply`. Promoted from that session's one-off. Also observed: `doc_freshness.py --write-baseline` drops resolved entries as it adds new ones; a generated doc whose Last reviewed comes from its data (topology scorecards) can only be baselined or regenerated from a new run (exemption for `Authority: generated` proposed, not decided: ROADMAP)
- scripts/adoption/adopt_governed_files.py: `over_budget_warning` prints the trim route when FILE_BUDGETS budgets a file already over it (operator, 2026-11-06: keep the ratchet, warn and route; UNC, enterprise-strategy, cambium-swap, vocus-profitability, smc-file-writing-analysis and voip-analysis AGENTS.md are over 12 KB)
- scripts/adoption/adopt_governed_files.py: FILE_BUDGETS: AGENTS.md and AI_NAVIGATION.md get `Budget: 150 lines, 12 KB` as README gets its own (operator, 2026-11-06: governance files read whole carry a budget; doc_freshness enforces it, grandfather_sizes keeps a file already over from failing); scripts/records/budget_plan.py reports those files against their stated budget; test asserts AGENTS.md gets it
- references/governed-file-roles.md: a rule moved out of AGENTS.md leaves a one-line summary; tighter budgets go in the file's `Budget:` header (2026-11-05, ansible-wifi). ROADMAP idea: line-range
  moves in move_sections.py.

## 20261105_2139 — promote: quoted front matter, Last reviewed, decisions_to_adrs

references/generation-policy.md, promote step: quote front-matter values (an unquoted colon fails `archcore status`), give each proposed document `Last reviewed` (tracked-only freshness check), render
decision ADRs with skill-knowledge-curator `decisions_to_adrs.py`, and clear the candidates file from every reference in the same pass. Found in the Continuum promotion, 2026-11-05.

## 20261105_2047 — adopt_governed_files: check recipe matched by exact name

The six `^check\b` patterns in `scripts/adoption/adopt_governed_files.py` also matched `check-links:` and `check-contracts:` (a hyphen is a word boundary). In Continuum (2026-11-05) a `check-links`
recipe above `check` made the roles gate look missing, and the fix would have edited the wrong recipe. Now `^check(?=[ \t:])`. New test `test_hyphenated_check_recipes_are_not_the_check_recipe` fails
on the old pattern; 222 tests pass.

## 20261105_1725 — agents_chain check: AGENTS.md chains for Claude Code and Codex

New `scripts/checks/agents_chain.py` (+ `tests/test_agents_chain.py`, 6 tests; recipe `just agents-chain <folder>`; catalogued in `scripts/README.md`): which AGENTS.md files Claude Code (`@` imports)
and Codex (project-root markers, `project_doc_max_bytes`) load for a folder, with missing imports, cycles, a cut file, files Codex cannot see and Codex trust spread.
`references/files-readme-agents-claude.md`: Learned 2026-11-05, AGENTS.md chains across folders, Claude Code vs Codex (inline block plus `.codex-root` marker; trust follows the project root; never a
marker in a trusted folder holding untrusted repos). Smoke-run on three real folders, 0.05-0.42 s.

## 20261103_1741 — mirror_skills: one client's skills linked into another

- `scripts/install/mirror_skills.py` (new, catalogued, `just mirror-skills`) with `tests/test_mirror_skills.py`: links each skill in a source install folder to its resolved canonical folder in a
  target folder; plan by default, `--apply` writes, `--prune` drops stale links, real folders are never touched. First use: 128 skills linked from ~/.claude/skills into ~/.continue/skills for Continue
  2.0.0 (vibeshell left as a real folder).
- Continue 2.0.0 follows a symlinked skill folder: its walker skips only entries whose VS Code type is exactly SymbolicLink (a broken link).

## 20261029_2015 — Pitfalls: one route for cross-project messages; route facts by class

- `references/pitfalls.md`: two entries from the 2026-10-29 harvest of a multi-project workspace root (hub-and-spoke messages with a directive register; device facts to domain packs, site and decision
  facts to projects). `references/readme.md` line count updated.
- Skipped as already covered: gates that fail on uncovered growth and stay stdlib-only (`patterns/governance-checks.md`, Coverage self-policing and the harness contract); architecture docs drifting
  from runtime config and README links to missing docs (path resolution, derived-artifact staleness, "text matching does not verify behaviour").

## 20261027_2055 — Slurp close: callers-check, write-backs, coherence

- Slurp close: `just callers-check` added (runs `just check` in every project or skill whose justfile calls this package; flags path errors apart from the project's own findings; 0 path errors, about
  43 s). ARCHITECTURE Key decisions: scripts in family folders, callers repointed (operator).
- Write-backs: skill-coder pattern P-32 (repoint callers after a move) and a write_gates entry (local writes need `write_patterns`), plus the missing P-31 index row; skill-staleness-audit tool hazards
  (the gate's YAML step SKIPPED under a host python3; Phase 4 counts rows, not judgements).
- Coherence pass after the audit: `scripts/README.md` checker row names the dependency check; ROADMAP Ideas: ship `check_declared_dependencies` in the template. Other repos touched by the repoint
  (apn, me, tools_stuff, governance) are left uncommitted: the commit was asked for skills_stuff.

## 20261027_2048 — Scripts in family folders; callers repointed; skill-coder gates in check

- `scripts/` split into family folders (operator chose "subfolders, update callers"): `records/`, `checks/`, `adoption/`, `navigation/`, `plans/`, `markdown/`, `survey/`; `check_governance.py` and the
  baselines stay at the root, where every governed project keeps its own. Cross-loads fixed (`role_check` finds a script in any family, `rotate_records` loads `checks/file_headers.py`, plans put
  `markdown/` and `checks/` on the path); `scripts/README.md` catalogued by family, `references/package-layout.md` tree redrawn.
- New `scripts/adoption/repoint_paths.py` (`just repoint-paths`, test `tests/test_repoint_paths.py`): 467 references in 43 files across 30 projects and skills repointed (justfiles, skill-slurp-chat
  SKILL.md, skill-coder refs, governance naming guide); CHANGELOGs, `docs/history/`, archives and dated `*-YYYYMMDD_hhmm.md` files left as written. 107 s over eight roots. smc-resiliency and
  unified-network-controller built the path in code (`AI_IT_SCRIPTS / f"{name}.py"`); their govcheck loaders now search the family folders. Every consumer's `just check` was run: no path errors.
- The checker found the move: catalogue paths failed, and its script scans were flat (`scripts/*.py`), so its count fell 492 to 411. Scans are recursive, catalogue coverage matches the path below
  `scripts/` (red when a script is listed under the wrong family), bare script names resolve in their family.
- skill-coder brought in: run/safety lines in 8 headers, `timeout=` on 21 subprocess calls, one `type: ignore` removed, a shrink-only size baseline (`scripts/code-size-baseline.json`, 8 modules, 17
  functions), and `scripts/write-gates.json` counting local file writes (23 writers; two GAP entries, navigation writers that plan only with `--dry-run`, are a ROADMAP item). `just self-check` runs
  the helpers; `just check` runs it and `nav-validate` (red on a YAML error). 520 checks, 213 tests.
- Incident, fixed: the repoint also rewrote three dated session-history lines inside this package's SCRATCHPAD.md (`audit_rotations.py` reported them LOST); restored word for word. The one live KEEP
  line whose path changed is accepted in `docs/history/rotation-audit-baseline.txt`. `repoint_paths.py` skips history files but not dated sections inside a living file (ROADMAP item).

## 20261027_2024 — Staleness audit: dependency claim derived, stale KEEP lines superseded

- Staleness audit, whole package ([staleness-audit-20261027_2023.md](docs/reviews/staleness-audit-20261027_2023.md)): 4 defects, none band M. `requirements.txt` claimed one script needed PyYAML (seven import it, `plan_timeline.py` and
  `target_map.py` at module level): count removed and `check_declared_dependencies` added to `scripts/check_governance.py` (red on PyYAML removed, green on restore; 458 to 490 checks). SCRATCHPAD: a
  done `KEEP` open item (no test recipe) superseded in place, a stale push next-action replaced.
- Why it survived: a hand-written count from 2026-09-23 (five scripts then, 32 now) that nothing derived. Phase 4 test rows were first filled with one stock line and redone one by one after a side
  agent flagged it; weak tests and residuals are listed in the report and SCRATCHPAD.

## 20261027_1941 — Open-items tracker reviewed

- `docs/trackers/open-items-20261010_1830.md` reviewed (it failed `just check`, due 2026-10-24); next review 2026-11-10, the date of its reference re-measure item. Closed: the
  `patterns/archcore-routing.md` review (done in 9d7fda8, `Last reviewed: 2026-10-19`). Still open, checked on disk: no governance checker yet in llm-m2max, vocus-profitability,
  opticomm-profitability, openbb or invoice-finance-analyst (jdm has one); `nav-validate` still not in `just check`; the context-map schema decision and the skill-coder helper overlap are undecided.

## 20261027_1922 — Quoted code excerpts restored after a markdown hook bug

- `references/target-map-and-timeline.md`: three quoted code excerpts had been joined into run-on prose by the markdown hook (a `rewrap.py` bug with quoted fences, fixed in scripts_stuff 2026-10-27).
  One restored from git history (`plan_timeline.py` reflow excerpt); two that were committed flattened rebuilt from `scripts/plan_tracker.py` and `scripts/plan_timeline.py`, words unchanged.

## 20261027_1840 — Pitfalls from the skill-goal-guard bootstrap; upgrader placement idea

- Three pitfalls from the skill-goal-guard bootstrap and promote (references/pitfalls.md): quote promoted titles that hold a colon and keep a small tag vocabulary for `archcore status`; a "folder
  readme covers its folder" catalog rule must skip the project root (found by a negative test); freshness reads only tracked files, so give created files their header summary before the first commit.
- ROADMAP Ideas: the upgrader appends its CHANGELOG entry at the bottom when a file dates entries as `###` under `## Unreleased`.
- Committed while `just check` fails on `docs/trackers/open-items-20261010_1830.md` (review due 2026-10-24), an existing finding that needs a fleet review; these edits do not touch it (operator asked
  for the write-backs to be committed and pushed).

## 20261026_1525 — Line-only budgets reverted: the 25 KB limit is back

- Operator, 2026-10-26, after a side agent's note: "Okay then put the limit back", "Wherever you removed it from". 59d3c31 (budgets by line count only) is reverted: the 200 lines and 25 KB budget is
  back in doc_freshness, rotate_records, budget_plan, add_changelog_entry, adopt_governed_files, move_sections, their tests and docs, and every `Budget: 200 lines, 25 KB` header the change rewrote.
- Why the KB part stays: Codex reads AGENTS.md only up to about 32 KiB and drops the rest without warning; 200 lines of up to 200 characters is about 40 KB, so a line budget alone lets an
  always-loaded file pass and still be cut short. Whether Codex counts the whole AGENTS.md chain against that cap is unverified.

## 20261022_2132 — plan_tracker: What next gets a detail block per item

- Operator, 2026-10-22 (smc-resiliency): "I'm still not able to understand what is really required next and what would the done when really make sense"; "update the skill about this approach for what
  next". What next is now a one-line table (#, Next, Owner, By, Done when) whose Next cell links to a `### <n>. <action>` block with What is needed, Why now, In hand and a Done when checklist.
- `scripts/plan_tracker.py`: `slug`, `detail_blocks`; a block without "Done when" fails, a row with no block on the page is a note (UNC's tracker passes with notes until it adopts). Tests
  `test_detail_blocks`, `test_slug_matches_vs_code` (8 pass). Template `templates/plan-tracker.md` and reference `target-map-and-timeline.md` (The plan tracker page; Learned 2026-10-22) updated.
- ROADMAP: the rotation item is answered on the consumer side; smc-resiliency's decision check now reads `docs/history/changelog-*.md`, as the rotation contract asks.
- The template's `Last reviewed: {today}` failed the skill's own freshness check: it now carries a real date and `--init` stamps today.

## 20261022_1819 — plan_tracker: plan tracker page setup and upkeep promoted from smc-resiliency and unified-network-controller

- Operator, 2026-10-22 (smc-resiliency session): "Ensure that plan tracker setup and maintenance is written back to skill-ai-it ... so that all the projects can follow it." New
  `scripts/plan_tracker.py` (`--init` prints, `--init --apply` writes the starter page when absent; `--check` fails on a missing section, a missing `As of`, or a What next row unlinked or split; split
  rows elsewhere and a stale `As of` are notes), `templates/plan-tracker.md` (the page both pilots share), `templates/AGENTS-plan-tracker-block.md` (upkeep rules to paste), recipe `just plan-tracker
  <project>`, tests `tests/test_plan_tracker.py` (6), and the reference section "The plan tracker page" with a Learned entry.
- First runs: smc-resiliency and unified-network-controller both failed on a split What next row (the markdown hook splits a row rendered wider than 200 columns); smc-resiliency's rows were shortened
  and now pass; unified-network-controller is told through the hub.

## 20261022_1749 — Slurp: tracker linking documented; incident, a commit made on a failed check

Slurp of unified-network-controller session 76e313d5. `references/target-map-and-timeline.md` gains `link_ids`, a "Linking a tracker" section (linked nouns, one-line rows, `anchor_links.py` with
`--outside warn`) and a Learned entry with its code excerpt. ROADMAP: plan_timeline.py over the module budget (486 lines), smc-resiliency adoption of anchor_links.py. Incident: fdf90d0 was committed
while `just check` failed (CHANGELOG at 206 of 200 lines); found on the check's exit code right after, fixed by rotation in 2d3665c. The commit was chained with `;`, not gated on the check.

## 20261022_1744 — anchor_links: --outside warn for links into other projects

A side agent's note on unified-network-controller (2026-10-22): its commit gate now follows links into smc-resiliency and enterprise-strategy files, so a heading renamed by another project's session
would block UNC's commits. `--outside warn` reports a broken link into a file outside the project root as a warning that names the likely cause (the linked project's recent edits) without failing
`--check`; `--outside fail` stays the default. The root is resolved before comparing (macOS temp folders live under /private). Test: test_outside_links_warn_only_when_asked; 202 pass.

## 20261022_1741 — anchor_links promoted; plan_timeline links ids to their headings

Operator, 2026-10-22, on unified-network-controller's plan tracker: "there should be hyperlink where possible, so that there is easy navigation", with smc-resiliency's tracker as the pattern, then
"yes" to promoting what both projects now share.

- `scripts/anchor_links.py` (new, read-only): every markdown link to a `#heading` must land on a heading that exists. Same rule as the copies piloted that day in smc-resiliency's and
  unified-network-controller's govchecks, which now call this one. Recipe `just anchor-links`.
- `scripts/plan_timeline.py`: a column may declare `link_ids: {page, heading}`; plain ids in its cells link to the first heading of `page` matching `heading` with the id filled in (`Step {id}` finds
  "Step 2 — ...", not "Step 21"). Unknown ids stay text; a cell that already holds a link is left as written, so hand-linked data keeps rendering byte for byte.
- Tests: `tests/test_anchor_links.py` (slugs, repeats, HTML anchors, skips, exit code) and three `LinkIds` cases; 201 pass.

## 20261010_2014 — Rotation fixes (explicit pins, prose units, lazy continuation); move_sections; split audit; adopter fixes

- `rotate_records.py`: pins only on the explicit marker (`` `PIN` `` or `<!-- PIN -->`; a bare "PIN" substring had pinned ansible-wifi entries about captive-portal PINs); a dated `###` subsection of
  prose rotates as one unit; wrapped items keep their unindented (lazy) continuation lines (before, heads moved and tails stayed live: 39 tails in 5 projects, repaired). Over-budget note names
  `move_sections.py`.
- New `move_sections.py` (+ `move-sections` recipe in justfile and template, catalogue row, tests): moves named `##` sections verbatim to an on-need reference doc with a pointer; refuses on loss.
  Promoted from a hand-written session script (operator: logic belongs in the skill).
- `audit_rotations.py`: reports SPLIT entries; counts sections moved by `move_sections.py` (provenance line) as kept.
- `adopt_governed_files.py`: adds a `check` recipe when a project has none (smc-file-writing-analysis gated nothing); `move-sections` in the recipe set; `ai_it` detected with aligned spacing (atar got
  a duplicate); new recipes reuse the project's interpreter (of-si `{{ai_py}}`) and drop `_require-venv` when the project lacks it.
- SKILL.md Rotation bullet and skill-slurp-chat step 7: a record left over budget is unfinished; reference goes out with `move-sections`. SKILL.md held to its ratchet (2,074 lines, 67 bytes smaller)
  by replacing the hand-written freshness bootstrap steps with the adopter call.
- Tests 14 to 22 (new: explicit pin, prose subsection, lazy continuation, move_sections x3, split audit x2, adopter x3), each negative-tested; check 229 pass.
