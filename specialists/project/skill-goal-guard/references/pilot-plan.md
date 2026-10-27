---
Title: GoalGuard v1.7 Pilot Plan
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

| # | Decision | Answer |
|---|---|---|
| D1 | Shared `apn` repository | Keep one repository; scope hooks, rules and `.gg/` records by project path inside it; decision logs per project folder |
| D2 | Pilot spoke | `unified-network-controller` |
| D3 | How an owner approval is authenticated | Signed Git commit (GPG or SSH signing key); GoalGuard verifies the signature; an unsigned approval is a proposal |
| D3 risk | Signing key may be usable by agents | Raised 2026-10-27: agents run as the operator's user; Git signing is not configured yet and the ssh-agent holds unlocked keys, so a key in the agent could sign as the owner. Before step 5, use a signing key kept out of the agent that needs a touch or passphrase per signature (hardware key or per-use prompt), or choose another approval method |
| D4 | Management plan and issued Excel | Find them in `enterprise-strategy` (read-only); candidates below, to confirm in step 1 |
| D5 | Vikunja deployment | Docker on OrbStack, official image, bundled SQLite, persisted volumes, localhost only, image digest pinned; deployed 2026-10-27 at http://localhost:3456 from `tools_stuff/vikunja` |
| D6 | Per-project folder name | `.gg/` |

## D4 candidates found 2026-10-27 (read-only, not yet confirmed)

| File (under `apn/enterprise-strategy/`) | What it is |
|---|---|
| `workstreams/continuity/unc-and-smc-project-plan-20261005_1605.md` | Full plan; `## Milestones` table with stable IDs M1-M11 (dates, owner project, `Dated` or `Proposed`); front matter `Status: draft` |
| `workstreams/continuity/unc-and-smc-project-plan-short-20261005_2031.{md,docx,pdf}` | Short version; the docx/pdf may be what was issued |
| `communications/emails/enterprise-strategy-plan-martin-20261014_1733.eml` | Plan sent to management 2026-10-14; shows what was issued |
| `workstreams/continuity/weekly-updates/weekly-update-20261023_1100.xlsx` | Latest weekly update workbook; candidate for the "issued Excel" |

Open point for step 1: the plan says `draft` while `Dated` rows come from "the project's adopted plan", so which revision is the protected management baseline must be confirmed from the
2026-10-14 email before any baseline is registered (handoff §23.1, H08). Candidate pilot milestones are the UNC `Dated` rows (M2 1 Nov, M4 15 Nov, M7 29 Nov, M9 11-15 Dec).

## Steps

| #   | Step                                                                                                    | Writes?             | Exit evidence                      | Tests                     |
| --- | ------------------------------------------------------------------------------------------------------- | ------------------- | ---------------------------------- | ------------------------- |
| 0   | **Done 2026-10-27:** Vikunja 2.7.1 at http://localhost:3456; version, URL, OpenAPI recorded                                          | operator            | version + `openapi.json` saved     | —                         |
|     |                                                                                                         |                     |   under `documents/`               |                           |
| 1   | Inventory (read-only): `target-map.yaml`, `code-map.toml`, `.archcore/`, `AGENTS.md`, Git boundaries,   | no                  | inventory table with exact paths   | M01, S01, S08             |
|     |   installed Claude Code version and hook payloads, hub plan and Excel, Vikunja schema                   |                     |                                    |                           |
| 2   | Current → proposed table: hierarchy, storage, owned files, which hooks really block                     | no                  | table (D1-D6 answered 2026-10-27)              | F01-F04                   |
| 3   | Owner approves the minimal change list                                                                  | —                   | approval record                    | —                         |
| 4   | Rewrite `scripts/goal_guard.py` per skill-coder: baseline/BLOCK, decision order, ranking pipeline,      | pack files          | `just check` green; prototype      | T01-T15, GG-001-012,      |
|     |   Vikunja reader, `decisions.jsonl`, docstrings and headers; fixtures for T01-T15                       |                     |   characterised first              |   GG-401-403, 406-408, 412         |
| 5   | Write the UNC MVP contract with the owner; approve it                                                   | project `.gg/`      | approved `mvp.yaml` revision 1     | T02, T08                  |
| 6   | Claude Code PreToolUse adapter in UNC: advisory, then blocking; Archcore rule                           | project hook + rule | **observed** allowed action and    | T03-T05, F07, F14         |
|     |                                                                                                         |                     |   **observed** blocked out-of-scope |                           |
|     |                                                                                                         |                     |   action; unenforced paths listed  |                           |
| 7   | Trace: hub milestone → baseline → MVP criterion → target-map target → Vikunja task; internal target;    | `.gg/mappings.yaml` | one verified trace, or REVIEW      | M02-M08, H01, H03,        |
|     |   Excel sample                                                                                          |                     |   naming the gap                   |   H06-H09, D03-D09        |
| 8   | Snapshot UNC tasks, parent manifest, dry run, clean-instance restore                                    | data peer           | checksums, counts, relations       | S02-S07                   |
|     |                                                                                                         |   + manifest        |   restored, no duplicates          |                           |
| 9   | Pilot report: PASS/FAIL per applicable test, exact changes, unsupported paths, data not captured,       | no                  | `reports/pilot-report-<YYYYMMDD_hhmm>.md`                  | —                         |
|     |   rollback, recommendation                                                                              |                     |                                    |                           |

## Prototype gaps fixed in step 4

Listed once, in [../scripts/readme.md](../scripts/readme.md) (Known gaps). Characterise the prototype's outputs before changing behaviour.
