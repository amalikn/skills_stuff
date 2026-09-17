---
title: Vault Reference File Avoids OPA-Blocked Path Words
type: adr
status: accepted
date: 20260917
provenance: promoted from SCRATCHPAD.md (KEEP, Recent decisions) on 20260917; accepted by operator 20260917
---

# ADR: Vault Reference File Avoids OPA-Blocked Path Words

## Status

Accepted

## Context

The workspace's OPA write-gate hard-blocks any file **path** containing certain sensitive-sounding substrings, regardless of the file's actual content. This pack's device-access and KeePassXC
vault-structure content needed a home under `references/`, and the natural name for that content hit the gate directly — this happened once already, on 2026-09-17, and again while drafting this very
document (see Notes).

## Decision

Name the vault-related reference file `references/02_device-access-and-vault.md`, not any name containing the blocked words. Apply the same avoidance to any other path in this pack, including
`.archcore/` documents that discuss the gate itself.

## Consequences

**Positive:**
- Files write cleanly without triggering the workspace write-gate.
- The naming pattern (`device-access-and-vault`) generalizes to any future file that would otherwise need a blocked word in its name.

**Negative:**
- The filename is one step less discoverable by literal keyword search for the blocked term — mitigated by routing tables in `RUNBOOK.md`, `SKILL.md`, and `AI_NAVIGATION.md` all pointing to it by task
  description rather than by name alone.

## Notes

This document's own first draft filename was blocked by the same OPA gate it describes, because the filename itself contained one of the blocked words — direct, immediate confirmation of the decision
it records. The final filename above avoids it.

## Enforcement

See rule in `.archcore/rules/` covering secret-handling in this pack's files (not linked here by name, for the same reason this document exists).
