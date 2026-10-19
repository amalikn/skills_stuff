---
title: draw.io lessons learned elsewhere are written back here
type: rule
status: accepted
tags: [pack-content, governance]
created: 2026-10-19
Last reviewed: 2026-10-19
---

# Rule: draw.io lessons learned elsewhere are written back here

Status: accepted (operator, 2026-10-19; sources `AGENTS.md` "Cross-project write-back trigger", `references/evolution-and-write-back.md`; promoted 2026-10-19 on the operator's instruction "promote and
accept")

## Rule

A session in any project that drew, rendered, exported or read a draw.io file writes what it learned back to this pack: a dated Learned entry plus a `CHANGELOG.md` line, read back and committed. If
this pack is not writable from that task, the entry is parked in the engaging project under `## skill-drawio write-back candidates`.

## Enforcement

`tests/test_package_contract.py` `test_write_back_entries_logged`; skill-slurp-chat Step 5b; skill-coder `write_back.py --skill skill-drawio`.
