---
title: Cambium/SMC Cross-Pack Boundary
type: rule
status: accepted
provenance: promoted from AGENTS.md (Working rules) on 20260917; accepted by operator 20260917
---

# Rule: Cambium/SMC Cross-Pack Boundary

Device/hardware/vault/asset-register/cnMaestro knowledge belongs in `skill-cambium`. SMC box, Ansible authoring, and provisioning-role knowledge belongs in `skill-smc`.

A fact spanning both domains (e.g. a `site_name` value, an `smc_cnmaestro_provisioning` behaviour) gets written to both packs' matching reference files in the same session — not deferred to a later
pass, and not left in only one pack on the assumption the other will pick it up.

**Rationale:** this is the enforcement mechanism for [`adr-separate-pack-from-skill-smc.md`](../adr/adr-separate-pack-from-skill-smc.md) — the two packs stay useful as separate, focused packs only if
domain knowledge is routed to the correct one immediately rather than accumulating in whichever pack happened to be open at the time.
