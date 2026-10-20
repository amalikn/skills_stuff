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
Last rotated: 20261020_1632
---

# Changelog — skill-ai-it

## Contents

- [20261020_1632 — Template: govcheck/core.py header states it is read-only](#20261020_1632--template-govcheckcorepy-header-states-it-is-read-only)
- [20261020_1322 — pitfalls: navigation dry run exits 2 when changes are pending](#20261020_1322--pitfalls-navigation-dry-run-exits-2-when-changes-are-pending)
- [20261020_1308 — Code map in bootstrap and refresh: adopt_code_map.py, check_code_map](#20261020_1308--code-map-in-bootstrap-and-refresh-adopt_code_mappy-check_code_map)
- [20261019_1829 — pitfalls: promote leaves routing to the deleted candidates file](#20261019_1829--pitfalls-promote-leaves-routing-to-the-deleted-candidates-file)
- [20261019_1813 — Checker template: duplicated KEBAB_LEGACY block removed](#20261019_1813--checker-template-duplicated-kebab_legacy-block-removed)
- [20261019_1734 — pitfalls: hand-bootstrapped packs write accepted archcore decisions](#20261019_1734--pitfalls-hand-bootstrapped-packs-write-accepted-archcore-decisions)
- [20261019_1707 — Recipe names back to kebab-case; upgrader renames the template's snake_case recipes](#20261019_1707--recipe-names-back-to-kebab-case-upgrader-renames-the-templates-snake_case-recipes)
- [20261015_0129 — doc_freshness: a Budget header counts only with a size](#20261015_0129--doc_freshness-a-budget-header-counts-only-with-a-size)
- [20261014_1247 — yaml_key_diff: context-map key changes and lost comments after an upgrade](#20261014_1247--yaml_key_diff-context-map-key-changes-and-lost-comments-after-an-upgrade)
- [20261014_1234 — pitfalls: the navigation upgrade drops context-map.yaml comments](#20261014_1234--pitfalls-the-navigation-upgrade-drops-context-mapyaml-comments)
- [20261014_1233 — validator: accepts the compact template's generated-output wording](#20261014_1233--validator-accepts-the-compact-templates-generated-output-wording)
- [20261014_1213 — govern: stops on uncommitted governed files; drops resolved baseline entries](#20261014_1213--govern-stops-on-uncommitted-governed-files-drops-resolved-baseline-entries)
- [20261014_1202 — adopt: a future deadline is not a review date](#20261014_1202--adopt-a-future-deadline-is-not-a-review-date)
- [20261014_1102 — Token efficiency from the UNC run: compact AGENTS block, load cost, header validity](#20261014_1102--token-efficiency-from-the-unc-run-compact-agents-block-load-cost-header-validity)
- [20261014_1058 — deterministic navigation-control upgrade](#20261014_1058--deterministic-navigation-control-upgrade)
- [20261014_1051 — govern fixes from the UNC run: folded legacy headers stay fenced; audit failures named](#20261014_1051--govern-fixes-from-the-unc-run-folded-legacy-headers-stay-fenced-audit-failures-named)
- [20261014_1039 — govern: one-step governance recipe and skill mode; refresh runs it first](#20261014_1039--govern-one-step-governance-recipe-and-skill-mode-refresh-runs-it-first)
- [20261014_1030 — role_check: context-map.yaml must parse (nav_validate stays manual)](#20261014_1030--role_check-context-mapyaml-must-parse-nav_validate-stays-manual)
- [20261010_2014 — Rotation fixes (explicit pins, prose units, lazy continuation); move_sections; split audit; adopter fixes](#20261010_2014--rotation-fixes-explicit-pins-prose-units-lazy-continuation-move_sections-split-audit-adopter-fixes)

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

## 20261015_0129 — doc_freshness: a Budget header counts only with a size

- `scripts/doc_freshness.py`: a `Budget` header counts as a file budget only when it states a size (`N lines` or `N KB`); a Python docstring line such as "Budget: 60 seconds" (a runtime budget) made two unified-network-controller modules fail as over a 200-line file budget (2026-10-15).

## 20261014_1247 — yaml_key_diff: context-map key changes and lost comments after an upgrade

- New `scripts/yaml_key_diff.py` (recipe `nav_check_context_map`, skill and project template justfiles; catalogued; `tests/test_yaml_key_diff.py`):
  compares `context-map.yaml` with a git ref by key and lists lost comments, exit 1 while one is lost. Smoke on smc-resiliency vs b1483af: two
  added keys, one expected lost comment (the old version stamp). Promoted from the smc-resiliency refresh's ad hoc check. 102 tests.
- `references/navigation-automation.md`: run the scripts with the venv python or `just nav_*`; a bare `python3` stops the upgrader on PyYAML.
  Step 5 names the new check. `references/pitfalls.md` points to it.

## 20261014_1234 — pitfalls: the navigation upgrade drops context-map.yaml comments

- `references/pitfalls.md`: the update_rules merge re-serialises `context-map.yaml` and loses its comments, including the purpose
  header; compare old and new by key, then restore the comments (smc-resiliency refresh, 2026-10-14).

## 20261014_1233 — validator: accepts the compact template's generated-output wording

- `validate_navigation_control_layer.py`: the generated-output policy check matched only "support-only", but the compact template
  (2026-10-10-compact-v1 on) says "never a source of truth", so every compact-block project failed it (found on smc-resiliency
  refresh, 2026-10-14). It now accepts both wordings.
- New `tests/test_validate_navigation.py` runs the validator against `templates/AI_NAVIGATION.md`, so template wording that the
  validator rejects fails a test; red without the fix, green with it. 99 tests.

## 20261014_1213 — govern: stops on uncommitted governed files; drops resolved baseline entries

- New `scripts/govern_guard.py`, first step of both `govern` recipes (template and skill): exits 1 listing governed paths
  with uncommitted work; `GOVERN_ALLOW_DIRTY=1` overrides. On enterprise-strategy (2026-10-14) govern rotated an uncommitted
  CHANGELOG and its edits could not be split from the operator's.
- `doc_freshness.py` and `role_check.py`: `--prune-baseline` drops resolved entries and never adds one; kept entries keep their
  recorded value, so an over-budget size stays the ratchet. govern runs it on both baselines. `--write-baseline` was unsafe for
  this: it also absorbs new findings.
- Project copies of `govern` pick the guard up on their next run (adopt refreshes them mid-run), so the first run after this
  release is still unguarded.
- Tests: `tests/test_govern_guard.py` (6). Live: cambium-swap refused (dirty `justfile`), enterprise-strategy passed.

## 20261014_1202 — adopt: a future deadline is not a review date

- `adopt_governed_files.py` `fix_record`: `Last reviewed` derived from content now ignores dates after today. On enterprise-strategy (govern run, 2026-10-14)
  it took a 25 Oct deadline in SCRATCHPAD as the review date and wrote 2026-10-25 on CHANGELOG and SCRATCHPAD; both corrected by hand.
- Test: `test_future_deadline_is_not_the_review_date`, shown failing without the fix (17 tests, OK with it).
- Other projects adopted earlier may carry a future `Last reviewed`; checked across governed projects in the same session.

## 20261014_1102 — Token efficiency from the UNC run: compact AGENTS block, load cost, header validity

- **Token efficiency, from the UNC run** (operator, 2026-10-14: confirm UNC follows efficient token use; fix gaps in the skill). UNC loaded 50 KB
  (~12,800 tokens) before work, and its preflight forced a full read of context-map.yaml (10.8 KB). Skill gaps fixed: the AGENTS navigation block
  (26 lines restating AI_NAVIGATION, still naming Graphify output) is now 9 lines of hard rules plus a pointer, and context-map.yaml is read only
  when routing or companions change (version `2026-10-14-compact-v2`); `role_check.py` prints `always loaded: N files, X KB (~T tokens)`
  following `@` imports; `govern` applies the navigation-block upgrade when its dry run is clean. UNC after: 48 KB (~12,500 tokens), AGENTS.md
  203 to 191 lines (within budget), and no forced context-map read.
- **Header validity:** `role_check.py` front-matter rule parses the header as YAML (UNC AGENTS.md had text after `>-`; smc-resiliency README an
  unquoted `: `); the adopter quotes values that need it (`fm_value`) and no longer mistakes a sentence with a colon for a `Key: value` line.
- **Outdated `govern` copies refreshed** by the adopter (project form only); interpreter detection ignores calls inside `$(...)`.
- **Checker:** CHANGELOG.md exempt from the unregistered-restatement scan (history; it stated the new stamp). Also carried: the other session's
  adopter fix for folded continuation lines and the govern summary naming rotation-audit losses (entry 20261014_1051).

## 20261014_1058 — deterministic navigation-control upgrade

<!-- skill-ai-it-upgrade: 2026-10-14-compact-v2 -->

- Applied `skill-ai-it` deterministic navigation-control upgrade.
- Upgraded managed navigation/scripts blocks to version `2026-10-14-compact-v2`.
- Ensured `context-map.yaml` contains `skill_ai_it_version`, `audit_checks`, `promotion_rules`, `context_recovery`, and `update_rules`.
- Preserved user-authored content outside managed blocks.
- Generated outputs remain support-only; no `.archcore/` promotion was performed.

Applied to: AI_NAVIGATION.md, context-map.yaml, AGENTS.md, scripts/README.md

## 20261014_1051 — govern fixes from the UNC run: folded legacy headers stay fenced; audit failures named

- **adopt_governed_files.py:** a legacy (unfenced) header's folded value now keeps its indented continuation lines inside the new fence; before,
  the fence closed after the first line and the tail landed below the `@` import (UNC AGENTS.md, first `govern` run). Test added (14 pass).
- **govern recipe** (justfile, templates/justfile): the NEEDS ATTENTION reason also names `audit: LOST|SPLIT`; it was blank when the rotation audit
  failed, because budget_plan.py returns before printing UNFINISHED. cambium-swap's adopted copy still has the old grep.

## 20261014_1039 — govern: one-step governance recipe and skill mode; refresh runs it first

- **`govern`: one step to the current standard** (operator, 2026-10-14: "wrap steps 1-3 into one recipe", a `govern` argument for the skill, and
  `refresh` calls govern before fixing content). `just govern [project]` here and a project-local `just govern` (template; adoption adds it):
  `adopt_governed_files.py --apply`, `budget_plan.py --apply` (rotation, ROADMAP trim, the project's `just check`), `role_check.py`, then one
  summary line naming what still needs attention; exit 1 when a file stays over budget or the check fails. SKILL.md: new `govern` mode
  (`/skill-ai-it govern`, no content edits); `refresh` runs `govern` first, then fixes content by the role findings. Measured: about 1 s on this
  package and on cambium-swap (budget: under 60 s). Canary cambium-swap: recipe added, 4 done ROADMAP items moved to history, summary names its
  over-budget AGENTS.md (220 lines). Adoption only adds a missing recipe; it does not refresh an existing `govern` copy.

## 20261014_1030 — role_check: context-map.yaml must parse (nav_validate stays manual)

- **`role_check.py` rule 8, `context-map-parse`** (operator, 2026-10-14: "keep nav_validate manual, and add one rule to role_check:
  context-map.yaml must parse"). Fails when the map does not parse or repeats a key; PyYAML absent reports SKIPPED, never passed. All 26
  context-map.yaml files under project_stuff and specialists parse today, so no project turns red. Test added; proven on this package (a repeated
  `version` key failed `just check`, restored green). `nav_validate` stays out of `check` (it fails every project on a skill version bump).

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
