---
Title: Pad usage guidelines (proposal)
Category: proposal
Status: draft
Authority: >-
  Proposal for the operator's decision; nothing here is in force until the operator approves it. Feature facts come from Pad v0.19.2 (CLI help and the
  upstream docs saved under references/upstream/).
Scope: How agents and the operator use Pad in apn project workspaces (smc-resiliency first, then unified-network-controller and the rest)
Last reviewed: 2026-11-10
Summary: >-
  What Pad offers at each level (workspace, collection, plan, task, convention, playbook, cross-session), what the smc-resiliency workspace uses today,
  and a proposed model: a needs-you Asks collection for operator input, plans and tasks as the personal queue over the repo trackers, a tag vocabulary,
  conventions and playbooks, ten worked use cases, a phased rollout and the questions the operator decides.
---

# Pad usage guidelines (proposal)

Operator, 2026-11-10: "How do you intend to use Pad? Only for listing the things you want my input in, or also plans and tasks for a project? Come up with guidelines so it can be used efficiently."
This is the answer, as a proposal to approve or amend.

**Short answer.** Both, with different weights. Pad becomes the place where (1) every ask of the operator lives, in its own collection that Pad routes to the operator's needs-you inbox, and (2) the
agent's working queue for the current focus lives, as plans and tasks that point at the repo trackers. The repo trackers stay the truth ([CONVE-9](#part-2-current-state)); Pad holds what is next, who it waits on, and the
trail of what an agent did between sessions.

## Contents

- [Part 1: What Pad offers](#part-1-what-pad-offers)
- [Part 2: Current state](#part-2-current-state)
- [Part 3: Principles](#part-3-principles)
- [Part 4: The proposed model](#part-4-the-proposed-model)
- [Part 5: Use cases](#part-5-use-cases)
- [Part 6: Rollout plan](#part-6-rollout-plan)
- [Part 7: Decisions for the operator](#part-7-decisions-for-the-operator)
- [Sources](#sources)

---

## Part 1: What Pad offers

Every row is VERIFIED_PRIMARY against Pad v0.19.2 (installed CLI `pad <cmd> --help`, and the upstream docs saved in [upstream/](upstream/readme.md)) unless it says otherwise. "Used" says whether the smc-resiliency
workspace uses it today.

### 1.1 Workspace level

| Feature           | What it does                                                                                        | Command or surface                         | Used                          |
| ----------------- | --------------------------------------------------------------------------------------------------- | ------------------------------------------ | ----------------------------- |
| Workspace         | `.pad.toml` links a project folder to one workspace; every `pad` call there resolves it             | `pad workspace init`, `.pad.toml`          | yes (smc-resiliency,          |
|   per folder      |                                                                                                     |                                            |   unified-network-controller) |
| Templates         | startup, scrum, product, spec, hiring, interviewing, blank; each seeds collections, conventions     | `pad workspace init --list-templates`      | startup                       |
|                   |   and playbooks                                                                                     |                                            |                               |
| Bootstrap         | One call returns workspace, collections, always-on conventions, convention index, roles, playbook   | `pad bootstrap --format json`              | yes (agents)                  |
|                   |   metadata, dashboard                                                                               |                                            |                               |
| Dashboard         | Counts by status, active plans with progress, attention (stalled, overdue, blocked), suggested      | `pad project dashboard`, web home          | yes                           |
|                   |   next, recent activity                                                                             |                                            |                               |
| Next / ready      | Up to three ranked items: fired reminders, overdue, in-progress, open items in active plans, high   | `pad project next`, `pad project ready`    | no                            |
|                   |   or critical priority; blocked items never listed                                                  |                                            |                               |
| Stale             | Stalled, blocked, overdue or orphaned items                                                         | `pad project stale`                        | no                            |
| Catch-up digest   | Since you last pressed Mark caught up (14 days max): needs you, finished, new and reopened,         | `pad project catch-up`; Mark caught up     | no                            |
|                   |   comments, what agents did                                                                         |   is web-only                              |                               |
| Needs-you inbox   | Open items that need a person, across every workspace; routed by ask collections, @mentions,        | web inbox; API `GET /api/v1/me/needs`; no  | no                            |
|                   |   assignment, owner fallback; per-user snooze                                                       |   CLI command (full cmdhelp tree);         |                               |
|                   |                                                                                                     |   `project catch-up` shows a               |                               |
|                   |                                                                                                     |   needs-you section                        |                               |
| Standup,          | Generated from recent activity and completed items                                                  | `pad project standup`,                     | no                            |
|   changelog       |                                                                                                     |   `pad project changelog`                  |                               |
| Insights / report | Windowed created vs completed, net flow, completion by collection, status mix; web adds cycle time, | `pad project report --window week`         | no                            |
|                   |   WIP ageing, time travel, print view                                                               |                                            |                               |
| Activity feed     | What users and agents changed, filterable by actor and date                                         | `pad project activity`,                    | no                            |
|                   |                                                                                                     |   `pad project watch` (stream)             |                               |
| Search, tags      | Full-text search over all items; tags are free labels across collections                            | `pad item search`, `pad tag list`          | search only                   |
| Share link        | A collection as a public read-only page at `/s/<token>` with its saved views                        | web UI                                     | no (and should stay off: see  |
|                   |                                                                                                     |                                            |   Part 3)                     |
| Library           | Pad's stock conventions and playbooks, diffable against the workspace copy                          | `pad library list`, `diff`,                | yes (four playbooks)          |
|                   |                                                                                                     |   `activate`, `update`                     |                               |
| Backup            | pad.db for all workspaces                                                                           | skill-pad `scripts/pad_backup.sh`          | yes                           |
|                   |                                                                                                     |   (launchd 02:30)                          |                               |

### 1.2 Collection level

| Feature         | What it does                                                                                                | Command                                       | Used                 |
| --------------- | ----------------------------------------------------------------------------------------------------------- | --------------------------------------------- | -------------------- |
| Schema fields   | text, select, multi_select, number, date, checkbox, url, relation (to another collection)                   | `pad collection create/update --fields`       | template fields only |
|                 |                                                                                                             |   or `--schema`                               |                      |
| Issue-ID prefix | Short stable IDs (TASK-5); a prefix can be changed                                                          | `pad collection update --prefix`              | default              |
| `awaits_human`  | The collection's items are asks of a person: an open, assigned item routes to that person's needs-you inbox | `--awaits-human true`                         | **no**               |
| `tracks_work`   | `false` makes a collection reference material: no parent progress, never blocks a parent from closing, out  | `--tracks-work false`                         | no                   |
|                 |   of default reports                                                                                        |                                               |                      |
| Views           | Board (default, grouped by `board_group_by`), list, table; layout fields-primary, content-primary, balanced | `--default-view`,                             | default              |
|                 |                                                                                                             |   `--board-group-by`, `--layout`              |                      |
| Move between    | Item keeps matching fields; others dropped or set with `--field`                                            | `pad item move <ref> <collection>`            | no                   |
|   collections   |                                                                                                             |                                               |                      |

### 1.3 Plan level

| Feature                      | What it does                                                                    | Command                                              | Used              |
| ---------------------------- | ------------------------------------------------------------------------------- | ---------------------------------------------------- | ----------------- |
| Plan item                    | status planned, active, completed, paused; start and end dates                  | `pad item create plan`                               | yes (4 active)    |
| Computed progress            | Percentage from child items (work collections only)                             | automatic                                            | yes               |
| Open-children guard          | A plan cannot close while a child is open unless `--force`                      | `pad item update --status completed`                 | yes               |
| Plan and decompose playbooks | Co-design a plan; turn a plan into child tasks with dependencies, dry-run first | `/pad plan <topic>`, `/pad decompose PLAN-N dry-run` | decompose not yet |
| Retro                        | Review a finished plan, save a retro doc                                        | skill workflow                                       | no                |

### 1.4 Item (task) level

| Feature                 | What it does                                                                                       | Command                                                 | Used        |
| ----------------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------------------- | ----------- |
| Fields                  | Tasks: status open, in-progress, done, cancelled; priority low to critical; due_date; effort xs    | `pad item create task ... --priority --field due_date=` | status,     |
|                         |   to xl                                                                                            |                                                         |   priority  |
| Parent                  | Any item can be the child of another (plan, task)                                                  | `--parent PLAN-N`                                       | yes         |
| Assignee, role          | A user and an agent-role pair                                                                      | `--assign`, `--role`                                    | no          |
| Tags                    | JSON array of labels                                                                               | `--tags '["stage:S1"]'`                                 | no          |
| Dependencies            | blocks, blocked-by; blocked items leave `next` and show in `stale`                                 | `pad item block/blocked-by/unblock`, `pad item deps`    | no          |
| Other relations         | implements, supersedes, split-from; backlinks from `[[ref]]` wiki links                            | `pad item implements/supersedes/split-from`,            | no          |
|                         |                                                                                                    |   `pad item related`, `backlinks`                       |             |
| Comments                | Addressed to a person; editable; threaded replies; @mentions open a needs-you claim until answered | `pad item comment`, `comment-edit`, `--reply-to`        | yes         |
| Implementation notes    | Addressed to the record: what was done                                                             | `pad item note <ref> "..." --details`                   | no          |
| Decision log            | What was chosen and why, on the item                                                               | `pad item decide <ref> "..." --rationale`               | no          |
| Status comment          | Audit line on every status change                                                                  | `pad item update --status X --comment "why"`            | yes         |
| Reminders               | One-shot, RFC3339 instant with time of day; fired reminders head `next` until acknowledged         | `pad item remind --remind-at`, `pad item ack`           | no          |
| Claim / lease           | Atomic claim with expiry (15 m default) so two sessions never work one item                        | `pad item claim --ttl 2h`, `pad item release`           | no          |
| Watch                   | Durable server-side watch, optionally until a status                                               | `pad watch <ref> --until status=done`                   | no          |
| Context brief           | Item, parent chain, acceptance criteria, matching conventions, playbooks, deps, decisions, within  | `pad item context <ref> --intent implement`             | no          |
|                         |   a size budget                                                                                    |                                                         |             |
| Patch, history          | Exact-text body edit with diff and undo; read-only version history                                 | `pad item patch`, `pad item history`                    | no          |
| Star, attachments, copy | Personal quick list; files and images; copy into another workspace                                 | `pad item star`,                                        | no          |
|                         |                                                                                                    |   `pad attachment upload`, `pad item copy`              |             |

### 1.5 Rules and procedures

| Feature           | What it does                                                                                                                                | Used                               |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| Conventions       | Rules with trigger (always, on-task-start, on-task-complete, on-implement, on-commit, on-pr-create, on-plan-start, on-plan-complete,        | 5 active (apn baseline)            |
|                   |   on-plan), scope, priority (must, should, nice-to-have), optional role, `commands`, `decision_check`                                       |                                    |
| Playbooks         | Multi-step procedures with `invocation_slug`, typed `arguments`, trigger; only `status=active` ones route                                   | 4 active (ship, plan,              |
|                   |                                                                                                                                             |   decompose, onboard)              |
| Export and import | A convention or playbook as a portable artifact                                                                                             | not used; the apn baseline TOML    |
|                   |                                                                                                                                             |   plays this part                  |

### 1.6 Cross-session

| Feature                    | What it does                                                                                       | Used                               |
| -------------------------- | -------------------------------------------------------------------------------------------------- | ---------------------------------- |
| Session registry           | `pad session register` gives each session a worker id, so leases are per session                   | no                                 |
| Push                       | Self-addressed instruction on an item to your own armed sessions; fire-and-forget, no inbox        | no                                 |
| Chat                       | Messages between agents and the owner; information only unless the operator arms direction locally | no                                 |
| Webhooks, MCP, GitHub link | Events out; MCP server for chat clients; PR state on items                                         | no (apn has one branch and no PRs) |

---

## Part 2: Current state

Read 2026-11-10 16:28 AEDT from `pad bootstrap` in smc-resiliency:

- **Collections:** tasks, plans, ideas, docs, conventions, playbooks (startup template). No roles, no tags, no ask collection.
- **Items:** 4 active plans (PLAN-10 to PLAN-13), 16 open tasks and 1 done (TASK-29), 5 conventions, 4 playbooks; mirrored to Git as `docs/trackers/pad-focus.md` by `just pad-export`.
- **Conventions:** the apn baseline (CONVE-1 to CONVE-4 on commit and task completion, CONVE-9 always: "Repo trackers are the truth; Pad items link to them").
- **Observed use:** tasks carry the tracker ID in their body; status comments are written; several tasks are really waits on the operator (TASK-14 bench, TASK-16 decide build tool, TASK-18 decide
  pick-up rule, TASK-30 approve the next two boxes) and nothing separates them from agent work, so the operator has to read every task to find what needs them.

---

## Part 3: Principles

1. **The repo is the truth; Pad is the queue.** A Pad item names the tracker entry it serves (stage criterion, bug ID, open-item stamp, decision record). Status changes land in the tracker first, then
   in Pad. Pad never holds the only copy of a fact, decision or result.
2. **Asks are separate from work.** Anything that needs the operator (a decision, an approval of a production write, a bench action, a review) is an ask item in its own collection, so the operator's
   list is one view, not a search.
3. **Small and current.** Pad holds the current focus (the next one to two weeks of the timeline), not the backlog. At most five active plans; a task is one session or less; an item no one will touch
   in a month is closed or turned into an idea.
4. **Every change says why.** Status changes carry `--comment`; what an agent did goes in `note`; a choice goes in the repo decision record and `decide` points at it.
5. **Private by default.** Site names, box names and fleet findings stay in the local workspace. No share links, no cloud workspace, no webhooks to outside services without the operator's say.
6. **Agents start and end with Pad.** Start: `pad project next` (plus catch-up when the operator asks). End: notes on worked items, asks raised, `pad-export`.

---

## Part 4: The proposed model

### 4.1 Collections

| Collection                                  | Holds                                                                                             | Change                            |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------- | --------------------------------- |
| **Asks** (new, prefix ASK, `awaits_human=true`) | Every item waiting on the operator                                                                | create                            |
| Plans                                       | One plan per current timeline focus (a roadmap step or stage, a survey follow-up, an audit batch) | keep                              |
| Tasks                                       | Agent work, plus operator work that is not a question (for example a bench run the operator does) | keep; move pure decisions to Asks |
| Ideas                                       | Parked proposals not yet on the timeline (feature ideas, "later" findings)                        | start using                       |
| Docs                                        | Not used: documents live in the repo. Set `tracks_work=false`, or leave empty                     | leave                             |
| Conventions, Playbooks                      | The rules and procedures in 4.5 and 4.6                                                           | extend                            |

Options for where asks live:

| Option                             | How                                      | For                                                    | Against                                                     |
| ---------------------------------- | ---------------------------------------- | ------------------------------------------------------ | ----------------------------------------------------------- |
| **A. Asks collection** (recommended) | New collection with `awaits_human=true`, | One list, its own fields (kind, needed-by, blocks),    | One more collection per workspace                           |
|                                    |   assigned to the operator               |   routed to needs-you, counted apart from work         |                                                             |
| B. @mention on the task            | Agent comments "@Malik decide X" on      | No new collection                                      | A mention closes when any later comment from the operator   |
|                                    |   the task                               |                                                        |   lands, answered or not; asks scatter across tasks         |
| C. Assign the task to the operator | `--assign` on the existing task          | Simplest                                               | Needs-you mixes "please do" with "please decide"; nothing   |
|                                    |                                          |                                                        |   records the question asked                                |

Asks fields (`--fields` DSL):

```text
status:select:open,answered,withdrawn;
kind:select:decision,approval,bench,review,info;
urgency:select:blocking,this-week,whenever;
needed_by:date;
answer:text
```

- **decision**: choose between options (TASK-16 build tool, N15 pick-up rule).
- **approval**: a production write or other gated action (the next two url_capture boxes in TASK-30, reimaging a box, a canary).
- **bench**: something only the operator's hands can do (TASK-14 power cut and undervoltage cases, `just lab versions` on the bench Pi).
- **review**: read and accept a document or design note (R1.2 review on 13 Nov).
- **info**: a fact only the operator has (site access, a vendor contact, a credential location).

An ask body always has the same four parts, so the operator can answer from the inbox:

```markdown
**Question:** one sentence.
**Options:** A. ... (recommended, why) / B. ... / C. ...
**Blocks:** TASK-N, PLAN-N; tracker entry (stage criterion, bug ID, open-item stamp).
**Evidence:** repo paths or a decision draft; what was checked and what was not.
```

The agent links the ask to the work it holds up: `pad item block ASK-N TASK-M`. A blocked task drops out of `next` and shows in `stale`, so the queue never offers work that waits on the operator. When
the operator answers (in the ask, by comment, or in chat), the agent records the answer in the repo first (decision record or tracker), sets `answer` and `status=answered` with a comment citing where
it was recorded, and unblocks the task.

### 4.2 Plans and tasks

- **A plan** serves one focus from the timeline (R1 to R6) and names it in its first line: `plan-timeline.yaml R2.1; target-map.yaml S1, S1V`. Status `active` only while it is in the current
  fortnight; otherwise `planned` or `paused`. End date = the timeline's date.
- **A task** is one session or less, names its tracker entry in its first line, carries priority and effort, and sits under a plan. A task bigger than a session is split (`pad item split-from`).
- **Status mapping:** open (not started), in-progress (an agent holds a claim or the work is part-done), done (tracker updated and `just check` passed, per CONVE-3), cancelled (with the reason).
  Waiting on the operator is not a status: it is a blocking ask.
- **Who works it:** agent tasks are unassigned or assigned to the operator's account with no role; operator-hands tasks are assigned to the operator. Roles stay off until two agents work one workspace
  in parallel (Part 7, Q3).
- **Priority:** critical = production at risk now (TASK-29 class); high = on the current timeline step; medium = this month; low = could slip.

### 4.3 Tags

Tags group across collections without new fields. A small fixed vocabulary, kebab-case with a colon namespace:

| Tag                | Meaning                                                 | Example                 |
| ------------------ | ------------------------------------------------------- | ----------------------- |
| `stage:<id>`       | Target-map stage                                        | `stage:S1`, `stage:S4`  |
| `bug:<id>`         | Bug-tracker entry                                       | `bug:N08`               |
| `survey:<finding>` | Fleet survey finding                                    | `survey:F6`             |
| `prod-write`       | Touches a production SMC (always an approval ask first) | TASK-29, TASK-30        |
| `bench`            | Needs the bench Pi or lab hardware                      | TASK-14, TASK-15        |
| `hub`              | Must go to enterprise-strategy (or UNC) through the hub | TASK-17 contract change |
| `skill-writeback`  | Owes a write-back to a skill pack                       | TASK-28                 |

New tags are added to this table first. `pad tag list` shows drift.

### 4.4 Notes, decisions, reminders, watches

- **note**: at the end of each session on an item, one line of what was done and the commit, for example `pad item note TASK-30 "prune fix canaried on koonibba" --details "ansible-wifi rise 74d574b0;
  check+apply gates pass; nothing deleted yet"`.
- **decide**: only to point at the repo decision record: `pad item decide TASK-17 "booted + committed release" --rationale "decision 20261110_1238 in SCRATCHPAD"`.
- **remind**: for a time the agent must come back (a cron run to verify, a review date, a hold that expires), at a time of day: `pad item remind TASK-30 --remind-at 2026-11-11T06:30:00+11:00`. A fired
  reminder heads `next` until `pad item ack`.
- **watch**: the operator may watch an item until done (`pad watch TASK-24 --until status=done`); agents do not create watches.

### 4.5 Conventions to add (apn baseline)

Proposed for `conventions/apn-baseline.toml`, applied with `scripts/pad_conventions.py`:

| id                 | Title                                                                 | Trigger          | Priority |
| ------------------ | --------------------------------------------------------------------- | ---------------- | -------- |
| asks-for-input     | Ask the operator through an ASK item, never only in chat              | always           | must     |
| prod-write-ask     | A production write waits on an approval ask (tag `prod-write`)        | on-task-start    | must     |
| session-start      | Start with `pad project next`; claim the item before working it       | on-task-start    | should   |
| session-close      | Note each worked item, raise asks, run `just pad-export`              | on-task-complete | should   |
| task-names-tracker | A plan or task names its tracker entry in its first line and in a tag | always           | must     |
| tag-vocabulary     | Use only the tags in the guidelines table                             | always           | should   |

CONVE-9 (trackers-truth) stays as it is; the first and fifth rows sit beside it.

### 4.6 Playbooks to add

| Slug              | What it does                                                                                                                 | Arguments                        |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| `ask`             | Create an ask with the four-part body, assign the operator, tag it, block the work it holds up                               | `about` (ref), `kind`, `urgency` |
| `answer`          | Record an answer: repo record first, then `answer` field, status, unblock, note                                              | `target` (ASK ref)               |
| `sync-trackers`   | Compare Pad items with the trackers they name; list drift (closed in tracker, open in Pad, and the reverse); plan by default | `apply` (flag)                   |
| `triage-findings` | Turn survey or audit findings into a plan with tasks and asks, dry-run first                                                 | `source` (repo path), `dry-run`  |

Keep ship, plan, decompose and onboard as they are.

### 4.7 What Pad is not for

- Not a copy of the trackers, the ROADMAP or the SCRATCHPAD.
- Not for long design text: that goes in `docs/`, the item links it.
- Not for secrets, credentials or customer data, even in comments or attachments.
- Not a cross-project channel: messages to other projects go through the hub (`to es:`, `just sync-projects`). A Pad item may record that a hub message was sent.

---

## Part 5: Use cases

Each use case gives the trigger, what the agent does, and what the operator sees.

### UC1. A design decision is needed (TASK-16 build tool)

1. Agent finds a choice it may not make: mkosi v27.1 against the alternatives, snapshot service, role build mode.
2. Agent drafts options in the repo (design note or SCRATCHPAD open item), then runs the `ask` playbook: ASK-N, kind decision, urgency this-week, options A/B/C with a recommendation, `pad item block
   ASK-N TASK-16`.
3. Operator sees ASK-N in needs-you, answers. Agent runs `answer`: decision record, tracker, ASK answered, TASK-16 unblocked and back in `next`.

### UC2. A production write needs approval (TASK-29, TASK-30)

1. Survey shows koonibba-smc01 root at 98 %. Agent creates TASK-29 (critical, tags `prod-write`, `survey:F6`) and ASK-N (approval, blocking): the exact commands, pre-checks done, rollback, what is
   read-only and what writes.
2. The agent does not run the write until the ask is answered. Approval and outcome go in the task as note and status comment.
3. For the remaining boxes (galiwinku, hope-vale), one approval ask per batch, naming the boxes, after the canary evidence is in.

### UC3. Operator hands needed (TASK-14 bench cases)

Task stays in Tasks, assigned to the operator, tag `bench`, with the exact commands and what to record. If the agent must wait for the result, an ask of kind bench blocks the follow-on task. The
operator's result goes in the test record in the repo; the agent closes the task after reading it.

### UC4. A review with a date (R1.2 review, Fri 13 Nov)

ASK-N kind review, needed_by 2026-11-13, linked to PLAN-10, reminder set for the morning before. If unanswered by the date, the agent reports it at session start rather than moving the date.

### UC5. Survey or audit findings arrive

Agent runs `triage-findings` on the survey file: one plan (PLAN-12 shape), one task per finding that needs work, an ask per finding that needs a decision, dry-run shown first. Findings that need
nothing are recorded in the survey file only.

### UC6. Two sessions at once

Each session registers (`pad session register`) and claims before working (`pad item claim TASK-N --ttl 2h`). A `lease_held` answer means pick another item. The message between sessions is the ping;
the item note is the record (upstream pattern, `blog_multi-session-claude-code.md`).

### UC7. Something comes back later (a cron run, a hold)

The url_capture prune runs at 16:10 on koonibba. Agent sets a reminder on TASK-30 for the next morning; the fired reminder heads `next`; the agent reads the box, notes the result, acks the reminder.

### UC8. Work that belongs to UNC or the hub (TASK-17 contract 0.4.0)

Tag `hub`. The agent sends the hub message (`to es:`) and notes "hub message sent, stamp ..." on the task. The task closes when the local part is done; the UNC part is UNC's own Pad item in its own
workspace, created by a UNC session, not copied by this one.

### UC9. A skill write-back owed (TASK-28)

Task with tag `skill-writeback`, naming the pack and the files. It closes when the write-back is committed in skills_stuff (commit ID in the note).

### UC10. Morning catch-up for the operator

Operator runs `pad project catch-up` (or the web page) for what changed and what needs them, then the needs-you inbox for asks across smc-resiliency and UNC in one list. `pad project report --window
week` weekly for flow.

---

## Part 6: Rollout plan

Each step is plan-first and needs the operator's go; nothing here writes until approved.

| Step | What                        | Commands (planned)                                                                                                  | Check                                     |
| ---- | --------------------------- | ------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| 0    | Operator approves or amends | none                                                                                                                | answers recorded                          |
|      |   this proposal (Part 7)    |                                                                                                                     |                                           |
| 1    | Create Asks                 | `pad collection create "Asks" --awaits-human true --fields "<fields in 4.1>"`, then                                 | `pad collection list`; a test ask shows   |
|      |   in smc-resiliency         |   `pad collection update asks --prefix ASK` (create has no prefix flag)                                             |   in needs-you                            |
| 2    | Move today's waits to asks  | ASK items for TASK-16, TASK-18, the TASK-30 batch approval, R1.2 review; `pad item block` each; keep TASK-14 as a   | `pad project next` no longer offers       |
|      |                             |   bench task                                                                                                        |   blocked tasks                           |
| 3    | Tag current items           | `pad item update <ref> --tags '[...]'` per 4.3                                                                      | `pad tag list` matches the table          |
| 4    | Conventions and playbooks   | Add 4.5 to `apn-baseline.toml`, run `pad_conventions.py` (plan, then `--apply`); create the 4.6 playbooks           | `pad bootstrap` lists them                |
|      |                             |   with `--field status=active`                                                                                      |                                           |
| 5    | Export                      | Check `pad_export.py` renders the Asks table (it skips only conventions and playbooks), consider adding an assignee | `just pad-export` diff                    |
|      |                             |   or kind column                                                                                                    |                                           |
| 6    | UNC                         | Same steps in unified-network-controller from its own session                                                       | its bootstrap                             |
| 7    | Review after two weeks      | `pad project report --window 2wk`, count asks answered and their wait time; keep, trim or drop                      | a short note in this folder               |

---

## Part 7: Decisions for the operator

| #   | Question                                | Options                                                                                                                              |
| --- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Q1  | Where do asks live?                     | **A. Asks collection (recommended)** / B. @mentions on tasks / C. assign tasks to you                                                |
| Q2  | How much work goes into Pad?            | **A. Current focus only, next one to two weeks (recommended)** / B. every open tracker item / C. asks only, no tasks                 |
| Q3  | Agent roles?                            | **A. None until two agents work in parallel (recommended)** / B. implementer and reviewer now                                        |
| Q4  | How do you answer an ask?               | **A. Comment or field on the ask; the agent records it (recommended)** / B. tell the session in chat, agent creates the record / C. both |
| Q5  | Roll out to UNC and other apn projects? | **A. After two weeks in smc-resiliency (recommended)** / B. now, together                                                            |

---

## Sources

- Installed CLI: `pad --version` 0.19.2 (22e50fe, 2026-11-08); help pages of `item`, `project`, `collection`, `playbook`, `session`, `chat`, `library`, `tag`, `push`, `watch` read 2026-11-10; the whole command tree (184 commands) from `pad help --all --format md|json` (cmdhelp v0.1), saved as [upstream/v0.19.2/cli/](upstream/readme.md).
- Upstream repo PerpetualSoftware/pad at tag v0.19.2, saved in [upstream/v0.19.2/](upstream/readme.md): `docs_api.md` (collection settings `tracks_work`, `awaits_human`; needs-you routing; catch-up), `README.md`,
  `docs_mcp.md`, `CLAUDE.md`.
- getpad.dev pages saved 2026-11-10 with all-scraper `md` in [upstream/getpad.dev/](upstream/readme.md): docs (collections, templates, playbooks, web UI, CLI, agent integration), learn guides, spec-driven, blog posts on
  Insights and tags, the item pane, the software factory and multi-session use.
- smc-resiliency workspace state: `pad bootstrap --format json`, `docs/trackers/pad-focus.md`, CONVE-9.
