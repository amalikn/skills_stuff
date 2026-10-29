---
Title: Servers, compute and facilities
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Systems and infrastructure architecture
Last reviewed: 2026-10-29
Summary: Servers, compute and facilities decisions, failure modes and validation.
---

# Servers, compute and facilities

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Memory reserve and N+k arithmetic](#memory-reserve-and-nk-arithmetic)
- [Power, UPS and thermal arithmetic](#power-ups-and-thermal-arithmetic)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

## Scope

- Hardware fit for a workload: CPU, NUMA, memory, accelerators.
- Host memory reserve and N+k admission under host loss.
- Physical failure domains: power, cooling, rack, out-of-band (OOB) management.
- Edge and small-site compute.

## Decision rules

Workload and hardware fit:

- Inventory criticality, CPU architecture (x86-64 or arm64), concurrency, memory working set, I/O pattern and accelerator need.
- Count sockets, cores, logical CPUs (SMT), NUMA nodes and instruction-set features separately. A vCPU is a schedulable thread, not a core.
- Measure sustained and burst behaviour on representative data. Core count alone never proves application performance.
- Pin the guest CPU model to the oldest host in a live-migration group. Mixed CPU vendors break live migration (see the virtualisation reference).
- For accelerators record memory size and bandwidth, interconnect, driver and runtime version, isolation mode (passthrough, mediated, shared), power and portability.
- Local LLM inference: the quantised model plus KV-cache headroom must fit accelerator memory. Measure tokens/s at the target concurrency.

Overcommit:

- Overcommit is workload-specific. Model swap, pressure stall (PSI) and tail latency, not a universal ratio.
- CPU overcommit shows as steal or ready time. Memory overcommit shows as swap, ballooning and OOM kills, which do far more damage.
- Ballooning and KSM may stretch memory only for workloads measured to tolerate it. Never count them in a failure scenario.

Physical failure domains:

- Map chassis, rack, power feed, UPS or generator, cooling zone, NIC/HBA, boot media, storage path and OOB for every host.
- Two PSUs on one PDU, or two PDUs on one UPS, are one failure domain.
- Two hosts on one top-of-rack (ToR) switch share a network failure domain.
- Prove OOB works with production network, DNS and identity provider down. That is when it is needed.
- Specify rack power and thermal envelope, remote hands, spares, firmware lifecycle, vendor support access and media disposal.

Edge and small sites:

- Edge boxes (Raspberry Pi class, fanless x86) fail mostly on storage wear, power quality and heat, not CPU.
- Use industrial or high-endurance media, a read-only or overlay root, logs in RAM with forwarding, and a watchdog reboot path.
- Budget PoE or DC power with brown-out margin. Under-voltage throttling and SD corruption are common (UNVERIFIED as a fleet rate; measure).
- Make each box reprovisionable from a golden image plus configuration management. Recovery is replacement, not repair.
- Judge enclosure heat from throttle and thermal counters, not uptime.
- Full design of unattended Linux site boxes (image layout, updates, flash wear, watchdog, power): [edge appliances](edge-appliances.md).

## Memory reserve and N+k arithmetic

```text
usable_host = RAM_installed
            - host_os_and_hypervisor          (measure; typically several GiB)
            - storage_cache_cap               (e.g. ZFS ARC limit)
            - storage_daemons                 (e.g. Ceph OSDs x per-OSD memory target)
            - agents, monitoring, backup client
```

- Admission rule: `sum(guest_RAM_committed) <= fill_target * sum(usable_host over the surviving set)`.
- Remove the largest host first (worst case). Remove a whole rack or feed when the requirement names it.
- Then check the largest single guest fits on one survivor. This is bin packing, not pooling.
- Ceph OSD memory target defaults to 4 GiB per OSD. VERIFIED_PRIMARY, [pveceph], checked 2026-10-29 (master, PVE 9.x era).

## Power, UPS and thermal arithmetic

Unit identities and planning arithmetic. Vendor runtime charts govern real runtime.

| Quantity               | Rule                                                                    | Example                              |
| ---------------------- | ----------------------------------------------------------------------- | ------------------------------------ |
| Real vs apparent power | `kW = kVA * power_factor`; size a UPS on both limits                    | 1500 VA at PF 0.9 => 1350 W ceiling  |
| Load ceiling           | Plan steady load <= ~80% of UPS W rating (operator policy, no standard) | 1350 W UPS => plan <= 1080 W         |
| Runtime estimate       | `hours ~= battery_Wh * usable_fraction * inverter_eff / load_W`         | 216 Wh * 0.8 * 0.9 / 300 W ~= 0.52 h |
| Heat                   | `BTU/h = W * 3.412`; all IT power becomes heat                          | 2 kW rack => ~6,824 BTU/h            |
| Redundant PSU load     | Each PSU must carry the whole host when the other fails                 | measure per-PSU draw with one pulled |

- Battery runtime is non-linear and degrades with age and heat; the linear estimate is optimistic. UNVERIFIED as a coefficient; use the vendor curve and a timed discharge.
- Shutdown must fit runtime: `UPS_runtime >= detection + shutdown_ordering + longest guest/storage shutdown + margin`.
- Stop storage clients before storage servers. Do not let a quorum cluster lose quorum mid-shutdown.

Colocation power billing and dual-feed draw:

- Colocation power is billed as metered energy (kWh), as committed capacity (contracted kVA or kW per cabinet), or both. Read the product names on the invoice line items before modelling any saving.
  Under committed-capacity billing, lower actual draw changes nothing on the invoice; the only direct lever is a lower contracted figure, gated by contract
  terms and notice periods. UNVERIFIED as a universal model: billing varies by provider and contract, so confirm it per contract.
- Size a committed figure from per-cabinet peaks over at least three months plus a stated margin, and name the most loaded cabinet as the constraint. Daily averages hide short peaks and inrush; prefer
  interval peak data. Never decommission a cabinet without a service map proving nothing live depends on it.
- Dual-PSU equipment normally shares load across both supplies, so near-equal A and B feed draw is expected, not waste. Total cabinet load is A + B, and on a feed failure one circuit carries all of
  it. Rule: A + B <= the usable rating of one feed, so each feed runs at or below about 50% of its usable rating in normal operation. Removing B-feed paths cuts resilience, not cost, under capacity
  billing. Load sharing is VERIFIED_SECONDARY (PSU vendor behaviour varies; some units run active/standby); measure per-PSU draw with the peer pulled (table above).

```text
Dual-feed power: each host draws one PSU from each independent feed

  ==== feed A ====================================
  utility A --> UPS A --> PDU A --+--> host-1 PSU1
                                  +--> host-2 PSU1
  ==== feed B ====================================
  utility B --> UPS B --> PDU B --+--> host-1 PSU2
                                  +--> host-2 PSU2

  Feed A lost: both hosts run on PSU2 alone, so each PSU2 carries 100% of its host.
  Same domain if shared: breaker, UPS, PDU, cooling zone, ToR switch, OOB switch, firmware batch.
  Legend: --> power flows to   ==== independent feed boundary
```

## Patterns and anti-patterns

| Pattern                             | Use when                          | Anti-pattern                           | Why it fails                                      |
| ----------------------------------- | --------------------------------- | -------------------------------------- | ------------------------------------------------- |
| One PSU per independent feed        | any host with two PSUs            | both PSUs on one PDU or UPS            | one breaker trip takes the "redundant" pair       |
| N+1 sized on the largest host       | any HA cluster                    | pooled RAM sized on the average host   | the largest host's guests have nowhere to go      |
| Guest CPU model = oldest host       | live migration across generations | `host` CPU type on mixed hardware      | migration fails or guests crash on the older host |
| OOB on its own path and credentials | every host and switch             | OOB behind production DNS, IdP or VLAN | unreachable in exactly the outage that needs it   |
| Replace-not-repair edge image       | fleets of small boxes             | hand-tuned edge boxes                  | each failure becomes a site visit and a snowflake |
| Measure PSI and p99 under load      | sizing and acceptance             | sizing from core count or average CPU  | saturation hides in tails and stall time          |

## Failure modes and tests

| Failure                                 | Symptom                                         | Blast radius                | Proving test                                           |
| --------------------------------------- | ----------------------------------------------- | --------------------------- | ------------------------------------------------------ |
| Both PSUs on one feed                   | host drops on a single breaker trip             | every host on that feed     | pull each PSU under load; record per-PSU W             |
| Pooled RAM fits, largest guest does not | guest stays down after host loss                | services on the lost host   | drain the largest host; every required guest starts    |
| UPS runtime shorter than shutdown chain | hard power-off mid-shutdown, fsck, rebuild      | whole rack                  | timed on-battery test to the shutdown trigger          |
| OOB depends on production services      | no console during an outage                     | recovery of every host      | reach OOB with the production network isolated         |
| Thermal throttling at summer peak       | latency spikes, throttle counters rise          | hosts in that cooling zone  | load test at worst ambient; read thermal counters      |
| Firmware drift across hosts             | one host behaves differently under failover     | the odd host and its guests | inventory diff of BIOS/NIC firmware before acceptance  |
| A + B draw above one feed's rating      | breaker trips on the survivor after a feed loss | whole cabinet               | sum per-feed peaks; compare with one feed's usable kVA |
| Saving modelled on the wrong billing    | kWh saving that never appears on the invoice    | the business case           | match each invoice line to energy or capacity billing  |

## Worked example

Three hosts of 128 GiB. Reserve per host: 8 GiB host OS plus four Ceph OSDs at 4 GiB = 24 GiB. Fill target 0.9 (headroom 0.1).

1. Usable per host = 128 - 24 = 104 GiB. N+1 survivors = 2 x 104 = 208 GiB.
2. Ceiling after the largest host fails = 208 x 0.9 = 187.2 GiB of guest RAM, not 3 x 128 = 384 GiB.
3. Test a proposed 200 GiB commitment (input: three nodes, `memory_gib` 128, `reserve_gib` 24, `demand_gib` 200, `headroom_fraction` 0.1):

```text
$ just capacity examples/compute-3-hosts.json
  normal   effective_memory_gib 280.8  demand 200  deficit 0
  lose-h1  effective_memory_gib 187.2  demand 200  deficit 12.8
  findings: ["lose-h1: memory deficit 12.8 GiB"]   status: findings (exit 1)
```

4. Decision: cap commitments at 187 GiB, or add a fourth host. Then confirm the largest guest fits one 104 GiB survivor.
5. Power check for the same rack: 3 hosts x 450 W measured = 1,350 W. A 1500 VA / PF 0.9 UPS has a 1,350 W ceiling. That is 100% of rating, above the 80% (1,080 W) policy, so size up the UPS.

## Review checklist

- [ ] Every host maps to rack, feed, UPS, PDU, cooling zone, ToR and OOB switch.
- [ ] Each PSU sits on a different independent feed; per-PSU draw measured with the peer pulled.
- [ ] N+k computed with the largest host removed and the reserve subtracted (`just capacity`).
- [ ] Largest guest fits one survivor; guest CPU model pinned to the oldest host.
- [ ] UPS load <= policy ceiling; runtime covers the measured shutdown chain.
- [ ] Colocation billing model read from invoice lines (energy, capacity or both) before any power saving is modelled.
- [ ] Cabinet A + B peak draw <= one feed's usable rating; near-equal A/B split treated as normal.
- [ ] Remote edge boxes follow [edge appliances](edge-appliances.md): A/B image, watchdog, flash write budget, power telemetry.
- [ ] OOB reachable with production network, DNS and IdP down.
- [ ] Firmware and driver versions inventoried and consistent; warranty and refresh dates recorded.
- [ ] Acceptance used representative load and recorded PSI, steal, I/O latency and p99, not averages.
- [ ] Network architect reviewed uplinks, OOB and storage paths; collection scripts go through skill-coder.

## Further reading

Links checked 2026-10-29. This reference keeps the decision rules; go to these for depth.

CPU, NUMA and memory

- [QEMU CPU models](https://www.qemu.org/docs/master/system/qemu-cpu-models.html): read this for choosing a guest CPU model that keeps live migration working across host generations.
- [Linux NUMA memory policy](https://docs.kernel.org/admin-guide/mm/numa_memory_policy.html): read this for how memory placement follows NUMA policy and why remote access costs latency.
- [Linux PSI (pressure stall information)](https://docs.kernel.org/accounting/psi.html): read this for measuring CPU, memory and I/O pressure instead of guessing from utilisation.
- [Linux KSM](https://docs.kernel.org/admin-guide/mm/ksm.html): read this for what memory page merging can and cannot save, and its CPU cost.

Hypervisor host sizing

- [Proxmox VE Ceph chapter](https://pve.proxmox.com/pve-docs/chapter-pveceph.html): read this for per-node CPU, memory and network recommendations when hosts also run Ceph.
- [pveceph]: Ceph chapter source cited for the OSD memory target (VERIFIED_PRIMARY, checked 2026-10-29).
- [Proxmox VE host system administration (ZFS, ARC limit)](https://pve.proxmox.com/pve-docs/chapter-sysadmin.html): read this for host memory taken by ZFS ARC and how to cap it.

Performance method

- [Brendan Gregg, USE method](https://www.brendangregg.com/usemethod.html): read this for a utilisation/saturation/errors checklist per resource.
- [Systems Performance, 2nd ed.](https://www.brendangregg.com/systems-performance-2nd-edition-book.html): read this for the full method and tooling for CPU, memory, disk and network analysis.

Facilities

- [ASHRAE Datacom series](https://www.ashrae.org/technical-resources/bookstore/datacom-series): read this for thermal envelopes and allowable inlet temperature classes for IT equipment.
- [Uptime Institute tier standard](https://uptimeinstitute.com/tiers): read this for the vocabulary of concurrently maintainable and fault-tolerant facility designs.

[pveceph]: https://raw.githubusercontent.com/proxmox/pve-docs/master/pveceph.adoc
