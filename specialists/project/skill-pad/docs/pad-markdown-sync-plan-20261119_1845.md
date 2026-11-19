---
Title: Pad and markdown sync plan
Category: plan
Status: proposed
Authority: >-
  Proposal for the operator; nothing here is in force until section 6 is answered. Pad CLI facts VERIFIED_PRIMARY against pad 0.21.0 on 2026-11-19
  unless marked; project experience is USER_STATED by three peer sessions (smc-resiliency-44, ansible-wifi-47, continuum-32) on 2026-11-19.
Scope: How markdown files in apn projects and Pad items are mapped, synced, checked and reverted; the skill-pad script gaps that block effective use
Last reviewed: 2026-11-19
Summary: >-
  One writer per type of record, a stable key written in the markdown itself, a sync that turns an edit of a generated block into a guarded Pad write and
  then regenerates the file, a committed before-image journal with revert, link checks in just check, and a shared helper layer so projects stop
  hand-rolling Pad calls. Built in six stages, smc-resiliency first as the canary.
---

# Pad and markdown sync plan

Operator, 2026-11-19: "So that we update the markdown files and pad is updated using a script and with time that can be reversed if needed. We update pad and then generate markdown files based on
that." Then: consult the other active sessions, ask them what gaps they see in the skill-pad scripts, and write a detailed plan for using Pad effectively.

**Short answer.** Yes to a mapping, a script and a revert. The one change from the request: a record type has one owner. For the types Pad owns (bugs, feature requests, tech debt, asks, tasks) the
operator's flow works as asked: edit the generated markdown, the sync writes the edit into Pad, then regenerates the file from Pad. For the types the repo owns (decisions, plan and stage trackers,
open items, design docs) the markdown stays the truth and Pad receives a one-way mirror or a link. All three peer sessions arrived at this split independently.

## Contents

- [1. Where things stand](#1-where-things-stand)
- [2. What the peer sessions said](#2-what-the-peer-sessions-said)
- [3. Design](#3-design)
  - [3.1 One owner per record type](#31-one-owner-per-record-type)
  - [3.2 Keys live in the markdown](#32-keys-live-in-the-markdown)
  - [3.3 The sync cycle](#33-the-sync-cycle)
  - [3.4 Journal and revert](#34-journal-and-revert)
  - [3.5 Conflicts](#35-conflicts)
  - [3.6 Link and drift checks](#36-link-and-drift-checks)
  - [3.7 Constraints every script obeys](#37-constraints-every-script-obeys)
  - [3.8 Collections: what Pad offers, what to use, what to add](#38-collections-what-pad-offers-what-to-use-what-to-add)
- [4. Script gaps](#4-script-gaps)
- [5. Stages](#5-stages)
- [6. Decisions for the operator](#6-decisions-for-the-operator)
- [7. Not verified and risks](#7-not-verified-and-risks)

## 1. Where things stand

| Record                             | Script today                                   | Direction                 | Key                         | Revert   |
| ---------------------------------- | ---------------------------------------------- | ------------------------- | --------------------------- | -------- |
| bug-tracker.md, features-to-add.md | `pad_tracker.py` export                        | Pad to md (import once)   | hash marker per block       | git only |
| pad-focus.md                       | `pad_export.py`                                | Pad to md                 | none (whole file)           | git only |
| Decisions (DECISION-LOG, `.kc/`)   | `pad_decisions.py`                             | md to Pad                 | decision id (DL-nnn, stamp) | none     |
| Plans, tasks                       | none                                           | prose `Serves:` / `Refs:` | none                        | none     |
| Asks                               | none (no collection in smc, UNC, ansible-wifi) | —                         | —                           | —        |

What Pad itself can undo (pad 0.21.0, read 2026-11-19): `pad item history --full` keeps body versions only, and restoring one is web-UI only; `pad item patch --undo` inverts one patch; `pad item
restore` un-archives a soft-deleted item. Fields, status and comments have no CLI undo, so the sync needs its own journal.

## 2. What the peer sessions said

Asked the same five questions and the gap question on 2026-11-19. Agreement is near total; differences are in the last column.

| Topic         | smc-resiliency-44                                              | ansible-wifi-47                               | continuum-32                                  | Taken into the plan |
| ------------- | -------------------------------------------------------------- | --------------------------------------------- | --------------------------------------------- | ------------------- |
| Who owns what | Pad: bugs, FR, generated trackers; repo: plan, stage,          | Pad: bugs/FR/TD, closing comments; repo: plan | Pad: tasks/TD/FR/BUG/ASK; repo: decisions     | 3.1                 |
|               |   open items                                                   |   files (fields only to Pad)                  |                                               |                     |
| Global flip   | no; keep `trackers-truth`, name the types                      | no; per-type table in the convention text     | no; one writer per type                       | 3.1, D1             |
|   to Pad      |                                                                |                                               |                                               |                     |
| Key           | existing IDs (B19-06, stamps, S1, X86-01)                      | explicit marker `<!-- pad:TASK-21 -->`        | ID or marker in the md; map derivable         | 3.2                 |
| Map file      | keep; declare truth per file in it                             | keep, keyed on markers                        | keep, but checkable, never the only link      | 3.2                 |
| Round trip    | drop for repo-owned files                                      | push fields only for plans                    | drop two-way on one type; separate input file | 3.3, D2             |
| Revert        | before-image, plan by default, refuse on moved seq,            | same; journal in git so it works with         | same; revert journalled too                   | 3.4                 |
|               |   correction comment                                           |   Pad gone                                    |                                               |                     |
| Conflict      | both changed: stop and report                                  | stop and list                                 | refuse and show diff                          | 3.5                 |
| New checks    | superseded stamps, staleness                                   | dangling refs, Serves paths, commit refs      | export current at commit, schema vs items,    | 3.6                 |
|               |                                                                |                                               |   decision drift in Pad                       |                     |

Peer claims checked here (pad 0.21.0, 2026-11-19): `item show --format md` is refused and `markdown` works (help takes `md`), VERIFIED; `fields` in `item show --format json` is a JSON string,
VERIFIED; `pad item list --format json` returns a list with `content_preview`, not the full body, VERIFIED (it explains a zero count of `Serves:` lines in this session); `pad item block A B` means A
blocks B, VERIFIED. Corrected: `pad collection show` does not exist (continuum read it as "not JSON"); `item-check` already takes several refs (`nargs="*"`), so the gap is "items touched this
session", not multi-ref.

## 3. Design

### 3.1 One owner per record type

The owner is the only writer of a record's content. The other side holds a generated copy, a mirror or a link.

| Record type                           | Owner | Other side                                                               | Flow the operator uses                                      |
| ------------------------------------- | ----- | ------------------------------------------------------------------------ | ----------------------------------------------------------- |
| Bugs, feature requests, tech debt     | Pad   | generated tracker file (marked blocks)                                   | edit the md block or Pad; `just pad-sync`; file regenerated |
| Asks                                  | Pad   | asks section in pad-focus.md                                             | Pad, or the generated block as for bugs                     |
| Tasks, plans (Pad-side queue)         | Pad   | pad-focus.md                                                             | edit Pad or the generated block                             |
| Comments, notes, DONE statements      | Pad   | read-only export                                                         | Pad only (append-only)                                      |
| Decisions                             | repo  | Pad `decisions` collection (mirror)                                      | edit the decision log; `just pad-decisions --apply`         |
| Plan tracker, stage tracker, timeline | repo  | Pad plan/task carries a marker link, plus fields (status, due, end_date) | edit the tracker; sync pushes fields only                   |
| Open items, SCRATCHPAD, CHANGELOG     | repo  | never mapped (rotation and budgets own them)                             | link by Pad ref in the line                                 |
| Design docs, skill references         | repo  | cited in `**Serves:**` / `**Refs:**`                                     | link only; checked by 3.6                                   |

The convention `trackers-truth` is rewritten to name the types in this table instead of saying "repo" in general (D1).

### 3.2 Keys live in the markdown

- Every mapped entry carries its key in the markdown: an existing ID where one exists (`B19-06`, `DL-037`, a decision stamp, `S1`, `X86-01`), otherwise a marker `<!-- pad:TASK-21 -->` on the entry's
  first line. Never a heading or title: formatters and rotation reword them.
- `pad-map.toml` (one per project) declares, per file: owner, collection, kind, and the fields that flow. Per entry it records the Pad ref, the last synced `seq`, the content hash on both sides and
  the sync stamp. It is a cache that can be rebuilt from the markers plus Pad; `pad_sync.py check` rebuilds it in memory and fails on any difference.
- Hashes are taken on normalised text (whitespace collapsed, `\_` folded to `_`, opener links turned back), so a markdown hook reflow is not a change.
- Pad items are created only from entries that carry an ID or are written to a template; never from free prose.
- New tracker IDs (B19-07) come from an allocator: highest in Pad and in the file, plus one, written with `--expected-seq` on a per-workspace counter item, so two sessions cannot take the same number.

### 3.3 The sync cycle

```text
JUST PAD-SYNC (plan by default; --apply writes)

+-------------+   +----------------------+   +--------------------+   +----------------+   +-----------------+
| 1 scan md   |-->| 2 read Pad (seq,     |-->| 3 classify each    |-->| 4 push md      |-->| 5 regenerate md |
| markers and |   |   body, fields)      |   |   entry: same,     |   |   edits to Pad |   |   from Pad,     |
| block hashes|   |                      |   |   md-only, Pad-only|   |   (journal     |   |   then check    |
+-------------+   +----------------------+   |   both, new, gone  |   |   first)       |   +-----------------+
                                             +--------------------+   +----------------+
                                                       |
                                                       X both changed: stop, show both diffs, write nothing

Legend: X refused
```

- **md changed, Pad not:** the edit becomes a Pad write (`item update --stdin --expected-seq`, body from a file), with a `--comment` naming the sync stamp. This replaces today's `pad_tracker.py
  export` refusal of a hand-edited block: the edit is consumed, not refused.
- **Pad changed, md not:** regenerate the block.
- **New entry in md (with ID or template):** `item create --op-key <project>-<key>-<hash8>`, so a rerun creates nothing twice.
- **Entry gone from md:** never deleted in Pad; reported for a decision (close with a comment, or restore the md line).
- **Repo-owned files:** only the declared fields flow md to Pad; bodies never.
- Step 5 runs `just check`; the files written are committed by the project's own `just commit-project`. The markdown side is reverted by git.

### 3.4 Journal and revert

- **Journal:** `docs/pad-sync/journal-YYYYMMDD_hhmm.jsonl` in the project (committed), one line per write: ref, op, before-image (body, fields, status, seq), after-seq, op-key, comment ids added.
  Written before each Pad call and completed after it, so a crash leaves a visible half entry.
- **Revert:** `just pad-sync revert <stamp>` is a plan by default. With `--apply` it restores body and fields per item only when the current seq equals the journal's after-seq; otherwise it lists the
  item and shows the diff. Comments are never deleted: a revert adds a `REVERTED <stamp>:` comment. Created items are closed as `cancelled` with that comment, not deleted. The revert writes its own
  journal, so a revert can be reverted.
- Pad's body history (`item history --full`) is the second copy; the journal works even if Pad's database is lost.

### 3.5 Conflicts

Sources disagree: stop and report, never merge (smc-resiliency rule). A conflict is: both sides changed since the last sync; a seq moved during the run (`--expected-seq` refused); an ID taken by
another session; an always-on convention missing from a project's adapted conventions file. Each is reported with the entry, both versions and the command that resolves it.

### 3.6 Link and drift checks

`pad_links.py check`, run by `just check` as a warning first and as a failure once clean:

| Check                             | Catches (seen 2026-11-19)                                      |
| --------------------------------- | -------------------------------------------------------------- |
| Dangling Pad ref in markdown      | "Pad TASK-21" written before the item existed (ansible-wifi)   |
| `Serves:` / `Refs:` path missing  | a renamed design file still cited by a task                    |
| Commit in `Refs:` not in the repo | a hash pasted by hand from another repo                        |
| Superseded decision cited         | tasks still serving 20261119_1556 after 1756 replaced it (smc) |
| Generated file stale              | pad-focus.md behind Pad at commit time (continuum)             |
| Field used but not declared       | tech-debt `priority` stored but not in the schema (continuum)  |
| Stale in-progress item            | no comment in N days                                           |
| Tracker drift (old 3.9 item)      | closed in the tracker, open in Pad, and the reverse            |

### 3.7 Constraints every script obeys

All learned in use on 2026-11-19 (USER_STATED by the sessions unless marked).

- Drive `pad` from Python with argument lists; bodies always from a file or stdin, never inline (hooks inspect command text and refused a body containing `group_vars`).
- Normalise JSON: list or `{"items": [...]}`, `ref` or `issue_id`, `fields` as a string (VERIFIED); `--format markdown` for `item show`, `md` for help (VERIFIED).
- Back off and retry on `rate_limited`; judge success by exit code, not stderr (`setpgid` noise under the harness).
- `item update` has no `--op-key`: read status first, then update with `--expected-seq` and `--comment`.
- Stamps from the clock (`date`), never typed; a writer into a budgeted file re-checks the budget after writing.
- Generated markdown backticks only real paths (a backticked `Network/SMC` failed a path check).
- Close order: the `DONE:` comment first, then the status change pointing at it.

### 3.8 Collections: what Pad offers, what to use, what to add

Pad ships six default collections and eight optional templates, and any collection can be custom (fields: text, select, multi_select, number, date, checkbox, url, relation). VERIFIED_PRIMARY:
[docs_collections.md](../references/upstream/getpad.dev/docs_collections.md) and `collection-templates.ts` (v0.19.2) in [references/upstream/](../references/upstream/readme.md). Live state read 2026-11-19: smc-resiliency, UNC and ansible-wifi each hold tasks, plans, ideas, docs, conventions,
playbooks, bugs, feature-requests and tech-debt; none holds asks or decisions; continuum holds asks and decisions (USER_STATED, continuum-32).

| Collection       | Kind     | Use here                                                                               | Owner (3.1)                   | Verdict                       |
| ---------------- | -------- | -------------------------------------------------------------------------------------- | ----------------------------- | ----------------------------- |
| Tasks            | default  | the agent's queue for the current focus; one session or less                           | Pad                           | keep                          |
| Plans            | default  | one per current focus; progress from child tasks; end_date from the timeline           | Pad (fields from the tracker) | keep                          |
| Ideas            | default  | proposals not yet on the timeline; promoted to a plan or rejected                      | Pad                           | start using                   |
| Docs             | default  | not used: documents live in the repo; a Pad doc would be a second copy                 | —                             | leave empty                   |
| Conventions      | default  | the apn baseline and per-project rules (`pad_conventions.py`)                          | skill-pad toml                | keep                          |
| Playbooks        | default  | ask, answer, triage-findings, sync (G10)                                               | skill-pad                     | keep, add four                |
| Bug Tracker      | template | bugs (tracker_id B19-nn); generated bug-tracker.md                                     | Pad                           | keep                          |
| Feature Requests | template | features; generated features-to-add.md                                                 | Pad                           | keep                          |
| Tech Debt        | template | debt; declare `priority` in the schema (continuum found it stored but undeclared)      | Pad                           | keep, fix schema              |
| Decisions        | template | one-way mirror of the decision log (`pad_decisions.py`); statuses include `superseded` | repo                          | add to smc, UNC, ansible-wifi |
| Meeting Notes    | template | not adopted: meetings and threads live in the comms tracker (skill-commtracker)        | —                             | no                            |
| OKRs             | template | not adopted: the enterprise-strategy timeline (R1 to R6) carries objectives            | —                             | no                            |
| Sprint Backlog   | template | not adopted: no sprints; plans and tasks with due dates cover it                       | —                             | no                            |
| Knowledge Base   | template | not adopted: skills and repo docs are the knowledge base                               | —                             | no                            |

**New collections proposed** (custom, schemas to add under `conventions/collection-schemas/`):

| Collection | Prefix | Fields                                                             | What we do with it                                                      | Where                           |
| ---------- | ------ | ------------------------------------------------------------------ | ----------------------------------------------------------------------- | ------------------------------- |
| Asks       | ASK    | status open/answered/withdrawn (closing), kind                     | every question for the operator, routed to needs-you; blocks the task   | all workspaces                  |
|            |        |   decision/approval/bench/review/fact, priority, due_date, answer  |   it holds up (guidelines 3.1; schema exists, never created in apn)     |                                 |
| Risks      | RISK   | status open/mitigating/accepted/closed, likelihood, impact, owner, | the risks now scattered in design docs (Pi image, x86 plan, recovery)   | smc-resiliency, UNC             |
|            |        |   review_date, mitigation (relation to tasks)                      |   become one register; review_date gives a reminder; a task mitigates a |                                 |
|            |        |                                                                    |   risk through `implements`                                             |                                 |
| Handoffs   | HND    | status sent/acknowledged/done/declined, from_project, to_project,  | a message from one project to another that cannot be lost (a push is    | one shared hub                  |
|            |        |   kind info/request/directive, due_date                            |   lost with no listener); replaces or backs `project_sync.py` outbox    |   workspace                     |
|            |        |                                                                    |   lines; the hub ticks it                                               |   (enterprise-strategy)         |
| Runs       | RUN    | status planned/running/passed/failed/aborted, target (card, VM,    | each bench or lab run with its log attached and its result, linked to   | smc-resiliency (lab)            |
|            |        |   box), stage, started, log attached                               |   the task and bug it serves; feeds `Evidence:` lines                   |                                 |

Asks is in the guidelines already. Risks and Handoffs are new and need the operator (D6, D7). Runs is the least certain: the lab rule records every test verbatim in the repo and on malik1tb, so a Runs
item must point at that record, not replace it (D8).

## 4. Script gaps

Merged from this session's review and the three peers. Stage = where section 5 builds it.

| #   | Gap                                                                                                            | Raised by                    | Stage |
| --- | -------------------------------------------------------------------------------------------------------------- | ---------------------------- | ----- |
| G1  | Shared helper module: JSON and format normalising, back-off, clock stamps, bodies from files                   | smc, continuum, ansible-wifi | S1    |
| G2  | Item writer to the standard: create, comment, close (DONE then status), attach log, item-check after           | all four                     | S2    |
| G3  | Templates per collection (task, bug, ask, FR, TD) printed or filled from fields                                | smc                          | S2    |
| G4  | Tracker ID allocator with a seq-guarded counter                                                                | smc                          | S2    |
| G5  | item-check for "items touched this session" (multi-ref exists)                                                 | smc (corrected)              | S2    |
| G6  | `pad_sync.py`: map, scan, push, regenerate, journal, revert, check                                             | operator                     | S3    |
| G7  | Link and drift checks (3.6), including `pad_tracker_drift.py` from the guidelines                              | all four                     | S4    |
| G8  | Superseded decisions flagged on the items that serve them; Pad-side edits to mirrored decisions reported       | smc, continuum               | S4    |
| G9  | Workspace bootstrap: init, delete Pad's skill copies, `.pad.toml`, collections from schemas, conventions, tags | ansible-wifi                 | S5    |
| G10 | Asks collection, `ask` / `answer` / `triage-findings` playbooks, the five missing 3.8 conventions              | this session                 | S5    |
| G11 | Shared `pad.just` imported by every project (today recipes are copied with absolute paths)                     | this session                 | S5    |
| G12 | Adapted conventions file still carries the baseline's always-on rules                                          | ansible-wifi                 | S5    |
| G13 | Cross-workspace view: needs-you, overdue, stale across all five workspaces                                     | this session                 | S6    |
| G14 | Commit link: commit-project comments `committed <hash>: <files>` on items named in the message                 | smc                          | S6    |
| G15 | Current-plan lookup for new tasks (by tag or date)                                                             | smc                          | S6    |
| G16 | Replay of asks and notes parked in SCRATCHPAD while Pad was down                                               | this session                 | S6    |
| G17 | Cross-project messages through Pad (today `project_sync.py`, APN-only; pushes lost with no listener)           | this session                 | S6    |
| G18 | Known defects: unquoted `{{ARGS}}` in nine recipes; guideline 3.1 code block uses old flag forms               | review 2026-11-19            | S1    |

## 5. Stages

Each stage is plan-first, built under skill-coder (purpose header, docstrings, `--apply` for writes, timeouts, tests with a fake pad, measured runtime), passes `just check` in skill-pad, and is tried
in smc-resiliency before the other workspaces. Budget: a sync of one project under 10 s for 100 items.

| Stage | Builds                                                                                                 | Done when                                                                           |
| ----- | ------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------- |
| S0    | Operator answers section 6; `trackers-truth` rewritten with the 3.1 table                              | answers recorded here and in SCRATCHPAD; convention applied to the five workspaces  |
| S1    | `padlib` (G1); existing scripts moved onto it; G18 fixed                                               | all ten tests pass on padlib; no script parses Pad JSON itself                      |
| S2    | `pad_item.py new / comment / close / attach` with templates, allocator, touched-items check (G2-G5)    | a task and a bug created, updated and closed in smc-resiliency; item-check exit 0;  |
|       |                                                                                                        |   a rerun creates nothing                                                           |
| S3    | `pad_sync.py` for Pad-owned types (bugs, FR, TD) in smc-resiliency, replacing the tracker export       | edit a bug in bug-tracker.md, sync, file regenerated; revert restores it; a         |
|       |   refusal; journal and revert (G6)                                                                     |   both-sides edit is refused                                                        |
| S4    | `pad_links.py` (G7, G8) as a warning in `just check` of smc, UNC, continuum, ansible-wifi              | first run's findings triaged; the check fails when a finding is planted             |
| S5    | `pad.just`, workspace bootstrap, Asks and its playbooks and conventions (G9-G12); the collections decided in D6, D7 and D9 (3.8); repo-owned field     | a new workspace set up by one recipe; one test ask end to end (guidelines rollout   |
|       |   push for plan and stage trackers                                                                     |   step 2)                                                                           |
| S6    | Cross-workspace view, commit link, current plan, replay, cross-project messages (G13-G17)              | the operator's morning view comes from one recipe                                   |

S1 to S3 cover the operator's request; S4 and S5 make it hold across projects; S6 is improvement and can be reordered.

## 6. Decisions for the operator

| #   | Question                                                                                                                     | Recommendation                                                  |
| --- | ---------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| D1  | Adopt one owner per record type (3.1) instead of "Pad first" for everything, and rewrite `trackers-truth` to name the types? | yes: all three sessions and the record checks need it           |
| D2  | For Pad-owned types, may the generated markdown block be edited and synced into Pad (3.3), or must edits go into Pad only?   | allow it: that is the flow asked for, guarded by                |
|     |                                                                                                                              |   conflict refusal                                              |
| D3  | Repo-owned plan and stage trackers: push status and dates to Pad, or link only?                                              | push fields only, never bodies                                  |
| D4  | Journal location: in each project (`docs/pad-sync/`, committed) or central in skill-pad data?                                | in each project, so it travels with the files it reverts        |
| D5  | Canary order after smc-resiliency: continuum, UNC, ansible-wifi?                                                             | continuum next: it already runs per-type truth                  |
| D6  | Create a Risks collection (RISK) in smc-resiliency and UNC as the one risk register, items linked to design-doc sections?    | yes: risks are scattered across three design docs today         |
| D7  | Create a Handoffs collection (HND) in a shared hub workspace for cross-project messages, backing `project_sync.py`?          | yes, trial in enterprise-strategy alongside the outbox first     |
| D8  | Create a Runs collection (RUN) for bench and lab runs, each pointing at its verbatim repo record and attached log?          | defer until S3 is done; the repo record stays the truth          |
| D9  | Add Asks and Decisions to smc-resiliency, UNC and ansible-wifi; fix the Tech Debt schema to declare `priority`?            | yes: Asks is already in force by the guidelines                  |

## 7. Not verified and risks

- How continuum's ASK-15 to ASK-180 were created is unknown (continuum-32 did not create them); its CHANGELOG of 2026-11-18 would say.
- Whether Pad's `--expected-seq` covers field-only updates as it does bodies is not tested; S2 tests it before S3 relies on it.
- `pad item patch --expected-seq` applies to a moved item when its anchors still match (help text, VERIFIED); the sync uses `item update`, not patch.
- Rate limits: the threshold is not documented; ansible-wifi slept 1 s between writes. S1 measures it.
- Risk: a sync that writes into Pad from a hand-edited block widens what an agent can change; every push is a plan first, and the journal is committed before the run is reported done.
- Risk: the map drifts from the markers; `pad_sync.py check` in `just check` rebuilds and compares on every run.
