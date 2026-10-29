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
  version: "2.2.0"
  reviewed: "2026-10-29"
  scope: "Vendor-neutral domain architecture"
---

# Systems Architect

## Contents

- [Use When](#use-when)
- [Standing Write-Back Contract](#standing-write-back-contract)
- [Start Here](#start-here)
- [Domain Routing](#domain-routing)
- [Operator Context (APN)](#operator-context-apn)
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

Load only the modules the task needs; for a narrow question load the named section, not the whole file. Every module opens with Scope and
Decision rules and ends with Further reading for depth.

| Module | Load when | Topical sections (load one when the task is narrow) |
| --- | --- | --- |
| [architecture-method](references/architecture-method.md) | every task: modes, requirements, evidence labels, options and decisions (shared) | [Evidence labels and layers](references/architecture-method.md#evidence-labels-and-layers), [Engagement modes](references/architecture-method.md#engagement-modes), [End-to-end flow](references/architecture-method.md#end-to-end-flow), [Quantitative rules](references/architecture-method.md#quantitative-rules) |
| [collaboration-protocol](references/collaboration-protocol.md) + [observability-and-incident](references/observability-and-incident.md) + [red-flags](references/red-flags.md) | a platform pack asks for review, or monitoring shows a symptom (no samples, stale data, alerts) | - |
| [compute-and-facilities](references/compute-and-facilities.md) | server sizing, power, UPS, cooling, rack and facility failure domains | [Memory reserve and N+k arithmetic](references/compute-and-facilities.md#memory-reserve-and-nk-arithmetic), [Power, UPS and thermal arithmetic](references/compute-and-facilities.md#power-ups-and-thermal-arithmetic) |
| [edge-appliances](references/edge-appliances.md) | Linux site boxes: read-only A/B images, pull-based updates, flash wear, watchdogs, telemetry spools, power | [Image layout and updates](references/edge-appliances.md#image-layout-and-updates), [Pull-based jobs over poor links](references/edge-appliances.md#pull-based-jobs-over-poor-links), [Flash wear and RAM placement](references/edge-appliances.md#flash-wear-and-ram-placement), [Measuring writes honestly](references/edge-appliances.md#measuring-writes-honestly) |
| [fleet-management](references/fleet-management.md) | fleet source of truth, field ownership, identity, collectors and spools, vendor exit by lifecycle event | [Source of truth and field ownership](references/fleet-management.md#source-of-truth-and-field-ownership), [Telemetry collectors and spools](references/fleet-management.md#telemetry-collectors-and-spools), [Vendor dependency and controller recovery](references/fleet-management.md#vendor-dependency-and-controller-recovery), [Lifecycle and recovery](references/fleet-management.md#lifecycle-and-recovery) |
| [service-provider-systems](references/service-provider-systems.md) | ISP OSS/BSS: service identifiers, ordering and assurance flows, usage and billing pipelines, reconciliation | [Identifiers and join keys](references/service-provider-systems.md#identifiers-and-join-keys), [Billing timing and the service-month grain](references/service-provider-systems.md#billing-timing-and-the-service-month-grain), [Reconciliation pipeline](references/service-provider-systems.md#reconciliation-pipeline), [Catalogue, cost allocation and voice](references/service-provider-systems.md#catalogue-cost-allocation-and-voice) |
| [virtualization-and-proxmox](references/virtualization-and-proxmox.md) | hypervisors, Proxmox clusters, quorum and QDevice, HA and fencing, replication | [Quorum arithmetic and QDevice](references/virtualization-and-proxmox.md#quorum-arithmetic-and-qdevice), [HA, fencing and replication timing](references/virtualization-and-proxmox.md#ha-fencing-and-replication-timing), [Topology decision table](references/virtualization-and-proxmox.md#topology-decision-table) |
| [storage-and-data](references/storage-and-data.md) | ZFS, Ceph, NAS/SAN, databases, data placement and capacity | [Capacity vocabulary and layouts](references/storage-and-data.md#capacity-vocabulary-and-layouts), [ZFS rules](references/storage-and-data.md#zfs-rules), [Ceph rules](references/storage-and-data.md#ceph-rules), [Two sites: stretch or replicate](references/storage-and-data.md#two-sites-stretch-or-replicate) |
| [backup-disaster-recovery](references/backup-disaster-recovery.md) | backup design, RPO/RTO, 3-2-1, restore tests, DR strategy | [DR strategy ladder](references/backup-disaster-recovery.md#dr-strategy-ladder), [Copy placement and isolation](references/backup-disaster-recovery.md#copy-placement-and-isolation), [Recovery budget arithmetic](references/backup-disaster-recovery.md#recovery-budget-arithmetic), [Implementation notes: PostgreSQL and PBS](references/backup-disaster-recovery.md#implementation-notes-postgresql-and-pbs) |
| [databases-and-ha](references/databases-and-ha.md) | PostgreSQL replication, Patroni failover, PITR and backup tools, MySQL/Galera, SQLite at the edge | [Replication and commit levels](references/databases-and-ha.md#replication-and-commit-levels), [Patroni, DCS and fencing](references/databases-and-ha.md#patroni-dcs-and-fencing), [Backup, PITR and replication types](references/databases-and-ha.md#backup-pitr-and-replication-types), [Connection routing and upgrades](references/databases-and-ha.md#connection-routing-and-upgrades) |
| [ai-inference-platforms](references/ai-inference-platforms.md) | self-hosted LLM sizing: weights, KV cache, concurrency, tokens/s, GPU vs Apple silicon | [Memory: weights and KV cache](references/ai-inference-platforms.md#memory-weights-and-kv-cache), [Speed: prefill, decode and batching](references/ai-inference-platforms.md#speed-prefill-decode-and-batching), [Serving engines and hardware](references/ai-inference-platforms.md#serving-engines-and-hardware), [Queueing for N users](references/ai-inference-platforms.md#queueing-for-n-users) |
| [capacity-and-performance](references/capacity-and-performance.md) | resource sizing, failure-scenario headroom, latency vs utilisation, growth | [Core formulas](references/capacity-and-performance.md#core-formulas), [Failure-scenario arithmetic](references/capacity-and-performance.md#failure-scenario-arithmetic), [Queueing and saturation](references/capacity-and-performance.md#queueing-and-saturation) |
| [containers-and-platforms](references/containers-and-platforms.md) | Docker/Compose, Kubernetes, platform services and their state | [Platform layers and failure domains](references/containers-and-platforms.md#platform-layers-and-failure-domains), [Single-host compose stacks](references/containers-and-platforms.md#single-host-compose-stacks), [Kubernetes essentials](references/containers-and-platforms.md#kubernetes-essentials) |
| [linux-unix](references/linux-unix.md) | Linux/Unix OS standards, lifecycle, patching, boot and time | [Lifecycle and EOL dates](references/linux-unix.md#lifecycle-and-eol-dates), [Patch rings](references/linux-unix.md#patch-rings), [Boot, trust and recovery chain](references/linux-unix.md#boot-trust-and-recovery-chain), [Time, logging, hardening and performance](references/linux-unix.md#time-logging-hardening-and-performance) |
| [windows-and-identity](references/windows-and-identity.md) | Windows Server, AD/Entra, Kerberos, LAPS, privileged access | [Lifecycle dates](references/windows-and-identity.md#lifecycle-dates), [Identity topology](references/windows-and-identity.md#identity-topology), [Login path, time and bootstrap](references/windows-and-identity.md#login-path-time-and-bootstrap), [Privileged access, break-glass and recovery](references/windows-and-identity.md#privileged-access-break-glass-and-recovery) |
| [macos-and-endpoints](references/macos-and-endpoints.md) | macOS/MDM, FileVault, endpoint lifecycle and update rings | [Lifecycle and enrollment](references/macos-and-endpoints.md#lifecycle-and-enrollment), [Recovery custody](references/macos-and-endpoints.md#recovery-custody), [Updates and identity](references/macos-and-endpoints.md#updates-and-identity), [Developer, admin and FOSS boundaries](references/macos-and-endpoints.md#developer-admin-and-foss-boundaries) |
| [security-and-service-identity](references/security-and-service-identity.md) | secrets, SSH/certificates, service identity, break-glass | [Trust-boundary pass](references/security-and-service-identity.md#trust-boundary-pass), [Identity trust chain](references/security-and-service-identity.md#identity-trust-chain), [Human and workload access](references/security-and-service-identity.md#human-and-workload-access), [Secrets and break-glass](references/security-and-service-identity.md#secrets-and-break-glass) |
| [provisioning-and-lifecycle](references/provisioning-and-lifecycle.md) | build automation, first boot, rollout waves, EOL and retirement | [Lifecycle states](references/provisioning-and-lifecycle.md#lifecycle-states), [Supply and configuration chain](references/provisioning-and-lifecycle.md#supply-and-configuration-chain), [Rollout waves](references/provisioning-and-lifecycle.md#rollout-waves), [EOL register and retirement](references/provisioning-and-lifecycle.md#eol-register-and-retirement) |
| [observability-and-incident](references/observability-and-incident.md) | monitoring and logging design, incident roles and diagnosis | [Signals and pipeline](references/observability-and-incident.md#signals-and-pipeline), [Incident roles and timeline](references/observability-and-incident.md#incident-roles-and-timeline), [Incident result shape](references/observability-and-incident.md#incident-result-shape), [What each probe does not prove](references/observability-and-incident.md#what-each-probe-does-not-prove) |
| [migration-and-hybrid](references/migration-and-hybrid.md) | migration strategy (7 Rs), cutover and rollback, hybrid operation | [Strategy selection](references/migration-and-hybrid.md#strategy-selection), [Measure before choosing a platform](references/migration-and-hybrid.md#measure-before-choosing-a-platform), [Discovery and waves](references/migration-and-hybrid.md#discovery-and-waves), [Cutover criteria and data authority](references/migration-and-hybrid.md#cutover-criteria-and-data-authority) |
| [red-flags](references/red-flags.md) | a symptom or signal needs triage: what it usually means, first question, data to pull | [Cluster and virtualisation](references/red-flags.md#cluster-and-virtualisation), [Storage](references/red-flags.md#storage), [Backup and recovery](references/red-flags.md#backup-and-recovery), [Compute and facilities](references/red-flags.md#compute-and-facilities) |
| [automation-and-safety](references/automation-and-safety.md) | automation that writes, fleet-wide changes, canary and batch limits (shared) | [Validation tiers](references/automation-and-safety.md#validation-tiers) |
| [collaboration-protocol](references/collaboration-protocol.md) | working with the network architect or a platform pack (shared) | [Roles and ownership](references/collaboration-protocol.md#roles-and-ownership), [Review states](references/collaboration-protocol.md#review-states) |
| [diagrams-and-deliverables](references/diagrams-and-deliverables.md) | diagram and deliverable shapes and review (shared) | [ASCII diagram conventions](references/diagrams-and-deliverables.md#ascii-diagram-conventions), [Diagram review checklist](references/diagrams-and-deliverables.md#diagram-review-checklist), [Architecture pack](references/diagrams-and-deliverables.md#architecture-pack), [Drawio handoff](references/diagrams-and-deliverables.md#drawio-handoff) |
| [foss-and-tool-selection](references/foss-and-tool-selection.md) | a tool choice is actually required (shared) | [Licence observations](references/foss-and-tool-selection.md#licence-observations) |
| [research-and-attribution](references/research-and-attribution.md) | researching, comparing or citing external material (shared) | [Sources evaluated](references/research-and-attribution.md#sources-evaluated), [Conventions verified](references/research-and-attribution.md#conventions-verified), [Limits and explicit negatives](references/research-and-attribution.md#limits-and-explicit-negatives) |

## Operator Context (APN)

When the work concerns the APN estate, read `../skill-network-architect/operator/apn/README.md` (shared with the network pack, not copied):
estate overview, topic files for OSS/BSS and fleet data and for site boxes and platforms, and the source projects.

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
