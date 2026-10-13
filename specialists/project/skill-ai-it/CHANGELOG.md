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
Last rotated: 20261014_1020
---

# Changelog — skill-ai-it

## Contents

- [20261014_1020 — Coherence pass: ARCHITECTURE key decisions, sibling skills, sweep clean](#20261014_1020--coherence-pass-architecture-key-decisions-sibling-skills-sweep-clean)
- [20261014_1018 — Staleness audit: upgrader header, derived index counts, links, indexes](#20261014_1018--staleness-audit-upgrader-header-derived-index-counts-links-indexes)
- [20261014_1006 — Graphify confirmed disabled; slurp write-backs (token-budget rule, roles_fleet)](#20261014_1006--graphify-confirmed-disabled-slurp-write-backs-token-budget-rule-roles_fleet)
- [20261014_1002 — File roles enforced: role_check.py, adoption adds headers, templates and loading tiers](#20261014_1002--file-roles-enforced-role_checkpy-adoption-adds-headers-templates-and-loading-tiers)
- [20261014_0943 — Governed file roles defined; README trimmed; front matter everywhere](#20261014_0943--governed-file-roles-defined-readme-trimmed-front-matter-everywhere)
- [20261014_0931 — ROADMAP contract, budget and trim (roadmap_trim.py promoted from UNC)](#20261014_0931--roadmap-contract-budget-and-trim-roadmap_trimpy-promoted-from-unc)
- [20261013_2241 — Pitfall: enforce skill invocation with a hook, not a rule](#20261013_2241--pitfall-enforce-skill-invocation-with-a-hook-not-a-rule)
- [20261013_2230 — Pitfall: the wrap hook runs on Write and Edit and reflows the whole file](#20261013_2230--pitfall-the-wrap-hook-runs-on-write-and-edit-and-reflows-the-whole-file)
- [20261012_0958 — check_outside_blocks.py; upgrader Python floor; adopter and the outline trial](#20261012_0958--check_outside_blockspy-upgrader-python-floor-adopter-and-the-outline-trial)
- [20261012_0952 — Upgrader CHANGELOG heading uses the YYYYMMDD_hhmm stamp](#20261012_0952--upgrader-changelog-heading-uses-the-yyyymmdd_hhmm-stamp)
- [20261011_0525 — Section-level Markdown reads (outline, section) and adopter attribute fix](#20261011_0525--section-level-markdown-reads-outline-section-and-adopter-attribute-fix)
- [20261010_2346 — move_sections link repointing and shared pointer; budget tidy step; add_changelog_entry](#20261010_2346--move_sections-link-repointing-and-shared-pointer-budget-tidy-step-add_changelog_entry)
- [20261010_2332 — Reference reads measured (not split); tracker pointer no longer duplicates](#20261010_2332--reference-reads-measured-not-split-tracker-pointer-no-longer-duplicates)
- [20261010_2014 — Rotation fixes (explicit pins, prose units, lazy continuation); move_sections; split audit; adopter fixes](#20261010_2014--rotation-fixes-explicit-pins-prose-units-lazy-continuation-move_sections-split-audit-adopter-fixes)

## 20261014_1020 — Coherence pass: ARCHITECTURE key decisions, sibling skills, sweep clean

- **Coherence pass** (operator, 2026-10-14) over the file-roles, staleness-audit and all-scraper changes: ARCHITECTURE.md gains "Key decisions"
  (roles and loading tiers, ratchet via adoption, README budget per project, record rotation, Graphify disabled), so the page readers open first
  carries today's decisions; scripts/README.md `adopt_governed_files.py` row describes what adoption now adds. Siblings: skill-project-coherence
  Tier 5 no longer regenerates Graphify (its CHANGELOG 2026-10-14); all-scraper SCRATCHPAD intro uses rotation wording. Stale-reference sweep
  across this package, skill-slurp-chat, skill-project-coherence, skill-staleness-audit and all-scraper: 0 active. No repomix config here.

## 20261014_1018 — Staleness audit: upgrader header, derived index counts, links, indexes

- **Staleness audit, whole package** (operator, 2026-10-14; report `docs/reviews/staleness-audit-20261014_1017.md`, gate PASSED). No money
  band. Fixed: the upgrader created AGENTS.md with an unfenced header that would fail `role_check.py` on first contact (latent; now fenced, test
  added); stale references index counts (now derived by `check_reference_index_lines`); ROADMAP links to UNC `target_map.py` (moved to
  `scripts/render/`); SCRATCHPAD 2026-08-11 counts superseded in place and a done open item ticked; folder indexes for `docs/`, `docs/archive/`,
  `patterns/`, `templates/`, `docs/reviews/`; baselines named in scripts/README.md. Both new checks negative-tested red and green. Why it
  survived: the upgrader builds its header in code, a generation path the template review did not reach. Residual register in SCRATCHPAD.

## 20261014_1006 — Graphify confirmed disabled; slurp write-backs (token-budget rule, roles_fleet)

- **Graphify confirmed disabled** (operator, 2026-10-14: "confirm and make sure that Graphify is disabled"). Every `graphify update` in this
  package (templates/context_preflight.sh, the embedded preflight in references/files-support.md, templates/context-map.yaml) and in the nine
  project justfiles that keep a `graph` recipe is gated by `GRAPHIFY_ENABLED=1`; no git hook, LaunchAgent, Claude hook or running process calls
  it; `~/.claude.json` holds only skill usage counts, no Graphify MCP server. Two ungated recovery steps fixed: this package's `context-map.yaml`
  `context_recovery` and `patterns/navigation/recovery-and-audit.md` step 3 (the reference the managed block links to).
- **Slurp:** operator rule on token budget added to AGENTS.md working rules (loading tiers; never inline what a link carries, never delete to
  save space); `just roles_fleet` recipe (one role-check line per governed project, to track the rollout); skill-slurp-chat Step 6 names what
  adoption now adds and that `just budget` trims ROADMAP. Canary entry written in cambium-swap's CHANGELOG (its changes are not committed).
- **Check surface retired:** CHANGELOG.md no longer a `managed-block-version` surface in `scripts/check_governance.py`. Rotation (`just budget`)
  moved the only entry stating the stamp to docs/history and the check failed on a past fact; a rotating log cannot hold a live claim.

## 20261014_1002 — File roles enforced: role_check.py, adoption adds headers, templates and loading tiers

- **Roles now reach projects and are enforced** (operator, 2026-10-14: "ensure that all the definitions ... are actually going to be defined for
  the projects in that way and it will adhere to that"; and the files must spend AI tokens well: small by default, detail on need). Analysis of
  the templates, the enforcement code and the 13 governed projects: every project broke a role, templates lacked front matter and a README quick
  start, no SETUP rule existed, and only budgets and links were gated.
- **`scripts/role_check.py`** (new, `just roles`, in `just check`, baseline `scripts/role-check-baseline.json`): front matter on root files,
  CLAUDE.md import first, README quick start and no status/history heading, ROADMAP dated phase and no done items or narrative, duplicated
  sections across root files. `tests/test_role_check.py` proves each rule fails; it also finds the three README/ARCHITECTURE duplicates in HEAD.
- **`adopt_governed_files.py`** (run at every slurp) adds `---` front matter to README, AGENTS, AI_NAVIGATION, ARCHITECTURE, CONVENTIONS, SETUP
  (legacy unfenced blocks fenced above the `@` import; `Review by` 30 days on), Authority/Scope/Last reviewed on the records, README's `Budget`
  key, `role_check.py` in `check`, the `roles` recipe and the role baseline; re-records the size of an over-budget file it heads, so adoption
  cannot fail the ratchet. Canary: cambium-swap (check green, second run reports adopted).
- **`budget_plan.py`** trims ROADMAP (slurp runs `just budget`, not `just rotate`, so ROADMAP was never trimmed at close).
- **Templates:** README (front matter, Quick start, no history in Context, local links fixed), AGENTS (front matter first, navigation block taken
  from `templates/` instead of a stale copy), CLAUDE (no H1 placeholders), ARCHITECTURE (data flow, boundaries, decisions with reasons,
  `Depends on`), CONVENTIONS, ROADMAP and CHANGELOG/SCRATCHPAD (full front matter; newest first; `KEEP` the exception), new SETUP.md rule and
  template; the drifted AI_NAVIGATION fallback removed; refresh table updated.
- **`references/governed-file-roles.md`**: loading model (always-read, read-once, on-need, on-demand tiers; summarise up, link down), tier per
  file, and an enforcement table that states only what code enforces. Also fixed: this package's AGENTS.md front matter fenced; the ROADMAP lines
  left behind by the earlier trim restored to their history file; a YAML error in `context-map.yaml` (found by `nav_validate`, not `just check`).

## 20261014_0943 — Governed file roles defined; README trimmed; front matter everywhere

- **Governed file roles defined** (operator, 2026-10-14: "define what each of these files mean ... and check if each of them ... are defined
  properly and this skill will take care of it"). New `references/governed-file-roles.md`: reader, holds, keeps out, how it changes and what
  enforces it for README, AGENTS, CLAUDE, AI_NAVIGATION, ARCHITECTURE, CONVENTIONS, SETUP (conditional), ROADMAP, CHANGELOG and SCRATCHPAD, plus a
  placement test and a role check. Linked from SKILL.md (Always-created files), the finishing quality checklist, `context-map.yaml`
  (`file_role_compliance` audit check, `package_docs` routing), AI_NAVIGATION.md and the references index.
- **Own files brought to their roles.** README.md rewritten from 241 to 116 lines: quick start added, sections duplicated from ARCHITECTURE.md
  replaced by a link, stale package layout and the "Graphify actively invoked" claim corrected, opted into the 200-line budget with a `Budget` key.
  ARCHITECTURE.md: Graphify marked disabled (2026-10-10) in the flow, tool stack and recovery steps; "four" capabilities corrected to five;
  `references/`, `scripts/`, `tests/`, ROADMAP and SCRATCHPAD added to package roles; the stale-outputs upgrade row moved over from README.
  ROADMAP.md put on its own contract: dated current phase, open `- [ ]` items by area, completed phases and the obsolete sync item moved
  verbatim to `docs/history/roadmap-20261014_0942.md` by `just rotate`.
- **Front matter added wherever missing** (operator): AI_NAVIGATION, ARCHITECTURE, README, five patterns (governance-checks fenced),
  scripts/README.md, docs/history/readme.md, and the six May 2026 plans, prompts and reviews (`Status: archived`); missing Authority, Scope and
  Last reviewed keys added to ROADMAP, CHANGELOG and SCRATCHPAD. Not given front matter: CLAUDE.md (its import line must stay its whole content)
  and the three `templates/` snippets that are inserted into other projects' files.

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
