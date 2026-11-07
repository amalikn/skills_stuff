---
title: Independent Vagrant platform pack
type: adr
status: proposed
tags: [pack-boundary, vagrant]
created: 2026-11-07
---

# ADR: Independent Vagrant platform pack

Status: proposed (2026-11-07), awaiting the operator.

## Context

Vagrant and Parallels lab knowledge was gathered inside smc-resiliency's Pi spike work (its Vagrantfile, `spike/to_vm.sh`, `spike/vm/sm/setup_sm.sh`) and in project rules. On 2026-11-07 the
operator asked for "skill-proxmox and skill-vagrant based on the learnings", built like skill-nautobot, and for online research to widen them.

## Decision

`skill-vagrant` is a standalone, cross-project pack under `specialists/platform/` for local lab VMs with Vagrant and the Parallels provider on Apple silicon. It is separate from
`skill-proxmox` (the x86 lab and OpenTofu) and from the skills that own what runs inside a guest (`skill-smc` for SMC images).

## Consequences

- The primary pack for a task is chosen by the object being changed (Vagrantfile, box, Parallels VM, lab guard).
- VM names, lab addresses and stages stay in the engaging project; the pack cites them only as worked examples with path and commit.
- Every engagement owes a write-back here (`references/evolution-and-write-back.md`).

Confidence: high on the operator's request; boundaries proposed by the building agent.
