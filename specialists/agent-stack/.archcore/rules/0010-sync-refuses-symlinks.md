Title: Rule 0010 — Sync refuses symlinks and enforces containment
Category: durable-rule
Status: superseded
Promoted: 20260902_0245 by skill-ai-it promote
Accepted: 20260902_0300 by operator
Source: scripts/sync_auto_company.py, audit finding A2
Summary: A symlink in an upstream checkout is refused outright, and both source and destination are verified to resolve inside their roots.
> **SUPERSEDED 20260903 — upstream sync retired.** Agent Stack is maintained as its own project now; there is no upstream to sync from, so `scripts/sync_auto_company.py`, `upstream-state.json` and
> `translation-memory.json` are removed. Kept as the record of a decision that was made and implemented, not as a live rule. The reasoning about report-first application, atomic promotion and symlink
> refusal remains correct for any future tool that copies files into this tree.


# Rule 0010 — Sync refuses symlinks and enforces containment

## Rule

- A symlink encountered while walking an upstream checkout **raises**; it is never followed.
- A source file must resolve inside the source root, and a tracked destination's parent must resolve inside the canonical stack root.

## Why refusal rather than filtering

`is_file()` follows symlinks, and `rglob` descends into symlinked directories, so a link supplied by the upstream repository could make the walk read and copy a
file anywhere on the machine — `copy2` copies content, not the link. Deciding which links are benign is a judgement the sync tool should not be making at all.
Closes audit finding A2.
