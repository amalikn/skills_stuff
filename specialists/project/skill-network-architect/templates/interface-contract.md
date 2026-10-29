---
Title: Shared interface contract template
Category: template
Status: current
Authority: authored-guidance
Scope: Portable architecture skill pack
Last reviewed: 2026-10-29
Summary: Contract for one interface between network, systems and specialist domains: flows, dependencies, budgets, failure behaviour, field ownership and acceptance tests.
---

# IF-<nnn>: <producer> to <consumer> interface contract

## How to use

- Write one contract per interface that crosses an ownership boundary (host uplink, storage transport, tunnel, controller API, telemetry feed, identity dependency).
- Both owners sign the same revision.
- A material change to any row reopens review.
- Label facts VERIFIED_PRIMARY / VERIFIED_SECONDARY / USER_STATED / UNVERIFIED.

## 1. Identity

| Field                     | Value                                               |
| ------------------------- | --------------------------------------------------- |
| Interface ID / revision   | IF-<nnn> / r<n>                                     |
| Producer (service, owner) | <service> / <role>                                  |
| Consumer (service, owner) | <service> / <role>                                  |
| Purpose                   | *What the consumer cannot do without this interface.* |
| Related                   | design <DES-nnn>, ADR-<nnnn>, requirements REQ-<nn> |

```text
INTERFACE IF-<nnn>: one flow across an ownership boundary

+------------------------+  <protocol>/<port>, <encryption>  +------------------------+
| <producer> @ <zone>    |---------------------------------->| <consumer> @ <zone>    |
+------------------------+  via <VLAN/VRF/overlay/tunnel>    +------------------------+

depends on: DNS, time, identity <list>
enforcement point: <policy point>; owners: producer <role>, consumer <role>
```

## 2. Flows

| Flow ID | Source (identity, prefix, zone) | Destination     | Protocol / port | Direction / stateful           | VLAN / VRF / overlay | Encryption and authN | Label       |
| ------- | ------------------------------- | --------------- | --------------- | ------------------------------ | -------------------- | -------------------- | ----------- |
| F1      | <role> <prefix> <zone>          | <role> <prefix> | tcp/<port>      | initiator->responder, stateful | <vlan/vrf>           | TLS, mutual cert     | USER_STATED |

Denied flows that must stay denied: *list with the enforcement point.*

## 3. Budgets and dependencies

| Item                            | Budget and unit                | How measured                         | Current value | Label      |
| ------------------------------- | ------------------------------ | ------------------------------------ | ------------- | ---------- |
| Path MTU (payload)              | <n> bytes after encapsulation  | `mtu_budget.py` model + DF-bit probe | <n>           | UNVERIFIED |
| Throughput                      | <n> Mbit/s sustained, <n> peak | flow export / iperf window           |               |            |
| Latency / jitter / loss         | p95 <n> ms / <n> ms / <n>%     | probe <interval> from <vantage>      |               |            |
| DNS / DHCP-RA / time / identity | *named service and fallback*   |                                      |               |            |

Storage interfaces add: multipath mode, latency sensitivity, rebuild/resync traffic, isolation from user traffic. Host interfaces add: bond mode, LACP rate, bridge/VLAN semantics, failover time.

## 4. Failure behaviour

| Condition                       | Expected behaviour   | Detection (signal, threshold) | Convergence / restore time | Consumer effect      | Recovery owner |
| ------------------------------- | -------------------- | ----------------------------- | -------------------------- | -------------------- | -------------- |
| Normal                          |                      |                               |                            |                      |                |
| Planned maintenance of producer | *drain, hold, or fail* |                               |                            |                      |                |
| Loss of one path / member       |                      |                               | <n> s                      |                      |                |
| Loss of producer domain         |                      |                               |                            | *RTO/RPO contribution* |                |

Independent recovery access: *how an operator reaches both ends when this interface is down.*

## 5. State ownership

| Field or object          | Authoritative writer (intent) | Observed-state producer | Freshness | Conflict policy                                     |
| ------------------------ | ----------------------------- | ----------------------- | --------- | --------------------------------------------------- |
| *e.g. VLAN on host uplink* | <inventory system / role>     | <collector>             | <n> min   | *observation raises a finding; never rewrites intent* |

## 6. Acceptance

| Test             | Method                       | Expected                              | Actual and evidence | Date | Reviewer |
| ---------------- | ---------------------------- | ------------------------------------- | ------------------- | ---- | -------- |
| Allowed flow F1  | connect from source identity | succeeds                              |                     |      |          |
| Denied flow      | connect from <zone>          | blocked and logged                    |                     |      |          |
| Full-size packet | DF-set probe at payload MTU  | passes, no fragmentation              |                     |      |          |
| Path loss        | fail member during load      | restore within <n> s, no session loss |                     |      |          |

## 7. Review state

| Revision | State    | Producer owner | Consumer owner | Date | Evidence |
| -------- | -------- | -------------- | -------------- | ---- | -------- |
| r1       | proposed |                |                |      |          |

States: proposed -> evidence-needed -> reviewed -> accepted -> implemented -> verified (also rejected, superseded).
