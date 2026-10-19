---
title: Installed now, made the default only after testing
type: adr
status: accepted
tags: [runtime, governance]
created: 2026-10-19
Last reviewed: 2026-10-19
---

# ADR: Installed now, made the default only after testing

Status: accepted (operator decisions in chat, 2026-10-19: "install it as skill but dont make it default yet" and "make it default once we have tested the skill"; source `SCRATCHPAD.md` KEEP item
"Activation"; promoted 2026-10-19 on the operator's instruction to add the missing Archcore entries)

## Context

A pack named in the global policy as the skill "for any code" is loaded on every coding task in every project, by every agent. An untested pack in that position spreads its mistakes everywhere at
once.

## Decision

Two stages. Now: the pack is installed (directory symlinks into the Claude, Codex and Hermes skill folders, and its row in the skills_stuff `README.md`), so it can be invoked by name and tested.
Later, once the operator judges it tested: one pass makes it the default, in the global policy's "Skills, context, and task routing" line (then the Codex sync), the skills_stuff
`.agents/skill-surfaces.md` row, and governance `coding-guide.md` linking the pack as its detailed source. The live step list and test evidence stay in the `SCRATCHPAD.md` KEEP item.

## Consequences

- Until the switch, the pack is invoked by name only. Its `SKILL.md` description says so (2026-10-19 review: the first description began "Use before
  writing, changing ... code in any project", which made Claude match it on every coding task, a default in all but name). The switch restores
  that broad trigger in the description, in the same pass as the global policy line.
- Outside the pack, governance `coding-guide.md` already links its naming reference (2026-10-19) as the canonical naming mapping; that is a citation,
  not routing, and does not make the pack the default.
- The default switch is one pass across all three surfaces, never one surface at a time.
- skill-ai-it's code checks calling this pack's helpers (one source per rule) is a separate later change, not part of the switch.
