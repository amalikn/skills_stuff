---
Title: Changelog
Category: change-log
Status: current
Summary: Newest entries only; older ones rotate to docs/history (search with --find, print with --show).
Kind: log
Budget: 200 lines, 25 KB
Archive: docs/history/ (`--find`, `--show`)
Last rotated: 20261010_1808
---

# Changelog — Agent Stack

## Contents

- [20261010_1805 — Governed-file standard: recipes, SCRATCHPAD rotated, checker split into scripts/govcheck](#20261010_1805--governed-file-standard-recipes-scratchpad-rotated-checker-split-into-scriptsgovcheck)
- [20260905_0036 — quick_validate.py enforces the agentskills.io name/directory match](#20260905_0036--quick_validatepy-enforces-the-agentskillsio-namedirectory-match)
- [20260904_1710 — Scoped staleness audit on the new survey document; a stale entry found in the standing 2026-09-01 residual register](#20260904_1710--scoped-staleness-audit-on-the-new-survey-document-a-stale-entry-found-in-the-standing-2026-09-01-residual-register)
- [20260904_1654 — New document: best-of-agent-harnesses survey, screening a 160-project external list for relevance](#20260904_1654--new-document-best-of-agent-harnesses-survey-screening-a-160-project-external-list-for-relevance)
- [20260904_1630 — Provenance detail section added to the phased implementation plan, at operator request](#20260904_1630--provenance-detail-section-added-to-the-phased-implementation-plan-at-operator-request)
- [20260904_1230 — Scoped staleness re-audit: two path defects fixed, prior 20260903_2200 register re-verified](#20260904_1230--scoped-staleness-re-audit-two-path-defects-fixed-prior-20260903_2200-register-re-verified)
- [20260904_1208 — Phased implementation and self-verification plan added, inert pending an operator-named trigger](#20260904_1208--phased-implementation-and-self-verification-plan-added-inert-pending-an-operator-named-trigger)
- [20260904_1155 — Sentry Skills / Prompt Optimizer row upgraded from recommendation to adopted record](#20260904_1155--sentry-skills--prompt-optimizer-row-upgraded-from-recommendation-to-adopted-record)
- [20260904_1150 — Six proposed archcore documents accepted by the operator](#20260904_1150--six-proposed-archcore-documents-accepted-by-the-operator)
- [20260901_1315](#20260901_1315)

## 20261010_1805 — Governed-file standard: recipes, SCRATCHPAD rotated, checker split into scripts/govcheck

- Workspace standard (operator, 2026-10-10; skill-ai-it "Governed files: headers, budgets, rotation and the checker's shape"): `justfile` gains
  `ai_it`, a second `check` line running skill-ai-it's `doc_freshness.py --check`, and the `stale`, `docs`, `history`, `history-show` and `rotate`
  recipes; `AGENTS.md` Working rules gain the triage line (`just docs <folder>`, `just stale`, `just history`); `doc_freshness.py --write-baseline`
  grandfathers existing findings (scripts/doc-freshness-baseline.json, 156 entries), so only new ones fail.
- SCRATCHPAD.md rotated 741 -> 655 lines (28 entries to `docs/history/`; the rest are undated or open and stay). CHANGELOG.md (1,268 lines) NOT rotated:
  skill-ai-it's rotate_records refused (44 removed lines not found in the archive) and wrote nothing; left for review.
- `scripts/check_governance.py` (910 lines) split by skill-ai-it's split_checker into `scripts/govcheck/` (config, helpers, core, six families
  plus `structure`); output identical before and after. The recipe-to-script scan now ignores another package's `{{ai_it}}/scripts/...` paths, and
  catalog coverage exempts the rotated archives (indexed by `docs/history/readme.md`, routed from `docs/README.md`).

## 20260905_0036 — quick_validate.py enforces the agentskills.io name/directory match

### Fixed

- `skills/skill-creator/scripts/quick_validate.py` checked the `name` field's character set and length against the agentskills.io specification but never checked the spec's other MUST for that field:
  the name must match the parent directory name. Found while comparing Agent Stack's skill contract against the agentskills.io open standard at operator request (following up on Hermes Agent citing it
  as its skills format) — the rest of the frontmatter contract (six spec fields plus 13 local extension fields, length/charset constraints) already matched the spec exactly, this was the one gap.
  Added the check; ran it against every skill directory in the repo with no false positives, then `just preflight` (1119 governance checks, 51 tests) green.

## 20260904_1710 — Scoped staleness audit on the new survey document; a stale entry found in the standing 2026-09-01 residual register

### Fixed

- The best-of-agent-harnesses survey (20260904_1654 entry below) originally stated a summed-total arithmetic error — "78 of 160 in-lane / 82 out of scope" where the correct sums of its own
  (individually correct) per-category counts are 77 and 83 — restated identically across six surfaces: the document's own frontmatter and body, this file, SCRATCHPAD.md, and both memory-keeper and
  mcp-project-context. Corrected everywhere; the 20260904_1654 entry below reflects the corrected figures directly, since it was not yet committed when the error was caught. Also corrected: an
  omnigent citation off by one line (README.md:11 -> the alpha-status badge is actually at README.md:12), and an approximation ("roughly 30 relevant projects") that undercounted a script-verified
  total of 40 named/individually-reasoned projects by a third.
- SCRATCHPAD.md's standing "Residual risk after the 2026-09-01 staleness audit" register: found stale during this audit's "confirm still valid" step, not introduced by anything in this entry. It
  described `personas/README.md` as absent, with "adding a README failed `just governance` immediately" — but that file was added and registered in `scripts/check_governance.py`'s `CATALOGS` on
  2026-09-03 (commit `c623350`), two days after the register was written and never updated to say so. Per the staleness-audit skill's own Phase 3 (supersession banners, don't rewrite history), the
  original paragraph is left as written with a `RESOLVED 2026-09-03` note appended in place. The matching Open Items checkbox was updated from "two residuals remain formally unaccepted" to "one" —
  only `skills/tailwind-v4-shadcn/templates/tsconfig.app.json`'s JSONC-vs-strict-JSON mismatch is still genuinely open.
- A second occurrence of the same-day governance false positive (backticking an external filename inside a governance "surface" file trips `check_referenced_paths()`'s path-existence check) — this
  time in SCRATCHPAD.md itself, same fix as the CHANGELOG.md occurrence below: write the external filename in plain prose, don't backtick it.

### Project coherence

Ran a coherence pass after the fixes above (change: corrected counts + one resolved-residual annotation). Checked AI_NAVIGATION.md, context-map.yaml, AGENTS.md, CLAUDE.md, `.archcore/`, and
`skills/skill-agent-stack/SKILL.md` for any reference to the survey's counts or to the personas/README residual — none found; `AI_NAVIGATION.md` already correctly points at `personas/README.md` as the
index (consistent with the 2026-09-03 fix, no update needed there). A repo-wide grep for the old figures found only the expected, correctly-framed audit-trail mentions in SCRATCHPAD.md's own "were
wrong" / "undercounted" sentences — no unexpected hits in active files. Did not propagate the new survey's own proposed-next-step candidates (Gemini CLI, opencode, aider, etc.) into the phased
implementation plan or the reliability-adaptation proposal — per this project's own standing rule, the external adaptation backlog is not implemented pre-emptively, only when an operator names a
triggering gap. Did not regenerate `.ai-context/`/`graphify-out/` — this change is a working document plus a corrected count and a residual-register annotation, not a structural change to
personas/skills/routing for either generator to re-map.

Verified: `just governance` (1118 checks, up from 1115 at the prior slurp checkpoint) and `just preflight` (51 tests) both green after every fix in this pass.

## 20260904_1654 — New document: best-of-agent-harnesses survey, screening a 160-project external list for relevance

### Added

- docs/reliability-adaptation/best-of-agent-harnesses-survey-20260904_1646.md: a source-verified screen of every project in ryanalberts/best-of-Agent-Harnesses (fetched directly as its own
  harnesses.json data file and README.md via `raw.githubusercontent.com`, not from a lossy HTML-to-markdown preview) against Agent Stack's own scope. 5 of 12 categories (77 of 160 projects) are
  in-lane; 40 are named and individually reasoned about in the findings table, each given a STEAL/ADAPT/CONFIRM/USE/WATCH/ALREADY-ASSESSED/SKIP verdict matching the vocabulary of the prior
  external-orchestrator-survey. The other 7 categories (83 projects) are recorded as confirmed-not-guessed out of scope. Two multi-agent projects not covered by the prior 25-repo survey (`omnigent`,
  `openai-agents-python`) were opened and quoted with file/line at operator request rather than left at description-only depth — `omnigent`'s "meta-harness" tagline turned out to wrap an always-on
  collaborative session server (STEAL idea-only, same daemon caveat as MetaGPT/AutoGen); `openai-agents-python`'s `handoff()` carries a typed `input_type` payload schema and a dynamic `is_enabled`
  legality gate (ADAPT), a narrower pair of primitives than Agency Swarm's already-assessed `extra_params_model` for the same handoff-legality declaration Phase 2 of the reliability-adaptation
  proposal sketches.
- docs/README.md: registered the new document in the Reliability adaptation table.

Verified: `just governance` (1113 checks) and `just preflight` (51 tests) both green.

## 20260904_1630 — Provenance detail section added to the phased implementation plan, at operator request

### Added

- docs/reliability-adaptation/phased-implementation-and-self-verification-plan-20260904_1208.md: a new "Provenance detail — feature, pick, effect, benefit" section, one prose block per repo across all
  17 rows of the existing "Tool and feature provenance" table. Operator found the single-line table (necessarily terse, per its own 200-character wrap-safety convention) did not answer what each
  source repo is actually known for, what narrow feature is being taken from it, whether the result enhances an existing Agent Stack surface or adds a new one, and what the end benefit is. A literal
  four-column table extension was considered and rejected: cramming four substantive answers into table cells would either be too terse to answer the question or long enough to trip the same
  wrap-corruption bug the existing table already guards against (see the 20260904_1208 entry below). Used prose blocks instead, organised under the same five phase headings as the rest of the
  document. No new information beyond what the reliability adaptation proposal's own comparison table and adaptation map already state — this restates their content per-repo, next to the phase it
  belongs to.
- Contents block and anchor updated to match (the project's own PostToolUse hook auto-syncs Contents to real headings, confirmed by watching a manually-added Contents entry get silently stripped until
  the matching heading existed).

Verified: `just governance` (1111 checks) and `just preflight` (51 tests) both green after the addition.

## 20260904_1230 — Scoped staleness re-audit: two path defects fixed, prior 20260903_2200 register re-verified

### Fixed

- skills/tailwind-v4-shadcn/SKILL.md: 5 occurrences of the singular "reference/" corrected to the real "references/" directory (common-gotchas.md, dark-mode.md), matching the 9 already-correct
  occurrences in the same file.
- docs/routing-evaluation/routing-failure-classification-20260901_1842.md:10 no longer links to agent-stack-capability-taxonomy-and-scoring.md, an untracked Baseline-v2-era draft one level above this
  repository that was never migrated in. Rewrote as prose naming what it is and pointing at Rule 0007 and routing.toml as what actually stands now. This resolves the residual the 20260904_0737
  docs-reorg entry explicitly left alone ("a known residual from an earlier phase, not something this reorganisation should paper over") — that entry's relative-path correction stands; this pass gives
  the underlying dead reference its actual resolution rather than leaving it dead indefinitely.

### Changed

- SCRATCHPAD.md: added a dated addendum under the existing 20260903_2200 residual-risk register (not a rewrite — history stays as written) recording this scoped re-audit's findings: the prior
  register's six items re-verified unchanged, the two fixes above, and today's own new reliability-adaptation documents' forward-looking file mentions classified EXEMPT (prospective, not yet built)
  rather than defects.

Run via skill-staleness-audit's own scripts (snapshot, coverage manifest, claim scan) as part of an operator-queued sequence. Explicitly scoped: full materiality-ranked treatment was given to this
project's own core surfaces; the pre-existing ~89 `skills/` path findings and ~163 manual-verification claims were sampled to confirm the existing register's characterisation still holds, not
re-triaged individually. The audit skill's completeness gate was not run to a PASS claim on that basis — this is a stated partial pass, snapshot and receipts kept intentionally, not a clean exit.
Verified: `just governance` (1111 checks) and `just preflight` (51 tests) both green after the fixes.

## 20260904_1208 — Phased implementation and self-verification plan added, inert pending an operator-named trigger

### Added

- docs/reliability-adaptation/phased-implementation-and-self-verification-plan-20260904_1208.md: for each of the five phases in the reliability adaptation proposal, fixes the exact implementation
  steps, the self-verification checklist to run afterward, and the revert behaviour on a failed check. Written at operator request after raising a felt gap (orchestrator routing quality, personas not
  coordinating hand-offs) that the project's own evidence store (6 field-log entries, 0 capability gaps) does not yet substantiate. The document changes no code and authorises no phase on its own —
  each phase still requires the operator to name its evidence trigger and approve that phase individually, per the proposal's existing decision.
- A "Tool and feature provenance" table added to the same document at operator request: all 17 mechanisms named across the five phases, each row naming the exact source repo, file/symbol, and what it
  becomes in Agent Stack. Authored as single-line, unpadded rows kept under 200 characters per row, following the survey document's own established convention, after the project's automatic prose-wrap
  hook mis-wrapped a first draft of the table across physical rows (cosmetic column padding is fine; a wrapped, multi-line-per-row table is not — verified the fix by re-reading the file and checking
  no row spans more than one physical line).
- Catalogued in docs/README.md's Reliability adaptation table.

## 20260904_1155 — Sentry Skills / Prompt Optimizer row upgraded from recommendation to adopted record

### Changed

- docs/routing-evaluation/token-optimization-tools-and-strategy.md's Sentry Skills / Prompt Optimizer row changed from ADAPT the method, not the tool (an open recommendation) to ADOPTED, as method —
  ADAPTED (a record), pointing at accepted rule 0013. Same treatment the Token Optimizer row already got when that recommendation was acted on.

## 20260904_1150 — Six proposed archcore documents accepted by the operator

### Changed

- Operator accepted all documents that were still carrying Status: proposed: rules 0012 (gate flags advisory) and 0013 (trim against the frozen corpus), specs 0006 (runner qualification), 0007
  (gate-only evaluation), 0008 (replay corpus contract), and plan 0003 (Holdout 2 protocol). Each file's header now reads Status: accepted with an Accepted: 20260904_1150 by operator line alongside
  its original Proposed line, matching the convention already used by rule 0011 and the earlier 29-document batch. The 20260902_0300 "29 documents" acceptance count in .archcore/README.md is left
  untouched as a dated historical fact (count:asat), not restated to a new total.
- .archcore/README.md's Rules, Contracts and Plans tables had their *(proposed)* tags removed for all six; the Holdout 2 protocol plan row now reads "Approved" to match plan 0001's existing style.

## 20260901_1315

### Added

- Applied the routing-evals delta update (`/Volumes/Data/_ai/_skills/skills_stuff/specialists/agent-stack-update`, 50 files verified). New: `ROUTING_EVALS.md`, `scripts/evaluate_routing.py`,
  `tests/test_routing_behavior.py`, and the `routing-eval-check` / `routing-eval` / `routing-eval-smoke` tasks. `evals/routing-cases.toml` expanded from 6 representative cases to 60 real-workload
  cases across six families (`networking-infrastructure`, `software-ai-engineering`, `jdm-import`, `atar-import`, `business-research`, `direct-adversarial`); `routing.toml` gained network,
  infrastructure, import-evidence, import-economics, supply-chain, current-fact and regulatory-research intents and gates.
- `scripts/README.md` — cataloged `scripts/evaluate_routing.py` with safety labels. The coverage check caught the new script and failed the gate until it was cataloged, which is the intended workflow.

### Changed

- **Interpreter resolution made explicit.** The `justfile` now defines `py := <working-cache venv>/bin/python` and every Python recipe addresses `{{py}}` by path and depends on `_require-venv`;
  `.mise.toml` tasks carry the absolute venv path too, so the two entrypoints cannot resolve differently. Previously every recipe used `mise exec -- python`, which *did* resolve to the venv — but only
  implicitly, via `_.python.venv` activation. That form hides the dependency at the call site and degrades silently to the host interpreter if activation stops applying; it also made the in-repo venv
  violation invisible at every call site while it existed.
- `scripts/check_governance.py` — `check_no_bare_interpreter` replaced by `check_interpreter_pinning`, which now also fails an implicit `mise exec -- python`. Proven to fail by deliberate breakage.
  `ROUTING_EVALS.md` and `ARCHITECTURE.md` added to `SURFACES`.
- Re-applied after the update overwrote them: the venv path in `.mise.toml`, the governance recipes and pointers in `justfile` and `README.md`, and the `skills/` path prefix in `SKILL_STANDARD.md` and
  `REVISION_NOTES.md`.
- `AI_NAVIGATION.md`, `context-map.yaml`, `ARCHITECTURE.md`, `repomix.config.json` — routed for the new routing-eval surface.

### Notes

- Generated by `skill-ai-it` in `refresh` mode.
- The update package's base was the ORIGINAL `agent-stack.zip`, so it validated 10 files as diverged and refused to apply. Run with `--force` on explicit operator approval, taking the newer library
  content and re-applying the governance deltas on top. Update backups: `.agent-stack-update-backups/20260901_130323/`; pre-update copies of the five files I had modified:
  `/Volumes/Data/_ai/_skills/skills-working-cache/agent-stack/_pre-update-mine-20260901/`.
- The lesson above was promoted into the canonical skill: `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it` gained the implicit-resolution rule in `SKILL.md` (runtime isolation
  section, conventions, and quality checklist), in that skill's `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/templates/justfile` RUNTIME PINNING header, and as a new Tier 2
  `check_interpreter_pinning` in its `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/templates/check_governance.py`, so every future bootstrapped project inherits the rule.
  Both template paths are relative to the skill package directory named above, not to this repo.
- Verified: `just preflight` green — interpreter resolving to the working-cache venv (3.14.5), contract validation PASS (52 capabilities; 15 personas; 37 skills), 334 governance checks PASS, routing
  corpus PASS (60 cases), 37 unit tests PASS. The suite grew from 32 to 37 with the update's routing-behaviour tests. <!-- count:asat -->

