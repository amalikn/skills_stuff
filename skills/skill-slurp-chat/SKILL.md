---
name: skill-slurp-chat
description: "Use when the user says /slurp-chat, slurp, slurp in detail or slurp close, before context compaction, or at session closeout."
---

# skill-slurp-chat

A slurp is done when every significant item of the session is findable in two places: the memory backends (memory-keeper, project-context, SCRATCHPAD) **and** the project's governed record (change
log, agent rules, status surfaces). Memory alone is not capture: the next agent reads the repo first.

## Contents

- [Modes](#modes)
- [Step 0 — The clock](#step-0--the-clock)
- [Step 1 — Channel and project ID](#step-1--channel-and-project-id)
- [Step 2 — Read existing state (mandatory before any write)](#step-2--read-existing-state-mandatory-before-any-write)
- [Step 3 — Zone B scan (thorough)](#step-3--zone-b-scan-thorough)
- [Step 4 — Zone A scan (light)](#step-4--zone-a-scan-light)
- [Step 5 — Memory backends](#step-5--memory-backends)
- [Step 6 — Governed record (the step memory-only slurps skip)](#step-6--governed-record-the-step-memory-only-slurps-skip)
- [Step 7 — Checkpoints and SCRATCHPAD](#step-7--checkpoints-and-scratchpad)
- [Step 8 — Closeout mode only](#step-8--closeout-mode-only)
- [Report — the coverage table](#report--the-coverage-table)
- [Red flags — stop and route the item](#red-flags--stop-and-route-the-item)

---

## Modes
- **`/slurp-chat`** — steps 0 to 7
- **`/slurp-chat close`** — same, plus the closeout entry (step 8)

A slurp never commits or pushes unless the user asked for that in the same request.

## Step 0 — The clock
Run `date '+%Y%m%d_%H%M'` before writing anything. Every stamp this slurp writes (keys, checkpoints, change-log entries, SCRATCHPAD lines) comes from that output or a later `date`. Never write a time
you did not read.

## Step 1 — Channel and project ID
Derive the channel from the active repo (e.g. `ansible-wifi`). Never `claude-main`. Get the project ID via `list_projects` if not known.

## Step 2 — Read existing state (mandatory before any write)
```
context_get(channel="<channel>", includeMetadata=true, sort="created_desc", limit=20)
get_project_context(projectId="<id>", channel="<channel>", section="notes", sort="created_desc")
```
Extract the newest memory-keeper and project-context timestamps and the topics each already covers. memory-keeper stores local time, so a `createdAfter` filter in UTC can return nothing: list by
`sort` instead. Also note the newest change-log entry's stamp.

**Zone boundary = the later of the two backend timestamps.** After it is Zone B (unsaved); before it is Zone A (light check). No entries in either backend → the whole conversation is Zone B.

## Step 3 — Zone B scan (thorough)
List every significant item as a numbered **item list**, one line each. Each item has a type:

| Type                  | Examples                                                                                           |
| --------------------- | -------------------------------------------------------------------------------------------------- |
| repo change           | file added or edited, rename, commit                                                               |
| operational event     | backup, restore, data written to a system of record, a production read or write done with approval |
| operator decision     | a choice the user made, with reason and the alternatives turned down                               |
| operator rule         | "from now on", "never", "always": anything that constrains future agent behaviour                  |
| undecided proposal    | options or a design put forward that the user did not decide                                       |
| status change         | work that moves a tracked target, milestone or step                                                |
| finding / error / fix | constraint, tool behaviour, root cause, workaround                                                 |
| open task             | pending work with owner, target and commands                                                       |

Skip chitchat and anything derivable from the repo alone (file contents, git log).

## Step 4 — Zone A scan (light)
For each existing entry, ask only: does the conversation hold specific detail (commands, sizes, names, error text) the entry omits? Yes → update that key, or a clearly titled delta note. No → skip.

## Step 5 — Memory backends
- memory-keeper: `context_save(key="<project>.<topic>", category, priority, channel, value)`. One key per topic. `high` for blockers.
- project-context: `add_note` per Zone B topic; `record_decision` for each operator decision. Never duplicate an existing note.
- Undecided proposals are saved as open, never as decisions.

## Step 6 — Governed record (the step memory-only slurps skip)
Find the project's governed surfaces before writing: its AGENTS.md or CLAUDE.md (change-log rule, working rules), `context-map.yaml` `update_rules`, and any status source of truth (a target map,
tracker, roadmap). Then route every item:

| Item type          | Must land in                                                                                     |
| ------------------ | ------------------------------------------------------------------------------------------------ |
| repo change        | change-log entry, if the project keeps one                                                       |
| operational event  | change-log entry, **even when no repo file changed** (what, where, size or count, how verified)  |
| operator decision  | change-log entry, plus the project's decision surface (register, roadmap) where one exists       |
| operator rule      | the project's agent rules (AGENTS.md working rules or its rules folder)                          |
| undecided proposal | SCRATCHPAD open items and the change log as "proposed, not decided"; never in a decision surface |
| status change      | the status source of truth, then regenerate its derived views                                    |

Run the project's own governance check (e.g. `scripts/check_governance.py`, `just check`) and any status validator afterwards. Fix the project, not the check.

## Step 7 — Checkpoints and SCRATCHPAD
```
context_checkpoint(name="slurp-<YYYYMMDD>-<topic>")
create_checkpoint(projectId, name="slurp-<YYYYMMDD>-<topic>")
```
In the project's `SCRATCHPAD.md` (create via `/skill-ai-it` if missing), update only the sections this session changed, marked `KEEP`: Current state, Open items (add undecided proposals), Key anchors,
Recent decisions, Session history (2–3 bullets), Next actions (replace), Memory pointers (keys, note and checkpoint IDs). No file-change lists, no task detail, no session logs.

## Step 8 — Closeout mode only
One more memory-keeper `progress` entry, key `session.closeout.<YYYYMMDD>.<topic>`: Session / Workstream, Scope, Completed, Files Changed, Decisions, Open Issues, Next Actions, Persistence Status
(memory-keeper, project-context, checkpoints, commits).

## Report — the coverage table
One row per Step 3 item. No cell may be blank: write the destination, or `not needed` with the reason.

| #   | Item | Type | memory-keeper key | project-context | Governed file | Status |
| --- | ---- | ---- | ----------------- | --------------- | ------------- | ------ |

Then: last memory-keeper and project-context timestamps, the boundary used, and how much of the conversation was Zone A and Zone B.

## Red flags — stop and route the item
| Thought                                           | Reality                                                                       |
| ------------------------------------------------- | ----------------------------------------------------------------------------- |
| "No repo file changed, so no change-log entry."   | Operational events are durable; the change log is where the next agent looks. |
| "It is in memory-keeper, so it is captured."      | Memory is not the project's record. Step 6 applies.                           |
| "Nobody decided it, so there is nothing to save." | An undecided proposal is saved as open, or it is lost.                        |
| "The rule is obvious from the code."              | Agents read the rules file, not the code. Write the rule.                     |
| "The status file will be updated next session."   | A stale status source misleads the next reader now.                           |
| "The time is about HH:MM."                        | Run `date`.                                                                   |
