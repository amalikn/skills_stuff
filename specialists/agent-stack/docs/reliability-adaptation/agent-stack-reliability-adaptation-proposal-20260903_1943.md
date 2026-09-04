Title: Agent Stack reliability adaptation proposal
Category: evidence-and-proposal
Status: proposed
Scope: An evidence-triggered, safety-preserving adaptation backlog drawn from the reusable reliability mechanisms identified in the 25-repository external survey
Last reviewed: 20260903_2014
Summary: No external project should be adopted as Agent Stack's runtime. The mechanisms below are a deferred, evidence-triggered backlog; Agent Stack is currently in field use, where existing records
  must reveal a real failure before any new control is designed.

# Agent Stack reliability adaptation proposal

## Contents

- [Decision requested](#decision-requested)
- [Scope and non-goals](#scope-and-non-goals)
- [Assessment basis](#assessment-basis)
- [Current project state and sequencing](#current-project-state-and-sequencing)
- [Comparison of all repositories](#comparison-of-all-repositories)
- [Verified upstream adaptation map](#verified-upstream-adaptation-map)
- [Target state](#target-state)
- [Phase 1 — portability and execution receipts](#phase-1--portability-and-execution-receipts)
- [Phase 2 — legal hand-offs](#phase-2--legal-hand-offs)
- [Phase 3 — post-dispatch verification](#phase-3--post-dispatch-verification)
- [Phase 4 — operator-controlled access and action authorization](#phase-4--operator-controlled-access-and-action-authorization)
- [Phase 5 — evidence-gated learning](#phase-5--evidence-gated-learning)
- [Invariants and failure behaviour](#invariants-and-failure-behaviour)
- [Validation plan](#validation-plan)
- [Rollout, rollback, and deferred work](#rollout-rollback-and-deferred-work)
- [Acceptance criteria](#acceptance-criteria)
- [Sources](#sources)

## Decision requested

Keep the five mechanisms as a **deferred research backlog**. Do not select an implementation candidate now. Agent Stack's live work is operator-controlled field use: capture real routes, persona
notes, gaps, and outcomes; then make a separate, evidence-backed decision only if a repeated, material failure appears. This document does not modify routing, persona authority, runtime installation,
or operator permissions. It is a proposal, not an architectural decision; an accepted decision belongs in `.archcore/`.

The order below is a dependency map for a future approved change, not a delivery sequence. Existing evidence must establish the missing fact first; only then may an operator approve a narrow plan and
its validation fixture. A check that scans an imagined problem is not a reliability control.

## Scope and non-goals

Agent Stack is a portable prompt-layer library, not an agent runtime. Its existing strengths are declarative ownership, precedence rules, deterministic gate closure, source-aware research, and a
frozen routing evaluation corpus. Its safety model excludes autonomous loops, background agents, daemons, implicit persistent state, and material external commitments without explicit operator
authority.

This proposal adapts only mechanisms that survive removal of an upstream project's server, scheduler, web UI, database, worker fleet, or autonomous goal loop.

It does not add:

- a daemon, scheduler, server, background task queue, or autonomous goal loop;
- automatic retries, resumption, re-dispatch, self-promotion, or installation;
- an agent ability to approve its own access request, change its own permissions, or authorise a material external action;
- a requirement to use multiple personas for otherwise narrow work; or
- a second routing engine that could drift from `routing.toml` and `close_route.py`.

## Assessment basis

The assessment compares a project only against Agent Stack's intended scope. A mature SDK or a local-agent workspace can be better at runtime orchestration while still being a worse fit for this
project. “Adapt” means copy the bounded mechanism into Agent Stack's declarative, operator-controlled model; it never means install the upstream framework.

The earlier survey is retained as a research lead in [external-orchestrator-survey-20260903_1849.md](external-orchestrator-survey-20260903_1849.md); this document normalises its findings into an
explicit per-repository table with direct repository links. Repository existence and default branches were refreshed on 2026-09-03. Exact star counts, release cadence, and undocumented implementation
details are intentionally not decision inputs here.

## Current project state and sequencing

Agent Stack is a prompt/source library with a small maintenance toolchain, not an agent runtime. Its product is measured routing integrity: personas hold judgement contracts; skills hold repeatable
procedures; `routing.toml` declares the catalogue; and `close_route.py` deterministically closes only finite route constraints. The model still judges task meaning, primary owner, and gate truth.

The project is in **FIELD USE**. Six field-log entries across three projects exist, the capability-gap log is empty, and the evidence is intentionally below the ten-entry minimum at which
`scripts/propose_evolution.py` may make a proposal. Those entries also contain sparse dispatch, return, token, and outcome data. They are useful instrumentation feedback, not a feature mandate.

The following evidence mechanisms already exist and must be extended rather than duplicated:

- `scripts/field_log.py` records route mode, owner, participants, skills, gates, closure change, dispatch/return facts, estimated tokens, run directory, and operator outcome when supplied.
- `scripts/persona_note.py` writes a project-local run `MANIFEST.json` with dispatched/returned participants, declared gaps, completion state, and raw persona notes; it also appends declared gaps to
  `evals/capability-gaps.jsonl`.
- `scripts/propose_evolution.py` reads those records and produces proposals only; it never edits the catalogue and suppresses proposals below ten field entries.
- `scripts/qualify_runner.py` and the runner-qualification specification already bind an evaluation run to its provider, model, runner, command, harness, corpus, and contract provenance. That receipt
  is for evaluation runs, not a general-work logging format.

| Candidate                 | Evidence trigger before a design is permitted                             | Existing surface to inspect first               | Explicit boundary                          |
| ------------------------- | ------------------------------------------------------------------------- | ----------------------------------------------- | ------------------------------------------ |
| Harness capability matrix | A reproducible install/runtime portability defect or an unverifiable      | `manifest.yaml`, install validator, and runner  | Do not invent product limits or a          |
|                           |   harness claim affects field use.                                        |   qualification receipts.                       |   duplicate receipt log.                   |
| Legal hand-off contract   | Recorded multi-persona work shows an unknown, missing, or wrongly         | `routing.toml`, route manifests, and            | Do not introduce a second persona model or |
|                           |   consumed input/output caused a real decision problem.                   |   frozen/replay cases.                          |   require a graph for narrow work.         |
| Post-dispatch             | A saved persona output demonstrably rules outside its declared `owns`, or | `scripts/persona_note.py` and its               | Do not infer semantic compliance from      |
|   verification            |   metadata proves a material mismatch.                                    |   `MANIFEST.json`.                              |   prose, re-route, retry, or edit output.  |
| Concurrent claim lease    | An operator records an actual competing claim on the same decision.       | Field-log `run_dir` and project-local run data. | No daemon, scheduler, or automatic         |
|                           |                                                                           |                                                 |   resumption.                              |
| Access/action control     | A scoped task exposes an authority or privacy boundary that existing      | Existing task authority policy and project      | Not a new routing gate and never           |
|                           |   operator authority does not make clear.                                 |   remote/privacy rules.                         |   self-approved.                           |
| Learning promotion        | The established field-log/gap thresholds are met with named evidence and  | `scripts/propose_evolution.py`.                 | Proposal only; no automatic catalogue      |
|                           |   counterexamples.                                                        |                                                 |   mutation.                                |

## Comparison of all repositories

Every phase label in this table means “candidate if its evidence trigger fires,” never “scheduled work.” “Skip” means no extracted component should be introduced into Agent Stack.

| Repository                   | Assessment against Agent Stack                                         | Adaptable mechanism                                             | Proposed disposition       |
| ---------------------------- | ---------------------------------------------------------------------- | --------------------------------------------------------------- | -------------------------- |
| [AWS CAO](https://github.com/awslabs/cli-agent-orchestrator) | Better at operating isolated CLI workers; not a fit as our runtime.    | Outcome → lesson → operator-approved promotion ladder.          | Phase 5 only.              |
| [Agent Zero](https://github.com/agent0ai/agent-zero) | Autonomous desktop-agent runtime, contrary to Agent Stack's defining   | None that justifies importing its runtime.                      | Skip.                      |
|                              |   constraint.                                                          |                                                                 |                            |
| [gAIOS](https://github.com/alirezarezvani/gaios) | A personal AIOS template, not a routing system.                        | Distinguish reversible/internal work from external or           | Phase 4.                   |
|                              |                                                                        |   irreversible actions.                                         |                            |
| [Podiom](https://github.com/Podiom/Podiom) | Better at local durable sessions, schedules, and goals; those are out  | Typed capability requests with operator-only decisions.         | Phase 4, schema only.      |
|                              |   of scope.                                                            |                                                                 |                            |
| [wshobson/agents](https://github.com/wshobson/agents) | Better at multi-harness plugin delivery.                               | Per-harness capability matrix, generated support docs,          | Phase 1.                   |
|                              |                                                                        |   portability lint.                                             |                            |
| [Agent Deck](https://github.com/claude-world/agent-deck) | Web orchestration product, not a routing-control improvement.          | Per-run spend budget is separable but not yet evidenced as a    | Defer.                     |
|                              |                                                                        |   need.                                                         |                            |
| [Squad](https://github.com/mco-org/squad) | Better at coordinating concurrent ownership.                           | Atomic claim with time-bounded lease.                           | Phase 3 only if concurrent |
|                              |                                                                        |                                                                 |   claims exist.            |
| [backnotprop/orchestrator](https://github.com/backnotprop/orchestrator) | Useful execution guard, not a better routing model.                    | Runtime/model discovery and declared fallback precedence.       | Phase 1.                   |
| [evanca/skills](https://github.com/evanca/skills) | Repository returned 404 during the survey and refresh.                 | Unknown.                                                        | Leave unreachable.         |
| [anytools-agent-skills](https://github.com/anytools-app/anytools-agent-skills) | Strong execution-audit discipline.                                     | Required-versus-actual tool/model audit and read-only audit     | Phases 1 and 3.            |
|                              |                                                                        |   mode.                                                         |                            |
| [SuperClaude](https://github.com/SuperClaude-Org/SuperClaude_Framework) | Broad Claude Code framework, weaker as a portable control plane.       | Explicit declared negative scope: “will not”.                   | Phase 2.                   |
| [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD) | Valuable workflow library but no stronger ownership or gate model.     | None in the routing layer.                                      | Skip as a framework.       |
| [Claude Squad](https://github.com/smtg-ai/claude-squad) | Terminal workspace manager, not an ownership/routing system.           | None.                                                           | Skip.                      |
| [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) | Better production runtime; its graph machinery exceeds this project's  | Directed hand-off graph with a deliberately non-permissive      | Phase 2 concept.           |
|                              |   scope.                                                               |   default.                                                      |                            |
| [Microsoft AutoGen](https://github.com/microsoft/autogen) | Better SDK/runtime breadth, not better for the prompt-layer scope.     | Narrow legal candidates before selection; validate a graph      | Phase 2 concept.           |
|                              |                                                                        |   before dispatch.                                              |                            |
| [Agency Swarm](https://github.com/VRSEN/agency-swarm) | Useful typed communication boundary.                                   | Required typed payload for each hand-off edge.                  | Phase 2.                   |
| [MetaGPT](https://github.com/FoundationAgents/MetaGPT) | Strongest complementary declarative role idea.                         | Declare each role's legal consumed artefacts, not only its      | Phase 2.                   |
|                              |                                                                        |   outputs.                                                      |                            |
| [LangGraph](https://github.com/langchain-ai/langgraph) | Better state-machine runtime; intentionally not a persona ownership    | None needed without adopting a runtime.                         | Skip.                      |
|                              |   system.                                                              |                                                                 |                            |
| [CrewAI](https://github.com/crewAIInc/crewAI) | Useful task-quality convention; its crew runtime is out of scope.      | Required expected-output contract and bounded evaluation.       | Phase 2; no automatic      |
|                              |                                                                        |                                                                 |   retry.                   |
| [Ruflo / Claude Flow](https://github.com/ruvnet/claude-flow) | Broad automation harness that conflicts with the safety boundary.      | None that warrants disentangling its runtime.                   | Skip.                      |
| [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) | Useful skill coverage and fixture conventions.                         | SLO, incident-response, and migration coverage; golden expected | Separate skill backlog.    |
|                              |                                                                        |   outputs.                                                      |                            |
| [joeblackwaslike/agent-skills](https://github.com/joeblackwaslike/agent-skills) | Useful imported-content provenance convention.                         | Source URL, retrieval timestamp, checksum, and pinned version   | Phase 1 for imported       |
|                              |                                                                        |   metadata.                                                     |   references.              |
| [heyimcarlos/agent-skills](https://github.com/heyimcarlos/agent-skills) | Useful authoring doctrine, not a control-plane advance.                | Sharper writing-for-agents guidance.                            | Separate quality-rule      |
|                              |                                                                        |                                                                 |   proposal.                |
| [fdarkaou/agent-skills](https://github.com/fdarkaou/agent-skills) | No material advantage over current delivery conventions.               | None.                                                           | Skip.                      |
| [carlkibler/agent-skills](https://github.com/carlkibler/agent-skills) | Useful operational-learning practice.                                  | Privacy-conscious session-log forensics that proposes, never    | Phase 5 input only.        |
|                              |                                                                        |   applies, improvements.                                        |                            |

## Verified upstream adaptation map

The paths and symbols below were checked against the public repositories on 2026-09-03. They identify the exact source boundary to study; they are **not** copy/paste targets. A “none” finding is
intentional and prevents a runtime dependency being smuggled in under the name of an adaptation.

1. **AWS CAO** — `src/cli_agent_orchestrator/services/learned_patterns.py`, `apply_deltas()` and `parse_profile()`: study bounded, itemised lesson deltas and corruption-safe delimiters. Adapt only
   after field evidence warrants a proposal; retain Agent Stack's proposal-only rule rather than CAO's profile mutation.
2. **Agent Zero** — `README.md`: no component. Its general autonomous-agent runtime is outside the project safety model.
3. **gAIOS** — `.claude/skills/decide/SKILL.md`, “Recommend” step: study its explicit falsifier and reversibility fields. If an authority-bound action is observed, add those fields to an operator
   decision record; do not create a new action engine.
4. **Podiom** — `cmd/podiomd/permission_mcp.go`, `forwardPermission()` and `forwardClaudeUserInput()`: study the request/decision separation. If triggered, adapt only the request schema and
   operator-owned decision transition; do not import its MCP service, sessions, or goals.
5. **wshobson/agents** — `plugins/agent-orchestration/.codex-plugin/plugin.json`, `skills` descriptor: study the per-client plugin descriptor boundary. If portability evidence appears, use a
   manifest-derived compatibility matrix rather than adding a second installer.
6. **Agent Deck** — `cli/commands/run.ts`, `execute()`: no component. Its plan/launch/monitor/finalise workflow and polling are an excluded autonomous runtime pattern.
7. **Squad** — `src/store.rs`, `Store::ack_task()` and `Store::complete_task()`: study the compare-and-check ownership transition using `lease_owner` and `lease_expires_at`. Adapt a one-shot local
   claim only after a recorded collision; do not import SQLite coordination or task resumption.
8. **backnotprop/orchestrator** — `packages/cli/src/runtime-doctor.ts`, `doctorRuntimeAvailability()`: study target executable discovery and an explicit unavailable result. Use only if a field
   portability defect needs a deterministic diagnosis.
9. **evanca/skills** — repository tree returned 404 on the refresh. No source boundary is available; do not adapt or infer one.
10. **anytools-agent-skills** — `skills/delegate/SKILL.md`, “role allocation” and “delegation eligibility gate” sections: study the fixed final-decision owner and read-only delegation boundary. Agent
    Stack already has an operator-control equivalent; do not import its orchestration workflow.
11. **SuperClaude Framework** — `skills/confidence-check/SKILL.md`, “Confidence Assessment Criteria”: study a declared negative-scope/research-evidence checklist. Consider only as prose-quality
    guidance, not a new scoring or routing control.
12. **BMAD Method** — `src/bmm-skills/ship/bmad-build/workflow.md`, “Ready for Development Standard”: study file-specific, ordered, testable plan requirements. Reuse only when a triggered change
    receives its separate implementation plan.
13. **Claude Squad** — `session/instance.go`, `Instance.Start()`, `Pause()`, and `Resume()`: no component. Persistent tmux session management breaches Agent Stack's no-resume/no-daemon boundary.
14. **Microsoft Agent Framework** — `python/packages/core/agent_framework/_workflows/_edge.py`, `Edge` and `EdgeGroup`: study a finite, validated edge definition. If hand-off evidence appears, adapt
    only a small declarative edge validator; do not add a workflow executor.
15. **Microsoft AutoGen** — `python/packages/autogen-agentchat/src/autogen_agentchat/base/_handoff.py`, `Handoff`: study an explicit target, description, and message contract. Use as a source for
    fields only; Agent Stack's hand-off must remain a data declaration rather than a callable transfer tool.
16. **Agency Swarm** — `src/agency_swarm/agent/agent_flow.py`, `AgentFlow.get_all_flows()`: study an inspectable directed edge list. If triggered, validate declared edges without adopting its
    comparison-operator syntax or communication runtime.
17. **MetaGPT** — `metagpt/base/base_role.py`, `BaseRole` methods `think()`, `act()`, `react()`, and `run()`: no direct component. It reinforces the distinction between a role contract and runtime
    lifecycle; Agent Stack keeps the former and rejects the latter.
18. **LangGraph** — `libs/langgraph/langgraph/graph/state.py`, `StateGraph`: no component. Stateful graph execution, checkpoints, and continuation exceed scope.
19. **CrewAI** — `lib/crewai/src/crewai/tasks/task_output.py`, `TaskOutput` and `has_tool_failures`: study an expected-output field plus explicit incomplete-tool fact. If hand-off evidence exists,
    carry only metadata/declared artefact fields; never store raw output in a cross-project registry.
20. **Ruflo / Claude Flow** — `.agents/skills/agent-consensus-coordinator/SKILL.md`: no component. Consensus coordination and adaptive multi-agent automation violate the single-operator and
    no-autonomous-loop model.
21. **alirezarezvani/claude-skills** — `.gemini/skills/agent-decision-receipts/SKILL.md`: the checked path is a relative wrapper, not a self-contained implementation. No portable component is
    verified; do not use it as a receipt schema source.
22. **joeblackwaslike/agent-skills** — `skills/multi-provider-plugins/SKILL.md`: study multi-provider packaging conventions only if the manifest cannot represent a confirmed compatibility fact. Keep
    source URL, retrieval date, and checksum as imported-reference provenance, not runtime state.
23. **heyimcarlos/agent-skills** — `skills/engineering/principle-encode-lessons-in-structure/SKILL.md`: study the principle that recurring lessons belong in enforceable structure. Use only after
    existing evidence reaches the project proposal threshold.
24. **fdarkaou/agent-skills** — `skills/fdarkaou/implement-with-validation/SKILL.md`: no new control. Its validation-before-claim pattern already aligns with Agent Stack's `just preflight` gate.
25. **carlkibler/agent-skills** — `skills/agent-log-forensics/SKILL.md`, “Preserve Privacy” and “Classify Findings”: study privacy-minimised, pattern-level reporting. It may contribute evidence only
    after explicit scope/consent; it must not read or centralise raw persona notes.

## Target state

The target, if a trigger makes it necessary, is a small extension of the existing evidence chain alongside the router—not a replacement for it. There is no active target-state build.

```text
routing.toml + close_route.py
        │
        ▼
existing field-log entry and project-local persona run manifest
        │
        ▼
optional, evidence-triggered contract or portability fact
        │
        ▼
read-only comparison of declared versus recorded facts
        │
        ▼
operator review of a named mismatch or evidence gap
        │
        ├── operator review or access request when authority is missing
        └── existing proposal-only evolution process
```

The router remains authoritative for ownership and gates. Any future record must extend an existing field-log row, run manifest, or evaluation receipt instead of creating a competing event store. It
must not silently repair, re-route, or overrule an operator.

## Phase 1 — portability and execution receipts

**Status: deferred.** No standalone receipt or harness registry should be built now. First establish that an existing record cannot answer a real portability or normal-work provenance question.

### Objective

When a verified portability defect appears, make the affected installation target explicit and record the smallest missing normal-work execution fact.

### New declarative surfaces

If triggered, add a harness capability registry with one row per *affected* target, derived from the current symlink delivery surfaces: Claude Code, Codex, and compatible `.agents` consumers. Each
capability is tri-state: `supported`, `unsupported`, or `unverified`. `unverified` is a finding, not permission to claim support. The registry must be a manifest companion, not a new installer.

```toml
[[harnesses]]
id = "codex"
discovery_path = "~/.codex/skills"
skill_metadata = "unverified"
hooks = "unverified"
per_agent_tool_allowlist = "unverified"
max_skill_body_bytes = "unverified"

[[harnesses]]
id = "claude-code"
discovery_path = "~/.claude/skills"
skill_metadata = "unverified"
hooks = "unverified"
per_agent_tool_allowlist = "unverified"
max_skill_body_bytes = "unverified"
```

The registry must not guess an 8 KB Codex skill limit. A numeric limit is recorded only after a reproducible target-specific test or authoritative documentation establishes it. Until then, the lint
can warn about unusually large skill bodies without asserting truncation.

### Existing records before a receipt

Do not add the generic receipt shown below unless an actual normal-work evidence field is absent from both `field_log.py` and the project-local persona `MANIFEST.json`. The runner qualification
receipt already answers a different question: whether an **evaluation** run is reproducible. It must not be relabelled as ordinary-work telemetry.

If a narrow normal-work record is later justified, write it as one JSON object per line in the existing `evals/field-log.jsonl` stream, preferably as an optional `receipt` object on the field-log
entry for the same run. Do not introduce a separate `receipts.json` file. `MANIFEST.json` remains a single per-run snapshot, because it records the complete run state rather than an event stream.
Neither record may contain secrets, prompts, file contents, or credentials. The example is one JSONL line and a possible field set, not an approved schema:

```jsonl
{"kind":"execution-receipt","schema_version":1,"run_id":"project-slug-20260903_1943","required":{"skill":"github-explorer","requires_any":["github-access"]},"actual":{"harness":"codex","model":"recorded-if-known","tool":"github-access"},"result":"honoured","evidence":"direct-runtime-observation","recorded_at":"2026-09-03T19:43:00+10:00"}
```

`result` is `honoured`, `mismatch`, or `unverifiable`. A missing observation is never reported as honoured. The initial JSONL line can be written by a human at task close; it does not require a new
runtime hook.

### Deliverables

- A documented evidence gap proving why existing records are inadequate.
- One minimal registry or existing-record extension, validator, and generated support table only if the gap is confirmed.
- Provenance metadata for imported reference content where an upstream source is retained.

## Phase 2 — legal hand-offs

**Status: deferred.** The current corpus and field log must first show that an unknown, missing, or wrongly consumed artefact caused a material multi-persona failure.

### Objective

Make a persona route auditable as a directed, typed information flow. Today `owns` states who decides or produces; it does not state what inputs the persona may rely on, what it must return, or what
the next participant is allowed to consume.

### Catalogue extension

If triggered, add optional declarations to the existing persona records. Start with actual multi-persona patterns in a replay or field record; do not invent a complete workflow graph or a second role
model.

```toml
[[personas]]
id = "cfo-campbell"
owns = ["economic-viability", "financial-guardrail", "pricing-economics"]
consumes = ["research-evidence", "cost-model", "product-constraints"]
produces = ["economic-verdict", "financial-guardrails"]
will_not = ["select-technical-architecture", "assert-current-regulatory-facts-without-research"]
```

`consumes`, `produces`, and `will_not` are declarations, not stylistic prose. Every value comes from a small shared artefact vocabulary. The validator rejects unknown vocabulary values, duplicate
values, and a route whose consumer has not declared the producer's artefact type.

**A third confirmed example of this pattern in production-shaped code**, found in an unrelated survey filed separately because it addresses building new agents rather than Agent Stack's own routing
(see [off-topic/vertical-agent-framework-survey-20260903_2126.md](../off-topic/vertical-agent-framework-survey-20260903_2126.md)): `chetanreddyv/vertical_aiAgent` implements a Gemini Manager
decomposing a request into typed steps for MCP-backed specialists (Email, SQL, Drive, Calendar, Jira, meeting-transcript search), each declaring the tools it consumes, with an explicit
human-in-the-loop confirmation gate on any mutating step — directly relevant prior art for this phase's `consumes`/`produces` split and for Phase 4's action-authorization boundary below. It is a
small, single-maintainer project (4 stars) whose README license badge is not backed by an actual LICENSE file, so treat it as a pattern to study, not code to depend on — the same caution already
applied to MetaGPT and Agency Swarm above.

### Handoff contract

Each dependency edge declares an expected output and required payload. The contract is intentionally small: producer, consumer, artefact type, required fields, and destination use.

```toml
[[handoffs]]
from = "research-thompson"
to = "cfo-campbell"
artefact = "research-evidence"
required_fields = ["claim", "source", "retrieved_at", "confidence"]
consumed_by = "economic-verdict"
```

No payload contains raw credentials or unrestricted source transcripts. A failed contract blocks only that hand-off from being represented as complete; it does not re-dispatch a persona or make a
substitute decision.

### Deliverables

- Shared artefact vocabulary and schema validation.
- `consumes`, `produces`, and `will_not` on the first supported persona paths.
- Expected-output contracts for multi-persona routes.
- Deterministic candidate narrowing before model selection when an edge gives a finite legal set.

## Phase 3 — post-dispatch verification

**Status: deliberately deferred.** `scripts/persona_note.py` already persists persona output and the run manifest. Building an enforcement check before a persona is shown to rule outside `owns` would
be a check against an unobserved failure. Revisit only from a saved, reviewable counterexample.

### Objective

If a counterexample appears, compare “the route chose this persona” with recorded, finite facts about its output and remit without judging prose quality or changing work automatically.

### Audit model

The read-only audit would extend `persona_note.py`'s existing `MANIFEST.json`; it must not create a second run log. It compares the route, a confirmed legal contract if one exists, and recorded output
metadata. It produces a result per participant:

| Status         | Meaning                                                                           | Required handling                                              |
| -------------- | --------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| `honoured`     | Required capability and declared remit match observed metadata.                   | Include in synthesis.                                          |
| `mismatch`     | Observed model/tool, producer, consumer, or artefact type differs from the route. | Surface prominently; never silently normalise.                 |
| `incomplete`   | Dispatch was recorded but an expected output did not return.                      | Preserve returned notes; operator decides whether to continue. |
| `unverifiable` | Required evidence was not captured.                                               | Report the evidence gap; do not infer compliance.              |

The audit can validate metadata and finite artefact contracts deterministically. It must not pretend to infer the semantic quality of a prose answer from labels alone, choose a new owner, or decide
gate truth. A later quality evaluator, if separately evidenced, remains bounded, recorded, and unable to retry or rewrite autonomously.

### Atomic claim, only where needed

If two execution contexts can work the same declared decision, the run manifest gains a compare-and-swap claim:

```text
claim(owner, decision_id, lease_until)
  succeeds only when decision_id is unclaimed or its lease has expired
  fails loudly when another owner holds a live claim
  never changes the declared route owner
```

This is not Phase 1 work. It is unnecessary for sequential or single-persona routes and must not become a daemon. A lease expires without automatically starting work; expiry only makes a future,
operator-authorised claim possible.

### Deliverables

- Read-only `audit-route` report producing the four statuses above.
- Contract fixtures for honoured, mismatch, incomplete, and unverifiable cases.
- Optional one-shot claim primitive, introduced only after concurrent collisions are observed.

## Phase 4 — operator-controlled access and action authorization

**Status: deferred.** Existing explicit operator authority is the control. A new request object is justified only if field use reveals a concrete authority ambiguity or a privacy/remote boundary that
cannot be handled through the existing task scope.

### Objective

Separate a missing capability from an action the operator must approve. The distinction prevents an agent from treating a missing tool, secret, permission, or external commitment as a problem to work
around silently.

### Request schema

```json
{
  "kind": "skill | mcp_server | cli_tool | env_var | permission_mode",
  "purpose": "why the route cannot complete without it",
  "scope": "task or project",
  "requested_by": "route participant",
  "status": "pending | approved | denied | fulfilled | expired",
  "operator_decision": null
}
```

An agent may create a request but cannot set `approved`, `denied`, or `fulfilled`. A future implementation is a durable proposal/ledger, not an API endpoint or notification service. It must also
preserve the project boundary: raw persona notes are project-owned evidence and are never collected, inspected, or copied across projects by Agent Stack automation.

### Existing authority boundary, not a new routing gate

If a trigger occurs, document the following action classification at the point of operator review. Do **not** encode it as a new routing gate: gate flags are advisory until a separately evidenced
gate-collapse decision, and this classification does not determine a persona owner.

| Action class                                                          | Default                                                       |
| --------------------------------------------------------------------- | ------------------------------------------------------------- |
| Internal and reversible                                               | Proceed within the user's task scope.                         |
| External but read-only                                                | Proceed when research/tool use is in scope; record sources.   |
| Persistent local change                                               | Proceed only when the user requested the change; validate it. |
| External, irreversible, privileged, regulated, or material commitment | Stop for explicit operator authority.                         |

This does not create approval theatre for normal read-only research. It formalises the existing safety rule at the point where an action is proposed.

## Phase 5 — evidence-gated learning

**Status: active only through the existing observation and proposal mechanism.** `field_log.py`, `persona_note.py`, `capability-gaps.jsonl`, and `propose_evolution.py` already implement the safe first
step. At six field entries, the correct result is no proposal.

### Objective

Keep the field log's safe destination without allowing observational, self-reported data to mutate guidance. Any future addition must improve an observed limitation of this mechanism, not duplicate
it.

### Promotion ladder

```text
field observation
  → proposal with linked receipts, audits, and counter-evidence
  → operator review
  → accepted, scoped instruction change with tests
  → later revalidation or retirement
```

Promotion is disabled by default. A proposal must include the repeated signal, its sample size, affected artefacts, alternative explanations, counterexamples, expected benefit, and a rollback path.
The proposer can create the document; only the operator can approve implementation. No task may promote itself, and no lesson may be injected into all future personas merely because it was recalled.

Session-log forensics can contribute evidence only after explicit scope and privacy review. It must minimise or redact source content, report recurring friction rather than private transcript text,
and write proposals rather than edits.

## Invariants and failure behaviour

The adaptation is acceptable only if these remain true:

1. `routing.toml` and `close_route.py` remain the single authority for ownership and gate closure.
2. A receipt cannot be marked `honoured` without recorded required and actual fields.
3. An absent output is `incomplete`, never silently treated as a successful route.
4. A missing audit input is `unverifiable`, never assumed compliant.
5. A hand-off is not complete unless its producer, consumer, artefact type, and required fields validate.
6. An agent can request access but cannot decide, grant, or install it.
7. A lease never starts, resumes, retries, or schedules work; it only prevents concurrent claims.
8. Field evidence creates proposals only; it cannot mutate personas, skills, routing, permissions, or global installation.
9. Existing direct-skill and single-persona routes remain usable without a hand-off graph.
10. No record stores secrets, unrestricted transcripts, or written file contents.
11. No new control is implemented before its named evidence trigger and an operator-approved plan; no control duplicates an existing log, manifest, or evaluation receipt.
12. A deterministic verifier may constrain only finite declared contracts and recorded facts; it cannot infer persona prose quality, primary owner, or gate truth.

Failure posture is explicit: writes to a requested-but-disabled control fail loudly before a partial change; read-only audits return a named `unverifiable` finding when evidence is absent; an invalid
or unreadable configuration fails closed for promotion and authorization controls.

## Validation plan

Validation starts only after the relevant evidence trigger is met and an operator approves a plan. Each approved change must pass the existing `just preflight` gate and its own focused tests before it
becomes a dependency for a later change. A negative fixture must reproduce the observed failure; do not add a check that only scans an imagined condition.

| Layer             | Minimal validation                                                       | Negative cases that must fail                                                                     |
| ----------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| Harness matrix    | Registry parser, target fixtures, generated support-table snapshot.      | Unknown harness; unsupported construct marked supported; asserted numeric limit with no evidence. |
| Execution receipt | One-record JSONL schema and append/read round trip in `field-log.jsonl`. | Missing actual field marked honoured; secret-shaped field; unrecognised status.                   |
| Handoff contract  | Catalogue and payload fixtures.                                          | Unknown artefact; producer/consumer mismatch; missing required field.                             |
| Route audit       | Deterministic status fixtures.                                           | Audit silently upgrades mismatch or unverifiable to honoured.                                     |
| Claim primitive   | One-shot concurrent-process test.                                        | Live claim overwritten; expiry starts a task; declared owner mutated.                             |
| Access request    | State-transition tests.                                                  | Agent actor approves/denies; a request carries an environment-variable value.                     |
| Promotion         | Proposal-only test and catalogue regression tests.                       | Observation changes a source file; insufficient evidence produces an accepted change.             |

The routing corpus remains frozen unless a separately approved evaluation protocol authorises a change. New tests should target the new evidence and contract layers, not tune routing labels until a
desired result appears.

## Rollout, rollback, and deferred work

No phase is scheduled. If a trigger is met, the resulting change is additive and opt-in. Existing routes remain valid if no receipt, contract, or audit is requested. A registry entry or schema is
introduced in `unverified` mode before it can fail a route. Warning-only reports become blocking only after tests demonstrate that the observed failure condition is meaningful and after an operator
accepts the policy.

Rollback is deletion or disabling of the new optional validation invocation, not deletion of evidence. Existing JSONL receipt entries and audit reports remain readable. A schema version bump must
retain a reader for the preceding version or report the old record as unsupported rather than corrupt.

Deferred until field evidence establishes need:

- atomic leases, unless concurrent decision claims actually collide;
- spend or token caps, unless measured cost lacks another effective control;
- LLM-as-judge quality scoring, unless deterministic contract checking leaves an evidenced quality gap;
- automatic adapters or content transformations for harnesses; and
- automatic continuation, retries, promotion, installation, and permissions changes.

## Acceptance criteria

This proposal is ready to become an implementation plan only when the operator accepts all of the following:

- A named field/replay counterexample satisfies one candidate's evidence trigger and identifies why the relevant existing record is insufficient.
- The plan reuses the existing field log, persona run manifest, or evaluation receipt rather than creating a competing store.
- A harness change starts warning-only and does not assert unverified Codex or other harness limits.
- A shared artefact vocabulary, if needed, is small and derives from real multi-persona routes.
- Post-dispatch audit, if needed, reports mismatches and evidence gaps without repairing work automatically.
- Access requests stay operator-controlled, protect project-owned persona notes, and do not introduce a background service or routing gate.
- Learning produces reviewable proposals, never automatic source changes.
- The implementation plan names each affected source, generated surface, test fixture, validation command, and rollback condition.

## Sources

- Agent Stack's current baseline: [routing catalogue](../../routing.toml), [orchestrator contract](../../skills/skill-agent-stack/SKILL.md), and [safety
  model](../../.archcore/rules/0001-safety-model.md).
- Current project sequencing and observed evidence: [field-use state](../../SCRATCHPAD.md), [field log](../../evals/field-log.jsonl), [evolution proposer](../../scripts/propose_evolution.py), and
  [persona-note recorder](../../scripts/persona_note.py).
- Existing evaluation provenance: [runner qualification](../../scripts/qualify_runner.py) and [runner qualification specification](../../.archcore/specs/0006-runner-qualification.md).
- Internal evidence synthesis: [external 25-repository survey](external-orchestrator-survey-20260903_1849.md).
- A third confirmed manager→specialist→MCP example, filed separately as it addresses a different initiative:
  [off-topic/vertical-agent-framework-survey-20260903_2126.md](../off-topic/vertical-agent-framework-survey-20260903_2126.md).
- Exact public-repository source paths and symbols are recorded in [Verified upstream adaptation map](#verified-upstream-adaptation-map); paths were inspected on 2026-09-03 and must be rechecked
  before any implementation decision.
- CAO's opt-in outcome/lesson/promotion design: [self-learning documentation](https://github.com/awslabs/cli-agent-orchestrator/blob/main/docs/self-learning.md).
- CAO's role/tool restriction surface: [tool restrictions](https://github.com/awslabs/cli-agent-orchestrator/blob/main/docs/tool-restrictions.md).
- Podiom's typed access requests and operator-only decision boundary: [goals documentation](https://github.com/Podiom/Podiom/blob/master/docs/goals.md).
- wshobson's multi-harness model and capability-matrix purpose: [repository overview](https://github.com/wshobson/agents) and [capability
  matrix](https://github.com/wshobson/agents/blob/main/tools/adapters/capabilities.py).
