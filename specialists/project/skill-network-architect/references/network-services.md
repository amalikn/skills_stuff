---
Title: DNS, DHCP, time, AAA and service delivery
Category: domain-reference
Status: current
Authority: authored-guidance
Scope: Network architecture
Last reviewed: 2026-10-29
Summary: DNS, DHCP, time, AAA, PKI and load-balancing decision rules, dependency order, failure modes, a resolver availability worked example and a review checklist.
---

# DNS, DHCP, time, AAA and service delivery

## Contents

- [Scope](#scope)
- [Decision rules](#decision-rules)
- [Dependency order](#dependency-order)
- [Resolver receive path](#resolver-receive-path)
- [Patterns and anti-patterns](#patterns-and-anti-patterns)
- [Failure modes and tests](#failure-modes-and-tests)
- [Worked example](#worked-example)
- [Review checklist](#review-checklist)
- [Further reading](#further-reading)

## Scope

- Decides: placement, redundancy, transport and failure behaviour of DNS, DHCP/RA, time, AAA, PKI reachability and load balancing.
- Per service record: dependencies, state, authoritative writer, failover, backup, authentication, reachability, behaviour in WAN or identity failure.
- Network owns reachability and relay; skill-systems-architect owns the servers, replication, key protection, backup and OS lifecycle.
- Hands to [addressing-and-ipv6](addressing-and-ipv6.md) (scopes, IPAM) and [security-and-segmentation](security-and-segmentation.md) (802.1X, RADIUS paths).

## Decision rules

All VERIFIED_PRIMARY rows checked 2026-10-29.

| Rule                                                          | Value or threshold                                                      | Evidence                                   |
| ------------------------------------------------------------- | ----------------------------------------------------------------------- | ------------------------------------------ |
| At least two recursive resolvers in different failure domains | Clients get both; remote sites run a local cache                        | UNVERIFIED (judgement)                     |
| Serve-stale at satellite or radio sites                       | Answer from expired cache when upstream is down                         | VERIFIED_PRIMARY [RFC 8767][rfc8767]       |
| Negative caching                                              | Know its duration before declaring a fix complete                       | VERIFIED_PRIMARY [RFC 9520][rfc9520]       |
| DNS over TCP is mandatory                                     | Servers and forwarders MUST support it; UDP-only firewalls break DNSSEC | VERIFIED_PRIMARY [RFC 9210][rfc9210] (BCP) |
| DoT                                                           | TCP/853                                                                 | VERIFIED_PRIMARY [RFC 7858][rfc7858]       |
| DoH                                                           | Over HTTPS; built-in client DoH bypasses site resolvers                 | VERIFIED_PRIMARY [RFC 8484][rfc8484]       |
| DoQ                                                           | UDP/853                                                                 | VERIFIED_PRIMARY [RFC 9250][rfc9250]       |
| Lower TTL one old-TTL ahead of cutover                        | Lowering it at cutover does not purge caches                            | UNVERIFIED (arithmetic)                    |
| Relay to two DHCP servers                                     | Failover pair with defined partner-down behaviour                       | UNVERIFIED (judgement)                     |
| Lease time vs outage                                          | Longer than the longest server/WAN outage, or DHCP on site              | UNVERIFIED (judgement)                     |
| Option 82                                                     | Circuit ID (sub 1), Remote ID (sub 2); trusted relays only              | VERIFIED_PRIMARY [RFC 3046][rfc3046]       |
| DHCPv6                                                        | RFC 8415 obsoletes 3315/3633/3736; relays use Interface-Id              | VERIFIED_PRIMARY [RFC 8415][rfc8415]       |
| Portable IPv6 baseline                                        | SLAAC plus RA DNS (RDNSS)                                               | VERIFIED_PRIMARY [RFC 8106][rfc8106]       |
| Android stateful DHCPv6                                       | Not supported                                                           | UNVERIFIED (confirm current platform docs) |
| NTP strata                                                    | 1 = reference clock; +1 per hop; 16 = unsynchronised                    | VERIFIED_PRIMARY [RFC 5905][rfc5905]       |
| NTP sources per client                                        | At least four, independent and diverse; two cannot outvote              | VERIFIED_PRIMARY [RFC 8633][rfc8633] (BCP 223) |
| NTS                                                           | Key establishment TCP/4460; needs roughly-right time first              | VERIFIED_PRIMARY [RFC 8915][rfc8915]       |
| PTP                                                           | Sub-microsecond only; G.8275.1 needs timing support every hop           | VERIFIED_PRIMARY [IEEE 1588][ieee1588], [G.8275.1][g8275] |
| RADIUS over UDP is forgeable on path                          | CVE-2024-3596 (Blast-RADIUS); use TLS or a protected path               | VERIFIED_PRIMARY [NVD][nvd]                |
| Vendor Message-Authenticator fixes                            | Apply per product                                                       | UNVERIFIED (per product)                   |
| RadSec                                                        | TCP/2083, Experimental                                                  | VERIFIED_PRIMARY [RFC 6614][rfc6614]       |
| RADIUS/1.1                                                    | Removes MD5 inside TLS; Experimental                                    | VERIFIED_PRIMARY [RFC 9765][rfc9765]       |
| radiusdtls-bis                                                | Proposed Standard in IESG evaluation; would obsolete 6614 and 7360      | VERIFIED_PRIMARY [datatracker][radext]     |
| CoA / Disconnect                                              | Change authorisation mid-session                                        | VERIFIED_PRIMARY [RFC 5176][rfc5176]       |
| Option 43 (vendor-specific)                                   | Opaque, vendor-defined; often points devices at a controller            | VERIFIED_PRIMARY [RFC 2132][rfc2132] s8.4  |
| A hot resolver: tune the receive path before adding CPU       | Buffers, then NIC queues and IRQ spread, then CPU                       | See [Resolver receive path](#resolver-receive-path) |

- Untrusted ports drop client-supplied option 82 (DHCP snooping). Align scopes, relays and RA/DHCPv6 policy with IPAM ownership.
- Monitor NTP offset, jitter, reachability and stratum, not "service running". Use NTP unless an app states a PTP need.
- At a remote site a local GNSS-disciplined or holdover server beats two upstream servers over satellite.
- AAA: define authorisation granularity, accounting retention, device identity, revocation; plan sealed, audited break-glass access.
- Certificate issuance, renewal, expiry and CRL/OCSP reachability must be observable and recoverable.
- Load balancing: separate DNS steering, L4 distribution and L7 proxying. Match health-check depth to real readiness.
- Check proxy timeouts and connection pools before blaming routing. A passing TCP check can hide a failing transaction.

## Dependency order

```text
Service bootstrap order: a failed box breaks everything to its right
+-------+   +------+   +-----------+   +-----+   +-----+   +-----------+   +-----+   +------------+
| power |-->| link |-->| DHCP / RA |-->| DNS |-->| NTP |-->| PKI / TLS |-->| AAA |-->| apps, logs |
+-------+   +------+   +-----------+   +-----+   +-----+   +-----------+   +-----+   +------------+
wrong time fails TLS, EAP-TLS and Kerberos even when DNS works
```

- A DNS name used to reach the recovery platform is a bootstrap dependency. Keep an address-literal or OOB recovery path.

```text
Remote site during WAN loss: what must keep working locally (X = failed WAN)
+--------------------------------------+
| site (must work offline)             |                +------------------------+
| DHCP, caching resolver (serve-stale) |                | central services       |
| local NTP or GNSS source             |<---- WAN --X-->| authoritative DNS, AAA |
| AAA fallback, break-glass account    |                | PKI, monitoring        |
+--------------------------------------+                +------------------------+
```

## Resolver receive path

A busy recursive resolver that looks CPU-bound is often a single receive path: one NIC queue, one interrupt on one CPU,
and UDP datagrams dropped at a full socket buffer while the other cores idle. Adding vCPUs does not reach that path.

```text
RESOLVER RECEIVE PATH: check left to right; buy CPU only at the last box
+---------------+   +----------------+   +----------------+   +----------------+   +-----------+
| pool balance  |-->| UDP socket     |-->| NIC queues     |-->| IRQ, softirq   |-->| more CPU  |
| per member    |   | buffer errors  |   | (RSS)          |   | spread per CPU |   | last rung |
+---------------+   +----------------+   +----------------+   +----------------+   +-----------+
 one heavy NAT       rmem_default,        1 combined queue     /proc/interrupts,    only when the
 source on one       rmem_max,            = one CPU takes      softnet_stat         daemon is busy
 member              udp_rmem_min         every interrupt      squeeze              on many threads
```

| Step | Check | Lever | Evidence |
| ---- | ----- | ----- | -------- |
| 1. Distribution | Per-member query rate behind the balancer | Fix hashing or stickiness first; one CGNAT or satellite source can land on one member | UNVERIFIED (method) |
| 2. Socket buffer | UDP receive errors growing (`netstat -su`) | Raise `rmem_*`, `udp_rmem_min` in a sysctl drop-in; watch growth | VERIFIED_PRIMARY [net][k-net], [ip-sysctl][k-ipsysctl] |
| 3. NIC queues | `ethtool -l` shows one combined queue | Enable multiqueue so RSS spreads flows across queues and CPUs | VERIFIED_PRIMARY [kernel scaling][k-scaling] |
| 4. IRQ spread | `/proc/interrupts` shows the NIC interrupt on one CPU; softirq time squeeze | Queue-to-CPU affinity, or RPS for a single-queue device | VERIFIED_PRIMARY [kernel scaling][k-scaling] |
| 5. CPU | Daemon busy across many worker threads, not one ingress socket | Add CPU only now | UNVERIFIED (design method) |

- Whether a running resolver picks up a larger socket buffer without a restart depends on how the daemon sets `SO_RCVBUF`. Check that version's documentation before claiming the effect.
- On a virtual machine the queue count is a hypervisor setting, not a guest setting. In libvirt the `<interface>` `queues` attribute sets
  virtio-net multiqueue and needs `<model type='virtio'/>` (VERIFIED_PRIMARY [libvirt domain XML][libvirt-fd]). A changed definition takes effect
  at the next boot of the domain (VERIFIED_PRIMARY [virsh][virsh]). Field experience: a reboot from inside the guest keeps the running process,
  so plan a full shutdown and start, a maintenance window and a saved copy of the old definition for rollback (UNVERIFIED).
- The guest may also need `ethtool -L <if> combined N` to use the queues (VERIFIED_SECONDARY [KVM multiqueue page][kvm-mq]).
- Template packet-heavy VMs (resolvers, gateways, collectors) with explicit multiqueue and a single-socket CPU topology from the start.

## Patterns and anti-patterns

| Pattern                                 | Use when                     | Anti-pattern                              | Why it fails                               |
| --------------------------------------- | ---------------------------- | ----------------------------------------- | ------------------------------------------ |
| Local caching resolver with serve-stale | Satellite or radio sites     | Clients query a central resolver over WAN | WAN loss stops all name resolution         |
| Four diverse NTP sources                | Any site                     | Two upstream servers                      | Two cannot outvote a bad source            |
| RADIUS inside TLS or a protected path   | Any AAA over shared networks | RADIUS/UDP across the WAN                 | On-path forgery (Blast-RADIUS)             |
| DNS allowed on UDP and TCP 53           | Every firewall               | UDP-only DNS rules                        | Large answers and DNSSEC break             |
| Readiness-depth health checks           | Load-balanced services       | TCP port check only                       | Traffic sent to broken backends            |
| Decided DoH policy                      | Managed clients              | Ignore browser DoH                        | Split-horizon names and filtering bypassed |
| Receive path tuned before CPU           | Hot resolver, idle cores     | Add vCPUs first                           | Single queue keeps every packet on one CPU |
| Edge recovery image keeps DHCP and DNS  | Site devices lease from the edge box | Rollback image without site services | Rollback takes the site management plane down |

## Failure modes and tests

| Failure                                    | Symptom                               | Blast radius                | Test that proves the design handles it             |
| ------------------------------------------ | ------------------------------------- | --------------------------- | -------------------------------------------------- |
| Upstream DNS unreachable                   | Names fail after TTL expiry           | Site or all clients         | Cut upstream; serve-stale keeps answering          |
| DNS over TCP blocked                       | Large or DNSSEC answers fail          | Some names                  | Query with TCP forced; must succeed                |
| DHCP server or relay loss                  | New clients get no lease              | Segment or site             | Stop one server; leases still issue                |
| Time source loss or false ticker           | Offset drift; TLS and Kerberos fail   | Every authenticated service | Remove a source; feed a bad one; client rejects it |
| NTS bootstrap without time                 | NTS-KE certificate check fails        | Clients at cold start       | Cold-boot with a wrong clock; recovery path works  |
| AAA unreachable                            | No 802.1X or admin login              | Site                        | Cut AAA path; fallback policy and break-glass work |
| Certificate expiry or CRL/OCSP unreachable | EAP-TLS and TLS fail                  | All certificate users       | Expire a test certificate; alert fires before      |
| Rogue DHCP server                          | Clients get a bad gateway or resolver | Segment                     | Start a rogue server in lab; snooping blocks it    |
| Resolver receive drops                     | Timeouts while CPU looks idle         | Every client of the member  | Load test; receive-buffer errors stay flat         |
| Controller discovery lost after rollback   | Factory-default devices find nothing  | New and reset devices       | Reset a device in a rollback drill; it registers   |

## Worked example

Question: do two site resolvers meet 99.9% name-resolution availability, and what if both run on one host?

Inputs (illustrative): site switch 0.9995; each resolver 0.995; shared hypervisor host 0.998. Target 0.999.

| Model                                           | Command                                   | Result                         |
| ----------------------------------------------- | ----------------------------------------- | ------------------------------ |
| switch, then resolvers A and B in parallel      | `just availability dns-avail.json`        | 0.999475; 276 min/yr; exit 0   |
| same, both resolvers on one host (series block) | `just availability dns-avail-shared.json` | 0.997476; 1,327 min/yr; exit 1 |

- Hand check, parallel pair: 1 - 0.005^2 = 0.999975; x 0.9995 = 0.999475. Matches.
- The shared host costs ~1,050 min/yr. Put resolvers on separate hosts and power.
- DHCP lease check: worst measured WAN outage 6 h with central DHCP means leases must exceed 6 h. Better: DHCP on site.

## Review checklist

- [ ] Dependency chain drawn; bootstrap path avoids names that need the failed service.
- [ ] Two resolvers in separate failure domains; serve-stale at remote sites; TCP 53 allowed.
- [ ] DoH policy decided for managed clients.
- [ ] DHCP: two servers or on site; lease longer than worst outage; snooping and option 82 trust set.
- [ ] IPv6: SLAAC plus RDNSS baseline; DHCPv6 only where clients support it.
- [ ] Four or more diverse NTP sources; offset and stratum monitored.
- [ ] RADIUS protected (TLS or protected path); break-glass sealed and audited.
- [ ] Certificate expiry and revocation reachability monitored.
- [ ] `just availability` run for the resolver, DHCP and AAA designs, with shared hosts as series blocks.
- [ ] Resolver VMs: per-member load even, receive-buffer errors flat, multiqueue set in the hypervisor definition, IRQs spread.
- [ ] Every service site devices take from an edge box (DHCP, DNS, option 43 controller discovery, NTP) survives its rollback image.

## Further reading

DNS:

- [RFC 9210][rfc9210]: why DNS over TCP is mandatory operationally.
- [RFC 8767][rfc8767]: serve-stale behaviour and limits.
- [NIST SP 800-81 Rev. 3](https://csrc.nist.gov/pubs/sp/800/81/r3/final): secure DNS deployment guide (March 2026).

DHCP and address configuration:

- [RFC 8415][rfc8415]: DHCPv6 client, relay and prefix delegation.
- [RFC 3046][rfc3046]: relay agent option 82 semantics and trust.

Time:

- [RFC 8633][rfc8633]: NTP deployment best practice (source count, diversity, monitoring).
- [RFC 8915][rfc8915]: read before enabling NTS.
- [ITU-T G.8275.1][g8275]: when an application needs PTP phase and time.

Host receive path:

- [Linux kernel: scaling in the networking stack][k-scaling]: RSS, RPS, RFS and XPS, and when each applies.
- [libvirt domain XML: network interfaces][libvirt-fd]: the `queues` attribute for virtio-net multiqueue.

AAA:

- [RFC 6614][rfc6614] and [RFC 9765][rfc9765]: RADIUS over TLS and the MD5-free RADIUS/1.1.
- [radext RADIUS/(D)TLS bis draft][radext]: the standards-track replacement.

[rfc2132]: https://www.rfc-editor.org/rfc/rfc2132.html
[rfc3046]: https://www.rfc-editor.org/rfc/rfc3046.html
[rfc5176]: https://www.rfc-editor.org/rfc/rfc5176.html
[rfc5905]: https://www.rfc-editor.org/rfc/rfc5905.html
[rfc6614]: https://www.rfc-editor.org/rfc/rfc6614.html
[rfc7858]: https://www.rfc-editor.org/rfc/rfc7858.html
[rfc8106]: https://www.rfc-editor.org/rfc/rfc8106.html
[rfc8415]: https://www.rfc-editor.org/rfc/rfc8415.html
[rfc8484]: https://www.rfc-editor.org/rfc/rfc8484.html
[rfc8633]: https://www.rfc-editor.org/rfc/rfc8633.html
[rfc8767]: https://www.rfc-editor.org/rfc/rfc8767.html
[rfc8915]: https://www.rfc-editor.org/rfc/rfc8915.html
[rfc9210]: https://www.rfc-editor.org/rfc/rfc9210.html
[rfc9250]: https://www.rfc-editor.org/rfc/rfc9250.html
[rfc9520]: https://www.rfc-editor.org/rfc/rfc9520.html
[rfc9765]: https://www.rfc-editor.org/rfc/rfc9765.html
[nvd]: https://nvd.nist.gov/vuln/detail/CVE-2024-3596
[radext]: https://datatracker.ietf.org/doc/draft-ietf-radext-radiusdtls-bis/
[ieee1588]: https://standards.ieee.org/ieee/1588/6825/
[g8275]: https://www.itu.int/rec/T-REC-G.8275.1/en
[k-scaling]: https://docs.kernel.org/networking/scaling.html
[k-ipsysctl]: https://docs.kernel.org/networking/ip-sysctl.html
[k-net]: https://docs.kernel.org/admin-guide/sysctl/net.html
[libvirt-fd]: https://libvirt.org/formatdomain.html
[virsh]: https://libvirt.org/manpages/virsh.html
[kvm-mq]: https://www.linux-kvm.org/page/Multiqueue
