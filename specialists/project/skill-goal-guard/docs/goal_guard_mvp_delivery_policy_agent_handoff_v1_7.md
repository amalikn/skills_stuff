---
Title: Goal Guard MVP Delivery Governance Handoff v1.7
Category: handoff-spec
Status: current
Authority: working design spec; controlling handoff for the pilot (operator, 2026-10-27); not implemented
Scope: MVP scope gate, Vikunja portfolio, Enterprise-Strategy hub, .gg storage and snapshot/restore for project_stuff
Last reviewed: 2026-10-27
Summary: "Layered v1.0-v1.7 policy: owner-approved MVP gate (PROCEED/PARK/REVIEW/BLOCK), Vikunja as live task authority, hub/spoke checks, dual deadlines, target-map reads and portable snapshots."
---

# GoalGuard — MVP Delivery Governance

**Document type:** Agent implementation handoff and formal policy specification  
**Version:** 1.7 (proposed; not yet implemented or approved for enforcement)  
**Date:** 2026-10-27  
**Status:** DESIGN / AGENT HANDOFF  
**Intended consumers:** Codex, Claude Code, local coding agents, GoalGuard implementer  
**Related systems:** Archcore, Vikunja, Knowledge Curator, Enterprise-Strategy strategic hub

**v1.7 authority update:** §37 establishes the hierarchical portable snapshot/restore contract, clarifies storage ownership, and corrects the root folder name to `project_stuff`. Where prior examples
conflict, §37 controls.

**v1.5 authority update:** Sections 30–35 add the proposed GoalGuard skill lifecycle, `.gg/` persistence and hierarchical configuration contract. They supplement, not replace, §§1–29. Layout is
provisional pending inspection of existing GoalGuard/Archcore conventions.

**v1.4 authority update:** Sections 25–29 supersede the plan-authority and export assumptions in §23 where they conflict. In particular, after a controlled migration, Vikunja is authoritative for
*live operational planning*; the formally approved management baseline remains immutable and separately versioned. An issued Excel workbook remains a historical snapshot, and strategic context remains
in Enterprise-Strategy Markdown.

## Contents

- [1. Intent and non-negotiable outcome](#1-intent-and-non-negotiable-outcome)
- [2. Confirmed operating decisions](#2-confirmed-operating-decisions)
- [3. System boundaries and authority](#3-system-boundaries-and-authority)
- [4. Formal policy clauses](#4-formal-policy-clauses)
- [5. MVP contract: minimum data model](#5-mvp-contract-minimum-data-model)
- [6. Workflow and gates](#6-workflow-and-gates)
- [7. Decision semantics](#7-decision-semantics)
- [8. Change-control contract](#8-change-control-contract)
- [9. Archcore integration requirements](#9-archcore-integration-requirements)
- [10. Deferred ideas and knowledge handling](#10-deferred-ideas-and-knowledge-handling)
- [11. Examples (illustrative, not approved project baselines)](#11-examples-illustrative-not-approved-project-baselines)
- [12. Implementation phases — smallest viable rollout](#12-implementation-phases--smallest-viable-rollout)
- [13. Mandatory acceptance tests](#13-mandatory-acceptance-tests)
- [14. Required implementation-agent deliverables](#14-required-implementation-agent-deliverables)
- [15. Instructions to the receiving agent](#15-instructions-to-the-receiving-agent)
- [16. Open integration facts to verify in the actual workspace](#16-open-integration-facts-to-verify-in-the-actual-workspace)
- [17. Extension: multi-project portfolio prioritization (requested 2026-10-27)](#17-extension-multi-project-portfolio-prioritization-requested-2026-10-27)
- [18. Extension: Archcore and AGENTS.md rule hierarchy](#18-extension-archcore-and-agentsmd-rule-hierarchy)
- [19. Revised minimal implementation order (do not expand phase one)](#19-revised-minimal-implementation-order-do-not-expand-phase-one)
- [20. Updated receiving-agent assignment](#20-updated-receiving-agent-assignment)
- [21. Change record (v1.2)](#21-change-record-v12)
- [22. Extension: Enterprise-Strategy hub-and-spoke coordination (v1.3)](#22-extension-enterprise-strategy-hub-and-spoke-coordination-v13)
- [23. Extension: management plan → GoalGuard → Vikunja traceability](#23-extension-management-plan--goalguard--vikunja-traceability)
- [24. Change record (v1.3)](#24-change-record-v13)
- [25. v1.4 — Planning-system decision and migration contract](#25-v14--planning-system-decision-and-migration-contract)
- [26. v1.4 — Dual-deadline and forecast policy](#26-v14--dual-deadline-and-forecast-policy)
- [27. v1.4 — FOSS platform choice and exit gate](#27-v14--foss-platform-choice-and-exit-gate)
- [28. v1.4 — Archcore / agent enforcement addition](#28-v14--archcore--agent-enforcement-addition)
- [29. v1.4 — Acceptance tests, rollout ceiling, and change record](#29-v14--acceptance-tests-rollout-ceiling-and-change-record)
- [30. v1.5 — GoalGuard packaging and skill hierarchy](#30-v15--goalguard-packaging-and-skill-hierarchy)
- [31. v1.5 — `.gg/` file contract and data ownership](#31-v15--gg-file-contract-and-data-ownership)
- [32. v1.5 — Resolution, startup and ongoing enforcement](#32-v15--resolution-startup-and-ongoing-enforcement)
- [33. v1.5 — Lifecycle, backups, migration and repository hygiene](#33-v15--lifecycle-backups-migration-and-repository-hygiene)
- [34. v1.5 — Minimal pilot and test gates (new tests F01–F14)](#34-v15--minimal-pilot-and-test-gates-new-tests-f01f14)
- [35. v1.5 — Coding-agent kickoff and definition of done](#35-v15--coding-agent-kickoff-and-definition-of-done)
- [36. v1.6 — Existing project maps are first-class integration inputs](#36-v16--existing-project-maps-are-first-class-integration-inputs)
- [37. Hierarchical `.gg/` storage, portable snapshots, and restore contract (v1.7)](#37-hierarchical-gg-storage-portable-snapshots-and-restore-contract-v17)

---

## 1. Intent and non-negotiable outcome

Stop projects from remaining indefinitely in idea/architecture planning, and stop coding agents from enlarging approved MVPs. Preserve freedom to brainstorm in ChatGPT without allowing brainstorming
to change implementation commitments.

**Success is a small, working, tested deliverable—not a complete plan, a comprehensive architecture, or additional feature proposals.**

This document specifies **GoalGuard delivery governance only**. It is not a request to redesign GoalGuard, Archcore, Vikunja, or the Knowledge Curator. The implementing agent must first inspect the
existing GoalGuard project and Archcore conventions, then make the minimum changes needed to implement this contract.

## 2. Confirmed operating decisions

1. **ChatGPT exploration remains unrestricted.** No real-time interruption, timeboxing, or enforced warnings during brainstorming.
2. **Governance begins at implementation handoff** to Codex, Claude Code, or another coding agent, and continues while they execute committed work.
3. Every implementation effort requires an explicit, testable MVP target and boundaries.
4. An approved MVP is frozen: novel ideas, attractive improvements, and speculative future-proofing do not automatically enter scope.
5. The project owner can explicitly authorize a change; an LLM cannot authorize itself.
6. **GoalGuard** owns scope, delivery decisions, deferred ideas, and milestones. **Archcore** owns project-local technical rules/specifications and surfaces GoalGuard's scope obligation to agents.
   **Knowledge Curator** processes and reconciles knowledge from large Markdown corpora; it is **not** the idea backlog or a scope-approval authority. **Vikunja**, where used, is the operational task
   source of truth (priority, due dates, relations, order, status), not the authority to approve scope changes.
7. Existing GoalGuard decision vocabulary: **PROCEED, PARK, REVIEW, BLOCK**. Reuse rather than invent a parallel status model.

## 3. System boundaries and authority

| Component | Owns | Does not own |
|---|---|---|
| GoalGuard | MVP contract, scope baseline, approved changes, delivery gates, deferred-idea register, evidence of completion | Semantic truth of all source Markdown; architectural implementation decisions |
| Archcore | Project-local architecture, design constraints, specifications and agent rules | Independent amendment of frozen MVP scope |
| Knowledge Curator | Extraction, provenance, reconciliation, conflict/staleness detection across Markdown files | Feature prioritization, MVP approval, backlog control |
| Vikunja | Operational tasks, priorities, dates, relations, status, and view ordering | Approve MVP scope changes or substitute for GoalGuard gates |
| ChatGPT | Brainstorming, analysis, drafting candidate ideas and handoff material | Automatic modification of an approved MVP |
| Coding agents | Execute approved scope, produce tests/evidence, propose changes | Self-approval of scope expansion |

**Authority precedence for delivery scope:** owner-approved GoalGuard baseline / authorized change > agent proposals / task suggestions / planning notes. Archcore's technical standards remain binding
within the approved scope. If technical constraints make that scope infeasible, halt the affected work and request **REVIEW**; do not silently change the target.

The Knowledge Curator may index or summarize GoalGuard Markdown records as ordinary source material; that read path does not grant write-back or approval authority.

## 4. Formal policy clauses

| ID | Normative requirement | Violation response |
|---|---|---|
| MVP-001 | Before any implementation handoff, an MVP contract **MUST** exist. | BLOCK |
| MVP-002 | Contract **MUST** define problem, one outcome, deliverable, verifiable acceptance criteria, exclusions, owner, and baseline identifier/version. | BLOCK if materially incomplete |
| MVP-003 | The MVP **MUST** be explicitly approved by the designated human owner before scope is frozen. | BLOCK |
| MVP-004 | A coding agent **MUST NOT** implement functionality outside approved acceptance criteria and necessary dependencies. | BLOCK or PARK |
| MVP-005 | Candidate enhancements **MUST** be retained as deferred ideas without changing current scope. | PARK |
| MVP-006 | A required change **MUST** explain why existing acceptance criteria cannot be met, supply evidence, and await owner authorization. | REVIEW |
| MVP-007 | An agent **MUST NOT** treat its own proposal, an LLM recommendation, or a Vikunja task as approval. | BLOCK |
| MVP-008 | The smallest demonstrable working slice **SHOULD** be completed before optional abstraction/optimization. | PARK optional work |
| MVP-009 | Work **MUST NOT** be declared delivered without acceptance evidence and the required human sign-off, if specified by the contract. | BLOCK completion |
| MVP-010 | Planning **MUST** end with a commit, explicit deferment, or named blocking question; speculation alone cannot satisfy the planning exit. | REVIEW at handoff |
| MVP-011 | Approved scope changes **MUST** preserve baseline history, rationale and authorizing actor. | BLOCK change without record |
| MVP-012 | If GoalGuard status or authoritative contract cannot be read reliably, the agent **MUST** fail closed on scope-changing operations. | BLOCK pending recovery |

**Necessary dependency test:** proposed work is necessary only if an existing acceptance criterion demonstrably cannot be met without it. “Good architecture,” “might be needed later,” and “easy to add
now” are not sufficient.

**Permitted implementation discretion:** low-level refactoring, bug fixes and tests that do not change observable scope and are necessary to satisfy an accepted criterion may proceed without fresh
approval. If an implementation choice changes architecture against an Archcore constraint, follow Archcore's existing approval process as well.

## 5. MVP contract: minimum data model

Store in the repository's existing, appropriate version-controlled format. **Do not introduce a new folder convention solely for this policy.** Schema below is conceptual; use current GoalGuard
names/structure if equivalent.

```yaml
mvp_id: "UNC-MVP-001"
baseline_version: 1
status: approved # draft | approved | delivered | superseded
owner: "human-project-owner"
problem: "What specific user problem is addressed?"
outcome: "One observable outcome, independently demonstrable"
deliverable: "The smallest working artifact that provides that outcome"
acceptance_criteria:
  - id: AC-01
    test: "Observable pass/fail condition"
    evidence_required: "Test output, log, or demonstration reference"
exclusions:
  - "Specific feature consciously deferred"
constraints:
  - "Binding existing architectural or operational constraints"
planning_exit:
  result: commit # commit | defer | blocked
  unresolved_blockers: []
approval:
  actor: "human-project-owner"
  evidence_ref: "immutable or auditable approval reference"
  approved_at: "ISO-8601 timestamp"
```

Contract rules:
- Reject empty, subjective, or untestable acceptance criteria (e.g., “enterprise ready,” “scalable,” “bulletproof”).
- An exclusion cannot be overridden by a task title, a planning document, or agent inference.
- Baseline identifiers must be immutable in the audit trail. Updates generate a new revision rather than overwriting historical authority.
- References should point to existing Archcore architecture/spec artifacts rather than duplicate their contents.

## 6. Workflow and gates

### Stage A — Exploration (outside enforcement)

ChatGPT conversations may explore alternatives indefinitely. A candidate feature can be submitted to GoalGuard explicitly; it is not promoted automatically. The Knowledge Curator remains free to
process Markdown knowledge per its separate specification.

### Stage B — Planning exit

Before coding handoff, the user or agent prepares one minimal MVP contract. GoalGuard validates fields and asks only for missing blocking decisions. The available outcomes are:
- **Commit** to the smallest verifiable MVP with human approval;
- **Defer** the work, preserving its status;
- **Blocked** on a concrete unresolved dependency or owner decision.

Do **not** add a universal planning-hour limit in v1; the user chose enforcement at coding handoff, not interruption of ChatGPT exploration. Planning exit is a **handoff requirement**, not a
prohibition on further discussion.

### Stage C — Handoff gate

For every proposed work item, the agent obtains the approved GoalGuard baseline and relevant Archcore rules. Evaluate:

1. Is the baseline present, approved and readable?
2. What acceptance criterion does the proposed work advance?
3. Is the work expressly excluded?
4. Is it necessary to meet that criterion, or merely an enhancement?
5. Does it violate an existing Archcore technical constraint?

Emit decision and short rationale; no novel work begins when result is REVIEW or BLOCK.

### Stage D — Execution guard

Evaluate at the beginning of each independently dispatched work item and when a new requirement, design enlargement, or significant dependency emerges. Do not require a model invocation for every file
write. Record evidence for decisions and exceptional approvals. Preserve the current authorized task when an unrelated idea is parked.

### Stage E — Completion gate

A milestone may be marked delivered only if every applicable acceptance criterion has linked evidence showing a pass, no blocking review is unresolved, and any specified sign-off is captured. Passing
CI without satisfying the observable outcome is insufficient. Mark optional enhancements as PARK; they must not block MVP completion.

## 7. Decision semantics

| Decision | Condition | Can agent execute the proposed work? | Record |
|---|---|---|---|
| PROCEED | Explicitly in scope or proved necessary for AC | Yes | AC reference and rationale |
| PARK | Useful but unnecessary for this baseline | No, not in current MVP | Idea + context + target future consideration |
| REVIEW | Possible critical missing requirement, conflict or baseline revision needed | No for affected work | Evidence, alternatives, requested human decision |
| BLOCK | Missing/unauthorized baseline, exclusion violation, or invalid self-approval | No | Failed clause and remedy |

**Fail safely:** Do not invent authority from incomplete records. For a completely unrelated unaffected task, a REVIEW need not freeze the entire project unless the approved policy expressly requires
it.

## 8. Change-control contract

When requesting an MVP change, an agent provides:
- Current baseline ID and criterion affected;
- Defect or constraint making the existing deliverable impossible/unsafe/invalid;
- Evidence and smallest proposed change;
- Alternatives that keep scope unchanged;
- Impact on deadline, tests, dependencies and exclusions;
- Explicit request to the designated owner.

Only an authenticated, auditable owner decision may create a new approved baseline. Approval must name the specific proposal/revision, not be inferred from conversational assent to another subject.
Maintain an append-only event record using GoalGuard's existing journal if present. Record denied or deferred proposals as such.

## 9. Archcore integration requirements

1. **Discover actual Archcore conventions in the target repository first.** Do not assume `.archcore/` paths or commands without inspection.
2. Install one **short agent-visible rule** in the existing Archcore rule mechanism. It should reference the **single authoritative** GoalGuard MVP contract; do not duplicate the full policy in
   several locations.
3. Ensure both Codex and Claude Code read the rule through their existing project instruction mechanism. Inspect supported hooks and bindings; do not claim technical blocking where only prompt
   guidance exists.
4. Provide a deterministic pre-work validation command/interface (or reuse the existing GoalGuard gate) returning structured decision + reason + matched criterion, with nonzero exit for
   blocked/review-needed work where appropriate.
5. Integrate the gate at the **dispatch/handoff boundary** and when work scope materially changes. Never rely on an LLM assertion alone to certify its own compliance.
6. If a runtime cannot enforce hooks, label that connection **advisory only** and report it rather than claiming full enforcement.

### Proposed compact Archcore rule text

> **MVP delivery guard:** Before implementing a new work item, read GoalGuard's owner-approved active MVP baseline and map the item to a specific acceptance criterion. Do not implement excluded or
> unapproved features. Send beneficial but unnecessary ideas to GoalGuard as PARK, and submit indispensable scope changes as REVIEW for explicit owner approval. Follow existing Archcore architectural
> constraints within authorized scope. Do not report MVP delivery until GoalGuard's evidence gate passes. If the authoritative baseline cannot be read, do not expand scope.

This is content to adapt to the established Archcore format, **not** a command to create a new governance directory.

## 10. Deferred ideas and knowledge handling

GoalGuard keeps a light deferred-ideas record with title, original context/source reference, why it may be valuable, why it is not needed for the current MVP, and optional future milestone. A one-line
idea may be linked to richer ChatGPT brainstorming without copying an entire conversation. These records must not turn into active Vikunja tasks without explicit promotion.

The Knowledge Curator's v1.0 corpus-processing responsibilities remain untouched. No new ingestion, synchronization, write-back, or scope mutation is required for the curator as part of this
implementation.

## 11. Examples (illustrative, not approved project baselines)

### UNC illustrative first slice

**Outcome:** Retrieve and present identifying/operational information from **one** Cambium device, end to end.  
**Potential acceptance evidence:** device connection succeeds; identity fields are extracted; persisted record is retrievable; a basic output displays the record.  
**PARK:** cross-vendor abstraction, complex topology, fleet firmware orchestration, dashboard polish.

### SMC resiliency illustrative first slice

**Outcome:** One Raspberry Pi returns automatically to a known-working system after an induced failed update.  
**Potential acceptance evidence:** inactive-slot update, deliberate health-check failure, bounded retry/fallback behavior, confirmation of healthy restored boot and retained previous image.  
**PARK:** full-fleet controller integration, x86 generalization, broad firmware matrix, advanced recovery UI.

**Important:** These are candidate MVPs, not commitments. The actual scope must be approved in each project's GoalGuard baseline; operational safety requirements cannot be waived to make a demo
easier.

## 12. Implementation phases — smallest viable rollout

### Phase 0 — Inspect before modifying

Find current GoalGuard model, journal, policy entry points, approvals, integrations and test setup. Inspect Archcore installation and project rules. Report what already exists and identify the
**minimal delta**. Do not refactor unrelated systems.

### Phase 1 — Policy and gate

Implement baseline validation, scope classification, owner-approved revisions and completion evidence using current GoalGuard primitives. Support PROCEED/PARK/REVIEW/BLOCK. Make the gate callable by a
coding agent or dispatcher; reject missing approval.

### Phase 2 — One-agent integration pilot

Wire one real repository and one agent (Codex **or** Claude Code) through existing Archcore instructions and a real enforcement point. Verify the guard fails closed when the baseline is missing. Do
not roll out across all repositories yet.

### Phase 3 — Expand only if proven

After successful pilot, reuse the same policy across the second agent and then other projects. Add Vikunja display mapping only if the existing integration needs it. Do not build a UI, dashboard,
notification system or curator integration in v1.

## 13. Mandatory acceptance tests

| Test | Given | Expected |
|---|---|---|
| T01 | No baseline at handoff | BLOCK; implementation not dispatched |
| T02 | Draft baseline without owner approval | BLOCK |
| T03 | Approved baseline + work directly satisfying AC-01 | PROCEED |
| T04 | Attractive feature unrelated to any AC | PARK; original task unaffected |
| T05 | Explicitly excluded feature presented as “future-proofing” | BLOCK or PARK, never execute |
| T06 | Essential missing dependency demonstrated with evidence | REVIEW until owner decision |
| T07 | Agent self-generates “approval” | BLOCK |
| T08 | Owner approves exact change | New auditable baseline revision; then re-evaluate |
| T09 | Tests absent or failed | Completion BLOCK |
| T10 | All criteria evidenced, no blockers, required sign-off exists | Mark MVP delivered |
| T11 | GoalGuard unreadable at handoff | Fail closed; no silent fallback |
| T12 | New ChatGPT brainstorm without explicit handoff | No mutation of approved scope |
| T13 | Curator extracts Markdown containing feature proposals | No automatic task/scope promotion |
| T14 | Agent finds conflicting Archcore technical requirement | REVIEW or existing architecture exception process, not unilateral rewrite |
| T15 | Non-scope-changing bug fix needed to pass an existing AC | PROCEED with rationale |

These should be automated in the existing test framework where feasible, with at least one end-to-end blocked handoff demonstration.

## 14. Required implementation-agent deliverables

1. **Gap analysis:** already-supported features vs changes required; exact integration points.
2. **Minimal code/policy changes** in existing structure; no unnecessary new service or architecture.
3. **One concrete approved test fixture** with baseline, scope exclusions and ACs.
4. **Working gate demo:** in-scope PROCEED, optional PARK, unauthorized BLOCK, essential-change REVIEW.
5. **Test evidence** including failure behavior and completion-gate behavior.
6. **Operational note:** invocation, source of truth, human approval path, rollback, and honest distinction between enforced vs advisory clients.

### Definition of done for this initiative

This initiative is complete when **one coding agent in one real project** demonstrably cannot start an out-of-scope implementation through the chosen gated workflow, can still execute in-scope work,
and can preserve a proposed idea without incorporating it into the current MVP. A policy Markdown file alone is not sufficient.

## 15. Instructions to the receiving agent

> Implement the smallest viable GoalGuard MVP-scope gate described here. First inspect the current repositories, existing GoalGuard decision machinery, Archcore conventions and test interfaces. Reuse
> what is already present. Keep ChatGPT exploration unrestricted. Do not modify Knowledge Curator functionality. Avoid creating a new PM system, UI, universal time tracker, additional daemon, or
> duplicate policy store. Before editing, return a concise implementation plan identifying existing components and the smallest code delta; then execute the permitted scope and validate the specified
> tests. Where a named integration feature is absent, report the limitation rather than inventing commands or claiming enforcement.

## 16. Open integration facts to verify in the actual workspace

- Existing GoalGuard repository location, baseline schema, decision log, and enforcement entry points.
- Archcore's *actual installed* rule-file paths, hooks and tool support in this repository.
- Which client supports an enforceable handoff hook versus advisory instructions only.
- Whether Vikunja is already integrated and how approval identity is authenticated.

These are **implementation discovery items**, not reasons to enlarge the MVP.


## 17. Extension: multi-project portfolio prioritization (requested 2026-10-27)

**Decision:** Treat Vikunja as the authoritative operational task register; GoalGuard computes *which eligible item to execute next*, enforces MVP/approval gates, and maintains an auditable
recommendation. Do not copy mutable task priorities, dates, or ordering into `AGENTS.md`, Archcore rules, or a parallel Markdown task ledger.

### 17.1 Portfolio boundaries and work contexts

Projects are organized under a shared `project_stuff/` root, including `project_stuff/APN/` (work) and sibling `project_stuff/me/` (personal). Each contains independently governed project
repositories. The root name `project_stuff` and sibling names `APN` and `me` are user-specified; absolute disk location, exact subprojects, and repository boundaries still require inspection. Discover
and preserve the live structure before creating configuration.

- **Global context:** Common policy principles and the current human-approved capacity allocation across work/personal contexts.
- **APN context:** Work obligations, business deadlines, operational incidents, APN priority overrides; visibility and credentials restricted to authorized APN projects.
- **me context:** Personal priorities and schedules; cannot silently override APN work obligations.
- **Project context:** MVP baseline, technical rules, active milestones, task-to-acceptance-criterion mapping.
- **Task context:** Vikunja item ID, priority, due date, task relations, status, estimate if actually provided, and explicit owner decision.

Portfolio recommendations must respect privacy and access boundaries: an agent opened in one project must not automatically retrieve protected content from sibling projects. A portfolio service may
use authorized metadata across projects, without distributing task contents or credentials to every coding agent.

### 17.2 Vikunja integration contract

Use the existing Vikunja instance and its supported API; do not invent a second PM database. Vikunja provides task priorities, dates, task relations (including `blocking`/`blocked_by`,
`precedes`/`follows`), and view-specific ordering. **View position is not necessarily a global execution rank.** Inspect the installed version and its API schema before mapping values.

The first connector slice MUST:
1. Read authorized projects and incomplete tasks, with stable IDs and source timestamps.
2. Read priority, due/start dates, task status, explicit dependency relations, and relevant project grouping; use documented per-version API fields.
3. Identify tasks blocked by incomplete prerequisites and exclude them from the immediately executable queue.
4. Associate tasks with a GoalGuard-approved MVP and acceptance criterion, where implementation work is requested.
5. Produce one ranked portfolio queue and exactly one **recommended next actionable task**, with rationale and source IDs.
6. Degrade transparently: if Vikunja is unavailable, use the last known snapshot for read-only orientation **with a stale-data warning**, but do not authorize new scope, reorder commitments, or
   declare completion.

Do not assume task title, numerical priority, or task existence constitutes approval of a scope change. Keep human approval and GoalGuard MVP baselines authoritative.

### 17.3 Distinguish urgency, priority, dependencies, and capacity

- **Priority:** Relative business/personal importance recorded in Vikunja; use configured field mapping, not hardcoded assumptions about integers.
- **Urgency:** Derived from proximity of deadlines, critical incidents, and explicit time-critical overrides; separate from importance.
- **Order:** Dependency/precedence relations are constraints; user-managed view ordering is only a tie-breaker when applicable.
- **Capacity:** One human executor. Default operating limit: **one active focus item**, plus an explicitly authorized operational interruption. A task estimate is optional; do not fabricate durations
  or capacity allocations.

Recommended deterministic selection pipeline:
1. Enforce context access, approved MVP, task status, and blocking dependencies.
2. Honor explicit human-selected work context, fixed commitments, and urgent operational exceptions.
3. Prioritize tasks with genuine imminent deadlines and blocking impact; then use user-set Vikunja priority; use effort/available time only when reliable data exists.
4. Use deterministic ties: explicit dependency/order, then due date, then stable task ID. Log ranking factors and exclusions.
5. Return one suggestion with concise rationale; allow the human to explicitly override it with a logged reason. Never auto-change Vikunja priority to rationalize a recommendation.

Avoid a complicated weighted score until real-world trials reveal inadequate ordering. Do not treat every new idea as urgent.

### 17.4 Operational interactions

- **What should I work on now?** Show current context, one task, its Vikunja ID, why it is eligible, why it outranks alternatives, and the precise next demonstrable action.
- **Interrupt:** Confirm actual urgency/authorization; checkpoint work, record interruption, and propose when to resume. Preserve previous task state.
- **Complete:** Attach accepted evidence to the existing GoalGuard MVP/acceptance record; update the corresponding Vikunja task via authenticated integration only after authorized outcome.
- **Reschedule/reprioritize:** User edits Vikunja; GoalGuard re-reads and recalculates. A GoalGuard human-approved exception may override a recommendation without overwriting the underlying priority.

### 17.5 Additional policy requirements

| ID | Requirement | Failure behavior |
|---|---|---|
| PORT-001 | Vikunja is the source of truth for task priority, dates, relations, and status | Never maintain a competing editable priority copy |
| PORT-002 | All coding tasks MUST map to an eligible, approved MVP before work begins | BLOCK handoff |
| PORT-003 | Blocking prerequisites MUST be respected | Do not recommend as immediately actionable |
| PORT-004 | No more than one primary focus item at a time without human override | REVIEW conflicting assignment |
| PORT-005 | APN/me scope and access separation MUST be preserved | BLOCK unauthorized cross-context content access |
| PORT-006 | Ranking MUST be explainable, deterministic, and based on current authorized inputs | REVIEW if required metadata ambiguous |
| PORT-007 | Human overrides MUST be recorded with actor, rationale and time | BLOCK silent priority/scope override |
| PORT-008 | On API failure, stale task data MUST NOT authorize changes | Fail closed for mutations |
| PORT-009 | Vikunja ordering MUST NOT be treated as a universal portfolio ordering if it is view-specific | Use explicit constraints/tie-breaks |

## 18. Extension: Archcore and AGENTS.md rule hierarchy

**Critical implementation caveat:** Archcore documents `.archcore/` as Git-native project context and supports free-form directories, typed Markdown documents, MCP and hooks. This does **not** by
itself prove that a rule in `project_stuff/.archcore/` automatically applies to independent nested Git repositories. Similarly, `AGENTS.md` discovery depends on the agent/client. Implement explicit
resolution and tests rather than assuming inherited scope.

### 18.1 User-defined folder hierarchy (subprojects illustrative)

```text
project_stuff/
  AGENTS.md                  # thin global handoff pointer, only if existing convention supports it
  .archcore/                 # optional shared global policy repo; verify tool support
  APN/
    AGENTS.md                # work-context boundary and pointer
    .archcore/               # optional context policy, verify independent repo behavior
    UNC/
      AGENTS.md              # project-local pointer
      .archcore/             # native Archcore project documents
    SMC-Resiliency/
      AGENTS.md
      .archcore/
  me/
    AGENTS.md                # personal-context boundary and pointer
    .archcore/               # optional context policy
    personal-project/
      AGENTS.md
      .archcore/
```

**Only `project_stuff`, `APN`, and `me` are confirmed folder names; child project names are illustrative. Not a directive to create all these files.** Survey the actual existing `AGENTS.md` tree, Git
roots, Archcore initialized roots, and agent working directories first. Make the smallest changes to existing files; do not duplicate full policy text into every level.

### 18.2 Effective-policy resolution

For a given coding session, resolve in this order:
1. **Global GoalGuard policy:** applicable to all projects (MVP, no unauthorized expansion, human approval).
2. **Context policy (`APN` or `me`):** allowed portfolio, confidentiality, deadlines, work/personal separation and capacity policy.
3. **Project GoalGuard baseline:** current approved MVP, acceptance criteria, exclusions and authorized task IDs.
4. **Project Archcore:** local technical standards, architecture, specs, ADRs, and commands.
5. **Task:** Vikunja operational metadata and dependency state; never a scope-approval override.

A more specific rule MAY tighten constraints but MUST NOT silently weaken an ancestor security, privacy, approval, or MVP boundary. When policies conflict, report the exact sources and request REVIEW.
Do not arbitrarily select the nearest file or whichever message appears last. GoalGuard is authoritative for delivery authorization; Archcore for in-scope technical constraints.

**Mechanism:** Prefer a single canonical versioned GoalGuard policy, referenced by IDs and retrieved at handoff by the GoalGuard adapter. Use existing Archcore integration to expose applicable
technical rules, and the existing `AGENTS.md` conventions only for a short bootstrap pointer. If native inheritance is unavailable, the adapter explicitly resolves and injects the applicable policy
layers; do not rely on implicit parent-directory discovery.

### 18.3 Minimal Archcore-facing rule text (semantic contract)

> Before proposing implementation, resolve current GoalGuard global, APN/me context, and project MVP scope; retrieve the Vikunja next-task recommendation and verify the task maps to an approved
> acceptance criterion. Do not infer permission from a task priority or from brainstorming. Execute only approved scope. On missing, conflicting, blocked, or stale authorization, return GoalGuard's
> decision and stop the affected work. Follow this project's Archcore technical constraints. Never import sibling-project confidential context.

The receiving agent must encode this in its **existing valid Archcore rule format** and bind it to actual hooks/integrations. Do not assume the prose alone enforces anything.

## 19. Revised minimal implementation order (do not expand phase one)

**Phase A: Discover, don't migrate.** Inspect current directory/repo boundaries, existing AGENTS hierarchy, Archcore setup, GoalGuard status, and Vikunja version/API. Produce an inheritance/coverage
table (`global`, `APN`, `me`, `project`) and identify supported vs unsupported enforcement hooks.

**Phase B: One vertical slice.** Choose **one APN repository and one agent**. Keep the original MVP gate; connect one Vikunja project, fetch open tasks/priorities/dependencies, and return one
explainable next task. Demonstrate a scope-violating task is blocked.

**Phase C: Cross-project proof.** Add **one** second repository/context and verify that the global baseline applies while APN/me boundaries and local Archcore technical rules remain isolated. Validate
explicit override and resume after interruption.

**Do not** onboard every project, mirror documents across directories, build a weighted scheduler, add an agent daemon, or configure two-way sync until earlier gates pass.

### Additional acceptance tests

| ID | Scenario | Expected outcome |
|---|---|---|
| P01 | Two eligible tasks in distinct authorized projects with known priority | One deterministic cross-project recommendation with IDs/rationale |
| P02 | High-priority task blocked by incomplete dependency | Not selected; blocker identified |
| P03 | Agent asked to execute unapproved high-priority Vikunja task | BLOCK, no edits |
| P04 | Due-soon lower-priority task vs higher-priority nonurgent item | Explain deterministic urgency/priority decision under configured policy |
| P05 | Vikunja API unavailable or stale | Show degraded read-only mode; no scope-changing authorization |
| P06 | Agent working under APN tries to read protected `me` contents | Denied or withheld |
| P07 | Shared global policy plus project-specific Archcore constraint | Both effective; local rule cannot loosen global safety/scope boundary |
| P08 | Independent child Git repository does not inherit ancestor Archcore automatically | Explicit adapter supplies global/context refs or reports unsupported; never assumes inheritance |
| P09 | Human changes Vikunja priority | Ranking changes on refresh without editing AGENTS/Archcore documents |
| P10 | Interrupt and resume | One active focus item restored with checkpoint; no lost original status |

## 20. Updated receiving-agent assignment

> Extend the existing GoalGuard MVP handoff policy *only* with Vikunja-backed portfolio prioritization and explicit policy resolution across the established `project_stuff/APN`, `project_stuff/me`,
> and individual project hierarchy. First inspect the actual file tree, agent instruction discovery, Archcore roots and Vikunja API/version. Preserve current `AGENTS.md` structure and Archcore
> documents; prefer short references to canonical GoalGuard policy. Implement a read-only portfolio next-task path plus a blocking implementation handoff in one repository. Validate task
> priority/dependency handling and global/context/project rules with the tests above before expanding. Never add Knowledge Curator responsibilities, duplicate a task DB, or assert Archcore automatic
> parent inheritance without proving it. Clearly distinguish implemented controls from advisory instructions.

## 21. Change record (v1.2)

- Corrected the portfolio root from the placeholder `projects` to the user-specified exact folder name `project_stuff` everywhere in hierarchy examples and agent instructions.
- Retained the existing approved design direction: Vikunja holds mutable priorities, dependencies, order and task state; GoalGuard selects actionable work and enforces scope; Archcore exposes the
  appropriate rules; the Knowledge Curator remains separate.
- **No implementation is asserted:** this document is a handoff specification, and actual hierarchy resolution, API binding and enforcement remain subject to live-workspace inspection and tests.


## 22. Extension: Enterprise-Strategy hub-and-spoke coordination (v1.3)

### 22.1 Authority and project relationships

User-described topology (verify real paths and identifiers before configuration):

```text
project_stuff/
├── APN/
│   ├── Enterprise-Strategy/   # hub: shared strategic decisions and management plan
│   ├── UNC/                   # spoke (illustrative spelling; inspect actual directory)
│   └── SMC-Resiliency/        # spoke (illustrative spelling; inspect actual directory)
└── me/                        # isolated personal portfolio
```

**Do not replace or consolidate Enterprise-Strategy into GoalGuard.** Enterprise-Strategy remains the authoritative APN hub for strategic direction, approved shared interfaces, and cross-project
decisions. Spokes own implementation, local specifications, local MVP acceptance evidence, and project-specific ADRs. GoalGuard owns orchestration: check freshness, flag conflicts, route cross-project
proposals, prioritize authorized work using Vikunja, and enforce the approved MVP gate. Archcore surfaces the applicable constraints and local technical rules. Knowledge Curator is independent and is
not a task or change approval service.

Register hub/spoke relationships explicitly in an existing configuration mechanism, using stable project IDs, real repository roots, authoritative document references, and scoped access. No automatic
project discovery is a substitute for human confirmation of the relationship.

### 22.2 Required checks and bounded escalation

- **Session start / resume / implementation handoff:** retrieve the hub's current approved decisions relevant to the spoke; compare version or commit/ref/checksum against the spoke's acknowledged
  version; check the spoke MVP and current Vikunja task. Record a provenance-rich read receipt (project, hub reference, revision, timestamp, applicable decision IDs). Do not copy complete hub contents
  into every spoke.
- **At meaningful change boundaries:** recheck the hub when an approved shared interface, device-identity schema, inter-project dependency, rollout assumption, or external deadline might be affected.
  Do not poll on every sentence or every unrelated local code edit.
- **Cross-project impact proposal:** create a candidate decision with source project, impacted projects, evidence, proposed contract/dependency change, affected milestones, and requester. Mark REVIEW
  pending authorized approval at the hub; do not mutate shared contract or another project's scope.
- **Approved hub change:** hub records a versioned decision with effective date and affected projects; GoalGuard marks affected spokes stale until they assess and acknowledge the revision; related
  Vikunja tasks may be updated through a controlled, attributable action, not by silently replacing priorities.
- **No impact:** local spoke implementation proceeds under its project-level Archcore rules and GoalGuard MVP gate; no hub approval for routine fixes/refactoring/testing.
- **Unavailable hub:** cached, version-pinned decisions can support already-approved, non-cross-project work only if policy permits; changes potentially affecting shared contracts are REVIEW/BLOCK.
  Never claim latest revision was checked without connectivity.
- **Conflict:** don't resolve a disagreement by selecting the newest or longest document automatically. Present competing references and obtain the appropriate hub/owner decision.

**Cross-project inference:** propose possible relationships with cited source passages and confidence/status `candidate`; confirmed dependencies require corroboration or human approval before adding
Vikunja dependency relations. The AI must not create cross-project dependencies, merge MVPs, or assign hub authority to itself.

## 23. Extension: management plan → GoalGuard → Vikunja traceability

### 23.1 Distinct sources of truth

The user reports that Enterprise-Strategy contains a **Markdown project plan** also shared with management in **Excel**. The actual plan files, workbook, column names, content, and approval procedure
**have not been provided or inspected**; they must be discovered before designing field-level mapping. The spreadsheet is not automatically a live source of truth merely because it was circulated.

| Information | System of record | Authoritative behavior |
|---|---|---|
| Management-accepted objectives, commitments, milestone scope, target dates | Versioned, approved Enterprise-Strategy plan baseline (Markdown, subject to confirming actual approval source) | Changes require management/authorized owner decision; GoalGuard must not silently rewrite |
| Published management Excel workbook | A dated snapshot/export of a specified plan baseline, unless evidence establishes otherwise | Preserve issuance date, audience, workbook hash/version, baseline ID; no automatic reimport as task truth |
| Delivery authorization, MVP and approved changes | GoalGuard | Enforces scope/approval; references management milestone IDs rather than copying large plan sections |
| Executable tasks, assignee, operational priority, due date, dependencies, status | Vikunja | Live delivery state, with stable task/project IDs; cannot silently change management commitments |
| Technical specifications/architecture | Archcore/project repositories and approved hub decisions | Technical constraints, not a second backlog |
| Extracted provenance/evidence from Markdown corpus | Knowledge Curator | Read-only reference for governance; no auto-approval or task promotion |

If management actually treats Excel as the **editable authoritative plan**, identify that during discovery and establish a single sanctioned approval/update path; do not assume Markdown wins by
default. Never build an uncontrolled bidirectional Markdown ↔ Excel ↔ Vikunja synchronizer.

### 23.2 Minimal identity and mapping contract

Use existing plan IDs and existing Vikunja task custom fields/descriptions/labels if sufficient. Do not introduce a new database to duplicate Vikunja. Conceptual linkage:

```yaml
plan_baseline:
  hub_project: Enterprise-Strategy
  document_ref: '<existing-relative-plan-path>'
  revision: '<git-commit-or-approved-document-version>'
  approved_by: '<authorized-party/reference>'
  management_export_ref: '<issued-file/version/hash-if-known>'

milestone_link:
  milestone_id: '<stable ID in management plan>'
  milestone_revision: '<baseline revision>'
  delivery_project_id: '<registered UNC-or-SMC-project-ID>'
  vikunja_project_id: '<actual API ID>'
  vikunja_task_ids: ['<actual API task ID>']
  goalguard_mvp_id: '<approved MVP ID>'
  mapping_status: proposed # proposed | verified | superseded
```

Requirements:
1. **Discover:** inspect actual management plan, Excel snapshot metadata, existing IDs, Vikunja version/API, and current hub/spoke practices. Do not fabricate milestones or task fields.
2. **Baseline:** register management-approved plan revision and stable milestone IDs; where IDs are missing, propose a minimal non-destructive mapping and request confirmation before publishing.
3. **Link:** create or verify per-milestone references to existing Vikunja tasks/projects and GoalGuard MVPs. A management milestone may map to several tasks or more than one delivery project; don't
   force a one-to-one mapping.
4. **Track:** calculate milestone progress from verified task completion **and** the milestone's own acceptance evidence; percent of tasks closed alone does not prove milestone delivery.
5. **Reconcile:** surface discrepancies such as management target date vs Vikunja operational due date, missing tasks, delayed dependencies, changes in scope, unlinked deliverables, and completed
   tasks without evidence. A discrepancy generates an explicit reconciliation record; no silent overwrites.
6. **Change control:** operational reprioritization may update Vikunja without changing approved management commitments; changing a committed milestone/date/scope requires a versioned hub/management
   decision and a new published-plan revision when appropriate.
7. **Report:** produce a management status view/export keyed to the published baseline: milestone, owner, committed date, forecast date, status, evidence, blockers, related projects, and variance
   rationale. Preserve historical reports; label a new Excel export as a new version, not a retroactive replacement.

### 23.3 Worked flow (illustrative, not a claim about the existing plan)

Suppose the approved management plan contains milestone `M-UNC-01`, “Demonstrate discovery of one Cambium device,” linked to `UNC-MVP-001`. Vikunja has three corresponding execution tasks and a
separate SMC task that could unblock an interface. GoalGuard checks whether the latter is a **confirmed** dependency, proposes a link if not, ranks only eligible tasks, and reports completion only
when the milestone's acceptance evidence exists. If the forecast slips, GoalGuard flags the variance against the management baseline; it does not silently move the committed deadline in Markdown or
change the previously shared Excel file.

### 23.4 Archcore/AGENTS agent-facing rule extension

> For APN spokes, before implementation or changes to shared contracts, resolve the registered Enterprise-Strategy hub and acknowledge applicable approved hub decision revisions. Resolve the current
> management-plan milestone link, approved GoalGuard MVP, and live Vikunja task. Treat the issued Excel workbook as a management snapshot unless an explicit verified authority decision says otherwise.
> Do not treat task priority, agent inference, or a newer unapproved Markdown draft as permission to alter a management commitment. Report conflicts and stale references; route strategic or
> cross-project changes for REVIEW. Follow the existing local Archcore rules and limit checks to material change boundaries.

This rule should be installed by referencing existing canonical rules at the correct hierarchy levels. Verify `AGENTS.md` discovery and Archcore inheritance/tool support empirically. A rule alone is
advisory unless an executable gate is wired and tested.

### 23.5 Additional acceptance tests

| ID | Scenario | Required result |
|---|---|---|
| H01 | UNC handoff and hub contains a relevant newer approved interface decision | Warn or REVIEW stale contract; prevent conflicting shared-interface implementation |
| H02 | SMC agent proposes shared contract amendment | Hub review candidate with provenance; no silent mutation of UNC or hub |
| H03 | Routine isolated spoke bug fix | PROCEED without mandatory hub approval when approved MVP and technical checks pass |
| H04 | Hub unavailable and proposed change affects shared interface | REVIEW/BLOCK; no false assertion that latest hub decision was checked |
| H05 | AI infers possible UNC↔SMC dependency | Candidate only; do not create enforced Vikunja blocker without validation |
| H06 | Management baseline milestone linked to multiple Vikunja tasks | Correct stable traceability and task aggregation, acceptance evidence separate |
| H07 | Vikunja operational due date differs from issued plan commitment | Record variance and escalate per policy; do not rewrite management baseline |
| H08 | Excel exported from revision A, Markdown draft revision B is newer but unapproved | Preserve A as published baseline; label B draft; no silent change to commitments |
| H09 | Task set marked complete but milestone acceptance proof missing | No milestone completion declaration |
| H10 | APN spoke session attempts to import `me` project contents | Deny cross-context access |

### 23.6 Delivery sequence and hard scope ceiling

**Pilot only:** inspect Enterprise-Strategy's real plan and one published workbook reference; register Enterprise-Strategy, UNC, and SMC as a hub/spoke topology in existing configuration; implement
**read-only** plan-to-task traceability for *one* approved management milestone and *one* spoke, plus a read-only hub staleness check. Demonstrate H01, H03, H06–H09 before enabling writes. Keep
existing GoalGuard single-project MVP gate as the primary deliverable.

**Later, after pilot proof:** controlled hub impact approvals and Vikunja relation writes; second spoke coordination; versioned Excel export. AI-assisted dependency discovery remains a proposal-only
add-on, not a prerequisite for MVP delivery.

**Explicitly out of scope for first rollout:** duplicating Enterprise-Strategy documents; importing the entire Excel workbook as authoritative; continuous background crawling; bidirectional sync;
constructing a new PM UI; universal agent hook interception; automatic business-priority overrides; restructuring the existing Git/Archcore tree; changing Knowledge Curator functionality.

## 24. Change record (v1.3)

- Preserved v1.2's global/APN/me hierarchy, Vikunja task authority, Archcore rule resolution, and Knowledge Curator separation.
- Added Enterprise-Strategy as APN strategic hub for UNC and SMC Resiliency; GoalGuard coordinates and checks freshness but does not replace hub decision authority.
- Added formal management-plan-to-Vikunja traceability, document/export version semantics, reconciliation rules, Archcore agent obligations, and acceptance tests H01–H10.
- No actual plan Markdown, issued Excel workbook, Vikunja project, or installed integration has been inspected; examples and field mappings are proposals awaiting on-system verification.


## 25. v1.4 — Planning-system decision and migration contract

**Decision:** Pilot **Vikunja as the sole live operational planning/task system** and GoalGuard as its scope/portfolio policy engine. Do **not** retire the existing Enterprise-Strategy Markdown plan
until migration, baseline reconciliation, and management-report reproduction have passed. Do not build a new scheduling product inside GoalGuard.

| Record | Responsible system after cutover | Mutation policy |
|---|---|---|
| Original management-approved commitments (milestone ID, scope, date, authorizer, version) | Versioned immutable baseline registered and referenced by GoalGuard | New approved revision only; never overwrite history |
| Live milestones/tasks, priorities, dependencies, assignee, status, scheduling dates | Vikunja | Authorized operational updates via API/UI |
| Personal/internal earlier completion target | GoalGuard-owned lightweight metadata keyed to stable Vikunja milestone ID, unless verified native field supports this without conflating schedule semantics | Owner-editable; separate from management baseline |
| Forecast completion and confidence/evidence | GoalGuard calculation/record keyed to milestone ID | Recalculate on new task/estimate/dependency evidence; mark unknown if insufficient input |
| Actual completion | Vikunja status plus supporting acceptance evidence and recorded completion timestamp | Audit corrections, never infer milestone acceptance from task closure alone |
| Strategy, architectural rationale, approved cross-project decisions | Enterprise-Strategy Markdown / Archcore as applicable | Existing review/version policy |
| Management Excel | Generated export from the protected baseline + approved live status/forecast | Read-only issued snapshot; label generation time and baseline revision |

Vikunja's `start_date`, `end_date`, and `due_date` MUST NOT be arbitrarily overloaded as management deadline, internal target, and forecast. Verify the installed version's field semantics and API. If
a missing concept requires metadata, prefer a *small* GoalGuard extension table or namespaced task metadata with deterministic IDs; no parallel task database.

### 25.1 Controlled migration and retirement gate

1. Discover the **actual** Enterprise-Strategy Markdown plan, issued Excel workbook and approvals; record hashes, revisions, dates, and provenance. Unapproved drafts do not replace published
   commitments.
2. Extract one management milestone with stable ID, committed scope/date, acceptance evidence requirements, and owning hub/spoke. Reconcile discrepancies with the issued Excel before importing.
3. Check for an existing Vikunja project/task; **idempotently upsert/link** rather than generating duplicates. Verify parent/child projects, dependencies, priorities, and status semantics via the
   running Vikunja API.
4. Populate Vikunja as the live operational representation and register a protected, versioned management baseline reference. Do not remove the Markdown plan yet.
5. Export a management Excel report from registered approved baseline + Vikunja status/forecast; compare key rows, dates, identities and layout against the original management workbook. Do not claim
   exact reproduction until verified.
6. Obtain owner sign-off after reconciliation and round-trip testing. Only then retire **duplicate operational scheduling edits** in Markdown. Preserve original plan and issued workbooks as immutable
   provenance; keep strategy and rationale in Markdown.
7. Define rollback: stop new writes, restore previous mappings/source-of-truth flag, preserve audit trail, and keep existing plan accessible. Avoid two-way synchronization.

**During transition**, every record must carry `authority_state = legacy_draft | published_baseline | vikunja_operational` and `migration_status = proposed | reconciled | cutover | rolled_back`.
Conflicts are REVIEW, never silent last-write-wins.

## 26. v1.4 — Dual-deadline and forecast policy

| ID | Normative rule | Outcome |
|---|---|---|
| DATE-001 | Every management-facing milestone MUST preserve original approved deadline, approval reference and revision. | BLOCK unapproved baseline rewrite |
| DATE-002 | The user's **internal target** MUST be independently editable and may precede the commitment. | REVIEW if a proposed target is impossible/ambiguous |
| DATE-003 | Forecast MUST be independently recorded, with calculation assumptions, evidence timestamp and an `unknown` state. | Never invent a predictive date |
| DATE-004 | Changes to tasks/effort/dependencies MAY alter forecast or internal target, but MUST NOT modify the protected commitment. | BLOCK silent baseline edits |
| DATE-005 | GoalGuard MUST distinguish internal-target breach, management-baseline risk, and missed management commitment. | Distinct alerts and suggested actions |
| DATE-006 | Management reports MUST default to approved deadline, actual status, forecast, risk and evidence, without publishing private internal stretch targets unless explicitly requested. | No unapproved exposure |
| DATE-007 | Actual milestone completion MUST be backed by acceptance evidence. | BLOCK premature done state |
| DATE-008 | Date comparisons MUST use explicit timezone/date-only semantics and preserve issued-baseline values. | REVIEW ambiguous conversion |

**Example (illustrative only):** Management deadline `2026-12-15`; internal target `2026-12-01`; forecast `2026-11-27`; actual `null` until acceptance. A forecast of `2026-12-05` is an
**internal-target breach** but not necessarily a missed commitment; a forecast of `2026-12-18` is a **management deadline at risk**. An actual completion after December 15 is a confirmed **miss**. Use
explicit milestone acceptance, not task counts, to determine delivery.

**Scheduling calculation:** Start with a transparent rule based on remaining estimated effort, working days/capacity available, verified blocking dependencies and configurable buffer. Provide
explanation and allow human override. If estimates/capacity are absent, report `forecast=unknown`, not a fabricated number. Never automatically reprioritize unrelated projects or rewrite approved
target dates.

## 27. v1.4 — FOSS platform choice and exit gate

**Default:** Vikunja, conditional on a real integration pilot. **Fallback candidate:** self-hosted OpenProject Community if the pilot proves that baseline tracking, dependency semantics, management
reporting, or date management require a disproportionate custom subsystem. No platform switch based on hypothetical concerns.

Run a single-milestone proof covering: immutable approved deadline; separately stored internal target; current forecast; actual evidence; UNC↔SMC hub-owned dependency; ranking of next eligible Vikunja
task; and Excel export. Record unsupported native fields, API behavior, effort and any edition/license limitations. Prefer verified FOSS functions; do not assume feature parity or paid-only features
are available.

**Switch evaluation threshold:** If GoalGuard must implement its own general-purpose milestone scheduler, custom field platform, or report-management UI to compensate for Vikunja, halt and compare
OpenProject Community using the same fixture. A small metadata mapping and focused Excel exporter do **not** alone justify switching.

## 28. v1.4 — Archcore / agent enforcement addition

Insert the following *reference rule* into the **existing** applicable Archcore/AGENTS.md hierarchy after discovering actual filenames, Git boundaries and precedence. Do not create duplicate full
policies in every project:

> For project delivery, resolve GoalGuard's approved MVP, relevant Enterprise-Strategy hub decisions and the live Vikunja task before modifying code. Vikunja is the source of truth for operational
> planning after the signed-off cutover; management commitments are versioned protected baselines, not editable task due dates. Distinguish protected deadline, owner's internal target, forecast, and
> evidenced actual completion. When an implementation change conflicts with approved scope, changes a protected baseline, introduces an unapproved cross-project dependency, or relies on
> stale/unavailable authority, stop the affected action and request GoalGuard REVIEW/BLOCK. Do not count planning as delivered work or self-approve scope changes.

Agent hook behavior MUST be tested against **installed client versions**. Do not assume Codex and Claude Code expose identical hook event names or that prompts/AGENTS rules guarantee pre-execution
enforcement. Prefer executable checks at verified handoff and supported pre-action boundaries; ensure the documented failure mode is safe for material scope changes.

## 29. v1.4 — Acceptance tests, rollout ceiling, and change record

| ID | Test | Pass criterion |
|---|---|---|
| D01 | Published Markdown milestone and issued Excel differ | Flag discrepancy; preserve both; REVIEW before cutover |
| D02 | Same milestone imported twice | One Vikunja identity, no duplicate tasks |
| D03 | Original management deadline edited via operational UI | Protected baseline unchanged; audit and discrepancy raised |
| D04 | Internal target earlier than protected deadline | Both stored independently and round-trip correctly |
| D05 | Forecast passes internal target but not baseline | Internal-target alert distinct from baseline risk |
| D06 | Forecast passes protected baseline | Management commitment risk raised, deadline not moved |
| D07 | No effort estimate or capacity available | Forecast `unknown`, not guessed |
| D08 | Vikunja subtasks completed without acceptance evidence | Milestone remains unaccepted |
| D09 | Excel export generated | Approved dates, revision, status, forecast and evidence traceable; original snapshot retained |
| D10 | Spoke task requires hub-updated contract | Stale spoke stops/reviews while unrelated authorized fix continues |
| D11 | Reconciliation or cutover fails | Safe rollback with original Markdown/export intact |
| D12 | APN agent accesses unrelated private `me` project | Access denied and no data leaked |

**Hard scope ceiling for next agent:** One approved Enterprise-Strategy milestone, one connected Vikunja project, one coding-agent adapter, one owner-controlled internal target, and one management
export sample. Produce an evidence-backed PASS/FAIL table before onboarding the second project or retiring Markdown operational planning. Do not simultaneously build predictive AI scheduling,
continuous sync, portfolio optimization, or a custom dashboard.

**Version 1.4 change record:** Adds conditional Vikunja migration/cutover, protected baseline ownership, separate internal target and forecast, original Excel-to-generated-Excel transition, FOSS tool
selection gate, Archcore instructions and tests D01–D12. All prior rules remain unless expressly superseded by §25. **Implementation status: not verified or deployed.**


## 30. v1.5 — GoalGuard packaging and skill hierarchy

**Purpose:** Define how a single reusable GoalGuard implementation governs many repositories without cloning its code or writable database into every project. This is a *proposed contract*, not a
claim about existing folders or current installed skill semantics.

1. **One canonical GoalGuard skill/code package** (location discovered under the user's existing skill convention; do not invent a new top-level `skills/` tree). It contains skill instructions, policy
   evaluator, optional MCP/API adapter, Vikunja adapter, CLI, schemas, and tests. Updating it updates behavior for all opted-in projects.
2. **One global governance configuration** at the verified `project_stuff` root, with immutable rule IDs and shared schema references. Root path is logical; discover absolute location on disk.
3. **One context configuration** under each governed boundary (`APN`, `me`), carrying access constraints and portfolio settings, not copied root policy text.
4. **One project-local `.gg/` governance record** per participating project, holding references and small portable, reviewable project-specific records, not a second task database.
5. **Optional local `.gg/` at `Enterprise-Strategy`** identifies hub authority and registered spokes; it must not become a second operational schedule.

**Suggested hierarchy (illustrative, not a creation instruction):**

```text
<existing-skills-root>/
  goalguard/                       # ONE canonical skill/package (verify actual convention)
    SKILL.md                       # how an agent invokes it
    policy/                        # stable global policy + rule IDs
    schemas/                       # versioned JSON schemas
    bin/                           # gate, status, link, check (only proven commands)
    tests/

project_stuff/
  .gg/                             # root-wide policy pointers and portfolio registration
    config.yaml
    portfolios.yaml
  AGENTS.md                        # existing thin pointer, only where applicable
  APN/
    .gg/
      config.yaml                  # work partition, permissions, hub pointer
    Enterprise-Strategy/
      .gg/
        project.yaml               # hub role, projects and strategy references
        links.yaml                 # approved hub/spoke relations
    UNC/
      .gg/
        project.yaml               # project ID, approved MVP revision, hub reference
        mvp.yaml                   # signed/approved MVP contract only if existing model fits
        decisions.jsonl            # append-only scope decisions (if project-owned)
        deferred.yaml              # optional parked ideas, NOT knowledge corpus
    SMC-Resiliency/
      .gg/...
  me/
    .gg/
      config.yaml                  # personal partition; must not ingest APN data
    <personal-project>/.gg/...

<canonical-data-root>/goalguard/   # external, durable, writable state (discover policy)
  cache/ or <canonical-cache-root>/goalguard/  # regenerable; separate from durable state
```

**Naming note:** `APN`, `me`, and `project_stuff` were supplied by the user. All child paths in this tree are examples until surveyed. The `.gg/` name is a proposed preference pending conflicts with
existing tools or repository policy. The exact canonical DATA/RUNTIME/CACHE roots must follow existing workspace policy; do not presume a physical path.

## 31. v1.5 — `.gg/` file contract and data ownership

| Proposed record | Scope | Owner | Persist? | Guardrail |
|---|---|---|---|---|
| `config.yaml` | root/context | GoalGuard operator | Git if non-secret | Only overrides/refs; no duplicate complete policy |
| `portfolios.yaml` | root | GoalGuard operator | Git | Project identifiers, access partitions; not task priority copies |
| `project.yaml` | project | project owner | Git | IDs, hub, baseline reference, Vikunja project ID; no credentials |
| `mvp.yaml` | project | human owner through controlled action | Git (after approval) | Version, criteria, exclusions, approval ID; edits require audited review |
| `links.yaml` | hub | human-approved GoalGuard coordination | Git | Explicit dependency/interface references; proposed AI links remain pending |
| `decisions.jsonl` | project or global durable store | GoalGuard append-only service | As policy permits | IDs, time, rule, actor, prior/new revision, rationale, hash; never rewrite history |
| `deferred.yaml` | project | GoalGuard | Git optional | Parked ideas only; no task or deadline authority |
| `state.db`, leases, tool events, tokens, caches, logs | external runtime/data | GoalGuard runtime | NO repo commit | Dedicated storage with permissions, backup, rotation and schema migration |

**Single-authority constraints:** Vikunja alone holds *live task state* and its native priority/due date/relation/status fields. Protected management baseline must retain an immutable revision and
approval evidence (stored in GoalGuard durable state and/or versioned baseline artifact); project `.gg/` may hold its ID/hash, not another editable deadline. Owner internal targets and forecasts may
live in GoalGuard's minimal metadata store keyed by stable Vikunja task/milestone IDs. Archcore owns design/technical documents. Enterprise-Strategy owns approved cross-project decisions. Knowledge
Curator may read published documents but has no scope-write permissions.

**Secrets and privacy:** Do not put API keys, private work details in personal context, credentials, or raw session transcripts in version control. Separate APN/me indexes, credentials and access
permissions. Use strict path resolution to prevent symlink traversal and accidental cross-boundary reads. Allow opt-out from registration for unrelated repositories.

## 32. v1.5 — Resolution, startup and ongoing enforcement

1. Detect current repository root and logical owner partition (`APN` vs `me`) using a normalized, tested path; reject ambiguous/nested/symlink escapes.
2. Load verified canonical policy package and nearest registered `.gg/` references in order: root → partition → project; load Enterprise-Strategy hub contract only when a hub relationship is declared
   and relevant.
3. Resolve current approved MVP revision and matching Vikunja task/management milestone; validate authorization and any stale hub revision. A missing or contradictory record is `REVIEW` or `BLOCK` for
   the affected work.
4. Present one recommended next task; do not turn the recommendation into approval to expand MVP.
5. Validate material tool actions through actual supported coding-client lifecycle integrations. Before changing code, require an action-to-criterion mapping; if uncertain, request review.
6. On context compaction/session resume, revalidate the authorization revision and hub revision, rather than trusting earlier conversational summaries.
7. On completion, attach acceptance evidence and audit decisions; never infer completion from planning or task-count changes.

**Enforcement honesty:** Neither `.gg/` nor `SKILL.md` nor `AGENTS.md` can themselves guarantee hard blocking. Audit the installed Codex and Claude Code versions' *real* hook/plugin boundaries and
their failure behavior. A tool path with no supported pre-action interception is advisory unless implemented through a controlled wrapper or sandbox. Do not claim every chat token can be
deterministically classified in real time. This design leaves ChatGPT brainstorming unrestricted and applies gates to coding-agent work.

**Conflict order:** Explicit owner-approved scope/commitment > canonical GoalGuard controls > partition constraints > project scope > Archcore in-scope implementation guidance > Vikunja operational
data > agent suggestion. Technical-scope conflicts require `REVIEW`, not overriding the relevant Archcore source.

## 33. v1.5 — Lifecycle, backups, migration and repository hygiene

- **Enroll:** `goalguard init --dry-run` (illustrative CLI only, not guaranteed implemented) inventories existing `.gg/`, `.archcore/`, `AGENTS.md`, git boundaries, policies and conflicting names. Do
  not create files until approved and diff-reviewed.
- **Register:** Stable project ID, type (`hub`/`spoke`/`standalone`), owning portfolio, Vikunja IDs, and optional hub relationship. Never auto-discover confidential sibling projects into an agent
  session.
- **Approve:** Version MVP/baseline and attach human approval provenance; maintain append-only changes. Disallow an agent silently rewriting approved files.
- **Operate:** Externalize volatile state; use atomic writes, locking, crash-safe recovery, audit/event rotation; read-only health checks must not mutate authoritative state.
- **Move/rename:** Stable IDs survive moving directories; verify mapping before changing persisted references. Reject two roots claiming same project ID.
- **Unregister:** Explicit owner action with archival/backup preservation and no silent deletion of decisions or protected baselines.
- **Backup/restore:** Include authoritative approved records, durable state, schema version, Vikunja mapping and hashes; exclude regenerable caches and secrets. Test restore and incompatibility
  handling.

**Repository contract:** Default `.gg/` project documents are small and reviewable. Add narrowly scoped `.gitignore` entries for local state and temporary artifacts (not `/.gg/` wholesale). Protect
approval records with repository permissions and/or signed immutable audit history where required; Git alone does not prove who approved a change.

## 34. v1.5 — Minimal pilot and test gates (new tests F01–F14)

| ID | Test | Pass condition |
|---|---|---|
| F01 | Root/partition/project nested resolution | Correct effective policy; source paths and hashes visible |
| F02 | Separate `APN` and `me` | A project in one cannot read or reprioritize the other without explicit authority |
| F03 | Project has no `.gg/` | Non-mutating discovery allowed; scope-changing work blocked pending enrollment/authorization |
| F04 | Independent Git repository | No assumption that parent Archcore or AGENTS.md is auto-inherited; adapter applies policy explicitly |
| F05 | Hub-spoke registration | UNC/SMC sees current relevant Enterprise-Strategy revision, not unrelated hub records |
| F06 | Hub revision changes mid-session | Relevant next action revalidated; stale contract invokes REVIEW |
| F07 | Agent adds feature outside MVP | Tool action blocked where enforcement is supported; alternative uncontrolled paths documented |
| F08 | Edit Vikunja priority | Next-task ranking changes without rewriting `.gg/` or Archcore task priorities |
| F09 | Alter protected baseline via proposed local edit | Unauthorized change rejected, original preserved, audit emitted |
| F10 | Crash during approval record write | No partial authoritative state; deterministic recovery |
| F11 | Rename project directory | Stable registered identity and task links survive or REVIEW if ambiguous |
| F12 | Malicious symlink/nested path | Prevent cross-partition policy/data access |
| F13 | Git status after normal operation | No DB/log/cache/token pollution; only authorized config changes visible |
| F14 | Skill absent/hook unavailable | State accurately reported as advisory/unprotected; never falsely assert hard enforcement |

**Phase ceiling remains unchanged:** one real Enterprise-Strategy milestone, one spoke project, one coding-agent adapter and one Vikunja integration. First deliver a read-only resolution and gate
demonstration; do not implement every optional file/command above unless required to pass the pilot. A separate plan may be produced for broader rollout only after evidence-based approval.

## 35. v1.5 — Coding-agent kickoff and definition of done

**Kickoff instruction:** Read §§1–35 of this specification, treating §§25–35 as later extensions that override older planning-authority or layout assumptions only where explicitly contradictory.
Inspect the live existing GoalGuard skill or prototype, Archcore layout, agent instructions, repository boundaries and real Vikunja version/API. Produce a factual inventory and minimal delta proposal.
Do not assume paths, install more tooling, introduce a second planner, or modify all repositories.

**First executable slice:** Register *one* spoke project and its Enterprise-Strategy hub reference; resolve root/partition/project policy, approved MVP and one Vikunja task; demonstrate a permitted
change and blocked out-of-scope change using one actually supported coding-agent enforcement path. Link one management milestone to its protected baseline and internal target; produce one traceable
report sample. Report which controls are deterministic vs AI-advisory and provide tests/evidence.

**Deliverables:** (a) inventory and decision table for proposed `.gg/` structure, (b) minimum implementation diff, (c) runnable test results F01–F14 as applicable to pilot, (d) identified unenforced
tool paths, (e) rollback notes, and (f) next-phase recommendation subject to owner approval.

**Version 1.5 change record:** Adds canonical skill vs per-project configuration separation; proposed `.gg/` file map; explicit workspace resolution and security isolation; lifecycle and persistence
rules; fourteen acceptance tests and kickoff instructions. Existing v1.4 design remains authoritative except for these additions. **No existing skill installation, hooks, folder contents or Vikunja
records were validated by authoring this document.**


## 36. v1.6 — Existing project maps are first-class integration inputs

**New owner-provided workspace convention:** Individual projects already maintain a `code-map.toml` containing an index of code under `scripts/`, and a `target-map` describing the targets to be
achieved. The user corrected the code map extension to **TOML**. The filename, serialization format, keys, mutation process, and actual paths for **`target-map` are not yet established**. The
implementation agent MUST discover them from real repositories before parsing or writing. Do not manufacture a `target-map.yaml`/`.toml` filename or schema.

**Compatibility principle:** GoalGuard MUST integrate with the current `target-map` convention rather than introduce a second independently maintained target catalog under `.gg/`. `code-map.toml` is
supporting implementation evidence, not a work queue or scope authority. Keep the source documents in their existing locations unless the owner explicitly approves a migration.

| Artifact | Proven/current purpose | GoalGuard relationship | Writable by GoalGuard initially? |
|---|---|---|---|
| Existing `target-map` (discover exact path and format) | Project targets/outcomes | Read targets; match target IDs to approved MVP acceptance criteria, Vikunja tasks and management milestones; flag conflicts and unmapped records | **No** — read-only in pilot |
| Existing `code-map.toml` | Catalog/index of scripts under `scripts/` | Read for traceability and impact analysis; optionally identify which script supports a selected target | **No** — read-only in pilot |
| Project `.gg/project.yaml` or equivalent existing registry | GoalGuard identity/links | Store only stable pointers, mapping IDs, source paths and source revision/hash; NOT duplicate target contents | Only through reviewed/authorized config changes |
| Vikunja | Live task data | Priority, status, task order, due dates and dependencies remain authoritative here | Via existing API permissions/policy |
| Approved GoalGuard MVP and immutable baseline | Scope/approval authority | Determine which targets are committed and permitted to implement | Only after authenticated owner approval |
| Enterprise-Strategy | Approved APN hub decisions and management commitments | Resolve strategic dependencies/constraints; do not promote spoke targets to management commitments automatically | Via separate hub change control |

### 36.1 Target-map precedence and conflict behavior

1. **Inventory before interpretation.** Locate the target map and `code-map.toml` for the selected pilot project; inspect `AGENTS.md`, Archcore rules, script-map generation tooling, edit ownership,
   history and any documented stable IDs. Produce a real field-mapping table. Do not invent paths or IDs.
2. **Separate desired targets from approved commitments.** An entry in `target-map` is a *candidate or recorded project target*, not self-approving scope. When it maps to the current owner-approved
   GoalGuard MVP, it may be executed; if not, classify it as PARK or REVIEW as appropriate. An approved baseline wins on scope conflicts.
3. **Reference, do not mirror.** `.gg/` stores a reference to `target-map`, plus optional stable target-to-MVP/task IDs and last-seen source revision; Vikunja continues to own live work status. Avoid
   copying target descriptions, priorities, dates or dependencies into duplicate editable records.
4. **No silent bidirectional sync.** Detect changes to `target-map` and show a proposed reconciliation diff. If the map is updated by an existing approved tool, allow that tool to remain its writer.
   GoalGuard MUST NOT overwrite or auto-normalize the original map during the pilot.
5. **Management and personal separation.** A spoke target cannot change Enterprise-Strategy's approved management milestone, baseline deadline, or internal target through file synchronization.
   Likewise, APN targets must not be exposed to `me` projects.
6. **Code-map is an index, not an implementation permission.** The presence of a script in `code-map.toml` never justifies an out-of-scope feature. Changes under `scripts/` must still pass GoalGuard's
   MVP gate. If the existing build tooling regenerates `code-map.toml`, use that documented flow rather than maintaining it manually.
7. **Unavailable or ambiguous mapping:** Do not invent IDs, merge unrelated targets, or block all read-only discovery. Return REVIEW for affected authorization and continue unaffected approved work.

### 36.2 Minimum mapping contract (conceptual, not a new mandated file)

For a single pilot target, the agent must be able to resolve: `project_id`, `target_source_ref`, `target_id` **if the map already provides one**, `target_source_revision`, `mvp_baseline_id`,
`acceptance_criterion_id`, and `vikunja_task_id` **where the link has been approved**. Optionally link an existing `code-map.toml` script identifier/path as evidence of implementation. Where the
source lacks stable identifiers, propose the smallest safe ID strategy and seek owner approval instead of changing the target-map schema automatically.

### 36.3 v1.6 acceptance tests (M01–M08)

| ID | Test | Passing evidence |
|---|---|---|
| M01 | Detect existing maps | Agent reports the actual `target-map` name, format, path, and `code-map.toml` location without guessing |
| M02 | Target traceability | One real target maps to an approved MVP criterion and a Vikunja task (or an explicit unresolved-mapping REVIEW) |
| M03 | Non-authoritative target | A new map entry outside approved MVP cannot authorize coding by itself |
| M04 | Read-only compatibility | Running the pilot does not rewrite either source map or create a duplicate target catalog |
| M05 | Changed map | Changed source revision produces a reconciliation proposal, never an unapproved scope change |
| M06 | Script impact | Existing `code-map.toml` reference can inform affected-script identification without overriding scope |
| M07 | Hub boundary | Spoke target cannot silently update Enterprise-Strategy commitments or dates |
| M08 | One authoritative task record | Vikunja remains the source for live task priority/status; no competing `.gg/` task state is introduced |

**Pilot ceiling unchanged:** Do not turn the target-map adapter into an automatic bidirectional synchronization platform. The first milestone is read-only discovery and one valid traceability link.
Any proposal to have GoalGuard *maintain* target maps must come **after** evidence of their schema, current generator/owner, and a specific problem that read-only integration cannot solve.

**Version 1.6 change record:** Integrates the pre-existing `target-map` and `code-map.toml` conventions without redesigning them. This addition refines v1.5 file ownership and pilot requirements;
§§1–35 otherwise remain unchanged. Neither map was provided for inspection in this conversation, so exact path, schema, naming and write ownership are explicitly unverified.


## 37. Hierarchical `.gg/` storage, portable snapshots, and restore contract (v1.7)

**Authoritative folder name:** `project_stuff` (lowercase with underscore), **not** `xproject_stuff` or `projects`. The actual absolute path and case-sensitive spellings of child directories must be
discovered on disk. `.gg/` is a proposed contract, not a preapproved mass migration.

### 37.1 Proposed minimal hierarchy

```text
project_stuff/
├── .gg/                         # Global governance, registry, recovery catalog
│   ├── config.yaml
│   ├── policy.yaml
│   ├── portfolios.yaml
│   └── snapshots/manifest.json  # Child references, not task copies
├── APN/
│   ├── .gg/
│   │   ├── config.yaml
│   │   ├── projects.yaml
│   │   ├── priorities.yaml      # Rules, not Vikunja priority values
│   │   └── snapshots/manifest.json
│   ├── Enterprise-Strategy/
│   │   └── .gg/
│   │       ├── project.yaml
│   │       ├── hub.yaml
│   │       ├── links.yaml
│   │       ├── mvp.yaml         # If an approved MVP exists
│   │       ├── mappings.yaml
│   │       ├── decisions.jsonl
│   │       └── snapshots/
│   │           ├── manifest.json
│   │           └── vikunja.json
│   ├── UNC/
│   │   └── .gg/
│   │       ├── project.yaml
│   │       ├── mvp.yaml
│   │       ├── mappings.yaml
│   │       ├── decisions.jsonl
│   │       ├── deferred.yaml
│   │       └── snapshots/
│   │           ├── manifest.json
│   │           └── vikunja.json
│   └── SMC-Resiliency/
│       └── .gg/                 # Same project layout as UNC
└── me/
    ├── .gg/
    │   ├── config.yaml
    │   ├── projects.yaml
    │   ├── priorities.yaml
    │   └── snapshots/manifest.json
    └── <personal-project>/.gg/  # Same project layout as UNC
```

All listed names are proposals; create only files needed for a validated pilot. The directories above are **logical illustrations**, not verified on-disk locations. Existing `AGENTS.md`, Archcore
configurations and project structure take precedence over inventing parallel conventions.

### 37.2 File ownership and precedence

| File | Ownership and purpose |
|---|---|
| Global `config.yaml`, `policy.yaml`, `portfolios.yaml` | Inheritance pointers, stable policy IDs, portfolio registry; no live task copies |
| Portfolio `projects.yaml`, `priorities.yaml` | Project membership and prioritization *rules*; no duplicated task status or priorities |
| Project `project.yaml` | Stable project identity, portfolio affiliation, Vikunja mapping and schema version |
| `hub.yaml`, `links.yaml` | Hub registration, approved cross-project relationships, revision acknowledgments |
| `mvp.yaml`, `decisions.jsonl`, `deferred.yaml` | Approved scope/acceptance criteria, append-only approvals, parked features |
| `mappings.yaml` | References to existing `target-map`, `code-map.toml`, management milestones, Vikunja IDs; no duplicate target-map catalog |
| `snapshots/vikunja.json` | Versioned portable export of task *data*, not a second editable operational task store |
| `snapshots/manifest.json` | Snapshot time, schema/format version, source instance, export completeness, checksum, records/counts, child references where applicable |

**Source of truth:** Vikunja owns current task execution state while available; GoalGuard owns authorization, scope approvals, internal targets, baseline revisions and cross-project policy;
Enterprise-Strategy owns approved strategic decisions; Archcore owns technical rules; Knowledge Curator owns Markdown knowledge curation. Source-of-truth changes must be explicitly approved, never
inferred from a newer file timestamp.

### 37.3 Portable snapshot format and hierarchy

1. Project snapshots are the **single stored copy** of that project's exported task entities. Include stable portable IDs, original provider IDs, task titles and descriptions, completion/status,
   priority, due/start/end dates, relationships, milestones, status timestamps, and mapping/provenance where the API exposes them. Preserve internal targets, approved management baseline links and
   forecast metadata from their actual authoritative GoalGuard records as *referenced supplementary data*, without falsely attributing them to Vikunja-native fields.
2. Capture cross-project dependency edges in an approved global/portfolio relationship index or referenced manifests; do not reproduce each external project's full task payload in every child project.
3. APN/me snapshot manifests reference child project snapshots; global manifest references portfolios and checksums. A reader can reconstruct the hierarchy by traversing manifests. Guard against
   cycles, duplicate portable IDs, broken references and missing files.
4. Version the portable export schema independently from Vikunja's native schema; record export time (UTC), source version and completeness. Retain last-known-good snapshots atomically, validate
   checksums, and never replace a good snapshot with a partial/failed export.
5. Never export API tokens, secrets, user credentials, private session state, or unnecessary personal information. Apply correct APN/me access separation; determine whether attachments, permissions,
   comments and users require additional export or a separate instance-level backup before claiming complete disaster recovery.
6. `.gg/` committed records must be small, reviewable and free of secrets; large data, sensitive exports, caches and temporary write files must use the established canonical DATA/RUNTIME/CACHE policy.
   A `.gg/` manifest may point to secured external snapshot payloads when version-control storage is inappropriate. Portability requires a documented bundle/export path that copies all referenced
   data.

### 37.4 Restore and outage behavior

- When Vikunja is offline, use the most recent verified snapshot for **read-only visibility**, prominently showing its age and partial-data warnings. Do not silently mark tasks complete, reprioritize
  work, or authorize unapproved scope based on stale data.
- Provide a dry-run restore command that validates schema, hashes, IDs, references, and complete dependency graph *before* touching a test destination. Default to no-write; a deliberate operator
  approval is required for migration/restore.
- Restore into a **clean test instance** first; map source portable IDs to newly allocated provider IDs, reconstruct task relations, and verify record counts, dates, priorities, dependencies and
  milestone links. Idempotent re-import must not duplicate tasks.
- Restoring to a live existing instance requires conflict detection, explicit reconciliation and backup, not last-write-wins. The importer must be portable enough that a provider-neutral intermediate
  export can be mapped to an alternate FOSS PM system without relying exclusively on Vikunja-specific IDs.
- An export is **not** proof of restore viability. Do not declare a recovery feature delivered without a verified restore test.

### 37.5 Minimum pilot gates (do not widen rollout)

| ID | Acceptance test |
|---|---|
| S01 | Discover actual `project_stuff` root and applicable existing Archcore/AGENTS.md conventions; no fabricated paths |
| S02 | Project snapshot contains real mapped tasks, dates, priority, status and dependency references, with schema/version and checksum |
| S03 | Parent manifests reference the project snapshot without duplicating task entities |
| S04 | Partial export is rejected without replacing the last-known-good snapshot |
| S05 | With Vikunja unavailable, verified read-only state is accessible with snapshot freshness warning |
| S06 | Dry-run and clean-test-instance restore recover task relations and stable mappings without duplicates |
| S07 | APN project data is not exposed through `me` manifests or agent access without authorization |
| S08 | Existing `target-map` and `code-map.toml` are discovered and read, not rewritten or re-schematized during pilot |

**Pilot ceiling:** First implement one project-level snapshot/export, one parent manifest, and one tested dry-run/clean-instance restore for an authorized APN pilot task. Do not build a general
synchronization platform, modify every project, or promise complete Vikunja server disaster recovery. This document supersedes v1.6 for handoff; runtime behavior remains unimplemented until validated.
