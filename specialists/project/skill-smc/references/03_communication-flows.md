# SMC Communication Flows

## Contents

- [3. Communication Flows](#3-communication-flows)
  * [All Inbound Access](#all-inbound-access)
  * [Backdoor SSH Access (raw reverse tunnel, bypasses Teleport's node agent)](#backdoor-ssh-access-raw-reverse-tunnel-bypasses-teleports-node-agent)
  * [Outbound from SMC Box](#outbound-from-smc-box)
  * [Fluent Bit / Graylog Sidecar Config Architecture](#fluent-bit-graylog-sidecar-config-architecture)
  * [WAN Uplink Addressing and Default-Route Programming](#wan-uplink-addressing-and-default-route-programming)
  * [Manual TBF/`ifb` Ingress Shaping — live, fleet-wide, NOT Ansible-managed](#manual-tbfifb-ingress-shaping-live-fleet-wide-not-ansible-managed)
  * [WAN-Path Diagnostic Techniques (from the 2026-07-30 dark-VLAN investigation)](#wan-path-diagnostic-techniques-from-the-2026-07-30-dark-vlan-investigation)
  * [Local (LAN) Traffic](#local-lan-traffic)
  * [Alert Flows](#alert-flows)
  * [Grafana / Prometheus MCP Access](#grafana-prometheus-mcp-access)
  * [Graylog REST API Access (via Teleport App, no MCP)](#graylog-rest-api-access-via-teleport-app-no-mcp)

## 3. Communication Flows

### All Inbound Access

```
External / Management
    │
    ▼
Teleport proxy (teleport.<project>.au)
    │
    ▼  [via autossh reverse SSH tunnel]
SMC box — port 22 (SSH)
    │
    ├── Human operators (tsh ssh / ansible)
    ├── Jenkins CI (Ansible playbook runs)
    └── Prometheus central (scrape via federation tunnel)
```

### Backdoor SSH Access (raw reverse tunnel, bypasses Teleport's node agent)

Use this when `tsh ssh <site>` hangs, refuses to connect, or the box is registered in Teleport (shows up in `tsh ls`) but is unresponsive over it — the Teleport agent on the SMC has stalled, but the
box's independent OpenSSH reverse tunnel can still be up. Confirmed working live against `galiwinku-smc01` (`nbn_accelerate` project, 2026-09-08); operator-confirmed to also work across the `APN`
project fleet (`rcp`/`wh`/`rct` flavors) — not independently re-validated against an APN-side host in that session.

**Mechanism**: the `smc_autossh` role (`roles/smc_autossh/`) runs an `autossh-teleport-openssh` systemd unit on every SMC box, independent of the Teleport agent itself:

```
ExecStart=/usr/bin/autossh ... -R {{ openssh_remoteport }}:127.0.0.1:22 ssh-portfwding@{{ teleport_address }}
```

This is a persistent, always-on OpenSSH reverse tunnel (`-R`) from the box's own port 22 back to the fleet's teleport bastion host, bound to a per-site port on that bastion. The tunnel itself
authenticates with a raw OpenSSH key (`/var/local/autossh/ssh-portfwding.id_rsa`) — Teleport is not in this path at all, which is exactly why it survives a hung Teleport node agent.

**Port formula** (`smc_bases.yml:78`): `openssh_remoteport = 50000 + site_eclipse_siteid`. `site_eclipse_siteid` is a globally unique Eclipse site ID (required var, `smc_definition` role) — the
resulting port uniquely identifies one site fleet-wide, regardless of which project/teleport cluster it belongs to.

**Which bastion, per project** (`group_vars/smc_bases.yml` per inventory; each project has multiple flavors nested under it — see `01_overview.md` "Remote Access"):

| Project        | Flavors (incl. central-infra)                     | `teleport_fqdn`                 | Bastion IP / alias                                              |
| -------------- | ------------------------------------------------- | ------------------------------- | --------------------------------------------------------------- |
| nbn_accelerate | `nbn_accelerate`, `nbn_wh` (+ `cw` central-infra) | `teleport.communitywifi.net.au` | `3.104.50.51` — reverse-DNS/`known_hosts` alias `cw-teleport01` |
| APN            | `rcp`, `wh`, `rct` (+ `apn` central-infra)        | `teleport.apn.au`               | `13.54.242.59`                                                  |

**Procedure**:
1. Find `site_eclipse_siteid` for the target site (`host_vars`/`group_vars`) and add 50000 to get its port.
2. `tsh ssh --proxy=<cluster-fqdn> root@<bastion>` — reach the bastion via Teleport (this hop still needs a working `tsh` session, but to the *bastion*, not the hung site).
3. From the bastion: `ssh -p <port> root@127.0.0.1` — a second, independent SSH hop straight into the SMC box's own sshd, entirely outside Teleport.
4. Credential: a fleet-wide shared root password, stored in the KeePassXC vault at `Network/SMC` (see `security-and-secrets-guide.md` for the `kp` retrieval workflow — `kp clip "Network/SMC"` copies
   it to the clipboard; paste directly into the interactive prompt rather than piping the plaintext through automation/tool logs).

**Caveats**:
- No Teleport session recording on this path — it's a raw root shell with none of Teleport's audit trail. Reserve it for cases where `tsh ssh` itself is what's broken; it is not a routine substitute
  for normal access.
- The tunnel depends on the box's own `autossh-teleport-openssh` service still running. If the box is fully hung (see the Silent Total Hang failure mode in `06_failure-modes.md`), this path is dead
  too — it rescues you from a *stuck Teleport agent*, not a *stuck kernel*.

### Outbound from SMC Box

```
autossh-teleport-openssh → teleport.<project>.au   (persistent, always on)
autossh-prometheus-federation → central Prometheus (metrics federation)
prometheus (local) → remote_write endpoint
speedtest-exporter → Ookla speed test servers      (every 1h)
cnmaestro-provisioning → CNMaestro cloud API       (WiFi AP provisioning)
rsyslog → Graylog UDP syslog                       (log shipping, when configured)
graylog-sidecar + fluent-bit → gl.aws.apn.au:443   (structured HTTPS GELF; X-GELF-Token header)
postfix → mail relay
NBN Accelerate API                                  (broadband management, nbn_accelerate flavor)
```

### Fluent Bit / Graylog Sidecar Config Architecture

Graylog Sidecar manages Fluent Bit config dynamically. `/etc/fluent-bit/fluent-bit.conf` is a placeholder only. Live config is stored under a hash-named subdirectory:

```
/var/lib/graylog-sidecar/generated/<collector-hash>/apn-gelf-http.conf
```

Inspect live tailed paths:
```bash
ls /var/lib/graylog-sidecar/generated/          # shows hash dir name
find /var/lib/graylog-sidecar/generated/ -type f -exec grep -h "^\[INPUT\]" -A5 {} \;
```

**Output endpoint is port 443 HTTPS, not UDP 9000.** Do not use `nc -zw3 gl.aws.apn.au 9000` to check connectivity — it will always fail. Correct check:
```bash
nc -zw3 gl.aws.apn.au 443 && echo GL_OK || echo GL_FAIL
```

**Fluent Bit reads NO journald directly.** All inputs are `tail`-based file readers. As of 2026-06-30 (verified on tjuntjuntjara-smc01), the 9 inputs are:

| Tag                 | Path                                                                  |
| ------------------- | --------------------------------------------------------------------- |
| syslog              | `/var/log/syslog`                                                     |
| misclog             | `/var/log/auth.log`, `kern.log`, `mail.log`, `daemon.log`, `dpkg.log` |
| apache              | `/var/log/apache2/*.log`                                              |
| squid               | `/var/log/squid/*.log`, `/var/log/squidguard/*.log`                   |
| apt                 | `/var/log/apt/*.log`                                                  |
| interfacecheck      | `/var/log/interfacecheck.log`                                         |
| sidecar             | `/run/graylog-sidecar/sidecar.log`                                    |
| fluent-bit          | `/var/log/fluent-bit/fluent-bit.log`                                  |
| unattended-upgrades | `/var/log/unattended-upgrades/*.log`                                  |

**journald → rsyslog path:** `ForwardToSyslog` is commented out (system default = no on Ubuntu 22.04). rsyslog reads journald via `imjournal` module, writing `/var/log/syslog` and facility files —
which Fluent Bit then tails. Setting `Storage=volatile` on journald does not break this pipeline since `imjournal` reads from `/run/log/journal/` (the volatile RAM location).

**Future improvement:** Adding `[INPUT] Name systemd` to the sidecar collector config and removing `syslog` + `misclog` tail inputs would give structured journald fields in Graylog and decouple Fluent
Bit from rsyslog files, enabling rsyslog write reduction independently.

**The live config is downloaded from the CENTRAL Graylog server, not from the box or the ansible role (critical — found 2026-07-23).** `sidecar.yml` sets `server_url: https://gl.aws.apn.au/api/` and
the sidecar polls every 10s, downloading its assigned Collector Configuration and regenerating the hash-dir file. So:
- **A local edit to `/var/lib/graylog-sidecar/generated/<hash>/*.conf` is reverted within 10s** — never fix the pipeline by editing the box.
- The ansible role file `roles/smc_graylog/files/apn-fluentbit-config-file` is a **reference copy only** — it is **NOT auto-deployed to Graylog**. It must be **manually applied** to the Graylog
  server-side Configuration. This is a real drift trap (see smcgroup gap below).
- All 50 SMC sidecars (every flavor) share **one** config: `68a08bfc1a864a6164886a2c` (`apn-gelf-http-configuration`). A test copy exists: `68a3b61c…` (`apn-gelf-http-test-configuration`).

**smcgroup shipping gap (canary log-loss, found + RESOLVED 2026-07-23):** the `smc_rsyslog` log-group split (canary on tjuntjuntjara only) `stop`s (MOVES) wifi/dhcp/system programs out of
`/var/log/syslog` into `/var/log/smc-groups/*.log`, but the `smcgroup` `[INPUT]` tailing those files existed **only in the ansible reference file, not in the live Graylog config** — so from
~2026-07-20 the diverted programs (`dhcpd`/`dhclient`/`nl80211`/`netifd`/exact-`systemd`/`hostapd`/`cnmaestro-provisioning`/`WIFI-4-CLIENT-*`…) **stopped reaching Graylog entirely** (`dhcpd`=0 in the
shipped syslog, all in the unshipped `dhcp.log`). `WIFI-6-CLIENT-*` is NOT diverted, so general wifi data still appeared — masking the gap. **RESOLVED 2026-07-23:** the `smcgroup` `[INPUT]` +
`rewrite_tag` `[FILTER]` (→ `smcgroup.wifi/.dhcp/.system`) were added to Graylog config `68a08bfc…` (UI paste). Verified: Graylog now receives `_tag:smcgroup*` (dhcpd back as `smcgroup.dhcp`).
**Fleet-safe:** the shared-config input is a no-op on non-split nodes (glob matches nothing → 0 records, no error — confirmed live on mornington). Naturally RCP-only because the files only exist where
the RCP-flavor split runs. **Standing note: `apn-fluentbit-config-file` changes must be MANUALLY re-applied to config `68a08bfc…` — there is no sync automation.**

**Consolidating /var/log writers onto the smc-groups tmpfs + rotation rules (2026-07-23, deployed fleet-wide 15/16 that evening — new-looma pending).** Beyond the rsyslog-split families, the other
residual SSD log-writers (squid `access.log`/`cache.log`, `interfacecheck.log`, and — added the same evening — mosquitto `mosquitto.log`) were moved onto the same tmpfs by **symlinking their paths**
into `/var/log/smc-groups/` (squid/mosquitto: `stop → rm dir → symlink → start`, to dodge the FD-shadow trap — mosquitto holds its log file open continuously same as squid, confirmed via `lsof`;
interfacecheck: plain file symlink). squid and interfacecheck kept their **existing** Fluent Bit inputs/tags (`squid`/`interfacecheck`); **mosquitto had NO existing input at all — it was not shipping
to Graylog before this** (confirmed live), so a new own-tag `mosquitto` input was added at the same time, closing a long-pending disposition rather than being a relocation of something already
shipping. All three keep their own tag rather than riding `smcgroup.*` for two reasons: their native log formats would misparse under `smcgroup`'s `syslog-rfc3164` parser, and `smcgroup`'s input globs
`/var/log/smc-groups/*.log` non-recursively so it would never match a subdirectory anyway. The tmpfs was bumped 64M→128M→**256M** (dir 0755 so `proxy`/`mosquitto` can traverse into their own subdirs)
— the 256M bump was a deliberate flood-headroom decision for heavy-squid/AP-flood-prone nodes (horn-island, mornington): a tmpfs `size=` is a ceiling not a preallocation, so raising it costs ~0 RAM at
steady state. Durable rotation rules for any tmpfs-backed log dir:
- **Fluent Bit `tail` is read-only — it NEVER deletes/truncates.** On a tmpfs, logrotate + the size cap are the *only* reclaim. So every relocated log needs a size-bounded logrotate.
- **No `delaycompress` on tmpfs** — it keeps an uncompressed ~20M `.1` per busy file (~doubles footprint); rsyslog/squid/mosquitto reopen via postrotate so nothing writes `.1` after rotation. Use
  `size 20M` + `rotate 4` + `compress`. squid and mosquitto each keep their own logrotate (glob `*.log` doesn't reach a subdirectory) — role-managed, `maxsize 20M` added to each.
- **A daily-only logrotate.timer means `size` triggers are checked once/day, not continuously** — found via mosquitto's own stock package fragment (`size 100k daily`), which never actually bounded it
  in practice: `logrotate.timer` is `OnCalendar=daily` fleet-wide (confirmed live, plus the `cron.daily` fallback), so a file can grow well past its "size" trigger between daily checks (mosquitto
  reached 4.5M on the heaviest node vs a 100k target). The same latent limitation likely applies to `smc-log-groups.logrotate`'s own `size 20M` trigger during a real burst — not yet independently
  verified, worth a follow-up check.
- **`Rotate_Wait` is a seconds-scale drain window, NOT an outage buffer** — set it small (30s). A long value pins the *unlinked-but-open* rotated inode's RAM on the tmpfs for that whole duration (an
  unlinked file still occupies space until the FD closes). Outage resilience is the fbpos 256M buffer instead: once FB reads a line it lives there independent of the source file.
- **Only tmpfs *log* dirs need logrotate.** `/tmp`, Prometheus-TSDB, textfile-collector, and fluent-bit-pos are self-bounding (retention / overwrite / SQLite autocheckpoint) — running logrotate
  against the TSDB or the pos SQLite DBs would corrupt them.

Implemented in `smc_rsyslog` (ansible-wifi commit `594653b` + a same-day mosquitto follow-up): tmpfs resize + squid/interfacecheck/mosquitto relocation + `smc-log-groups.logrotate` (size-based) +
role-managed `squid.logrotate`/`mosquitto.logrotate`; `Rotate_Wait 30` on all 4 tmpfs-tailed inputs (reference config + applied to Graylog `68a08bfc` for both the smcgroup and mosquitto inputs).
**Deployed fleet-wide** — squid/ interfacecheck on 15/16 (new-looma pending), mosquitto on 14/15 (also n/a on tjuntjuntjara — confirmed no `mosquitto.service` there). Both deploys hit and recovered
from transient tooling incidents unrelated to the SMC side: an ansible interrupted-handler trap (config deployed but rsyslog never restarted, so the split looked present but was inactive — caught by a
post-deploy fatrace audit, not by `changed=0`) and a Homebrew `ansible` auto-upgrade mid-run (Cellar dir removed while a process still had imports open — just retry).

**Shared-config flavor gating — FreeMarker `<#if>`, NOT Go-template (2026-07-23 incident).** The central config `68a08bfc` is pulled by **~300 sidecars of every flavor** (rcp/rct/wh), so any
flavor-specific tail INPUT must be gated or it errors continuously on flavors that lack the path — a real-disk `fluent-bit.log` error loop, the exact write class this project targets. This bit us both
directions: the mosquitto INPUT (rcp-only) errored on all rct/wh; the `rise_logs`/`rise_status` INPUTs (rct/wh-only) error on all rcp (making `fluent-bit` the #1 real-disk writer on 11/15 rcp nodes).
Gating mechanism, version-confirmed on the deployed **Graylog server 6.3.1 / Sidecar 1.5.1 / Fluent Bit 4.0.7**:
- **Graylog Sidecar templating is FreeMarker**, per the server's own in-app docs — `<#if sidecar.tags.<tag>??> … </#if>`, existence-tested with `??` on `sidecar.tags.<tag>`. **NOT** Go-template `{{ if
  in "x" .tags }}` (wrong engine — renders as literal text, then Fluent Bit rejects it: "indentation level is too low"; sidecars keep their last-good config so it's not an outage, but the config can't
  update until fixed).
- Flavor tags come from the sidecar's `sidecar.yml` `tags:` list. rcp nodes are tagged `rcp` via `smc_graylog.yml`'s `graylog_sidecar_extra_tags: ["{{ inventory_dir.split('/')|last }}"]`; rct/wh
  already carry a `rise` tag. Gate rcp-only inputs on `<#if sidecar.tags.rcp??>`, RISE inputs on `<#if sidecar.tags.rise??>`.
- **`record_modifier` multi-word values MUST be quoted.** Fluent Bit's `Record` is `FLB_CONFIG_MAP_SLIST_2` (exactly KEY + one VALUE token); `Record log RISE status update` (4 tokens) is **silently
  dropped** — the field is never added, config still validates + starts. Use `Record log "RISE status update"`. This is why `rise.status` (which uses `parser json`, dropping the default `log` field)
  needs a quoted `log` record_modifier to satisfy the GELF encoder's `gelf_short_message_key log` (else "missing short_message key").
- **Guardrails (project tooling):** `just graylog-config-lint` (read-only lint of the live config for all three of the above failure modes) and `just sidecar-health` (fleet probe: sidecar state,
  config-validation, recent fb errors, unrendered-literal count, tag/gating). Run both after ANY `68a08bfc` edit.
- **General rule reinforced:** never guess syntax for a shared/production system — verify against the docs or source for the *exact deployed version* (all three errors above "validated" but silently
  didn't work).

**Graylog REST API access (read-only inspection):** reach it via the `apn-graylog` **Teleport app** (`tsh apps login apn-graylog`, mTLS) — the endpoint 302-redirects to Teleport login otherwise. Auth
is a **Graylog API token** as basic auth `<token>:token` (the on-box `admin:admin` and the GELF `X-GELF-Token` and the SSM `/apn-graylog/access-token` all do NOT work for the API — the working token
is stored per-project, e.g. `smc-file-writing-analysis/.graylog-token`, gitignored). Convenience recipes: `just graylog-configs`, `just graylog-check-smcgroup`, `just graylog-config <id>`, `just
graylog-api <path>`. `apn-graylog01` is the server host (`tsh ssh`), API on `localhost:9000`.

**Teleport / tsh scope:** SSH access + the `apn-graylog` **app** (Graylog API via `tsh apps login`). DB/Kubernetes access not in use.

### WAN Uplink Addressing and Default-Route Programming

Established 2026-07-29 from ansible-wifi source during the APN routing-issue investigation (`local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/`). All source-verified unless marked
otherwise. **Not yet confirmed on a live box.**

> **The `internet` / `starlink` role labels mean the opposite of what they say (operator-confirmed 2026-07-29).** Originally `internet` = Skymuster Plus primaries (the nbn satellite product; note the
> spelling — **Skymuster**, not "Skymaster") and `starlink` = Starlink backup, which is what the `internetNN` / `starlinkNN` interface keys encode. Starlink was later promoted to primary and simply
> inherited the existing `internet` label; the `starlink` label stayed on what is now the **single SMP backup link per site — `vlan621`**, with `vlan631` as its switch02 counterpart. Nothing was
> renamed, and no `provider`/`description` field exists anywhere in `topology_vars` to record it. Read every `role:` value, interface key and template comment mentioning "starlink" with this inversion
> in mind. A label retrofit is planned but **has not happened** — do not assume it has.

**Second confirmed instance, and a concrete retrofit proposal — 2026-07-31 (operator discussion with Sandro, `local-knowledge-ansible/ansible-wifi/issues/internet-link-handling/`).** Pia Wadjari is a
second live case of the same inversion, deploying with the roles reversed from Horn Island: active links are Starlink (label `internet`), backup links are SkyMuster Plus (label `starlink`). Agreed
with Sandro: the deployment proceeds as scheduled — this is a labeling/monitoring-clarity issue, not a functional one, confirmed against the live mechanism (see "The decisive behaviour is the
enter-hook override" below — `dhclient-enter-hooks.j2`'s per-interface-table vs. main-table-metric split operates on `role:`, not on provider identity, so it works correctly regardless of which
provider sits in which role).

**Proposed fix (design only, not agreed with the wider team, not implemented):** relabel by role rather than provider — e.g. `active-internet` / `standby-internet` — and add explicit per-link metadata
(`provider:`, `link_type:` e.g. satellite/fibre/fixed-wireless, plus any other operationally useful attributes) as separate `topology_vars` fields, rather than encoding provider identity into the
label itself. Must stay backward-compatible with already-deployed sites' current monitoring (no forced redeploy as a precondition); new deployments would follow the revised convention once agreed.
Estimated 2-3 weeks design+testing+implementation once the team agrees. A separate, not-yet-actioned process-improvement ask came out of the same discussion: better version control, diffable change
communication, and formal stakeholder sign-off for deployment-specific decisions like this one — organizational, not technical, tracked in the source workspace only. Full detail:
`local-knowledge-ansible/ansible-wifi/issues/internet-link-handling/internet-link-labeling-and-metadata-convention-20260731_1241.md` (analysis, code-verified) and
`internet-link-labeling-and-metadata-prompt-20260731_1244.md` (verbatim source).

**Site VLAN scheme** (rcp, repo-verified): `internetNN` keys alternate across two switch uplinks — `52x` VLANs on `switch01`, `53x` on `switch02` — and `starlink01`/`02` are `vlan621` (switch01) and
`vlan631` (switch02). Two pairing conventions exist: same-index (521↔531) at old-looma, new-looma, beagle-bay, warburton, horn-island; offset-by-one (521↔532, 523↔534, …) at umoona, pandanus-park,
mornington. Useful when judging whether an unexpected VLAN is a new uplink or a typo.

- **Every rcp site is wired with both VLAN blocks, but switch02 (`53x`) is cold standby by design at every site except Horn Island.** *(live-verified 2026-07-29, Grafana `rate()` on
  `node_network_receive_bytes_total`, all seven sites)* Horn Island is the transition site — built at the point the fleet moved from two switches to one, with too many Starlink services to fit on a
  single switch, so it's the only site actually using both. Every site built after it (all six others) shows exactly **0 bps** on every `53x` VLAN, live, right now — netplan/the hook still define
  those VLANs (so they count toward a "missing N" hook-coverage gap), but nothing is physically plugged into switch02 there. **Do not size customer impact directly from a hook-coverage gap without
  splitting switch01 from switch02 first** — on the four sites checked during the 2026-07-29 routing investigation, roughly half of each site's "missing" count was switch02, cold and harmless; only
  the switch01 half was costing anything. A second refinement on the switch01 half itself: `ip -br link` showing an interface `UP` does not mean it's **leased** — `ip -br addr` (a real CGNAT address
  present) is what distinguishes a genuine orphaned uplink (costing bandwidth right now) from an empty, never-provisioned slot (present in netplan, no dish behind it yet, costing nothing). **Caveat:**
  this assumes switch02 stays unplugged — if it's ever wired up at a site whose `dhclient-enter-hooks` case list is stale, the hook's ignorance of those VLANs reproduces the exact same
  stray-route/missing-route symptom the moment they go live.
- **`LAN1`/`LAN2` (Testra-managed, residential-plan Starlink, 50 Mbps unlimited) are a separate uplink pair, outside the `Swp1/9`–`1/18` VLAN scheme entirely and not yet correlated to any
  `topology_vars` interface key.** *(operator-reported provisioning table, 2026-07-29)* Present at six of seven sites (two lines each); Horn Island has only `LAN1`. Distinct from the direct-Starlink
  enterprise-plan VLANs (`521`–`52N`/`531`–`53N`, 2 TB cap) this section otherwise describes — if a site-specific WAN count doesn't add up against `topology_vars`, check whether `LAN1`/`LAN2` are the
  unaccounted-for difference before assuming a topology drift.

WAN interfaces are *not* managed by systemd-networkd. `netplan.yml.j2` renders every interface with `role: internet` or `role: starlink` as `activation-mode: manual` with **no `dhcp4` key**;
`00-interface-activation.sh.j2` brings them up, and a per-interface `dhclient@<iface>.service` does DHCP using `ubuntu-dhclient-script.j2` (an APN fork of the CentOS dhclient script).

**The decisive behaviour is the enter-hook override.** `ubuntu-dhclient-script.j2`'s `add_default_gateway()` is replaced at runtime by `/etc/dhcp/dhclient-enter-hooks`, generated from
`roles/smc_application/templates/dhclient-enter-hooks.j2`. That hook's `case` list is built at template-render time from **`role == 'internet'` only** — `starlink` is deliberately excluded — and it
has two branches:

|                            | Matched (`role: internet`)                             | Fallback (`*)`) |
| -------------------------- | ------------------------------------------------------ | --------------- |
| Default route lands in     | per-interface table named after the interface          | **main table**  |
| Source policy routing      | `ip rule from <lease-ip> table <iface>`                | none            |
| Metric                     | from DHCP (normally none)                              | **100**         |
| Registers with portal app  | yes — `cd /var/www/html/wifi && kohana status:gateway` | no              |
| Visible in `ip route show` | no                                                     | **yes**         |

Consequences worth knowing before diagnosing any WAN routing question:

- **`ip route show` is not the whole picture.** Healthy `role: internet` uplinks do not appear in the main table at all. Check `ip rule show` and `ip route show table <iface>`.
- **A stray `default via <gw> dev <iface> metric 100` in the main table means that interface is missing from the generated case list** — it is being given backup-link treatment. The fallback itself is
  not a bug (metric 100 loses to the metric-0 ECMP pool, which is correct for the SMP backup on `vlan621`), but a *primary* WAN VLAN landing there is silent misconfiguration: no per-interface table,
  no source rule, no registration with the portal app, and — because the primaries are Starlink — **an installed, leased, healthy dish carrying no traffic at all** while the pool is up. It also
  degrades failover, since the `*)` branch is meant to hold exactly one link. Nothing logs this and no monitoring distinguishes "in the pool" from "parked at metric 100".
- **The one-line triage: does the hook's case list cover every uplink VLAN in netplan?** *(live-verified 2026-07-29 across seven `rcp` sites — 7/7 accurate, no exceptions.)* A site is healthy
  **exactly** when it does, excluding `vlan621`/`vlan631` which are *meant* to be absent. Compare the `case` arm in `/etc/dhcp/dhclient-enter-hooks` against `vlanNNN:` keys in `/etc/netplan/*.yaml`.
  Any VLAN in netplan and not in the hook is a confirmed orphan. This is faster and more reliable than reading routes, because it names the *cause* rather than one of its symptoms.
- **The `*)` branch is first-come, so the number of stray routes tells you nothing about how many interfaces are affected.** It runs `ip -4 route add default …`, which only succeeds when the main
  table has no default. The first orphan to obtain a lease installs the `metric 100` route; every later orphan installs **nothing at all** and is invisible in `ip route show`. One site observed with
  three orphaned uplinks showed a single stray route. **Never size the impact from the route table** — count the gap between the hook list and netplan instead.
- **Confirmation that the fallback is the backup path, not a bug:** a healthy site was observed carrying `default via … dev vlan621 metric 100` — the SMP backup, exactly where the `*)` branch is
  supposed to put it. Absence of that route on other healthy sites means their backup is not leasing, which is its own failover finding.
- **The three network-touching roles can disagree, and which one is stale is diagnostic.** `smc_network` writes netplan, `smc_iptables` writes the NAT masquerade set, `smc_application` writes the
  hook. On every affected site observed, the first two agreed with each other on a newer topology and only `smc_application` lagged — which narrows remediation to one role. Cross-check with `iptables
  -t nat -S | grep POSTROUTING` (masquerade covers every uplink `smc_iptables` believes in).
- **`iptables -S` shows only the `filter` table.** `smc_iptables` templates declare `*filter`, `*mangle` and `*nat`. Use `iptables-save`. For the record, `mangle` on these boxes holds only
  `connmark`-based session accounting on `bridge_501` (`COUNT*`, `MARK_SESSION`, `ECLIPSE_*` chains) for portal quota — **there is no `fwmark` policy routing**, so neither `nat` nor `mangle`
  participates in uplink selection. That is decided entirely by the hook, the per-interface tables and the `ip rule` set.
- **The `smc_application` override is `/etc/dhcp/dhclient-enter-hooks` — extensionless. `dhclient-enter-hooks.d/` is a decoy.** That directory holds only stock Debian fragments (`debug`, `resolved`)
  and never contains `add_default_gateway()`. Both this and the `iptables -S` trap above fail **silently** — exit code 0, plausible-looking output, wrong content — so a capture script or a manual
  `cat` that only checked the `.d/` directory would read as "the hook is empty/minimal" when the real override was never inspected.
- **`dhclient@<iface>.service` is only ever instantiated by `networkd-dispatcher` when the underlying netplan device actually exists.** A stale `/etc/dhcp/dhclient.<name>.conf` file left over from a
  VLAN that's since been removed from `topology_vars` (see `smc_network`'s idempotency gap below) has no running unit behind it and is currently inert — `systemctl list-units 'dhclient@*' --all` only
  ever shows real, live interfaces, never orphaned conf-file names. Useful when auditing whether a conf file on disk implies an active interface: it doesn't, check `dhclient@<name>.service` state
  directly rather than inferring from file presence.
- **The deployed commit is a per-host fact, not a fleet-wide one.** Two of seven sites were found running a hook rendered from a *different branch* than the one believed deployed. Where a site's
  topology differs between two candidate commits, the hook's case list identifies which one it came from — a cheap, reliable way to pin per-host deploy state. Where the commits define a site
  identically the hook cannot discriminate, and that must be stated rather than assumed away.
- **A topology file can shrink.** One site's `internetNN` definitions went from 16 to 6 on a branch, and the shrunken render reached `smc_application` while netplan still held all 16. The failure
  looks identical to a site outgrowing its topology file; only the direction differs. **Stale `ip rule` entries are the forensic marker** — a rule with no matching hook entry is residue from an
  earlier render, since rules persist until deleted or reboot. An interface holding *both* a stale rule and a `metric 100` default is two renders coexisting, not a contradiction.
- **The `100` is accidental.** `metric` is empty at that point, so the code runs `expr + 100`; GNU `expr` treats a leading `+` as a quoting operator, yielding `100`. If DHCP ever returns more than one
  router, `metric` is already the string `metric 1`, `expr metric 1 + 100` errors, and the route is added with **no metric at all** — colliding with the ECMP entry instead of losing to it.
- **Nothing in ansible-wifi builds the ECMP multipath default.** `grep -rn nexthop roles/` returns zero hits. The matched branch calls `kohana status:gateway` on every lease, so the multipath route is
  built by the Kohana wifi app — *inferred, not verified* (that repo is not checked out locally). Practical effect: ECMP membership reflects the portal app's view of link health, which is why an
  unhealthy link quietly leaves the pool.
- **`interfacecheckv2.sh` does not delete routes.** It pings `8.8.8.8` (`-c 4 -W 3`) per interface and on failure runs `systemctl restart dhclient@<iface>.service`, writing
  `my_node_interfacecheck_success{device="…"} 0`. Route disappearance is second-order. That series is a usable per-interface failure-onset history without box access (`mcp-grafana-apn` for
  rcp/rct/wh).
- **`192.168.100.0/24` is the modem's own DHCP scope**, not an SMC address range. Both `roles/smc_network/files/dhclient.conf` and `dhclient-starlink.conf` carry `reject 192.168.100.0/24;` with the
  comments "nbn modem dhcp scope" / "starlink modem dhcp scope". On a primary uplink this is the **Starlink dish management address** (Starlink's standard `192.168.100.1`). Seeing ARP from it on a WAN
  VLAN means the dish's LAN side shares that broadcast domain — the dish is not in a clean bypass state, a real finding worth chasing — but **live-verified 2026-07-29 not to be the cause of "lease
  held, can't ping" by itself.** On two sites where this ARP traffic was captured, `ip neigh` showed the *same* MAC correctly resolving as the gateway on every WAN interface, healthy and broken alike
  — it is the segment's real gateway, periodically also ARPing from its own management IP for its own upstream next-hops. See the missing-route bullet below for what actually broke those interfaces.
  Corroborating signal for the bypass concern independently of that: a `100.64.x.x/10` lease with gateway `100.64.0.1` is Starlink's own CGNAT, so on those links the "carrier gateway" the SMC ARPs for
  is the dish itself — and a public-IP lease (not `100.64.0.0/10`) turning up in an `ip rule`/lease file anywhere is a stronger, independent signal the dish handed out a router-mode address at some
  point.
- **"Lease held, can't ping 8.8.8.8" can be a missing route, not an ARP failure — check which before assuming the dish.** *(live-verified 2026-07-29, two `rcp` sites)* An interface orphaned from the
  hook's `case` list (see the first-come bullet above) can end up with **zero default route in any table** if it lost the race for the `*)` branch's single shared `metric 100` route — that branch runs
  `ip route add`, not `replace`, so only the first orphan to renew gets a route; every later orphan gets none. With no route out that device at all, `ping -I <iface> <off-link-target>` fails
  **locally** (`Destination Host Unreachable` from the SMC's own address, or silent 100% loss with nothing ever sent) — before ARP is even attempted. The tell that distinguishes this from a real L2/
  dish problem: `ping -I <iface> <on-link-gateway>` (e.g. `100.64.0.1`, inside the leased `/10`) still succeeds, because on-link destinations resolve via ARP directly and never need a routing-table
  entry. Diagnose with `ip route show table all | grep <iface>` (real orphans show only the on-link `scope link` route, no `default via ... dev <iface>` anywhere) and `ip rule show` (no `from
  <lease-ip> lookup <iface>` entry). This is the same root mechanism as the stray-route bullet above, just the *losing* side of the same race rather than the winning side — fixing the hook's `case`
  list fixes both. Full evidence: `local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/docs/problem2-live-root-cause-20260729_2112.md`.
- **WAN VLAN MACs are deterministic**, seeded on hostname + interface name: `'72:77:77' | random_mac(seed='{}{}'.format(inventory_hostname, iface_name))`. Renaming a site or a VLAN changes its MAC,
  which can strand a carrier-side or upstream-device binding.
- **`INPUT -i <starlink-iface> -j DROP` is intentional, but its comment is stale.** `iptables.smp.j2` says "Starlink has a public ip, we want to hide it as much as possible" — written when the label
  meant Starlink. Under today's inversion the rule protects the **SMP backup**; the actual Starlink primaries, under the `internet` label, get no equivalent DROP. Currently harmless because they sit
  on CGNAT, but true by accident rather than design. The rule sits after the `ESTABLISHED,RELATED` accept, so outbound-initiated traffic is unaffected, and it is `DROP` not `REJECT` so the host does
  not answer a scanner. Note the template's INPUT chain already ends in `-j REJECT --reject-with icmp-host-prohibited`, so against the template the DROP governs *how* traffic is refused rather than
  *whether* — but a box whose live ruleset shows `-P INPUT ACCEPT` and no trailing REJECT has the DROP as its only protection there. Never recommend deleting it; add a narrower ACCEPT above it if
  inbound access is genuinely required.
- **DHCP negotiation bypasses the `iptables` filter-table `INPUT` chain entirely — this is why the starlink DROP rule above never blocks DHCP, and generalizes to any interface-scoped `INPUT ... -j
  DROP`/`REJECT` rule on this fleet.** ISC `dhclient` (the fleet's DHCP client) opens a raw `AF_PACKET` socket for its own port-68 traffic, tapping frames at the link layer before/parallel to
  netfilter's `NF_INET_LOCAL_IN` hook where the filter table's `INPUT` chain lives — true for the initial `DISCOVER`/`OFFER`/`ACK` exchange (before the interface has an IP at all, so
  `ESTABLISHED,RELATED` can't be the explanation either) and for later unicast-retry/broadcast-rebind renewals alike. Confirmed live on Warburton: DHCP lease renewal on `vlan621` succeeds cleanly
  despite 1.68M packets dropped on that same interface by the very DROP rule in question, and the template's own `dss` role block has an explicit dhcp-broadcast ACCEPT carve-out before its DROP while
  the starlink block has none — yet starlink DHCP demonstrably works, confirming it isn't relying on any filter-table rule at all.
- **Deterministic WAN MACs are a forensic tool, not just a config detail.** Because the seed is `inventory_hostname + iface_name`, the expected MAC for any host/interface pair can be recomputed
  offline and compared against what the box actually has:
  ```python
  from random import Random; import re
  def mac(prefix, seed):
      v = Random(seed).randint(68719476736, 1099511627775)
      return prefix + re.sub(r"(..)", r":\1", f"{v:x}"[:2*(6-len(prefix.split(":")))])
  mac("72:77:77", "old-looma-smc01" + "vlan525")   # -> 72:77:77:d1:90:4a
  ```
A match proves Ansible rendered that stanza (the interface was not hand-created) **and** that the interface carried `role: internet`/`nbn-modem` at render time, since no other role emits a
`macaddress:` line. A mismatch means the interface came from somewhere else. This was the evidence that identified an rcp site whose production netplan had been rendered from inventory present in no
ref of the repository — see `local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/`.
- **Generated artifacts can disagree with each other.** `smc_network` renders netplan and `00-interface-activation.sh`; `smc_application` renders `/etc/dhcp/dhclient-enter-hooks`. A tag- or
  role-limited run can update one and not the other, leaving an interface that netplan treats as a primary and the hook has never heard of — which is exactly what produces a stray `metric 100` route.
  Compare `stat` mtimes of `/etc/netplan/*.yaml` and `/etc/dhcp/dhclient-enter-hooks` when diagnosing. Same failure class as `rule-005`.
- **VRF and multi-WAN policy routing (`multiwan-setup.sh.j2`, `smc-link-allocator.py`, fwmark/nft hashing, per-link tc shaping) exist only on `rise-multi`** (commit `d0635e5e`) and are **not
  deployed**. If WAN routes appear in the main table, VRF is not in play on that box. **More precise 2026-07-31 (git archaeology, `local-knowledge-ansible/ansible-wifi/issues/internet-link-handling/`,
  confirmed on the branch now shared by `rise-multi`/`internet-label-rename` after a same-day reset):** the *deploying* Ansible task block for `multiwan-setup.sh.j2`/`.service.j2`
  (`roles/smc_network/tasks/ubuntu.yml`, ~lines 377-405) is fully commented out — added by commit `5eb127bf` (2025-10-16, the per-WAN-VRF fix for same-subnet/same-MAC Starlink CPE ARP flapping), then
  disabled as **apparent incidental collateral** of an unrelated commit, `c19a61fa` (2026-06-09, a URL-capture-v2 refactor) — no deliberate rationale recorded. This reads as accidentally orphaned
  complexity, not a considered decision to abandon the mechanism. **Important nuance not previously captured here:** the fwmark script being dead does not mean VRF is fully "not in play" —
  `roles/smc_network/templates/netplan.yml.j2`'s per-WAN VRF *allocation* (the `{% if interface.role in ['internet','starlink'] %}` VRF-membership block, ~lines 46/127) is **still live and rendered
  into every deploy today**. Only the fwmark `ip rule`s that would route traffic into those VRF tables are missing. A box could plausibly carry allocated-but-unused `vrf-<tableid>` devices as a result
  — **not yet checked on any live SMC**, flagged as an open item, not confirmed either way.
- **`smc_application`'s dhclient-restart handler had no connectivity safety net — `smc_network`'s does. Fixed 2026-07-29, not yet live-tested under a real failure.** Both roles can trigger `systemctl
  restart dhclient@*.service` (every WAN interface, all at once). `smc_network` (`roles/smc_network/handlers/main.yml`, listen `Protected dhclient services restart`) schedules an independent `at
  systemctl restart teleport` job 2 minutes out *before* the restart, runs the restart `async`/`poll: 0`, then `wait_for_connection` (up to 1h) and cancels the `at` job only if the connection comes
  back — protecting against the exact case where the current SSH/Teleport session dies mid-restart. `smc_application`'s equivalent (`roles/smc_application/handlers/main.yml`, listen `Restart Internet
  interfaces`, fired by the `dhclient-enter-hooks` template task) was a bare synchronous `systemctl restart dhclient@*.service` with none of that — confirmed the only listener repo-wide. **The same
  protected pattern has now been ported into `smc_application`'s handler**, on branch `fix/routing-issue` (uncommitted as of 2026-07-29), `at`/`atd` confirmed installed and active on all four affected
  sites. It has been syntax-checked and validated with `ansible-playbook --check --diff` dry-runs, but **not yet exercised against a real connection-loss scenario** — treat it as
  fixed-on-paper-and-in-dry-run, not fully proven, until that happens. Full detail: `local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/docs/dhclient-restart-safety-gap-20260729_2006.md`.

### Manual TBF/`ifb` Ingress Shaping — live, fleet-wide, NOT Ansible-managed

Established 2026-07-29, live-verified (read-only capture, all seven `rcp` sites). **This is a separate mechanism from the `rise-multi`/VRF "per-link tc shaping" mentioned above** — that one is part of
the undeployed multi-WAN allocator; this one is deployed today, on the currently-live branch, and has nothing to do with VRF.

**Mechanism, confirmed identical everywhere it runs:** a manually-installed script (`/usr/local/sbin/internet-ingress-shaping.sh`) plus a hand-installed `systemd` oneshot unit
(`internet-shaping.service`, `WantedBy=multi-user.target`, runs once at boot). Since `tc` only natively shapes egress, ingress shaping uses the standard redirect pattern: for each shaped `vlanN`, an
`ingress` qdisc redirects all traffic to a paired `ifbN` device (`tc filter ... action mirred egress redirect dev ifbN`), then a `tbf` (token bucket filter) qdisc on that `ifb`'s egress caps the rate.
Only direct-Starlink VLANs (`role: internet`) are shaped — Testra-managed `LAN1`/`LAN2` (already at a 50 Mbps plan cap) and the nbn SMP backup are deliberately excluded, per the operator's own design
intent.

**Not templated, not idempotent, not rendered by any `smc_*` role — confirmed by grep and by absence from every relevant role's tasks.** A future `smc_bases.yml` run will not recreate this if it's
ever lost (e.g. a reinstall), and nothing currently guards against configuration drifting between sites other than each site's script having been hand-edited once at install time.

**The script is hand-parametrized per site, not identical fleet-wide — do not assume a pasted example applies verbatim to another site.** Confirmed live: VLAN loop range varies (2 to 10 VLANs per
site), and Horn Island's rate itself differs — `70mbit` for 10 VLANs, `80mbit` for the other 4, versus `150mbit` uniformly at the other six sites that have the script at all. A site whose live rate
doesn't match a "should be 150mbit" assumption is not necessarily a fault; check that site's own script text first.

**`tc -s qdisc show`'s byte counters are cumulative since the shaping unit last ran (i.e. since last boot), not an instantaneous rate.** For a live rate, query Prometheus instead:
`rate(node_network_receive_bytes_total{device=~"vlan5[0-9]+"}[5m]) * 8` via `mcp-grafana-apn` — this is also how the switch01-vs-switch02 cold-standby fact above was established.

**Known gap, not a fault:** New Looma (installed 2026-07-25, the most recently onboarded rcp site) has no shaping script, unit, or `ifb` interfaces at all — `ip -br link show type ifb` returns empty.
Consistent with shaping being rolled out per-site by hand rather than fleet-wide in one pass; New Looma simply hasn't received it yet. Also confirmed: shaping scripts only ever cover the `52x`
(switch01) block on sites that have them — the `53x` (switch02) cold-standby block above is unshaped everywhere, which is expected since it carries no traffic to shape.

**Corrected 2026-07-30 — not "planned, not started".** A `smc_qos` role already exists in the repo, but it is gated `when: inventory_dir.split('/')|last == 'rct'` — it silently no-ops on every
`rcp`/`nbn_accelerate` deploy. `--tags qos` ran clean during all three 2026-07-30 canary deploys and never fired. Manual TBF/`ifb` shaping (above) remains the only active mechanism on rcp, and it has
NOT been extended to VLANs that were only newly fixed by the routing-drift remediation: 2 VLANs missing shaping at Pandanus Park, 10 at Umoona, 8 at Old Looma (as of 2026-07-30). Two open design
questions if `smc_qos` is regated for rcp/nbn_accelerate: (1) the rate-variable shape needs to support Horn Island's per-VLAN split, not just a single per-host rate — six of seven sites use one rate,
Horn Island needs two; (2) role placement/name relative to `smc_network`/`smc_application` in `smc_bases.yml`'s run order is unconfirmed. Source: `local-knowledge-ansible/ansible-wifi/
issues/apn/routing-issue/docs/ingress-shaping-not-managed-or-extended-20260730_1245.md`.

### WAN-Path Diagnostic Techniques (from the 2026-07-30 dark-VLAN investigation)

Two generalizable techniques, not site-specific, established while chasing a Starlink-backup VLAN that showed as provisioned but was dark at L2:

- **A NIC-level RX counter of exactly `0` (`ip -s link show <iface>`) rules out firewall/L3-L4 causes instantly** — nothing has ever arrived on that interface for iptables/routing to act on, so time
  is better spent on the physical/L2 path (cable, switch port, switch-trunk VLAN membership, carrier CPE) than on iptables rules.
- **The sibling-VLAN isolation test**: if a different VLAN sharing the same physical parent NIC/port as the dark VLAN is carrying real traffic, that exonerates the cable/port/NIC — the fault is
  isolated to the dark VLAN's own switch-trunk membership or the carrier-side CPE, not anything the SMC itself controls.

This pair found Pandanus Park/Umoona/Beagle Bay's `vlan621` backup circuit provisioned in topology but dark at L2 (fixed switch-side, outside ansible-wifi's scope) and separately confirmed Horn
Island's `starlink01`/`starlink02` topology block is applied even at sites with no backup circuit ever ordered — see `13_known-issues.md`. Source: `local-knowledge-ansible/ansible-wifi/
issues/apn/routing-issue/docs/starlink-backup-no-lease-l2-investigation-20260730_1400.md`.

### Local (LAN) Traffic

```
WiFi clients ─→ hostapd (radio)
               ─→ bridge_501 (client VLAN)
               ─→ isc-dhcp-server (DHCP for clients)
               ─→ unbound/named (DNS for clients)
               ─→ NAT/routing (iptables MASQUERADE)
               ─→ upstream WAN

MQTT devices → mosquitto (IoT telemetry)
```

### Alert Flows

```
Prometheus alertmanager
    ├── → prometheus_noc_msteams_webhook → Teams (NOC)
    └── → prometheus_dev_msteams_webhook → Teams (dev)

Jenkins
    └── → jenkins_teams_webhook → Teams
```

### Grafana / Prometheus MCP Access

**Read-only:** mcp-grafana is used for reads only — metric queries, alert state, dashboard inspection. Never write, modify, or create anything in Grafana via MCP.

Grafana instances are not directly accessible — they're reached via local SSH tunnel port-forwards. Use the flavor-specific instance, not `mcp-grafana` (central NOC Grafana, unrelated to SMC boxes).

| MCP instance      | Grafana URL              | Covers flavors       |
| ----------------- | ------------------------ | -------------------- |
| `mcp-grafana-nbn` | `http://127.0.0.1:63000` | nbn_accelerate, nbn_wh |
| `mcp-grafana-apn` | `http://127.0.0.1:53000` | rcp, rct, wh         |

Note: `mcp-grafana` (`monitoring.apn.net.au:3000`) is central NOC Grafana — do NOT use for SMC box troubleshooting. It covers network/ISP dashboards, not SMC host metrics.

**Prerequisite:** The SSH tunnel port-forward must be active before the MCP will respond. Verify with:
```bash
lsof -nP -iTCP:63000 -sTCP:LISTEN   # nbn cluster
lsof -nP -iTCP:53000 -sTCP:LISTEN   # apn cluster
```

**Dashboard inventory (confirmed live 2026-08-03).** The two instances are not mirrors — `mcp-grafana-apn` has 20 dashboards vs 9 on `mcp-grafana-nbn`. Both share a common "smc"-tagged core (Alerts,
Heatmaps, Disk Wear and Tear, Internet Speed Analysis, SMC Disk Life Time, SMC Home, SMC Network, SMC System, Speedtest Exporter). `mcp-grafana-apn` additionally carries dashboards with no NBN
counterpart:

| Dashboard                                    | UID                                    | Purpose                                                                                                      |
| -------------------------------------------- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| RISE SMC Health Detail                       | `rise-smc-detailed-health`             | Per-host RISE health subscores, penalties, thermal/temp, overlay/inode/zram — see "RISE Health/Watchdog      |
|                                              |                                        |   Framework" in `02_service-map.md`                                                                          |
| RISE SMC Table                               | `e3c73c2a-351f-4734-b6f9-3eed971ceaa9` | Fleet-wide RISE rollup: Fleet Summary (WATCHDOG#/ZRAM#/OVERLAY#/HEALTH CHECK#/DOWN SMC# counts), Offline     |
|                                              |                                        |   SMCs (30d), Pending sites (RISE not yet deployed)                                                          |
| RISE Dashboard                               | `rise-stage0_5`                        | Earlier-stage RISE rollout view                                                                              |
| Sites not reporting                          | `fa620053-7cdf-4737-8be1-c60cd3b31b8d` | Per-cluster (RCP/RCT/WH) reporting-site counts + list of non-reporting sites                                 |
| Site Reporting Graph                         | `e0774e71-5f36-4f20-80c1-d84d7cfd9dde` | Time-series view of the above                                                                                |
| SMC Table                                    | `b796b0ef-7d6d-4a44-953c-3591960f84f7` | Per-host flavor-filtered detail table (non-RISE)                                                             |
| RPi SD Card Status                           | `f560056d-6545-4d01-ac4b-bfb086c32686` | SD card wear/status table, RPi flavors only                                                                  |
| Data Backlog / (1)Prometheus RW Receiver +   | `d4921bf0-…`,                          | Federation `remote_write` pipeline backlog — `Data Backlog` has 0 panels (unused/placeholder), the two RW    |
|   Sender Backlog                             |   `prom-rw-backlog`,                   |   Backlog dashboards are the live ones                                                                       |
|                                              |   `1prom-rw-backlog`                   |                                                                                                              |
| Servers Network / Servers System Information | `ddd96f19-…`, `c1b900ba-…`             | Backend infra servers, not SMC boxes — out of skill-smc scope                                                |

RISE dashboards exist **only** on `mcp-grafana-apn` because RISE is deployed to `rct`/`wh` flavors only (confirmed via the `flavor=~"rct|wh"` gate in the "Pending sites" panel query) — `rcp` (x86
non-RISE) and the NBN Accelerate cluster (`nbn_accelerate`/`nbn_wh`) run no RISE metrics at all, which is why they're absent from `mcp-grafana-nbn`.

### Graylog REST API Access (via Teleport App, no MCP)

There is no Graylog MCP server. Direct log queries (not dashboard/Sidecar-config work, which the `graylog_config_lint.sh` script already handles) go through the Graylog REST API, reached the same way
as any other internal HTTP app: a Teleport Application Access proxy, not a bare `curl` to the public hostname.

**Why a bare `curl` fails:** `apn-graylog.teleport.apn.au` is a Teleport-proxied app. An unauthenticated request (even with a valid Graylog API token in the `Authorization`/Basic-auth header) gets a
`302` redirect to `teleport.apn.au/web/launch/...` — Teleport intercepts the connection before it ever reaches Graylog, because the client presented no Teleport app certificate. Confirmed live
2026-09-07: this happens even with a correct token, so a 302 here means "not through the Teleport app proxy," not "bad token."

**Working method (verified live 2026-09-07, pandanus-park-smc01):**

```bash
# 1. One-time per session: log into the app on the APN cluster proxy
#    (tsh must already have a valid login to teleport.apn.au — `tsh status` to check,
#    `tsh login --proxy=teleport.apn.au` if not)
tsh --proxy=teleport.apn.au apps login apn-graylog

# This prints the mTLS cert/key paths, e.g.:
#   --cert /Users/<you>/.tsh/keys/teleport.apn.au/<user>-app/teleport.apn.au/apn-graylog-x509.pem
#   --key  /Users/<you>/.tsh/keys/teleport.apn.au/<user>

# 2. Query the Graylog REST API through the app cert, with the Graylog API token as
#    Basic-auth username and the literal string "token" as password (Graylog's convention
#    for token-based API auth — NOT a real password):
TOKEN=$(cat /path/to/.graylog-token)   # see token location note below
curl -s \
  --cert /Users/<you>/.tsh/keys/teleport.apn.au/<user>-app/teleport.apn.au/apn-graylog-x509.pem \
  --key  /Users/<you>/.tsh/keys/teleport.apn.au/<user> \
  -u "${TOKEN}:token" \
  -H "Accept: application/json" \
  --data-urlencode "query=source:pandanus-park*" \
  --data-urlencode "range=86400" \
  --data-urlencode "limit=30" \
  --data-urlencode "sort=timestamp:desc" \
  -G "https://apn-graylog.teleport.apn.au/api/search/universal/relative"
```

- `range` is relative, in **seconds** (86400 = 24h, 604800 = 7d).
- `query` is standard Lucene syntax against Graylog's indexed fields — wildcard with `*`.
- Response is JSON: `{"messages":[{"message": {...fields...}}], "total_results": N, ...}`.
- **A `source:<name>` filter must match the field value exactly** — SMC hostnames are indexed as `<site>-smc01` (e.g. `pandanus-park-smc01`), so `source:pandanus-park*` (not `source:pandanus-park`) is
  needed to catch it. Confirmed field: every SMC-originated message carries `source`, `_nodename`, and `tp_hostname`, all equal to the same `<site>-smc01` string, plus `tp_site` (bare site name, no
  `-smc01` suffix) and `path` (originating log file, e.g. `/var/log/smc-groups/dhcpd.log`).
- `total_results: 0` on a `source:`-scoped query is not proof of "no logs" by itself — check the node is actually shipping (see "Sites not reporting" dashboard above) and widen `range` before
  concluding a gap.
- CW-cluster flavors (`nbn_accelerate`, `nbn_wh`) would use the equivalent `cw-teleport01`/`teleport.communitywifi.net.au` proxy and whatever Graylog app that cluster exposes — not verified as of
  2026-09-07, confirm the app name with `tsh --proxy=teleport.communitywifi.net.au apps ls` before assuming parity.

**Token location (moved 2026-09-07):** the Graylog API token now lives at `skill-smc/.graylog-token` (this skill's own directory — gitignored in `skills_stuff`, `chmod 600`; the symlinked installs in
`~/.claude/skills`, `~/.codex/skills`, `~/.hermes` follow the same directory so the file is present there too, excluded from git by name not by directory). It was previously project-local at
`smc-file-writing-analysis/.graylog-token`; moved here so the credential travels with this access-method doc instead of being re-derived per project. The `smc-file-writing-analysis` project's
`justfile` (`GRAYLOG_TOKEN_FILE` variable) and `scripts/graylog_config_lint.sh` both reference this path directly, with `GRAYLOG_TOKEN` env var as the override. Reuse that same file/env-var convention
for ad hoc queries rather than creating a second copy.

---

