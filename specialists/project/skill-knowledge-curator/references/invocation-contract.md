---
Title: Invocation contract
Category: reference
Status: current
Authority: local-supplement; handoff sections 4 and 6 (invocation-contract); schemas/intake-payload.schema.json; operator decision 2026-10-27 to wire slurp after the pilot
Scope: Direct invocation, the optional skill-slurp-chat Step 4b call, payload and response, trigger rules and failure handling
Last reviewed: 2026-10-27
Summary: >-
  Direct use runs the workflow on a project; slurp's optional Step 4b sends its already-collected items and gets one outcome per item for its Step 6b audit.
  The slurp wiring is documented now and installed only after the pilot passes. Settles source conflict C10.
---

# Invocation contract

## Contents

- [Direct invocation](#direct-invocation)
- [From skill-slurp-chat (Step 4b, after the pilot)](#from-skill-slurp-chat-step-4b-after-the-pilot)
- [Payload and response](#payload-and-response)
- [Failure handling](#failure-handling)

## Direct invocation

The operator or an agent invokes the skill on a project or a subset ("curate the docs in X", "are these notes contradicting each other", "what is the current design of Y"). It runs the [workflow](workflow.md):
read-only until `--apply`; source documents and governing files are never edited.

## From skill-slurp-chat (Step 4b, after the pilot)

Status: **not wired.** The operator chose to wire it after the standalone pilot passes (2026-10-27). The intended contract:

```text
  skill-slurp-chat                              skill-knowledge-curator
  Steps 0-4: read state, extract typed items
        |
        |  knowledge-bearing items present?  -- no --> Steps 5-8 as today
        | yes
        v
  Step 4b: write payload.json  ------------->  kc intake --project P --payload payload.json
                                                 (read-only; one outcome per item)
        <-------------------------------------  response: findings, routing_hints, trace
        |
        v
  Steps 5-8 unchanged: slurp writes memory and governed records itself;
  Step 6b audits each item_id against the trace
```

- **Trigger:** items that are knowledge-bearing (decisions, facts, requirements, design statements) and look new, overlapping, contradicting or stale, or the operator asks for full curation. Routine
  progress, operations and status changes do not call it.
- **Input:** the Step 3 item list with source pointers, not a second transcript scan.
- **Authority:** slurp keeps Step 3 coverage and Step 6 routing; the curator only advises. A `review_required` finding is recorded by slurp as an open item, never as a settled fact.
- **Mechanism:** reuse slurp's existing skill-to-skill call style (a shell call to `kc intake`); no MCP dependency.

## Payload and response

Payload ([schemas/intake-payload.schema.json](../schemas/intake-payload.schema.json)):

```json
{"schema_version": "1.0", "mode": "slurp", "read_only": true, "project_root": "/path/to/project",
 "items": [{"item_id": "slurp-001", "type": "operator decision", "text": "...", "source_ref": "..."}]}
```

Response:

```json
{"schema_version": "1.0", "status": "completed",
 "findings": [{"finding_id": "finding-001", "item_ids": ["slurp-001"], "type": "conflict", "disposition": "review_required",
               "claim_ids": ["cl-..."], "conflict_ids": ["cf-..."], "sources": [], "reason": "matches a disputed claim"}],
 "proposed_records": [], "routing_hints": ["route slurp-001 to the review queue"],
 "trace": [{"item_id": "slurp-001", "outcome": "conflict", "finding_id": "finding-001"}], "errors": []}
```

Finding types: `skipped` (routine type: progress, status, operation, command, routine), `new_knowledge` (no matching claim: extract it), `matches_current`, `matches_history`, `matches_unsettled`,
`conflict`. Matching is RapidFuzz similarity of at least 85 against claim text. The trace has exactly one row per input `item_id`. A payload failing the schema (including `read_only` not true) returns
`status: rejected` with the errors and no findings: unknown formats are never guessed into records.

## Failure handling

If the curator is missing or fails, slurp still records its items in its usual destinations and reports `curation_skipped` or `curation_failed`; it never marks a disputed claim authoritative because
curation did not run.
