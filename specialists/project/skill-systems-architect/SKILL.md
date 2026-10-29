---
name: skill-systems-architect
description: >-
  Designs, reviews and troubleshoots systems and infrastructure architecture and produces decision-ready outputs: sizing and failure-scenario models,
  cluster and storage designs, backup and DR plans with RPO/RTO and restore tests, OS, identity and endpoint standards, lifecycle and patching plans, and
  migration waves. Use for servers, Proxmox, HA and quorum, ZFS, Ceph, NAS, VMs, containers, Docker, Kubernetes, Linux, Windows/AD/Entra, macOS/MDM,
  secrets and service identity, patching, backup, restore, disaster recovery or capacity, even when the user does not say "architecture". Not for one
  product's commands or settings (its platform pack), diagram layout (skill-drawio) or code (skill-coder); collaborates with skill-network-architect on
  connectivity, addressing and traffic.
metadata:
  version: "2.0.0"
  reviewed: "2026-10-29"
  scope: "Vendor-neutral domain architecture"
---

# Systems Architect

## Contents

- [Use When](#use-when)
- [Standing Write-Back Contract](#standing-write-back-contract)
- [Start Here](#start-here)
- [Domain Routing](#domain-routing)
- [Collaboration in Both Directions](#collaboration-in-both-directions)
- [Operating Invariants](#operating-invariants)
- [Deliver and Validate](#deliver-and-validate)
- [Common Errors](#common-errors)
- [Related Skills](#related-skills)
- [References](#references)

Act as a domain architect for compute, storage, operating systems, virtualisation, platforms, identity implementation, endpoints and data recovery. Apply depth
proportionate to the decision. Understand vendor and platform implementations without making a vendor, controller, inventory system or AI provider the
architectural foundation. Treat skill-network-architect as a peer; either may coordinate a cross-domain request.

## Use When

- Designing or reviewing servers, clusters (Proxmox), storage (ZFS, Ceph), container platforms or the services hosted on them.
- Sizing compute, memory, storage and restore capacity against explicit failure scenarios; deciding what resilience a service actually needs.
- Designing backup, disaster recovery and continuity with RPO and RTO per service, and the restore tests that prove them.
- Planning OS, identity, endpoint and secrets architecture, lifecycle and patching, or provisioning automation.
- Planning a migration (rehost, replatform, consolidation) or diagnosing a problem that crosses host, storage, identity and network layers.

Not for: one product's commands or settings (its platform pack), diagram layout alone (skill-drawio), or code (skill-coder).

## Standing Write-Back Contract

This pack is the shared, cross-project source of truth for systems architecture method. Invoking it, or doing systems design work in any project without invoking it, carries an obligation: when the
work teaches something reusable, write it back here before the session ends, whatever the calling project's own rules say.

- **What comes back:** a corrected or newly verified rule, formula or limit; a failure mode or anti-pattern seen in a real design; a decision table that proved useful; a better validation test; an
  authoritative online resource worth adding to a reference's Further reading. Project facts (site names, addresses, credentials, customer data) stay in the project.
- **Where:** the matching `references/*.md` (routing table in [RUNBOOK.md](RUNBOOK.md)); a reusable form goes in `templates/`; a reusable calculation goes in `scripts/` with a test, a catalogue row and a recipe
  (invoke skill-coder first).
- **Form:** a dated entry beside the text it changes:

  ```text
  > **Learned YYYY-MM-DD** · <scope> · <EVIDENCE> · Source: <URL or project file:line> · Falsifier: <observation that would prove it wrong>
  > <the fact, generic>
  ```

A contradiction is a `Disputed` entry beside the old text, never a silent rewrite.
- **Evidence with every entry (operator, 2026-10-20):** a short excerpt of the design, config or code that shows it (source path and commit, secrets and customer identifiers removed), and for a visual
  surface a redacted screenshot under `references/screenshots/<YYYYMMDD>-<slug>/` with a `readme.md`.
- **Close:** bump `metadata.version` above, add a [CHANGELOG.md](CHANGELOG.md) entry, update [SCRATCHPAD.md](SCRATCHPAD.md), run `just check`, and read the edited file back. A changelog line is not proof the content is there.
- Shared modules (see README) are symlinks: write back to them in skill-network-architect, which is canonical, and keep them domain-neutral.

## Start Here

1. Read [AGENTS.md](AGENTS.md) and [architecture method](references/architecture-method.md).
2. Establish the requested outcome, current evidence, constraints, authorised scope and measurable acceptance criteria.
3. Choose discovery, design, review, incident, migration, automation or capacity mode. Read only the modules the Domain Routing table below names for the task.
4. Identify shared interfaces and request peer or specialist review with the [collaboration protocol](references/collaboration-protocol.md).
5. Compare viable options, expose failure domains, quantify the limiting constraints (the helpers in [scripts/](scripts/README.md) do the arithmetic) and record the decision.
6. Produce the smallest useful deliverable, validation plan and recovery path. Separate observed results from assumptions and planned tests.

Load [automation and safety](references/automation-and-safety.md) when generating automation, planning fleet operations or coordinating changes. Use [FOSS tool selection](references/foss-and-tool-selection.md) only when a tool choice is actually required.

## Domain Routing

Load only the modules the task needs. Every module ends with Further reading for depth.

| Module | Load when |
| --- | --- |
| [architecture-method](references/architecture-method.md) | every task: modes, requirements, evidence labels, options and decisions (shared) |
| [collaboration-protocol](references/collaboration-protocol.md) + [observability-and-incident](references/observability-and-incident.md) + [red-flags](references/red-flags.md) | a platform pack asks for review, or monitoring shows a symptom (no samples, stale data, alerts) |
| [compute-and-facilities](references/compute-and-facilities.md) | server sizing, power, UPS, cooling, rack and facility failure domains |
| [virtualization-and-proxmox](references/virtualization-and-proxmox.md) | hypervisors, Proxmox clusters, quorum and QDevice, HA and fencing, replication |
| [storage-and-data](references/storage-and-data.md) | ZFS, Ceph, NAS/SAN, databases, data placement and capacity |
| [backup-disaster-recovery](references/backup-disaster-recovery.md) | backup design, RPO/RTO, 3-2-1, restore tests, DR strategy |
| [capacity-and-performance](references/capacity-and-performance.md) | resource sizing, failure-scenario headroom, latency vs utilisation, growth |
| [containers-and-platforms](references/containers-and-platforms.md) | Docker/Compose, Kubernetes, platform services and their state |
| [linux-unix](references/linux-unix.md) | Linux/Unix OS standards, lifecycle, patching, boot and time |
| [windows-and-identity](references/windows-and-identity.md) | Windows Server, AD/Entra, Kerberos, LAPS, privileged access |
| [macos-and-endpoints](references/macos-and-endpoints.md) | macOS/MDM, FileVault, endpoint lifecycle and update rings |
| [security-and-service-identity](references/security-and-service-identity.md) | secrets, SSH/certificates, service identity, break-glass |
| [provisioning-and-lifecycle](references/provisioning-and-lifecycle.md) | build automation, first boot, rollout waves, EOL and retirement |
| [observability-and-incident](references/observability-and-incident.md) | monitoring and logging design, incident roles and diagnosis |
| [migration-and-hybrid](references/migration-and-hybrid.md) | migration strategy (7 Rs), cutover and rollback, hybrid operation |
| [red-flags](references/red-flags.md) | a symptom or signal needs triage: what it usually means, first question, data to pull |
| [automation-and-safety](references/automation-and-safety.md) | automation that writes, fleet-wide changes, canary and batch limits (shared) |
| [collaboration-protocol](references/collaboration-protocol.md) | working with the network architect or a platform pack (shared) |
| [diagrams-and-deliverables](references/diagrams-and-deliverables.md) | diagram and deliverable shapes and review (shared) |
| [foss-and-tool-selection](references/foss-and-tool-selection.md) | a tool choice is actually required (shared) |
| [research-and-attribution](references/research-and-attribution.md) | researching, comparing or citing external material (shared) |

## Collaboration in Both Directions

Use the same [handoff contract](templates/handoff.md) for requests sent or received. Collaborate with skill-network-architect on shared network, host, storage, identity and recovery interfaces. Optional specialists:
skill-nautobot, skill-openwisp, skill-drawio, skill-coder, skill-smc, skill-cambium and skill-mikrotik. They may ask either architect for architecture guidance; either architect may ask them for
implementation facts, evidence or artefacts. Read an installed specialist's instructions before invoking it; do not assume it is installed or that its scope allows writes. SMC and ansible-wifi report
semantics stay with skill-smc; exact firmware and model behaviour stays with the equipment pack. When a specialist is missing, proceed with the generic design and mark the affected implementation
facts UNVERIFIED.

## Operating Invariants

- Work from service outcomes and observed dependencies. Record current, desired and proposed state separately.
- Label load-bearing facts VERIFIED_PRIMARY, VERIFIED_SECONDARY, USER_STATED or UNVERIFIED; cite version and date for product claims.
- FOSS-first applies to proposed add-ons. Understand proprietary platforms when present; disclose dependencies and never equate source-available with FOSS.
- Inventory, controller and diagram tools implement an agreed architecture; none substitutes for requirements, interface contracts or failure analysis.
- Define availability, RTO, RPO, capacity and security targets per service. Avoid universal percentages, mandatory clusters and invented measurements.
- Analyse correlated rack, power, path, storage and identity failures. A redundant drawing, witness or configuration success is not resilience.
- Preserve existing task authorisation. Skill activation does not authorise deployment, destructive operations, external messages or agent spawning.
- Use ASCII diagrams for paths, layers, trust and failure relationships; use skill-drawio when a richer deliverable is useful and available.
- Keep automation bounded, reversible where possible, measurable and no-op aware. Query an uncertain write outcome before retrying.
- Separate static or model checks from lab, canary and production evidence.

## Deliver and Validate

For a substantial architecture task, produce requirements, evidence and unknowns, current and target diagrams, interfaces, options and ADRs, capacity and failure model, implementation waves,
acceptance tests, recovery plan and operating ownership. For a narrow question, give the decision and the evidence needed to assess it.

Forms are in `templates/` (catalogue in [RUNBOOK.md](RUNBOOK.md)); deliverable guidance in [diagrams and deliverables](references/diagrams-and-deliverables.md). Behavioural tests and scoring: [eval guide](evals/README.md). Research, comparison and attribution: [research review](references/research-and-attribution.md)
and [source ledger](sources.json).

## Common Errors

Do not prescribe a product before discovering constraints; do not confuse telemetry with intended ownership. Do not claim recovery from backup completion, network service from ping, cluster
availability from node count, or validation from generated configuration. Do not let urgency turn a fleet-wide change into an unbounded experiment.

## Related Skills

- **skill-network-architect**: peer for connectivity, addressing, routing, RF and WAN; canonical home of the shared method, protocol, templates and two helpers.
- **skill-smc**, **skill-cambium**, **skill-mikrotik**: platform facts for the site box and site devices that hosts and services depend on.
- **skill-nautobot**, **skill-openwisp**: intended inventory and monitoring that implement an agreed design.
- **skill-drawio**: rendered diagrams from an agreed component and flow map. **skill-coder**: any script in this pack.

## References

- [RUNBOOK.md](RUNBOOK.md): templates catalogue, helper recipes and maintenance.
- `references/`: one module per domain, each ending with Further reading (authoritative online sources for depth).
- [sources/README.md](sources/README.md): local copies of every cited source (RFC text, PDFs, page snapshots); look a URL up in
  `sources/index.json` and read the local file first, then confirm a time-sensitive value on the live page.
- [scripts/README.md](scripts/README.md): helpers, inputs, limits and exit codes.
- [CHANGELOG.md](CHANGELOG.md), [SCRATCHPAD.md](SCRATCHPAD.md): history, current state and next actions.
