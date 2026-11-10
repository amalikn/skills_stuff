---
title: "skill-pad is the operator's own skill; Pad's plugin is not used"
type: adr
status: accepted
tags: [decision, architecture]
created: 2026-11-10
---

# ADR: skill-pad is the operator's own skill; Pad's plugin is not used

Status: accepted (operator, 2026-11-10)

Promoted by `skill-ai-it promote` on 2026-11-10 (operator: "yes" to writing the ADRs). Pointer document: the cited source stays canonical; this states it and links there.

## Decision

skill-pad is an operator-authored skill (one SKILL.md for Claude Code and Codex). Pad's Claude Code plugin is not installed; its skills, monitor and presence hooks are rebuilt as modes, `scripts/pad_monitor.sh` and two settings hooks. Pad-shipped skill files are not kept in the pack (`check_no_pad_shipped_skills`).

## Why

operator, 2026-11-10: "I want to develop our own skill and not rely on the plugin".

## Canonical source

[ARCHITECTURE.md](../../ARCHITECTURE.md#key-decisions), section "Key decisions".
