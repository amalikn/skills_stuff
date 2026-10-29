---
Title: Network Architect runbook
Category: navigation-index
Status: current
Authority: authored-guidance
Scope: skill-network-architect task routing, templates and recipes
Last reviewed: 2026-10-29
Summary: Routes a task to the one reference, template or helper it needs. Load only what the task needs.
---

# Network Architect runbook

Navigation index for `skill-network-architect`. Do not write domain content here; write it to the matching reference.

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
| Design | [ip-addressing-plan](templates/ip-addressing-plan.md) | IPv4/IPv6 hierarchy, per-site block, VLAN/VRF map; validate with `just ip-plan` | this pack |
| Design | [site-network-design](templates/site-network-design.md) | per-site build sheet: WAN, MTU (`just mtu`), radio (`just link-budget`), VLANs, Wi-Fi, OOB, PoE | this pack |
| Design | [routing-policy](templates/routing-policy.md) | prefix ownership, per-peer import/export, filters, failover expectations | this pack |
| Design | [bgp-peer-policy](templates/bgp-peer-policy.md) | one row per BGP peer: role, RFC 8212 default, prefix limits, ROV, GTSM, BFD, tests | this pack |
| Design | [evpn-fabric-build](templates/evpn-fabric-build.md) | EVPN/VXLAN fabric build sheet: underlay ASNs, VNI/VRF/RT plan, IRB mode, ESI, MTU, failure tests | this pack |
| Accept | [wifi-survey-acceptance](templates/wifi-survey-acceptance.md) | Wi-Fi survey targets per area vs measured results, client types, sign-off | this pack |
| Accept | [ptp-link-record](templates/ptp-link-record.md) | point-to-point radio link: predicted (`just link-budget`) vs measured RSL, margin, acceptance | this pack |
| Decide | [decision-record](templates/decision-record.md) | one decision (MADR 4.0), confirmation and reopen triggers | shared |
| Decide | [risk-register](templates/risk-register.md) | scored risks with trigger, response, owner and residual | shared |
| Hand off | [handoff](templates/handoff.md) | request and response envelope between architects and specialists | shared |
| Change | [change-and-validation](templates/change-and-validation.md) | Method of Procedure: pre-checks, steps with rollback, gates, canary, batches | shared |
| Accept | [test-and-acceptance-plan](templates/test-and-acceptance-plan.md) | tests traced to requirements, oracle, failure injection, sign-off | shared |
| Operate | [post-incident-review](templates/post-incident-review.md) | blameless review: timeline, contributing factors, owned actions | shared |

## Helpers

| Need | Recipe |
| --- | --- |
| Do these segments overlap, are gateways valid? | `just ip-plan <plan.json>` |
| How much payload MTU survives this tunnel stack? | `just mtu <budget.json>` |
| Does this radio path close with margin and clearance? | `just link-budget <links.json>` |
| What availability does this series/parallel design give? | `just availability <model.json>` |
| Does the fibre plant fit the optic's budget with margin? | `just fibre <links.json>` |
| Does PoE fit each switch, and the site fit the UPS? | `just power <site.json>` |
| Are the cited links still alive? (network, read-only) | `just links` |
| Refresh local copies of cited sources (plan, then `--apply`) | `just fetch-sources` |
| Rebuild the source ledger after adding citations (plan, then `--apply`) | `just ledger` |

Inputs, formulas and limits: [scripts/README.md](scripts/README.md). Examples: `examples/`.

## Maintenance

`just bootstrap` once, `just check` before claiming any change complete. Write-back rules: [SKILL.md](SKILL.md#standing-write-back-contract).
