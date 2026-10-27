---
Title: Goal Guard Authority and Sources of Truth
Category: reference
Status: current
Authority: consolidated from the v1.7 handoff §2-3, §17, §23.1, §25, §31, §36-37 and research pack 00; operator decisions 2026-10-27
Scope: Which system owns which record, conflict order, trust levels and what Goal Guard must never hold
Last reviewed: 2026-10-27
Summary: >-
  Vikunja owns live tasks; Goal Guard owns scope, approvals, decisions, deferred ideas, internal targets and forecasts; Enterprise-Strategy owns
  approved cross-project decisions and management commitments; Archcore owns technical rules. One owner per record, references not copies.
---

# Authority and sources of truth

## Decision that settles the design lines

The research pack (v0.x) made Goal Guard's own store canonical for tasks and treated Vikunja as a read-only projection. The v1.7 handoff made Vikunja the live task authority. **The operator chose
Vikunja (2026-10-27).** Everything below follows that; research-pack text that says otherwise is superseded on this point only.

## Ownership table

| Record                                            | Owner                                         | Goal Guard's relationship                                            | Source                     |
| ------------------------------------------------- | --------------------------------------------- | ------------------------------------------------------------------- | -------------------------- |
| Goal, MVP, exclusions, acceptance                 | Human owner, recorded by Goal Guard            | Authoritative contract (`mvp.yaml`), revision-controlled,           | handoff §3, §5, §31        |
|   criteria, approvals                             |                                               |   owner-approved only                                               |                            |
| Scope decisions, overrides, change approvals      | Goal Guard append-only decision log            | Writes; never rewrites history                                      | handoff §8, §31; pack 00   |
| Deferred ideas (PARK)                             | Goal Guard (`deferred.yaml`)                   | Writes; ideas never become Vikunja tasks without explicit promotion | handoff §10                |
| Live tasks: priority, status, due/start/end       | **Vikunja**                                   | Reads; writes only through an authorised, attributable action after | handoff §2.6,              |
|   dates, relations, order, assignee               |                                               |   a decision                                                        |   §17, PORT-001            |
| Owner's internal target, forecast and             | Goal Guard metadata keyed to stable Vikunja    | Writes                                                              | handoff §25, DATE-002/003  |
|   its evidence                                    |   milestone/task IDs                          |                                                                     |                            |
| Management commitments (milestone, committed      | Enterprise-Strategy approved baseline,        | Reads and references; never edits                                   | handoff §23.1,             |
|   date, scope, approver, revision)                |   registered by Goal Guard as an               |                                                                     |   §25, DATE-001            |
|                                                   |   immutable reference                         |                                                                     |                            |
| Issued management Excel                           | Dated snapshot of a baseline revision         | Reads metadata (hash, date, revision); generated exports are        | handoff §23.1, §25         |
|                                                   |                                               |   new versions                                                      |                            |
| Approved cross-project decisions,                 | Enterprise-Strategy hub                       | Checks freshness, routes proposals as REVIEW                        | handoff §22                |
|   shared interfaces                               |                                               |                                                                     |                            |
| Technical rules, architecture, specs, ADRs        | Archcore / the project                        | Surfaces; binding inside approved scope                             | handoff §3, §9             |
| Project targets                                   | The project's `target-map.yaml`               | Reads only in the pilot; a target is a candidate, not approval      | handoff §36                |
|                                                   |   (existing writer)                           |                                                                     |                            |
| Script index                                      | The project's `code-map.toml`                 | Reads only; evidence, never permission                              | handoff §36                |
| Markdown knowledge extraction                     | Knowledge Curator                             | None; Curator may read Goal Guard records, never approve or promote  | handoff §3, §10            |
| Agent/subagent running state                      | Instrumented telemetry                        | `UNKNOWN` when absent or stale; an assignee is not a running agent  | pack 00, GG-204/205        |
| Completion proof                                  | Tests, review artefacts, acceptance evidence  | Required before DONE or delivered; agent claims are not proof       | handoff MVP-009, §6        |
|                                                   |                                               |                                                                     |   Stage E                  |

## Never held by Goal Guard

- A second editable copy of task priority, status, due date or dependencies (PORT-001, M08). `priorities.yaml` holds ranking **rules**, never values (handoff §37.2).
- A copy of target-map content, hub documents or the management plan; only IDs, paths, revisions and hashes (handoff §36.1, §22.2).
- Secrets, tokens, raw transcripts, or APN data in a `me` context (handoff §31, §37.3).

## Conflict order

Owner-approved scope or commitment > Goal Guard global controls > partition (`apn` / `me`) constraints > project scope > Archcore in-scope guidance > Vikunja operational data > agent suggestion
(handoff §32). A more specific layer may tighten, never loosen, an ancestor's safety, privacy, approval or MVP boundary (handoff §18.2). Two sources that disagree are reported with both references and
resolved by REVIEW, never by picking the newest or longest file (handoff §22.2).

## Trust levels

| Input                                                    | Counts as                                 | Source                         |
| -------------------------------------------------------- | ----------------------------------------- | ------------------------------ |
| Model or agent claim (necessity, criterion link, "done") | Untrusted proposal                        | pack 06 §4                     |
| Provider hook event                                      | Observation, not approval                 | pack 06 §4                     |
| Authenticated owner decision naming the exact revision   | Approval                                  | handoff §8, MVP-007            |
| Deterministic tests, human verification                  | Completion evidence                       | pack 06 §4, handoff §6 Stage E |
| A Vikunja task, its title or priority                    | Operational data, never approval of scope | handoff MVP-007, PORT-002      |

Owner approval is a signed Git commit (GPG or SSH signing key) that Goal Guard verifies; Git authorship alone does not prove the approver (handoff §33), and an unsigned approval is only a proposal
(operator, 2026-10-27; [pilot-plan.md](pilot-plan.md), D3). Open risk: a key the agent can reach could sign as the owner; see D3 risk in [pilot-plan.md](pilot-plan.md).
