---
title: Memory channel is exactly proxmox
type: rule
status: proposed
tags: [memory]
created: 2026-11-07
---

# Rule: Memory channel is exactly `proxmox`

Status: proposed (2026-11-07). skill-nautobot's channel `nautobot` was named by the operator; `proxmox` follows the same pattern and needs
the operator's confirmation.

## Rule

memory-keeper entries about this pack use the channel `proxmox`, exactly that string. Project-specific engagement notes may also go to the
engaging project's channel.

## Enforcement

None automated. memory-keeper truncates channels to 20 characters and normalises underscores to hyphens; `proxmox` is unaffected by either.
