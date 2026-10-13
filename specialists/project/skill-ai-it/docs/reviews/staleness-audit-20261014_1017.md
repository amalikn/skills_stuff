---
Title: Staleness audit — skill-ai-it — 2026-10-14
Category: audit
Status: current
Authority: record
Scope: The whole skill-ai-it package, focus on changes since 9ed0a35
Last reviewed: 2026-10-14
Summary: >-
  No money-band finding (the package files nothing with third parties). Two enforcement holes fixed (the upgrader created a role-failing
  AGENTS.md; CHANGELOG was enforced as a live surface for a past fact), six drift items fixed, two derived checks added and negative-tested.
---

# Staleness audit — `skill-ai-it` — `2026-10-14`

<!-- claim-scan:examples reason="names filenames as examples of a class, not as references" -->

**Scope:** whole package (121 files), focus on the 96 files changed since `9ed0a35`
**Standard:** would a careful reader be misled — not "does the suite pass"
**Validation:** 343 checks before → 368 after · `just check` green (governance, doc freshness, file roles); 86 unit tests green

---

## Contents

- [What was found that could cost money](#what-was-found-that-could-cost-money)
- [Why it survived](#why-it-survived)
- [What was corrected](#what-was-corrected)
- [Coverage](#coverage)
- [Claim verification](#claim-verification)
- [New checks, and proof they can fail](#new-checks-and-proof-they-can-fail)
- [Errors made during this audit](#errors-made-during-this-audit)
- [What this run does NOT prove](#what-this-run-does-not-prove)
- [Residual risks](#residual-risks)
- [Next actions](#next-actions)
- [Audit evidence](#audit-evidence)
- [Gate result](#gate-result)

## What was found that could cost money

None. The package holds governance tooling and no money, licence, filing or price figure; band M is empty. The most expensive finding
is H1 below, because it would have broken every project's `just check` on first contact.

> **H1 — the upgrader created a role-failing AGENTS.md.** `upgrade_navigation_control_layer.py` wrote a new AGENTS.md with an unfenced
> `Title:` header. **Latent, never realised**: no project lacked AGENTS.md when the role check was adopted. It would bite the first time
> `just nav_upgrade` ran on a project without AGENTS.md after adoption: the new file is a role finding outside the baseline, so `just check` fails.

## Why it survived

The role check was written the same day from the templates in `references/`; the upgrader builds its own header in code, a second generation
path the template audit did not reach. Phase 4's question "does it compute anything whose meaning changed" found it, not a grep. Likewise the
CHANGELOG version-stamp surface: it passed for weeks because the stating entry was never old enough to rotate.

## What was corrected

| Area | Change |
|---|---|
| Upgrader | New AGENTS.md gets fenced front matter; regression test |
| Checker | CHANGELOG retired as a version-stamp surface (history); `check_reference_index_lines` derives the references index counts |
| references/readme.md | Three stale line counts recomputed |
| ROADMAP.md | Two links to UNC `target_map.py` repointed to `scripts/render/` |
| SCRATCHPAD.md | 2026-08-11 counts superseded by a dated banner (`count:asat`); a done open item ticked |
| Graphify | Two ungated recovery steps gated (context-map.yaml, patterns/navigation/recovery-and-audit.md) |
| Indexes | `docs/`, `docs/archive/`, `patterns/`, `templates/` get folder indexes; baselines named in scripts/README.md |

## Coverage

```text
Total files in scope:            121
  Examined:                      100
  Exempt (reason stated):        21
  Out of scope (stated):         0
                                ----
                                 121   ✓ reconciles
```

No binary or tabular files in the package. Six structured-config files were parsed strictly (JSON, JSONC with comments stripped, YAML with
a duplicate-key loader): all valid, no duplicate keys.

## Claim verification

```text
Checkable claims:                1726
  VERIFIED against source:       1243
  MARKED-HISTORICAL:             18
  RESIDUAL (see register):       465
                                ----
                                 1726   ✓ reconciles
```

Residual splits into 189 path claims that do not resolve in this package (classified: about half in history and archived docs, 9 test
fixtures, the rest paths that exist in target projects, which this package specifies), 145 conditional paths and 131 claims needing a reader.
The one absolute path among them (UNC `target_map.py`) was real drift and is fixed.

## New checks, and proof they can fail

| Check | Defect it exists for | Negative-tested |
|---|---|---|
| `check_reference_index_lines` | Authored line counts in references/readme.md drifted | ✓ red on the three stale counts, green after recompute |
| `test_new_agents_md_has_fenced_front_matter` | Upgrader wrote an unfenced AGENTS.md header | ✓ red on the HEAD upgrader, green on the fix |

## Errors made during this audit

None during the audit itself. Earlier in the same session, all fixed before this run: a ROADMAP edit left three stray lines after the trim;
a YAML scalar with `: ` broke context-map.yaml (caught by `nav_validate`, not `just check`); adoption grew an over-budget AGENTS.md and failed
the ratchet in the cambium-swap canary. Two SCRATCHPAD lines this audit edited on purpose are recorded in `docs/history/rotation-audit-baseline.txt`.

## What this run does NOT prove

Every checkable claim is now verified, marked historical, or listed as residual. **That does not establish that any external fact is still
true**: the paths into target projects and the behaviour of external tools (Archcore, Repomix, markdownlint) were not re-checked here.

## Residual risks

SCRATCHPAD.md, open item "Residual risk, staleness audit 20261014". The two that matter most: `nav_validate` is not in `just check`, so a
broken context-map.yaml passes the gate; the role check's duplicate rule misses reworded copies.

## Next actions

1. Decide whether `just check` runs `nav_validate` (or a YAML parse of context-map.yaml).
2. Roll the role check out to the other 11 projects (CHANGELOG 20261014_1002) and work their baselines down.

<!-- BEGIN staleness-audit:evidence sha256=4c67d3997eb0beee2b4e25821662bc1cc492d5c7199557b6c0a3cd22063f48b6 -->
## Audit evidence

Generated by `audit_report.py` from `.staleness-audit/` before the gate deleted it. Do not edit by hand; re-run the
script instead.

### Receipts

| Phase | Key | Value |
|---|---|---|
| 0 | `snapshot_path` | .staleness-audit-snapshot-20261013_230951 |
| 0 | `files_snapshotted` | 47 |
| 1 | `files_total` | 121 |
| 1 | `files_examined` | 100 |
| 1 | `files_exempt` | 21 |
| 1 | `files_out_of_scope` | 0 |
| 1 | `defects_found` | 8 |
| 1 | `systems_of_record` | 0 |
| 1 | `sor_objects_changed` | 0 |
| 1 | `sor_objects_read` | 0 |
| 2 | `defects_fixed` | 8 |
| 3 | `banners_added` | 1 |
| 4 | `artifacts_total` | 42 |
| 4 | `artifacts_reasoned` | 42 |
| 4 | `findings` | 1 |
| 5 | `checks_negative_tested` | 2 |
| 5 | `checks_added` | 2 |
| 6 | `residual_items` | 8 |
| 7 | `claims_total` | 1726 |
| 7 | `claims_verified` | 1243 |
| 7 | `claims_historical` | 18 |
| 7 | `claims_residual` | 465 |
| 7 | `claims_residual_manual` | 131 |
| 7 | `claims_residual_broken` | 189 |
| 7 | `claims_residual_conditional` | 145 |
| 7 | `claims_residual_on_box` | 0 |
| 7 | `inverse_orphan_dirs` | 0 |
| 7 | `inverse_unindexed_dirs` | 0 |
| 7 | `inverse_displaced_refs` | 0 |
| 7 | `inverse_empty_indexes` | 0 |
| 7 | `inverse_unlisted_entries` | 0 |

Focus: files changed since `9ed0a35` (`9ed0a3520010`).

### Negative tests

- **reference-index-lines** red — accepted; exit 1; `/Volumes/Data/_ai/_skills/skills-working-cache/specialists/project/skill-ai-it/.venv/bin/python scripts/check_governance.py`; expect `references/readme.md says`; output sha256 `3de745023ac6aa23`; 2026-10-13T23:11:41+00:00

  ```text
    ✗ count: references/readme.md says finishing.md has 152 lines; it has 153
    ✗ count: references/readme.md says generation-policy.md has 155 lines; it has 160
    ✗ count: references/readme.md says pitfalls.md has 38 lines; it has 55
  …
  FAIL — 3 issue(s) across 361 checks
  
    ✗ count: references/readme.md says finishing.md has 152 lines; it has 153
    ✗ count: references/readme.md says generation-policy.md has 155 lines; it has 160
    ✗ count: references/readme.md says pitfalls.md has 38 lines; it has 55
  ```

- **reference-index-lines** green — accepted; exit 0; `/Volumes/Data/_ai/_skills/skills-working-cache/specialists/project/skill-ai-it/.venv/bin/python scripts/check_governance.py`; expect `references/readme.md says`; output sha256 `1b9fe0b92e8a568f`; 2026-10-13T23:11:41+00:00

  ```text
  …
  OK — 361 governance checks passed
  ```

- **upgrader-agents-front-matter** red — accepted; exit 1; `/Volumes/Data/_ai/_skills/skills-working-cache/specialists/project/skill-ai-it/.venv/bin/python -m unittest tests.test_upgrade_navigation_control_layer`; expect `FAIL: test_new_agents_md_has_fenced_front_matter`; output sha256 `e9d7dad39ac78502`; 2026-10-13T23:15:35+00:00

  ```text
  FAIL: test_new_agents_md_has_fenced_front_matter (tests.test_upgrade_navigation_control_layer.AppendChangelogTest.test_new_agents_md_has_fenced_front_matter)
  …
  
  ----------------------------------------------------------------------
  Ran 3 tests in 0.006s
  
  FAILED (failures=1)
  ```

- **upgrader-agents-front-matter** green — accepted; exit 0; `/Volumes/Data/_ai/_skills/skills-working-cache/specialists/project/skill-ai-it/.venv/bin/python -m unittest tests.test_upgrade_navigation_control_layer`; expect `FAIL: test_new_agents_md_has_fenced_front_matter`; output sha256 `199ba496f288116d`; 2026-10-13T23:15:35+00:00

  ```text
  …
  ...
  ----------------------------------------------------------------------
  Ran 3 tests in 0.002s
  
  OK
  ```


### `defect-register.md`

### Defect register — skill-ai-it, 2026-10-14

| # | Materiality | File:line | Defect | Evidence | Fix |
|---|---|---|---|---|---|
| 1 | H | scripts/upgrade_navigation_control_layer.py:629 | Created AGENTS.md with an unfenced header; `role_check.py` front-matter rule fails a project the moment the upgrader creates the file | Phase 4 reasoning; smoke run in scratchpad/upg2 | Fenced front matter; test `test_new_agents_md_has_fenced_front_matter` (negtest red/green) |
| 2 | H | scripts/check_governance.py CONSTANT_SURFACES | CHANGELOG.md registered as a live surface for the version stamp; rotation moved the stating entry and the check failed on history | `just check` FAIL after `just budget --apply` | CHANGELOG retired from surfaces with reason (CHANGELOG 20261014_1006) |
| 3 | G | references/readme.md:13-25 | Authored line counts stale (pitfalls 38 vs 55, generation-policy 155 vs 160, finishing 152 vs 153) | script comparison | Counts recomputed; `check_reference_index_lines` derives them (negtest red/green) |
| 4 | G | ROADMAP.md:47,56 | Links to UNC `scripts/target_map.py`, moved to `scripts/render/target_map.py` (UNC commit d51d953) | claim_scan BROKEN | Links repointed |
| 5 | G | SCRATCHPAD.md:39-40 | KEEP block states "129 assertions" and "twelve surfaces" (as at 2026-08-11; now 361 checks, 11 surfaces) | `just check` output; CONSTANT_SURFACES | Dated supersession banner, `count:asat` marker |
| 6 | G | SCRATCHPAD.md:72 | Open item "Dogfood the checker" still open; done since 2026-08-11 | scripts/check_governance.py in `just check` | Ticked with date and evidence |
| 7 | G | context-map.yaml:270, patterns/navigation/recovery-and-audit.md:32 | Recovery steps said to regenerate graphify-out (Graphify disabled 2026-10-10) | grep | Gated wording (fixed in slurp, before this audit) |
| 8 | G | all-scraper README.md:81 | `scripts/all-scraper.sh` paths only valid from tools_stuff/ (seen 2026-09-29, unfixed) | ls | README note (tools_stuff repo) |


### `artifacts.md`

### Phase 4 — per-artifact reasoning worksheet

**One line per artifact. Skipping an artifact is fine; skipping the QUESTION is not.**

Ask all three prompts of each:

1. Does it print or compute anything whose **meaning** changed, though its wording did not?
2. Does it assume **continuity, completeness, or availability** that is no longer true?
3. Does it **enumerate a live inventory** (an API list, a database, an inventory file) whose population
   changed since the last audit? Then its reach changed with no line of code changing. `REACH?` rows also
   write, install or connect: name what the population is today and whether every member is meant.

`GENERATOR` rows get a third: **would running it now revert something?** Run it and diff —
a clean diff proves the output is current and proves nothing about the generator's assumptions.

Flags are a PRIORITISATION HINT, not an answer. An unflagged artifact still needs a verdict,
and "clear" needs a reason — an unfalsifiable verdict is not a verdict.

Artifacts: **42**

Focus: **8** changed since 9ed0a35, listed first. Every artifact still needs a verdict.

| Artifact | What it is | Flags | Verdict (fill in) |
|---|---|---|---|
| `scripts/adopt_governed_files.py` | Check a project's adoption of the governed-file standard and add what is missing. Idempotent. S | CHANGED back-solve? GENERATOR | |
| `scripts/budget_plan.py` | Bring a project's governed files within budget, or say exactly what keeps one over. Stdlib plus | CHANGED back-solve? continuity? GENERATOR | |
| `scripts/check_governance.py` | Governance coherence checks for <PROJECT NAME>. | CHANGED back-solve? continuity? | |
| `scripts/role_check.py` | Check that a project's root governance files keep to their roles, as a ratchet that only tighte | CHANGED GENERATOR | |
| `scripts/upgrade_navigation_control_layer.py` | Deterministic upgrade script for skill-ai-it navigation control layer. | CHANGED back-solve? continuity? GENERATOR | |
| `tests/test_adopt_governed_files.py` | Offline tests for scripts/adopt_governed_files.py: it adds only what is missing and a second ru | CHANGED back-solve? GENERATOR | |
| `tests/test_role_check.py` | Offline tests for scripts/role_check.py: every rule fails on a breach and passes on a project t | CHANGED back-solve? GENERATOR | |
| `tests/test_upgrade_navigation_control_layer.py` | Offline tests for scripts/upgrade_navigation_control_layer.py: the CHANGELOG entry it writes ca | CHANGED GENERATOR | |
| `scripts/add_changelog_entry.py` | Add one entry to a project's CHANGELOG.md in that project's own heading style and order, with i | back-solve? GENERATOR | |
| `scripts/agent_usage.py` | Measure whether agents actually use a file, folder or command, from recent Claude Code transcri | back-solve? | |
| `scripts/audit_rotations.py` | Audit rotated records: every content line of a record before its first rotation is still live,  | back-solve? | |
| `scripts/check_expected_diff.py` | Check that only expected files changed after a navigation control upgrade. | back-solve? GENERATOR | |
| `scripts/check_outside_blocks.py` | Confirm that a navigation upgrade changed only the text inside skill-ai-it's managed blocks. | — | |
| `scripts/doc_freshness.py` | Find project files that have gone stale, grown past their budget or lack a header, as a ratchet | back-solve? GENERATOR | |
| `scripts/docstring_ratchet.py` | Measure and hold a project's Python docstrings to the global standard, as a ratchet that only t | GENERATOR | |
| `scripts/file_headers.py` | Read every governed file's header in the form native to its type, and list them so a file is as | back-solve? | |
| `scripts/md_sections.py` | Read a large Markdown file by section: an outline with each heading's line range, or one sectio | back-solve? | |
| `scripts/migrate_legacy_blocks.py` | Move a project's managed blocks from the pre-2026-09-23 layout to the template-sourced one with | back-solve? GENERATOR | |
| `scripts/move_doc.py` | Move a project document (typically a superseded one into its folder's `archive/`) without break | back-solve? GENERATOR | |
| `scripts/move_sections.py` | Move named sections of a governed markdown file (AGENTS.md, SCRATCHPAD.md, SKILL.md) verbatim i | back-solve? GENERATOR | |
| `scripts/normalise_records.py` | Give a working-state record (SCRATCHPAD.md) the headings rotation needs, without changing a lin | back-solve? GENERATOR | |
| `scripts/roadmap_trim.py` | Keep ROADMAP.md to what is open: move every done item into a dated archive under docs/history/, | back-solve? GENERATOR | |
| `scripts/rotate_records.py` | Rotate a running record (CHANGELOG.md, SCRATCHPAD.md) into dated archive files so the live file | back-solve? GENERATOR | |
| `scripts/selftest_blocks.py` | Self-test for the managed-block builders in upgrade_navigation_control_layer.py. | back-solve? continuity? GENERATOR | |
| `scripts/skills_registry.py` | Build or check a project area's skills.md: the list of skills its child projects invoke. | back-solve? GENERATOR | |
| `scripts/split_checker.py` | Split a project's single-file `scripts/check_governance.py` into the govcheck package (patterns | back-solve? continuity? GENERATOR | |
| `scripts/validate_navigation_control_layer.py` | Validate the navigation control layer in a project. | back-solve? continuity? GENERATOR | |
| `templates/check_governance.py` | Governance coherence checks for <PROJECT NAME>. | back-solve? | |
| `templates/context_preflight.sh` | /usr/bin/env bash | — | |
| `templates/govcheck/checks/structure.py` | The checker's own shape (skill-ai-it patterns/governance-checks.md, "Structure and growth"): sm | continuity? | |
| `templates/govcheck/core.py` | Engine of a project's governance checker: failure collection, assertion counting, the runner an | — | |
| `tests/test_add_changelog_entry.py` | Offline tests for scripts/add_changelog_entry.py: each project's heading style and order, the C | back-solve? GENERATOR | |
| `tests/test_agent_usage.py` | Offline tests for scripts/agent_usage.py --md-reads: outline greps, recipe calls and whole/rang | GENERATOR | |
| `tests/test_audit_rotations.py` | Offline tests for scripts/audit_rotations.py: an entry whose first line moved while its wrapped | GENERATOR | |
| `tests/test_budget_plan.py` | Offline tests for scripts/budget_plan.py: a SCRATCHPAD of dated bold paragraphs and a reference | back-solve? GENERATOR | |
| `tests/test_check_outside_blocks.py` | Offline tests for scripts/check_outside_blocks.py: managed blocks are ignored, any change outsi | GENERATOR | |
| `tests/test_md_sections.py` | Offline tests for scripts/md_sections.py: line ranges, fences, setext, exact-by-default selecto | GENERATOR | |
| `tests/test_move_doc.py` | Offline tests for scripts/move_doc.py: repeated --keep-records flags all protect their files. | GENERATOR | |
| `tests/test_move_sections.py` | Offline tests for scripts/move_sections.py: sections move verbatim, Contents and pointer are ri | back-solve? GENERATOR | |
| `tests/test_normalise_records.py` | Offline tests for scripts/normalise_records.py: headings are added, no original line changes, a | GENERATOR | |
| `tests/test_roadmap_trim.py` | Offline tests for scripts/roadmap_trim.py: done items move with their continuation lines, open, | back-solve? GENERATOR | |
| `tests/test_rotate_records.py` | Offline tests for scripts/rotate_records.py: rotation never loses a content line, keeps prose u | GENERATOR | |

<!-- END staleness-audit:evidence -->

<!-- BEGIN staleness-audit:gate -->
## Gate result

```text
GATE PASSED 2026-10-14 10:18
coverage      : 105 examined + 24 exempt = 129
structured    : 4 files parsed (duplicate keys checked)
old-value hits: 0 for none given
inverse sweep : 0 item(s)
suite         : exit 0 (just check)
warning       : PyYAML absent — YAML duplicate-key detection SKIPPED, not passed
Does NOT establish that any claim about the external world is still true; for those the audit verified provenance label and as-at date only.
```
<!-- END staleness-audit:gate -->
