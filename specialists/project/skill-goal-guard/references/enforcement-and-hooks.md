---
Title: Goal Guard Enforcement and Agent Hooks
Category: reference
Status: current
Authority: >-
  consolidated from the v1.7 handoff §9, §28, §32, research pack 00, 02 (C10-C12) and 06 (Thekedar); hook capabilities are as the sources
  report them, UNVERIFIED against the installed Claude Code and Codex versions
Scope: Where the gate runs, which client blocks, honesty about advisory paths, the Archcore rule, and the Thekedar mechanisms adopted
Last reviewed: 2026-10-27
Summary: >-
  The gate runs at handoff and at supported pre-action hooks; a skill, AGENTS.md or Archcore rule alone enforces nothing. Claude Code's PreToolUse
  is the first adapter; every unintercepted path is declared advisory; protected writes are enforced at Goal Guard's writer, not the hook.
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
uninstall without deleting Goal Guard data (GG-422).

## What hooks cannot do

A hook sees only the events it receives. Shell writes, symlink traversal, network actions and spawned subagents can bypass file-edit hooks (pack 06 §3C). So: protected state (contract, approvals,
baselines) is enforced at Goal Guard's trusted writer and by file permissions; hooks are a preventive second line. Read-only steps fail open with an alert; protected decisions fail closed.

## Archcore and AGENTS.md rule

Install one short rule in the project's existing Archcore mechanism that points to the single Goal Guard contract; do not duplicate policy at every level (handoff §9, §18, §28). Adapted text:

> Before implementing a new work item, read Goal Guard's owner-approved MVP for this project, the relevant Enterprise-Strategy hub decisions and the live Vikunja task, and map the item to one
> acceptance criterion. Do not implement excluded or unapproved features; send useful but unnecessary ideas to Goal Guard as PARK and necessary scope changes as REVIEW. Management commitments are
> protected baselines, not task due dates. If authority is missing, stale or conflicting, stop the affected work. Never import sibling-project or `me` context. Do not report delivery until the
> evidence gate passes.

Archcore inheritance into nested folders is unproven (handoff §18, P08, F04); the adapter resolves and injects policy explicitly. `smc-resiliency` has no `.archcore/` (checked 2026-10-27).

## Thekedar mechanisms adopted (MIT, ideas only unless code is copied)

| Mechanism            | Goal Guard form                                                                                          | Phase                        | Tests           |
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

## Learned

> **Learned 2026-10-27** · Claude Code 2.1.310 hooks · VERIFIED_PRIMARY for the documentation, UNVERIFIED on this machine · Source: https://code.claude.com/docs/en/hooks (read 2026-10-27);
> `scripts/goal_guard_lib/hook.py` · Falsifier: a captured PreToolUse payload without `tool_input.file_path` for Write, or an exit-2 hook whose tool call still runs PreToolUse input carries
> `session_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name`, `tool_name`, `tool_input` (Write: `file_path`, `content`) and `tool_use_id`. Exit 2 blocks the call and stderr becomes
> the reason; JSON on stdout cannot override an exit 2. On exit 0, `hookSpecificOutput.permissionDecision` (allow, deny, ask, defer) decides, deny > defer > ask > allow across hooks, and
> `additionalContext` reaches the model. Printing `allow` skips the user's permission prompt, so the Goal Guard hook prints nothing when it passes. Any exit code other than 0 or 2 is a non-blocking
> error, so the hook turns its own crashes into a denial. Timeouts are in seconds (600 by default for PreToolUse command hooks).
>
> ```python
> # scripts/goal_guard_hook.py (2026-10-27, uncommitted)
> try:
>   outcome = hook.evaluate(payload, cfg, args.mode, now)
> except Exception as err:  # a bug here must not let a write through: exit 1 is a non-blocking error in Claude Code
>   outcome = hook.deny(args.mode, f"internal error {type(err).__name__}: {err}; failing closed")
> ```

> **Learned 2026-10-27** · Goal Guard hook design · USER_STATED (review note relayed to the operator) · Source: `scripts/goal_guard_lib/hook.py` `_verdict_gap` · Falsifier: a blocking-mode
> run that lets an edit through to a file the last PROCEED did not list One PROCEED verdict must not unlock the whole project. The verdict carries its proposal's `proposed_files`; the hook passes only
> those files, only for `GG_VERDICT_MAX_HOURS` (2 by default) and only against the current contract revision. The agent still writes its own proposal, so the gate bounds what it may touch; it does not
> stop it proposing.
