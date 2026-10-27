---
Title: GoalGuard Enforcement and Agent Hooks
Category: reference
Status: current
Authority: >-
  consolidated from the v1.7 handoff §9, §28, §32, research pack 00, 02 (C10-C12) and 06 (Thekedar); hook capabilities are as the sources
  report them, UNVERIFIED against the installed Claude Code and Codex versions
Scope: Where the gate runs, which client blocks, honesty about advisory paths, the Archcore rule, and the Thekedar mechanisms adopted
Last reviewed: 2026-10-27
Summary: >-
  The gate runs at handoff and at supported pre-action hooks; a skill, AGENTS.md or Archcore rule alone enforces nothing. Claude Code's PreToolUse
  is the first adapter; every unintercepted path is declared advisory; protected writes are enforced at GoalGuard's writer, not the hook.
---
# Enforcement and agent hooks

## Enforcement honesty

Neither `SKILL.md`, `AGENTS.md`, an Archcore rule nor a `.gg/` file blocks anything by itself (handoff §32). Enforcement exists only where an executable check runs at a boundary the client actually
calls and its failure stops the action. Everything else is **advisory** and is reported as such (handoff §9.6, F14, GG-423). A pilot passes only on an **observed** allowed action and an **observed**
blocked action (kickoff, completion gate); otherwise it is `PARTIAL`.

## Where the gate runs

1. **Handoff / dispatch** — before an independently dispatched work item starts (handoff §6 Stage C-D).
2. **Material change** — when a new requirement, design enlargement or significant dependency appears; not on every file write, and no model call per write (handoff §6 Stage D).
3. **Session start and resume** — revalidate contract and hub revision; never trust a compacted summary (handoff §32.6).
4. **Pre-action hook** — where the client supports a blocking synchronous hook.

## Clients

| Client      | Claimed capability (sources, UNVERIFIED locally)                                                                  | Pilot role                                                         |
| ----------- | ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| Claude Code | Blocking synchronous `PreToolUse`; `SessionStart`, `PostToolUse`                                                  | **First and only adapter in the pilot** (one agent: handoff §12    |
|             |                                                                                                                   |   Phase 2)                                                         |
| Codex       | `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `Stop`, `SubagentStop`; async hooks cannot block; `apply_patch` | Later phase; never reuse the Claude parser (GG-413)                |
|             |   may carry several files and no `file_path`                                                                      |                                                                    |

Capture real payloads from the installed versions as fixtures before trusting either (pack 03 fixtures, GG-423). Install adapters by merging, never overwriting existing hooks; detect duplicates;
uninstall without deleting GoalGuard data (GG-422).

## What hooks cannot do

A hook sees only the events it receives. Shell writes, symlink traversal, network actions and spawned subagents can bypass file-edit hooks (pack 06 §3C). So: protected state (contract, approvals,
baselines) is enforced at GoalGuard's trusted writer and by file permissions; hooks are a preventive second line. Read-only steps fail open with an alert; protected decisions fail closed.

## Archcore and AGENTS.md rule

Install one short rule in the project's existing Archcore mechanism that points to the single GoalGuard contract; do not duplicate policy at every level (handoff §9, §18, §28). Adapted text:

> Before implementing a new work item, read GoalGuard's owner-approved MVP for this project, the relevant Enterprise-Strategy hub decisions and the live Vikunja task, and map the item to one
> acceptance criterion. Do not implement excluded or unapproved features; send useful but unnecessary ideas to GoalGuard as PARK and necessary scope changes as REVIEW. Management commitments are
> protected baselines, not task due dates. If authority is missing, stale or conflicting, stop the affected work. Never import sibling-project or `me` context. Do not report delivery until the
> evidence gate passes.

Archcore inheritance into nested folders is unproven (handoff §18, P08, F04); the adapter resolves and injects policy explicitly. `smc-resiliency` has no `.archcore/` (checked 2026-10-27).

## Thekedar mechanisms adopted (MIT, ideas only unless code is copied)

| Mechanism            | GoalGuard form                                                                                          | Phase                        | Tests           |
| -------------------- | ------------------------------------------------------------------------------------------------------- | ---------------------------- | --------------- |
| Pre-edit scope guard | Semantic criterion gate **first**, file allowlist second; canonicalise paths; unknown → REVIEW          | pilot gate; file scope later | GG-401-407, 412 |
| Session brief        | Bounded SessionStart snapshot: goal, contract revision, focus, task, stop criterion, last verified work | later                        | GG-414          |
| Facts-only ledger    | Normalised events with IDs, deduplicated, single writer; Markdown only as a generated view              | later                        | GG-416-418      |
| Drift audit          | Task-start Git baseline (commit + dirty snapshot); `--porcelain=v1 -z`; pre-existing changes not blamed | later                        | GG-409-411      |
| Completion record    | Changed, deliberately unchanged, evidence per criterion                                                 | pilot                        | GG-419          |
| Bounded fix loop     | Attempts and time budget, then BLOCKED/REVIEW                                                           | later                        | GG-420          |
| Doctor               | Hook wiring, schema, stale leases, payload fixtures; never writes the production ledger                 | minimal in pilot             | GG-421          |

Not imported: the orchestrator, the 109 specialist agents, the reviewer pipeline, the writable task Markdown as state, the `.thekedar/**` self-edit exemption (pack 06 §1, §6). Copying source requires
the pinned upstream commit, file SHAs and an MIT notice (GG-425).
