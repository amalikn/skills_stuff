---
title: "The live push feed runs under Claude Code's Monitor tool"
type: adr
status: accepted
tags: [decision, architecture]
created: 2026-11-10
---

# ADR: The live push feed runs under Claude Code's Monitor tool

Status: accepted (operator, 2026-11-10)

Promoted by `skill-ai-it promote` on 2026-11-10 (operator: "yes" to writing the ADRs). Pointer document: the cited source stays canonical; this states it and links there.

## Decision

`connect` starts `scripts/pad_monitor.sh` (consent gate, per-session lock, reconnect loop over `pad watch --stream --for-session`) with the Monitor tool and re-arms it at each 30-minute expiry; the lock prevents a double stream. Codex has no Monitor: connect there arms consent only.

## Why

operator, 2026-11-10: rebuild the connect/disconnect live feed; a skill cannot declare a session-long background process the way a plugin's monitors.json does.

## Canonical source

[ARCHITECTURE.md](../../ARCHITECTURE.md#key-decisions), section "Key decisions".
