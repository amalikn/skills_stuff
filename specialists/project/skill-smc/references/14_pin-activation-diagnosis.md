# SMC Pin Activation Diagnosis

## Contents

- [14.1 The core distinction: validity vs issuance](#141-the-core-distinction-validity-vs-issuance)
- [14.2 Mechanism 1 — is a pin currently valid (`iptables -t mangle`)](#142-mechanism-1--is-a-pin-currently-valid-iptables--t-mangle)
- [14.3 Mechanism 2 — was a pin actually issued (Apache access log)](#143-mechanism-2--was-a-pin-actually-issued-apache-access-log)
- [14.4 Correlating MAC ↔ IP via `dhcpd.leases`](#144-correlating-mac--ip-via-dhcpdleases)
- [14.5 Controller code path](#145-controller-code-path)
- [14.6 Pitfalls](#146-pitfalls)
- [14.7 Fleet case study — 2026-09-11 portal-FQDN regression](#147-fleet-case-study--2026-09-11-portal-fqdn-regression)
- [14.8 Reusable tooling](#148-reusable-tooling)

## 14.1 The core distinction: validity vs issuance

Two independent mechanisms answer two different questions, and conflating them is the mistake to avoid. Neither one alone tells the full story:

| Question                                                       | Mechanism                                 | Answers                                                                        |
| -------------------------------------------------------------- | ----------------------------------------- | ------------------------------------------------------------------------------ |
| Is this pin valid **right now**?                               | `iptables -t mangle -L ECLIPSE_MARK`      | Current state — a snapshot. Says nothing about how or when the mark got there. |
| Was a pin **actually issued/activated** through this box's portal? | Apache access log, `wifi/access` endpoint | An audit trail over time — every activation attempt, with outcome.             |

A mark can exist with **no** corresponding activation in the local Apache log — see [14.6](#146-pitfalls) ("marks ≠ activations"). Conversely, a burst of failed activation attempts (log entries with a
non-302 status) with zero marks tells you the portal is reachable but issuance is failing — a different failure mode than a redirect-FQDN regression (see [10_captive-portal.md](10_captive-portal.md)
and [13_known-issues.md](13_known-issues.md)).

Use **both**. A single mechanism checked in isolation under-diagnoses: mangle-only makes a long-broken site with a couple of still-valid legacy pins look "fine"; log-only (on a box whose local logs
were recently rotated or rebuilt) can wrongly read a healthy site as dead.

## 14.2 Mechanism 1 — is a pin currently valid (`iptables -t mangle`)

```bash
iptables -t mangle -L ECLIPSE_MARK -v -x -n
```

One rule per currently-valid activated PIN, keyed on the client's MAC:

```
    pkts      bytes target     prot opt in     out     source               destination
       0        0 CONNMARK   all  --  *      *       0.0.0.0/0            0.0.0.0/0            MACea:7c:64:70:0f:9e CONNMARK set 0x80061241
```

- **`CONNMARK set 0x8xxxxxxx`** — top nibble carries flag bits, the low 30 bits are the pin-class id. The `0x8` high bit is always set on a valid mark; that's what the tier-routing rules in
  [14.2.1](#tier-routing) key on.
- **`pkts`/`bytes` on this specific rule** = traffic from *this* MAC since *this rule* was installed (i.e. since this pin was last activated/pushed) — not since boot, not since some global counter
  reset. Zero pkts/bytes on a currently-valid mark means that device hasn't sent traffic since activation, not that the mark is fake.
- **Rule count = number of currently-valid pins, full stop.** This is the only number in either mechanism that answers "how many working pins does this site have right now."

This tells you validity **now**. It does **not** tell you issuance — a mark can exist purely because Eclipse pushed it server-side (periodic sync), with no local activation ever having happened on
this box. See [14.6](#146-pitfalls).

### Tier routing (`iptables -t nat -L SQUID_REDIRECT`)

```bash
iptables -t nat -L SQUID_REDIRECT -v -x -n
```

```
    pkts      bytes target     prot opt in     out     source               destination
  131923  7863304 REDIRECT   tcp  --  *      *       0.0.0.0/0            0.0.0.0/0            connmark match  0x0 redir ports 3128
       0        0 REDIRECT   tcp  --  *      *       0.0.0.0/0            0.0.0.0/0            connmark match  0x0/0x80000000 redir ports 3130
      58     3712 REDIRECT   tcp  --  *      *       0.0.0.0/0            0.0.0.0/0            redir ports 3131
```

| Port | Connmark match                  | Tier                                                               |
| ---- | ------------------------------- | ------------------------------------------------------------------ |
| **3128** | `0x0`                           | No pin — captive-portal redirect (the "you need to activate" path) |
| **3130** | `0x0/0x80000000` (top bit only) | Top-bit-only tier — a lesser access class, not full any-data       |
| **3131** | (catch-all, already marked)     | Any-data PIN — full unrestricted access                            |

**Chain-level `pkts`/`bytes` here are cumulative since these NAT rules were last (re)loaded** — typically since `smc_squid`/`smc_iptables` last ran on this box, which can be a very long time ago on a
box that hasn't been re-provisioned (confirmed live: a box whose rules were last loaded over a year prior still showed millions of accumulated packets on port 3131 despite having only one
currently-valid mark — that large number is *history*, not *now*; the mark count is *now*). Don't read a large 3131 total as proof the site is currently healthy — cross-check it against the mark count
and the mtime of whatever last touched the NAT/mangle rules (squid.conf regeneration, typically).

A site where **3128 dominates and 3131 is near-zero**, alongside a near-empty `ECLIPSE_MARK` chain, is the live signature of "essentially everyone hitting this network right now has no valid pin."

## 14.3 Mechanism 2 — was a pin actually issued (Apache access log)

```bash
zcat -f /var/log/apache2/access.log* /var/log/apache2/other_vhosts_access.log* 2>/dev/null | grep 'wifi/access'
```

Endpoint: `POST /index.php/wifi/access/<epoch>`.

| Status | Meaning                                                                            |
| ------ | ---------------------------------------------------------------------------------- |
| **302** | Successful activation — redirect out of the portal, pin applied                    |
| **200** | Failure — the controller re-renders the welcome page inline instead of redirecting |

```
10.0.57.199 - - [06/Sep/2026:10:05:34 +1000] "POST /index.php/wifi/access/1788653131 HTTP/1.1" 302 363 "https://communitywifi.net.au/" "Mozilla/5.0 (iPhone; ...)"
```

Client IP + timestamp + status is the audit trail. **A count of 302s over a window is the closest thing to a real issuance-rate metric this fleet has** — see the case study in
[14.7](#147-fleet-case-study--2026-09-11-portal-fqdn-regression) for what that looks like used comparatively across sites.

Related endpoints worth including in a fuller audit, same log grep pattern: `prepaid`, `payment`, `token` (purchased pins), `index`, `terms`, `limited`, `resume`, `success`, `me`.

**Verified timing** (2026-09-06, hope-vale-smc01): device `10.0.57.199`'s activation POST landed at `10:05:34`; the first allowed Squid flow for that same client appeared **9 seconds later** at
`10:05:43`. The activation → mark → traffic-allowed pipeline is fast once it works; a device stuck at the portal for minutes is a different, earlier-stage failure (DNS/redirect/FQDN — see
[10_captive-portal.md §11.7](10_captive-portal.md)), not a slow activation.

## 14.4 Correlating MAC ↔ IP via `dhcpd.leases`

Both mechanisms above key on different identifiers — mangle on MAC, the access log on client IP. To connect a specific mark to a specific log entry (or vice versa), for a **one-off manual check**:

```bash
grep -B2 -A8 '<ip-or-mac>' /var/lib/dhcp/dhcpd.leases | grep -E 'lease|hardware ethernet|client-hostname'
```

`dhcpd.leases` is append-only and can be large (multi-MB) on a busy site — grep for the specific identifier rather than reading the whole file. Each block looks like:

```
lease 10.0.36.140 {
  starts epoch 1789102221; # Fri Sep 11 14:50:21 2026
  ends epoch 1789145421; # Sat Sep 12 02:50:21 2026
  cltt epoch 1789106232; # Fri Sep 11 15:57:12 2026
  binding state active;
  hardware ethernet 56:39:cf:bd:8e:dd;
}
```

`starts`/`ends`/`cltt` are already Unix epoch on this fleet's dhcpd config (`# <human>` is just a trailing comment) — no date parsing needed if you're scripting against them.

### The join-order bug — do not `tail -1` the lease blocks for an IP

**`dhcpd.leases` is append-only, and a given IP accumulates multiple lease blocks over time** (each renewal appends a new block; ISC dhcpd's own semantics treat the *last* block as the
current/authoritative state). That matters for a live-appliance snapshot, but it is the **wrong** block to use when correlating a *historical* activation timestamp — "the last block in the file for
this IP" can have a `starts` epoch **after** the activation you're trying to explain.

**Confirmed live 2026-09-11, `hope-vale-smc01`, IP `10.0.36.28`:** the last lease block in the file for that IP had `starts epoch` = `15:53:29`, but the real `wifi/access` activation for that IP was
logged at `15:52:41` — **48 seconds before** the lease that block claims created the binding. The correct block (an earlier renewal, same MAC) was further up the file. A naive `tail -1` join would
have reported a technically-true-later MAC as the one active at activation time — usually harmless if it's the same device renewing, but not something to assert as fact without checking.

**The correct method: scan every lease block recorded for that IP, and pick the one whose `starts` epoch is the *latest one still `<=` the activation epoch* — the lease actually in force at that
instant, not the file's last word on that IP.** If no known lease had started by the activation time at all (the earliest known lease is itself later — also seen live, 4 of 30 sampled IPs on
`hope-vale-smc01` in the same session), there is no confirmed binding; report that explicitly rather than guessing.

**This is exactly what `scripts/correlate-pin-activation.sh` automates** — do not hand-roll this join for anything beyond a single spot-check; the ordering bug is easy to reintroduce. It also handles
the data gaps found live on this fleet: an IP with no lease record at all in the window (`no-lease-found`), and a matched lease block that itself has no `hardware ethernet` line
(`no-mac-in-lease-record`) — both print an explicit label rather than a blank field or a silent wrong answer. See [14.8](#148-reusable-tooling).

## 14.5 Controller code path

`application/classes/controller/wifi.php` → `action_access` confirms the flow end-to-end:

1. Client accepts Terms & Conditions.
2. Controller calls Eclipse `get_free_pin_monthly` (or the paid equivalent for `prepaid`/`payment`/`token`).
3. Controller deauth+auth's the client at the AP/gateway level, which is what actually installs the `ECLIPSE_MARK` rule (mechanism 1).
4. Controller issues a `302` (success) or re-renders the welcome page with an inline error, `200` (failure) — this is mechanism 2.

This is why the two mechanisms normally track each other tightly (9-second gap, confirmed above) — but see [14.6](#146-pitfalls) for the one path that decouples them.

## 14.6 Pitfalls

- **Log location varies by box.** On some boxes `/var/log/apache2/access.log` is missing or empty and portal hits land in `other_vhosts_access.log` instead — confirmed live on `bungardi-smc01`, where
  `access.log` was absent entirely. **Always check both**, and both need `zcat -f` across their rotated `.gz` siblings — Apache's default logrotate policy on this fleet keeps roughly 14 days, so a
  3-month historical comparison from logs alone is not possible; only the mark count (a snapshot) and Prometheus-derived traffic proxies (see [13_known-issues.md](13_known-issues.md) — no
  application-level metric exists) reach further back.
- **Marks ≠ activations.** On `hope-vale-smc01` (2026-09), one of the currently-valid marks (MAC `ea:7c:...` → `10.0.37.250`) had **no** corresponding `wifi/access` POST anywhere in the retained log
  window. The pin was generated Eclipse-side and pushed to the box by its periodic sync (roughly every 5 minutes) — the local box never ran the activation flow for it. Do not assume every mark implies
  a local activation event; do not assume every activation implies the reverse either without checking.
- **A near-empty `ECLIPSE_MARK` chain does not mean a dead site.** Confirmed live 2026-09-11 on `amata-smc01` (a healthy control site): the mangle snapshot read **0 currently-valid marks** at the
  exact moment it was sampled, on a box whose `wifi/access` log showed **628 successful activations** in the same window (dozens that same morning, minutes apart). Marks evidently don't sit around
  long enough on this fleet for a point-in-time sample to reliably catch a nonzero count even on a thriving site — whatever expires/reissues them cycles faster than the snapshot interval. **Never call
  a site dead on mark count alone; the `wifi/access` log's 302 count over a real time window is the more trustworthy signal, and the two should always be read together, not the mangle table in
  isolation.** This is the mirror-image failure mode of the previous bullet: that one is "mark present, no activation logged"; this one is "activation-rich, mark snapshot reads zero."
- **Pin-generation timestamps and numbers are Eclipse-side only** — not queryable from the SMC appliance or from Grafana (confirmed no captive-portal/pin-issuance Prometheus metric exists anywhere in
  this fleet's monitoring — see [13_known-issues.md](13_known-issues.md)). **The operator does have a separate Eclipse admin report** ("PIN Last Issued" per site, by site ID/community name) outside
  this fleet's own tooling entirely — confirmed 2026-09-11 as a third, independent corroborating source: it flagged `bungardi` at 10 days stale (last issued 2026-09-01) while every healthy site showed
  same-day, matching this file's own two mechanisms exactly. Treat a stale date there as a trigger to run `audit-pin-activation.sh` against that site, not as a replacement for it — it gives a
  last-issued date, not the pkts/marks/tier detail needed to diagnose *why*.
- **The local per-box MariaDB (`community_connect`) is not the pin store to check.** It exists on some boxes (deployed, in-progress work per the operator, not the production issuance path) and is
  empty/inactive on others — confirmed live 2026-09-11 (schema-less on a freshly-rebuilt box, service not even running on three separate control sites). Don't spend time here; go straight to the two
  mechanisms above.

## 14.7 Fleet case study — 2026-09-11 portal-FQDN regression

Context: `inventories/nbn_accelerate` and `inventories/nbn_wh` both independently had periods where `smc_bases_portal_fqdn` pointed at the Teleport proxy hostname instead of the real portal domain —
see [13_known-issues.md](13_known-issues.md) for the full git-archaeology timeline (two separate regressions, `nbn_accelerate` ~1 month in 2025, `nbn_wh` ~14 months from 2025-07-01 to 2026-09-03).
Applying both mechanisms above across the flagged sites plus healthy controls, same ~15-day log window (28/29 Aug → 11 Sep 2026), settled the question definitively:

| Site                                             | Valid marks now | 3128 (no-pin) pkts | 3131 (any-data) pkts | 302 (activated) | 200 (failed) |
| ------------------------------------------------ | --------------- | ------------------ | -------------------- | --------------- | ------------ |
| hope-vale-smc01                                  | 2               | 131,966            | 58                   | **2**           | 0            |
| kowanyama-smc01                                  | 1               | 1,187,849          | 2,163,868            | **1**           | 0            |
| bungardi-smc01 (`nbn_wh`, confirmed 2026-09-11)  | 2               | 698                | 167                  | **2**           | 0            |
| galiwinku-smc01 (fixed 2026-09-08)               | 370             | 74,109             | 57,095               | 474             | 101          |
| kaltjiti-fergon-smc01 (control — never affected) | 150             | 5,138              | 18,065               | 179             | 105          |
| doomadgee-smc01 (control)                        | 570             | 505,770            | 161,201              | 893             | 207          |
| amata-smc01 (control)                            | 183             | 26                 | 15                   | 628             | 44           |
| aurukun-smc01 (control)                          | 650             | 126                | 990                  | 724             | 87           |

`hope-vale`/`kowanyama`/`bungardi` had **1–2 successful activations in a 15-day window**, against 179–893 everywhere else checked. This is decisive, not a proxy-metric inference — both mechanisms
independently confirm the same three sites, and only those three, currently have a dead pin-issuance pipeline. `kowanyama`'s large 3131 total despite one current mark is exactly the pitfall described
in [14.2](#tier-routing) — its NAT rules haven't reloaded since 2025-07-05, so that counter reflects over a year of history from pins that *were* valid at various points, not current traffic.
`bungardi` was initially unreachable over Teleport ("no tunnel connection found") — a retry within the hour succeeded; a transient tunnel-registration issue, not a real second outage.

Cross-referenced against the config-regression sweep (deny_info/squid.conf mtime/stale Apache vhost/cron — see [13_known-issues.md](13_known-issues.md)): `hope-vale`, `kowanyama`, and `bungardi` are
the only three sites whose `deny_info` still points at the Teleport hostname today. The pin-activation evidence and the config evidence agree independently — and the operator's own Eclipse-side "PIN
Last Issued" report agrees with both (see the pitfalls bullet above), a third independent source landing on the same three sites.

## 14.8 Reusable tooling

- **`scripts/audit-pin-activation.sh <site> [<site> ...]`** — runs both mechanisms per host (mangle marks, NAT tier counters, `wifi/access` log audit across both log files and all rotations) and
  prints the comparison table above. See `scripts/README.md`.
- **`scripts/correlate-pin-activation.sh <site> [<site> ...]`** — the per-pin follow-up to the above: for every real activation at a site, joins in its MAC and DHCP lease window (§14.4) and current
  live status, one row per pin. Written 2026-09-11 in response to an operator request for exactly this timeline; implements the correct time-windowed lease join described in §14.4 rather than the
  naive last-block lookup. See `scripts/README.md`.
- **`scripts/collect-fleet-health.sh`**'s `05-portal-fqdn-status` capture — the config-side half of this case study (deny_info, squid.conf mtime, Apache vhosts, sslcertcopy cron). Run both together
  when investigating a suspected portal-issuance problem: config state explains *why*, this file's two mechanisms confirm *whether it's actually happening* and *how severely*.
