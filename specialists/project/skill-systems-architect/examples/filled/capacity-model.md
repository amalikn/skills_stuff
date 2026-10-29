---
Title: hub-1 capacity model (worked example)
Category: worked-example
Status: current
Authority: authored-guidance
Scope: Filled example of templates/capacity-model.md for a fictional remote-site operator
Last reviewed: 2026-10-29
Summary: >-
  Memory, Ceph storage and hub uplink capacity for hub-1 now (40 sites) and at a 3-year horizon (60 sites), under normal, maintenance, host loss and
  power-domain loss; `just capacity` and `just ceph` do the arithmetic. All site facts are fictional.
---

# hub-1 capacity model

Fills template: [templates/capacity-model.md](../../templates/capacity-model.md). Cluster as in `host-and-cluster-build.md` (DES-014); site WAN design DES-012 and tunnel interface IF-004.

## Contents

- [How to use](#how-to-use)
- [1. Demand](#1-demand)
- [2. Supply and failure scenarios](#2-supply-and-failure-scenarios)
- [3. Headroom](#3-headroom)
- [4. Limiting resource and economics](#4-limiting-resource-and-economics)
- [5. Triggers and monitoring](#5-triggers-and-monitoring)
- [6. Assumptions and review state](#6-assumptions-and-review-state)

## How to use

How this example applied the template's rules:

- Three limiting resources modelled separately: cluster memory (GiB), Ceph usable capacity (TB) and hub internet uplink per direction (Mbit/s).
- Scenarios: normal, maintenance (pve-1 drained), largest unit lost (one host, or one uplink), correlated domain lost (rack-a with feed A). All three hosts are equal, so the largest unit is any host.
- Labels: every ERN fact is fictional and therefore USER_STATED. Helper results are static (model) evidence on those inputs.

## 1. Demand

| Resource          | Population        | Measured p95           | Peak / burst   | Window and source             | Growth rate (per year)               | Horizon | Forecast at horizon | Label       |
| ----------------- | ----------------- | ---------------------- | -------------- | ----------------------------- | ------------------------------------ | ------- | ------------------- | ----------- |
| Memory pool       | hub-1 cluster,    | 112 GiB configured     | 112            | Proxmox guest                 | site-scaled guests x 1.5 at 60 sites | 3 yr    | 148 GiB             | USER_STATED |
|                   |   9 guests        |                        |   GiB (static) |   config, 2026-10-20          |                                      |         |                     |             |
| Ceph usable       | pool vm-rbd       | 2.4 TB used            | n/a            | `ceph df`, 2026-10-20         | x 1.5 at 60 sites, plus 1.0 TB Loki  | 3 yr    | 4.6 TB              | USER_STATED |
|                   |                   |                        |                |                               |   retention 14 -> 30 d               |         |                     |             |
| Hub uplink,       | 40 sites          | 22 Mbit/s per site (18 | coincidence    | busy hour, 30 d, interface    | 15% per site, plus 20 new sites      | 3 yr    | 1,254.7 Mbit/s      | USER_STATED |
|   per direction   |   tunnelled       |   down + 4 up)         |   0.6          |   counters per tunnel         |                                      |         |                     |             |
|                   |   to hub          |                        |                |                               |                                      |         |                     |             |

Memory horizon: site-scaled guests (OpenWISP 16, InfluxDB 16, Prometheus 24, Loki 16 = 72 GiB) x 60 / 40 = 108 GiB, plus fixed guests 40 GiB = 148 GiB.

Uplink arithmetic. Site traffic hairpins through hub-1 (DES-012: tunnels terminate at hub-gw-1/2, internet breakout at hub-1), so each uplink direction carries a site's download plus its upload:

- now: 40 sites x 22 Mbit/s x 0.6 = 528 Mbit/s; with WireGuard overhead at full-size packets x 1500 / 1440 = 550.0 Mbit/s;
- horizon: per-site 22 x 1.15^3 = 33.46 Mbit/s; 60 x 33.46 x 0.6 = 1,204.5 Mbit/s; x 1500 / 1440 = 1,254.7 Mbit/s.

The 1440-byte inner MTU is the `just mtu` result for a WireGuard IPv4 layer on a 1500-byte underlay (network pack examples; CHG-031 later lowers the tunnel MTU, which raises the overhead share
slightly).

## 2. Supply and failure scenarios

```text
$ just capacity examples/filled/capacity-model.json            # exit 0, demand 112 GiB
  normal 280.8 | maintenance-drain-pve-1 187.2 | lose-pve-2 187.2 | lose-rack-a 187.2 | lose-comms-c 187.2

$ just capacity examples/filled/capacity-model-horizon.json    # exit 0, demand 148 GiB
  normal 280.8 | maintenance-drain-pve-1 187.2 | lose-pve-2 187.2 | lose-rack-a 187.2 | lose-comms-c 187.2

$ just ceph examples/filled/capacity-model-ceph.json           # exit 1
  vm-rbd-now      raw_tb 23.04  surviving_raw_tb 15.36  plan_tb 4.352  demand_tb 2.4
  vm-rbd-horizon  raw_tb 23.04  surviving_raw_tb 15.36  plan_tb 4.352  demand_tb 4.6
  findings: "vm-rbd-horizon: demand 4.6 TB exceeds the plan limit 4.35 TB after losing 1 domain(s)"
            and, for both pools, "losing 1 domain(s) leaves 2 for 3 placements; data stays degraded"
```

Ceph normal supply is not printed by the helper: 23.04 / 3 x 0.85 = 6.528 TB (same formula with no domain removed).

| Resource    | Unit            | Units | Usable per unit (after reserve) | Normal supply | Maintenance (N-1) | Largest unit lost | Correlated domain lost (which)                            | Unit   |
| ----------- | --------------- | ----- | ------------------------------- | ------------- | ----------------- | ----------------- | --------------------------------------------------------- | ------ |
| Memory      | host            | 3     | (128 - 24) x 0.9 = 93.6 GiB     | 280.8         | 187.2             | 187.2             | rack-a (pve-1): 187.2                                     | GiB    |
| Ceph usable | host (7.68      | 3     | 7.68 / 3 x 0.85 = 2.176 TB      | 6.528         | 4.352             | 4.352             | rack-a (pve-1): 4.352                                     | TB     |
|             |   TB raw)       |       |                                 |               |                   |                   |                                                           |        |
| Hub uplink  | carrier link    | 2     | 1,000 Mbit/s per direction      | 2,000         | 1,000             | 1,000             | hub-1 building entry: 0 (both carriers share one          | Mbit/s |
|             |                 |       |                                 |               |                   |                   |   duct, USER_STATED)                                      |        |

## 3. Headroom

Headroom % = headroom / supply in that scenario.

| Resource    | Scenario                         | Demand         | Supply       | Headroom = supply - demand        | Headroom % | Policy minimum | Meets?                   |
| ----------- | -------------------------------- | -------------- | ------------ | --------------------------------- | ---------- | -------------- | ------------------------ |
| Memory      | normal, now                      | 112 GiB        | 280.8 GiB    | 168.8 GiB                         | 60.1%      | 20%            | yes                      |
| Memory      | one host or domain lost, now     | 112 GiB        | 187.2 GiB    | 75.2 GiB                          | 40.2%      | 0%             | yes                      |
| Memory      | one host or domain lost, horizon | 148 GiB        | 187.2 GiB    | 39.2 GiB                          | 20.9%      | 0%             | yes                      |
| Ceph usable | normal, horizon                  | 4.6 TB         | 6.528 TB     | 1.928 TB                          | 29.5%      | 20%            | yes                      |
| Ceph usable | one host lost, now               | 2.4 TB         | 4.352 TB     | 1.952 TB                          | 44.9%      | 0%             | yes                      |
| Ceph usable | one host lost, horizon           | 4.6 TB         | 4.352 TB     | -0.248 TB                         | -5.7%      | 0%             | no                       |
| Hub uplink  | normal, horizon                  | 1,254.7 Mbit/s | 2,000 Mbit/s | 745.3 Mbit/s                      | 37.3%      | 20%            | yes                      |
| Hub uplink  | one uplink lost, now             | 550.0 Mbit/s   | 1,000 Mbit/s | 450.0 Mbit/s                      | 45.0%      | 0%             | yes                      |
| Hub uplink  | one uplink lost, horizon         | 1,254.7 Mbit/s | 1,000 Mbit/s | -254.7 Mbit/s                     | -25.5%     | 0%             | no                       |
| Hub uplink  | shared duct cut                  | any            | 0            | all sites lose hub-routed service | n/a        | n/a            | no (accepted, see below) |

Degraded service allowed (USER_STATED, service owner): on one uplink lost at the horizon, best-effort data may queue, but voice and telemetry keep priority by the hub QoS policy; on the shared duct
cut, site guest Wi-Fi continues on local satellite breakout and all hub-routed services stop. The duct risk is owned by DES-012, not by this model.

## 4. Limiting resource and economics

- Limiting resource now: none fails. Smallest worst-case margin today is the hub uplink (45.0%).
- At horizon: the hub uplink fails first and deepest (-254.7 Mbit/s with one link lost), then Ceph (-0.248 TB after a host loss). Memory still holds (20.9%).
- Options to add capacity (no prices invented; quote per option before the ADR):
  - Uplink: raise each carrier link to 2 Gbit/s (carrier lead time USER_STATED 10-12 weeks), or move guest and bulk traffic to site-local breakout (design change in DES-012, no lead time but policy
    review).
  - Ceph: two more 3.84 TB OSDs per host (raw 23.04 -> 46.08 TB; plan after a host loss = (46.08 - 15.36) / 3 x 0.85 = 8.704 TB); NVMe lead time USER_STATED 4 weeks; or shorten Loki retention back to
    14 d (-1.0 TB).
  - Memory: none needed in the horizon.

## 5. Triggers and monitoring

| Trigger             | Measurement                                 | Threshold                             | Lead time needed | Action                                    | Owner             |
| ------------------- | ------------------------------------------- | ------------------------------------- | ---------------- | ----------------------------------------- | ----------------- |
| upgrade hub uplinks | p95 per direction, 7-day, sum of both links | > 800 Mbit/s (80% of one-link supply) | 12 weeks         | order 2 Gbit/s on both carriers           | network architect |
| add Ceph OSDs       | `ceph df` used on vm-rbd                    | > 3.5 TB (80% of the 4.352 TB plan)   | 4 weeks          | buy and add 2 OSDs per host               | systems architect |
| re-check memory     | configured guest memory                     | > 150 GiB (80% of 187.2 GiB)          | 2 weeks          | re-run `just capacity`; right-size guests | systems architect |
| re-run this model   | site count in Nautobot                      | > 48 sites                            | n/a              | update demand with measured per-site p95  | systems architect |

## 6. Assumptions and review state

| ID     | Assumption                                            | Sensitivity (what changes if wrong)                                                        | Label       |
| ------ | ----------------------------------------------------- | ------------------------------------------------------------------------------------------ | ----------- |
| ASM-01 | coincidence factor 0.6 across sites at busy hour      | at 1.0 the horizon one-link demand is 2,091 Mbit/s; one link is exceeded above 28.7 sites | USER_STATED |
| ASM-02 | per-site growth 15% per year                          | at 25% the horizon uplink demand is 1,611.3 Mbit/s with the same 60 sites                    | UNVERIFIED  |
| ASM-03 | site-scaled guests grow linearly with site count      | InfluxDB series cardinality may grow faster; re-measure at 48 sites                        | UNVERIFIED  |
| ASM-04 | WireGuard overhead at full-size packets (1500 / 1440) | small-packet voice traffic carries a larger share of overhead                              | UNVERIFIED  |

Sensitivity arithmetic:

- ASM-01 at 1.0: 60 x 33.46 x 1500 / 1440 = 2,091.2 Mbit/s. One link holds 1,000 / (22 x 1500 / 1440) = 43.6 sites at the current per-site demand,
  and 1,000 / (33.46 x 1500 / 1440) = 28.7 sites at horizon demand.
- ASM-02 at 25%: 22 x 1.25^3 = 42.97 Mbit/s; 60 x 42.97 x 0.6 x 1500 / 1440 = 1,611.3 Mbit/s.

| Revision | State    | Date       | Reviewer (role)   | Evidence                                    |
| -------- | -------- | ---------- | ----------------- | ------------------------------------------- |
| r1       | reviewed | 2026-10-29 | network architect | helper runs in section 2; uplink arithmetic |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
