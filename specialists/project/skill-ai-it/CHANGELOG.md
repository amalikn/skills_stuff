# Changelog — skill-ai-it

## Contents

- [20260828_2104](#20260828_2104)
- [20260825_2150](#20260825_2150)
- [20260825_2030](#20260825_2030)
- [20260811_0914 — fix: refresh now invokes the deterministic upgrade; nav-script path bug corrected](#20260811_0914-fix-refresh-now-invokes-the-deterministic-upgrade-nav-script-path-bug-corrected)
- [20260811_0859 — fix: Claude install converted from copy to symlink](#20260811_0859-fix-claude-install-converted-from-copy-to-symlink)
- [20260811_0855 — fix: coherence sweep for the governance-checks capability + version bump](#20260811_0855-fix-coherence-sweep-for-the-governance-checks-capability-version-bump)
- [20260811_0838 — feat: governance coherence checker as a standard capability](#20260811_0838-feat-governance-coherence-checker-as-a-standard-capability)
- [20260529_0426 — fix: coherence sweep — SCRATCHPAD, AI_NAVIGATION duplicate, README layout, context-map routing gap](#20260529_0426-fix-coherence-sweep-scratchpad-ai_navigation-duplicate-readme-layout-context-map-routing-gap)
- [20260529_0142 — feat: Watchman filesystem event monitoring](#20260529_0142-feat-watchman-filesystem-event-monitoring)
- [20260523_1045 — fix: Archcore candidate report completion gate](#20260523_1045-fix-archcore-candidate-report-completion-gate)
- [20260523_0000 — feat: Archcore promotion candidate reporting](#20260523_0000-feat-archcore-promotion-candidate-reporting)
- [20260522_1755 — fix: embedded justfile fallback + deploy templates/ and patterns/ to installed copy](#20260522_1755-fix-embedded-justfile-fallback-deploy-templates-and-patterns-to-installed-copy)
- [20260522_1807 — feat: markdown quality rules enforced during file creation/update](#20260522_1807-feat-markdown-quality-rules-enforced-during-file-creationupdate)
- [20260522_1900 — remove: mise removed from skill entirely](#20260522_1900-remove-mise-removed-from-skill-entirely)
- [20260522_1800 — refactor: just-preferred task-runner strategy replaces mise-first](#20260522_1800-refactor-just-preferred-task-runner-strategy-replaces-mise-first)
- [20260522_1700 — fix: scripts/README.md update obligation added to navigation block](#20260522_1700-fix-scriptsreadmemd-update-obligation-added-to-navigation-block)
- [20260522_1643 — fix: scripts/README.md creation in refresh mode](#20260522_1643-fix-scriptsreadmemd-creation-in-refresh-mode)
- [20260522_1434 — full coherence sweep](#20260522_1434-full-coherence-sweep)
- [20260522_1432 — ARCHITECTURE.md tool-stack update for active CLI roles](#20260522_1432-architecturemd-tool-stack-update-for-active-cli-roles)
- [20260522_1431 — tool-stack auto-invocation policy](#20260522_1431-tool-stack-auto-invocation-policy)
- [20260522_1417 — coherence cleanup](#20260522_1417-coherence-cleanup)
- [20260522_1253 — script and task inventory capability](#20260522_1253-script-and-task-inventory-capability)
- [20260522_1246 — tool-stack architecture documentation](#20260522_1246-tool-stack-architecture-documentation)
- [20260522_1234 — Archcore initialization in main workflow](#20260522_1234-archcore-initialization-in-main-workflow)
- [20260522_1200 — Archcore preflight auto-init](#20260522_1200-archcore-preflight-auto-init)
- [20260522_1147 — local preflight opt-in policy](#20260522_1147-local-preflight-opt-in-policy)
- [20260522_1100 — preflight template CLI compatibility](#20260522_1100-preflight-template-cli-compatibility)
- [20260522_1045 — package coherence pass](#20260522_1045-package-coherence-pass)
- [20260522_0930 — CHANGELOG governance integration](#20260522_0930-changelog-governance-integration)
- [20260522_0900 — initial navigation module](#20260522_0900-initial-navigation-module)
- [20260529 — feat: AI navigation control-layer upgrade](#20260529-feat-ai-navigation-control-layer-upgrade)
- [20260529_HHMM — deterministic navigation-control automation](#20260529_hhmm-deterministic-navigation-control-automation)
- [20260812_1300](#20260812_1300)

---

## 20260828_2104

### Added

- **Two check families promoted upstream from a governed project, taking the template from five families to seven.** Both were authored in one project's checker on 2026-08-28 after the defect they
  catch had already been paid for once, and both are generic — nothing about either is specific to the project that found them.
  - **Family 6, table grain (`check_append_only_grain`).** An append-only table records a re-measurement by ADDING a row, which preserves the earlier measurement and is the right design. It is also
    useless on its own: without a column that ORDERS the passes, nothing can compute which row is current, and every aggregate over the table double-counts whatever was re-measured. Found with twelve
    rows standing for eight entities, the supersession recorded only in a prose note. Two assertions — every row stamps its pass, and no pass records the same entity twice. Registered per project in
    `APPEND_ONLY_TABLES` as `path -> (entity column, pass column)`.
  - **Family 7, evidence provenance (`check_evidence_provenance`).** The existence of a capture FILE is not evidence; it proves somebody wrote something down. Found backing a `VERIFIED` cost row whose
    only recorded fetch had returned HTTP 403 — invisible precisely because the file existed and read plausibly. Requires a `Canonical URL`, `Retrieved` and `HTTP status` header on every markdown
    capture under `EVIDENCE_DIR`. Pairs with a **corrections registry**, not an ignore-list: a capture predating the rule is accepted only while it names the later capture supplying its provenance AND
    that capture is on disk, so where captures are immutable the only way to clear an entry is to take the correcting capture. Removing an entry whose correction does not exist turns the check red —
    the registry cannot be emptied by deletion, only by doing the work.
- Both registries ship commented-out and contribute **zero assertions** when unset, so a project that has neither artifact reads honestly as "not covered yet" rather than as a pass.
- Added a `table_rows()` harness helper (stdlib `csv`, absent file returns an empty list) and updated `patterns/governance-checks.md`, the inference table, the maintenance-trigger table, `SKILL.md`
  and `templates/AGENTS-governance-checks-block.md` to describe seven families rather than five.
- Verified against the originating project: the ported checks reproduce its result exactly (81 assertions, zero failures) and both fail when the registry is deliberately mis-registered.

## 20260825_2150

### Fixed

- **Four defects ported into `templates/check_governance.py`.** They were found by using a generated checker rather than reading it, fixed in one project's copy, and would otherwise have been
  inherited by every project bootstrapped from the template:
  - **Path resolution ignored the referencing file's directory.** References resolved only against the repo root, so every correct relative link written inside a subfolder README false-failed —
    `scripts/README.md` naming `../AGENTS.md` or `check_governance.py` both reported as missing. Now resolves against the referencing file first, then the root.
  - **The recipe regex rejected variadic `just` recipes.** `^([a-zA-Z][\w-]*)\s*(?:[a-zA-Z_].*)?:(?!=)` cannot match `query *ARGS:` — the optional parameter group requires `[a-zA-Z_]` and meets `*` —
    so real recipes were reported as undefined. Widened to `[*+a-zA-Z_]`.
  - **Self-exclusion compared a repo-relative path against a bare filename.** `rel == Path(__file__).name` never matched, so the checker scanned its own `CONSTANT_SURFACES` pattern definitions and
    flagged every registered constant as an unregistered restatement. Now compares against a module-level `SELF`.
  - **Illustrative filenames were read as real references.** A naming-convention table's Example column failed path resolution. Added `EXAMPLE_MARKER` (`path:example`), per line and visible in the
    document, following the template's own `count:asat` precedent.
- Added a `CONDITIONAL_PATHS` registry (commented, tune per project) for artefacts a governance surface references *conditionally* — the generic navigation block names `Taskfile.yml`, `package.json`,
  `graphify-out/*`, `.ai-context/*` and `memory-bank/*`, none of which exist in every project. Registered with a per-entry reason rather than silently ignore-listed, so the exemption stays reviewable.
- Verified against a scratch fixture exercising all four: clean at baseline, and each still fails when deliberately broken.

### Changed

- **`promote` now deletes `ARCHCORE_PROMOTION_CANDIDATES.md` and writes `.archcore/README.md` as the durable index.** The candidates file is a proposal queue that exists between the run surfacing
  candidates and the run promoting them. Keeping it afterwards produces a stale second index under a name that misdescribes its contents — and it lives at the repo root, which `bootstrap` and
  `refresh` both rewrite, so anything durable recorded there is destroyed by the next skill invocation without trace. Observed 2026-08-25 on a real project.
- The *never promote* reasoning is carried out of the candidates file into `.archcore/README.md` before deletion. Without it, the next scan re-proposes the same rejected candidates every refresh.
- The orphan check points at `.archcore/README.md`; the candidates filename is registered in `CONDITIONAL_PATHS` so historical mentions in `CHANGELOG.md` do not fail path resolution once the file is
  gone. History is not a live claim.
- Quality checklist and `patterns/archcore-routing.md` updated to match.

## 20260825_2030

### Fixed

- **Generated justfiles called bare `python3`, so every project bootstrapped from this skill silently used the host interpreter rather than its own `.mise.toml` pin.** Found 2026-08-25 in a project
  that pinned Python 3.14 and Node 26 while its recipes ran Homebrew's 3.14.7 and Node 26.7.0. The defect is dangerous precisely because it works: it passes every check on the machine it was written
  on and fails later, inside a script, looking like a code bug.
- `templates/justfile` now declares `wc` / `py` / `nd` interpreter variables, routes every recipe through them, and ships `bootstrap`, `runtimes` and a `_require-venv` guard. The embedded fallback
  justfile in `SKILL.md` carried the same defect and was fixed with it.
- `templates/scripts-README.md` gained a Runtimes section, so a project's script catalog states what its recipes actually use.
- `bootstrap` now installs `requirements.txt` when one exists. Pinning the interpreter without declaring packages relocates the hidden host dependency rather than removing it: the moment the affected
  project switched off the host interpreter, `just nav-validate` failed on a PyYAML that Homebrew's Python had been supplying invisibly all session, and which nothing had ever declared.

### Added

- `SKILL.md` — **Runtime isolation** section under *Script and task inventory*: the three artefacts that must be generated together, the working-cache peer path mapping for each source root, why `uv
  run` is not the primary path (it resolves its own interpreter independently of mise), and why no `.python-version` accompanies `.mise.toml`.
- Quality checklist gained a blocking item: no generated recipe may call a bare interpreter, and `just runtimes` must be **executed** and its output reported — the same "prove it can fail" discipline
  the governance checker already carries.
- Phase 3 inference table gained a *Runtime requirements* row, so the interpreters a project invokes are inferred rather than assumed.

### Notes

- `runtimes` exists to make the invariant observable. Without it, "the recipes use the pinned runtime" is an assumption nobody can check quickly — the same reason the governance checker prints its
  assertion count.

## 20260811_0914 — fix: refresh now invokes the deterministic upgrade; nav-script path bug corrected

Prompted by the operator asking why upgrading a project was two manual steps when `refresh` should cover it. It should — SKILL.md already said "Scripts are the **primary mechanism** for
existing-project upgrade" — but three defects made that instruction unusable in practice.

**1. The documented commands could not work.** The sequence read `python scripts/upgrade_navigation_control_layer.py --project-root .`, which implies running from inside the target project. The
scripts live in the SKILL PACKAGE; target projects carry no copies. An agent following it literally in a target gets "can't open file". Rewritten to an explicit `SKILL_DIR` / `TARGET` form with
absolute invocation, and the "these do not live in your project" fact stated outright rather than left to inference.

**2. The section was orphaned.** Its only inbound reference was the TOC. Nothing in Operating Modes or Phase 4 pointed at it, and it sits at line ~1611 of ~1730 — after the Quality Check, where an
agent running `refresh` plausibly never reaches. The `refresh` and `navigation-add` mode rows now state the sequence runs FIRST and link to it.

**3. It predated the governance checker.** The sequence ended at "agent fixes remaining failures". Added step 6 (create or extend `scripts/check_governance.py` — flagged as judgement, not mechanics,
since Tier 3 invariants must be read out of the target's own rules) and step 7 (regenerate `.ai-context/governance-pack.md`, which embeds copies of the managed blocks and otherwise keeps serving the
pre-upgrade version to agents).

**Same path bug in `templates/justfile`, and worse there** — it ships into target projects, so every project bootstrapped from it received four `nav-*` recipes that fail on invocation. Now defined
against a `skill_dir := "..."` variable, overridable per call (`just skill_dir=/path nav-validate`). Verified: `just --list` parses and `just --evaluate skill_dir` resolves.

Also fixed a cosmetic defect introduced at `20260811_0838`: the `check` recipe's two-line comment meant `just --list` advertised "Must exit 0 before durable work is called complete" as the recipe's
description, because just takes the LAST comment line. Lines reordered so the summary is what shows.

**Net effect:** `/skill-ai-it refresh <project>` is now one command that upgrades managed blocks, restamps the version, adds missing context-map keys, adopts the governance checker, and regenerates
the context pack — rather than a prose instruction pointing at commands that fail.

## 20260811_0859 — fix: Claude install converted from copy to symlink

`~/.claude/skills/skill-ai-it` is now a symlink to canonical, matching `~/.agents/skills/skill-ai-it`. The copy-drift class is closed for this skill: there is no longer anything to sync and nothing
that can silently fall behind.

**The recorded blocker did not exist.** The `20260811_0855` entry named `governance/watchman-events/` runtime state inside the install as the reason the swap was blocked. That was asserted from the
directory's presence without opening it. On inspection it holds a single `.gitkeep` and no event files, in both the install and canonical, and `watchman watch-list` shows watchman watching canonical
only — never the install path. Nothing needed relocating.

Worth recording as a pattern rather than a one-off: the blocker was stated confidently, written into three governance surfaces and two memory backends, and survived a coherence sweep — because a sweep
verifies that claims are *consistent across surfaces*, not that they are *true*. Consistency propagates a wrong fact perfectly. The check that would have caught it was one `find` on the directory, run
before the claim rather than after it.

**Procedure used:** confirmed the trees were byte-identical apart from canonical-only extras (`.DS_Store`, `.remember/`, `docs/`), moved the copy to a session-scratchpad backup rather than deleting
it, created the symlink, then verified the link target resolves, `SKILL.md` reads through it at full length, and both `templates/` and `patterns/` enumerate completely.

**Files updated:** `SCRATCHPAD.md` (item ticked, blocker correction recorded), `ROADMAP.md` ("Sync installed copy" marked obsolete with its reason retained), `CHANGELOG.md` (this entry, plus a
forward-pointer added to the superseded clause in `20260811_0855`).

**Also corrected:** the `20260811_0855` entry was originally stamped `20260811_0912` — a timestamp 13 minutes in the future at the time of writing. Fixed to its actual write time rather than left to
stand as a fabricated value in a durable record.

## 20260811_0855 — fix: coherence sweep for the governance-checks capability + version bump

Coherence sweep following the capability added at 20260811_0838. The feature commit updated the package's documentation surfaces; this sweep found what documentation alone could not reach.

**The generator was still emitting the old model.** `scripts/upgrade_navigation_control_layer.py` embeds the managed blocks it writes into target projects as Python string literals. Documenting the
new capability in `SKILL.md` did nothing for any project upgraded by that script — it would have kept emitting navigation guidance with no mention of the checker, indefinitely. This is the failure
class `patterns/generator-and-derived-artifact-tracing` exists for, and a phrase-grep could not have found it: there was no stale string, only a missing one.

**Per-script findings (Tier 1):**
- `upgrade_navigation_control_layer.py` — emitted AI_NAVIGATION block gained a `## Governance coherence checks` section and a `scripts/check_governance.py` context-file row; emitted AGENTS block
  gained item 14; companion table gained the checker as a companion of "New script added" plus a new "New artifact class" row
- `validate_navigation_control_layer.py` — new `validate_governance_checker()` reports present / wired into a runner / referenced from `AGENTS.md`. Deliberately `warn`, never `fail`: the checker is a
  capability projects adopt at refresh, not a precondition of the control layer, and failing on it would mark every project bootstrapped before the capability existed as broken. A checker that is
  present but unwired *is* flagged
- `check_expected_diff.py` — `scripts/check_governance.py` added to `DEFAULT_EXPECTED` so a project gaining one during an upgrade does not read as an UNEXPECTED change

**Version bump — `2026-05-29-ai-navigation-control-layer-v1` → `2026-08-11-governance-checks-layer-v1`.** The emitted block content changed, so the stamp had to. Leaving two different block contents
under one stamp is the silent-drift anti-pattern the new pattern file documents. Synced across 11 surfaces (both scripts, four templates, `SKILL.md` ×3, `AGENTS.md`, `AI_NAVIGATION.md`,
`context-map.yaml`, `patterns/script-task-audit-checklist.md`). The historical stamp in this CHANGELOG was left alone — it is a record, not a claim.

**Consequence, stated plainly:** three projects still carry the previous stamp and will report "missing current version stamp" under `just nav-validate` until re-upgraded — `me/llm-m2max`,
`apn/vocus-profitability`, `apn/opticomm-profitability`. That report is the intended re-upgrade signal, not a project defect. Remediation is one `just nav-upgrade` each.

**Adoption gap closed.** The operator asked whether re-running the skill on an existing project would add a checker. It would not have: the `refresh` row read "extend registries for new artifacts",
which is a no-op when no checker exists. `refresh` is now explicitly the adoption path for projects predating the capability, and is expected to produce more than the bootstrap baseline because a
mature project has accumulated more invariants than it had at setup.

**Also updated:** `templates/update_rules.yaml` and `templates/context-map.yaml` (checker as a companion; new `new_artifact_class` rule), `templates/AI_NAVIGATION.md` and
`templates/AGENTS-navigation-block.md` (governance-checks guidance), `templates/scripts-README.md` (`just check` catalog row), `patterns/navigation-control-automation.md` (relationship to
`patterns/governance-checks.md`; version-stamp and re-upgrade semantics), package `AGENTS.md` (template-follows-doctrine rule; VERSION restatement rule), `SCRATCHPAD.md`, `ROADMAP.md`.

**Stale next-action corrected:** SCRATCHPAD carried a "MANUAL: sync installed copy — blocked by permission gate" action from May 29. The sync was performed this session; the entry now records the
durable fix (symlink the install) and what was believed to be its blocker. That blocker was disproved minutes later — see `20260811_0859`.

## 20260811_0838 — feat: governance coherence checker as a standard capability

Generalized from the `jdm` project, whose hand-built `scripts/check_governance.py` had grown to 10 check groups and 521 assertions and had repeatedly caught defects that prose review did not — stale
paths, count claims contradicted by the filesystem, a derived parquet built from a superseded snapshot, and a threshold restated across 14 surfaces that drifted in one.

Every governed project now gets `scripts/check_governance.py`: a stdlib-only script that turns the project's governance **claims** into assertions that fail, gated by the task runner.

**Architecture decision — self-contained per project.** The checker is copied and tuned, not imported from a shared package. Universal-check fixes must be re-propagated, which is the accepted cost; in
exchange no project gains a runtime dependency, custom checks need no escape hatches, and a defect in one project's checker cannot break every other project's gate.

**Enforcement decision — the checker polices its own coverage.** The "keep it fine-tuned as files are added" obligation is enforced by the artifact, not by prose an agent may skip. Coverage checks run
in **both** directions: a catalog naming a file that vanished, and a file that exists which no catalog names. Only the second grows silently, and it is the one that makes the checker self-extending —
a new file turns the build red until it is registered, so extending the checker becomes a blocking condition rather than a good intention.

**Files added:**
- `patterns/governance-checks.md` — doctrine: the harness contract, the three-tier model, the five check families (count-claim, link/path resolution, contract conformance, derived-artifact staleness,
  duplicated-fact sync), coverage self-policing, the artifact-to-check inference table, maintenance triggers, sizing guidance, and anti-patterns
- `templates/check_governance.py` — stdlib-only checker template. CONFIG registries the agent tunes per project; Tier 1 universal checks implemented generically; Tier 2/3 regions marked. Verified
  against a synthetic project: 5 failures across 5 families, then clean green with no false positives
- `templates/AGENTS-governance-checks-block.md` — managed AGENTS block carrying the maintenance-trigger table and the four non-negotiables, so the obligation lives where the working agent reads it

**Files updated:**
- `SKILL.md` — package layout; Phase 3 gains a "Coherence invariants" inference row; Phase 4 file-policy table gains a `scripts/check_governance.py` row; new `### Governance coherence checker` section
  (tiers, self-policing, mode behavior, non-negotiables); embedded justfile fallback gains a `check` recipe; AGENTS.md template references the new managed block; six items added to the quality
  checklist, including that the checker must be **executed** and its exit status reported
- `templates/justfile` — `check` recipe added; `preflight` now depends on it
- `README.md`, `ARCHITECTURE.md`, `AI_NAVIGATION.md`, `context-map.yaml` — new template/pattern files registered; ARCHITECTURE distinguishes this layer from `patterns/drift-audit.md` (a checklist the
  agent runs) as a gate the project runs
- `CHANGELOG.md` — this entry

**Deliberately not done:** no checker was generated into any existing project by this change. Rollout is per project via `/skill-ai-it refresh`, starting from Tier 1 only.

## 20260529_0426 — fix: coherence sweep — SCRATCHPAD, AI_NAVIGATION duplicate, README layout, context-map routing gap

Post-watchman coherence sweep triggered by `/project coherence`.

**Files updated:**
- `SCRATCHPAD.md` — current state updated to reflect watchman integration; May 29 session history added
- `AI_NAVIGATION.md` — removed duplicate `templates/justfile` row; added `patterns/navigation-control-automation.md` and `templates/update_rules.yaml` to context map table
- `README.md` — package layout updated to include `.watchmanconfig`, `governance/watchman-events/`, `patterns/navigation-control-automation.md`, `templates/update_rules.yaml`
- `CHANGELOG.md` — this entry

**Installed copy sync:** Blocked by session permission gate. Manual action required: sync all differing files and add `patterns/navigation-control-automation.md` and `templates/update_rules.yaml` to
`~/.claude/skills/skill-ai-it/`.

**Also noted:** Installed copy has old managed-block format (`<!-- BEGIN skill-ai-it:navigation -->` without MANAGED: prefix and version string). Requires upgrade pass.

## 20260529_0142 — feat: Watchman filesystem event monitoring

Added Watchman filesystem event monitoring support to the skill-ai-it package.

**Files added:**
- `.watchmanconfig` — settle 100ms, ignores `.git`, `graphify-out`, `.ai-context`
- `governance/watchman-events/.gitkeep` — event log directory for historical context recovery

**Files updated:**
- `context-map.yaml` — added `governance/watchman-events` to `authority_order`; added `historical_context_recovery` routing section
- `AGENTS.md` — added "Historical context recovery" section with 4-step evidence source priority
- `AI_NAVIGATION.md` — added `governance/watchman-events/` and `.watchmanconfig` to context map table; added "Historical context recovery" section with watchman query command

**Why:** Global AGENTS.md policy (evidence source #6) specifies watchman event logs as a fallback when memory backends lack session detail. Wiring this package into that recovery chain closes a gap
identified in the AI navigation control-layer audit.

**Watchman root registered:** `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it`

## 20260523_1045 — fix: Archcore candidate report completion gate

Converted Archcore promotion candidate reporting from workflow guidance into an explicit completion gate. Future `bootstrap`, `navigation-add`, and `refresh` runs with `.archcore/` present must verify
`ARCHCORE_PROMOTION_CANDIDATES.md`, read or section-check it before final response, and confirm that no `.archcore/adr/`, `.archcore/rules/`, `.archcore/specs/`, `.archcore/guides/`, or
`.archcore/plans/` content files were created outside `promote` mode.

Also updated the Repomix template to include `ARCHCORE_PROMOTION_CANDIDATES.md` by default so the candidate report is present in generated governance context.

### Files changed

- `SKILL.md` — quality checklist now requires Archcore candidate report verification and promotion-safety checks
- `patterns/archcore-routing.md` — added completion gate for candidate report and no-promotion validation
- `templates/repomix.config.json` — includes `ARCHCORE_PROMOTION_CANDIDATES.md`

## 20260523_0000 — feat: Archcore promotion candidate reporting

Added Archcore promotion candidate reporting to `bootstrap` and `refresh` modes. After `archcore init`, the skill inspects governance files and emits `ARCHCORE_PROMOTION_CANDIDATES.md` — a grouped,
sourced list of durable content candidates (adr, rules, specs, guides, plans). No `.archcore/` content files are written during bootstrap or refresh. Only `promote` mode creates `.archcore/` content
(direct user instruction also triggers promote).

**Extraction heuristics added to `patterns/archcore-routing.md`:** two-part test (durability signal + normative language); category-specific rules for adr/rules/specs/guides/plans; exclusion list
(TODOs, session notes, unmarked SCRATCHPAD, CHANGELOG as direct source, generated files, inherited parent rules, stale roadmap items).

**Design basis:** dual Codex consultation (2026-05-22) via codex-bridge MCP. See [`docs/fix-archcore-bootstrap-seeding-20260522_2331.md`](fix-archcore-bootstrap-seeding-20260522_2331.md).

### Files changed

- `patterns/archcore-routing.md` — full replacement with core principle, extraction heuristics, exclusion table, candidate report format
- `SKILL.md` — Archcore init section expanded with promotion candidate reporting subsection; promote mode row updated
- `templates/AI_NAVIGATION.md` — `ARCHCORE_PROMOTION_CANDIDATES.md` row added to project context files table
- `AI_NAVIGATION.md` — row added to context map table; heuristic validation note added to Archcore routing block
- `README.md` — promote mode description updated; Archcore tool-stack bullet updated
- `ARCHITECTURE.md` — Archcore section updated with two-phase description; flow diagram updated
- `context-map.yaml` — `generated_output` key added under `guidance_patterns`
- `templates/context-map.yaml` — `ARCHCORE_PROMOTION_CANDIDATES.md` added to `authority_order`, `planning.read`, and `governance.read`

## 20260522_1755 — fix: embedded justfile fallback + deploy templates/ and patterns/ to installed copy

### Fixed

- `SKILL.md` — added `#### justfile — embedded fallback` block after "Task safety labels" section. Provides a 4-task minimal justfile (`default`, `audit-scripts`, `preflight`, `lint-md`) when
  `templates/justfile` is unavailable. Mirrors the existing embedded-fallback pattern already used for `context-preflight.sh` and `scripts/README.md`.

### Deployed

- `~/.claude/skills/skill-ai-it/templates/` — synced all 7 template files from canonical source. Previously the installed copy only contained `SKILL.md`; templates/ was never deployed.
- `~/.claude/skills/skill-ai-it/patterns/` — synced all 4 pattern files from canonical source.

### Root cause

During `/skill-ai-it bootstrap` on `invoice-finance-analyst`, the justfile was skipped on first pass. Investigation showed the installed skill (`~/.claude/skills/skill-ai-it/`) contained only
`SKILL.md` with no `templates/` or `patterns/` subdirectories. The skill tried to use `templates/justfile`, found it absent, had no embedded fallback to fall back to, and silently skipped the step.
The canonical source always had `templates/justfile`; it was a deploy omission.

---

## 20260522_1807 — feat: markdown quality rules enforced during file creation/update

Added "Markdown quality rules" section to Phase 4 of SKILL.md. Rules applied to every `.md` file created or updated by this skill:

- Naming: time-bound files use `<slug>-YYYYMMDD_hhmm.md`; stable entrypoints unchanged; metadata timestamps use `YYYYMMDD_hhmm`
- TOC: required for files over 100 lines; `## Contents` heading; placed immediately after main `#` heading; updated in same pass when editing
- Links: references in README/index files must be markdown links; metadata fields naming files render as links
- Quality pass: fix malformed lists and stale headings in same pass

Authority: [`/Volumes/Data/_ai/governance/categories/markdown-guide.md`](/Volumes/Data/_ai/governance/categories/markdown-guide.md)

---

## 20260522_1900 — remove: mise removed from skill entirely

### Removed

- **`templates/mise.toml`** — deleted. Skill no longer ships or generates mise files.
- All mise references removed from: `SKILL.md`, `README.md`, `ARCHITECTURE.md`, `AGENTS.md`, `AI_NAVIGATION.md`, `context-map.yaml`, `templates/AI_NAVIGATION.md`, `templates/context-map.yaml`,
  `templates/AGENTS-navigation-block.md`, `templates/scripts-README.md`, `templates/context-preflight.sh`, `templates/repomix.config.json`, `patterns/script-task-audit-checklist.md`.
- mise initialization section removed from `SKILL.md`.
- mise step [5/6] removed from `templates/context-preflight.sh`; steps renumbered to [1/5]–[5/5].
- mise from Phase 1 inventory table, Phase 4 file creation table, detection order, mode behaviors.

### Why

mise is no longer a concept this skill knows about. `just` is the task runner. Target projects that use other runners (Taskfile.yml, Makefile, package.json) are still detected and respected. The skill
does not generate, detect, or route through mise in any form.

---

## 20260522_1800 — refactor: just-preferred task-runner strategy replaces mise-first

### Changed

- **`templates/justfile`** — new file added to templates/. Lightweight task catalog with `inventory`, `audit-scripts`, `preflight`, and `lint-md` recipes. Used when no existing task runner is present
  and the project does not require mise's env/version features.
- **`templates/mise.toml`** — demoted to optional env/tool-version template. Added header comments making role explicit: "prefer justfile → scripts/README.md → mise.toml".
- **`templates/scripts-README.md`** — execution policy rewritten. Preferred order: existing canonical runner → `just` → `scripts/README.md` → other runners → raw scripts. Task inventory examples
  changed to `just inventory` / `just audit-scripts`.
- **`templates/AGENTS-navigation-block.md`** — rule 9 updated: justfile first in inspect order, `just` preferred, mise only when project uses mise, mise not default task runner.
- **`templates/repomix.config.json`** — added `"Justfile"` (capital J) to include list alongside `"justfile"`.
- **`templates/AI_NAVIGATION.md`** — Script and Task Navigation section rewritten: justfile first in 8-item read order, just-preferred execution guidance.
- **`templates/context-map.yaml`** — scripts and automation routing: justfile first, updated rules (respect canonical runner, prefer justfile for new catalogs, mise only when already present).
- **`AI_NAVIGATION.md`** (package-level) — Script and Task Navigation: same just-preferred order. Context map table: added `templates/justfile` row; updated `templates/mise.toml` description.
- **`context-map.yaml`** (package-level) — scripts/automation routing: justfile first, updated rules. `generated_templates` routing: added `templates/justfile`.
- **`SKILL.md`** — Phase 1 inventory table: added `justfile`/`Justfile` row, updated `mise.toml` row description. Phase 4 file creation table: added `justfile` row (bootstrap only), updated
  `mise.toml` row to "create only when explicitly requested or tool/env management clearly needed". Detection order rewritten (8 items, justfile first). Bootstrap mode: prefer justfile for new
  catalogs, mise only when explicitly needed. Navigation-add mode: route to existing runner first. Refresh mode: respect existing runner, don't silently convert.
- **`README.md`** — Key rules: mise-first wording replaced with just-preferred. Package layout: added `templates/justfile`. Tool stack section: "mise tasks" entry replaced with "just / task runners"
  entry plus separate "mise (env/version management)" entry. Authority order updated.
- **`ARCHITECTURE.md`** — Flow diagram: script/task inventory layer updated. Source-of-truth direction diagram updated. Script and Task Inventory Layer section rewritten: justfile as preferred,
  existing runner priority, mise as env/version tool, agent preference order documented.
- **`AGENTS.md`** (package-level) — task catalog inspect order updated: justfile first. just-preferred and mise-optional rules added.

### Why

The previous strategy made mise the canonical runnable task catalog by default. This was heavier than necessary for projects that do not need mise's env/version management features. `just` is simpler,
widely available, and better suited for lightweight project task catalogs. The refactor makes just the preferred new-project default while preserving full mise support for projects that already use
it.

### Constraints honored

- mise support not removed.
- just not made mandatory — existing canonical runners always take priority.
- No existing project task runners silently converted.
- Archcore, Graphify, and Repomix behavior unchanged.
- Repeat-safety contract intact.
- Spec source: `docs/replace-mise-with-just-20260522_1652.md`.

---

## 20260522_1700 — fix: scripts/README.md update obligation added to navigation block

### Fixed

- `templates/AGENTS-navigation-block.md`: added rule 12 — "When adding, modifying, or removing scripts or tasks, update `scripts/README.md` to reflect the change — purpose, inputs, outputs, safety
  label, and idempotency."
- `SKILL.md` embedded AGENTS.md fallback: same rule 12 added.

### Why

Rule 11 ("identify which governance files must be updated") was too vague to reliably trigger `scripts/README.md` maintenance when scripts change. Without an explicit rule, agents would create/modify
scripts without updating the catalog, causing silent drift. Rule 12 makes the update obligation specific and actionable. This closes the write-side of the circular dependency: rule 9 covers reading
before running; rule 12 covers writing after changing.

### Also

- `openbb/AGENTS.md` managed block: rule 12 propagated to the live target project.

## 20260522_1643 — fix: scripts/README.md creation in refresh mode

### Fixed

- `SKILL.md` file creation table: `Refresh` column for `scripts/README.md` changed from "update managed inventory blocks only" to "create from template if scripts/tasks exist and file missing; update
  managed blocks if exists". Previously, refresh mode would only update an existing file, never creating it — leaving a gap where script navigation rules pointed to a file that the refresh would not
  create.
- `SKILL.md` Script/task inventory mode behavior: `refresh` entry updated to match the file creation table fix.

### Why

AGENTS.md navigation block (rule 9) tells agents to inspect `scripts/README.md` when present, but refresh mode never created the file if it was missing. Any project that received the navigation block
via refresh but had no pre-existing `scripts/README.md` would have agents follow a pointer to a file that did not exist. Discovered when OpenBB received navigation rules but no `scripts/README.md` was
created.

## 20260522_1434 — full coherence sweep

### Changed

- `README.md`: added TOC (118 lines, governance compliance); updated tool stack from "three optional" to "four project-context tools"; updated Graphify and Repomix bullet descriptions to reflect
  active invocation.
- `ARCHITECTURE.md`: added TOC (134 lines, governance compliance).
- `SCRATCHPAD.md`: updated current state, open items, recent decisions, and session history to reflect all changes from this session.
- All coherence checks verified: SKILL.md three-section Phase 4, active tool invocation policy, preflight mise step, CHANGELOG TOC completeness, `.gitignore` hygiene, required files and terms present.

### Notes

- No content drift found in `AGENTS.md`, `AI_NAVIGATION.md`, `context-map.yaml`, `templates/AI_NAVIGATION.md`, or `templates/context-map.yaml` — those files were already coherent.
- `slurp-chat` skill not installed; session state captured manually in `SCRATCHPAD.md`.

## 20260522_1432 — ARCHITECTURE.md tool-stack update for active CLI roles

### Changed

- `ARCHITECTURE.md` Graphify section: updated from passive description to active required tool — `graphify update .` is invoked on every `bootstrap`, `navigation-add`, and `refresh` run; Graphify is
  now listed as required for full skill operation.
- `ARCHITECTURE.md` Repomix section: updated to reflect active invocation — runs `repomix --config repomix.config.json` on every active-mode run; creates config from template if missing.
- `ARCHITECTURE.md` flow diagram: renamed "Generated support layer" to "Active context generation (CLIs invoked when available)" showing `graphify update .` and `repomix --config` as explicit CLI
  steps; added `mise install + mise tasks` to the Script/task inventory layer.

### Notes

- These changes align `ARCHITECTURE.md` with the policy changes made in the tool-stack auto-invocation entry above.

## 20260522_1431 — tool-stack auto-invocation policy

### Changed

- `SKILL.md` Repeat-Safety Contract rule 9: updated to state that Graphify and Repomix are actively run when their CLIs are available; outputs remain disposable support, not canonical truth.
- `SKILL.md` file creation table: added `Graphify / graphify-out/` row (`run if CLI available` for bootstrap/navigation-add/refresh); updated `repomix.config.json` row (`initialize if CLI available`);
  updated `mise.toml` row (`initialize if CLI available and no task runner canonical`).
- `SKILL.md`: added `### Graphify initialization and refresh` section — run `graphify update .` on every active-mode run; initializes if `graphify-out/` missing.
- `SKILL.md`: added `### Repomix initialization and refresh` section — create config from template if missing, run on every active-mode run.
- `SKILL.md`: added `### mise initialization` section — create `mise.toml` from template during bootstrap if CLI available and no task runner canonical.
- `templates/context-preflight.sh`: added step `[5/6] Checking mise task catalog` — runs `mise install` and `mise tasks` if `mise.toml` or `.mise/tasks/` present; renumbered all steps from `/5` to
  `/6`.

### Notes

- Graphify refresh on every skill rerun was explicitly requested; previously Graphify was passive (generated-output-only policy).
- mise was the only tool-stack item absent from the preflight; now all four (Archcore, Graphify, Repomix, mise) are covered.

## 20260522_1417 — coherence cleanup

### Changed

- `SKILL.md` Phase 4: split `### Always-created files` into three clear sections: `### Always-created files` (README.md, AGENTS.md, CLAUDE.md, SCRATCHPAD.md, CHANGELOG.md), `### Conditionally-created
  files` (ARCHITECTURE.md, CONVENTIONS.md, ROADMAP.md, AI_NAVIGATION.md, context-map.yaml, repomix.config.json, .graphifyignore, memory-bank/, scripts/README.md, mise.toml), `### Optional/generated
  support files` (summary table of explicit-request-only and generated artifacts).
- `SKILL.md` Phase 4: added inline stubs for ARCHITECTURE.md, CONVENTIONS.md, ROADMAP.md, scripts/README.md, and mise.toml/.mise/tasks/ under Conditionally-created files.
- `README.md`: added `SCRATCHPAD.md` to package layout tree.
- `AI_NAVIGATION.md`: added `SCRATCHPAD.md` row (Low authority) to context map table.
- `SCRATCHPAD.md`: marked script inventory / `mise tasks` open item as resolved (implemented 2026-05-22).
- `templates/mise.toml`: updated Python version comment from `3.12` to `3.14`.
- Root hygiene: moved `codex_prompt_fix_skill_ai_it_changelog_governance.md` to `docs/archive/`.
- Root hygiene: confirmed `SKILL.md.bak` already removed from earlier session.
- Root hygiene: removed `.DS_Store` from package root.
- Added `.gitignore` with `.DS_Store`, `.remember/logs/`, `graphify-out/`, `.ai-context/` entries.

### Notes

- Generated by coherence cleanup pass following audit in `docs/review-coherence-audit-20260522_1401.md`.
- `templates/AI_NAVIGATION.md`, `templates/context-map.yaml`, `templates/AGENTS-navigation-block.md`, `context-map.yaml`, and `AI_NAVIGATION.md` were already correct and required no changes.
- Navigation and context-map surfaces were verified after the cleanup; only required drift fixes were applied.

## 20260522_1253 — script and task inventory capability

### Added

- Added optional script/task inventory capability using `mise.toml` and `.mise/tasks/` as the executable source of truth when present.
- Added `templates/scripts-README.md` as the human/agent-readable script inventory template.
- Added `templates/mise.toml` as the default optional task catalog template.
- Added `patterns/script-task-audit-checklist.md` for repeat-safe task/script inventory audits.
- Added script/task navigation and context-map routing for `mise`, task runners, raw scripts, and automation safety.

### Changed

- Updated README, ARCHITECTURE, SKILL orchestration, AGENTS guidance, navigation templates, context-map templates, and Repomix packing rules for scripts and automation.
- Clarified safety handling for uncataloged, destructive, review-required, and unknown-safety tasks.

## 20260522_1246 — tool-stack architecture documentation

### Added

- Added `ARCHITECTURE.md` to explain the skill package architecture and the roles of Archcore, Graphify, and Repomix.

### Changed

- Updated `README.md`, `SKILL.md`, `AI_NAVIGATION.md`, and `context-map.yaml` so `ARCHITECTURE.md` is part of the maintained package navigation surface.

## 20260522_1234 — Archcore initialization in main workflow

### Changed

- Moved Archcore initialization into the main `SKILL.md` workflow so rerunning the skill can create `.archcore/` when the `archcore` CLI is available.
- Updated the Archcore pattern and README to distinguish allowed `archcore init` setup from governed Archcore content edits.

### Notes

- `audit` mode remains read-only unless the user asks for changes; bootstrap, navigation-add, and refresh initialize Archcore when possible.

## 20260522_1200 — Archcore preflight auto-init

### Changed

- Updated the optional local preflight template and embedded fallback to run `archcore init` automatically when the Archcore CLI exists and `.archcore/` is missing.

### Notes

- Local preflight scripts remain explicit opt-in artifacts.

## 20260522_1147 — local preflight opt-in policy

### Changed

- Changed `scripts/context-preflight.sh` generation from default/useful behavior to explicit request only.
- Clarified that generic preflight behavior is maintained in `skill-ai-it`, not in repo-local generated scripts.
- Updated generated README pointers and quality checks so local preflight scripts do not become a second source of truth.

### Notes

- Existing project-local preflight scripts should be audited and proposed for update only when the operator asks to keep them.

## 20260522_1100 — preflight template CLI compatibility

### Changed

- Updated `templates/context-preflight.sh` and the embedded fallback to avoid treating missing `.archcore/` as a failed Archcore setup.
- Replaced stale `graphify .` guidance with `graphify update .` for the installed Graphify CLI.
- Clarified the reusable preflight behavior so generated project scripts remain local entrypoints while generic logic stays maintained in this skill package.

### Notes

- Project-specific generated scripts may still add local anchor checks or local command adaptations.

## 20260522_1045 — package coherence pass

### Changed

- Aligned external managed-block markers with the documented `<!-- BEGIN skill-ai-it:navigation -->` / `<!-- END skill-ai-it:navigation -->` convention.
- Updated context preflight fallback and template checks to include `CHANGELOG.md`.
- Reconciled package templates and embedded fallback content for governance/navigation consistency.

### Notes

- `SKILL.md.bak` was intentionally ignored during this pass.

## 20260522_0930 — CHANGELOG governance integration

### Changed

- Promoted `CHANGELOG.md` to a first-class governance file for both the skill package and generated project governance.
- Updated `SKILL.md`, package governance files, templates, and drift-audit pattern to route, read, and update `CHANGELOG.md`.
- Fixed the `SKILL.md` SCRATCHPAD/CHANGELOG section ordering so each governance file has its own valid section.

### Notes

- `CHANGELOG.md` is now treated as a durable package/project history ledger and should be appended on meaningful bootstrap, navigation-add, refresh, audit, or promote runs.

## 20260522_0900 — initial navigation module

### Added

- AI navigation/context-routing module.
- Repeat-safe operating modes:
  - `bootstrap`
  - `navigation-add`
  - `refresh`
  - `audit`
  - `promote`
- External template package:
  - `templates/AI_NAVIGATION.md`
  - `templates/context-map.yaml`
  - `templates/repomix.config.json`
  - `templates/AGENTS-navigation-block.md`
  - `templates/context-preflight.sh`
- External pattern package:
  - `patterns/archcore-routing.md`
  - `patterns/memory-bank-structure.md`
  - `patterns/drift-audit.md`
- Skill package governance files:
  - `README.md`
  - `AGENTS.md`
  - `CLAUDE.md`
  - `AI_NAVIGATION.md`
  - `context-map.yaml`

### Changed

- Expanded skill from initial bootstrap only to repeat-safe governance/navigation maintenance.
- Added template precedence and fallback rules.
- Restored conditional templates for:
  - `ARCHITECTURE.md`
  - `CONVENTIONS.md`
  - `ROADMAP.md`

---

## 20260529 — feat: AI navigation control-layer upgrade

### Added

- **Context compaction recovery** — step-by-step procedure added to SKILL.md, AI_NAVIGATION.md (package and template), README.md, and ARCHITECTURE.md. Agents now have explicit instructions for
  rebuilding context after compaction.
- **context-map.yaml schema fields** — `audit_checks`, `promotion_rules`, and `context_recovery` added to both package and template context-map.yaml. Covers governance file presence, version
  consistency, companion update completeness, generated-output policy, task-runner consistency, stale reference detection, archcore promotion gates, and post-compaction recovery.
- **Drift audit expansion** — `patterns/drift-audit.md` rewritten from 11 shallow checkpoints to 13 comprehensive sections covering: governance file presence, managed block integrity, version
  consistency, navigation map completeness, authority consistency, companion update verification, generated-output policy enforcement, archcore promotion gate verification, context compaction
  recovery, script/task consistency, stale reference detection, repeat-run safety, and AI_NAVIGATION.md vs context-map.yaml cross-reference.
- **Four-capabilities documentation** — README.md and ARCHITECTURE.md now document the four first-class capabilities: AI navigation map, file relationship/dependency logic, agent coherence/compliance
  checks, and structured machine-readable context.
- **Existing-project upgrade behavior** — detection matrix documented in README.md and ARCHITECTURE.md: file missing, exists with current/older/no managed block, user-authored content, conflicting
  manual content, older schema.
- **scripts/README.md freshness check** — added step 5 to `templates/context-preflight.sh`.

### Changed

- **Managed block standard** — all managed blocks updated from `<!-- BEGIN skill-ait:navigation -->` to `<!-- BEGIN MANAGED: skill-ai-it:<section-name> -->` with version stamping. Format: `<!--
  skill-ai-it-version: 2026-05-29-ai-navigation-control-layer-v1 -->`. Files updated: SKILL.md, AGENTS.md, AI_NAVIGATION.md, templates/AI_NAVIGATION.md, templates/AGENTS-navigation-block.md.
- **AGENTS.md navigation block** — expanded from 7 to 11 instructions including: inspect companion-file rules before edits, do not treat Graphify/Repomix output as canonical truth, run audit/check
  commands before completion, update CHANGELOG.md for all governance/navigation changes, preserve user-authored content outside managed sections. Same expansion applied to
  templates/AGENTS-navigation-block.md (from 12 to 15 rules).
- **SKILL.md workflow** — added "Workflow: Applying This Skill to a Project" section with explicit 12-step process covering: read existing files, detect versions, detect customizations, read
  context-map.yaml, check companion rules, generate updates in memory, apply managed blocks, create .proposed files, regenerate outputs only when stale, run validation, append CHANGELOG.md, report
  result. Generated outputs explicitly labeled as support-only.
- **templates/context-preflight.sh** — fixed numbering bug: `[5/5]` → `[6/6]` with added step 5 for context pack freshness check.
- **context-map.yaml (package)** — fixed duplicate `templates/justfile` entry in `generated_templates.read`.

### Files changed

- `SKILL.md` — managed block pattern, embedded AGENTS navigation block, context compaction recovery section, workflow section
- `AGENTS.md` — managed block markers, navigation block rules
- `AI_NAVIGATION.md` — managed block markers, compaction recovery, audit procedure
- `context-map.yaml` — duplicate fix, audit_checks/promotion_rules/context_recovery
- `README.md` — four-capabilities table, managed block behavior, existing-project upgrade, compaction recovery, drift audit, TOC
- `ARCHITECTURE.md` — four-capabilities table, managed block behavior, existing-project upgrade, compaction recovery, drift audit
- `templates/AI_NAVIGATION.md` — managed block markers, compaction recovery, audit procedure
- `templates/context-map.yaml` — audit_checks/promotion_rules/context_recovery
- `templates/AGENTS-navigation-block.md` — managed block markers, expanded rules
- `templates/context-preflight.sh` — numbering fix, freshness check step
- `patterns/drift-audit.md` — full rewrite with 13 comprehensive sections
- `CHANGELOG.md` — this entry

### Notes

- Generated outputs (`graphify-out/`, `.ai-context/`) remain support-only and are never automatically promoted to canonical truth.
- `.archcore/` promotion still requires explicit authorization (promote mode only).
- Existing projects generated by older versions of this skill will have managed blocks inserted without overwriting user-authored content.
- Idempotency: re-running this upgrade twice will not duplicate managed blocks or CHANGELOG entries. Version strings prevent re-upgrade.

---

## 20260529_HHMM — deterministic navigation-control automation

### Added

- `scripts/upgrade_navigation_control_layer.py` — deterministic, idempotent upgrade script for navigation/control-layer files. Upgrades old managed block markers, adds version stamps, adds missing
  context-map.yaml keys (audit_checks, promotion_rules, context_recovery, update_rules). Supports --dry-run, --report-json, and .proposed fallback for risky YAML merges.
- `scripts/validate_navigation_control_layer.py` — deterministic validation script. Checks governance file presence, managed block integrity, version consistency, YAML validity, required schema keys,
  generated-output policy, context compaction recovery, script/task governance, companion consistency, and stale claim detection.
- `scripts/check_expected_diff.py` — git-diff check that only expected governance files (AGENTS.md, AI_NAVIGATION.md, CHANGELOG.md, context-map.yaml, scripts/README.md) changed after an upgrade.
  Detects accidental modifications to source files.
- `templates/update_rules.yaml` — default companion-file update rules template (governance_navigation section with AGENTS.md, AI_NAVIGATION.md, context-map.yaml, scripts/README.md, new_script_added
  relationships).
- `patterns/navigation-control-automation.md` — explains why automation exists, when to run each script, how to interpret exit codes, how to handle .proposed files, and how this complements
  patterns/drift-audit.md and patterns/script-task-audit-checklist.md.

### Changed

- `templates/justfile` — added 4 new targets: nav-upgrade-dry-run, nav-upgrade, nav-validate, nav-check-diff.
- `templates/scripts-README.md` — added entries for the three new automation scripts in the Task Inventory table.
- `SKILL.md` — added "Deterministic Navigation-Control Automation" section with recommended 6-step refresh order, key rules, and script table.
- `README.md` — added "Deterministic navigation-control automation" section with component table and key rules.
- `ARCHITECTURE.md` — added "Deterministic navigation-control automation" section with script table and references to templates/ and patterns/.

### Notes

- Scripts are the primary mechanism for existing-project upgrade. Markdown patterns are policy/explanation.
- All scripts are idempotent and safe to rerun. --dry-run mode provides safe preview.
- Upgrade script does not create .archcore/, .ai-context/, or graphify-out/.
- Generated outputs remain support-only. No automatic promotion.
- Fallback: .proposed files written when YAML merge is too risky.

## 20260812_1300

### Fixed

- **`upgrade_navigation_control_layer.py` no longer overwrites project-authored managed blocks.** It replaced any block whose markers matched, unconditionally — correct only while the block still
  contains what this skill put there, which stops being true the moment a project authors real content inside one. Found on a real project: a dry run would have stripped **222 lines** from
  `AI_NAVIGATION.md` (every supersession chain, every gate reference, the entire domain-routing table) and dropped three load-bearing rules from `AGENTS.md`, reporting only `replaced-old-block`.
- **Old-style markers were the MOST exposed, not the least.** `insert_or_replace_block()` tests `old_begin` first and matches it preferentially, so a project that had kept legacy markers — believing,
  as one did, that this protected it — was in fact first in line to be overwritten.

### Added

- **Provenance guard** — a block lacking a `skill-ai-it-version:` marker is never replaced. The generic block goes to `<file>.proposed-<section>-block` and the run is flagged for manual review.
- **`<!-- skill-ai-it:manual reason="..." -->` opt-out token**, honoured by the upgrader (never replaces, and never *inserts* an absent section) and by the validator (reports a pass rather than a
  missing-block/old-marker failure). Without it an intentionally-diverged project is permanently red, and a validator that always fails is one nobody reads.
- **`--force`** to override both guards, discarding current block contents. For use only after reading the `.proposed` file.

### Notes

- Strictly conservative: the guards can only ever refuse to overwrite. A false positive costs an unwanted `.proposed` file; a false negative cost 222 lines.
- Verified by running the upgrader against rsync'd scratch copies of a real project before and after: content preserved byte-for-byte (318/134/182 lines unchanged), validator went 11 failures + 5
  warnings → **0 and 0**.

### Blast radius, measured rather than assumed

Before shipping the guard, every project on this machine carrying a `skill-ai-it` managed block was checked for (a) the version marker and (b) how far its block had diverged from the current template.
Result across ~30 projects:

- **Not one carried a `skill-ai-it-version:` marker.** These blocks were authored by an agent following `SKILL.md` by hand, not written by the upgrade script, so none had the fingerprint.
- **Every block measured was 73–94% content that does not appear in the template**, ranging from 12 novel lines (`aws-to-local/AGENTS.md`) to 240 (`vocus-profitability/AI_NAVIGATION.md`).

So the exposure was never specific to one project: **running the upgrader anywhere in this estate would have destroyed project-authored content**, and the worst case was not the 222 lines that
prompted the investigation. A similarity threshold was considered and rejected — with no population sitting close to the template, it would add tunable complexity while separating nothing. The simple
provenance rule is both correct and sufficient here.

The practical consequence for existing projects: the first run after this change refuses everywhere and leaves `.proposed` files. That is the intended migration path — review the proposed block, merge
anything wanted by hand, then declare `<!-- skill-ai-it:manual reason="..." -->` to settle the block permanently.
