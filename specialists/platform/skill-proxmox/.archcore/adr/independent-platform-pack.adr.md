---
title: Independent Proxmox VE platform pack
type: adr
status: proposed
tags: [pack-boundary, proxmox]
created: 2026-11-07
---

# ADR: Independent Proxmox VE platform pack

Status: proposed (2026-11-07, at creation; awaits operator acceptance)

## Context

Proxmox VE knowledge first gathered in project work (smc-resiliency's x86 lab, the vbng podbng lab). On 2026-11-07 the operator asked for
"skill-proxmox like skill-nautobot ... with the same detail and logic" (USER_STATED).

## Decision

`skill-proxmox` is a standalone, cross-project pack for the Proxmox VE platform and OpenTofu with the bpg/proxmox provider, beside
skill-nautobot and skill-openwisp under `specialists/platform/`. It is not a section of a project or of skill-smc.

## Consequences

- The primary pack for a task is chosen by the object being changed (`SKILL.md`, Route the task); a guest's own OS stays with its workload.
- Node names, addresses, VMIDs and lab inventories stay in the engaging project.
- Every engagement owes a write-back here (`references/evolution-and-write-back.md`).

Confidence: high for the operator's request; the boundary wording is this session's proposal.
