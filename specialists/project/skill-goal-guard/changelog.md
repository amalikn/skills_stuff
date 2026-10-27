---
Title: skill-goal-guard Changelog
Category: changelog
Kind: log
Status: current
Authority: local-supplement
Scope: Every change to skill-goal-guard's rules, code, layout and sources
Last reviewed: 2026-10-27
Summary: History of skill-goal-guard, newest first; the release heading is the only place the pack version lives.
---
# Changelog

## Unreleased

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
