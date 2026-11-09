---
title: Capability search order
type: rule
status: accepted
tags: [capability, extension]
created: 2026-11-07
---

# Rule: Capability search order

Status: accepted (operator, 2026-11-09, after the archcore review that corrected it). The order is the operator's (USER_STATED 2026-10-01, accepted for skill-nautobot on 2026-10-05), applied here to Proxmox.

## Rule

Before building anything around Proxmox VE, search in this order and state at each step why the previous level cannot meet the acceptance test:

1. Proxmox VE core (API, CLIs, SDN, HA, firewall, vzdump, metric servers, notifications).
2. Proxmox products (Proxmox Backup Server, Proxmox Datacenter Manager) and the bpg/proxmox provider.
3. Supported seams: hook scripts, cloud-init custom data, API clients.
4. Compatible external FOSS through the API.
5. A from-scratch component, only when the acceptance test still cannot be met.

Never patch PVE's own files on a node; an update overwrites them silently.

## Enforcement

Judgement at design time; `SKILL.md` (Search before building) and `references/capability-extension.md` restate it at the point of decision.
