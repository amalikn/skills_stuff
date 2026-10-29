---
Title: Systems observability, incidents and reliability
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Systems and infrastructure architecture
Last reviewed: 2026-10-29
Summary: >-
  Systems observability, incidents and reliability: SLIs first, signal design, retention and clock correctness, alert quality, incident result shape, probe limits, incident roles,
  post-incident review, acceptance.
---

# Systems observability, incidents and reliability

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Signals and pipeline](#signals-and-pipeline)
- [Incident roles and timeline](#incident-roles-and-timeline)
- [Incident result shape](#incident-result-shape)
- [What each probe does not prove](#what-each-probe-does-not-prove)
- [Investigation and review](#investigation-and-review)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

## Scope

- Service-level indicators, signal pipelines, retention, alerting, incident handling and post-incident review for systems.
- Define user journeys and SLIs (availability, latency, freshness, correctness) before choosing a stack.
- Map resources, dependencies, owners, escalation, maintenance suppression and evidence retention.
- Network-path diagnosis belongs with skill-network-architect; OpenWISP with skill-openwisp; ansible-wifi reports with skill-smc.

## Decision rules

| Decision             | Rule and threshold                                                                                                   | Evidence                               |
| -------------------- | -------------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| Objectives           | Set per service; use error budgets only where a team will act on them                                                | Design rule; [SRE workbook][sloimpl]   |
| Paging               | Page only on symptoms that need a human now: SLO burn, user path down, data-loss risk. Causes go to tickets          | Design rule                            |
| Runbooks             | Every page links symptom, safe diagnostics, reversible response, stop conditions, escalation                         | Design rule                            |
| Noisy alerts         | Review monthly; an alert nobody acts on is deleted or demoted                                                        | Design rule                            |
| Prometheus retention | Default 15d when neither time nor size is set; size retention at most 80-85% of the disk                             | VERIFIED_PRIMARY [P1]                  |
| Single local TSDB    | Treat as non-HA; use remote write or a long-term store when retention or HA matters                                  | Design judgement, UNVERIFIED as a      |
|                      |                                                                                                                      | vendor statement                       |
| Freshness            | Alert on data age and absence (`absent()`, last-sample age), not only on values                                      | Design rule                            |
| Labels               | No user IDs, request IDs or free text as metric labels                                                               | Cited [Prometheus practices][promprac] |
| Audit log retention  | Per legal or contract duty: USER_STATED or cited, never guessed                                                      | Design rule                            |
| Incident roles       | Commander, operations, communications, planning. The commander holds every undelegated role; only operations changes | VERIFIED_PRIMARY [G1]                  |
|                      | the system                                                                                                           |                                        |
| Security incidents   | NIST SP 800-61 Rev. 3 (April 2025), aligned to CSF 2.0 functions: preserve evidence, scope before eradication        | VERIFIED_PRIMARY [N1]                  |
| Incident result      | Exactly one most-likely fault domain with confidence; conflicting evidence means "inconclusive"                      | Design rule (this file)                |

## Signals and pipeline

```text
Telemetry pipeline with meta-monitoring

+----------------+     +----------------+     +----------------+     +----------------+     +----------------+
| hosts, apps,   | --> | agents and     | --> | collector:     | --> | stores: TSDB,  | --> | query and      |
| devices        |     | exporters      |     | buffer,        |     | logs, traces   |     | alerts         |
| (journald,     |     | (node_         |     | relabel,       |     |                |     | (Grafana,      |
| SNMP)          |     | exporter)      |     | redact (OTel,  |     |                |     | Alertmanager)  |
|                |     |                |     | Vector, Alloy) |     |                |     |                |
+----------------+     +----------------+     +----------------+     +----------------+     +----------------+
                                                      ^                                             |
                                                      |  meta-monitoring: scrape success,           |
                                                      |  sample age, queue depth, drops             |
                                                      +---------------------------------------------+

Legend: --> telemetry flow   loop = the pipeline watches its own health
```

| Signal           | Use for                           | Watch                                                              |
| ---------------- | --------------------------------- | ------------------------------------------------------------------ |
| Metrics          | Rates, saturation, SLIs, alerting | Label cardinality: no user IDs, request IDs or free text as labels |
| Logs             | Event detail, audit, forensics    | Structured fields, UTC, PII redaction, volume per source           |
| Traces           | Latency across services           | Sampling policy; propagate context across hops                     |
| Synthetic probes | Outside-in user path              | Probe from where users are, not only from the monitoring host      |

- Size the collector disk buffer for the longest upstream outage.
- OpenTelemetry provides open APIs, SDKs and a collector for traces, metrics and logs. Use it at boundaries to limit lock-in; check signal stability in its docs.
- A collector reporting "success" can still leave samples stale or missing downstream.
- Retention per class: operational metrics weeks to months; logs for incident and security review; audit logs per duty.
- Size storage from measured ingest rate x retention x overhead; re-measure when the fleet grows.
- Log in UTC; record receive time beside event time. A host with a bad clock is an unreliable witness.
- Edge boxes without an RTC battery can boot with a wrong date: gate log shipping and TLS on time sync. Journald details: [linux-unix](linux-unix.md).

## Incident roles and timeline

```text
Incident timeline and the three durations to measure

T0 first         T1 detected,     T2 commander,    T3 mitigated     T4 resolved      T5 review,
signal           severity set     comms started    impact stops     root fix         actions owned
|                |                |                |                |                |
+----------------+----------------+----------------+----------------+----------------+-->
|                |                |                |                |                |
|<-- detect ---->|<-- mitigate ------------------->|
                 |<-- resolve ------------------------------------->|

Legend: + stage boundary on the time axis   |<-- x -->| measured interval (T1-T0, T3-T1, T4-T1)
```

- Keep a live incident document: UTC timeline, actions and who took them, hypotheses and their tests, decisions, current state.
- Mitigate before root cause: roll back, fail over, shed load. Record each change so it can be reverted.
- Hand off explicitly ("you are now incident commander") with a state summary. No silent handoffs.
- Security incidents: involve the security owner; follow [N1].

## Incident result shape

Every diagnosis returns this shape, so the next responder can act on it.

```text
Symptom:      <user-visible effect, affected population, first and last seen (UTC)>
Observations: [Observed] <measured this incident, with source and timestamp>
              [Inferred] <derived from observations; name the step of reasoning>
              [Unknown]  <not checked yet, or not checkable>
Fault domain: <exactly one> application | runtime/container | OS/host | hypervisor/cluster | storage
              | network (hand to network architect) | identity/DNS/time | external dependency | inconclusive
Confidence:   low | medium | high
Next check:   <one safest read-only or reversible check that splits the remaining hypotheses>
```

- Name one most-likely domain, not a list. When observations conflict, answer "inconclusive" rather than guess.
- Map tags to evidence labels: Observed is direct evidence; Inferred and Unknown are never stated as fact.

## What each probe does not prove

| Probe result        | Does not prove                                                                                    | Prove it with                                            |
| ------------------- | ------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| Ping replies        | The service or application is healthy. A failed ping can be ICMP filtering, not an outage         | A real transaction on the service path                   |
| DNS resolves        | The target is reachable or serving                                                                | A connection and a protocol request                      |
| TCP port open       | The application answers correctly; a proxy or load balancer may accept for it                     | A protocol request with expected content                 |
| HTTP 200            | Correct content or fresh data. An error page, cached reply or shallow health check can return 200 | Check body and version; a write-then-read round trip     |
| Process running     | It is serving, not deadlocked, and has its dependencies                                           | An outside-in SLI; queue depth or PSI                    |
| Backup job green    | The data is restorable, complete or inside the RPO                                                | A timed restore with checksum comparison                 |
| Replication healthy | The replica is consistent, current within the RPO, or promotable                                  | Lag measured in time; checksum compare; a failover drill |

## Investigation and review

- Record impact population, first and last observation, UTC timestamps, clock quality, versions and recent changes.
- Follow application -> runtime -> OS -> hypervisor -> storage/network -> hardware.
- Preserve volatile state (logs, counters, `ss`, `dmesg`, journal) before restarting anything.
- Separate saturation, errors, queueing and dependency timeouts. Compare hypotheses with a bounded discriminating test, not by restarting every layer.
- Never convert an observed "offline" status into retirement or an inventory ownership change.
- Post-incident review: blameless, written, within an agreed period. Separate trigger, contributing conditions, detection gaps and missing evidence.
- Actions are specific, owned and dated. Prefer the narrow fix for the failure mechanism and validate it; avoid broad redesign during uncertain diagnosis.

## Patterns and anti-patterns

| Pattern                         | Use when             | Anti-pattern                        | Why it fails                                   |
| ------------------------------- | -------------------- | ----------------------------------- | ---------------------------------------------- |
| Symptom paging tied to SLOs     | Any on-call rotation | Page on every cause metric          | Fatigue; real pages get ignored                |
| Freshness and absence alerts    | Every pipeline       | Alert only on values                | A dead exporter looks like a healthy flat line |
| Low-cardinality labels          | Metrics design       | User or request IDs as labels       | Storage and query cost explode                 |
| Outside-in synthetic probe      | User-facing services | Probe only from the monitoring host | Misses the user's path and DNS                 |
| Fixed incident result shape     | Every diagnosis      | Free-form "probably X" notes        | Guesses travel as facts; handoffs lose state   |
| Mitigate first, then root cause | Active impact        | Debug while users are down          | Impact lasts as long as the investigation      |

## Failure modes and tests

| Failure                        | Symptom                              | Blast radius              | Proving test                                               |
| ------------------------------ | ------------------------------------ | ------------------------- | ---------------------------------------------------------- |
| Pager path broken              | Alert fires, nobody is paged         | Every incident            | End-to-end page test to a phone                            |
| Stale or missing data          | Flat dashboards during an outage     | Detection for that source | Stop an exporter; the absence alert fires                  |
| Collector loss                 | Gap in all signals                   | Whole fleet's visibility  | Kill the collector; buffer replays on recovery             |
| Clock skew across sources      | Events out of order                  | Every timeline            | Compare event and receive times; alert on NTP offset       |
| Retention too short            | Evidence gone before review          | Post-incident and audit   | Query the oldest required sample                           |
| Silent incident handoff        | Two people change the system at once | Incident outcome          | Exercise with a forced commander handoff                   |
| Dashboard green, users failing | Users report what monitoring misses  | Trust in monitoring       | Measure restored user transactions after each intervention |

## Worked example

SLO: 99.9% of requests succeed over 30 days. Error budget = 0.001 x 30 days = 43.2 minutes.

1. Incident: 20% of requests fail for 60 minutes. Burn rate = 0.20 / 0.001 = 200.
2. Budget used = 0.20 x 60 = 12 minutes of full outage, which is 12 / 43.2 = 27.8% of the month's budget.
3. Result shape during the incident:
   - Symptom: 20% HTTP 5xx on checkout since 09:12 UTC.
   - Observed: storage latency p99 rose at 09:11 on one cluster node. Inferred: the app pool waits on that volume. Unknown: whether other volumes are affected.
   - Fault domain: storage, medium confidence. Next check: read-only latency query for the other volumes on that node.
4. Mitigation: move the pool off the node. Impact stops; root cause stays provisional until proved.

## Review checklist

- [ ] SLIs and objectives exist per service before any tool choice.
- [ ] Pages are symptom-based with runbooks; causes go to tickets; noisy alerts are reviewed monthly.
- [ ] Freshness, absence and meta-monitoring alerts cover the pipeline.
- [ ] Retention per class is measured against the agreed window; clocks are monitored; events carry receive time.
- [ ] Incident roles, live document and explicit handoff are rehearsed.
- [ ] Every diagnosis uses the result shape; no probe is treated as proof beyond the table above.
- [ ] Acceptance: pager path, absence alerts, time alignment, owner response, collector recovery, restored user transactions.

## Further reading

Reliability and incidents:
- [G1] [Google SRE book: Managing Incidents](https://sre.google/sre-book/managing-incidents/) - read this for incident roles and the live document (VERIFIED_PRIMARY, checked 2026-10-29).
- [Google SRE book: Postmortem Culture](https://sre.google/sre-book/postmortem-culture/) - read this for blameless review practice.
- [Google SRE workbook: Implementing SLOs][sloimpl] - read this for SLI/SLO selection.
- [Google SRE workbook: Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/) - read this for burn-rate alerting.
- [N1] [NIST SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final) - read this for security incident response (VERIFIED_PRIMARY, checked 2026-10-29).

Metrics and telemetry:
- [P1] [Prometheus storage](https://prometheus.io/docs/prometheus/latest/storage/) - read this for retention flags and durability limits (VERIFIED_PRIMARY, checked 2026-10-29).
- [Prometheus: instrumentation practices][promprac] - read this for label and cardinality discipline.
- [OpenTelemetry documentation](https://opentelemetry.io/docs/) - read this for collector, signals and semantic conventions.

Logs:
- [journald.conf(5)](https://www.freedesktop.org/software/systemd/man/latest/journald.conf.html) - read this for host log persistence and caps.

[sloimpl]: https://sre.google/workbook/implementing-slos/

[promprac]: https://prometheus.io/docs/practices/instrumentation/
