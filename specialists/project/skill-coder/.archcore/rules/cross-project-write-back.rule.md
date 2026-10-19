---
title: Reusable practice learned elsewhere is written back here
type: rule
status: accepted
tags: [pack-content, governance]
created: 2026-10-19
Last reviewed: 2026-10-19
---

# Rule: Reusable practice learned elsewhere is written back here

Status: accepted (stated in `AGENTS.md` "Cross-project write-back trigger"; promoted 2026-10-19 on the operator's instruction to add the missing Archcore entries)

## Rule

Any project that invokes this skill and learns reusable programming practice writes it back before the session closes: a dated Learned entry in the focused reference or language file, plus one
`CHANGELOG.md` line under `## Unreleased` naming the file and date, read back after writing. A finding that contradicts existing text is a Disputed entry beside it (`Conflicts: <claim ID>`), never a
deletion or silent rewrite. If this source is not writable from the engaging task, the entry stays in the engaging project as a candidate. A project-specific rule stays in that project.

## Why

The pack improves only from real engagements; a lesson left in one project's notes is lost to every other project.

## Enforcement

`tests/test_package_contract.py` (`test_write_back_entries_logged`, proven able to fail by `test_bad_write_back_entries`): every Learned or Disputed entry has its CHANGELOG line. Entry format:
`references/evolution-and-write-back.md`.
