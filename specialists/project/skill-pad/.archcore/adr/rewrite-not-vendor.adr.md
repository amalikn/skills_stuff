---
title: "Pad's text is rewritten into references; the upstream mirror stays verbatim"
type: adr
status: accepted
tags: [decision, architecture]
created: 2026-11-10
---

# ADR: Pad's text is rewritten into references; the upstream mirror stays verbatim

Status: accepted (operator, 2026-11-10)

Promoted by `skill-ai-it promote` on 2026-11-10 (operator: "yes" to writing the ADRs). Pointer document: the cited source stays canonical; this states it and links there.

## Decision

What Pad's skill, plugin and docs teach is rewritten into `references/*.md` in this pack's words, never pasted. `references/upstream/` keeps verbatim sources per version for diffing at an upgrade (`references/upgrade.md`) and is never edited.

## Why

operator, 2026-11-10: "extract information from both ... then remove these files"; "tweak and optimize it, not like a copy paste".

## Canonical source

[ARCHITECTURE.md](../../ARCHITECTURE.md#key-decisions), section "Key decisions".
