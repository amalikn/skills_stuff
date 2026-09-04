Title: Phased implementation and self-verification plan
Category: evidence-and-proposal
Status: proposed
Scope: Per-phase implementation steps and the self-verification each phase requires, for the five mechanisms in the reliability adaptation proposal
Last reviewed: 20260904_1208
Summary: This document is inert until an operator names the evidence trigger for a specific phase and approves that phase individually. It does not authorise any implementation on its own. For each
  phase it fixes what gets changed, in what order, and exactly what must be run and pass afterward before the next phase — or the next file in the same phase — may start.

# Phased implementation and self-verification plan

## Contents

- [What this document is and is not](#what-this-document-is-and-is-not)
- [Tool and feature provenance](#tool-and-feature-provenance)
- [Standing rule for every phase](#standing-rule-for-every-phase)
- [Common verification commands](#common-verification-commands)
- [Phase 1 — portability and execution receipts](#phase-1-portability-and-execution-receipts)
- [Phase 2 — legal hand-offs](#phase-2-legal-hand-offs)
- [Phase 3 — post-dispatch verification](#phase-3-post-dispatch-verification)
- [Phase 4 — operator-controlled access and action authorization](#phase-4-operator-controlled-access-and-action-authorization)
- [Phase 5 — evidence-gated learning](#phase-5-evidence-gated-learning)
- [What happens if a verification step fails](#what-happens-if-a-verification-step-fails)
- [Sources](#sources)
## What this document is and is not

This is **not** an implementation plan in the `.archcore/plans/` sense — it has not been accepted, and per [the reliability adaptation
proposal](agent-stack-reliability-adaptation-proposal-20260903_1943.md)'s own decision, none of the five phases may be designed or built until its named evidence trigger fires and an operator approves
a scoped plan for that phase specifically. Writing this document is not that approval, and does not constitute one.

What it *is*: the answer to "once a phase is triggered, what exactly happens and how do I check my own work before calling it done" — so that when the operator does trigger a phase, execution is not
improvised. It exists so the operator can review the intended mechanics **before** any trigger fires, not after.

**This document changes no code, no `routing.toml`, no persona files, and no scripts.** It is markdown only.

## Tool and feature provenance

Every mechanism named in the phase sections below traces to one exact upstream file and symbol, verified against the public repository on 2026-09-03 (see the proposal's own [Verified upstream
adaptation map](agent-stack-reliability-adaptation-proposal-20260903_1943.md#verified-upstream-adaptation-map)). Nothing here is a framework import — each row is a bounded idea copied into Agent
Stack's own declarative, operator-controlled model, never the upstream project's runtime, service, or dependency.

NOTE: authored as single-line, unpadded rows kept under 200 characters each, per this project's own table-authoring convention — the automatic prose-wrap hook mis-wraps table cells across physical
rows on anything longer, which breaks column alignment without an error. If this table is ever edited, keep every row on one line; do not let a formatter rewrap it. See
[external-orchestrator-survey-20260903_1849.md](external-orchestrator-survey-20260903_1849.md) for the earlier occurrence of the same failure mode.

| Phase | Feature adapted                                   | Source repo                  | Exact source                                    | Becomes, in Agent Stack                                 |
| ----- | ------------------------------------------------- | ---------------------------- | ----------------------------------------------- | ------------------------------------------------------- |
| 1     | Per-harness capability descriptor                 | wshobson/agents              | plugin.json `skills` descriptor                 | `harness-capabilities.toml` registry                    |
| 1     | Runtime discovery, explicit unavailable result    | backnotprop/orchestrator     | runtime-doctor.ts `doctorRuntimeAvailability()` | diagnostic mode of the harness validator                |
| 1     | Required-vs-actual execution audit line           | anytools-agent-skills        | delegate/SKILL.md audit                         | optional `receipt` object on a field-log entry          |
| 1     | Imported-reference provenance stamp               | joeblackwaslike/agent-skills | multi-provider-plugins/SKILL.md                 | source URL/date/checksum on imported refs only          |
| 2     | Declared legally-consumed artefact types          | MetaGPT                      | architect.py:52 `_watch({WritePRD})`            | `consumes` array on the personas actually involved      |
| 2     | Required typed payload on a hand-off edge         | Agency Swarm                 | send_message.py `extra_params_model`            | `required_fields` on a `[[handoffs]]` entry             |
| 2     | Per-task expected-output contract                 | CrewAI                       | task_output.py `TaskOutput`/`expected_output`   | `produces` field plus expected artefact shape           |
| 2     | Explicit hand-off target/message fields           | Microsoft AutoGen            | `_handoff.py` `Handoff` dataclass               | field vocabulary for `[[handoffs]]` (data only)         |
| 2     | Validated non-permissive directed edge            | MS Agent Framework           | `_edge.py` `Edge`/`EdgeGroup`                   | structural shape of `[[handoffs]]` if ever multi-hop    |
| 2     | Candidate narrowing before model selection        | Microsoft AutoGen            | `_selector_group_chat.py` `candidate_func`      | `close_route.py` narrows routes before selection        |
| 2     | Declared negative scope                           | SuperClaude Framework        | confidence-check/SKILL.md                       | `will_not` array on the personas actually involved      |
| 3     | Routed-vs-honoured, four-state audit              | anytools-agent-skills        | delegate/SKILL.md five-stage audit              | `scripts/audit_route.py`                                |
| 3     | Atomic claim, time-boxed lease                    | Squad                        | store.rs `ack_task()`/`complete_task()`         | one-shot claim primitive, added only after a collision  |
| 4     | Typed capability request, operator-only decision  | Podiom                       | permission_mcp.go `forwardPermission()`         | access-request schema                                   |
| 4     | Reversibility/externality classification          | gAIOS                        | decide/SKILL.md "Recommend" step                | four-row action-classification table                    |
| 5     | Outcome-lesson-promotion ladder, reference only   | AWS CLI Agent Orchestrator   | learned_patterns.py `apply_deltas()`            | studied only if the existing ladder proves insufficient |
| 5     | Privacy-minimised log forensics as proposal input | carlkibler/agent-skills      | agent-log-forensics/SKILL.md                    | optional evidence input only, never an automatic edit   |

Full repo URLs and additional context for each row are in the proposal's [Verified upstream adaptation
map](agent-stack-reliability-adaptation-proposal-20260903_1943.md#verified-upstream-adaptation-map). Repositories the survey opened and read but that contribute **no** component to this plan — Agent
Zero, Agent Deck, BMAD Method, Claude Squad (smtg-ai), LangGraph, Ruflo/Claude Flow, evanca/skills (404, unreachable), fdarkaou/agent-skills — are not repeated here; the reasoning for each is in the
proposal's [comparison table](agent-stack-reliability-adaptation-proposal-20260903_1943.md#comparison-of-all-repositories).

## Standing rule for every phase

Before starting any phase's implementation:

1. The operator names the specific evidence (a field-log entry, a `capability-gaps.jsonl` entry, or a described real incident) that satisfies that phase's trigger from the proposal's evidence table.
2. The operator explicitly approves proceeding with that phase, scoped to what is described below — not a larger or different change.
3. Work happens on a feature branch or in a clearly reversible working-tree state; nothing is squashed into an existing accepted commit.
4. Each phase is implemented and verified as its own unit before the next phase starts. Phases are not batched.
5. If a verification step in this document and the actual behaviour of a check disagree, the check's actual behaviour governs — this document is updated to match, not the other way around.

No phase begins from this document alone. Every phase section below starts with its trigger restated for that reason: to make it impossible to execute a phase by skimming past the gate.

## Common verification commands

Run after **every** phase, in addition to the phase-specific checks:

```bash
just bootstrap      # only if the venv is not already provisioned
just preflight       # governance + library contract validation, chained
just governance       # scripts/check_governance.py directly, if isolating a failure
just test            # unit test suite
```

`just preflight` must exit 0 before a phase is reported complete. A phase that leaves `just preflight` red is not done — it is reverted, not left for a later cleanup pass.

Where a phase touches `routing.toml`, `close_route.py`, or any persona/skill file that participates in routing, additionally run the frozen-corpus gate from [Rule
0013](../../.archcore/rules/0013-trim-against-the-frozen-corpus-as-a-gate.md) before and after the change:

```bash
just routing-eval-hermes   # or the qualified runner in use at the time — see scripts/qualify_runner.py
```

Compare hard-invariant scores only (gate misses, not soft routing-quality drift). A phase that regresses a hard invariant on the frozen 60-case corpus is reverted, full stop — it does not proceed to a
"fix in the next phase" note.

## Phase 1 — portability and execution receipts

**Trigger (restated, must be named by the operator before this section is used):** a reproducible install/runtime portability defect, or an unverifiable harness claim, has affected field use.

### Implementation steps

1. Add the harness capability registry as a new file, `harness-capabilities.toml`, at repo root — a manifest companion, not a new installer. Seed only the *affected* harness(es) named in the
   triggering evidence; do not pre-populate entries for harnesses with no reported defect.
2. Every field starts `"unverified"`. Flip a field to `"supported"` or `"unsupported"` only after a reproducible test or authoritative upstream documentation is cited inline as a TOML comment.
3. Write `scripts/validate_harness_capabilities.py`: parses the registry, rejects an unknown harness id, rejects a numeric limit field with no cited evidence, and renders a generated support table
   (`docs/reliability-adaptation/harness-support-table.md` or equivalent — catalogued per the existing `docs/README.md` convention the moment it exists).
4. If the triggering evidence is a normal-work execution fact rather than a harness limit, add the optional `receipt` object to a `field_log.py` entry instead — do not create `receipts.json`. Schema:
   `kind`, `schema_version`, `run_id`, `required`, `actual`, `result` (`honoured`/`mismatch`/`unverifiable`), `evidence`, `recorded_at`. `result` is never `honoured` without both `required` and
   `actual` populated.
5. Register the new script in `scripts/README.md` (purpose, inputs, outputs, safety label, idempotency) and add its row to `manifest.yaml` if it becomes a routinely-run maintenance task.

### Self-verification after this phase

- [ ] `just preflight` exits 0.
- [ ] `scripts/validate_harness_capabilities.py` run against the seeded registry exits 0 on the valid case.
- [ ] Negative fixture: an unknown harness id in the registry causes the validator to fail — confirmed by actually adding one and watching it fail, not by reading the code and assuming it would.
- [ ] Negative fixture: a numeric limit field with no evidence comment causes the validator to fail.
- [ ] Negative fixture: a `receipt` object missing `actual` is rejected, not silently marked `honoured`.
- [ ] `scripts/README.md` and `manifest.yaml` (if applicable) are updated in the same commit — governance coverage check confirms this, not a manual read-through.
- [ ] `docs/README.md` links the generated support table if one was produced.
- [ ] `CHANGELOG.md` gets one entry naming the triggering evidence, the files touched, and the verification results above.
- [ ] Frozen-corpus gate unaffected (this phase should not touch `routing.toml`; if it somehow needs to, the corpus gate above applies and any regression reverts the phase).

## Phase 2 — legal hand-offs

**Trigger (restated):** recorded multi-persona work shows an unknown, missing, or wrongly consumed input/output caused a real decision problem.

### Implementation steps

1. Define a small shared artefact vocabulary as a new TOML table, `[artefact_types]`, in `routing.toml` — enumerate only the artefact types that appear in the actual triggering multi-persona case(s),
   not a speculative complete set.
2. Add optional `consumes`, `produces`, and `will_not` arrays to the `[[personas]]` entries actually involved in the triggering case — not a blanket addition across all personas in one pass.
3. Extend `scripts/validate_agent_stack.py` (the existing structural validator, per [Rule 0006](../../.archcore/rules/0006-required-personas-is-ownership.md) precedent) to reject: an unknown artefact
   vocabulary value, a duplicate value within one persona's list, and — where a `[[handoffs]]` entry exists — a consumer that has not declared the producer's artefact type among its `consumes`.
4. Add `[[handoffs]]` entries only for the specific producer→consumer edge the triggering evidence names: `from`, `to`, `artefact`, `required_fields`, `consumed_by`. No payload field may carry raw
   credentials or an unrestricted transcript — enforce this as a validator rule, not a comment.
5. Where AutoGen's candidate-narrowing discipline applies (see the survey's convergent finding), extend `close_route.py` to narrow the legal candidate set using the new `consumes`/`produces` facts
   *before* the model proposes a route, mirroring the repair-time discipline it already applies after.

### Self-verification after this phase

- [ ] `just preflight` exits 0.
- [ ] Catalogue and payload fixtures pass: a valid hand-off with all required fields validates; an unknown artefact value fails; a producer/consumer mismatch fails; a hand-off missing a required field
  fails.
- [ ] The triggering real case, re-run through the eval harness or replayed manually, now validates correctly where it previously did not — this is the actual proof the phase closed the named gap, not
  an abstract schema test alone.
- [ ] Frozen 60-case corpus gate: run before and after, hard-invariant scores compared. Any new miss reverts the phase. This is mandatory here because `routing.toml` and `close_route.py` are both
  touched.
- [ ] Existing single-persona and direct-skill routes with no hand-off declared still resolve exactly as before — spot-check at least the corpus cases that previously used the touched personas.
- [ ] `skills/skill-agent-stack/SKILL.md`'s routing-contract description is updated to mention `consumes`/`produces`/`will_not` if the orchestrator prompt surfaces persona declarations (check
  `eval-routing-contract` block per [SCRATCHPAD](../../SCRATCHPAD.md) — production and eval prompts must not drift).
- [ ] `CHANGELOG.md` entry naming the specific triggering case, the exact personas/artefacts touched, and the before/after corpus scores.

## Phase 3 — post-dispatch verification

**Trigger (restated):** a saved persona output, recorded via `persona_note.py`'s `MANIFEST.json`, demonstrably rules outside its declared `owns`, or recorded metadata proves a material mismatch.

### Implementation steps

1. Write `scripts/audit_route.py`, read-only, extending `persona_note.py`'s existing `MANIFEST.json` rather than creating a second run log. It compares: the route decision, the confirmed contract (if
   Phase 2 has produced one for that edge), and recorded output metadata.
2. Implement exactly the four statuses from the proposal: `honoured`, `mismatch`, `incomplete`, `unverifiable`. A missing observation is `unverifiable`, never inferred as `honoured`. The audit must
   not attempt to score prose quality, choose a new owner, or alter the route.
3. Add `--audit-all` (or per-run `--run-dir <path>`) invocation modes, mirroring anytools' read-only audit mode.
4. Only if a concurrent claim collision is *separately, actually* observed (not merely plausible): add the one-shot compare-and-swap claim primitive to the run manifest, modelled on Squad's
   `lease_owner`/`lease_expires_at`. This does not start, resume, or retry work — a lease expiring only makes a future operator-authorised claim possible.

### Self-verification after this phase

- [ ] `just preflight` exits 0.
- [ ] Four contract fixtures exist and pass: an `honoured` case, a `mismatch` case, an `incomplete` case (dispatch recorded, no returned output), and an `unverifiable` case (required evidence absent).
- [ ] Negative fixture: the audit does not silently upgrade a `mismatch` or `unverifiable` finding to `honoured` under any input shape tried.
- [ ] The triggering real case is re-audited and now correctly reports `mismatch` (or whatever status the original counterexample actually was) — proof the audit catches the real, already-observed
  failure, not a synthetic stand-in for it.
- [ ] If the claim primitive was added: a one-shot concurrent-process test confirms a live claim is never overwritten, an expired lease does not auto-start work, and the declared route owner in
  `routing.toml` is never mutated by the claim mechanism.
- [ ] `evals/field-log.jsonl` and `MANIFEST.json` remain the only two records — confirm no new competing log file was introduced.
- [ ] `CHANGELOG.md` entry naming the triggering `MANIFEST.json` case and the audit's verdict on it.

## Phase 4 — operator-controlled access and action authorization

**Trigger (restated):** a scoped task exposes an authority or privacy boundary that existing operator authority does not already make clear.

### Implementation steps

1. Add the access-request schema (`kind`, `purpose`, `scope`, `requested_by`, `status`, `operator_decision`) as a durable record format — a proposal/ledger file, not an API or notification service.
2. Implement request creation only. No code path may set `status` to `approved`, `denied`, or `fulfilled` except an explicit operator-invoked step (a CLI flag requiring interactive confirmation, or a
   manual file edit the operator makes themselves).
3. Document the four-row action classification table (internal/reversible, external/read-only, persistent local change, external/irreversible/privileged) at the point of operator review — as
   documentation and a review checklist, not as a new routing gate. Do not wire it into `[[gates]]` or `close_route.py`.
4. Confirm the project-boundary invariant holds: raw persona notes remain project-owned and are never collected, inspected, or copied across projects by any part of this mechanism.

### Self-verification after this phase

- [ ] `just preflight` exits 0.
- [ ] State-transition tests: an agent-created request can reach `pending` only; any attempted programmatic transition to `approved`/`denied`/`fulfilled` fails.
- [ ] Negative fixture: a request payload carrying an environment-variable value or secret-shaped field is rejected.
- [ ] Confirm by code review (not assumption) that no new `[[gates]]` entry or `[[precedence]]` entry was introduced — this phase must not become a routing gate.
- [ ] The specific authority ambiguity that triggered this phase is now resolved by an operator decision recorded against a request object — the concrete proof, not just passing unit tests.
- [ ] `CHANGELOG.md` entry naming the triggering ambiguity and the operator's recorded decision.

## Phase 5 — evidence-gated learning

**Status note:** the underlying mechanism (`field_log.py` → `capability-gaps.jsonl` → `propose_evolution.py`) already exists and is already active. This phase is only "implementation" in the sense of
extending an existing, working pipeline — it is not a new subsystem.

**Trigger (restated):** the established field-log/gap thresholds are met (currently 6/10 field-log entries, 0 capability gaps — not yet met) with named evidence and counterexamples.

### Implementation steps

1. Do not build anything until `propose_evolution.py`'s own ten-entry minimum is reached with real field-log entries — check `evals/field-log.jsonl` line count before doing anything else in this
   phase.
2. When it is reached and a proposal is generated, extend the promotion ladder only if the *existing* ladder (field observation → proposal with receipts → operator review → accepted, scoped
   instruction change with tests → later revalidation) proves insufficient for a real proposal already produced. Do not add a richer lesson-delta format (AWS CAO-style) speculatively.
3. Any addition remains proposal-only. No code path may let a task promote itself, and no lesson may be injected into all future personas merely because it was recalled once.

### Self-verification after this phase

- [ ] `just preflight` exits 0.
- [ ] Proposal-only test: running the evolution proposer against real data produces a document, never a source-file edit.
- [ ] Catalogue regression test: an insufficient-evidence run produces no accepted change.
- [ ] `CHANGELOG.md` entry naming the field-log count at the time the threshold was crossed and the resulting proposal.

## What happens if a verification step fails

A failed checkbox in any phase means that phase is **not complete**. The response is:

1. Revert the specific change that caused the failure — not the whole phase, if the failure is isolable; the whole phase, if it is not.
2. Record the failure and its cause in `CHANGELOG.md` even though the phase did not land — per this project's own rule that a silently-abandoned check is indistinguishable from one that never existed.
3. Do not proceed to the next phase, and do not report the phase as done to the operator, until every checkbox for that phase is genuinely checked against observed output — not asserted from reading
   the code.
4. Where a failure reveals that this document's described mechanics were wrong (not just unimplemented), correct this document in the same pass so the next attempt does not repeat the mistake.

## Sources

- Phase objectives, schemas, and evidence triggers: [reliability adaptation proposal](agent-stack-reliability-adaptation-proposal-20260903_1943.md).
- Verified upstream source pointers per mechanism: proposal's [Verified upstream adaptation map](agent-stack-reliability-adaptation-proposal-20260903_1943.md#verified-upstream-adaptation-map).
- Existing evidence mechanisms this phase plan extends rather than duplicates: [field log](../../evals/field-log.jsonl), [persona-note recorder](../../scripts/persona_note.py), [evolution
  proposer](../../scripts/propose_evolution.py).
- Frozen-corpus gating discipline: [Rule 0013](../../.archcore/rules/0013-trim-against-the-frozen-corpus-as-a-gate.md).
- Safety model this plan must not weaken: [Rule 0001](../../.archcore/rules/0001-safety-model.md).
