---
title: "docs/history is one folder per kind with a generated index"
status: accepted
tags: [records]
---

Added 2026-11-11; [AGENTS.md](../../AGENTS.md) (Working rules) has one line pointing here.

## Rule

Rotated records live in `docs/history/<kind>/` (changelog, scratchpad, roadmap, session-records, sync); the folder's `readme.md` index is
generated with a summary line per file and keeps descriptions written by hand. Writers and readers go through
`scripts/records/history_layout.py`; a flat folder moves with `just history-migrate <project>`. Detail:
[references/files-history.md](../../references/files-history.md).

## Rationale

Operator, 2026-11-11: "create sub directories and make it a standard"; one flat folder held 369 files in UNC, and its index said only
"1 entries from CHANGELOG.md".
