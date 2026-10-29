---
Title: Migration, hybrid infrastructure and operating model
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Systems and infrastructure architecture
Last reviewed: 2026-10-29
Summary: >-
  Migration, hybrid infrastructure and operating model: 7 Rs strategy selection, dependency waves, cutover and rollback criteria, data authority, hybrid identity/DNS/time constraints, handoff.
---

# Migration, hybrid infrastructure and operating model

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Strategy selection](#strategy-selection)
- [Measure before choosing a platform](#measure-before-choosing-a-platform)
- [Discovery and waves](#discovery-and-waves)
- [Cutover criteria and data authority](#cutover-criteria-and-data-authority)
- [Hybrid constraints and handoff](#hybrid-constraints-and-handoff)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

## Scope

- Moving workloads between on-premises, Proxmox, colocation, edge and cloud: strategy, discovery, waves, cutover, rollback and data authority.
- Hybrid estates: identity, DNS, time, addressing and ownership across both sides.
- Handing the result to an operating owner.

## Decision rules

| Decision             | Rule and threshold                                                                                            | Evidence                         |
| -------------------- | ------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| Strategy vocabulary  | Use the 7 Rs for any target; they do not imply a cloud destination                                            | VERIFIED_PRIMARY [M1]            |
| Classification       | Every workload: dependency, state, support constraint, data volume, downtime tolerance, rollback limit, owner | Design rule                      |
| Cost model           | On-premises, edge and cloud options in one model                                                              | Design rule                      |
| Dependency map       | Built from evidence; each dependency marked observed, user-stated or assumed                                  | Design rule                      |
| Wave order           | Foundations first (identity, DNS, time, access, monitoring, backup), then dependents                          | Design rule                      |
| Criteria             | Go, abort and rollback criteria written with numbers and agreed with the owner before the window              | Design rule                      |
| Point of no return   | Defined in advance, with the after-path named: reverse replication or forward fix                             | Design rule                      |
| Data authority       | Exactly one authoritative side per dataset at any time                                                        | Design rule                      |
| DNS TTL              | Lower TTLs at least one current TTL period before cutover; verify clients honour them                         | Design rule; [RFC 1034][rfc1034] |
| Source after cutover | Keep it intact and read-only for an agreed hold period                                                        | Design rule                      |
| Completion           | Not complete while data reconciliation, decommission or operating ownership is open                           | Design rule                      |
| Platform choice      | No platform, product or purchase approved before inventory, utilisation and cost baselines are signed off     | Design rule                      |
| Default answer       | Retain unless the workload passes a cull test; "do not migrate" is a valid, recorded result                   | Design rule                      |

## Strategy selection

AWS Prescriptive Guidance names seven strategies (VERIFIED_PRIMARY [M1], checked 2026-10-29).

| Strategy   | Means                                                       | Choose when                                       | Main risk                                    |
| ---------- | ----------------------------------------------------------- | ------------------------------------------------- | -------------------------------------------- |
| Retire     | Switch off                                                  | No users or value; traffic evidence confirms      | Hidden consumer, retention duty              |
| Retain     | Leave in place, revisit                                     | Hardware/compliance dependency, recent investment | Becomes permanent unowned debt               |
| Rehost     | Move as-is (P2V, V2V, image copy)                           | Deadline-driven exit, stable app                  | Carries old OS/EOL problems along            |
| Relocate   | Move the platform unchanged (e.g. hypervisor to hypervisor) | Same platform at target                           | Licensing/hardware compatibility             |
| Repurchase | Replace with SaaS/product                                   | Commodity function                                | Data export, lock-in, identity integration   |
| Replatform | Small changes for a managed/containerised runtime           | Gains with limited code change                    | Behaviour drift in storage, time, networking |
| Refactor   | Re-architect                                                | Scale/resilience needs justify cost               | Longest, riskiest; needs product ownership   |

## Measure before choosing a platform

Investigation may start early; commitment waits for evidence. A platform chosen before the workload is measured usually fits a workload
that does not exist.

1. Inventory every workload: OS and version, vCPU, RAM, storage, utilisation profile, monthly cost, data volume and owner. Check that each
   source service in a capability map actually exists in the estate before designing its replacement.
2. Cull per workload before designing the receiver. Test utilisation, cost, coupling to provider-specific features (IAM conditions, event
   buses, step workflows, managed identity), data gravity, latency to retained services, compliance, refactor cost and remaining life. A
   workload due to retire within about 18 months is retained. Low-volume serverless glue (functions, queues, API gateways) is often the
   cheapest to keep and the riskiest to rebuild.
3. Build the optimised baseline the new option must beat: eliminate workloads first (often the largest saving), then rightsize, then
   commit (savings plans, reservations) against the post-elimination estate. Running commitments during dual-running means paying twice,
   so record their expiry dates.
4. Decide the platform from measured density. Fix the threshold and scoring weights before the data arrives, to avoid fitting the
   threshold to a favoured answer. When container density is low, include a non-Kubernetes candidate: a hypervisor cluster plus the
   existing identity, DNS, load balancing, secrets, monitoring and backup is a complete platform with close to zero new products.
5. Apply the same evidence rule to "obvious" platform services (IdP, secrets store, DNS, load balancer, backup). Each must show the
   incumbent cannot serve before it is added; an existing operated capability costs no new skills, patching or on-call.
6. Record an ADR taken before its evidence as Withdrawn, distinct from Rejected, and re-decide after the baseline.

```text
MEASURE BEFORE PLATFORM: commitment is gated, investigation is not

+-----------+   +------+   +-----------+   +-----------------+   +--------------------+
| inventory |-->| cull |-->| optimised |-->| density and TCO |-->| platform decision  |
| + util    |   | per  |   | baseline  |   | vs threshold    |   | (or: do not move)  |
| + cost    |   | wkld |   | to beat   |   | fixed in advance|   |                    |
+-----------+   +------+   +-----------+   +-----------------+   +--------------------+
      ^ market tests and non-binding quotes may run in parallel; no purchase before the gate
```

- Full local TCO adds the lines business cases forget: staff labour and on-call, training, migration effort, spare capacity and
  spares stock, hardware refresh, colocation and power, connectivity, DR, monitoring and security tooling, compliance evidence the
  provider used to supply, and expected outage cost. Report 3- and 5-year TCO with sensitivity, not one number.
- An OS past end of life turns a rehost into a refactor (package manager, init, mandatory access control and libraries change).
  Marketplace or vendor-managed images often cannot be exported; get the vendor's supported backup, export or re-registration path.

## Discovery and waves

- Evidence sources: flow logs/conntrack, listening sockets, DNS query logs, config references, scheduled jobs, certificates and credentials, owner interviews.
- Inventory alone misses hard-coded IPs, licence dongles, cron jobs and partner allow-lists.
- Watch for circular dependencies (identity hosted on the platform being moved) and shared maintenance windows that couple failures.

```text
Migration waves: each gate passes before the next wave starts

+--------------------------------------------------+
| wave 0  foundations at target: identity, DNS,    |
|         time, access path, monitoring, backup    |
+--------------------------------------------------+
        |  gate: target authenticates, resolves, syncs time, is observed and restored
        v
+--------------------------------------------------+
| wave 1  pilot: low-risk stateless service        |
+--------------------------------------------------+
        |  gate: rehearsal timings met, rollback rehearsed
        v
+--------------------------------------------------+
| wave 2  stateful services with replication       |
+--------------------------------------------------+
        |  gate: cutover criteria met (see data authority diagram)
        v
+--------------------------------------------------+
| wave 3  remaining services; decommission source  |
|         after the hold period                    |
+--------------------------------------------------+

Legend: v next wave   gate = exit evidence required
```

## Cutover criteria and data authority

| Criterion              | Write before the window                                                                                                                              |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Go                     | Rehearsal done with representative data; final sync fits the window; target health, backups and monitoring green; rollback rehearsed; owners present |
| Abort before switch    | Final sync not complete by a set time; integrity mismatch (row counts, checksums); any foundation dependency failing                                 |
| Roll back after switch | User transactions failing above an agreed threshold for an agreed period; data integrity defect; security control missing                            |
| Decision owner         | Named person who calls abort or rollback                                                                                                             |

```text
Data authority during a stateful cutover (time runs left to right)

source | authoritative, writable    | frozen   | read-only, kept for the hold period
target | replica, receiving sync    | final    | authoritative, writable
       |                            | sync     |
-------+----------------------------+----------+------------------------------------>
                                    RB         PNR

RB  = last rollback point: the source is still authoritative; switching back loses nothing
PNR = point of no return: the target accepted a write the source cannot receive
      after PNR, rollback means reverse replication or a forward fix
```

- Record the switch moment, replication direction, conflict prevention (freeze, fencing, read-only source) and the reconciliation check.
- Account for data gravity, transfer time on real bandwidth, egress cost and the restore path at the target.

## Hybrid constraints and handoff

- Model identity federation and sync, DNS views and split-horizon, time sources on both sides, address overlap, private access, latency and site/region outages.
- Coordinate with the network architect for routes, policy, effective bandwidth and service discovery.
- Never promise transparent portability when APIs, storage semantics or hardware dependencies prevent it.
- Name owners of cloud account recovery (break-glass), platform operations, billing and provider outage response.
- Microsoft hybrid identity: see [windows-and-identity](windows-and-identity.md).
- Handoff: named owners, service runbook, on-call schedule, patch/backup policy, spares, capacity reviews, EOL register entries, recovery exercises.
- Use skill-smc for remote SMC sites and ansible-wifi reports, skill-nautobot for inventory lifecycle, skill-openwisp for controller/telemetry readiness.
- Endpoint-heavy rollouts also need onboarding, offboarding and user-support planning.

## Patterns and anti-patterns

| Pattern                                 | Use when             | Anti-pattern                                              | Why it fails                                      |
| --------------------------------------- | -------------------- | --------------------------------------------------------- | ------------------------------------------------- |
| Evidence-built dependency map           | Before any wave      | Plan from the inventory                                   | Hard-coded IPs and cron jobs break after the move |
| Foundations wave first                  | Every migration      | Move apps before identity, DNS and backup exist at target | Target cannot authenticate, resolve or restore    |
| Numeric criteria agreed in advance      | Every cutover        | Decide go or rollback in the window                       | Sunk cost overrides evidence at 2 am              |
| Single authoritative side               | Stateful data        | Writes allowed on both sides                              | Split brain; data lost in reconciliation          |
| Source kept read-only for a hold period | After cutover        | Decommission source the same night                        | No reference copy for reconciliation or rollback  |
| Rehost with a dated follow-up           | Deadline-driven exit | Rehost and call it done                                   | Old OS and EOL debt move with the workload        |
| Expand, migrate, contract (schema)      | Schema change near a cutover | Change schema and cutover in one window          | Rollback needs the old schema the change removed  |
| Inventory, cull, baseline, then decide  | Platform or repatriation choice | Pick the platform stack first                  | Fits an imagined workload; reuse never considered |
| Identity as its own dataset             | Any service with logins | Move data, assume credentials follow               | Users locked out; hashes or aliases lost          |

## Failure modes and tests

| Failure                    | Symptom                                | Blast radius                 | Proving test                                             |
| -------------------------- | -------------------------------------- | ---------------------------- | -------------------------------------------------------- |
| Hidden dependency          | Feature fails after cutover            | Services using it            | Compare flow and DNS logs before and after the rehearsal |
| Final sync overruns        | Window ends mid-sync                   | That wave                    | Timed rehearsal with representative data                 |
| Writes on both sides       | Conflicting records                    | The dataset                  | Fencing test: the frozen source rejects writes           |
| Stale DNS caches           | Some clients reach the old side        | Users behind those resolvers | Query from client resolvers after the TTL period         |
| Circular dependency        | Target cannot start without the source | Whole wave                   | Start the target with the source isolated                |
| No restore at target       | Backup exists, restore fails           | Every migrated dataset       | Restore test at the target before decommission           |
| Unowned service after move | Alerts go nowhere                      | Migrated services            | Page test to the named owner                             |
| Credentials not migrated   | Logins fail after a clean data move     | Every user of the service    | Row-count parity, no empty hashes, sample logins per tenant |
| Bulk sync hurts the source | Live service slows during sync          | Users of the source          | Throttle tied to a health signal; watch it during the rehearsal |

## Worked example

Dataset: 2 TB over a 1 Gbit/s link at a measured 70% efficiency. Change rate: 3% per day. Window: 2 hours.

1. Initial copy: 2 x 10^12 x 8 / (10^9 x 0.7) = 22,857 s, about 6.3 hours. Run it before the window.
2. Final delta: 3% of 2 TB = 60 GB; 60 x 10^9 x 8 / (0.7 x 10^9) = 686 s, about 11.4 minutes.
3. Window budget: freeze 5 + final sync 12 + verify 20 + switch 10 + smoke test 30 = 77 minutes, leaving 43 minutes.
4. Abort rule: final sync not done by window start + 30 minutes means abort before the switch.
5. DNS: current TTL 3600 s; lower it to 300 s at least 1 hour before the window.
6. Efficiency and change rate are illustrative; measure both in the rehearsal.

Platform decision (measure before platform). An estate of 72 vCPU, 224 GB RAM and about 5.5 TB across VMs, managed databases, one
container service and serverless glue. Containers are 13-14% of compute and 9% of memory.

1. The density threshold for a Kubernetes-centred platform was fixed before the data; 13% is below any reasonable threshold.
2. The bake-off must include the non-Kubernetes candidate: hypervisor cluster, VMs, a container runtime on VMs for the few containers.
3. A platform ADR approved before the inventory existed is marked Withdrawn and re-decided on the evidence.
4. The serverless glue costs little in place; it is retained unless the cull shows otherwise. "Do not migrate" stays a valid result.

## Review checklist

- [ ] Every workload has a strategy, classification and owner; options share one cost model.
- [ ] Inventory, utilisation and cost baselines signed off before any platform or purchase; retain and do-not-migrate considered.
- [ ] Platform density threshold fixed before the data; a non-Kubernetes candidate included when density is low.
- [ ] Credentials, aliases and routing tables tracked as their own dataset with a parity gate.
- [ ] Dependencies come from evidence and carry observed, user-stated or assumed labels.
- [ ] Wave 0 foundations pass their gate before any service moves.
- [ ] Go, abort and rollback criteria have numbers and a named decision owner.
- [ ] Point of no return and the after-path are written down; one side is authoritative per dataset.
- [ ] DNS TTLs are lowered in time; the source stays read-only for the hold period.
- [ ] Rehearsal covers integrity, identity, transactions, performance, observability and restore; actual timings are kept apart from estimates.
- [ ] Untested failure scenarios and accepted risks are recorded; operating ownership is handed over.

## Further reading

- [Parallel change (expand, migrate, contract)](https://martinfowler.com/bliki/ParallelChange.html): read this for splitting a breaking schema or
  interface change from the cutover so each step can roll back alone.

Strategy frameworks:
- [M1] [AWS: migration strategies (7 Rs)][m1url] - read this for strategy definitions and use cases (VERIFIED_PRIMARY, checked 2026-10-29).
- [Microsoft Cloud Adoption Framework: Migrate][cafurl] - read this for wave planning and cutover practice.
- [Google Cloud: migration to Google Cloud, getting started][gcpurl] - read this for assess/plan/deploy/optimise phases.

Hybrid identity and DNS:
- [Microsoft Entra hybrid identity](https://learn.microsoft.com/en-us/entra/identity/hybrid/) - read this for Connect Sync vs Cloud Sync and auth methods.
- [RFC 1034][rfc1034] - read this for TTL and caching semantics behind cutover timing.

Reliability during cutover:
- [Google SRE book: Managing Incidents](https://sre.google/sre-book/managing-incidents/) - read this to run a cutover window with incident roles.

[m1url]: https://docs.aws.amazon.com/prescriptive-guidance/latest/large-migration-guide/migration-strategies.html

[cafurl]: https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/migrate/

[gcpurl]: https://cloud.google.com/architecture/migration-to-gcp-getting-started

[rfc1034]: https://www.rfc-editor.org/rfc/rfc1034.html
