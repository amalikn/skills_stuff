# SMC Family-Friendly Content Filtering

## 13. Family-Friendly Content Filtering

### 13.1 VLAN 501 access model

Family-friendly sites use `VLAN_501_ACCESS_METHOD: Prepaid Pins` (from Eclipse config.txt). Unauthenticated clients on VLAN 501 are redirected to the captive portal by iptables rules. Authentication happens via PIN entry in the Kohana portal.

Access flow:
```
Client (VLAN 501)
  → HTTP request → iptables REDIRECT/DNAT → Apache captive portal
  → PIN entry → Kohana app → Eclipse validates PIN
  → Eclipse sends MARK command → SMC sets connmark
  → iptables ECLIPSE_MARK allows client traffic through FORWARD chain
  → Squid proxies HTTP; Unbound resolves DNS
```

### 13.2 iptables chains for VLAN 501

Key chains (inspect on SMC):
```bash
iptables -t mangle -S ECLIPSE_MARK          # authenticated user marks
iptables -t mangle -S ECLIPSE_METERED_TIME  # time-based metering marks
iptables -S FORWARD | grep -E "501|MARK"    # FORWARD chain filter rules
iptables -t nat -S PREROUTING | grep 501    # captive portal redirect rules
```

If `ECLIPSE_MARK` is empty: no users have authenticated, or the Eclipse command to populate marks has not been received.

**Differential diagnosis: VLAN 500 working while VLAN 501 doesn't is by design, not a fault.**
`bridge_500` (management VLAN) carries an **unconditional ACCEPT** in the FORWARD chain and bypasses
Eclipse enforcement entirely — it is not subject to `connmark`/`ECLIPSE_MARK` gating at all.
`bridge_501` (public/family-friendly WiFi) is the only VLAN that requires `connmark != 0` to pass
FORWARD. If a site reports "management access works fine but public WiFi doesn't authenticate,"
that is consistent with everything working correctly — it is not evidence the FORWARD chain itself
is broken. Source: `.archcore/specs/spec-002-iptables-forward-chain-behavior-by-bridge.md`.

### 13.3 Content filtering stack

| Layer | Component | Config location |
|---|---|---|
| DNS | Unbound | `/etc/unbound/unbound.conf` (managed by `smc_dns` role) |
| HTTP proxy | Squid | `/etc/squid/squid.conf` (managed by `smc_squid` role) |
| Content filter | SquidGuard | `/etc/squid/squidGuard.conf` (managed by `smc_squid` role) |
| Captive portal | Apache + Kohana | `/var/www/html/wifi` (cloned from Bitbucket wifi.git) |
| Access control | iptables | managed by `smc_iptables` role + Eclipse mark updates |

### 13.4 Eclipse identity model and MAC randomization

**Identity chain** (no human in loop, no PII):
```
T&C acceptance
  → Eclipse auto-generates PIN (invisible to user)
  → PIN bound to client MAC address
  → iptables connmark set per PIN/MAC via ECLIPSE_MARK chain
  → Subsequent packets matched by connmark → allowed through FORWARD
```

**Control granularity**: Binary only — full access or none. No **per-user** rate shaping (`tc`/`htb`) deployed. Squid present on SMP flavor but no delay pools configured. (Do not read this as "no
`tc` shaping anywhere on the fleet" — a separate, manually-installed **per-WAN-link** ingress-shaping mechanism, `tc`/`tbf`/`ifb` on the Starlink VLANs, is live fleet-wide; see
`03_communication-flows.md`, "Manual TBF/`ifb` Ingress Shaping". Different layer, different purpose — WAN-link cap vs. per-client fairness.)

**MAC randomization impacts**:

| Scenario | Effect |
|---|---|
| iOS or Android — stable per-SSID private MAC | PIN binding survives reconnects ✓ |
| User forgets + rejoins same SSID | MAC rotates → new auto-PIN → any prior PIN suspension bypassed ✗ |
| Android Enhanced Randomization | MAC rotates periodically on same SSID without user action → new PIN needed ✗ |

**No-PII constraint**: Cannot tie identity to phone, email, name, or community ID above PIN level in Eclipse. PIN suspension requires automated Eclipse threshold logic — not currently built.

### 13.5 CAKE fair queuing (per-user bandwidth fairness)

Deploy CAKE on `bridge_501` (LAN-facing bridge), **not** per WAN interface.

```bash
# Set total WAN bandwidth (example: 5 × 80Mbps = 400Mbps)
tc qdisc replace dev bridge_501 root cake bandwidth 400mbit
```

**Why bridge_501 not per-WAN**: Per-WAN CAKE creates uneven fair shares — nftables may hash 5 users to WAN1 and 10 to WAN2. `bridge_501` sees all users combined regardless of WAN assignment; fair share is consistent.

**How host fairness works**: Equal slice per device IP regardless of parallel flows. Idle users' slices go to active users. MAC-proof — shapes packets in flight, not identity claims.

**Limits**: CAKE solves speed hogging but does NOT limit total data usage. A user at fair share 24/7 still consumes heavily. Full per-user total usage limiting requires persistent identity or Eclipse automation (neither currently deployed on family-friendly flavor).

### 13.6 Verify content filtering works

```bash
# From cf-test-client — after PIN authentication
# HTTP request should go through Squid (check X-Cache or Squid headers)
curl -sv http://www.google.com/ 2>&1 | grep -E "Via|X-Squid|Cache"

# DNS resolution via SMC Unbound
dig @10.0.0.1 www.google.com +short

# Check Squid access log
vagrant ssh family-friendly-vsmc01 -- tail -20 /var/log/squid/access.log

# Unauthenticated client should be redirected (HTTP 302 to portal)
# (from client before PIN entry)
curl -sv http://1.1.1.1/ 2>&1 | grep -E "Location|302|wifi"
```
