---
Title: skill-goal-guard Changelog
Category: changelog
Kind: log
Status: current
Authority: local-supplement
Scope: Every change to skill-goal-guard's rules, code, layout and sources
Last reviewed: 2026-10-27
Summary: History of skill-goal-guard, newest first; the release heading is the only place the pack version lives.
Budget: 200 lines, 25 KB
---

# Changelog

## Unreleased

### 2026-10-27 18:29 — Overview: Records and data under Outside systems (operator review of the drawing)

- `docs/goal-guard-flows/parts/master.yaml` sets `drawing.look.last_row_align: centre` (new skill-drawio look key, fixed in the engine, not by hand): the lone
  "Records and data" group now sits under Outside systems; arrows into it shorter; layout audit clean; page exported and reviewed.

### 2026-10-27 18:27 — flow diagrams moved under docs/ (operator: "goal-guard-flows move under docs")

- `goal-guard-flows/` moved to `docs/goal-guard-flows/` with `git mv` (history kept); `just flows` and `just flows-check` point there; the drawing is unchanged and only the
  generated map's banner line names the new path. References updated in readme, SKILL.md, AGENTS.md (Layout), docs/catalog.md and the Archcore handoff guide.
- `context-map.yaml` given its one-line header summary (skill-coder's form), which the freshness check asked for once the file was tracked.

### 2026-10-27 18:23 — AGENTS.md tracked (operator: "it should be committed")

- `AGENTS.md` was never committed: the repo's `.git/info/exclude` line `AGENTS.md` hides every AGENTS.md. Committed files and four Archcore rules link to it, so a fresh
  clone would break those links and `just check`. Force-added (`git add -f`), as skill-nautobot's and skill-openwisp's were; once tracked, the exclude no longer applies to it.
  The repo-wide exclude rule is unchanged (it hides other packs' AGENTS.md too; reported to the operator).

### 2026-10-27 18:22 — Archcore content promoted (operator: "/skill-ai-it promote and approve all")

- 19 documents written as `accepted` pointer documents (option A: each states the item and links to the section that stays canonical, so `references/` remains
  where rules change, as in skill-smc and skill-nautobot): 6 ADRs, 6 rules, 4 specs, 2 guides, 1 plan; plus `.archcore/index.guide.md` with the not-promoted reasons.
  Excluded as in the report: the inherited skill-coder rule, roadmap phases L1-L5, the readme quick start.
- `archcore status` clean after quoting titles with colons and folding single-use tags into a nine-tag vocabulary; every link in `.archcore/` resolves.
- `ARCHCORE_PROMOTION_CANDIDATES.md` deleted (a transient queue, per the skill); AGENTS.md Working rules, `context-map.yaml` (`promoted`, `authority: pointer-documents`)
  and the catalog updated.

### 2026-10-27 18:10 — Archcore initialized (operator: "/skill-ai-it bootstrap for archcore")

- `archcore init` (archcore v0.3.6) created `.archcore/` with `settings.json` only; `archcore status` clean. No Archcore content written (only `promote` does that).
- `ARCHCORE_PROMOTION_CANDIDATES.md` lists candidates from SKILL.md, AGENTS.md, the references, scripts/readme.md and the pilot plan: 6 ADR, 7 rules (one excluded as inherited), 4 specs,
  2 guides, 2 plans (one excluded). It leads with an open question: AGENTS.md makes `references/` canonical while Archcore wins on conflict; options A pointer documents (proposed),
  B Archcore canonical, C decisions only.
- `context-map.yaml` `promotion_rules.archcore`: `initialized` and `authority_question: open` added (comments kept); navigation layer already routes to `.archcore/` when present.

### 2026-10-27 18:00 — flow map split into parts (operator: "can the flow be divided into smaller parts and then combined, like for unc")

- Source moved to `goal-guard-flows/parts/`: `master.yaml` (drawing settings and `#@include` lines) plus `components-people-and-agents`, `-outside-systems`, `-goal-guard-tools`,
  `-records-and-data` and `flows-scope-gate`, `-focus`, `-traceability`, `-resilience`; `goal_guard_flows.yaml` is now assembled from them (skill-drawio `assemble_flowmap.py`).
- Proof: flows identical; components identical except list order (grouped); the drawing holds the same 721 elements with the same labels and geometry (only two End-to-end boxes
  change place in the XML); layout audit clean. `just flows` assembles then renders; `just flows-check` adds the assembly drift check.

### 2026-10-27 17:57 — flow diagrams (operator: "also create flows for this skill")

- New `goal-guard-flows/goal_guard_flows.yaml` (skill-drawio flow map: 15 components, 7 flows in four families: scope gate, focus, traceability, resilience) and the drawing
  `goal_guard_flows.drawio` GENERATED from it: Overview, End-to-end, Handoff, Decision order, Hook gate, What's Next, Milestone trace and workbook, Snapshot export, Clean-instance restore.
- `just flows` renders it; `just flows-check` (drift plus layout audit, part of `just check`) passes, audit clean on every page; pages exported and reviewed before handing over (one
  crossing on the Overview between two thick arrows, within the audit's rules).
- Catalog, readme, SKILL.md tools table and AGENTS.md Layout updated; the drawing is never edited by hand.

### 2026-10-27 17:52 — skill-ai-it bootstrap (operator: "/skill-ai-it bootstrap")

<!-- skill-ai-it-upgrade: 2026-10-14-compact-v2 -->

- Navigation layer by the deterministic upgrader (version `2026-10-14-compact-v2`): new `AI_NAVIGATION.md` and `context-map.yaml`; managed blocks inserted in `AGENTS.md` and
  `scripts/readme.md`; `validate_navigation_control_layer.py` 0 failures. No `.archcore/` promotion; Graphify not run (disabled).
- Governed-files adoption (`adopt_governed_files.py --apply`): justfile recipes (`stale`, `roles`, `govern`, `docs`, `history`, `rotate`, `budget`, `changelog-entry`, `move-sections`,
  `outline`, `section`), freshness and role checks in `just check`, record keys on changelog, SCRATCHPAD and roadmap, front matter on `readme.md` and `AI_NAVIGATION.md`. All six findings
  it baselined were fixed instead (proposal YAML headers, readme quick start, roadmap current phase) and both baselines pruned to empty.
- Governance checker in the package layout: `scripts/check_governance.py` over `scripts/govcheck/` (`core.py` identical to the skill-ai-it template, excluded from ruff because it is
  four-space); families paths, catalog (SKILL.md routes every reference, docs/catalog.md lists every file, every front end has a row and a recipe), records (front matter keys and the blank
  line after it), runner (recipes use the pinned venv), structure. `just governance`, part of `just check`: 430 checks. Negative tests in `tests/test_govcheck.py`; one of them found a hole
  (the root readme counted as indexing every root file), fixed before commit.
- Code map: `adopt_code_map.py --apply` added 43 module entries; all decided `project_only` with reasons. Re-run of the bootstrap the same evening found one more (`tests/test_govcheck.py`), decided the same way; every other step
  reported nothing to do.
- Changes the hand-run checks in AGENTS.md "Before calling work done" into `just check`; AGENTS.md "Governance tooling status" updated (local file, git-excluded).

### 2026-10-27 17:35 — session findings, incidents and proposals (slurp close)

- Readiness finding: the pack is not installed for any agent (no symlink in `~/.claude/skills`, `~/.codex/skills`, `~/.agents/skills`); install stays deferred (SCRATCHPAD).
- Finding: SKILL.md TOC warnings and dead links come from VS Code's chat prompt-file validator treating SKILL.md as a skill file; anchors verified correct; fix is an operator setting (not changed).
- Finding: AGENTS.md is excluded from git in this repo (`.git/info/exclude`), so its table fix is local only.
- Incidents, all resolved in the session: an inline `noqa` placeholder written into `goal_guard.py` and replaced within minutes by a rewrite (never committed); a response cut off by a network drop
  while its refactor commands still ran (transcript shows them; state reconciled by `just check`); auto-mode permission checks timed out on three writes (retried); a security hook flagged a test
  string naming `os.system` (test now uses `builtins.print`); the OPA gate blocked a recursive delete of a scratch folder (used a new folder); the claude-code-guide subagent could not read the hooks
  page (context-mode hook blocks WebFetch, the subagent has no ctx tool), so the page was read through `ctx_fetch_and_index` in the main session.
- Proposed, not decided: cover shell writes the hook cannot see (git pre-commit check, read-only modes on protected records).
- Vikunja API facts used by the code checked against the captured OpenAPI 2.7.1 (Learned entry in `references/vikunja-integration.md`).
- Name spelled "Goal Guard" in prose across the pack (operator, 2026-10-27): 137 replacements in 50 files; identifiers, file and format names, and verbatim `docs/` text and `documents/` captures unchanged; changed markdown rewrapped with the canonical rewrap tool. The rename changed a comment in the fixture target map, so `goal_guard_trace.py` reported REVIEW until the
  fixture hashes in `examples/.../mappings.yaml` were re-pinned (the trace caught the change, as designed).
- A blank line added after the front matter in 27 markdown files (operator, 2026-10-27: "there should be a line gap after the frontmatter"); in `docs/` only the added front matter is touched, the verbatim text is unchanged.

### 2026-10-27 17:25 — pilot tools written under skill-coder (step 4, tools for steps 6-8)

- New `scripts/goal_guard_lib/` and seven front ends: `goal_guard.py` rewritten (baseline, BLOCK, decision order, ranking pipeline, Vikunja reads, `decisions.jsonl` behind `--apply`),
  `goal_guard_vikunja.py`, `goal_guard_trace.py`, `goal_guard_snapshot.py` (export, verify, clean-instance restore), `goal_guard_excel.py`, `goal_guard_doctor.py`, `goal_guard_hook.py` (DRAFT).
- Hook: advisory by default; fails closed on an unrecognised payload or its own crash; one PROCEED covers only its proposal's files for 2 hours (review note relayed 2026-10-27); a session's
  project also protects its `protected_paths` outside the project.
- Tests: v0.1 `tests/test_goal_guard.py` removed with the prototype (git history); 71 new tests; `just check` now runs ruff, the tests, skill-coder's helpers and the fixture.
- Fixtures: `examples/project_stuff/`, `examples/vikunja-tasks.json`, `examples/proposals/`; v0.1 fixtures moved to `examples/v0.1/`.
- New `requirements.txt` (PyYAML 6.0.3, openpyxl 3.1.5, ruff 0.17.3) and `ruff.toml`; `justfile` recipes for every script; `code-map.toml` updated.
- References: pilot-plan step 4 status and what it did not do; enforcement-and-hooks Learned entries (Claude Code 2.1.310 hook contract; file-scoped verdicts); vikunja-integration relation
  direction marked as an open check; decision-rules schemas note.
- Open before live use: relation direction on the instance, real hook captures and one observed block, restore read-back, D3 signing.

### 2026-10-27 16:27 — SKILL.md source layout

- Route table realigned (link column padded to its widest cell) and three lines over 200 columns wrapped; no wording changed.
- AGENTS.md: Layout table realigned the same way and the write-back trigger paragraph (257 columns) wrapped; no wording changed.

### 2026-10-27 15:03 — write-back audit; two write-backs deferred to the next session

- Audit (operator: "were skills written back to?"): skill-goal-guard has two Learned entries in `references/vikunja-integration.md` (commit 1dff9c8); skill-coder was judged `no_new_reusable_learning`
  at closeout (0 parked entries); the OPA gate traps were only in auto-memory. Two gaps found: the OPA tool's own record, and a skill-coder `reusable_candidate` on proving a move unchanged.
- Operator decision ("capture them both for the next chat session"): both write-backs deferred, not written; recorded in `SCRATCHPAD.md` Open items with targets and evidence, memory-keeper
  `skill-goal-guard.writeback-owed` and project-context.

### 2026-10-27 14:54 — definition pass, independent review, slurp close

- `AGENTS.md` rewritten to house style (operator: "make sure AGENTS.md and SKILL.md are properly defined"): layout incl. `documents/` and `SCRATCHPAD.md`, front-matter and catalog rule, naming rule,
  dependencies and consumers (Vikunja, UNC, hub, skill-coder), cross-project write-back trigger, governance tooling status (skill-ai-it bootstrap deferred).
- `SKILL.md`: status line (Vikunja deployed, nothing enforcing), Vikunja run location, Related skills, trigger phrases; name and description validated (593 of 1024 characters).
- Independent structure review (operator: "make sure the skills and references structure is efficient and coherent") applied: stale Vikunja/D-status in five places; GG-404/405 moved to L1 with file
  scope (feature #9), P09/F08 both pilot; backlog IDs cited as B-NN; BLOCK (unmapped task) vs PARK (unmapped idea) clarified; record formats added to `decision-rules.md`; approval verification added
  to `mvp-contract-and-change-control.md`; `me` partition noted; pilot report moves to `reports/`; one owner each for status (SKILL.md), workspace facts (project-layout), prototype gaps
  (`scripts/readme.md`), degraded mode (snapshot); conflict 8 settled; catalog rows for readme, SCRATCHPAD, documents.
- Learned entries added to `references/vikunja-integration.md` (dump nesting and filename collision, dumps hold the secret; registration flag location; shell-less image).
- `SCRATCHPAD.md` created. skills_stuff `README.md` gains a skill-goal-guard row; `.agents/skill-surfaces.md` (local-only, excluded from Git) too.
- Incidents this session: the OPA gate blocked recursive deletes and a pipe into the SHA-sum tool (read as pipe-to-shell), so the empty `docs/goal-guard/{scripts,tests,examples}` folders remain;
  context-mode blocks WebFetch and curl (its fetch tool was used); `code-map.toml` was first written with YAML syntax and an invalid module status (fixed); a one-off move script reported rc=1 from a
  wrong-cwd test step while bytes and behaviour were identical.

### 2026-10-27 — Vikunja deployed (pilot step 0)

- Vikunja 2.7.1 running locally from `tools_stuff/vikunja` (OrbStack, SQLite, localhost only); live OpenAPI and info saved under `documents/vikunja-2.7.1-20261027/`;
  `references/vikunja-integration.md` and `references/pilot-plan.md` (step 0 done) updated.
- D3 risk recorded in `references/pilot-plan.md`: a signing key held unlocked in the ssh-agent would let an agent sign approvals as the owner.

### 2026-10-27 — pilot decisions D1-D6

- Recorded in `references/pilot-plan.md`: one `apn` repository scoped by path; pilot spoke `unified-network-controller`; owner approval by signed Git commit; Vikunja on OrbStack with SQLite; `.gg/`
  folder name; D4 plan and Excel candidates found read-only in `enterprise-strategy` (full plan with milestones M1-M11 but `Status: draft`; to confirm which revision was issued).
- Updated `references/project-layout-and-storage.md`, `references/authority-and-sources-of-truth.md`, `roadmap.md` and `docs/catalog.md` to match.

### 2026-10-27 — pack created and sources consolidated

- Structure modelled on skill-drawio, skill-coder and skill-smc: root `SKILL.md` (`name: skill-goal-guard`, alias skill-gg), `AGENTS.md`, `CLAUDE.md`, `references/`, `scripts/`, `tests/`, `examples/`,
  `justfile`, `.mise.toml` (Python 3.14), `code-map.toml`; venv at `skills-working-cache/skill-goal-guard/.venv` (`just bootstrap`, 3.14.5).
- Thirteen references consolidate the v1.7 handoff, v1.7 kickoff, v0.x research pack and v0.1 skill; where each of the eight document conflicts is settled is listed in `docs/catalog.md`.
- Operator decisions recorded: Vikunja owns live tasks; Vikunja will be deployed locally; the first build is the full v1.7 pilot; lower-case markdown filenames; `goal-guard` folders and `goal_guard`
  files.
- Sources moved verbatim under `docs/` with front matter added and prose rewrapped to 200 columns (token invariance verified by `rewrap.py`); `docs/catalog.md` indexes them.
- Prototype moved byte-identical: `docs/goal-guard/{scripts,tests,examples}` → `scripts/goal_guard.py`, `tests/test_goal_guard.py`, `examples/*.json`; CLI output hash unchanged, 10 tests pass.
  Purpose/usage/safety headers then added to both files (skill-coder `script_headers` now OK; output hash still `2504fb41c7e48f1f`).
- Workspace facts read: `apn/` is one Git repository holding enterprise-strategy, unified-network-controller and smc-resiliency; `target-map.yaml` and `code-map.toml` in UNC and SMC; no `.archcore/`
  in SMC; no `.gg/` anywhere.
