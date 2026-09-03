Title: ADR 0009 — Upstream sync apply is staged, then promoted
Category: architecture-decision
Status: superseded
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: scripts/sync_auto_company.py, audit finding A1
Summary: Files are staged beside their destinations and promoted by rename; state is written atomically. Implemented 2026-09-02, closing audit finding A1.
> **SUPERSEDED 20260903 — upstream sync retired.** Agent Stack is maintained as its own project now; there is no upstream to sync from, so `scripts/sync_auto_company.py`, `upstream-state.json` and
> `translation-memory.json` are removed. Kept as the record of a decision that was made and implemented, not as a live rule. The reasoning about report-first application, atomic promotion and symlink
> refusal remains correct for any future tool that copies files into this tree.


# ADR 0009 — Upstream sync apply is staged, then promoted

## Decision

`apply_safe_changes` stages every file beside its destination, then promotes them all with `os.replace`. `write_json` writes a sibling temp file and renames it.

## Rationale

The previous version copied straight into the tree one file at a time, so a failure on file 7 of 12 left six files updated, six stale, and the state file
describing neither — and recovery from that forces `manual_merge` on files that were never in conflict.

Promotion is a rename per file rather than one transaction, which POSIX cannot give across a directory tree. What it removes is the slow part — reading and
writing content — from the window where a failure does damage. What remains is a sequence of atomic renames over a set already known to be complete and readable.

## Consequences

- Supersedes the deferral recorded in `REVISION_NOTES.md`, which said this revision would not rewrite the sync transaction model.
- Paired with [rule 0010](../rules/0010-sync-refuses-symlinks.md), which closes the containment half of the same audit.
