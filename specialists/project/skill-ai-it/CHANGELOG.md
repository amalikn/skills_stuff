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
Last rotated: 20261112_1656
---

# Changelog — skill-ai-it

## Contents

- [Unreleased](#unreleased)
- [20261112_1700 — new-skill: Learned entry on prompt templates under the formatter](#20261112_1700--new-skill-learned-entry-on-prompt-templates-under-the-formatter)
- [20261112_1656 — new-skill: Deferred and extensions section, stamped template dates, brief front matter](#20261112_1656--new-skill-deferred-and-extensions-section-stamped-template-dates-brief-front-matter)
- [20261112_1552 — new-skill: intake, research briefs, seed folder with research and parts](#20261112_1552--new-skill-intake-research-briefs-seed-folder-with-research-and-parts)
- [20261112_1536 — new-skill mode: seed template, pack scaffold and pack contract check](#20261112_1536--new-skill-mode-seed-template-pack-scaffold-and-pack-contract-check)
- [20261111_1259 — central project tooling plan, the skill's flow map, md_examples_check](#20261111_1259--central-project-tooling-plan-the-skills-flow-map-md_examples_check)
- [20261111_1213 — history_migrate: check gate, dirty-reference refusal, survey](#20261111_1213--history_migrate-check-gate-dirty-reference-refusal-survey)
- [20261111_1135 — archcore, ruff, code map, templates and the Pad question](#20261111_1135--archcore-ruff-code-map-templates-and-the-pad-question)
- [20261111_1125 — docs/history by kind, generated index with summaries, migration](#20261111_1125--docshistory-by-kind-generated-index-with-summaries-migration)
- [20261105_2139 — promote: quoted front matter, Last reviewed, decisions_to_adrs](#20261105_2139--promote-quoted-front-matter-last-reviewed-decisions_to_adrs)
- [20261105_2047 — adopt_governed_files: check recipe matched by exact name](#20261105_2047--adopt_governed_files-check-recipe-matched-by-exact-name)
- [20261105_1725 — agents_chain check: AGENTS.md chains for Claude Code and Codex](#20261105_1725--agents_chain-check-agentsmd-chains-for-claude-code-and-codex)
- [20261103_1741 — mirror_skills: one client's skills linked into another](#20261103_1741--mirror_skills-one-clients-skills-linked-into-another)
- [20261029_2015 — Pitfalls: one route for cross-project messages; route facts by class](#20261029_2015--pitfalls-one-route-for-cross-project-messages-route-facts-by-class)
- [20261027_2055 — Slurp close: callers-check, write-backs, coherence](#20261027_2055--slurp-close-callers-check-write-backs-coherence)
- [20261010_2014 — Rotation fixes (explicit pins, prose units, lazy continuation); move_sections; split audit; adopter fixes](#20261010_2014--rotation-fixes-explicit-pins-prose-units-lazy-continuation-move_sections-split-audit-adopter-fixes)

## Unreleased

- 2026-11-11 scripts/checks/doc_freshness.py: the dependency rule skips commits that only rewrite link targets or backticked paths
  (`path_only_change`, `content_change_date`, at most 20 commits back); tests/test_doc_freshness_paths.py (7 tests, a temporary git repository).
  Found when history_migrate's link repoints in UNC's options register flagged four dependent documents for review.
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

## 20261112_1700 — new-skill: Learned entry on prompt templates under the formatter

- references/new-skill.md: Learned 2026-11-12 (prompt and form templates saved as markdown: formatter-joined lines, real front matter and dates, strip front matter when written; 0ce0278).

## 20261112_1656 — new-skill: Deferred and extensions section, stamped template dates, brief front matter

- new-skill: the seed template gains a `Deferred and extensions` section (everything researched or considered and not used now, why, where the evidence is, how to enable it; routed
  as an `extensions.md` reference), so a personal or scoped skill records what it set aside (operator, 2026-11-12). Templates now carry a real `Last reviewed` date that generation
  stamps with the clock (the placeholder dates failed the freshness check once tracked); the research brief template has front matter that is stripped when a brief is written, and
  its lines no longer merge under the table formatter. First real run through the intake: skill-presentation (intake, five briefs, seed 1653, parts for mind maps, analysis
  workbooks and extensions).

## 20261112_1552 — new-skill: intake, research briefs, seed folder with research and parts

- new-skill now runs the seeding itself (operator, 2026-11-12): `new-skill-intake` writes an interview form (four rounds, at most four questions each, answers recorded as
  USER_STATED, search before asking); `new-skill-research-briefs` writes one generic research brief per topic and refuses a forbidden term; `new-skill-seed --from-intake` pre-fills
  the seed. Added `templates/skill-intake.md`, `templates/research-brief.md`, `templates/seed-folder/`, `scripts/skills/skill_intake.py` and `skill_scaffold.py` (split from
  `new_skill.py` to keep modules under 400 lines), and 9 tests.
- The seed is a folder in `pending_skills/<name>/`: `research/` and `parts/` stay beside it for good (operator ruling); a `parts/<reference>.md` becomes that reference's body on
  scaffold; the scaffold never copies the seed into the pack and refuses a `forbidden_terms` name in any generated file. The seed parser merges rows wrapped by the repo's table
  formatter.

## 20261112_1536 — new-skill mode: seed template, pack scaffold and pack contract check

- New mode `new-skill` (operator, 2026-11-12): a new skill pack is built from a written seed, scaffolded to the shared shape and checked against one contract. Added
  `templates/skill-seed.md` (nineteen sections; "What was learned" is the core), `templates/skill-pack/` (SKILL.md, AGENTS, README, CHANGELOG, references, sources.yaml,
  compatibility.yaml, scenarios, contract test, Python pin and ruff for packs with scripts), `scripts/skills/` (`new_skill.py` seed, check-seed and scaffold; `skill_seed.py`;
  `skill_pack_check.py`), four recipes (`new-skill-seed`, `new-skill-check`, `new-skill-scaffold`, `skill-pack-check`), `references/new-skill.md`, archcore rule `new-skills-start-
  from-a-seed` and 21 tests. Shape taken from skill-nautobot, skill-vagrant, skill-coder, skill-network-architect and skill-systems-architect. The scaffold plans by default, never
  overwrites (`.proposed` beside a different file) and does not install, commit or push.
- SKILL.md: the Inputs section moved verbatim to `references/inputs.md` (move_sections.py) to make room; SKILL.md is 194 lines.

## 20261111_1259 — central project tooling plan, the skill's flow map, md_examples_check

- `docs/central-project-tooling-plan-20261111_1141.md` (new, status proposed): the central project tooling plan from a unified-network-controller session (operator, 2026-11-11). Two read-only
  surveys (govcheck in three projects; justfiles, hooks, configs and tests across 13), the home decision (skill-ai-it now, versioned packages, extraction trigger to a pinned
  package), the project standard (Core, Modules, Local; the `standard:` block in context-map.yaml; levels Mandatory, Advised, Optional), map formats with a `meta` block,
  CUE schemas, HCL as the env-map source, Pad collections and `tracker-map.toml`, stages S0 to S8 with go and abort numbers and rollout waves, proposed scripts with excerpts,
  language choice. Reviewed against skill-coder and skill-systems-architect the same day; all fixes the operator accepted are in. Indexed in `docs/readme.md`.
- `docs/flows/` (new): the skill's first flow map (skill-drawio standard: parts, assembled `flows.yaml`, `drawio/skill-ai-it-flows.drawio`): today's bootstrap, rotation,
  history migration and governance check, and the plan's proposed release, refresh and conformance flows. Recipes `just flows` and `just flows-check` (in `just check`;
  0.4 s), run on skill-drawio's interpreter for PyYAML. Layout audit clean; Overview and End-to-end pages exported and reviewed.
- `scripts/markdown/md_examples_check.py` (new, `just md-examples`, tests/test_md_examples_check.py, 11 tests): a design document's fenced TOML, YAML, JSON (or JSON Lines)
  and Python examples parse, table rows match their header's cell count, internal anchors resolve. Promoted from the session's ad hoc check; 0.06 s on the 1,650-line plan.
- ROADMAP: three Fleet adoption items (the plan's open decisions; rotation front matter missing Authority and Scope; per-folder docs index after history_migrate).

## 20261111_1213 — history_migrate: check gate, dirty-reference refusal, survey

From the rollout to 18 other projects (smc-resiliency session, operator "do all of them", 2026-11-11).

- `scripts/records/history_migrate.py`: `--check-cmd 'just check'` refuses a project whose check is already red and undoes the move (git restore to HEAD)
  when the check is red after it; a file the migration would rewrite with uncommitted edits refuses the apply; several `--project-root` values plan them
  all (a survey), while `--apply` takes one. Promoted from the session's one-off scripts. Test `test_check_gate_and_dirty_references`; 6 history tests pass.
- [references/files-history.md](references/files-history.md): "Rolling it out across projects" and a Learned entry (12 of 18 checks already red; one project per run).
- The 22 docs past review: approved by the operator 2026-11-11 (`a806ef4`).

## 20261111_1135 — archcore, ruff, code map, templates and the Pad question

Operator, 2026-11-11: skill-ai-it gets the lint config, code map and archcore "like we do in our other skills", its templates updated with any
missing ones added, and bootstrap and refresh ask whether to link a Pad workspace (a suggested name; repos may share one).

- Added `.archcore/` (archcore 0.3.6 init, `archcore status` clean): eight rules, one file each, and `index.guide.md`; AGENTS.md Working rules are now
  one line and a link per rule (AGENTS.md re-read in full, Last reviewed 2026-11-11).
- Added `ruff.toml` (two-space, 160 columns, the other skills' rule set; the 65 older Python files excluded until a reformat is decided, Markdown
  excluded), `ruff==0.17.3` in requirements.txt, `just lint` inside `just check` (proved to fail on a bad new file).
- Added `code-map.toml` (adopt_code_map.py): 38 modules, all `promoted` (this pack's own tooling).
- Added templates `history-readme.md` (used by history_layout.py for a project without an index), `session-record.md` (slurp closeouts; skill-slurp-chat
  Step 8 names it), `archcore/index.guide.md` and `archcore/rule.md` (promote; patterns/archcore-routing.md names them); AI_NAVIGATION template names the
  history folders.
- Added [references/pad-workspace.md](references/pad-workspace.md) and its SKILL.md step: with no `.pad.toml`, ask once (folder name suggested, existing
  workspaces offered, `pad workspace link <slug>` shares one; VERIFIED_PRIMARY `pad workspace --help` v0.19.2); "no" recorded in AGENTS.md.
- Proposed, not built: a project `ruff.toml` template belongs with skill-coder (owner of lint rules).

## 20261111_1125 — docs/history by kind, generated index with summaries, migration

Operator, 2026-11-11: docs/history gets one subfolder per kind (changelog, scratchpad, roadmap, session-records, sync) as the standard, and its index a summary line
per file like the session records have. [references/files-history.md](references/files-history.md).

- Added `scripts/records/history_layout.py` (layout, archive lookup in both layouts, link rewrite, generated index keeping hand-written descriptions) and
  `scripts/records/history_migrate.py` (`just history-migrate <project> [--apply]`: git mv, links inside and references elsewhere repointed, another project's
  same-name archive untouched, `.remember/` skipped, links verified); tests `tests/test_history_layout.py` (5).
- Changed: rotate_records.py, roadmap_trim.py, audit_rotations.py and target_map.py write and read through the layout; roadmap_trim.py now relinks moved items
  (it never did); rotate_records.py relinks the archive index rows too (a row could keep a root-relative link that never resolved). Older tests read archives
  recursively. 234 tests pass.
- Migrated: this pack's own docs/history (58 files) and smc-resiliency's (151 files, the canary).
- Open: 24 doc-freshness reviews came due before this change (AGENTS.md, patterns/navigation/*, the open-items tracker and others); not bumped without a re-read.

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
