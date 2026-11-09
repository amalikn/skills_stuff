---
Title: AI Navigation — skill-proxmox
Category: navigation
Status: current
Authority: local-supplement
Scope: Root AI_NAVIGATION.md of skill-proxmox
Last reviewed: 2026-11-07
Summary: This file is a router, not the full knowledge store.
Review by: 2026-12-09
Budget: 150 lines, 12 KB
---

# AI Navigation — skill-proxmox

Purpose: this file is the project context entrypoint for AI agents. It tells agents where project truth lives, what to read first, what is authoritative, what is temporary, and what must be updated
after work.

This file is a router, not the full knowledge store.

<!-- This Contents block sits OUTSIDE the managed markers on purpose: it indexes the whole file,
     including any project-authored sections below the END marker, and the upgrader regenerates
     everything between the markers. Keep it updated when sections are added either side. -->

## Contents

- [Mandatory read order](#mandatory-read-order)
- [Source priority](#source-priority)
- [Project context files](#project-context-files)
- [Task routing](#task-routing)
  - [Architecture/design questions](#architecturedesign-questions)
  - [Planning/status questions](#planningstatus-questions)
  - [Agent/governance questions](#agentgovernance-questions)
  - [Implementation/code questions](#implementationcode-questions)
- [Script and Task Navigation](#script-and-task-navigation)
  - [Documentation updates](#documentation-updates)
- [Governance coherence checks](#governance-coherence-checks)
- [Companion consistency](#companion-consistency)
- [Drift handling](#drift-handling)
- [Update rules](#update-rules)
- [Generated context](#generated-context)
- [Context compaction recovery](#context-compaction-recovery)
- [Audit procedure](#audit-procedure)
- [Agent answer contract](#agent-answer-contract)
- [Pack domain routing](#pack-domain-routing)
- [Pack artifacts](#pack-artifacts)

<!-- BEGIN MANAGED: skill-ai-it:navigation -->
<!-- skill-ai-it-version: 2026-10-14-compact-v2 -->

## Mandatory read order

`AGENTS.md`, then this file, then `context-map.yaml`, then the newest `CHANGELOG.md` entries, then relevant `.archcore/` and `memory-bank/` files if present, then the docs and code the task needs.
Triage before opening: `just docs <folder>` (one header line per file); `just stale` lists stale docs.

## Source priority

`.archcore/` accepted documents, then `AGENTS.md` / `CLAUDE.md`, this file, `context-map.yaml`, `CHANGELOG.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `memory-bank/`, `SCRATCHPAD.md`, then drafts and
archives. `SCRATCHPAD.md` is transient unless marked `KEEP` or promoted.

## Project context files

High: `AGENTS.md`, `CLAUDE.md`, this file, `context-map.yaml`; highest when present: `.archcore/`. Medium-high: `CHANGELOG.md`, `ARCHITECTURE.md`, `ROADMAP.md`. Medium: `memory-bank/`. Low:
`SCRATCHPAD.md`. On need only: `docs/history/` (rotated records, `just history <term>`) and `docs/trackers/` (open items). Generated, never truth: `.ai-context/`. Full table:
[reference](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/navigation/read-order-and-sources.md#project-context-files).

## Task routing

| Question               | Read first                                                                                               |
| ---------------------- | -------------------------------------------------------------------------------------------------------- |
| Architecture or design | `.archcore/adr/`, `.archcore/specs/`, `ARCHITECTURE.md`, `docs/`; never answer from the scratchpad alone |
| Planning or status     | `.archcore/plans/`, `ROADMAP.md`, `CHANGELOG.md`, `memory-bank/`; say so when they disagree              |
| Agents or governance   | `AGENTS.md`, `CLAUDE.md`, this file, `context-map.yaml`, `.archcore/rules/`                              |
| Implementation or code | `AGENTS.md`, `context-map.yaml`, `.archcore/specs/`, the source and its tests                            |
| Documentation          | `.archcore/`, `README.md`, `CHANGELOG.md`, `docs/`; leave companions consistent                          |

## Script and Task Navigation

`just --list` first, then `scripts/README.md`, then any other runner. Never run an uncatalogued script, or one marked `destructive`, `review-required` or `unknown`, without review; propose a catalogue
update when it is stale.

## Governance coherence checks

Run `just check` (or `scripts/check_governance.py`) before calling a durable change done and after adding, moving or retiring a file. When it fails, fix the project, not the check; a new artifact
class, generated output or restated constant extends the checker's registries in the same pass.

## Companion consistency

`AGENTS.md` goes with this file, `context-map.yaml` and `scripts/README.md`; a new script goes with `scripts/README.md`, `justfile` and the checker. `context-map.yaml` `update_rules` is authoritative
for this project.

## Drift handling

When files disagree: stop, name them, say which has higher authority, propose the smallest correction. Never merge conflicting assumptions silently.

## Update rules

Decision: `.archcore/adr/`. Rule: `.archcore/rules/` or `AGENTS.md`. Routing: this file and `context-map.yaml`. Any governance or navigation change: `CHANGELOG.md`. Records over budget: `just budget
--apply`. Full table: [reference](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/navigation/change-rules.md#update-rules).

## Generated context

`.ai-context/` packs help navigation and are never a source of truth; regenerate after large changes with `repomix --config repomix.config.json`.

## Context compaction recovery

Re-read this file, `.archcore/` and the newest `CHANGELOG.md` entries; check `SCRATCHPAD.md` against the memory backends; confirm companions agree. Steps:
[reference](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/navigation/recovery-and-audit.md#context-compaction-recovery).

## Audit procedure

`just check` and `just stale` cover the mechanical part; the ten manual checks are in the
[reference](/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/patterns/navigation/recovery-and-audit.md#audit-procedure).

## Agent answer contract

Cite file paths; never invent project state; say "not found in project context" when unsupported; separate confirmed facts from assumptions; ask only when required, otherwise proceed with stated
assumptions.

<!-- END MANAGED: skill-ai-it:navigation -->

## Pack domain routing

Project-authored (outside the managed block); mirrors [SKILL.md](SKILL.md). The checker fails when a reference is missing from either.
Ordinary tasks load one reference. What runs inside a guest belongs to that workload's skill; the inventory of record belongs to the source-of-truth skill
(for example [skill-nautobot](../skill-nautobot/SKILL.md)).

| Task | Read first |
|---|---|
| Exact syntax: pvesh, pveum, qm, pct, pvesm, API paths | [references/operations-cookbook.md](references/operations-cookbook.md) |
| Nodes, clusters, Corosync, quorum, pmxcfs, node removal, arm64 | [references/architecture-and-cluster.md](references/architecture-and-cluster.md) |
| Storage types, content types, import, hyperconverged Ceph | [references/storage.md](references/storage.md) |
| Bridges, VLAN-aware bridges, SDN zones, VNets, DHCP and IPAM | [references/networking-and-sdn.md](references/networking-and-sdn.md) |
| VMs: q35, OVMF, boot order, cloud-init, agent, serial, clones, migration, mappings | [references/qemu-vms.md](references/qemu-vms.md) |
| LXC containers, privileged and unprivileged, templates | [references/lxc-containers.md](references/lxc-containers.md) |
| Users, realms, roles, privileges, ACLs, pools, API tokens, 2FA | [references/access-control.md](references/access-control.md) |
| REST API, authentication, tasks, safe readers and writers | [references/api-and-cli.md](references/api-and-cli.md) |
| OpenTofu with bpg/proxmox: auth, ssh block, import, state | [references/opentofu-bpg-provider.md](references/opentofu-bpg-provider.md) |
| vzdump, PBS 4.x (S3), retention and restore | [references/backup-and-restore.md](references/backup-and-restore.md) |
| HA, placement rules, fencing, storage replication | [references/ha-and-replication.md](references/ha-and-replication.md) |
| Repositories, updates, 8-to-9 upgrade, 9.x changes, triage | [references/upgrade-and-troubleshooting.md](references/upgrade-and-troubleshooting.md) |
| Certificates, ACME, firewall, hardening | [references/security-certificates-firewall.md](references/security-certificates-firewall.md) |
| Health reads, metrics, notifications, node report | [references/monitoring-and-metrics.md](references/monitoring-and-metrics.md) |
| Missing capability: native, Proxmox products, seams, FOSS | [references/capability-extension.md](references/capability-extension.md) |
| Reusable learning capture and engagement closeout | [references/evolution-and-write-back.md](references/evolution-and-write-back.md) |

## Pack artifacts

| Artifact | Role | Enforced by |
|---|---|---|
| [SKILL.md](SKILL.md) | Activation surface: role, boundaries, orient-first commands, routing, write-back contract | `tests/test_package_contract.py` |
| `references/` | Content source, one focused file per domain; each carries dated Learned entries | Contract test + `scripts/check_governance.py` |
| [sources.yaml](sources.yaml) | Claim ledger (P-Cnn): statement, evidence rung, source type, reference, scenario | Contract test schema |
| [compatibility.yaml](compatibility.yaml) | Environment ledger: product version, validation layer, result | Contract test schema |
| [documents/readme.md](documents/readme.md) | Index of the verbatim source captures with sha256 | Contract test (both directions + hash) |
| [tests/scenarios.md](tests/scenarios.md) | Evaluation scenarios (P-Snn) each claim links to | Contract test |
| [tests/eval-procedure.md](tests/eval-procedure.md) | How to run a with/without-skill evaluation | — |
| [scripts/README.md](scripts/README.md) | Helper and recipe catalog | `scripts/check_governance.py` |
| [CHANGELOG.md](CHANGELOG.md) | Release history; `## Unreleased` collects write-back lines | Contract test |
| [.archcore/index.guide.md](.archcore/index.guide.md) | Index of durable ADRs, rules and plans, and what is never promoted | `scripts/check_governance.py` (both directions) |
