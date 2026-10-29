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
- [Alert routing and honest measurement](#alert-routing-and-honest-measurement)
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
| Alert routing        | An alert is done only when a test fire reaches a human who acts; routing is audited end to end                       | Design rule; [AM1]                     |
| Automatic recovery   | Every watchdog reboot, power cycle or self-heal emits an event to monitoring                                         | Design rule                            |

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

## Alert routing and honest measurement

Monitoring is not done when the rule fires; it is done when the right person receives it and acts.

- Alertmanager deduplicates, groups and routes alerts to receivers; the root route must name a receiver so unmatched alerts still go
  somewhere (VERIFIED_PRIMARY [AM1], checked 2026-10-29). Audit which receiver each critical rule reaches, and test-fire it to a phone.
  Rules that fire into an unwatched receiver are a silent failure: hosts can stay dark for months with "working" alerts.
- Meta-monitor the monitoring: alert on absent targets and on the pipeline itself, not only on values ([Prometheus alerting
  practices][promalert], Metamonitoring).
- Any automatic recovery (hardware watchdog reboot, external power-cycle board, service restart loop) must emit an event. Without it,
  frequent hangs are invisible because the box always comes back.
- Emit "success" and freshness from the stage the consumer reads, and derive age from the data's own upstream timestamp. A timestamp
  written at download time reports fresh while the later build stage fails.
- Instantaneous gauges miss intermittent faults between scrapes. Prefer latched or counting sources (kernel log counts, sticky status
  bits, monotonic error counters) for undervoltage, throttling and receive errors.
- Prove each new series reaches the central store. Collector filters and relabel rules remove data silently: check the deployed
  node_exporter `fs-types-exclude` (the upstream default, checked 2026-10-29, excludes `overlay`, `squashfs` and `erofs` but not
  `tmpfs`; a local override can hide capped RAM mounts) and any `metric_relabel_configs` that discard raw series ([NE1]).
- For a vendor SMART attribute, confirm per model which column (normalised VALUE or RAW) carries life remaining before alerting on it.
- Classify every dark period with boot-time and pattern evidence (power, hang, WAN, switch) before accepting "the link was down".
  Same-clock-time boots and seasonal clustering point to power, not connectivity.
- Before suppressing "log noise", trace what the failing job's success unlocks downstream; an error silenced untraced can be the only
  sign of a broken control chain.
- Sample the actual lines of a new log flood before assigning a known root cause; similar shapes have different causes.

Honest measurement (writes, receive errors, rates):

| Instrument                       | Counts                                  | Misses                                       | Quote against                    |
| -------------------------------- | --------------------------------------- | -------------------------------------------- | -------------------------------- |
| Syscall or fanotify tracer       | write calls on device-backed mounts     | bytes, page-cache coalescing, tmpfs          | ranking only                     |
| Short sampling window (5-10 min) | steady writers                          | daily burst writers moving hundreds of MB    | pair with a 24 h large-file scan |
| Per-process I/O totals (`/proc`) | bytes by processes alive at sample time | short-lived processes (a floor, not a total) | block-device bytes               |
| Block-device bytes, SMART        | what reached the media                  | attribution to a process                     | the denominator for any share    |

- A share quoted against the process sum, not the device total, inflates every percentage. A consistent unattributed band across
  hosts signals instrument loss, not a hidden writer.

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
| Alert routed to nobody         | Rule fires for months; hosts dark    | Every alert on that route | Test-fire each critical rule; a human acknowledges         |
| Self-recovery hides faults     | Box returns; hang rate unknown       | Root cause never found    | Force a recovery; the recovery event reaches monitoring    |
| Freshness from the wrong stage | Fresh timestamp on failed builds     | Consumers of stale data   | Break the last stage; the age alert fires                  |

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
- [ ] Each critical alert test-fired to its receiver; automatic recoveries emit events; freshness comes from the consumer's stage.
- [ ] New mounts and series proven present in the central store; collector excludes and relabel rules reviewed.
- [ ] Rates and shares quoted against the device or system total, with the instrument's blind spots stated.

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
- [AM1] [Alertmanager configuration](https://prometheus.io/docs/alerting/latest/configuration/) - read this for routes, receivers and grouping (VERIFIED_PRIMARY, checked 2026-10-29).
- [Prometheus alerting practices][promalert] - read this for symptom alerting and metamonitoring.
- [NE1] [node_exporter filesystem collector][ne1url] - read this for the default excluded filesystem types (VERIFIED_PRIMARY, checked 2026-10-29).

Logs:
- [journald.conf(5)](https://www.freedesktop.org/software/systemd/man/latest/journald.conf.html) - read this for host log persistence and caps.

[sloimpl]: https://sre.google/workbook/implementing-slos/

[promprac]: https://prometheus.io/docs/practices/instrumentation/

[promalert]: https://prometheus.io/docs/practices/alerting/

[ne1url]: https://github.com/prometheus/node_exporter/blob/master/collector/filesystem_linux.go
