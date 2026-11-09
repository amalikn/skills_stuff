---
title: OpenTofu drives Proxmox VE through the bpg/proxmox provider, never Telmate
type: adr
status: accepted
tags: [opentofu, provider]
created: 2026-11-09
---

# ADR: bpg/proxmox, not Telmate

Status: accepted (operator, 2026-11-09: "promote and accept all"; the policy itself predates the pack and is stated in `SKILL.md` and `references/opentofu-bpg-provider.md` as operator policy).

## Context

Two community OpenTofu/Terraform providers drive Proxmox VE: `bpg/proxmox` and `Telmate/proxmox`. The pack's worked examples, captures (`documents/research-sources-20261107/bpg-provider-*`) and claims
(P-C03 and others) all rest on bpg/proxmox 0.120.0.

## Decision

Every OpenTofu configuration this pack describes uses `bpg/proxmox`. The Telmate provider is not used, not documented and not offered as an alternative.

## Consequences

- Provider facts live in `references/opentofu-bpg-provider.md` and are checked against the version in the project's lock file.
- A project found on Telmate is a migration task for that project, not a second supported path here.
- The operator's reason for the policy is not recorded in the pack; if it is needed later, ask and add it here.

Confidence: high for the decision (operator policy, stated twice in the pack); low for the rationale, which is not written down.
