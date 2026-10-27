---
Title: Thekedar to GoalGuard Source Extraction Matrix
Category: source-extraction
Status: proposed, not decided
Authority: upstream source inspected on GitHub main 2026-10-27; adaptations not implemented
Scope: Which Thekedar (MIT) mechanisms GoalGuard adapts and the tests that guard them
Last reviewed: 2026-10-27
Summary: Maps Thekedar hooks/templates to GoalGuard destinations and CTPS IDs, lists mandatory adaptations and MIT reuse obligations.
---
# Thekedar → GoalGuard v0.2: Source Extraction and Regression Contract

**Status:** implementation specification; source inspected, GoalGuard adaptations **not implemented or tested**.  
**Reviewed:** 2026-10-27. **Upstream:** [soumyachk101/Thekedar](https://github.com/soumyachk101/Thekedar), `main` at inspection. Before implementing, pin a specific upstream commit and re-check these paths.  
**GoalGuard scope:** extend **existing** M1/M2 work (C05, C08, C09–C12, C20 / GG-04, GG-06–GG-11). This is **not** a new product, repository or v0.2 feature track.  
**Source terms:** Thekedar is MIT licensed, copyright © 2026 Soumya Chakraborty. Preserve attribution and a copy of its licence if code is actually incorporated. Architectural concepts themselves may
  be independently implemented; do not assume source licence covers every dependency automatically.

## Contents

- [1. Decision](#1-decision)
- [2. Exact source-file extraction matrix](#2-exact-source-file-extraction-matrix)
- [3. Critical source findings and mandatory adaptations](#3-critical-source-findings-and-mandatory-adaptations)
- [4. GoalGuard v0.2 minimal event and decision contracts (proposed)](#4-goalguard-v02-minimal-event-and-decision-contracts-proposed)
- [5. Integration into *existing* milestones](#5-integration-into-existing-milestones)
- [6. Explicit exclusions and acceptance](#6-explicit-exclusions-and-acceptance)
- [7. Provenance and implementation hygiene](#7-provenance-and-implementation-hygiene)

---

## 1. Decision

**Extract / adapt the following small mechanisms:** preflight file scope, post-execution diff audit, session briefing, facts-only event ledger, explicit task contract, task-level verification record,
bounded fix loops, and installation self-checks. **Do not import** the orchestrator, 109 specialist agents, complete review pipeline, git-required workflow, state file parser as authoritative
database, or cloud integrations.

**Boundary:** Thekedar answers whether a coding task is being carried out within declared file scope. **GoalGuard first answers whether that task is necessary to the agreed goal/MVP**, whether it is
the highest-value next action given deadlines/dependencies/one-human capacity, and what evidence demonstrates completion. Thekedar's file checks are a second line of defence; neither they nor semantic
LLM judgments constitute a trusted filesystem sandbox.

## 2. Exact source-file extraction matrix

All paths below refer to the upstream repository root. Source links are to the inspected *path*, not a commit-pinned blob; implementation must pin and record revision hashes.

| Source file | Verified source behaviour / reusable logic | GoalGuard destination / planned modification | Existing task | Tests | Action |
|---|---|---|---|---|---|
| [`hooks/scope-guard.sh`](https://github.com/soumyachk101/Thekedar/blob/main/hooks/scope-guard.sh) | `PreToolUse` for file edits; task `Expected files` and `Scope addition` allowlist; exit 2 on confirmed miss; lexical `.` / `..` canonicalization; fail-open on parse doubt/no active task. | `adapters/claude/pretool.py` + `core/file_scope.py` (planned). Normalize agent event, validate task lease/contract revision first; allowed paths from **approved** task revision; semantic criterion gate precedes file test. Unknown/unparseable → `REVIEW` for protected proposal. | C05/C10 | GG-401–407, 412–413 | **Adapt logic**; do not copy script as-is |
| [`hooks/drift-check.sh`](https://github.com/soumyachk101/Thekedar/blob/main/hooks/drift-check.sh) | End-of-task `git status --porcelain` vs allowlist; reports `DRIFT`, always exit 0. | `core/changed_files.py` (planned). Compare a task-start baseline and observed changes; include staged, unstaged, renamed, untracked; record unknowns and prevent falsely attributing pre-existing files; output evidence-linked warning. | C08/C12 | GG-409–411 | **Adapt audit concept** |
| [`hooks/session-brief.sh`](https://github.com/soumyachk101/Thekedar/blob/main/hooks/session-brief.sh) | SessionStart prints terse `PROJECT_STATE.md`, active task and latest changelog pointer; bootstrap scaffolding optional; returns 0. | `core/brief.py` + provider start adapter (planned). Read GoalGuard canonical snapshot (not manually editable `.thekedar` state): current approved goal/contract revision, one human focus, project's next task, active agent leases, milestone/deadline, open decisions; enforce output size cap. | C10/C11 | GG-414–415 | **Adopt pattern** |
| [`hooks/munshi.sh`](https://github.com/soumyachk101/Thekedar/blob/main/hooks/munshi.sh) | PostToolUse append-only Markdown ledger: timestamp/tool/file; never blocks a session. | `core/event_ingest.py` (planned). Normalize events with `provider`, `session_id`, `agent_id`, `parent_agent_id?`, `task_id`, `contract_rev`, `event_id`, `observed_at`, `outcome`, `evidence_hash`; persist atomically with dedupe. Markdown report is generated view, not canonical state. | C09/C12 | GG-416–418 | **Adopt pattern, replace storage** |
| [`templates/task.md`](https://github.com/soumyachk101/Thekedar/blob/main/templates/task.md) | Objective, in-scope, NOT-in-scope, acceptance criteria, dependencies, expected files, risk/size. | `contracts/task.schema.json` (planned) + optional Markdown rendering: `goal_id`, `criterion_id`, `milestone_id`, deadline type, blockers, minimal next step, stop condition, evidence contract, optional paths; compact ad-hoc mode. | C03/C05 | GG-401, 403, 408 | **Adapt fields** |
| [`templates/PROJECT_STATE.md`](https://github.com/soumyachk101/Thekedar/blob/main/templates/PROJECT_STATE.md) | Current phase/task, completed work, next and decision log, designed for session resume. | `core/snapshot.py` (planned): generated read-only human-facing snapshot from canonical store; *three-level What's Next* and cross-project interruption/resume preserved. Never make a writable Markdown snapshot authoritative. | C06/C07/C09 | GG-414–415 | **Adopt presentation pattern** |
| [`templates/changelog-entry.md`](https://github.com/soumyachk101/Thekedar/blob/main/templates/changelog-entry.md) | Per-task what changed, what deliberately did not, why, files, reviewers, drift and follow-ups. | `reports/completion.md` (planned) with observed work, **non-work intentionally deferred**, criterion/evidence mapping, reviewer identity, disposition and approval record; works for infra/research/ad-hoc jobs without Git. | C08/C12 | GG-419 | **Adopt format** |
| [`templates/config.md`](https://github.com/soumyachk101/Thekedar/blob/main/templates/config.md) | Has `fix_loop_cap: 3` and `scope_guard: on` (with advisory/off modes). | `config/policy.yaml` (planned): separate retry budget (bounded attempts + time), advisory/enforce policy, protected-field whitelist, interruption/review policy. Do not inherit unrestricted opt-out for protected changes. | C05/C20 | GG-420, 406 | **Adapt small settings** |
| [`scripts/doctor.sh`](https://github.com/soumyachk101/Thekedar/blob/main/scripts/doctor.sh) | Checks installed hooks/configs/stored task state and self-tests guard events. | `goalguard doctor` (planned): validates schema, hook wiring, policy file ownership, event store, exact provider payload fixtures, stale leases and duplicate hooks; no writes to production ledger during diagnostics. | C08/C20 | GG-421 | **Adapt test pattern** |
| [`tests/test-scope-guard.sh`](https://github.com/soumyachk101/Thekedar/blob/main/tests/test-scope-guard.sh) | Tests allow/block/no-active/advisory, scope additions, path traversal and shell-glob expansion. | Port its relevant **behavioural cases** into provider-agnostic Python tests, but invert the dangerous policy assumptions (self-add scope / no-active). Use real Claude/Codex captured event fixtures. | C08/C10/C11 | GG-402–407, 413 | **Use as regression reference** |
| [`scripts/install-codex.sh`](https://github.com/soumyachk101/Thekedar/blob/main/scripts/install-codex.sh) + [`.codex/hooks/hooks.json`](https://github.com/soumyachk101/Thekedar/blob/main/.codex/hooks/hooks.json) | Installs skills and hook scripts; emits `SessionStart`, `PreToolUse`, `PostToolUse` declarations and `AGENTS.md`. | `adapters/codex` (planned): source-version-controlled config snippets with *actual installed Codex runtime* feature and payload tests; merge rather than overwrite existing hooks; keep opt-in. | C11 | GG-422–423 | **Adapt installation strategy, not configuration verbatim** |
| [`install.sh`](https://github.com/soumyachk101/Thekedar/blob/main/install.sh) | Copies hooks/skills/templates, merges Claude settings, backs up overwritten files. | `install/adapters` (planned): dry-run, existing-hook collision detection, reversible scoped merge, uninstall preserving GoalGuard data. | C10/C11/C20 | GG-422–423 | **Adopt safe-update pattern** |
| [`docs/TROUBLESHOOTING.md`](https://github.com/soumyachk101/Thekedar/blob/main/docs/TROUBLESHOOTING.md) | Explicitly documents simultaneous sessions causing task-state races; hook limitations and manual repair. | Make C09's single-writer transactions/optimistic revisions **non-optional** before multi-agent writes. Document degraded mode. | C09/C20 | GG-416–418 | **Use as negative-case evidence** |
| [`docs/BENCHMARKS.md`](https://github.com/soumyachk101/Thekedar/blob/main/docs/BENCHMARKS.md) | Test methodology; explicitly says no measured results published yet. | Compare guarded vs unguarded workflows on same goal scenarios; measure false blocks, missed scope creep, operator interruptions and task throughput. | C02/C08/C20 | GG-424 | **Adopt methodology only** |
| [`LICENSE`](https://github.com/soumyachk101/Thekedar/blob/main/LICENSE) | MIT licence. | If copied source is introduced, add `THIRD_PARTY_NOTICES.md` and original licence text for relevant portions, with source revision and modified files. | C20 | GG-425 | **Compliance requirement** |

Thekedar's top-level `README.md` and `ROADMAP.md` describe a larger coding-crew orchestration approach; only the small mechanisms in this table are in scope. **No claim that all of Thekedar was tested
locally.**

## 3. Critical source findings and mandatory adaptations

### A. Prevent **semantic** scope creep, not only path creep

- Thekedar allows edits to approved paths even if an agent adds irrelevant functionality inside them.
- GoalGuard preflight must resolve: approved `goal_id` → `criterion_id`/verified blocker → **necessity rationale** → smallest viable action → acceptable blast radius → authorization.
- A criterion ID alone is not proof of relevance; a separate semantic critic may recommend a disposition, but deterministic contract/approval checks take precedence.
- Example: `src/boot/recovery.py` is allowed by file scope; an optional plugin system added there is still `PARK` or `REVIEW` if unrelated to A/B recovery.

### B. Stop unauthorized self-approval

- In Thekedar, `.thekedar/**` is exempt, and a doer can add `## Scope addition` to the task file. That is operationally convenient but is not strong governance.
- GoalGuard stores immutable approved goal revisions and decisions through a **separate trusted writer**; the agent can propose, but cannot approve a new requirement, external deadline, milestone
  acceptance criterion or material scope expansion.
- Minor file-list discoveries within a pre-approved task may be automatically permitted **only** if governed by a pre-approved policy, with reason and audit event. Do **not** require the user to
  approve every extra test file.
- Unknown authority, missing task assignment or outdated contract revision must lead to `REVIEW` for material changes rather than silently trusting a modified Markdown file.

### C. Hooks are **not** a complete write sandbox

- `scope-guard.sh` handles declared file-edit tools; Thekedar notes Bash writes and symlink traversal can bypass it.
- GoalGuard cannot promise to intercept every code change, shell command, network action, file system write or spawned subagent. Protect high-risk state through the writer/API and filesystem
  permissions, with model/agent hooks as preventive advice where supported.
- Normalize *actual* hook payloads per client/version. Multiline `apply_patch` needs a dedicated parser if supported; never assume a `file_path` field exists.
- Read-only/non-destructive steps may fail-open with alert; protected decisions and contract writes must fail-safe at the trusted writer.

### D. Do not infer drift from `git status` alone

- Working-tree status can mix pre-existing dirty files with an agent's changes and miss already committed work.
- Anchor the task to an initial Git commit + dirty-file snapshot; inspect task-scoped events/commits and classify unknown/pre-existing changes separately. Use a robust Git parser (`--porcelain=v1 -z`
  or appropriate Git plumbing) when implemented, not space-delimited `sed` parsing.
- For ad-hoc/non-code tasks, use documented execution evidence, external references and acceptance checks; Git is optional.

### E. Preserve owner focus while allowing agent parallelism

- Thekedar describes single-active-task workflow within a repository. GoalGuard must track **one operator focus** across UNC/SMC/ad-hoc and multiple explicitly assigned bounded agent tasks.
- Authoritative task states need revision checks and unique task leases; stale leases should be `STALE/UNKNOWN`, never implicitly `DONE`.
- Scope guard must never grab the wrong `ACTIVE` task by reading the first file matching a grep; use explicit `task_id` + contract revision + agent assignment in each event.

## 4. GoalGuard v0.2 minimal event and decision contracts (proposed)

```json
{
  "event_id": "provider-session-seq-or-uuid",
  "provider": "claude_code",
  "session_id": "opaque-id",
  "agent_id": "opaque-id",
  "parent_agent_id": null,
  "task_id": "SMC-T014",
  "contract_revision": 3,
  "observed_at": "2026-10-27T08:00:00+11:00",
  "event_type": "proposed_action",
  "action": "modify A/B boot rollback path",
  "criterion_id": "SMC-AC04",
  "claimed_necessity": "required to satisfy boot failure acceptance test",
  "evidence_refs": ["test-report-id"],
  "proposed_files": ["src/boot/recovery.py"]
}
```

`event_id` must deduplicate retries; `observed_at` is evidence timing, not proof of completion. A semantic judgment should return one of `PROCEED`, `PARK`, `REVIEW`, `BLOCK` plus `reason_code`,
`contract_revision`, linked evidence and `requires_owner_approval`. It must never silently mutate the approved contract.

**Trust levels:** model-supplied claims = untrusted; provider hook activity = observation (not proof of approval); signed/locally-authenticated owner decision = approval; deterministic tests/human
verification = completion evidence. Do not equate a logged edit to completion.

## 5. Integration into *existing* milestones

| Gate | Already planned GoalGuard work | Thekedar-inspired refinement | Exit requirements |
|---|---|---|---|
| **M0** | Approved goal and MVP contract; labelled scenarios | Adopt `In scope / NOT in scope / Acceptance` structure where useful | Owner signs one scope baseline; ad-hoc compact contract retained |
| **M1** | C05 scope engine; C08 regression suite | Split semantic criterion check from file allowlist; build explicit proposal/approval model; port lexical traversal and scope-addition counterexamples | GG-401–408, 412, basic GG-420 executed; P0 pass (provider GG-413 deferred to M2) |
| **M2** | C09 durable journal, C10/11 hooks, C12 evidence | Add session brief, per-event ledger, task-start Git baseline, bounded fix loop, provider payload normalization, stale-session handling | GG-409–411, 413–419, 421–423 run; race/crash and hooks validated |
| **M3** | Vikunja projection, dashboard | Project evidence/decision snapshots, not raw doer edits | No Thekedar-specific feature; existing GG-301–310 still gate |
| **M4/M5** | Scheduled supervision, pilot/hardening | Review drift alerts and operator time saved; retain no-fork decision | Existing gates remain, plus GG-424 and licence check GG-425 if source copied |

Thekedar does **not** add an extra milestone or force Vikunja into M1. **Stop after M1** if the goal-to-action decision engine is not sufficiently reliable.

## 6. Explicit exclusions and acceptance

Excluded: importing `install.sh --all`, specialist-role catalog, blanket 3-reviewer-per-task pipeline, Thekedar task-state Markdown as GoalGuard canonical DB, automatic Git commit for non-code tasks,
full plugin installation in existing projects, re-implementing security/secret scanners, separate PM backend, and any new dashboard.

**Acceptance condition for extraction:** A reviewed GoalGuard prototype must (1) stop a same-file non-MVP feature even where file allowlist passes; (2) allow evidenced necessary repair; (3) refuse
silent owner-scope mutation; (4) resume an interrupted approved task; (5) report pre-existing changed files without falsely blaming the current agent; (6) reject concurrent conflicting task updates;
and (7) report what to do next for task/project/portfolio. These are **targets, not accomplished tests**.

## 7. Provenance and implementation hygiene

- Source files were inspected through GitHub on 2026-10-27; file links refer to `main`, whose content may change.
- Thekedar MIT licence reviewed. Before copying code, record immutable upstream commit hash, file SHA(s), reuse type, local modifications, author notice and tests.
- The copied shell implementation is **not assumed compatible** with all Codex/Claude versions; use versioned JSON event fixtures and actual live-hook probes.
- Where rewriting is simpler than importing Bash parsing, prefer a minimal Python implementation in GoalGuard rather than reproducing brittle text parsing.
- Verify package licence compatibility with GoalGuard's chosen FOSS licence prior to redistribution. These documents do not themselves import any upstream executable code.
