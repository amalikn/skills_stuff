---
title: Separate Pack From skill-smc
type: adr
status: accepted
date: 20260917
provenance: promoted from SCRATCHPAD.md (KEEP, Recent decisions) on 20260917; accepted by operator 20260917
---

# ADR: Separate Pack From skill-smc

## Status

Accepted

## Context

`skill-cambium`'s content — device families/firmware, the local-admin credential vault, the cnMaestro estate, site asset-register conventions, and the `device-inventory.csv` schema — was first
discovered and written down during `cambium-swap`'s device-credentialing and device-inventory extraction session. `skill-smc` already existed as the pack for the SMC box / ansible-wifi provisioning
layer around this same hardware, and one of skill-smc's own numbered reference files already held an early version of the asset-register naming-convention content that later became this pack's
canonical home for that topic.

## Decision

Scaffold `skill-cambium` as its own specialist pack rather than folding this content into `skill-smc`.

Rationale:
- Different domain: hardware/credentials/asset-registers/cnMaestro versus the SMC box/Ansible authoring/provisioning-role layer.
- The content already had real cross-project-reusable volume of its own, not just a few notes.
- This mirrors the precedent that created `skill-smc` in the first place — a pack is split out once its content earns independent reuse rather than staying folded into an adjacent pack.

## Consequences

**Positive:**
- Each pack stays scoped to one domain; an agent working the SMC box does not have to load Cambium hardware/credential content and vice versa.
- The asset-register naming-convention content gained one canonical home (`references/03_asset-register-conventions.md`) instead of living forked across two packs.

**Negative:**
- Two packs must now stay cross-referenced in both directions (`SKILL.md` Related Skills, `RUNBOOK.md`/`AI_NAVIGATION.md` routing) — see the cross-pack boundary rule.
- A fact spanning both domains must be written to both packs in the same session, which is easy to forget.

## Enforcement

See rule: [`.archcore/rules/rule-cambium-smc-cross-pack-boundary.md`](../rules/rule-cambium-smc-cross-pack-boundary.md)
