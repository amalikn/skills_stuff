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

A busy recursive resolver that looks CPU-bound is often a single receive path: one NIC queue, one interrupt on one CPU, and UDP datagrams dropped at a full socket buffer while the other cores idle.
Adding vCPUs does not reach that path.

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

| Step             | Check                                                               | Lever                                                                     | Evidence                        |
| ---------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------- | ------------------------------- |
| 1. Distribution  | Per-member query rate behind the balancer                           | Fix hashing or stickiness first; one CGNAT or satellite source can land   | UNVERIFIED (method)             |
|                  |                                                                     |   on one member                                                           |                                 |
| 2. Socket buffer | UDP receive errors growing (`netstat -su`)                          | Raise `rmem_*`, `udp_rmem_min` in a sysctl drop-in; watch growth          | VERIFIED_PRIMARY [net][k-net], [ip-sysctl][k-ipsysctl] |
| 3. NIC queues    | `ethtool -l` shows one combined queue                               | Enable multiqueue so RSS spreads flows across queues and CPUs             | VERIFIED_PRIMARY [kernel scaling][k-scaling] |
| 4. IRQ spread    | `/proc/interrupts` shows the NIC interrupt on one CPU; softirq      | Queue-to-CPU affinity, or RPS for a single-queue device                   | VERIFIED_PRIMARY [kernel scaling][k-scaling] |
|                  |   time squeeze                                                      |                                                                           |                                 |
| 5. CPU           | Daemon busy across many worker threads, not one ingress socket      | Add CPU only now                                                          | UNVERIFIED (design method)      |

- Whether a running resolver picks up a larger socket buffer without a restart depends on how the daemon sets `SO_RCVBUF`. Check that version's documentation before claiming the effect.
- On a virtual machine the queue count is a hypervisor setting, not a guest setting. In libvirt the `<interface>` `queues` attribute sets virtio-net multiqueue and needs `<model type='virtio'/>`
  (VERIFIED_PRIMARY [libvirt domain XML][libvirt-fd]). A changed definition takes effect at the next boot of the domain (VERIFIED_PRIMARY [virsh][virsh]). Field experience: a reboot from inside the
  guest keeps the running process, so plan a full shutdown and start, a maintenance window and a saved copy of the old definition for rollback (UNVERIFIED).
- The guest may also need `ethtool -L <if> combined N` to use the queues (VERIFIED_SECONDARY [KVM multiqueue page][kvm-mq]).
- Template packet-heavy VMs (resolvers, gateways, collectors) with explicit multiqueue and a single-socket CPU topology from the start.

## Patterns and anti-patterns

| Pattern                                 | Use when                             | Anti-pattern                              | Why it fails                                  |
| --------------------------------------- | ------------------------------------ | ----------------------------------------- | --------------------------------------------- |
| Local caching resolver with serve-stale | Satellite or radio sites             | Clients query a central resolver over WAN | WAN loss stops all name resolution            |
| Four diverse NTP sources                | Any site                             | Two upstream servers                      | Two cannot outvote a bad source               |
| RADIUS inside TLS or a protected path   | Any AAA over shared networks         | RADIUS/UDP across the WAN                 | On-path forgery (Blast-RADIUS)                |
| DNS allowed on UDP and TCP 53           | Every firewall                       | UDP-only DNS rules                        | Large answers and DNSSEC break                |
| Readiness-depth health checks           | Load-balanced services               | TCP port check only                       | Traffic sent to broken backends               |
| Decided DoH policy                      | Managed clients                      | Ignore browser DoH                        | Split-horizon names and filtering bypassed    |
| Receive path tuned before CPU           | Hot resolver, idle cores             | Add vCPUs first                           | Single queue keeps every packet on one CPU    |
| Edge recovery image keeps DHCP and DNS  | Site devices lease from the edge box | Rollback image without site services      | Rollback takes the site management plane down |

### Reaching a home or lab service from a phone with passkeys

> **Learned 2026-11-23** · LAN exposure of a WebAuthn sign-in · VERIFIED_PRIMARY (W3C WebAuthn L3 RP ID validation; Apple support 102390 and
> 103769; OpenSSL refuses a leaf outside the root's name constraint, verify error 47) · Source: continuum FR-510 options record and spikes/fr-510-lan-passkey (DL-196) · Falsifier: a browser that
> creates a passkey on an IP-address origin

- A passkey cannot be bound to an IP address (WebAuthn rejects an effective domain that is not a valid domain) and needs HTTPS (only localhost is exempt), so a LAN service signed into with passkeys
  needs a name. Without local DNS records, mDNS gives one (`<host>.local`).
- The certificate: a private root with an X.509 name constraint permitting only that host, so a leaked root key cannot impersonate other sites; the leaf within Apple's rules (DNS name in the SAN,
  serverAuth EKU, at most 825 days, SHA-2). iOS trusts a manually installed root only after Settings > General > About > Certificate Trust Settings; whether iOS enforces name constraints is to be
  tested with a deliberate out-of-constraint leaf.
- Getting the root onto the phone is a step of its own (Learned 2026-11-24, continuum FR-510 rerun, VERIFIED_PRIMARY on the device): serve only the public root certificate over plain HTTP on the LAN,
  open it in Safari (Allow), install it under Settings > Profile Downloaded, then turn it on in Certificate Trust Settings. An empty Certificate Trust Settings list means no root is installed, so any
  HTTPS page reached was a hand-accepted warning. A page cannot tell the two apart: `window.isSecureContext` is true either way, so a probe page must not claim "trusted"; check Safari's padlock
  (Connection Security Details: "This certificate is valid").
- Compare the fingerprint by the certificate's DER hash, or `openssl x509 -noout -fingerprint -sha256` with no other option: OpenSSL 4.1.0 printed a different SHA-256 when `-ext nameConstraints` was
  on the same command line. The serial number is a second, easy check on iOS.
- The RP ID moves with the name: passkeys made for `localhost` cannot be used from the phone; plan one new registration.
- Bind the listener to the LAN address only, route only the sign-in and the pages needed (never the IdP admin console), and turn on the host firewall: a laptop with the firewall off exposed every
  0.0.0.0 service to the home LAN.

> **Learned 2026-11-24** · cloud provider host names as identity anchors · VERIFIED_PRIMARY (publicsuffix.org list, read 2026-11-24: `*.compute.amazonaws.com`) ·
> Source: continuum chat 2026-11-24 ("why don't we use EC2 public DNS?"), DL-173 · Falsifier: AWS leaving the Public Suffix List. Every `ec2-a-b-c-d.<region>.compute.amazonaws.com` is its own
> registrable domain (a public suffix sits above it), so a WebAuthn RP ID, cookie scope or certificate bound to it is bound to that one address: releasing the Elastic IP or rebuilding the host breaks
> every passkey. It also resolves to the public address, useless for a service reachable only over a VPN, and changes on every start of a host without a static IP. Use a subdomain of a domain the
> organisation owns, resolved on the VPN's resolver; pick one kept for years with auto-renew, because changing the RP ID re-registers every passkey.

> **Learned 2026-11-24 (b)** · free subdomain registrars as identity anchors (DigitalPlat FreeDomain) · VERIFIED_PRIMARY (publicsuffix.org list read
> 2026-11-24: DigitalPlat section lists `dpdns.org`, `us.kg`, `qzz.io`; live API `GET https://domain-api.digitalplat.org/api/v1/domains/<name>` with a Bearer key returned `expires_at` one year after
> `created_at`, `auto_renew` null) · VERIFIED_SECONDARY (third-party auto-renew repo: free renewal opens 120 days before expiry, `POST /domains/{domain}/renew`) · Source: continuum DL-227, TASK-588 ·
> Falsifier: a DigitalPlat name renewed for more than a year, or the suffix leaving the Public Suffix List. A name under a suffix on the Public Suffix List (`<name>.dpdns.org`) is its own registrable
> domain: valid as a WebAuthn RP ID and with its own Let's Encrypt rate limits, unlike a name under a provider suffix that is not listed. Free registrations run one year and must be renewed (by API,
> in the window): a lapse changes the RP ID and re-registers every passkey, so renewal is a scheduled job with an alert, not a calendar note. The API host answers scripts; the website hosts
> (`dash.domain.digitalplat.org`, `dashboard.digitalplat.org`) serve a bot challenge even to API paths. The open-source code (DigitalPlatDev/Domain-OSS `docs/API.md`) documents DNS records and an ACME
> DNS-01 challenge endpoint; lego and acme.sh had no DigitalPlat provider when checked, so DNS-01 needs a hook script.

> **Learned 2026-11-24 (c)** · is a home line reachable inbound · VERIFIED_PRIMARY (RFC 6598 100.64.0.0/10; a traceroute from a Mac on a home LAN) · Source:
> continuum NAS options, DL-230; `scripts/home_line.py` · Falsifier: a CGNAT line whose first hop after the router is a public address. Before planning a port forward (WireGuard hub at home), run
> `traceroute -n -m 5 -q 1 1.1.1.1` from the LAN and note the public address from an echo service: hop 1 is the router; a 100.64.0.0/10 hop next means CGNAT, an RFC 1918 hop means a second NAT, a
> public hop means the router most likely holds the public address. The router's own WAN address equal to the public one confirms it. `just home-line <line.json>` classifies the saved output. A
> "static" address is the ISP's statement and cannot be seen from the line.

> **Learned 2026-11-25 (d)** · a free registrar's hosted API (DigitalPlat), refines (b) · VERIFIED_PRIMARY (read 2026-11-24/25 with a key, GET only; renewal call
> VERIFIED_SECONDARY from a third-party auto-renew repo, not yet run) · Source: continuum TASK-588, continuum-app `scripts/deploy/domain_renew.py` (5068f33) · Falsifier: a hosted-API path under a
> domain that answers something other than 403 for a route that does not exist, or an ACME-challenge route on the hosted API. Records are at `GET /api/v1/domains/<name>/dns/records`; the zone is at
> `/dns`, with free-plan limits in the answer (60 changes a minute, 1000 a day, 200 records a zone). Every other path under a domain answers 403 `forbidden` as a catch-all, so a 403 proves nothing
> about whether a route exists; no ACME-challenge route was found. The error shape `{"error":{"code","message"},"success":false}` differs from the open-source Domain-OSS code, so the OSS docs (cited
> in (b)) do not describe the hosted service: probe the hosted API before building on an OSS endpoint. `expires_at` comes without a UTC offset: read it as UTC. Renewal is `POST /domains/<name>/renew`
> with `{"renewal_type":"free","years":1}` and an `Idempotency-Key` header.
>
> ```python
> # continuum-app scripts/deploy/domain_renew.py (5068f33)
> when = dt.datetime.fromisoformat(str(data["expires_at"]).replace("Z", "+00:00"))
> # The live API answers without an offset (2026-11-25); read that as UTC.
> headers |= {"Content-Type": "application/json", "Idempotency-Key": str(uuid.uuid4())}
> call(base, key, "POST", f"/domains/{urllib.parse.quote(domain)}/renew", {"renewal_type": "free", "years": 1})
> ```

> **Learned 2026-11-25 (e)** · DNS on Cloudflare Free for a name from a free registrar · VERIFIED_PRIMARY (developers.cloudflare.com DNS zone setups, full setup, read
> 2026-11-25); acceptance of a private-section suffix UNVERIFIED until tried · Source: continuum DL-237, DL-241, ASK-612 · Falsifier: Cloudflare accepting or refusing a zone one level below a PSL
> private-section suffix. Cloudflare's full setup needs the zone apex to be one level below a Public Suffix List suffix. Whether a suffix in the PSL's private section (where free registrars' suffixes
> sit) counts is not documented: try onboarding before planning on it. If accepted, the registrar keeps the domain and only the nameservers move; an API token limited to Zone DNS Edit on that one zone
> serves DNS-01 through the stock lego, acme.sh or Traefik Cloudflare provider and cannot transfer or release the domain, so it is a smaller secret than the registrar's API key.

> **Learned 2026-11-25 (f)** · push alerts to an iPhone from self-hosted ntfy · VERIFIED_PRIMARY (docs.ntfy.sh/config, "iOS instant notifications", read 2026-11-25) ·
> Source: continuum DL-243 · Falsifier: an ntfy release whose iOS app gets instant delivery from a self-hosted server with no upstream. iOS instant delivery needs the public ntfy.sh as upstream even
> for a self-hosted server (Apple push goes through ntfy.sh), so self-hosting does not remove the third party for an iPhone. For a few alerts, the public ntfy.sh with a long random topic name, kept in
> the password manager and out of Git and cloud-init, is the simple option; send nothing secret in the message (host and days left).

> **Learned 2026-11-25 (g)** · moving a free-registrar name to Cloudflare and issuing by DNS-01, resolves the open point in (e) · VERIFIED_PRIMARY (done 2026-11-25:
> Cloudflare Free accepted `<name>.dpdns.org`; registrar API GET showed the new nameservers; `dig +trace` delegation; a Let's Encrypt staging certificate by DNS-01; caddy-dns/cloudflare README read
> the same day) · Source: continuum ASK-612, TASK-599, continuum-app c3afdad · Falsifier: a resolver that answers a just-delegated zone correctly on the first query, or a Caddy Cloudflare module
> that works with a token without Zone Read. (1) Cloudflare accepted a zone one level below a PSL private-section suffix and activated it about 40 minutes after the nameserver change. (2)
> DigitalPlat's hosted API shows `nameservers` but documents no write for them: change them in its dashboard, never by guessing a write path. Its API host sits behind Cloudflare and refuses Python's
> default User-Agent (403, error 1010): send your own. (3) On the day of the move, 1.1.1.1 answered SERVFAIL for names under the zone while 8.8.8.8 and the zone's own nameservers answered NXDOMAIN
> (most likely the old delegation still cached), and Caddy's zone lookup failed through it: give the ACME client more than one resolver (`resolvers 8.8.8.8 1.1.1.1`) and retry on another before
> blaming the token. (4) Caddy's Cloudflare provider finds the zone by name, so its token needs Zone Read as well as DNS Edit (module README; refines (e); lego's provider UNVERIFIED); a TXT create,
> read from the zone's nameserver, delete round trip proves the token before any ACME run.
>
> ```text
> # continuum-app deploy/nas/caddy/Dockerfile (c3afdad)
> FROM caddy:2.11.9-builder AS build
> RUN xcaddy build v2.11.9 --with github.com/caddy-dns/cloudflare@a8737d095ad5a48ca031cea6ab704057dbc2d250
> FROM caddy:2.11.9
> COPY --from=build /usr/bin/caddy /usr/bin/caddy
> ```

> **Learned 2026-11-26** · ACME DNS-01 propagation checks (Caddy 2.11.9 caddy-dns/cloudflare, Traefik v3.7 lego) · VERIFIED_PRIMARY (deployment:
> `dig @8.8.8.8` showed the cached SOA with 1146 s of the zone's 1800 s negative TTL left; after switching the check to the zone's own nameservers the
> certificate issued 21 s after a restart) · Source: continuum-app deploy/coordinator/tls-acme.caddy (be572df) · Falsifier: a public recursor answers a
> freshly created `_acme-challenge` TXT inside the zone's negative TTL after an earlier NXDOMAIN for that name
> Point the ACME client's propagation check at the zone's authoritative nameservers, not public recursors. The first lookup of a challenge name
> before its TXT exists caches NXDOMAIN for the SOA minimum (Cloudflare: 1800 s), and every retry inside that window times out; Caddy then also falls
> back to the staging CA. Caddy: `tls { dns cloudflare {env.CF_API_TOKEN}; resolvers <ns1> <ns2> }`; Traefik:
> `--certificatesresolvers.<r>.acme.dnschallenge.resolvers=<ns1>:53,<ns2>:53`. Update the names if the provider moves the zone (`dig NS <zone>`).
>
> **Learned 2026-11-26** · Caddy automatic HTTPS with a loaded certificate · VERIFIED_PRIMARY (Caddy log "skipping automatic certificate management
> because one or more matching certificates are already loaded") · Source: continuum-app deploy/coordinator/bootstrap.py edge_alt_names (be572df) ·
> Falsifier: Caddy obtains a public certificate for a name an already loaded certificate (`tls <cert> <key>` elsewhere in the config) also covers
> Caddy does not issue a public certificate for a name that any loaded certificate in the config already matches, even when that site asks for ACME. An
> internal certificate for other sites must not carry the public names; it then quietly serves the internal one on the public names.

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

> **Learned 2026-11-25 (h)** · DNS-01 token check for a zone on Cloudflare Free · VERIFIED_PRIMARY (run 2026-11-25) · Source: home NAS project
> `scripts/nas_dns_check.py` (commit a3c6fae) · Falsifier: a zone-scoped token that lists other zones from `GET /zones`
> A token made in an account that already holds another zone saw both zones (the second project's zone too) until its Zone Resources were narrowed to
> the one zone; nothing in DNS-01 itself shows that. Check every new or rotated token: `GET /user/tokens/verify` is active, `GET /zones` returns exactly
> the expected zone, the zone's nameservers match what public resolvers return, then a TXT record is created, read straight from the zone's
> authoritative server (`dig @<ns>`), and deleted. Read-only by default; the round trip only with an explicit flag.

> **Learned 2026-11-25 (i)** · public A record for a private address, home LAN behind a consumer router · VERIFIED_PRIMARY (dig against the
> zone's nameserver, 1.1.1.1, 8.8.8.8 and the router, repeated; curl through the macOS system resolver) · Source: home NAS project
> scripts/nas_dns_records.py and scripts/nas_api.sh at 7651961 · Falsifier: a router that returns NXDOMAIN for the name after the zone's negative TTL
> (1) A DNS-only public A record pointing at a LAN address lets every device (and VPN clients routed to the LAN) use the name on a Let's Encrypt
> certificate with no local DNS; the router passed private answers (no rebinding filter seen). (2) Query a new name only after creating it: the first
> lookups made right after creation were cached as NXDOMAIN for the zone's SOA minimum (Cloudflare 1800 s). The router flapped between answer and
> NXDOMAIN (two upstreams, one with the negative cached), and the macOS system resolver held its own negative entry while `dig` (which bypasses it)
> already answered; both cleared within the TTL without a flush. Check with the system resolver (curl, getaddrinfo), not only dig. (3) Make API
> clients independent of LAN DNS by pinning the certificate name to the known IP and verifying with the system trust store:
> ```bash
> curl --resolve "malik-nas.example.org:8006:192.168.86.151" https://malik-nas.example.org:8006/api2/json/version   # name verified, no DNS
> ```

> **Learned 2026-11-26** · Caddy 2 behind cloudflared on the same host · VERIFIED_PRIMARY (Caddy docs, matchers: client_ip and remote_ip; a LAN request returned 200
> and the rule is in place) · Source: me/nas apps/caddy/Caddyfile (commit 5dd355d), DL-081 · Falsifier: a Caddy release where remote_ip honours trusted_proxies
> To keep a path private (home LAN and Tailscale only) on a host that cloudflared also serves, match `client_ip`, never `remote_ip`: tunnel requests reach Caddy
> from 127.0.0.1, which `private_ranges` includes, so a remote_ip rule lets the internet in. With `trusted_proxies static 127.0.0.1/32` and
> `client_ip_headers Cf-Connecting-Ip`, client_ip is the visitor's public address for tunnel traffic and the real LAN address otherwise. Tailscale through a
> subnet router arrives SNATed from the router's LAN address; 100.64.0.0/10 covers direct tailnet peers.
```caddy
handle /ops/* {
	@outside not client_ip private_ranges 100.64.0.0/10
	respond @outside "Only on the home network or Tailscale" 403
	uri strip_prefix /ops
	reverse_proxy 127.0.0.1:3100
}
```

> **Learned 2026-11-26 (b)** · Tailscale beside another CGNAT overlay (NetBird) · VERIFIED_PRIMARY (Tailscale docs "IP pool", validated 2026-01-12; tailscale/tailscale
> issue 12828, open) · Source: me/nas DL-084, scripts/mac/nas_tailscale_policy.py (commit 8cbb4b67) · Falsifier: a Tailscale release that routes only the pool
> Tailscale's IP pool (beta, `nodeAttrs` `ipPool`) narrows the addresses given to NEW devices only (existing ones keep theirs), and the client still installs
> a route for all of 100.64.0.0/10, so a pool does not free the range. Two CGNAT overlays coexist on macOS and Windows when their addresses do not overlap
> (the other overlay's narrower route wins); Linux Tailscale drops other 100.64.0.0/10 traffic unless its CGNAT drop rule is turned off. Check every current
> device against the other overlay's block before relying on the pool, and avoid 100.100.0.0/24, 100.100.100.0/24, 100.115.92.0/23.
```json
"nodeAttrs": [{"target": ["*"], "ipPool": ["100.64.0.0/12"]}]
```

> **Learned 2026-11-26 (c)** · NetBird (self-hosted 0.83.2) service users and `GET /api/users/current` · VERIFIED_PRIMARY (HTTP 403 `permission denied` with a
> fresh service-user token that lists users and its own tokens fine) · Source: continuum-app `deploy/netbird/overlay.py` `cmd_service_token` (b3a3772) ·
> Falsifier: a NetBird release answering `users/current` for a service user. A service user's personal access token (role admin) works for the management API,
> but `users/current` is refused, because there is no signed-in human behind it. To prove a newly minted token, call something the service user may read,
> e.g. its own token list. Service-user tokens are the right automation identity: they cannot sign in to the dashboard as a person; mint them with an
> expiry (`expires_in` days) and alert before it.
> ```python
> check = Api(token()).call("GET", f"users/{svc['id']}/tokens") or []   # not users/current: 403 for a service user
> ```
