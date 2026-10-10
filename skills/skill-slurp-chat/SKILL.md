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
- [Step 5a — Persistent scripts (every slurp, unprompted; operator, 2026-10-09: "when slurp is called, scripts should be handled in it as well")](#step-5a--persistent-scripts-every-slurp-unprompted-operator-2026-10-09-when-slurp-is-called-scripts-should-be-handled-in-it-as-well)
- [Step 6 — Governed record (the step memory-only slurps skip)](#step-6--governed-record-the-step-memory-only-slurps-skip)
- [Step 6b — Self-audit before the report (mandatory)](#step-6b--self-audit-before-the-report-mandatory)
- [Step 7 — Checkpoints and SCRATCHPAD](#step-7--checkpoints-and-scratchpad)
- [Step 8 — Closeout mode only](#step-8--closeout-mode-only)
- [Report — the coverage table](#report--the-coverage-table)
- [Red flags — stop and route the item](#red-flags--stop-and-route-the-item)

---

## Modes
- **`/slurp-chat`** — steps 0 to 7, including 5a and 6b
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

**Zone boundary = the last *slurp* of this conversation** (an entry or checkpoint a slurp wrote: `slurp-*`, `session.closeout.*`), never a progress
note written mid-session. A summary saved during the work is not a capture of the work: everything since the conversation's last slurp is Zone B,
however many memory entries were written in between. No slurp yet in this conversation → the whole conversation is Zone B.

**Compaction (operator, 2026-10-09: "as auto compaction happened before slurp so slurp should take necessary steps to make important info is not
lost").** If the context was summarised since the boundary, the summary is not the source: it drops mid-turn messages, question answers, exact
commands and incidents. Read the raw transcript instead (`~/.claude/projects/<cwd-slug>/<session>.jsonl`; the summary names it) with
`scripts/transcript_passes.py --since <boundary, UTC>`, which prints both Step 3 passes from it. Every line it prints is walked; the report states
that the transcript, not the summary, was used and gives its counts.

## Step 3 — Zone B scan (thorough)
Walk the conversation **in order, from the boundary to now**, not from what is fresh in mind. Two passes, both written down:

1. **Every user message**, one line each: what it asked, decided, ruled or challenged. A question that changes how work is done ("why custom and not
   native?", "why did I have to remind you?") is an operator rule or preference, not chitchat.
2. **Every action with a side effect**, in order: writes to a system of record, deploys and restarts, backups, permission or schema changes, deletes,
   device logins and reads of production, files created outside the repo, and anything that went wrong (an incident: data stored that must not be,
   a write refused, a rollback).

`scripts/transcript_passes.py` prints both passes from the transcript (typed turns, messages sent mid-turn, AskUserQuestion answers; Bash
commands, file writes, MCP writes). Use it whenever the session is long or was compacted; never rebuild the passes from memory or a summary.

From the two passes, list every significant item as a numbered **item list**, one line each. Each item has a type:

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
| incident              | something that went wrong or broke a rule, even if fixed minutes later: what, where, how resolved  |
| script                | any code written or run ad hoc this session (scratchpad files, heredocs, one-off probes, analyses) |

Skip chitchat and anything derivable from the repo alone (file contents, git log).

## Step 4 — Zone A scan (light)
For each existing entry, ask only: does the conversation hold specific detail (commands, sizes, names, error text) the entry omits? Yes → update that key, or a clearly titled delta note. No → skip.

## Step 5 — Memory backends
- memory-keeper: `context_save(key="<project>.<topic>", category, priority, channel, value)`. One key per topic. `high` for blockers.
- project-context: `add_note` per Zone B topic; `record_decision` for each operator decision. Never duplicate an existing note.
- Undecided proposals are saved as open, never as decisions.

## Step 5a — Persistent scripts (every slurp, unprompted; operator, 2026-10-09: "when slurp is called, scripts should be handled in it as well")
List every script the session wrote or ran ad hoc: scratchpad files, heredoc programs, one-off probes and measurements. Judge each by how likely it
is to be needed again (operator, 2026-10-09: "only the scripts which you judge are good to have due to their probability for future use"); promote
those, and give every other one a line saying why not:

| Kind                                                      | Action                                                                                         |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| likely reused (a probe, measurement, check or fetch)     | promote now: the matching skill's `scripts/` (or the project's) with generic inputs, docstrings |
|                                                           | (Args/Returns), a recipe, a catalogue row, an offline test, and a smoke run on real input      |
| already persistent (a committed tool covers it)           | name the tool that covers it in the coverage table                                             |
| a one-off edit (a records patch, a migration helper)      | `not needed` with that reason in the coverage table                                            |

Register each promoted script in every registry the project keeps (promotion register, script catalogue, tracker, tests index), then run the
project's check. A slurp is not complete while a script judged worth keeping exists only in the scratchpad. Do not wait to be asked; do not promote one-offs.

## Step 6 — Governed record (the step memory-only slurps skip)
Find the project's governed surfaces before writing: its AGENTS.md or CLAUDE.md (change-log rule, working rules), `context-map.yaml` `update_rules`, and any status source of truth (a target map,
tracker, roadmap). Then route every item:

| Item type          | Must land in                                                                                     |
| ------------------ | ------------------------------------------------------------------------------------------------ |
| repo change        | change-log entry, if the project keeps one                                                       |
| script             | Step 5a: promoted and registered, or the covering tool named, or `not needed` with its reason    |
| operational event  | change-log entry, **even when no repo file changed** (what, where, size or count, how verified)  |
| operator decision  | change-log entry, plus the project's decision surface (register, roadmap) where one exists       |
| operator rule      | the project's agent rules (AGENTS.md working rules or its rules folder)                          |
| undecided proposal | SCRATCHPAD open items and the change log as "proposed, not decided"; never in a decision surface |
| status change      | the status source of truth, then regenerate its derived views                                    |

| incident           | change-log entry: what happened, what it touched, how it was found and resolved                  |

Then the project's **companion rules**: list the files this session changed (`git status --short` in every repo touched) and apply the project's
own update rules to each (`context-map.yaml` `update_rules`, AGENTS.md "update X in the same pass" rules, folder indexes, trackers and matrices the
rules name, rendered views). A changed file whose companion was not updated is a gap, not a detail.

Before that check, run skill-ai-it `scripts/adopt_governed_files.py --project-root <project> --apply` (operator, 2026-10-10): it adds any part
of the governed-file standard the project lacks (recipes, freshness in `check`, records front matter, baseline) and does nothing when adopted.

Run the project's own governance check (e.g. `scripts/check_governance.py`, `just check`) and any status validator afterwards. Fix the project, not the check.

## Step 6b — Self-audit before the report (mandatory)
Before reporting, check the capture against the conversation, not against the item list:
- Every user message from pass 1 has a destination in the coverage table (or a stated reason it needs none).
- Every side-effect action from pass 2 is in a change-log entry or the operational memory key.
- Every repo with changes has its companions applied (Step 6) and its check passing.
- No row bundles unrelated items; one operator decision is one row and one `record_decision`.
If any check fails, fix it and run the audit again. Report only when it passes; say in the report that it passed.

## Step 7 — Checkpoints and SCRATCHPAD
```
context_checkpoint(name="slurp-<YYYYMMDD>-<topic>")
create_checkpoint(projectId, name="slurp-<YYYYMMDD>-<topic>")
```
In the project's `SCRATCHPAD.md` (create via `/skill-ai-it` if missing), update only the sections this session changed, marked `KEEP`: Current state, Open items (add undecided proposals), Key anchors,
Recent decisions, Session history (2–3 bullets), Next actions (replace), Memory pointers (keys, note and checkpoint IDs). No file-change lists, no task detail, no session logs.

Then keep the records within budget (operator, 2026-10-10): `just budget` (plan) and `just budget --apply` (skill-ai-it `scripts/budget_plan.py`:
normalises dated paragraphs, rotates to `docs/history/`, moves non-working-state sections to reference docs, audits for lost or split lines, runs
`just check`). A project without the recipe: run the script with `--project-root`. A file it reports as still over budget is not done (operator,
2026-10-10): list it, with the section it names, in the closeout as open work; never report it as within budget. Write CHANGELOG entries short: what changed and where, with `just changelog-entry --title ... --body-file ... --apply` (skill-ai-it
`scripts/add_changelog_entry.py`: the project's own heading style and order, Contents line included).

Then regenerate the project's wiki page from those files (operator, 2026-10-10; the page is generated, never hand-written):
`just -f /Volumes/Data/_ai/_wiki/wiki_stuff/justfile project_page <project-path>`. It rewrites only its generated block in
`projects/<folder-name>.md` and appends to the wiki's `log.md`; add the page to `index.md` the first time it prints a note. Report it in the coverage table.

## Step 8 — Closeout mode only
One more memory-keeper `progress` entry, key `session.closeout.<YYYYMMDD>.<topic>`: Session / Workstream, Scope, Completed, Files Changed, Decisions, Open Issues, Next Actions, Persistence Status
(memory-keeper, project-context, checkpoints, commits).

## Report — the coverage table
One row per Step 3 item. No cell may be blank: write the destination, or `not needed` with the reason.

| #   | Item | Type | memory-keeper key | project-context | Governed file | Status |
| --- | ---- | ---- | ----------------- | --------------- | ------------- | ------ |

Then: the boundary used (which slurp), whether the passes came from the transcript (required after a compaction), how many user messages and side-effect actions the two passes found, the repos and files checked against
companion rules, the Step 6b result, and the last memory-keeper and project-context timestamps.

## Red flags — stop and route the item
| Thought                                           | Reality                                                                       |
| ------------------------------------------------- | ----------------------------------------------------------------------------- |
| "The scripts were throwaway, nobody asked"        | Step 5a is mandatory: judge each; promote the likely-reused ones, unprompted  |
| "No repo file changed, so no change-log entry."   | Operational events are durable; the change log is where the next agent looks. |
| "It is in memory-keeper, so it is captured."      | Memory is not the project's record. Step 6 applies.                           |
| "Nobody decided it, so there is nothing to save." | An undecided proposal is saved as open, or it is lost.                        |
| "The rule is obvious from the code."              | Agents read the rules file, not the code. Write the rule.                     |
| "The status file will be updated next session."   | A stale status source misleads the next reader now.                           |
| "The time is about HH:MM."                        | Run `date`.                                                                   |
| "The compaction summary covers the early part"    | It is lossy. Run `scripts/transcript_passes.py` on the raw transcript        |
| "I saved a summary earlier, so that work is done" | A mid-session note is not a slurp; the boundary is the last slurp (Step 2)     |
| "The early part of the chat is covered"           | Walk it in order (Step 3); early incidents and ops are the ones that get lost |
| "One row for all the decisions is enough"         | One decision, one row, one record_decision                                    |
| "The changed file is recorded; its index can wait" | Companion rules are part of the slurp (Step 6)                               |
