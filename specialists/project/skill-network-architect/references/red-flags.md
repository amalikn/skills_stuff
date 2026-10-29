---
Title: Network red flags
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Network architecture review and incident triage
Last reviewed: 2026-10-29
Summary: Symptom-to-question index of 27 network red flags, each with its usual meaning, first question, data to pull and owning reference module.
---

# Network red flags

## Contents

- [How to use](#how-to-use)
- [Redundancy and physical](#redundancy-and-physical)
- [Routing, WAN and MTU](#routing-wan-and-mtu)
- [Addressing and services](#addressing-and-services)
- [Wireless and radio](#wireless-and-radio)
- [Security, capacity and operations](#security-capacity-and-operations)
- [Remote-site fleets](#remote-site-fleets)
- [Provenance](#provenance)

## How to use

- Use in review and incident modes. Scan the design or the evidence for each signal.
- A red flag is a prompt for a question, not a finding. Ask the first question, pull the data, then decide.
- Record each hit with an evidence label. Route the follow-up to the owning module.
- Owners: [physical](physical-and-campus.md), [routing](routing-and-switching.md), [WAN](wan-and-remote-access.md),
  [addressing](addressing-and-ipv6.md), [services](network-services.md), [wireless](wireless-and-radio.md),
  [security](security-and-segmentation.md), [capacity](capacity-and-resilience.md), [fleet](remote-site-fleet.md),
  [observability](observability-troubleshooting.md).
- In an incident, keep one primary fault domain per hypothesis; one probe never proves a root cause.

## Redundancy and physical

| Signal                                         | Usually means                         | First question                            | Data to pull                             | Owner    |
| ---------------------------------------------- | ------------------------------------- | ----------------------------------------- | ---------------------------------------- | -------- |
| "Redundant" links never traced end to end      | Shared duct, pole, entry or exchange  | Where do the two physical paths converge? | Path records, carrier diversity letters  | physical |
| Single uplink in a "redundant" design          | A drawn pair; one link carries all    | What breaks if this one link fails?       | Topology, LLDP neighbours, port status   | physical |
| Both members of a pair on one UPS or circuit   | One power failure domain              | Which feed is upstream of each UPS?       | Power schematic, PDU and UPS map         | physical |
| Rising CRC or FCS errors on a link that is up  | Dirty optic, bad cable, duplex or EMI | Did errors start with a change or load?   | Error trend, DOM light, changes          | physical |
| PoE devices reboot under load or on PSU loss   | PoE budget exceeded                   | What is the budget with one PSU failed?   | PoE draw per port, PSU state, PD classes | physical |
| OOB path shares the production uplink or power | OOB dies with the failure it serves   | Does OOB work with production down?       | OOB path and power, live test            | physical |

## Routing, WAN and MTU

| Signal                                        | Usually means                               | First question                               | Data to pull                                 | Owner   |
| --------------------------------------------- | ------------------------------------------- | -------------------------------------------- | -------------------------------------------- | ------- |
| Asymmetric routing after failover             | Return path uses the other edge             | Which device holds the return-flow state?    | Traces both ways, routes, firewall state     | routing |
| BGP session flaps                             | Loss, aggressive BFD, MTU or CPU limits     | Do flaps line up with loss, load or timers?  | Session log, BFD, link loss, CPU             | routing |
| Max-prefix warnings from a peer               | Leak upstream or a limit set too low        | Did the peer's prefix count change suddenly? | Prefix counts over time, peer notices        | routing |
| Small packets work, large transfers hang      | MTU blackhole; ICMP Too Big filtered        | What is the smallest MTU on the path?        | DF probes, tunnel stack, ICMP filter rules   | WAN     |
| Failover on interface state only              | Silent path loss goes undetected            | Does detection see loss beyond the CPE?      | Failover config, probe or BFD settings       | WAN     |
| CGNAT-only site with inbound management       | Inbound cannot work; mappings expire        | Who starts the session, and how often?       | WAN address (100.64/10?), keepalive interval | WAN     |
| Throughput far below link rate on a long path | Window smaller than bandwidth-delay product | What are RTT and the TCP window?             | RTT, window scaling, single-flow test        | WAN     |
| One ECMP or LAG member hot, others idle       | Elephant flows or a poor hash               | Which flows dominate that member?            | Member counters, flows, hash inputs          | routing |
| Names fail intermittently, raw IP works       | Address-only ECMP hash pins a resolver to a dead uplink | Which uplink does each fixed target hash to? | Hash policy, per-uplink probes | routing |
| Two equal default routes nobody designed      | Accidental ECMP from two DHCP uplinks       | Is this host meant to be active/backup?      | Routing table, DHCP client config            | routing |
| SR or MPLS proposed without a measured failure | Reopening a baseline on instinct           | Which written trigger fired, with what data? | Baseline decision, test results              | routing |

## Addressing and services

| Signal                                      | Usually means                              | First question                            | Data to pull                               | Owner      |
| ------------------------------------------- | ------------------------------------------ | ----------------------------------------- | ------------------------------------------ | ---------- |
| DHCP pool exhaustion                        | Pool too small, leases too long, or a scan | How many active leases versus pool size?  | Lease table, lease time, new-device rate   | services   |
| Same prefix at two sites about to be joined | Overlap needs translation or renumbering   | Which endpoints actually conflict?        | IPAM export, `just ip-plan` output         | addressing |
| 100.64.0.0/10 used on an enterprise LAN     | Collision with carrier CGNAT space         | Which sites sit behind a CGNAT carrier?   | Upstream addresses per site                | addressing |
| NTP drift or stratum 16                     | Lost or bad sources; too few to outvote    | How many independent sources does it see? | Offset, jitter, stratum, source list       | services   |
| Name resolution fails during WAN loss       | No local resolver or serve-stale           | Where do site clients resolve names?      | Resolver config, DHCP DNS option, WAN log  | services   |
| EAP-TLS or TLS failures start together      | Expiry, wrong clock, CRL/OCSP unreachable  | Is the clock right and the CA reachable?  | Expiry dates, clock offset, CRL/OCSP reach | services   |
| Resolver timeouts while its CPU looks idle  | Single NIC queue or small socket buffer    | Are UDP receive-buffer errors growing?    | `netstat -su`, `ethtool -l`, interrupts per CPU | services |
| Factory-reset device never registers        | Controller discovery (option 43, DNS) lost | Does the edge's current image serve it?   | DHCP options on the site scope, edge image | services   |

## Wireless and radio

| Signal                                    | Usually means                              | First question                                 | Data to pull                                 | Owner    |
| ----------------------------------------- | ------------------------------------------ | ---------------------------------------------- | -------------------------------------------- | -------- |
| DFS events on a backhaul or critical cell | Radar detection forces channel moves       | Is this channel DFS, and what is the fallback? | DFS event log, channel history, link outages | wireless |
| Good RSSI, poor Wi-Fi throughput          | Airtime contention, retries, wide channels | What are channel utilisation and retry rate?   | Utilisation, retries, client mix, width plan | wireless |
| PtP RSL well below prediction             | Misalignment, obstruction or wrong inputs  | Is the measured RSL low at both ends?          | RSL both ends, alignment record, path survey | wireless |
| Modulation drops in rain or at night      | Fade margin too thin; multipath            | What margin does the availability target need? | MCS history, weather, `just link-budget`     | wireless |

## Security, capacity and operations

| Signal                              | Usually means                         | First question                         | Data to pull                          | Owner    |
| ----------------------------------- | ------------------------------------- | -------------------------------------- | ------------------------------------- | -------- |
| Zones named after departments       | Segmentation by org chart, not trust  | Which flows cross each zone, and why?  | Flow logs, zone matrix                | security |
| Allow rules with no owner or expiry | Policy drift and forgotten exceptions | Who needs this flow today?             | Rule hit counts, change records       | security |
| Link sized from a 24-hour average   | Busy hour already near saturation     | What is the busy-hour p95 utilisation? | 5-minute utilisation, busy-hour peaks | capacity |

## Remote-site fleets

| Signal | Usually means | First question | Data to pull | Owner |
| --- | --- | --- | --- | --- |
| Most sites go critical at once, same error | Shared access dependency: certificate or proxy | Is the access path itself healthy? | Certificate expiry, proxy login, error text | security |
| Central ping or SNMP check never passes | Access proxy carries TCP only | Does the probe cross a TCP-only proxy? | Probe path, proxy type | security |
| One IP maps to devices at several sites | Management plans repeat; IP is not identity | Is every key (site, IP) or a device ID? | IPAM namespaces, collector keys | fleet |
| Poll cycle overruns over satellite links | Per-session and per-request RTT cost dominates | What does one session and one read cost? | Session setup time, per-read time, cycle time | fleet |
| Dark periods at the same clock time each day | Power (solar autonomy, battery), not the link | Do boots cluster by time of day and season? | Boot times, battery logs, season | observability |
| Box sends but nothing returns on its one port | Switch or trunk fault mimicking a WAN outage | What do the switch counters show? | Link counters both ways, switch status | observability |
| Alert rules firing with nobody responding | Alert routing never verified | Where does this rule deliver, and who acked it? | Routing tree, receiver log, synthetic alert | observability |
| Health check passes, transfer fails | Probe uses another channel than the workload | Does the probe move a real payload the same way? | Probe definition, workload connections | observability |
| Rollback or safe mode drops the site's devices | Edge served DHCP, DNS or controller discovery | What do site devices take from the edge box? | Service list per edge image, DHCP scope | services |
| Second box in the user path | Two series failure points for one outcome | Does users' internet survive this box failing? | Forwarding path, fail-open test | fleet |
| Placement drawn from a switch MAC table | MAC tables behind wireless bridges mislead | Was this source measured against ground truth? | Install records, AP bridge tables | fleet |
| Remote site authorised by source IP | NAT or multi-carrier address will drift | What happens when the site's egress changes? | ACL hits, egress address history | security |

## Provenance

- Format (signal, meaning, first question, data, owner) adopted from survey item A1 in the
  [similar-skills survey](../docs/research/similar-skills-survey-20261029_1758.md). Wording and entries are this pack's own.
- Each flag points to rules already labelled in the owning module. Do not cite this index as evidence; cite the module's source.
