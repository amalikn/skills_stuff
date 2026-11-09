---
title: Memory channel is exactly proxmox
type: rule
status: accepted
tags: [memory]
created: 2026-11-07
---

# Rule: Memory channel is exactly `proxmox`

Status: accepted (operator, 2026-11-09, after the archcore review that corrected it). Follows skill-nautobot's channel `nautobot`, which the operator named.

## Rule

Memory entries about this pack use the channel `proxmox`, exactly that string, in both memory backends: memory-keeper and
mcp-project-context (the operator's rule is to write both every time). Project-specific engagement notes may also go to the engaging
project's channel.

## Enforcement

None automated. memory-keeper truncates channels to 20 characters and normalises underscores to hyphens; `proxmox` is unaffected by either.
On 2026-11-09 memory-keeper had no `proxmox` channel yet: the first write creates it; read it back to confirm the name survived.
