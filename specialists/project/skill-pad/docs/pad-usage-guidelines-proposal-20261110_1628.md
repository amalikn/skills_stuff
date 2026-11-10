---
Title: Pad usage guidelines (proposal)
Category: proposal
Status: draft
Authority: >-
  Proposal for the operator's decision; nothing here is in force until the operator approves it. Pad facts are VERIFIED_PRIMARY against CLI v0.19.2
  and the upstream sources in references/upstream/ unless marked otherwise.
Scope: How agents and the operator use Pad in apn project workspaces; smc-resiliency is the pilot, unified-network-controller already runs a trial
Last reviewed: 2026-11-10
Summary: >-
  Pad holds two things: every ask of the operator, in an Asks collection routed to the needs-you inbox, and the agent's current-focus queue of plans
  and tasks that point at the repo trackers. Rewritten 2026-11-10 after a review against both live workspaces: closable Asks schema, no tracker tags,
  dates in fields, a degraded mode when Pad is down, and one joint trial review.
---

# Pad usage guidelines (proposal)

Operator, 2026-11-10: "How do you intend to use Pad? Only for listing the things you want my input in, or also plans and tasks for a project? Come up with guidelines so it can be used efficiently."

**Short answer.** Both. Pad holds (1) every ask of the operator, in its own collection that Pad routes to the needs-you inbox, and (2) the agent's queue for the current focus, as plans and tasks that
name their tracker entry. The repo trackers stay the truth (convention `trackers-truth`). Pad holds what is next, who it waits on, and what an agent did between sessions. Features and commands are in
this pack's references: [items-and-edits.md](../references/items-and-edits.md), [playbooks-and-workflows.md](../references/playbooks-and-workflows.md), [cli-reference.md](../references/cli-reference.md).

```text
PAD OVER THE TRACKERS: the repo holds every fact; Pad holds the queue and the asks

+----------------------------+   item names its entry   +------------------------------+
| project repo (truth)       |<-------------------------| Pad workspace (queue)        |
|  trackers, ROADMAP,        |                          |  Plans --> Tasks (agents)    |
|  SCRATCHPAD, decisions     |<-------------------------|  Asks (the operator)         |
+----------------------------+   pad_export.py copy     +------------------------------+
                                                           |                      |
                                                           | open asks            | pad db backup
                                                           v                      v 02:30 nightly
                                                 +------------------+   +-------------------+
                                                 | needs-you inbox  |   | OneDrive backups  |
                                                 | (web, catch-up)  |   | newest 30 (Q6)    |
                                                 +------------------+   +-------------------+

Legend: --> from the side that refers, copies or sends, to its target
```

## Contents

- [1. Where things stand](#1-where-things-stand)
- [2. Principles](#2-principles)
- [3. The model](#3-the-model)
- [4. When Pad is down, and recovery](#4-when-pad-is-down-and-recovery)
- [5. Use cases](#5-use-cases)
- [6. Rollout](#6-rollout)
- [7. Decisions for the operator](#7-decisions-for-the-operator)
- [8. Review changes](#8-review-changes)

---

## 1. Where things stand

Read 2026-11-10 from `pad bootstrap` and `pad item list --all` in both workspaces:

| Workspace                  | Template | Plans    | Tasks           | Other                              | Waits on the operator mixed into tasks |
| -------------------------- | -------- | -------- | --------------- | ---------------------------------- | -------------------------------------- |
| smc-resiliency (pilot)     | startup  | 4 active | 16 open, 1 done | 5 conventions, 4 playbooks         | 5 (decisions, an approval, bench work) |
| unified-network-controller | startup  | 3 active | 9 open, 2 done  | 1 idea; 5 conventions, 4 playbooks | 2 (a stakeholder review, TASK-20)      |

What already works: every task names its tracker entry on its first line; status changes carry comments; parents are plans. What does not: nothing separates the operator's asks from agent work; due
dates sit in body text (UNC TASK-12 "Due Fri 20 Nov") so Pad cannot flag them overdue; no tags, roles or asks. UNC TASK-20 already holds a review of the Pad trial on or after 17 Nov.

## 2. Principles

1. **The repo is the truth; Pad is the queue.** An item names its tracker entry on its first line (stage criterion, bug ID, open-item stamp, decision record). Status lands in the tracker first, then
   in Pad. Pad never holds the only copy of a fact, decision or result.
2. **Asks are separate from work.** Anything that needs the operator (a decision, an approval of a production write, hands-on bench work, a review, a fact) is an ask, so the operator's list is one
   inbox, not a search.
3. **Small and current.** Pad holds the next one to two weeks, not the backlog: at most five active plans; a task is one session or less; an item nobody will touch within a month is closed or becomes
   an idea.
4. **Every change says why.** Status changes carry `--comment`; work done goes in `note`; a choice goes in the repo decision record and `decide` points at it.
5. **Private by default.** Site and box names and fleet findings stay in the local workspace and the project's repo. No share links, cloud workspaces or outbound webhooks without the operator. The
   backup copy is the one stated exception (Q6).
6. **Pad is not on the critical path.** Agents use Pad when it answers and the trackers when it does not (section 4).

## 3. The model

### 3.1 Collections

| Collection             | Holds                                                                                    | Change                            |
| ---------------------- | ---------------------------------------------------------------------------------------- | --------------------------------- |
| **Asks** (new, ASK)    | Every item waiting on the operator                                                       | create (schema below)             |
| Plans                  | One plan per current timeline focus (a roadmap step, a survey follow-up, an audit batch) | keep                              |
| Tasks                  | Agent work, and operator hands-on work that is not a question                            | keep; move pure decisions to Asks |
| Ideas                  | Proposals not yet on the timeline                                                        | start using                       |
| Docs                   | Unused: documents live in the repo                                                       | leave empty                       |
| Conventions, Playbooks | Rules and procedures (3.6, 3.7)                                                          | extend                            |

Asks must be created with `--schema`, not `--fields`: the DSL cannot declare which statuses close an item, and Pad would then treat `answered` as open forever ([cli-reference.md](../references/cli-reference.md), Traps). `--tracks-work
false` keeps answered asks out of changelog, standup and progress counts.

```bash
pad collection create "Asks" --awaits-human true --tracks-work false --schema @asks-schema.json
pad collection update asks --prefix ASK          # create has no --prefix flag
```

```json
{"fields": [
  {"key": "status", "type": "select", "options": ["open", "answered", "withdrawn"], "terminal_options": ["answered", "withdrawn"],
   "abandoned_options": ["withdrawn"], "default": "open", "required": true},
  {"key": "kind", "type": "select", "options": ["decision", "approval", "bench", "review", "info"], "default": "decision"},
  {"key": "priority", "type": "select", "options": ["low", "medium", "high", "critical"], "default": "medium"},
  {"key": "due_date", "type": "date"},
  {"key": "answer", "type": "text"}
]}
```

`priority` and `due_date` reuse the task field names, so `next`, `stale`, the dashboard and `pad_export.py` treat asks like tasks (critical = blocks production work now). Routing: an open item in an
`awaits_human` collection reaches its assignee's needs-you inbox, and an unassigned one reaches the workspace owner, so in a single-operator workspace assigning is optional. The inbox has no CLI
command; `pad project catch-up` shows its needs-you section.

An ask body has four parts, so it can be answered from the inbox:

```markdown
**Question:** one sentence.
**Options:** A. ... (recommended, why) / B. ... / C. ...
**Blocks:** TASK-N; tracker entry.
**Evidence:** repo paths or a decision draft; what was checked and what was not.
```

The agent links the ask to the work it holds up (`pad item block ASK-N TASK-M`): the task leaves `next` and shows in `stale`. On the answer, the agent records it in the repo first, then sets `answer`,
`status=answered` with a comment citing where it was recorded, and unblocks the task.

```text
ASK LIFECYCLE: an open ask blocks its task; the answer reaches the repo before Pad

+------------------+    block    +-------------------------+
| ASK-N open       |------------>| TASK-M blocked          |
| (needs-you)      |             | out of next, in stale   |
+------------------+             +-------------------------+
         |                                    ^
         | operator answers                   | unblock
         v                                    |
+------------------+    then     +-------------------------+
| answer recorded  |------------>| ASK-N answered (closed) |
| in the repo      |             | answer field, comment   |
+------------------+             | cites the record        |
                                 +-------------------------+

withdrawn: ASK-N closes without delivering; TASK-M is unblocked or cancelled with the reason
```

### 3.2 Plans and tasks

- **Plan:** one per current focus; its first line names the timeline entry; `end_date` set to the timeline's date; `active` only in the current fortnight, otherwise `planned` or `paused`.
- **Task:** one session or less; first line names the tracker entry; `priority` set; `due_date` set when the tracker has a date (never only in the body). Bigger than a session: split it (`pad item
  split-from`).
- **Parent:** under a plan, except housekeeping (tool pins, refactors, skill reviews), which may stay parentless rather than live under a plan that never ends.
- **Status is the work, the lease is the lock.** open, in-progress (work started, part-done), done (tracker updated and `just check` passed), cancelled (with the reason). A claim (`pad item claim`,
  15-minute default) only stops two sessions colliding; it expires on its own, so status never depends on it. Waiting on the operator is not a status: it is a blocking ask.
- **Priority:** critical = production at risk now; high = on the current timeline step; medium = this month; low = could slip.
- **Roles:** off until two agents work one workspace in parallel (Q3).

### 3.3 Tags

Tracker IDs are not tags: the first line already carries them, and a second copy drifts. Tags mark only what cuts across plans:

| Tag               | Meaning                                                 |
| ----------------- | ------------------------------------------------------- |
| `prod-write`      | Touches a production box: an approval ask comes first   |
| `bench`           | Needs the bench or lab hardware                         |
| `hub`             | Belongs partly to another project, sent through the hub |
| `skill-writeback` | Owes a write-back to a skill pack                       |

A new tag is added here first; `pad tag list` shows drift.

### 3.4 Notes, decisions, reminders, watches

- `note`: at the end of each session on an item, what was done and the commit.
- `decide`: only to point at the repo decision record.
- `remind`: when the agent must come back (a scheduled run to verify, a review date), at a time of day; a fired reminder heads `next` until `pad item ack`.
- `watch`: the operator's, to follow an item until done; agents do not create watches.

### 3.4a Pushes are nudges, not records

A push (`pad push <ref> -m ...`) reaches only a session whose stream is running at that moment; Pad keeps no inbox, so a push sent during a gap is lost
([modes.md](../references/modes.md), Delivery limits). Anything that must not be lost is an item: an ask, a task or a comment. A push only says "look
at this now", and the item still holds the instruction if the push was missed.

### 3.5 What Pad is not for

Not a copy of the trackers, ROADMAP or SCRATCHPAD; not for long design text (it lives in `docs/`, the item links it); never secrets, credentials or customer data; not a cross-project channel (messages
go through the hub; an item may record that one was sent).

### 3.6 Conventions to add to the apn baseline

Added to `conventions/apn-baseline.toml` and applied with `scripts/pad_conventions.py` (plan, then `--apply`):

| id                 | Rule                                                                         | Trigger          | Priority |
| ------------------ | ---------------------------------------------------------------------------- | ---------------- | -------- |
| asks-for-input     | Ask the operator through an ASK item, never only in chat                     | always           | must     |
| prod-write-ask     | A production write waits on an answered approval ask (tag `prod-write`)      | on-task-start    | must     |
| task-names-tracker | A plan or task names its tracker entry on its first line; dates in fields    | always           | must     |
| session-start      | Start with `pad project next` (trackers if Pad does not answer); claim first | on-task-start    | should   |
| session-close      | Note each worked item, raise asks, run `just pad-export`                     | on-task-complete | should   |

### 3.7 Playbooks and scripts

| Name                   | Kind                         | What it does                                                                                                                                 |
| ---------------------- | ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `ask`                  | playbook                     | Create an ask with the four-part body, set priority and due date, block the work it holds up                                                 |
| `answer`               | playbook                     | Repo record first, then `answer`, status, unblock, note                                                                                      |
| `triage-findings`      | playbook                     | Turn survey or audit findings into a plan with tasks and asks, dry-run first                                                                 |
| `pad_tracker_drift.py` | skill-pad script             | Compare each item's first-line tracker reference with the tracker; list drift both ways (closed there, open here, and the reverse);          |
|                        |   (skill-coder rules)        |   read-only, tested, run by a `sync-trackers` playbook and by `just check` as a warning                                                      |

Drift detection is a script, not playbook prose, because it must give the same answer every run. `pad_export.py` gains an ask column set (kind, due date) when Asks exist.

## 4. When Pad is down, and recovery

Pad's data lives on malik1tb (`~/.pad` is a link to it); the server runs on this Mac only.

| Failure                           | Effect                                 | What agents do                                                                                                          |
| --------------------------------- | -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| malik1tb not mounted, server down | every `pad` call fails or hangs        | work from the trackers and the last `pad-focus.md` export; record asks in SCRATCHPAD open items; add them to Pad when   |
|                                   |                                        |   it is back                                                                                                            |
| pad.db damaged or lost            | items, comments, history gone          | `pad db restore` from the newest nightly backup (loss up to 24 hours); the trackers hold every fact                     |
| Backup job failing silently       | the next restore is older              | the backup log and file dates are checked weekly (rollout step 7)                                                       |
|                                   |   than expected                        |                                                                                                                         |

```text
SESSION START WHEN PAD MAY BE DOWN: Pad when it answers, the trackers when it does not

+------------------+   answers   +--------------------------------+
| pad project next |------------>| work the queue; claim first    |
+------------------+             +--------------------------------+
         |
         X no answer (malik1tb not mounted, server down)
         v
+--------------------------------+   Pad back   +--------------------------------+
| work from the trackers and the |------------->| add the asks noted in          |
| last pad-focus.md export; asks |              | SCRATCHPAD; note the work done |
| go to SCRATCHPAD open items    |              +--------------------------------+
+--------------------------------+

Legend: X failed call
```

A backup is not a recovery until a restore has been shown to work: rollout step 1 restores the newest backup into a scratch `PAD_DATA_DIR` and compares item counts with the live workspace.

## 5. Use cases

| #   | Trigger                           | Agent does                                                                                                          | Operator sees                        |
| --- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| UC1 | A design choice the agent may     | Draft options in the repo; `ask` (decision); block the task                                                         | one ask in needs-you; answers there  |
|     |   not make                        |                                                                                                                     |                                      |
| UC2 | A production write is needed      | Task tagged `prod-write`; `ask` (approval) with commands, pre-checks, rollback; writes nothing until answered; one  | an approval ask per batch            |
|     |                                   |   ask per batch after the canary                                                                                    |                                      |
| UC3 | Hands-on bench work               | Task assigned to the operator, tag `bench`, exact commands; an ask (bench) only if follow-on work waits on it       | a task, or an ask when it blocks     |
| UC4 | A review with a date              | `ask` (review) with `due_date`, reminder the morning before; if missed, raise it at session start                   | a dated ask; overdue if missed       |
| UC5 | Survey or audit findings          | `triage-findings`, dry-run first: one plan, a task per finding needing work, an ask per finding needing a decision  | the plan and its asks                |
| UC6 | Two sessions at once              | Each registers and claims before working; `lease_held` means pick another item                                      | nothing                              |
| UC7 | Something to check later          | Reminder on the task; it heads `next` when it fires; note the result, ack                                           | nothing unless it fails              |
| UC8 | Work shared with another project  | Tag `hub`; send the hub message; note it; the other project tracks its part in its own workspace                    | the hub message                      |
| UC9 | Morning catch-up                  | —                                                                                                                   | `pad project catch-up`, then         |
|     |                                   |                                                                                                                     |   needs-you across all workspaces    |

## 6. Rollout

Each step plans first and needs the operator's go. Pilot: smc-resiliency; UNC is already on a trial.

| Step | What                                                                                                                            | Check                                                  |
| ---- | ------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| 0    | Operator answers section 7                                                                                                      | answers recorded here                                  |
| 1    | Restore test: newest backup into a scratch `PAD_DATA_DIR`                                                                       | item counts match the live workspaces                  |
| 2    | Create Asks in smc-resiliency (3.1 schema); one test ask end to end                                                             | it shows in catch-up's needs-you; `answered` closes it |
| 3    | Move today's waits to asks and block their tasks; move body dates into `due_date`                                               | `pad project next` offers no blocked task              |
| 4    | Tags (3.3), conventions (3.6), playbooks (3.7) with `--field status=active`                                                     | `pad bootstrap` lists them                             |
| 5    | `pad_tracker_drift.py` and the export ask columns (skill-coder: tests, plan by default)                                         | `just check` in skill-pad; a drift run on the pilot    |
| 6    | One joint review of both workspaces through UNC TASK-20 (on or after 17 Nov): asks raised and answered, wait times, drift found | keep, trim or drop; result in this file                |
| 7    | If kept: the same steps in UNC from its own session; weekly backup check                                                        | its bootstrap; backup log dates                        |

## 7. Decisions for the operator

| #   | Question                            | Options                                                                                                                                               |
| --- | ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Q1  | Where do asks live?                 | **A. Asks collection (recommended)** / B. @mentions on tasks (a mention closes on any later comment from you, answered or not) / C. tasks assigned to you |
| Q2  | How much work goes into Pad?        | **A. Current focus, next one to two weeks (recommended)** / B. every open tracker item / C. asks only                                                 |
| Q3  | Agent roles?                        | **A. None until two agents work in parallel (recommended)** / B. implementer and reviewer now                                                         |
| Q4  | How do you answer an ask?           | **A. On the ask; the agent records it (recommended)** / B. in the session chat; the agent creates the ask record / C. both                            |
| Q5  | When to roll out to UNC and others? | **A. After the joint review through UNC TASK-20 (recommended)** / B. now, together                                                                    |
| Q6  | The nightly backup goes to OneDrive | **A. Keep, as the stated exception to "private by default" (recommended)** / B. encrypt before upload / C. a local disk only                          |

## 8. Review changes

Rewritten 2026-11-10 after a review against both live workspaces and the CLI (skill-systems-architect, skill-coder). Previous text: commit history of this file. Changes: the Asks schema now declares
its closed statuses and is created with `--schema` and `--tracks-work false`; site and box names removed (they stay in the projects); one joint trial review through UNC TASK-20 instead of a separate
two-week pilot; tracker-ID tags dropped; dates moved from body text to `due_date` and `end_date`; status separated from the claim; parentless housekeeping tasks allowed; a degraded mode, a restore
test and the backup's cloud copy (Q6) added; tracker sync became a tested script; the feature catalogue moved to the pack's references.
