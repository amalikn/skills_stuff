---
Title: Network capacity, resilience and economics
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Network architecture
Last reviewed: 2026-10-29
Summary: >-
  Sizing links and devices for normal and failure load, composing availability, convergence budgets and cost comparison, with patterns, failure tests,
  a worked example run through `just availability` and a review checklist.
---

# Network capacity, resilience and economics

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

---

## Scope

- Link, device and path capacity under normal, maintenance and failure load; availability targets; convergence; cost per option.
- General formulas (availability, Little's law, queueing, error budget) live in the [architecture method](architecture-method.md#quantitative-rules).
- Form: [capacity model](../templates/capacity-model.md). Helper: `just availability <model.json>`.
- Host, storage and restore throughput: give skill-systems-architect the effective path rate, not the advertised one.

## Decision rules

Demand:
- Size on busy-hour demand, never on a 24-hour average. State payload, overhead, burst and concurrent peak separately.
- Map each flow to every shared bottleneck: radio, uplink, firewall, tunnel crypto, proxy, destination.
- A 10 Gbit/s port is not 10 Gbit/s of encrypted, inspected or small-packet throughput. Use the datasheet figure for that mode, then test.
- Use an explicit forecast per resource, not a universal headroom percentage.

Headroom under failure (arithmetic):
- n equal links at utilisation u carry u x n / (n - 1) each after one loss.
- To stay under U after one loss, keep normal u <= U x (n - 1) / n. Two links, U = 80%: normal <= 40% each.
- ECMP and LAG hash per flow. One large flow is capped at one member, whatever the bundle size.

Queueing and transfer:
- M/M/1 time in system = S / (1 - rho): 2x at 50% load, 5x at 80%, 10x at 90%. VERIFIED_SECONDARY; real traffic knees earlier.
- Transfer time = bytes x 8 / (rate x efficiency). 500 GB at 100 Mbit/s and 0.9 efficiency = 4,000 Gbit / 90 Mbit/s ~ 12.3 h.
- One TCP flow is capped at window / RTT. A 64 KiB window at 50 ms caps near 10.5 Mbit/s. VERIFIED_PRIMARY, RFC 6349.
- Sessions or trunks: Erlang B, B(E, 0) = 1; B(E, n) = E x B(E, n-1) / (n + E x B(E, n-1)). Blocked attempts are assumed lost. VERIFIED_SECONDARY.
- 95th-percentile billing: 5-minute samples over 30 days = 8,640; the top 432 (about 36 h) are free. Contract terms vary: UNVERIFIED as a rule.

Availability:
- Series A = product of blocks; parallel A = 1 - product of (1 - A_i). VERIFIED_PRIMARY, NIST handbook, checked 2026-10-29.
- Both formulas assume independent failures and perfect failover. Model the shared element and the failover mechanism as series blocks.
- Steady-state A = MTBF / (MTBF + MTTR). At remote sites MTTR includes travel and spares; it often decides the design.
- Convergence budget = detection (BFD or hold timers) + propagation + FIB update + session or application retry. Measure it end to end.

Economics:
- Compare capital, support, circuits, licences, energy, training, spares and replacement over the same horizon for every option.
- Normalise to cost per site-year, or per delivered Mbit/s at the required availability. Never invent a current price.
- Free control software may still need paid hardware or subscriptions. Include exportability, EOL lead time and ownership.
- Prefer a phased improvement when it meets the outcome without a new fabric or controller.

## Patterns and anti-patterns

| Situation                        | Do                                                  | Avoid                            | Why                                         |
| -------------------------------- | --------------------------------------------------- | -------------------------------- | ------------------------------------------- |
| Two "diverse" WAN links          | prove separate duct, carrier and entry point        | trusting two lines on a drawing  | a shared duct turns the pair into one block |
| Sizing a site uplink             | busy-hour p95 plus failure load                     | 24-hour average                  | the busy hour can already saturate          |
| Dual firewalls                   | check upstream switch and state-sync path           | counting two boxes as redundancy | both may hang off one switch                |
| Replication over WAN             | give the effective rate after crypto and contention | quoting the circuit rate         | restore time is set by the real rate        |
| Real-time traffic on a busy link | reserve or prioritise, then verify enforcement      | relying on headroom alone        | queueing delay grows sharply near the knee  |
| Choosing between options         | cost per site-year at the required availability     | upfront price only               | support and travel dominate at remote sites |

## Failure modes and tests

| Failure                             | Signal                                             | Test that proves detection and recovery                          |
| ----------------------------------- | -------------------------------------------------- | ---------------------------------------------------------------- |
| One uplink lost; survivor saturates | drops and p95 latency rise on the survivor         | fail one link at busy hour in a window; measure the survivor     |
| Common-mode failure (power, duct)   | both paths down together                           | trace both paths physically; pull the shared feed in a window    |
| Slow convergence                    | user sessions reset; flows black-holed for seconds | fail a link under load; time loss from both ends                 |
| Elephant flow on one member         | one LAG member full, others idle                   | run a single large transfer; read per-member counters            |
| Failover path never exercised       | backup link carries no traffic for months          | scheduled failover drill; confirm the backup carries the service |

## Worked example

Site with power, a core switch and two fibre WANs. Target availability 0.999. Model A ignores the duct; model B adds it.

```text
AVAILABILITY BLOCKS: series blocks multiply; the WAN pair is parallel; the duct is a hidden series block

                                                        +-------------+
                                                    +-->| WAN-A fibre |
                                                    |   | 0.995       |
+------------+   +-------------+   +-------------+  |   +-------------+
| site power |-->| core switch |-->| shared duct |--+
| 0.999      |   | 0.9995      |   | 0.999 ?     |  |
+------------+   +-------------+   +-------------+  |
                                                    |   +-------------+
                                                    +-->| WAN-B fibre |
                                                        | 0.995       |
                                                        +-------------+
Legend: --> series path; branch at + = parallel pair; '?' = UNVERIFIED shared-risk block
```

Input for model B (model A omits the `shared duct` block):

```json
{"schema_version": 1, "target": 0.999, "model": {"series": [
  {"name": "site power", "availability": 0.999},
  {"name": "core switch", "availability": 0.9995},
  {"name": "shared duct", "availability": 0.999},
  {"parallel": [{"name": "WAN-A", "availability": 0.995}, {"name": "WAN-B", "availability": 0.995}]}]}}
```

Real output of `just availability`, run 2026-10-29:

| Model               | availability | downtime_minutes_per_year | status                        |
| ------------------- | ------------ | ----------------------- | ----------------------------- |
| A, independent WANs | 0.998475537  | 801.81 (13.4 h)         | findings: misses target 0.999 |
| B, shared duct      | 0.997477062  | 1326.96 (22.1 h)        | findings: misses target 0.999 |

- The WAN pair alone reaches 1 - 0.005^2 = 0.999975. Power and the switch set the result, not the second WAN.
- The unverified duct adds 8.7 h a year. Survey the duct before buying a third WAN.
- Headroom check: two 1 Gbit/s links, busy hour 700 Mbit/s total. Normal 35% each; after one loss 70% of one link, under an 80% limit.

## Review checklist

- [ ] Demand is busy-hour, with units, source and window
- [ ] Each flow mapped to its bottleneck, including crypto and inspection limits
- [ ] Normal, maintenance, single-loss and correlated-loss scenarios computed
- [ ] Shared elements (power, duct, switch, control plane) modelled as series blocks
- [ ] `just availability` run; result compared with the requirement, not a generic target
- [ ] Convergence measured end to end, not taken from timer settings
- [ ] Degraded mode stated: which services are limited or paused after a loss
- [ ] Costs compared per site-year over one horizon, with assumptions labelled

## Further reading

All links resolved 2026-10-29.

Availability and risk:
- NIST handbook series and parallel reliability models:
  - <https://www.itl.nist.gov/div898/handbook/apr/section1/apr181.htm>
  - <https://www.itl.nist.gov/div898/handbook/apr/section1/apr182.htm>
- [SRE book: Embracing risk](https://sre.google/sre-book/embracing-risk/): availability targets as a cost decision.
- [AWS Well-Architected: Reliability pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html): failure-domain questions.
- [NIST SP 800-160 Vol. 2 Rev. 1](https://csrc.nist.gov/pubs/sp/800/160/v2/r1/final): anticipate, withstand, recover, adapt as resilience goals.

Overload and convergence:
- [SRE book: Handling overload](https://sre.google/sre-book/handling-overload/): why near-saturation systems collapse.
- [SRE book: Addressing cascading failures](https://sre.google/sre-book/addressing-cascading-failures/): how retries amplify load.
- [RFC 5880 BFD](https://www.rfc-editor.org/rfc/rfc5880.html): failure-detection timing that bounds convergence.
- [RFC 4594 DiffServ service classes](https://www.rfc-editor.org/rfc/rfc4594.html): mapping traffic types to queues.

Throughput testing and queueing:
- [RFC 6349 TCP throughput testing](https://www.rfc-editor.org/rfc/rfc6349.html): BDP, window sizing, TCP efficiency.
- [RFC 2544 benchmarking](https://www.rfc-editor.org/rfc/rfc2544.html): lab throughput and frame-size tests.
- [ITU-T Y.1564](https://www.itu.int/rec/T-REC-Y.1564): service activation tests of a delivered circuit.
- [M/M/1 queue](https://en.wikipedia.org/wiki/M/M/1_queue) and [Erlang unit](https://en.wikipedia.org/wiki/Erlang_(unit)): secondary sources for the models above.
