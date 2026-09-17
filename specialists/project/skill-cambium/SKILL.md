---
name: skill-cambium
description: "Cambium device fleet operations: device families/firmware, local-admin credential vault, cnMaestro estate, site asset-register conventions, device-inventory schema."
metadata:
  short-description: Cambium wireless fleet operational knowledge
---

# Cambium: Device Fleet Operations

## Contents

- [Use When](#use-when)
- [Standing Write-Back Contract (applies no matter which project invoked this skill)](#standing-write-back-contract-applies-no-matter-which-project-invoked-this-skill)
- [What This Pack Covers](#what-this-pack-covers)
- [Related Workspaces](#related-workspaces)
- [Related Skills](#related-skills)
- [References](#references)

## Use When

- Working with any Cambium device: Enterprise Wi-Fi (XV2/E-series), cnPilot R195P, ePMP AP/SM (Force 300 family), cnWave 60 GHz
- Looking up or storing a device's local-admin access (KeePassXC `cambium-devices/` vault)
- Reading, extracting from, or building a site's Cambium asset register
- Populating or querying `device-inventory.csv` or `device-family-matrix.csv` in `cambium-swap`
- Understanding a Cambium model's firmware baseline, EoL/EoS status, or family classification
- Looking up a device's REST API endpoints or SSH CLI commands, e.g. for adapter/integration code
- Deciding whether a fact belongs here (device/hardware layer) or in `skill-smc` (box/Ansible layer)

## Standing Write-Back Contract (applies no matter which project invoked this skill)

This skill is the **shared, cross-project source of truth** for Cambium device-fleet knowledge — not something scoped to whichever project happens to be open. If, while doing Cambium-related work in
**any** project, you discover a new fact, fix, access method, root cause, or behavior change relevant to Cambium hardware, credentials, asset registers, or the device-inventory schema, **write it back
to the appropriate `references/*.md` file in this skill before ending the session** — regardless of whether the calling project's own `AGENTS.md`/`CLAUDE.md` says to. Do not wait for a project-local
governance file to remind you; invoking this skill at all carries that obligation, including the first time a brand-new project ever touches Cambium work.

- Pick the right file with `RUNBOOK.md`'s Reference Routing table (add a row there if a genuinely new domain surfaces — don't force-fit into an existing one).
- Verify the update by **reading the file back** after writing, in the same session. A session-history note, a `SCRATCHPAD.md` claim, or a file timestamp is not proof the content is present — only
  reading the file body counts.
- A project's own `AGENTS.md`/`CLAUDE.md` MAY restate this obligation with project-specific detail — that's reinforcement, not the source of the rule. A project that says nothing about skill-cambium
  at all still carries this obligation the moment it invokes this skill.
- **Boundary with `skill-smc`:** device/hardware/credential/asset-register/cnMaestro knowledge comes here; SMC box, Ansible authoring, and provisioning-role knowledge goes to `skill-smc`. A fact that
  spans both (e.g. a new site's `site_name`, a `smc_cnmaestro_provisioning` behaviour change) gets written to **both** packs in the same session — see each pack's `RUNBOOK.md` Related Workspaces row
  pointing at the other.
- **Never write a device password (or any secret value) into a reference file.** Reference it as `<secret:keepassxc:cambium-devices/<entry>>` — see `references/02_device-access-and-vault.md`.

## What This Pack Covers

APN's Cambium wireless fleet: five device families (Enterprise Wi-Fi, cnPilot R-series, ePMP AP, ePMP SM, cnWave 60 GHz), their local-admin credential vault, the cnMaestro estate, and the
site-maintained Excel asset registers that track deployed hardware before any of it reaches cnMaestro. Seeded 2026-09-17 from `cambium-swap`'s first device-credentialing and device-inventory pass. See
`references/01_overview.md` for the full family/model breakdown.

**This pack does not own the SMC box, ansible-wifi, or the provisioning layer** — that's `skill-smc`. It also does not own `cambium-swap`'s own vendor-continuity/exit-planning business analysis, which
stays project-local.

## Related Workspaces

| Path                                                                   | Relationship                                                                                 |
| ---------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `/Volumes/Data/_ai/_project/project_stuff/apn/cambium-swap`            | Live source of truth for the device-family matrix, device inventory, and cnMaestro estate    |
| `/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-smc` | SMC box / ansible-wifi provisioning layer — the fleet's management plane                     |
| `/Volumes/Data/_ansible/ansible-wifi`                                  | Canonical `site_name` values, per-site inventory                                             |
| `/Volumes/Data/_ansible/local-knowledge-ansible`                       | Local-only SMC/Cambium investigation knowledge — check before assuming a gap is unresearched |

## Related Skills

- **`skill-smc`** — the SMC box and ansible-wifi authoring layer. Call it for: SMC service troubleshooting, Ansible topology/role questions, `smc_cnmaestro_provisioning` behaviour, Teleport access to
  a box. It calls back here for: device credentials, device-family/firmware facts, asset-register conventions. Neither pack duplicates the other's content — cross-reference, don't copy.

## References

- `RUNBOOK.md` — navigation index and reference-routing table.
- `references/01_overview.md` — device families/models, EoL/EoS snapshot, evidence-state discipline.
- `references/02_device-access-and-vault.md` — KeePassXC `cambium-devices/` vault structure, `kp` wrapper gotchas, reference convention.
- `references/03_asset-register-conventions.md` — naming grammar, per-site drift, site-name convention, R195P IP-derivation rule.
- `references/site-addressing.yaml` — machine-readable per-site/family IP addressing trust state and MAC-OUI lookup, companion to 03's narrative.
- `references/04_device-inventory-schema.md` — `device-inventory.csv` column contract, `UNKNOWN` discipline, extraction workflow.
- `references/05_known-issues.md` — coverage gaps, unverified assumptions, staleness risks.
- `references/06_device-api-cli-reference.md` — device REST API / SSH CLI data points per adapter method, config-backup source, write-ops boundary.
