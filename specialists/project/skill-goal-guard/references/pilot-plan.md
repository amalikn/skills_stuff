---
Title: Goal Guard v1.7 Pilot Plan
Category: plan
Status: current
Authority: the v1.7 kickoff and handoff §19, §23.6, §29, §35, §37.5, re-expressed with the real workspace paths read 2026-10-27; operator chose the full v1.7 pilot (2026-10-27)
Scope: Prerequisites, ordered steps, owner decisions, stop conditions, prototype gaps and the completion gate for the first end-to-end pilot
Last reviewed: 2026-10-27
Summary: >-
  Nine ordered steps from local Vikunja deployment and a read-only inventory to an observed allowed and blocked action in one apn spoke, one
  traced milestone with an Excel sample, and one snapshot restore; owner decisions block the write steps; a missing proof means PARTIAL.
---

# v1.7 pilot plan

## Ceiling

One Enterprise-Strategy milestone, one spoke, one Vikunja project, one coding-agent adapter (Claude Code), one approved MVP, one allowed and one blocked action, one internal target, one Excel sample,
one snapshot with one restore proof. Nothing beyond this until the pilot report is accepted (kickoff; handoff §29, §35, §37.5).

## Pilot spoke (operator, 2026-10-27)

`apn/unified-network-controller`: it has `.archcore/`, `target-map.yaml` and `code-map.toml`.

## Owner decisions (answered 2026-10-27)

| #       | Decision                  | Answer                                                                                                                                                         |
| ------- | ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| D1      | Shared `apn` repository   | Keep one repository; scope hooks, rules and `.gg/` records by project path inside it; decision logs per project folder                                         |
| D2      | Pilot spoke               | `unified-network-controller`                                                                                                                                   |
| D3      | How an owner approval     | Signed Git commit (GPG or SSH signing key); Goal Guard verifies the signature; an unsigned approval is a proposal                                               |
|         |   is authenticated        |                                                                                                                                                                |
| D3 risk | Signing key may be usable | Raised 2026-10-27: agents run as the operator's user; Git signing is not configured yet and the ssh-agent holds unlocked keys, so a key in the agent could     |
|         |   by agents               |   sign as the owner. Before step 5, use a signing key kept out of the agent that needs a touch or passphrase per signature (hardware key or per-use prompt),   |
|         |                           |   or choose another approval method                                                                                                                            |
| D4      | Management plan and       | Find them in `enterprise-strategy` (read-only); candidates below, to confirm in step 1                                                                         |
|         |   issued Excel            |                                                                                                                                                                |
| D5      | Vikunja deployment        | Docker on OrbStack, official image, bundled SQLite, persisted volumes, localhost only, image digest pinned; deployed 2026-10-27 at http://localhost:3456       |
|         |                           |   from `tools_stuff/vikunja`                                                                                                                                   |
| D6      | Per-project folder name   | `.gg/`                                                                                                                                                         |

## D4 candidates found 2026-10-27 (read-only, not yet confirmed)

| File (under `apn/enterprise-strategy/`)                                             | What it is                                                                                                     |
| ----------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `workstreams/continuity/unc-and-smc-project-plan-20261005_1605.md`                  | Full plan; `## Milestones` table with stable IDs M1-M11 (dates, owner project, `Dated` or `Proposed`); front   |
|                                                                                     |   matter `Status: draft`                                                                                       |
| `workstreams/continuity/unc-and-smc-project-plan-short-20261005_2031.{md,docx,pdf}` | Short version; the docx/pdf may be what was issued                                                             |
| `communications/emails/enterprise-strategy-plan-martin-20261014_1733.eml`           | Plan sent to management 2026-10-14; shows what was issued                                                      |
| `workstreams/continuity/weekly-updates/weekly-update-20261023_1100.xlsx`            | Latest weekly update workbook; candidate for the "issued Excel"                                                |

Open point for step 1: the plan says `draft` while `Dated` rows come from "the project's adopted plan", so which revision is the protected management baseline must be confirmed from the 2026-10-14
email before any baseline is registered (handoff §23.1, H08). Candidate pilot milestones are the UNC `Dated` rows (M2 1 Nov, M4 15 Nov, M7 29 Nov, M9 11-15 Dec).

## Steps

| #   | Step                                                                                     | Writes?             | Exit evidence                                        | Tests                  |
| --- | ---------------------------------------------------------------------------------------- | ------------------- | ---------------------------------------------------- | ---------------------- |
| 0   | **Done 2026-10-27:** Vikunja 2.7.1 at http://localhost:3456; version, URL, OpenAPI recorded | operator            | version + `openapi.json` saved under `documents/`    | —                      |
| 1   | Inventory (read-only): `target-map.yaml`, `code-map.toml`, `.archcore/`, `AGENTS.md`,    | no                  | inventory table with exact paths                     | M01, S01, S08          |
|     |   Git boundaries, installed Claude Code version and hook payloads, hub plan and Excel,   |                     |                                                      |                        |
|     |   Vikunja schema                                                                         |                     |                                                      |                        |
| 2   | Current → proposed table: hierarchy, storage, owned files, which hooks really block      | no                  | table (D1-D6 answered 2026-10-27)                    | F01-F04                |
| 3   | Owner approves the minimal change list                                                   | —                   | approval record                                      | —                      |
| 4   | **Built 2026-10-27 (operator: "create all those scripts"), ahead of steps 1-3; partial,** | pack files          | `just check` green; prototype characterised first    | T01-T15, GG-001-012,   |
|     |   **see below.** Rewrite `scripts/goal_guard.py` per skill-coder: baseline/BLOCK, decision |                     |                                                      |   GG-401-403,          |
|     |   order, ranking pipeline, Vikunja reader, `decisions.jsonl`, docstrings and headers;    |                     |                                                      |   406-408, 412         |
|     |   fixtures for T01-T15                                                                   |                     |                                                      |                        |
| 5   | Write the UNC MVP contract with the owner; approve it                                    | project `.gg/`      | approved `mvp.yaml` revision 1                       | T02, T08               |
| 6   | Claude Code PreToolUse adapter in UNC: advisory, then blocking; Archcore rule            | project hook + rule | **observed** allowed action and **observed** blocked | T03-T05, F07, F14      |
|     |                                                                                          |                     |   out-of-scope action; unenforced paths listed       |                        |
| 7   | Trace: hub milestone → baseline → MVP criterion → target-map target → Vikunja task;      | `.gg/mappings.yaml` | one verified trace, or REVIEW naming the gap         | M02-M08, H01, H03,     |
|     |   internal target; Excel sample                                                          |                     |                                                      |   H06-H09, D03-D09     |
| 8   | Snapshot UNC tasks, parent manifest, dry run, clean-instance restore                     | data peer           | checksums, counts, relations restored, no duplicates | S02-S07                |
|     |                                                                                          |   + manifest        |                                                      |                        |
| 9   | Pilot report: PASS/FAIL per applicable test, exact changes, unsupported paths, data not  | no                  | `reports/pilot-report-<YYYYMMDD_hhmm>.md`            | —                      |
|     |   captured, rollback, recommendation                                                     |                     |                                                      |                        |

## Prototype gaps fixed in step 4

Built 2026-10-27 under skill-coder: `goal_guard.py` (baseline, BLOCK, the decision order, the ranking pipeline, Vikunja reads, `decisions.jsonl`) plus the tools for steps 6-8 (draft hook, doctor,
trace, snapshot/restore, Excel sample); `just check` green (71 tests). Catalogue and live checks still open: [../scripts/readme.md](../scripts/readme.md).

What step 4 did not do, stated plainly:

- The prototype's outputs were not characterised before the rewrite; its behaviour was replaced on purpose (the settled conflicts in [decision-rules.md](decision-rules.md)), and its test cases (park unlinked, review
  scope, proceed, blocked dependency, done without evidence) are re-expressed in `tests/test_decide.py` and `tests/test_rank.py`.
- Fixtures cover T01, T02, T04-T07, T11 and T15; the other T and GG tests in [test-catalog.md](test-catalog.md) have no fixture yet.
- A dependency cycle among Vikunja tasks leaves its tasks ineligible but is not reported by `next` (the prototype's `validate` reported cycles); snapshot `verify` does report it.
- JSON schemas (`schemas/`) were not written; the record contract is enforced in `records.py` and `mvp.py`.
- Steps 1-3 (inventory, current → proposed table, owner approval of the change list) are still owed before anything is installed in the pilot spoke.
