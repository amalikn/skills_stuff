---
Title: GoalGuard Test Catalog and Crosswalk
Category: reference
Status: current
Authority: consolidated from the v1.7 handoff test tables (T, P, H, D, F, M, S series), research pack 03 (GG series) and the v0.1 unit tests; specified tests, none run except the 10 v0.1 unit tests
Scope: Every test series, which phase it gates, duplicates merged, and the ID collision with the backlog
Last reviewed: 2026-10-27
Summary: >-
  146 specified tests (plus 10 v0.1 unit tests) across eight series collapse to one pilot set grouped by capability; duplicates are listed once with all their IDs;
  backlog items are renamed B-01..B-19 here to end the clash with GG-001.. tests.
---
# Test catalog and crosswalk

## Series

| Series                                              | Count | Topic                                                       | Source                     |
| --------------------------------------------------- | ----- | ----------------------------------------------------------- | -------------------------- |
| T01-T15                                             | 15    | MVP gate                                                    | handoff §13                |
| P01-P10                                             | 10    | Portfolio and policy resolution                             | handoff §19                |
| H01-H10                                             | 10    | Hub and management traceability                             | handoff §23.5              |
| D01-D12                                             | 12    | Migration, dates, Excel                                     | handoff §29                |
| F01-F14                                             | 14    | Packaging, `.gg/`, isolation                                | handoff §34                |
| M01-M08                                             | 8     | `target-map` and `code-map`                                 | handoff §36.3              |
| S01-S08                                             | 8     | Snapshot and restore                                        | handoff §37.5              |
| GG-001..012, 101..112, 201..210, 301..310, 401..425 | 69    | Decisions, portfolio, robustness, Vikunja, Thekedar-derived | pack 03                    |
| v0.1 unit tests                                     | 10    | Prototype CLI (pass, 2026-10-27)                            | `tests/test_goal_guard.py` |

**ID collision fixed here:** the research backlog's items `GG-01`..`GG-19` (pack 05) are cited in this pack as `B-01`..`B-19`; `GG-` followed by three digits is always a test.

## Merged duplicates (one behaviour, several IDs)

| Behaviour                                           | IDs                               |
| --------------------------------------------------- | --------------------------------- |
| Done without evidence is refused                    | T09, GG-203, GG-419, D08, H09     |
| Agent self-approval refused                         | T07, GG-403, GG-418               |
| Unreadable or malformed authority fails safe        | T11, GG-407 (rule PORT-008)             |
| Excluded or unrelated feature parked or blocked     | T04, T05, GG-001, GG-009, GG-401  |
| Criterion cited but unrelated                       | GG-007, GG-412                    |
| Necessary dependency needs approval                 | T06, GG-008                       |
| Blocked dependency surfaces the prerequisite        | P02, GG-103, GG-105               |
| Dependency cycle is an error                        | GG-104, v0.1 `test_cycle`         |
| One operator focus                                  | PORT-004, GG-108, v0.1 `test_wip` |
| Vikunja unavailable: read-only, stale warning       | P05, S05, GG-306                  |
| Idempotent import, no duplicates                    | D02, GG-301, part of S06          |
| `apn` / `me` isolation                              | P06, H10, D12, F02, S07           |
| No assumed Archcore/AGENTS inheritance              | P08, F04                          |
| Hook absent or schema differs: report advisory      | F14, GG-421, GG-423               |
| Protected baseline not editable from the UI         | D03, F09, GG-207                  |
| Interrupt and resume                                | P10, GG-102, GG-415               |
| Vikunja priority change re-ranks without file edits | P09, F08                          |
| Brainstorm or extraction never changes scope        | T12, T13, GG-005                  |

## Pilot set (by capability)

| Capability               | Tests                                |
| ------------------------ | ------------------------------------ |
| Gate                     | T01-T15; GG-001-012; GG-401-403, 406-408, 412 |
| Ranking and focus        | P01-P05, P09; GG-101, 103-108, 110   |
| Resolution and isolation | P06-P08; F01-F05, F07-F09, F13, F14 |
| Hub and management trace | H01, H03, H06-H09; D03-D09           |
| Maps                     | M01-M08                              |
| Snapshot and restore     | S01-S08                              |

## Later phases

L1: P10, GG-102, 109, 111, 112, 404, 405 (file scope, feature #9), 413-415, F06, F11, H02, H04, H05. L2: GG-201-210, 301-310, 409-411, 416-418, 420-422, F10, F12, D01, D02, D10, D11. L5: GG-424. Conditional: GG-425 whenever source
code is copied.

## Evaluation thresholds (pack 03)

At least 40 labelled cases across both projects and ad-hoc work, balanced between necessary work and creep; aim for ≥90% macro-average agreement and 100% prevention of known P0 expansions; measure, do
not assume. Track `false_block_rate`, `missed_scope_expansion_rate`, `time_to_decision`, `duplicate_alert_rate`, `operator_interruption_count`. Every automated test asserts verdict, `reason_code`, no
unauthorised authoritative mutation and journal count where relevant.
