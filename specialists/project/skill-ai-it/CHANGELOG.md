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
Last rotated: 20261119_1648
---

# Changelog — skill-ai-it

## Contents

- [Unreleased](#unreleased)
- [20261119_1647 — Identifiers redacted from pack text (operator)](#20261119_1647--identifiers-redacted-from-pack-text-operator)
- [20261119_1638 — Periodic review; 90-day window; rotation no longer overwrites a same-minute archive](#20261119_1638--periodic-review-90-day-window-rotation-no-longer-overwrites-a-same-minute-archive)
- [20261119_1551 — rotation_verify.py: did this rotation move every removed line](#20261119_1551--rotation_verifypy-did-this-rotation-move-every-removed-line)
- [20261112_1700 — new-skill: Learned entry on prompt templates under the formatter](#20261112_1700--new-skill-learned-entry-on-prompt-templates-under-the-formatter)
- [20261112_1656 — new-skill: Deferred and extensions section, stamped template dates, brief front matter](#20261112_1656--new-skill-deferred-and-extensions-section-stamped-template-dates-brief-front-matter)
- [20261112_1552 — new-skill: intake, research briefs, seed folder with research and parts](#20261112_1552--new-skill-intake-research-briefs-seed-folder-with-research-and-parts)
- [20261112_1536 — new-skill mode: seed template, pack scaffold and pack contract check](#20261112_1536--new-skill-mode-seed-template-pack-scaffold-and-pack-contract-check)
- [20261111_1259 — central project tooling plan, the skill's flow map, md_examples_check](#20261111_1259--central-project-tooling-plan-the-skills-flow-map-md_examples_check)
- [20261111_1213 — history_migrate: check gate, dirty-reference refusal, survey](#20261111_1213--history_migrate-check-gate-dirty-reference-refusal-survey)
- [20261111_1135 — archcore, ruff, code map, templates and the Pad question](#20261111_1135--archcore-ruff-code-map-templates-and-the-pad-question)
- [20261010_2014 — Rotation fixes (explicit pins, prose units, lazy continuation); move_sections; split audit; adopter fixes](#20261010_2014--rotation-fixes-explicit-pins-prose-units-lazy-continuation-move_sections-split-audit-adopter-fixes)

## Unreleased

- 2026-11-19 · `scripts/records/rotate_records.py`: an `Open items tracker:` value that is not a relative markdown path (prose such as "this file, Open items") is ignored with a message; it once made
  a file named `this` in skill-coder (2026-11-07). One test in `tests/test_rotate_records.py`.
- 2026-11-19 · `scripts/records/audit_rotations.py` `text_only`: a ticked task checkbox (`- [x]`) matches the open one, so a sync inbox item archived ticked under docs/history/sync/ is no longer
  reported lost (smc-resiliency BUG-68: 6 lines; `just budget --apply`'s audit now OK there); two tests in `tests/test_audit_rotations.py`.
- 2026-11-19 · `scripts/adoption/adopt_governed_files.py` `fix_justfile`: without a `py :=` line, `ai_it :=` now goes after the leading comment block; above it, the justfile header lost its summary
  and `govern` baselined a no-header finding (continuum-app). Test `test_ai_it_goes_below_the_header_comment` fails without the change.
- 2026-11-19 · `scripts/records/rotate_records.py`: archive front matter now carries `Authority: record` and `Scope`, which the governance header standard requires (skill-pad's check failed on a fresh
  archive). `test_archive_has_no_blank_line_runs` asserts both.
- 2026-11-19 · `scripts/checks/file_headers.py`: package-manager lock files (`LOCK_NAMES`: pnpm-lock.yaml and others) are generated data and leave the header check; a tracked `pnpm-lock.yaml` failed
  continuum's `just check` with no-header. Test `LockFiles` in `tests/test_doc_freshness_paths.py` fails without the change.
- 2026-11-18 · `scripts/records/rotate_records.py` `archive_text`: trims each unit's trailing blank lines and ends the archive with one newline (archives failed MD012 in continuum after every `just
  budget --apply`); regression test `test_archive_has_no_blank_line_runs` (fails without the fix). `templates/.markdownlint-cli2.jsonc`: MD013 off, the markdown-wrap-toc hook owns width and measures
  it without link targets (operator, 2026-11-18). Open: the rotation audit reports a heading as LOST that is in neither the live record nor HEAD (`20261118_2150` in continuum); not investigated.
- 2026-11-18: `scripts/markdown/wrap_added.py` (`just wrap-added`) and `tests/test_wrap_added.py`, promoted from Continuum: wrap only the long lines a diff added.

- 2026-11-18 `scripts/records/audit_rotations.py`: fixed, the audit took its comparison text from the commit that added the oldest archive file, which a regroup of docs/history by kind re-adds (61
  lines reported lost in unified-network-controller); it now asks git for the first add under either layout, and counts `docs/history/sync/sync-archive-*.md` as archived for SCRATCHPAD.
  `tests/test_audit_rotations_baseline.py`: three cases (fail before, pass after; seven audit tests pass). Found by a read-only side agent of the unified-network-controller D17 session.

- 2026-11-18 `references/pitfalls.md`: Learned, a check recipe of one line per step hides every failure after the first; run all and fail at the end (unified-network-controller). The bootstrap
  template is unchanged; fix open
- 2026-11-18 `references/pitfalls.md`: Learned entry, `history_layout.py` cuts a description inside a Markdown link and leaves a broken link in the generated history index (unified-network-controller
  audit 16); the script is unchanged, fix open
- 2026-11-18 `scripts/records/move_sections.py`: a BEGIN/END block marker before the next heading stays in the source instead of moving with the section (orphaned END found in of-si); tests
  BlockMarkerTest; references/pitfalls.md Learned.
- 2026-11-18 `scripts/records/budget_plan.py`: a navigation block with no `skill-ai-it-version` marker is reported as skipped by govern and refused by the upgrader, not hinted for an upgrade that
  cannot run; references/pitfalls.md Learned (from of-si).
- 2026-11-17 `templates/skill-pack/tests/test_package_contract.py.tmpl` registers the checker in `sys.modules` before loading it (`@dataclass` failed); references/new-skill.md Learned (from
  skill-ascii-diagrams, 71b26f9).
- 2026-11-17 `scripts/records/rotate_records.py` never rotates a CHANGELOG's `## Unreleased` (git blame dated the heading oldest); test reproduces it; references/files-records.md Learned (7f8791b).
- 2026-11-16 references/target-map-and-timeline.md Learned: a CHANGELOG entry naming a target's mention after its review stops the render until the target is reviewed (smc-resiliency write-back).
- 2026-11-16 scripts/checks/doc_freshness.py: `transcript` joins the point-in-time categories, so a meeting transcript is never review-due (a 13 Oct transcript was flagged in apn enterprise-strategy);
  tests/test_doc_freshness_point_in_time.py (2 tests: transcript skipped, living document still due; fails without the fix).
- 2026-11-12 patterns/governance-checks.md: Learned entry, the governance-checks block moves verbatim to `.agents/governance-checks.md` when AGENTS.md is trimmed to one line per rule; AGENTS.md keeps
  a line naming `scripts/check_governance.py` (from apn enterprise-strategy).
- 2026-11-11 scripts/checks/doc_freshness.py: the dependency rule skips commits that only rewrite link targets or backticked paths (`path_only_change`, `content_change_date`, at most 20 commits back);
  tests/test_doc_freshness_paths.py (7 tests, a temporary git repository). Found when history_migrate's link repoints in UNC's options register flagged four dependent documents for review.
- 20261110 references/pitfalls.md: Learned 2026-11-10 (skill-pad bootstrap): walk the generation-policy table (archcore, markdownlint, repomix); the markdown hook re-wraps whole files, so edit
  budgeted or hash-guarded files from Bash.

- scripts/adoption/adopt_governed_files.py: a legacy-header value hard-wrapped onto an unindented line now stays in the fenced value (`wrapped_continuation`, previous line 100+ characters; operator,
  2026-11-09: "Fix with a test"); 2 tests, red on the old code; references/pitfalls.md entry updated.
- ROADMAP idea (2026-11-09, unified-network-controller): the target-map change-log rule counts a target ID mentioned only as a date anchor as work on that target
- 2026-11-09 write-back from skill-vagrant refresh: references/pitfalls.md (govern skips code-map; quoted Summary; wrapped CHANGELOG lines; GOVERN_ALLOW_DIRTY refused; CATALOGS per research folder)
- 2026-11-09 write-back from skill-proxmox refresh: references/pitfalls.md (unindented legacy-header continuation lost on adoption; docs/history and docs/trackers need CONDITIONAL_PATHS; govern
  baselines are a ratchet; accepted archcore leaves the review clock; candidates file owed)
- scripts/markdown/table_add_column.py (+ tests/test_table_add_column.py, `just table-add-column`): add a column to markdown tables keyed by the first cell; wrapped continuation rows merged to one
  line per row; a missing key refused unless `--default`; a `|` in a value escaped (an unescaped one split cells even inside backticks, and the markdown hook then mangled the row: found 2026-11-09 in
  unified-network-controller's audit verdict column); plan without `--apply`. Promoted from that session's one-off. Also observed: `doc_freshness.py --write-baseline` drops resolved entries as it adds
  new ones; a generated doc whose Last reviewed comes from its data (topology scorecards) can only be baselined or regenerated from a new run (exemption for `Authority: generated` proposed, not
  decided: ROADMAP)
- scripts/adoption/adopt_governed_files.py: `over_budget_warning` prints the trim route when FILE_BUDGETS budgets a file already over it (operator, 2026-11-06: keep the ratchet, warn and route; UNC,
  enterprise-strategy, cambium-swap, vocus-profitability, smc-file-writing-analysis and voip-analysis AGENTS.md are over 12 KB)
- scripts/adoption/adopt_governed_files.py: FILE_BUDGETS: AGENTS.md and AI_NAVIGATION.md get `Budget: 150 lines, 12 KB` as README gets its own (operator, 2026-11-06: governance files read whole carry
  a budget; doc_freshness enforces it, grandfather_sizes keeps a file already over from failing); scripts/records/budget_plan.py reports those files against their stated budget; test asserts AGENTS.md
  gets it
- references/governed-file-roles.md: a rule moved out of AGENTS.md leaves a one-line summary; tighter budgets go in the file's `Budget:` header (2026-11-05, ansible-wifi). ROADMAP idea: line-range
  moves in move_sections.py.

## 20261119_1647 — Identifiers redacted from pack text (operator)

- Company domain, a project name and a person's name replaced with generic placeholders (operator, 2026-11-19: redact identifiers in pack text).

## 20261119_1638 — Periodic review; 90-day window; rotation no longer overwrites a same-minute archive

- Periodic review (operator, 2026-11-19): all 55 due docs re-read in full and dated 2026-11-19; body rules aligned with Learned entries (Unreleased never rotates, kebab-case recipes, KEEP contradiction), Contents and front matter added, ROADMAP items closed. Review window now 90 days (`--window-days 90`).
- `scripts/records/rotate_records.py`: a second rotation in the same minute wrote the same archive name and erased the first (skill-drawio and skill-nautobot lost entries, restored from git); `free_archive_name` adds `-2`, `-3`. Tracker-path check moved into `tracker_path`. Test `test_a_second_rotation_in_the_same_minute_keeps_the_first_archive`; `repoint_paths.py` DATED accepts the suffix.
- `scripts/adoption/adopt_governed_files.py`: the role_check line copied from the freshness line drops `--window-days` (role_check has no such option). Test `test_role_check_line_drops_the_freshness_window`.
- `templates/AGENTS-governance-checks-block.md`: `<RUNNER CHECK COMMAND>` placeholder (never substituted) now `just check`.

## 20261119_1551 — rotation_verify.py: did this rotation move every removed line

- New `scripts/records/rotation_verify.py` (`just rotation-verify`), 3 offline tests: every content line the uncommitted change removed from a record is in docs/history/, whitespace-folded. The narrow
  check run by hand four times on 2026-11-19 (continuum, skill-pad, skill-coder) while audit_rotations.py reported phantom LOST lines (ROADMAP item stays open).

## 20261112_1700 — new-skill: Learned entry on prompt templates under the formatter

- references/new-skill.md: Learned 2026-11-12 (prompt and form templates saved as markdown: formatter-joined lines, real front matter and dates, strip front matter when written; 0ce0278).

## 20261112_1656 — new-skill: Deferred and extensions section, stamped template dates, brief front matter

- new-skill: the seed template gains a `Deferred and extensions` section (everything researched or considered and not used now, why, where the evidence is, how to enable it; routed as an
  `extensions.md` reference), so a personal or scoped skill records what it set aside (operator, 2026-11-12). Templates now carry a real `Last reviewed` date that generation stamps with the clock (the
  placeholder dates failed the freshness check once tracked); the research brief template has front matter that is stripped when a brief is written, and its lines no longer merge under the table
  formatter. First real run through the intake: skill-presentation (intake, five briefs, seed 1653, parts for mind maps, analysis workbooks and extensions).

## 20261112_1552 — new-skill: intake, research briefs, seed folder with research and parts

- new-skill now runs the seeding itself (operator, 2026-11-12): `new-skill-intake` writes an interview form (four rounds, at most four questions each, answers recorded as USER_STATED, search before
  asking); `new-skill-research-briefs` writes one generic research brief per topic and refuses a forbidden term; `new-skill-seed --from-intake` pre-fills the seed. Added `templates/skill-intake.md`,
  `templates/research-brief.md`, `templates/seed-folder/`, `scripts/skills/skill_intake.py` and `skill_scaffold.py` (split from `new_skill.py` to keep modules under 400 lines), and 9 tests.
- The seed is a folder in `pending_skills/<name>/`: `research/` and `parts/` stay beside it for good (operator ruling); a `parts/<reference>.md` becomes that reference's body on scaffold; the scaffold
  never copies the seed into the pack and refuses a `forbidden_terms` name in any generated file. The seed parser merges rows wrapped by the repo's table formatter.

## 20261112_1536 — new-skill mode: seed template, pack scaffold and pack contract check

- New mode `new-skill` (operator, 2026-11-12): a new skill pack is built from a written seed, scaffolded to the shared shape and checked against one contract. Added `templates/skill-seed.md` (nineteen
  sections; "What was learned" is the core), `templates/skill-pack/` (SKILL.md, AGENTS, README, CHANGELOG, references, sources.yaml, compatibility.yaml, scenarios, contract test, Python pin and ruff
  for packs with scripts), `scripts/skills/` (`new_skill.py` seed, check-seed and scaffold; `skill_seed.py`; `skill_pack_check.py`), four recipes (`new-skill-seed`, `new-skill-check`,
  `new-skill-scaffold`, `skill-pack-check`), `references/new-skill.md`, archcore rule `new-skills-start- from-a-seed` and 21 tests. Shape taken from skill-nautobot, skill-vagrant, skill-coder,
  skill-network-architect and skill-systems-architect. The scaffold plans by default, never overwrites (`.proposed` beside a different file) and does not install, commit or push.
- SKILL.md: the Inputs section moved verbatim to `references/inputs.md` (move_sections.py) to make room; SKILL.md is 194 lines.

## 20261111_1259 — central project tooling plan, the skill's flow map, md_examples_check

- `docs/central-project-tooling-plan-20261111_1141.md` (new, status proposed): the central project tooling plan from a unified-network-controller session (operator, 2026-11-11). Two read-only surveys
  (govcheck in three projects; justfiles, hooks, configs and tests across 13), the home decision (skill-ai-it now, versioned packages, extraction trigger to a pinned package), the project standard
  (Core, Modules, Local; the `standard:` block in context-map.yaml; levels Mandatory, Advised, Optional), map formats with a `meta` block, CUE schemas, HCL as the env-map source, Pad collections and
  `tracker-map.toml`, stages S0 to S8 with go and abort numbers and rollout waves, proposed scripts with excerpts, language choice. Reviewed against skill-coder and skill-systems-architect the same
  day; all fixes the operator accepted are in. Indexed in `docs/readme.md`.
- `docs/flows/` (new): the skill's first flow map (skill-drawio standard: parts, assembled `flows.yaml`, `drawio/skill-ai-it-flows.drawio`): today's bootstrap, rotation, history migration and
  governance check, and the plan's proposed release, refresh and conformance flows. Recipes `just flows` and `just flows-check` (in `just check`; 0.4 s), run on skill-drawio's interpreter for PyYAML.
  Layout audit clean; Overview and End-to-end pages exported and reviewed.
- `scripts/markdown/md_examples_check.py` (new, `just md-examples`, tests/test_md_examples_check.py, 11 tests): a design document's fenced TOML, YAML, JSON (or JSON Lines) and Python examples parse,
  table rows match their header's cell count, internal anchors resolve. Promoted from the session's ad hoc check; 0.06 s on the 1,650-line plan.
- ROADMAP: three Fleet adoption items (the plan's open decisions; rotation front matter missing Authority and Scope; per-folder docs index after history_migrate).

## 20261111_1213 — history_migrate: check gate, dirty-reference refusal, survey

From the rollout to 18 other projects (smc-resiliency session, operator "do all of them", 2026-11-11).

- `scripts/records/history_migrate.py`: `--check-cmd 'just check'` refuses a project whose check is already red and undoes the move (git restore to HEAD) when the check is red after it; a file the
  migration would rewrite with uncommitted edits refuses the apply; several `--project-root` values plan them all (a survey), while `--apply` takes one. Promoted from the session's one-off scripts.
  Test `test_check_gate_and_dirty_references`; 6 history tests pass.
- [references/files-history.md](references/files-history.md): "Rolling it out across projects" and a Learned entry (12 of 18 checks already red; one project per run).
- The 22 docs past review: approved by the operator 2026-11-11 (`a806ef4`).

## 20261111_1135 — archcore, ruff, code map, templates and the Pad question

Operator, 2026-11-11: skill-ai-it gets the lint config, code map and archcore "like we do in our other skills", its templates updated with any missing ones added, and bootstrap and refresh ask whether
to link a Pad workspace (a suggested name; repos may share one).

- Added `.archcore/` (archcore 0.3.6 init, `archcore status` clean): eight rules, one file each, and `index.guide.md`; AGENTS.md Working rules are now one line and a link per rule (AGENTS.md re-read
  in full, Last reviewed 2026-11-11).
- Added `ruff.toml` (two-space, 160 columns, the other skills' rule set; the 65 older Python files excluded until a reformat is decided, Markdown excluded), `ruff==0.17.3` in requirements.txt, `just
  lint` inside `just check` (proved to fail on a bad new file).
- Added `code-map.toml` (adopt_code_map.py): 38 modules, all `promoted` (this pack's own tooling).
- Added templates `history-readme.md` (used by history_layout.py for a project without an index), `session-record.md` (slurp closeouts; skill-slurp-chat Step 8 names it), `archcore/index.guide.md` and
  `archcore/rule.md` (promote; patterns/archcore-routing.md names them); AI_NAVIGATION template names the history folders.
- Added [references/pad-workspace.md](references/pad-workspace.md) and its SKILL.md step: with no `.pad.toml`, ask once (folder name suggested, existing workspaces offered, `pad workspace link <slug>` shares one; VERIFIED_PRIMARY
  `pad workspace --help` v0.19.2); "no" recorded in AGENTS.md.
- Proposed, not built: a project `ruff.toml` template belongs with skill-coder (owner of lint rules).

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
