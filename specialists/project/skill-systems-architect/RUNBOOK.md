---
Title: Systems Architect runbook
Category: navigation-index
Status: current
Authority: authored-guidance
Scope: skill-systems-architect task routing, templates and recipes
Last reviewed: 2026-10-29
Summary: Routes a task to the one reference, template or helper it needs. Load only what the task needs.
---

# Systems Architect runbook

Navigation index for `skill-systems-architect`. Do not write domain content here; write it to the matching reference.

## Reference Routing

Reference routing lives in [SKILL.md](SKILL.md#domain-routing), one hop from the entry point.

## Templates

Ordered by when they are used. Shared forms are canonical in skill-network-architect.

| Phase | Template | Use it for | Home |
| --- | --- | --- | --- |
| Discover | [current-state-discovery](templates/current-state-discovery.md) | what exists now, evidence coverage, intent-versus-observation drift | shared |
| Require | [requirements-and-constraints](templates/requirements-and-constraints.md) | measurable per-service targets with owner, window, method and evidence label | shared |
| Design | [design](templates/design.md) | the design document: outcome, views, failure model, waves, sign-off | shared |
| Design | [interface-contract](templates/interface-contract.md) | one interface between domains: flows, budgets, failure behaviour, field ownership | shared |
| Design | [capacity-model](templates/capacity-model.md) | demand, supply and headroom under normal, maintenance and failure | shared |
| Design | [failure-mode-analysis](templates/failure-mode-analysis.md) | FMEA per component, shared-risk groups, correlated failures | shared |
| Design | [host-and-cluster-build](templates/host-and-cluster-build.md) | host or cluster build sheet: sizing, quorum (`just quorum`), storage (`just ceph`), bonds, backup | this pack |
| Decide | [decision-record](templates/decision-record.md) | one decision (MADR 4.0), confirmation and reopen triggers | shared |
| Decide | [risk-register](templates/risk-register.md) | scored risks with trigger, response, owner and residual | shared |
| Hand off | [handoff](templates/handoff.md) | request and response envelope between architects and specialists | shared |
| Change | [change-and-validation](templates/change-and-validation.md) | Method of Procedure: pre-checks, steps with rollback, gates, canary, batches | shared |
| Accept | [test-and-acceptance-plan](templates/test-and-acceptance-plan.md) | tests traced to requirements, oracle, failure injection, sign-off | shared |
| Accept | [backup-and-restore-test](templates/backup-and-restore-test.md) | RPO/RTO per dataset, 3-2-1 placement, restore drill vs target (`just capacity`) | this pack |
| Operate | [post-incident-review](templates/post-incident-review.md) | blameless review: timeline, contributing factors, owned actions | shared |
| Operate | [lifecycle-and-patching](templates/lifecycle-and-patching.md) | EOL tracking, patch rings, windows, emergency path | this pack |

## Helpers

| Need | Recipe |
| --- | --- |
| Does memory survive each failure scenario; does restore meet RTO? | `just capacity <plan.json>` |
| What availability does this series/parallel design give? | `just availability <model.json>` |
| Are the cited links still alive? (network, read-only) | `just links` |
| Refresh local copies of cited sources (plan, then `--apply`) | `just fetch-sources` |
| Rebuild the source ledger after adding citations (plan, then `--apply`) | `just ledger` |

Inputs, formulas and limits: [scripts/README.md](scripts/README.md). Examples: `examples/`.

## Maintenance

`just bootstrap` once, `just check` before claiming any change complete. Write-back rules: [SKILL.md](SKILL.md#standing-write-back-contract).
