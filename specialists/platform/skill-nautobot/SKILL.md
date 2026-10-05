---
name: skill-nautobot
description: >-
  Design, query and troubleshoot Nautobot: inventory, IPAM and Namespaces, custom fields, computed fields, Relationships, Dynamic Groups, Config Contexts,
  Secrets, REST/GraphQL/pynautobot, Jobs and Job Hooks, webhooks, approvals, change log, Golden Config, staged onboarding, field ownership, permissions and
  upgrades (nautobot-server), app development, SSoT/DiffSync, Ansible and Nornir inventories, backup and restore, metrics and security settings.
  Use for Nautobot work; not as the primary skill for OpenWISP telemetry, graphs or alerts.
---

# Nautobot

## Role and non-goals

Use Nautobot primarily for intended network source-of-truth modelling, inventory, IPAM, relationships, lifecycle workflows, validation, Jobs/apps and integration APIs.
Do not treat telemetry monitoring as its default responsibility, or describe a project worked case as product behaviour.

## Read, write, and evidence boundaries

Read-only investigation may produce observations; it does not authorize an inventory mutation.
Observed discovery does not automatically become intended inventory, and transient health must not silently redefine lifecycle state.
Obtain project-specific authorization before every write, keep the writer identity and idempotence contract explicit, and fail closed on ambiguity.
Keep an observation's source, time, vantage and confidence when it may affect a later decision.
Do not embed client credentials, customer topology, or equipment-specific commands in reusable guidance.

## Orient first

On an unfamiliar deployment, establish the version, the installed apps and whether workers answer before reading anything else; models, API shapes
and Job interfaces change between releases.

```bash
nautobot-server --version; pip list 2>/dev/null | grep -iE 'nautobot|pynautobot|diffsync|nornir'; grep -nE '^PLUGINS' "$NAUTOBOT_CONFIG"
nautobot-server celery inspect ping -t 5; nautobot-server celery inspect active_queues; nautobot-server health_check
```

`scripts/` holds tested, stdlib-only helpers: `nautobot_paging.py` (`listing()` adds a total order; `traverse()` refuses a listing that repeats,
skips or miscounts) and `nautobot_ipam.py` (an address's mask from the narrowest network Prefix).

## Route the task

Choose the primary skill by the object or failure **being changed**: a Nautobot field, Device, Job or intent edge starts here; OpenWISP registration/metric/worker/
health/graph starts in `skill-openwisp`. A synchronization task uses the owner of the requested change as primary and reads the other skill only for its contract.
Observed topology uses the collector/presentation component as primary; accepted topology uses Nautobot. Vendor commands, OIDs, RF interpretation and transport
execution begin with equipment/transport expertise, with this skill supplying only the inventory integration contract. Ordinary single-platform tasks load one pack.

| Task                                                      | Read first                                |
| --------------------------------------------------------- | ----------------------------------------- |
| Exact syntax: REST, GraphQL, groups, fields, hooks, CLI   | [references/operations-cookbook.md](references/operations-cookbook.md) |
| Locations, platforms, interfaces, VLANs, modules, contacts | [references/data-model.md](references/data-model.md) |
| Writing a Nautobot app: models, API, UI, Jobs, tests      | [references/app-development.md](references/app-development.md) |
| pynautobot, SSoT/DiffSync, Git data, Ansible, Nornir, GC  | [references/integrations.md](references/integrations.md) |
| Backup, restore, health, metrics, performance, security   | [references/operations-and-recovery.md](references/operations-and-recovery.md) |
| Ownership, IPAM, relationships, custom data models        | [references/authority-and-modeling.md](references/authority-and-modeling.md) |
| API traversal, deterministic readers, safe writers        | [references/api-and-writers.md](references/api-and-writers.md) |
| Brownfield discovery, identity, staging and approval      | [references/staged-onboarding.md](references/staged-onboarding.md) |
| Replacement, custody, labels and identity continuity      | [references/lifecycle-and-replacement.md](references/lifecycle-and-replacement.md) |
| Discovery sources, conflicts and topology evidence        | [references/discovery-and-topology.md](references/discovery-and-topology.md) |
| Apps, Jobs, validators, workers and permissions           | [references/apps-jobs-validation.md](references/apps-jobs-validation.md) |
| Backup, redaction, compliance, restore and deployment     | [references/config-backup-compliance.md](references/config-backup-compliance.md) |
| Missing capability, providers, NTC and complementary FOSS | [references/capability-extension.md](references/capability-extension.md) |
| Upgrade preflight, extension register and incident triage | [references/upgrade-and-troubleshooting.md](references/upgrade-and-troubleshooting.md) |
| Reusable learning capture and engagement closeout         | [references/evolution-and-write-back.md](references/evolution-and-write-back.md) |

## Verify version-sensitive facts

Before asserting a current endpoint, model field, Job/app interface, or release behaviour, inspect version-matched official documentation and record the source/date in [sources.yaml](sources.yaml).
Use [compatibility.yaml](compatibility.yaml) only for its stated environment and evidence rung; an observed install is not behavioural proof.
Record unknowns as unknown rather than extrapolating a supported version range.

## Search before building

```text
desired operator outcome
  ↓ existing Nautobot core capability
  ↓ installed or maintained product apps/modules and relevant NTC tooling
  ↓ supported extension points of those components
  ↓ compatible external FOSS and its supported seams
  ↓ from-scratch component only when the acceptance test still cannot be met
```

At every downward transition, state why the preceding level cannot meet the acceptance test.
Check current maintenance, license, compatibility, reachability and extension support; do not maintain a static best-tools ranking.
Prefer the narrowest supported seam and cover the behaviour it relies on with a regression test.

## Project and equipment boundary

Keep customer, site and exact device state in its governing project.
Route device commands, OIDs and vendor-specific behaviour to the appropriate equipment expertise rather than copying them here.
For a cross-platform task, load another skill only when the task actually crosses its ownership boundary.

## Project conventions

A project that runs Nautobot may keep a platform-conventions file (its field owners, writer accounts, naming, safety tiers and evidence vocabulary). Check the
engaging project's `AGENTS.md` for it before any write; project rules outrank the generic guidance here. For UNC that file is
`docs/engineering/platform-skills-project-layer-20261005_1349.md` in the unified-network-controller project.

## Standing write-back contract

Invoking this skill obliges you to write back what the engagement taught, in any project, before the session ends: a dated Learned entry in the focused reference
plus one CHANGELOG line under `## Unreleased`, read back after writing. Classify every engagement in one sentence (no new learning, verified update, candidate,
contradiction, project-only, equipment-only). Skill use never authorizes editing a live system, and editing this source only when the task permits it; otherwise
leave the entry in the engaging project. Format, classes and release reconciliation:
[references/evolution-and-write-back.md](references/evolution-and-write-back.md).
