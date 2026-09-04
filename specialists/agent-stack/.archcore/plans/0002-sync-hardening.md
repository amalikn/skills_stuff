Title: Plan 0002 — Sync hardening (audit A1/A2) — COMPLETED
Category: approved-plan
Status: accepted
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: REVISION_NOTES.md, docs/audits/audit-agent-stack-full-20260901_1010.md
Summary: Both P1 audit findings implemented 2026-09-02. Retained as the record of a closed plan.

# Plan 0002 — Sync hardening (audit A1/A2) — COMPLETED

## Status: COMPLETED 2026-09-02

Both findings were deliberately deferred at the 2026-09-01 revision and implemented the following day.

| Finding | Was | Now |
| --- | --- | --- |
| A1 non-atomic apply | Copy-in-place per file; state written afterwards | Staged beside destination, promoted by `os.replace`; state written via temp-file rename |
| A2 symlink escape | `is_file()` followed links; only the relative path was guarded | Symlinks refused outright; source and destination containment both verified |

Recorded as [ADR 0009](../adr/0009-sync-apply-is-atomic.md) and [rule 0010](../rules/0010-sync-refuses-symlinks.md). Retained here because a closed plan is the
evidence that a deferral was honoured rather than forgotten.
