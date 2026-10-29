---
Title: Systems capacity, performance and economics
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Systems and infrastructure architecture
Last reviewed: 2026-10-29
Summary: Systems capacity, performance and economics decisions, failure modes and validation.
---

# Systems capacity, performance and economics

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Core formulas](#core-formulas)
- [Failure-scenario arithmetic](#failure-scenario-arithmetic)
- [Queueing and saturation](#queueing-and-saturation)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

## Scope

- Demand, growth and headroom for CPU, memory, storage, network, GPU and operator effort.
- Capacity under normal, maintenance and failure scenarios; availability arithmetic.
- Performance diagnosis method and cost of ownership.

## Decision rules

Model constraints, not averages:

- Use percentile targets at representative concurrency.
- Include background load: backups, scrubs, rebuild or backfill, log ingestion, compaction, update windows. These often set the peak.
- Separate limits, reservations and measured use. Overcommit policy must cover coincident peaks, not means.

Availability:

- Series: `A = A1 * A2 * ... * An`. Parallel: `A = 1 - (1 - A1)(1 - A2)...`, only for independent failures.
- Downtime per year = `(1 - A) * 8,760 h`: 99.9% ~ 8.76 h, 99.99% ~ 52.6 min. VERIFIED_PRIMARY, [ha-manager] table, checked 2026-10-29.
- Correlated failures (rack, power, firmware, operator, software bug) break independence. Model a shared element as a series block and state what the model excludes.
- Proxmox HA failover takes about 2 minutes. Automatic restart alone cannot meet a per-incident outage budget below that. VERIFIED_PRIMARY, [ha-manager].

Diagnosis:

- Start from end-to-end service latency. Then apply the USE method per resource: utilisation, saturation, errors.
- Correlate CPU scheduling, memory pressure, storage queues and network before tuning anything.
- Change one variable against a baseline. Record load, data size, cache state, duration and instrumentation overhead.
- Never tune caches, queues or kernel settings from a single counter.

Economics:

- Count hardware, support, power and cooling (`kWh/year = average_kW * 8,760`), space, backup, connectivity, staff time, spares, licensing and exit cost.
- Use current quoted primary sources for prices. Otherwise label ranges and assumptions.
- A more distributed design can cut one failure risk while raising staffing and coordination cost.
- Recommend the simplest option that meets agreed objectives. State the trigger to revisit it (growth runway, failure rate, cost).

## Core formulas

| Quantity              | Formula                                                            | Use                                            |
| --------------------- | ------------------------------------------------------------------ | ---------------------------------------------- |
| Little's law          | `L = lambda * W` (items in system = arrival rate x time in system) | concurrency, queue depth, connection pools     |
| IOPS from queue depth | `IOPS = outstanding_IOs / latency_s`                               | QD 32 at 0.5 ms => 64,000; QD 1 at 2 ms => 500 |
| Throughput            | `bytes/s = IOPS * IO_size`                                         | 64,000 x 4 KiB ~ 250 MiB/s                     |
| Utilisation           | `U = lambda * S` (S = service time per request)                    | U must stay < 1; plan well below it            |
| M/M/1 response time   | `R = S / (1 - U)` (single queue, random arrivals)                  | at U 0.5 R = 2S; at 0.8 R = 5S; at 0.9 R = 10S |
| Growth runway         | `months = ln(capacity / current) / ln(1 + monthly_growth)`         | 60% full, 3%/month => ~17 months to 100%       |
| Headroom              | `plan_limit = capacity * target_util`                              | target from latency curve, not a fixed 80%     |

- Little's law holds for any stable system averaged over time.
- M/M/1 shows the shape (non-linear latency near saturation). It is not a prediction.
- A single-threaded synchronous workload (QD 1) is bound by per-I/O latency, whatever IOPS the device advertises. Database commits are the common case.

## Failure-scenario arithmetic

- Compute capacity for normal, maintenance (one host drained), each required host loss and correlated rack or site loss.
- Subtract per-survivor reserve (hypervisor, ZFS ARC cap, Ceph OSD memory), then apply justified headroom.
- Pooled RAM sufficiency is necessary, not sufficient. Check the largest guest fits one survivor, plus CPU compatibility, NUMA, passthrough, affinity and storage locality.
- [capacity_check.py](../scripts/capacity_check.py) enumerates stated failure domains. It is a pooled-memory screen, not a scheduler, storage model or availability proof.

```text
Failure-scenario capacity pipeline (run once per scenario)

  +-----------------+    +------------------+    +---------------+    +-----------+
  | normal capacity |--->| remove failed    |--->| subtract      |--->| apply     |
  | (all nodes)     |    | node or domain X |    | reserve/node  |    | headroom  |
  +-----------------+    +------------------+    +---------------+    +-----+-----+
                                                                            |
                                                                            v
                                   +----------------------------------------+-----+
                                   | effective capacity >= required workload set? |
                                   +----------------------------------------------+
  Still unproven after a pass: placement, quorum, storage, network reachability.
  Legend: X the scenario's failed element   ---> next step
```

## Queueing and saturation

```text
M/M/1 response time R = S / (1 - U): latency rises non-linearly near saturation

  R/S
 10 |                                            *  U=0.9: R=10S
    |
    |
    |
    |
  5 |                                       *  U=0.8: R=5S
    |
    |
  2 |                        *  U=0.5: R=2S
  1 *  U=0: R=S
    +----+----+----+----+----+----+----+----+----+----+--> U (utilisation)
    0                        0.5            0.8  0.9  1.0
  Plan the operating point left of the knee, measured per resource. Real arrivals are burstier.
```

- Saturation shows as queueing. CPU: run-queue length and PSI. Memory: PSI and major faults. Disk: device queue and await. NIC: drops.
- Retries and timeouts amplify load near saturation.
- Size connection pools from Little's law, not from the maximum allowed connections.
- Ceph client latency includes round trips to the primary OSD and its replicas. A slow OSD sets the tail for every PG it serves.

## Patterns and anti-patterns

| Pattern                                  | Use when                    | Anti-pattern                           | Why it fails                                       |
| ---------------------------------------- | --------------------------- | -------------------------------------- | -------------------------------------------------- |
| Size on busy-hour p95/p99                | any capacity plan           | size on 24-hour average                | the peak hour is already saturated                 |
| Scenario per failure domain              | HA clusters                 | one "N+1" number for the whole estate  | a rack or feed loss removes several hosts at once  |
| Background load in the peak              | storage and backup planning | ignoring scrub, rebuild, backup        | recovery traffic lands on the busiest hour         |
| Pool sized by Little's law               | DB and app connection pools | pool = max_connections                 | contention and memory blow-up under load           |
| Shared element as a series block         | availability models         | parallel formula over shared power/ToR | overstates availability by orders of magnitude     |
| Headroom from the measured latency curve | headroom policy             | fixed 80% everywhere                   | some resources knee at 60%, others run fine at 90% |

## Failure modes and tests

| Failure                        | Symptom                                | Blast radius                     | Proving test                                                               |
| ------------------------------ | -------------------------------------- | -------------------------------- | -------------------------------------------------------------------------- |
| N+1 holds on paper only        | guests fail to start after host loss   | guests of the largest host       | drain the largest host; all required guests run within latency targets     |
| Storage misses latency at load | p99 spikes, app timeouts               | every guest on the pool          | fio or app test at target QD, data beyond cache; p99 recorded              |
| Growth outruns capacity        | sudden full or saturation              | the whole resource pool          | trend from monitoring, projected with the runway formula; alert at trigger |
| Rebuild breaches the SLO       | client p99 doubles during recovery     | every client of the pool         | fail a disk or OSD at peak load; measure client p99 during recovery        |
| Retry storm near saturation    | load multiplies after a small slowdown | the service and its dependencies | load test past the knee with real client retry settings                    |

## Worked example

Two 96 GiB nodes in rack A, one 64 GiB node in rack B. Demand 140 GiB. Reserve 16 GiB per node. No headroom.

1. Normal: (96 + 96 + 64) - 3 x 16 = 208 GiB. Lose a1: 96 + 64 - 32 = 128 GiB. Lose rack A: 64 - 16 = 48 GiB.

```text
$ just capacity examples/capacity-plan.json        (exit 1)
  normal       effective 208  demand 140  deficit 0
  lose-a1      effective 128  demand 140  deficit 12
  lose-rack-a  effective  48  demand 140  deficit 92
```

2. Rack B also holds only 1 of 3 votes, so it is inquorate anyway (`just quorum examples/quorum.json`). A witness fixes neither problem.
3. Adding a 128 GiB node b2 in rack B (`examples/capacity-plan-pass.json`) gives 320 / 240 / 160 GiB: every scenario passes.
4. Availability of the hosting chain, with both hosts behind one ToR switch (input saved as `model.json`):

```text
$ just availability examples/availability-shared-tor.json             (exit 1)
  series: power 0.9995 * shared ToR 0.9995 * parallel(host A 0.995, host B 0.995) * guest+app 0.999
  availability 0.99798  downtime 1,064 min/yr  vs target 0.999 (526 min/yr)
```

5. Pairing the ToR switches still gives 0.99848 (802 min/yr). A series guest+app at 0.999 alone uses the whole budget. The application layer, not the hosts, must improve.

## Review checklist

- [ ] Demand stated with units, percentile and concurrency; background load included.
- [ ] Every required scenario modelled: normal, maintenance, largest host, each rack or feed (`just capacity`).
- [ ] Largest guest fits one survivor; reserve per host subtracted.
- [ ] Headroom justified from a measured latency curve, not a fixed ratio.
- [ ] Availability model treats shared elements as series blocks (`just availability`); exclusions listed.
- [ ] Growth runway computed; revisit trigger and alert defined.
- [ ] Cost includes staff, power, spares, support and exit; prices sourced or labelled.
- [ ] Acceptance records inputs, units, limiting resource, sensitivity and per-phase runtime of any repeated job.

## Further reading

Links checked 2026-10-29.

Primary sources cited above

- [ha-manager]: Proxmox VE HA chapter source (availability table, ~2 min failover). VERIFIED_PRIMARY, checked 2026-10-29.
- Little's law, utilisation law, M/M/1 and availability products are standard identities; the M/M/1 curve is an illustrative model.

Method

- [USE method](https://www.brendangregg.com/usemethod.html): read this for a per-resource checklist of utilisation, saturation and errors.
- [Linux performance tools](https://www.brendangregg.com/linuxperf.html): read this for which observability tool answers which question.
- [Systems Performance, 2nd ed.](https://www.brendangregg.com/systems-performance-2nd-edition-book.html): read this for queueing, capacity planning and benchmarking method in depth.
- [Linux PSI](https://docs.kernel.org/accounting/psi.html): read this for measuring stall time due to CPU, memory and I/O pressure.

Overload and reliability

- [Google SRE book](https://sre.google/sre-book/table-of-contents/): read this for SLOs, error budgets and capacity planning practice.
- [Handling overload](https://sre.google/sre-book/handling-overload/): read this for load shedding, retries and why utilisation targets stay below saturation.
- [Google SRE workbook](https://sre.google/workbook/table-of-contents/): read this for worked SLO and alerting examples.

Benchmarking and platform sizing

- [fio documentation](https://fio.readthedocs.io/en/latest/fio_doc.html): read this for queue depth, sync and block-size options that make a storage test representative.
- [Ceph hardware recommendations](https://docs.ceph.com/en/latest/start/hardware-recommendations/): read this for per-OSD CPU, RAM and network sizing.
- [Kubernetes resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/): read this for requests, limits and how they drive scheduling and eviction.

[ha-manager]: https://raw.githubusercontent.com/proxmox/pve-docs/master/ha-manager.adoc
