---
Title: Network observability and troubleshooting
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Network architecture
Last reviewed: 2026-10-29
Summary: >-
  Telemetry design and cross-layer incident diagnosis: a fixed incident result shape, what each probe does not prove, telemetry limits with numbers,
  SLO alerting, failure modes, a worked error-budget example and a review checklist.
---

# Network observability and troubleshooting

## Contents

- [Scope](#scope)
- [Incident result shape](#incident-result-shape)
- [Decision rules](#decision-rules)
- [Probes, alert routing and outages that are not connectivity](#probes-alert-routing-and-outages-that-are-not-connectivity)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

---

## Scope

- Telemetry design (SNMP, gNMI, flow, syslog, probes) and diagnosis of problems that cross devices or layers.
- Incident mode of the [architecture method](architecture-method.md#engagement-modes).
- Host, hypervisor and storage symptoms that mimic network faults: ask skill-systems-architect.
- Controller and report semantics: skill-openwisp (collection, freshness), skill-smc (ansible-wifi reports).

## Incident result shape

Every incident answer returns this shape, in this order. It lets an agent stop early and hand over cleanly.

| Field             | Content                                                                                                      |
| ----------------- | ------------------------------------------------------------------------------------------------------------ |
| Symptom           | what fails, for whom, since when, how measured                                                               |
| Observations      | each tagged Observed (seen now, with source), Inferred (reasoned from observations) or Unknown (not checked) |
| Fault domain      | exactly one most likely domain, with confidence low, medium or high; or "inconclusive"                       |
| Next safest check | one read-only check that would confirm or eliminate that domain                                              |
| Not yet done      | evidence still missing; actions deliberately not taken                                                       |

- When observations conflict, return "inconclusive" rather than a confident guess.
- Preserve evidence before any restart or counter clear.

```text
FAULT-DOMAIN WALK: client to service; stop at the first domain whose check fails

+---------+   +---------+   +---------+   +---------+   +---------+   +---------+   +---------+
| local   |-->| L2      |-->| address |-->| DNS     |-->| routing |-->| policy  |-->| remote  |
| link/RF |   | domain  |   | DHCP/RA |   |         |   | path    |   | FW/NAT  |   | service |
+---------+   +---------+   +---------+   +---------+   +---------+   +---------+   +---------+
Each box is a fault domain. Telemetry or management path is a separate domain; 'inconclusive' is allowed.
```

What each probe does not prove:

| Probe result                            | Does not prove                                          | Check instead                                          |
| --------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------ |
| Ping fails                              | the host is down (ICMP may be filtered or rate-limited) | TCP or UDP connect to the service port                 |
| Ping succeeds                           | the application works, or large packets pass            | service transaction; DF-set probe at real payload size |
| Traceroute hop shows loss or high delay | loss at that router (control plane deprioritises ICMP)  | end-to-end loss from the far side                      |
| DNS resolves                            | the address is reachable or correct for this client     | connect to the answer; compare resolvers               |
| Interface up, no errors                 | traffic is forwarded on the right VLAN or VRF           | MAC and ARP/ND tables, a real flow                     |
| Graph shows zero                        | traffic was zero (collection gap looks the same)        | collector freshness and sequence gaps                  |
| Device unreachable over the tunnel      | the site is down                                        | an independent liveness signal for the site            |
| Slow first byte                         | network latency (the app may be slow)                   | compare TCP connect time with first-byte time          |

## Decision rules

Diagnosis:
- Record symptom, first and last occurrence, affected population, window, expected behaviour and recent changes.
- Split the population before the path. All sites in one minute points at a shared dependency (collector, DNS, time, controller).
- One site, all metrics points at the site uplink or its management path. One metric, all sites points at the exporter or query.
- Capture only the relevant flow, with permission, rate and time limits.
- Change one causal variable, then repeat the same measurement.

```text
TELEMETRY PIPELINE: each hop can turn 'no data' into 'zero' or 'down' (X = where data is lost)

+-------------+   +-------------+   +-------------+   +-------------+   +-------------+   +-------------+
| device      |-->| transport   |-->| collector   |-->| store       |-->| query/alert |-->| human       |
+-------------+   +-------------+   +-------------+   +-------------+   +-------------+   +-------------+
       X                 X                 X                 X                 X                 X
counter reset     UDP loss          queue backlog     retention         rate window       alert fatigue
sampling          ACL, NAT, skew    parse drop        downsampling      staleness         wrong panel
```

Telemetry limits (each VERIFIED_PRIMARY, checked 2026-10-29, sources in Further reading):
- SNMP: 64-bit octet counters MUST exist above 20 Mbit/s, packet counters at 650 Mbit/s (RFC 2863 s3.1.6).
  - 32-bit wrap time = 2^32 x 8 / rate: 34 s at 1 Gbit/s; 344 s at 100 Mbit/s. Use ifHC* objects and ifCounterDiscontinuityTime.
- gNMI Subscribe STREAM modes: ON_CHANGE, SAMPLE, TARGET_DEFINED. A target that cannot meet sample_interval must reject it. ON_CHANGE for state, SAMPLE for counters.
- IPFIX: SCTP is mandatory to implement; UDP export is allowed but loss is silent (RFC 7011 s10). Count sequence gaps at the collector.
- sFlow v5: 1-in-N packet sampling; estimated total = samples x N. Small flows over short windows are unreliable.
  - The error bound "196 x sqrt(1/c) percent at 95%" for c samples is UNVERIFIED (an image on the sFlow page; consistent with its examples).

Measurement:
- Rate = delta(counter) / delta(t). Discard a negative delta as a reset.
- A 5-minute average hides microbursts. Queue drops with low average utilisation are the signature.
- Report latency as p50/p95/p99, never a mean. Percentiles cannot be averaged across devices; aggregate histogram buckets.
- Record timezone and clock source. Clock skew invents a false order of events.
- State whether an SLI is active (probe traffic, own path) or passive (real traffic). RFC 7799 defines both.
- USE per resource (utilisation, saturation, errors). RED per service (rate, errors, duration).

SLO alerting (SRE workbook, VERIFIED_PRIMARY):
- Error budget = (1 - SLO) x window. 99.9% over 30 days = 43.2 min.
- Burn rate = error ratio / (1 - SLO). Page at 14.4x over 1 h (2% of a 30-day budget); ticket on slow burn.
- Alert on collector freshness separately from device health.

## Probes, alert routing and outages that are not connectivity

Probe on the workload's real channel:
- A probe proves only the channel it exercises. FTP moves data on a separate data connection from the control connection
  (VERIFIED_PRIMARY [RFC 959](https://www.rfc-editor.org/rfc/rfc959.html)), so a header-only request that uses the control connection can pass while every
  transfer fails. Probe with a real payload over every connection the workload opens; prefer a single-connection transport (rsync over SSH, HTTPS) for unattended fleet feeds.
- Monitor the user-facing function, not reachability: portal HTTP status, DNS resolution through the site resolver, internet reachability per uplink.
  Black-box probers cover HTTP, HTTPS, DNS, TCP, ICMP and gRPC (VERIFIED_PRIMARY [blackbox exporter](https://github.com/prometheus/blackbox_exporter)).
  Black-box monitoring is symptom-oriented and shows active problems (VERIFIED_PRIMARY [SRE book ch. 6](https://sre.google/sre-book/monitoring-distributed-systems/)).
- An accepted push is not stored data. Verify that the stored value exists after a write, and call a check done only when the result stays
  correct through the next check interval (UNVERIFIED, field observation).
- Names lie: a role called "URL capture" that records DNS queries yields domains, not URLs, and misses clients that use DoH
  (VERIFIED_PRIMARY [RFC 8484](https://www.rfc-editor.org/rfc/rfc8484.html)). Per-application reporting on a backhaul needs flow export or
  classification designed in ([RFC 7011](https://www.rfc-editor.org/rfc/rfc7011.html)).

Alert routing must be verified:
- An alert rule that fires is not an alert delivered. Routing trees and receivers are separate configuration (VERIFIED_PRIMARY
  [Alertmanager configuration](https://prometheus.io/docs/alerting/latest/configuration/)). A misrouted rule can fire for months with nobody told.
- Acceptance test: a synthetic alert per route reaches a named person who acknowledges it; repeat after every routing change. Alert on absent
  targets (a host that stopped reporting), not only on bad values.

Outages that are not connectivity:

| Pattern in the evidence | Likely class | Check |
| ----------------------- | ------------ | ----- |
| Boots at nearly the same clock time on many days, more in winter | Power: solar or battery autonomy runs out before dawn | Boot-time series against sunrise and season; battery logs |
| Most targets fail together with the same error | Shared dependency: access certificate, proxy, collector, DNS | The access path first (certificate validity, proxy login) |
| Box transmits but nothing returns on its only port | Switch or trunk fault, not the WAN | Link counters both ways on the box and on the switch |
| Kernel logs undervoltage all day; alarm metric reads 0 | Undersized supply; the gauge is not latched between scrapes | Latched flags and kernel logs, not an instantaneous gauge |
| A self-heal action every few minutes on a degraded link | The remediation causes the flap | Self-heal with backoff, a cap and an event record |

- Classify every dark period with boot-time and pattern evidence (power, hang, WAN, switch) before filing it as a link outage (UNVERIFIED, field method).

## Patterns and anti-patterns

| Situation                              | Do                                             | Avoid                              | Why                                        |
| -------------------------------------- | ---------------------------------------------- | ---------------------------------- | ------------------------------------------ |
| Many sites go grey at once             | check collector, DNS, time, controller first   | open a ticket per site             | one shared dependency explains all of them |
| Remote site behind a tunnel or bastion | carry a second, independent liveness signal    | treat lost management as site down | the paths fail separately                  |
| Busy link with 5-min polling           | 64-bit counters, shorter interval or streaming | 32-bit counters                    | a wrap reads as a dip or a reset           |
| Top talkers from sampled flow          | widen the window until samples are many        | trusting a 1-minute top list       | sampling error dominates small counts      |
| Telemetry disagrees with inventory     | raise a finding to the intent owner            | overwrite intent from telemetry    | observation is not ownership               |
| Service check for a site function      | probe the real channel with a payload          | ping or a control-channel check    | the workload channel fails unseen          |
| New or changed alert route             | fire a synthetic alert to a person             | trust that the rule fires          | firing is not delivery                     |

## Failure modes and tests

| Failure                            | Signal                                        | Test                                                                |
| ---------------------------------- | --------------------------------------------- | ------------------------------------------------------------------- |
| Collector stalls; graphs show zero | freshness age rising, no sequence gaps logged | stop the collector in lab; a freshness alert must fire              |
| Counter wrap or reset              | negative delta, sudden drop                   | replay a wrapping counter; the pipeline must discard it             |
| UDP export loss                    | IPFIX sequence gaps                           | drop 5% of export packets in lab; gaps must be counted              |
| Clock skew between sources         | events out of order across devices            | skew one device by 60 s in lab; the time-quality check must flag it |
| Probe path differs from user path  | probe green while users fail                  | compare probe route with user route under failover                  |
| Alert misrouted                    | rule firing, nobody acknowledged              | synthetic alert per route; a named person acknowledges it           |
| Power outage filed as link outage  | boots cluster at one clock time, seasonal     | correlate boot times with time of day and season                    |

## Worked example

Service SLO 99.9% over 30 days. Error budget = 0.001 x 43,200 min = 43.2 bad minutes.

| Event                 | Arithmetic            | Budget used    |
| --------------------- | --------------------- | -------------- |
| Full outage, day 3    | 10 min x 100% errors  | 10.0 min       |
| Partial errors, day 9 | 120 min x 0.5% errors | 0.6 min        |
| Total used            | 10.0 + 0.6            | 10.6 min (25%) |
| Left                  | 43.2 - 10.6           | 32.6 min       |

- Day 9 burn rate = 0.005 / 0.001 = 5x. Below the 14.4x page threshold over 1 h: a ticket, not a page.
- The same link polled at 300 s with 32-bit octet counters at 100 Mbit/s: wrap every 344 s. One wrap per poll is near-certain at peak.

Incident answer for a site reported "down" in monitoring:

| Field             | Value                                                                                                         |
| ----------------- | ------------------------------------------------------------------------------------------------------------- |
| Symptom           | site 14 grey in monitoring since 02:10 UTC; no user reports                                                   |
| Observations      | Observed: tunnel to site 14 down. Observed: site POS transactions logged at 02:30. Unknown: site WAN counters |
| Fault domain      | management path (tunnel), confidence medium                                                                   |
| Next safest check | read the tunnel peer's status on the hub; no change to the site                                               |
| Not yet done      | no site reboot; no ticket to the carrier                                                                      |

## Review checklist

- [ ] Incident answers use the result shape; each observation tagged
- [ ] One fault domain with confidence, or "inconclusive"
- [ ] No conclusion rests on a single probe (see the table above)
- [ ] 64-bit counters on links above 20 Mbit/s; poll interval below wrap time
- [ ] Collector freshness alerted separately from device health
- [ ] Latency reported as percentiles from histograms
- [ ] Clock source and timezone recorded for every evidence source
- [ ] SLO, window, budget and burn thresholds written down
- [ ] Each probe exercises the workload's real channel with a payload
- [ ] Every alert route proven by a synthetic alert acknowledged by a person
- [ ] Dark periods classified (power, hang, WAN, switch) before blaming the link

## Further reading

All links resolved 2026-10-29.

SLOs and alerting:
- [SRE book: Monitoring distributed systems](https://sre.google/sre-book/monitoring-distributed-systems/): golden signals; symptom versus cause.
- [SRE book: Service level objectives](https://sre.google/sre-book/service-level-objectives/): choosing SLIs; percentiles over means.
- [SRE workbook: Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/): multi-window, multi-burn-rate alerts.
- [Alertmanager configuration](https://prometheus.io/docs/alerting/latest/configuration/): routing trees, receivers and inhibition.
- [Prometheus: Histograms and summaries](https://prometheus.io/docs/practices/histograms/): why quantiles cannot be averaged.

Methods:
- [USE method](https://www.brendangregg.com/usemethod.html): utilisation, saturation, errors per resource.
- [RED method](https://grafana.com/blog/2018/08/02/the-red-method-how-to-instrument-your-services/): rate, errors, duration per service.

Network telemetry protocols:
- [RFC 2863 Interfaces MIB](https://www.rfc-editor.org/rfc/rfc2863.html): counter widths and discontinuities.
- [gNMI specification](https://github.com/openconfig/reference/blob/master/rpc/gnmi/gnmi-specification.md): subscription modes.
- [RFC 7011 IPFIX](https://www.rfc-editor.org/rfc/rfc7011.html) and [RFC 3954 NetFlow v9](https://www.rfc-editor.org/rfc/rfc3954.html): templates, transport, export loss.
- [sFlow v5](https://sflow.org/sflow_version_5.txt) and [sFlow sampling basics](https://sflow.org/packetSamplingBasics/index.htm): sampled-flow accuracy.
- [RFC 5424 Syslog](https://www.rfc-editor.org/rfc/rfc5424.html): structured fields and timestamps.
- [RFC 7799 Active and passive measurement](https://www.rfc-editor.org/rfc/rfc7799.html): what a probe or counter measures.
- [wshobson connectivity-triage](https://github.com/wshobson/agents/blob/main/plugins/incident-response/skills/connectivity-triage/SKILL.md): idea source for the result shape (MIT; paraphrased).
