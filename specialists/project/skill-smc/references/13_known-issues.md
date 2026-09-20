# skill-smc Known Issues and Gaps

## Contents

- [Knowledge Gaps (by design — require execution layer)](#knowledge-gaps-by-design--require-execution-layer)
- [Coverage Gaps (partial knowledge)](#coverage-gaps-partial-knowledge)
- [Skill Staleness Risks](#skill-staleness-risks)
- [Fleet-Wide Architecture Risks (identified, not yet remediated)](#fleet-wide-architecture-risks-identified-not-yet-remediated)
- [Jump-Host Tooling Varies Per Box — `snmpget` Absent on Most SMC Boxes (confirmed 2026-09-20)](#jump-host-tooling-varies-per-box--snmpget-absent-on-most-smc-boxes-confirmed-2026-09-20)
- [Known Operational Bugs (rcp fleet — confirmed 2026-06-30)](#known-operational-bugs-rcp-fleet--confirmed-2026-06-30)
- [Known Operational Bugs (NBN Accelerate cluster — full fleet sweep, 2026-08-03)](#known-operational-bugs-nbn-accelerate-cluster--full-fleet-sweep-2026-08-03)
- [Known Site Issues (as of 2026-06-30)](#known-site-issues-as-of-2026-06-30)
- [Out of Scope (permanent)](#out-of-scope-permanent)
- [2026-07-28 — fleet fatrace sweep findings (all 16 rcp incl. new-looma)](#2026-07-28--fleet-fatrace-sweep-findings-all-16-rcp-incl-new-looma)
- [2026-08-18 — `delye-smc01` 5-minute reboot loop: a 2.6 GiB Laravel log vs a 3.81 GiB overlay (RESOLVED)](#2026-08-18--delye-smc01-5-minute-reboot-loop-a-26-gib-laravel-log-vs-a-381-gib-overlay-resolved)
- [2026-08-18 — `rise-watchdog.service` dead with `status=226/NAMESPACE` whenever overlay is off](#2026-08-18--rise-watchdogservice-dead-with-status226namespace-whenever-overlay-is-off)
- [2026-08-18 — Ubuntu's stock rsyslog logrotate has no size limit (fleet-wide)](#2026-08-18--ubuntus-stock-rsyslog-logrotate-has-no-size-limit-fleet-wide)
- [2026-08-18 — legacy `ozai` logger still writing post-RISE; graylog-sidecar logs accumulate forever](#2026-08-18--legacy-ozai-logger-still-writing-post-rise-graylog-sidecar-logs-accumulate-forever)
- [2026-08-18 — plaintext secrets in `group_vars`, and a copied Graylog config that shared them](#2026-08-18--plaintext-secrets-in-group_vars-and-a-copied-graylog-config-that-shared-them)
- [2026-09-08 — upstream keepalived VIP config bug: `lb_algo rr` silently ignores the lweb03 drain intent (`202.171.100.138`)](#2026-09-08--upstream-keepalived-vip-config-bug-lb_algo-rr-silently-ignores-the-lweb03-drain-intent-202171100138)
- [2026-09-11 — portal-FQDN regression: two separate incidents, one still live on 2 sites](#2026-09-11--portal-fqdn-regression-two-separate-incidents-one-still-live-on-2-sites)

---

## Knowledge Gaps (by design — require execution layer)

| Gap                                                  | Why                                                   | Mitigation                                                                            |
| ---------------------------------------------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Actual flattened topology output for a specific host | Requires executing `vars_plugins/topology_vars.py`    | Phase 3: ansible-wifi MCP                                                             |
|                                                      |   against live inventory                              |                                                                                       |
| Live service status, log content, running metrics    | Requires SSH access to the box                        | Direct `tsh ssh root@<hostname>` (no MCP — operator arranges `tsh login` manually per |
|                                                      |                                                       |   flavor's Teleport cluster) + `mcp-grafana` for metrics                              |
| Cross-flavor inventory impact at scale               | Requires running `ansible-inventory --list` ×         | Phase 3: ansible-wifi MCP                                                             |
|                                                      |   7 flavors                                           |                                                                                       |

## Coverage Gaps (partial knowledge)

| Area                             | Status                       | Notes                                                                                                                              |
| -------------------------------- | ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| x86 / apn flavor live validation | Not validated                | RUNBOOK flavor differences are from code inspection only; malik-rct01 is the only live-validated box                               |
| cnmaestro-provisioning internals | Partial, deployment side now | Deployment mechanism (`smc_cnmaestro_provisioning` role, `smc_ltp.yml` playbook, per-model Cambium hardware profiles, IP/SSID      |
|                                  |   well-documented            |   auto-allocation) now covered in `08_ansible-authoring.md` "smc_ltp Sub-Group". Still undocumented: `cnmaestro-provisioning.py`'s |
|                                  |   (2026-08-03)               |   actual runtime behavior against the CNMaestro cloud API (error handling, retry logic, what happens on a provisioning conflict) — |
|                                  |                              |   not live-validated                                                                                                               |
| NBN Accelerate API behavior      | Minimal                      | API call pattern noted; response handling and error states undocumented                                                            |
| Redis usage details              | Minimal                      | Used by cnmaestro-provisioning; key schema undocumented                                                                            |
| Kohana / Tstik web apps          | Minimal                      | Running on RCT; role config paths known; app internals not documented                                                              |
| RISE monitoring suite            | Partial                      | Unit names known; behavioral details from code inspection only                                                                     |
|   (riseclient, risengine)        |                              |                                                                                                                                    |
| Host-level (own) DNS resolution  | Newly documented 2026-07-03, | `systemd-resolved` stub is disabled by design (`DNSStubListener=no`, unconditional) — host DNS bypasses unbound/stubby/bind        |
|   architecture, as distinct from |   single-incident-grounded   |   entirely and goes straight to `external_dns_servers`. Confirmed via the garimba-smc01 RCA; not independently re-validated at any |
|   DHCP/LAN client DNS            |                              |   other site yet. See `02_service-map.md` + `06_failure-modes.md`                                                                  |
| Project → Teleport cluster       | Resolved 2026-07-31,         | APN project (`rcp`/`rct`/`wh` flavors + `apn` central-infra) → `teleport.apn.au`; nbn_accelerate project                           |
|   domain mapping (corrected      |   terminology                |   (`nbn_accelerate`/`nbn_wh` flavors + `cw` central-infra) → `teleport.communitywifi.net.au`. Covers all 7 inventory flavors       |
|   2026-09-08 — was mislabeled    |   fixed 2026-09-08           |   across 2 projects. Operators still arrange `tsh login` manually per site — this table is for orientation, not for hardcoding     |
|   "Flavor → ..."; the split is   |                              |   into scripts/tooling. See `01_overview.md` "Remote Access" and `03_communication-flows.md` §Backdoor SSH Access for the          |
|   by project, each project has   |                              |   raw-OpenSSH fallback path when `tsh ssh` itself is unreachable.                                                                  |
|   multiple flavors)              |                              |                                                                                                                                    |
| **NBN Accelerate cluster**       | Largely closed — full fleet  | `01_overview.md` "APN Cluster vs NBN Accelerate Cluster — Structural Comparison" and `08_ansible-authoring.md` "Flavor/Cluster     |
|   **coverage gap**               |   sweep done 2026-08-03      |   Conditional Branching" were structural/code-inspection only when written. **Full-fleet live validation 2026-08-03** (`tsh ssh` to |
|                                  |                              |   all 26 reachable `nbn_accelerate` hosts + both `nbn_wh` hosts, 28 total): Teleport domain, HTTPS-only portal, mobile-app         |
|                                  |                              |   backend, ClamAV+Lynis presence, Asterisk absence, non-`smc_ltp` DNS stack, and full hardware inventory all confirmed live — see  |
|                                  |                              |   "Known Operational Bugs (NBN Accelerate cluster — full fleet sweep, 2026-08-03)" above and `07_hardware-overlay.md` "NBN         |
|                                  |                              |   Accelerate / NBN WH Hardware Inventory". **Still not live-validated**: `cw` flavor itself (central-infra only, no site hosts to  |
|                                  |                              |   check), `aurukun-smc03` (unreachable at capture time); every troubleshooting entry in                                            |
|                                  |                              |   `05_troubleshooting.md`/`06_failure-modes.md`/this file's incident rows *besides* the NBN Accelerate bugs section above is still |
|                                  |                              |   an APN-cluster (`rcp`) site.                                                                                                     |
| **"Low touch" onboarding method ↔** | Confirmed,                   | All 7 low-touch sites (`guda-guda` pilot 2025-04-15, `umoona`, `warburton`, `beagle-bay`, `pandanus-park`, `old-looma`,            |
|   **`smc_ltp`** **link —**       |   operator-directed;         |   `new-looma`) are now `smc_ltp` group members — operator confirmed the link is real (low-touch onboarding implies `smc_ltp`) and  |
|   **resolved 2026-08-03**        |   mechanism confirmed manual |   directed adding the 3 missing sites (`umoona`/`warburton`/`beagle-bay`) to `inventories/rcp/prod`'s `smc_ltp` group, closing     |
|                                  |                              |   what had been a plain inventory gap, not a coincidental correlation. **Mechanism confirmed 2026-08-03: it's a manual step someone** |
|                                  |                              |   **has to remember** — no low-touch onboarding tooling automatically assigns `smc_ltp` group membership, and nothing enforces or  |
|                                  |                              |   checks that it happened. This is the actual root cause of the 3-site gap — treat this as a standing risk for any future          |
|                                  |                              |   low-touch site, not a one-off fixed with this correction; verify `smc_ltp:children` membership explicitly whenever a new         |
|                                  |                              |   low-touch site goes live rather than assuming it's automatic. Separately, Ansible-code-wise the *string* "low touch" still means |
|                                  |                              |   nothing: the one `low_touch` hit in the whole repo (`smc_bases_low_touch_provisioning: true` on `pierre-rcp01`, not a cohort     |
|                                  |                              |   member) is never read by any role/playbook — an orphaned var, not evidence of an implemented low-touch code path distinct from   |
|                                  |                              |   `smc_ltp` group membership itself. See `08_ansible-authoring.md` "'Low Touch' Onboarding Method and Site Deployment History".    |
|                                  |
## Skill Staleness Risks

- Service names and config paths may drift as ansible-wifi roles are updated.
- Flavor differences (RCT vs x86) are grounded in live RCT validation only; x86 assumptions are from role code inspection.
- **2026-07-03 correction**: the DNS resolver row in `02_service-map.md` previously generalized "unbound = RCT flavor, bind = non-RCT flavors" from the single initial RCT validation — this was wrong.
The real gate is `smc_ltp` inventory-group membership (orthogonal to flavor), confirmed by repo-wide grep across all inventories during the garimba-smc01 RCA. Treat any other flavor-generalized claim
in this pack derived from a single-host validation as unverified for other flavors until independently checked.
- **2026-08-03 correction**: that same garimba-smc01 RCA grep undercounted `smc_ltp` group membership as "only `rcp`/guda-guda" — it was `.yml`-scoped and missed `inventories/rcp/prod`, the INI-format
static inventory where the group is actually defined. Direct read of `prod` initially showed 4 member sites: `guda-guda`, `pandanus-park`, `old-looma`, `new-looma`. Same failure class as the pattern
below — grep-only inventory investigation missing a non-`.yml` file. See `02_service-map.md` and `08_ansible-authoring.md` "smc_ltp Sub-Group" for the corrected, fuller picture (including the
previously undocumented CNMaestro-provisioning purpose of the group, mislabeled elsewhere in this pack as "mDNS").
- **2026-08-03, same day, superseding the count above**: operator confirmed `smc_ltp` should have **7** members, not 4 — the group is meant to track "low touch" onboarding sites, and 3 (`umoona`,
  `warburton`, `beagle-bay`) were low-touch-deployed but missing from `inventories/rcp/prod`'s `smc_ltp` group, a real inventory gap rather than a grep miss this time. Operator directed the fix
  directly: `warburton_smc_ltp`/`beagle-bay_smc_ltp`/`umoona_smc_ltp` child groups added to `inventories/rcp/prod` (`smc_ltp:children` now lists all 7), verified via `ansible-inventory --list` and
  `ansible-playbook --syntax-check smc_ltp.yml`, both clean. This resolves the "low touch ↔ smc_ltp link unresolved" row above — see its updated text. **Uncommitted** as of this edit — a real,
  file-level production Ansible inventory change (not yet run against any live SMC).
- **2026-07-28 correction**: `10_captive-portal.md` previously stated flatly that "PHP-FPM processes `.php` files" and that a permanent Ansible `SetHandler` fix "landed 2026-06-26". **Both were
  wrong** — generalizations from `family-friendly-smc01` hotfix work in June 2026 that never reached the production fleet. Verified on three sampled `rcp` hosts: zero `php*-fpm` packages,
  `libapache2-mod-php` installed, `apache2ctl -M` shows `php_module`, no `/etc/php/8.1/fpm/` directory; and repo-wide grep finds no `SetHandler` in any template, with the enabled-modules list being
  only `rewrite` and `ssl`. **This is the third instance of the same failure pattern in this pack** (after the 2026-07-03 DNS row and the 2026-07-09 MySQL row): a single host's observed behaviour
  written up as fleet-wide architecture. When adding architecture claims, state the validation scope explicitly — which hosts, which flavors, verified how.
- Prometheus alert names and thresholds are taken from `roles/smc_prometheus/` at commit `0d0c91a`; these may change.
- **Unreconciled duplicate-fix risk (flagged, not resolved):** `.remember` daily logs (2026-07-24/07-26) describe an "apt-lock-race" backport (`/proc/locks` probe, an `is sequence` trap, a
`tmpfiles.d` template, the 44GB journal reclaim, and reordering lock-clearing in `custom_apt_update_cache.yml`/`custom_apt_install.yml`) fixing `rc:100 apt-daily-upgrade` collisions. This pack already
documents a *different*-sounding apt-daily-upgrade fix (masking `apt-daily.timer`/`apt-daily-upgrade.timer`, commit `0c51cb1`, see `08_ansible-authoring.md`). It is not established whether these are
the same fix described two ways or a genuine additional hardening layer — confirm against the actual commits before treating both as independently true.
- **2026-07-09 correction**: the "Kohana PHP tries MySQL (not installed on rcp)" bug row below was diagnosed from smc-file-writing-analysis's 2026-06-02 burringurrah audit, which found no
`/var/lib/mysql` and concluded the 1min/5min/daily Kohana cron jobs were failing local DB connections. ansible-wifi ADR-002 (`.archcore/adr/adr-002-eclipse-kohana-captive-portal-architecture.md`)
documents the exact same three cron cadences as Kohana's sync jobs with a **remote Eclipse server** (`wifi.activ8me.net.au:443`), not local MySQL — Kohana is the local half of a two-tier
captive-portal auth system, and the `ECLIPSE_MARK` iptables chain (gates `bridge_501` public WiFi) is only populated after a successful Eclipse sync. The "MySQL not installed" fact may still be true
but is not established as the actual failure path for these specific cron errors. Treat the root cause as unresolved until a live node's actual PHP error text and Eclipse connectivity are checked —
see `smc-file-writing-analysis` memory-keeper key `smc.audit.kohana.eclipse.correction.20260709`.
- **"Community wifi" naming collision — this is why this pack calls the `cw`/`nbn_accelerate`/`nbn_wh` customer "NBN Accelerate," not "Community WiFi" (found 2026-08-03, operator-directed rename same
  day).** `local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/{README,problem}.md` use the phrase "community-wifi"/"community wifi" generically, to mean **`rcp` sites within the APN
  network**
(i.e. an APN-cluster community's WiFi service) — a completely different sense from the `cw`/`nbn_accelerate`/`nbn_wh` customer this pack documents in `01_overview.md`. Anyone grepping the ansible-wifi
knowledge tree for "community wifi" to find NBN-Accelerate-cluster content will hit that apn/routing-issue file instead and may misattribute apn-cluster routing-issue findings to the wrong cluster.
This pack deliberately avoids the ambiguous term as the cluster's display name — use "NBN Accelerate cluster" (or the literal `teleport.communitywifi.net.au` domain / `cw`/`nbn_accelerate`/`nbn_wh`
flavor names) instead. Check which sense is meant before treating any "community wifi" hit elsewhere in the ansible-wifi tree as evidence about this cluster.
- **OPA policy layer has no dedicated `cw` entry, and `environments.json` is incomplete/possibly stale (found 2026-08-03).** `opa/data/flavors.json` defines per-flavor policy for `rcp`, `nbn_wh`,
`nbn_accelerate` only — no `cw`, `apn`, `rct`, or `wh` entries exist. `opa/data/environments.json`'s prod `inventory_groups` list is similarly partial (`rcp`, `nbn_wh`, `nbn_accelerate` only). Not
established whether this is intentional scoping (OPA gating only applies to flavors that run destructive-command-guarded playbooks) or a genuine coverage gap — confirm against OPA policy intent before
assuming `cw`/`apn`/`rct`/`wh` are ungated by design.

## Fleet-Wide Architecture Risks (identified, not yet remediated)

| Risk                             | Detail                                                                                                         | Evidence basis                                   |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| Stubby DoT upstream has          | Exactly one `upstream_recursive_servers` entry (`127.0.0.1@60853`, reached via an autossh local port forward   | garimba-smc01 DNS RCA,                           |
|   no failover                    |   to Teleport) is configured fleet-wide, identically, for every non-`smc_ltp` site —                           |   2026-07-03, `roles/smc_dns/files/stubby.yml`   |
|                                  |   `round_robin_upstreams: 1` is set but meaningless with a single upstream                                     |                                                  |
| No monitoring for the autossh    | Repo-wide search found no Prometheus alert rule specific to `autossh-teleport.service` state or DNS-upstream   | garimba-smc01 DNS RCA, 2026-07-03                |
|   local forward or Stubby        |   health; if the Teleport connection drops, DHCP/LAN client DNS on that SMC has no fallback once Unbound's     |                                                  |
|   upstream reachability          |   cache expires (positive TTL up to 24h, negative TTL up to 5min) — failure would be silent until users notice |                                                  |
| **No HTTP-level captive-portal** | Nothing probes whether the portal actually serves. The only portal-adjacent signals are the Kohana             | rcp portal outage RCA, 2026-07-28,               |
|   **monitoring anywhere in**     |   `status:update:usage` / `status:update:status` crons, which run as **root** and therefore keep succeeding even |   `issues/rcp-fleet/rcp-captive-portal-cache-\`  |
|   **the fleet**                  |   when the portal is dead for `www-data` — Eclipse keeps receiving data throughout an outage. This let 10 of   |   `perms-outage-20260728_1240.md`                |
|                                  |   16 `rcp` sites sit fully down for 7 days undetected. A naive probe would not help either: the failure        |                                                  |
|                                  |   returns **HTTP 200** with a 40-byte error body, so any check must assert on response body content or size, not |                                                  |
|                                  |   status code                                                                                                  |                                                  |
| Host-level DNS resolution        | `DNSStubListener=no` + `Cache=no` unconditional on all non-`smc_ltp` hosts — host glibc is directly exposed to | See `06_failure-modes.md` — mitigation candidate |
|   bypasses any stub/cache        |   any WAN-path DNS anomaly with no resolver-level mitigation in place today                                    |   exists but is not yet fleet-validated          |
| `smc_qos` role exists but is | last == 'rct'` — silently no-ops on every `rcp`/`nbn_accelerate` site | `03_communication-flows.md` previously stated | routing-issue investigation, |
|   gated `when: |  |   Ansible-managed QoS was "planned, not started" |   `ingress-shaping-not-managed-or-extended-\` |
|   inventory_dir.split('/') |  |   — that's stale. The role exists and |   `20260730_1245.md` |
|  |  |   `--tags qos` runs during rcp deploys, it just |  |
|  |  |   never fires due to the gate. Manual TBF/ifb |  |
|  |  |   shaping remains the only active mechanism on |  |
|  |  |   rcp, and it has NOT been extended to |  |
|  |  |   newly-fixed VLANs at every site (2 missing at |  |
|  |  |   Pandanus Park, 10 at Umoona, 8 at Old Looma as |  |
|  |  |   of 2026-07-30) |  |
| Fixed-topology                   | Confirmed at Horn Island: the boilerplate two-interface starlink block is applied regardless of whether a      | routing-issue investigation,                     |
|   `starlink01`/`starlink02`      |   backup circuit actually exists, inflating `interfacecheckv2.sh`'s per-cycle ping count for no operational    |   `starlink-backup-no-lease-l2-investigation-\`  |
|   interfaces defined even at     |   benefit. Topology generation should condition this block on actual provisioning, not apply it                |   `20260730_1400.md`                             |
|   sites with no Starlink         |   unconditionally per flavor                                                                                   |                                                  |
|   circuit ordered                |                                                                                                                |                                                  |
| `watchdog.auto_reboot: 0` does   | (1) Line 16 templates `WATCHDOG_AUTO_REBOOT = "{{ watchdog.auto_reboot \| int }}"` without wrapping in `int()` | ansible-wifi session, 2026-09-03, open item —    |
|   not actually disable automatic |   like every other templated scalar in the file, so it renders the **string** `"0"` — truthy in Python — meaning |   SCRATCHPAD.md `ansible-wifi`                   |
|   reboots — two independent      |   the guard at line 641 is always true. (2) Separately, the second reboot path at line 653                     |                                                  |
|   defects in                     |   (`if not args.dry_run: reboot()`) never consults the flag at any value. Confirmed live, not from the         |                                                  |
|   `roles/smc_rise_watchdog/\`    |   template alone: `/opt/rise/status/watchdog.json` on a `flavor` set to `auto_reboot: 0` emits                 |                                                  |
|   `templates/rise_watchdog.py.j2` |   `"auto_reboot":"0"` (quoted). **Not yet fixed — do not apply blind.** `fb7ff6fa`-style precedent exists of a |                                                  |
|                                  |   guard being deliberate and masking a spurious-reboot case the diff doesn't show; check `rct` and `nbn_wh`    |                                                  |
|                                  |   values before changing anything                                                                              |                                                  |
| **No per-device `role: internet` | `roles/prometheus_prometheus/files/rules.yml` has `NodeStarlinkInterfacecheckPacketLoss` (~line 173),          | ansible-wifi session,                            |
|                                  |   aggregated across ALL `role="starlink"` devices, firing only at                                              |                                                  |
| Prometheus alert exists —**      | 100% combined loss sustained `for: 60m` — appropriate for a small backup-link category where losing all of     | 2026-09-08, galiwinku-smc01                      |
|                                  |   them at once is the only thing worth paging on. There is                                                     |                                                  |
| **only an aggregated Starlink rule** | **no equivalent alert for `role="internet"` interfaces at all.** The only other related rule,                  | vlan523/vlan525 outage                           |
|   **and a stale-collector rule,** |   `HostInterfacecheckTextfileCollectorNotUpdated` (~line 383), checks whether `interfacecheckv2.sh`'s own      |                                                  |
|   **neither of which pages on a** |   textfile output has gone stale (file-mtime > 450s) — it says nothing about whether an individual             |                                                  |
|   **single dead internet link**  |   `role: internet` device is failing while the script continues running fine and faithfully reporting that     |                                                  |
|                                  |   failure into an unwatched metric (`my_node_interfacecheck_loss_ratio`). This is fleet-wide, not              |                                                  |
|                                  |   galiwinku-specific — every multi-WAN SMC site has the same blind spot, and it is precisely why the           |                                                  |
|                                  |   vlan523/vlan525 outage at galiwinku (see `06_failure-modes.md` "interfacecheckv2.sh's Unconditional dhclient |                                                  |
|                                  |   Restart") went undetected for hours, requiring manual SSH diagnosis. **Recommended fix (not yet implemented** |                                                  |
|                                  |   **anywhere):** a PER-DEVICE alert on `my_node_interfacecheck_loss_ratio` scoped to `role="internet"`, NOT    |                                                  |
|                                  |   aggregated like the Starlink rule (one-of-many internet links being down is expected/tolerable and shouldn't |                                                  |
|                                  |   page immediately, but a sustained single-device failure — 30-60+ minutes — should), modeled closely on the   |                                                  |
|                                  |   Starlink rule's structure but per-device instead of aggregated, with a threshold realistic for this fleet's  |                                                  |
|                                  |   known link flakiness. See `SKILL.md` "Key Prometheus Alerts Reference" — that table lists                    |                                                  |
|                                  |   `NodeStarlinkInterfacecheckPacketLoss` but has no `role="internet"` row; do not read its absence there as    |                                                  |
|                                  |   evidence the coverage exists elsewhere.                                                                      |                                                  |

## Jump-Host Tooling Varies Per Box — `snmpget` Absent on Most SMC Boxes (confirmed 2026-09-20)

`net-snmp` client tools are **missing on most SMC boxes, and their presence does not follow the inventory flavour**. Sampled 2026-09-20:

| Box | Flavour | `snmpget` |
| --- | --- | --- |
| `hope-vale-smc01` | nbn_accelerate | present |
| `burringurrah-smc01` | rcp | present |
| `wandawuy-smc01` | nbn_accelerate | **missing** |
| `amata-smc01` | nbn_accelerate | **missing** |
| `doomadgee-smc01` | nbn_accelerate | **missing** |
| `tjuntjuntjara-smc01` | rcp | **missing** |

Two of six sampled boxes have it, one from each flavour. An earlier version of this note said the split followed the `rcp`/`nbn_accelerate` boundary — that was drawn from three boxes and is wrong.
**Treat `snmpget` as per-box and probe for it; do not infer it from the flavour.**

**Why it matters beyond the missing package:** a device sweep that shells out to `snmpget` from the SMC box and swallows stderr will report every device at those sites as unreachable. That happened
on 2026-09-20 — 20 Cambium APs across two sites were briefly recorded as down when the devices were healthy: ping clean, HTTPS 200, REST API answering normally. The failure was `command not found`
on the jump host.

**Before concluding a site is unreachable from an SMC box**, prove the jump host has the tool (`command -v snmpget`) and prove the device is up by a second, independent path (`ping`, or a `curl`
HTTPS probe). Do not let a sweep's own fallback string stand as evidence of a device state.

**Workaround without installing anything:** reach the device's REST API through a Teleport port-forward (`tsh ssh --proxy=<proxy> -L <local>:<device-ip>:443 root@<node>`) and query it directly from
the workstation. Note this does **not** substitute for SNMP itself — SNMP is UDP and a Teleport `-L` forward carries TCP only, so an SNMP-specific test cannot be run this way. These boxes run
overlayroot, so anything installed to work around this is lost on reboot unless the lower dir is remounted read-write first.

## Known Operational Bugs (rcp fleet — confirmed 2026-06-30)

| Bug                                       | Impact                                                                                                  | Fix location                                   |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| `interfacecheckv2.sh` outputs empty float | 2,880 syslog entries/day fleet-wide                                                                     | **Fix drafted + committed 2026-07-15** (`ae838c2`, |
|   → node_exporter parse error             |                                                                                                         |   writes `NaN` on empty sed match instead of   |
|                                           |                                                                                                         |   feeding it into `bc`) — deploy deferred to a |
|                                           |                                                                                                         |   later session, not yet on any node.          |
|                                           |                                                                                                         |   `roles/smc_network/templates/\`              |
|                                           |                                                                                                         |   `interfacecheckv2.sh.j2`                     |
| Kohana PHP cron error (root cause revised | 1,440 syslog entries/day fleet-wide; possible silent bridge_501 public WiFi outage on Eclipse-enabled   | **Investigated live 2026-07-15, no active**    |
|   2026-07-09 — see below)                 |   sites, not just log spam                                                                              |   **failure found.** The 2026-07-09 theory does |
|                                           |                                                                                                         |   not hold up: `wifi.activ8me.net.au:443` TLS  |
|                                           |                                                                                                         |   handshake clean, `bridge_501` up,            |
|                                           |                                                                                                         |   `ECLIPSE_MARK` correctly populated, manual   |
|                                           |                                                                                                         |   `kohana status:update:status` exits 0.       |
|                                           |                                                                                                         |   `rpm`/`sbltm-cli` "not found" errors seen    |
|                                           |                                                                                                         |   during the manual run are from an unrelated  |
|                                           |                                                                                                         |   Eclipse-server-side dev script, not this     |
|                                           |                                                                                                         |   project's concern. No fix applied — nothing  |
|                                           |                                                                                                         |   currently                                    |
|                                           |                                                                                                         |   reproducing. `roles/smc_application/`        |
| `sbdm.prom` = 0 bytes on tjuntjuntjara +  | No SSD health metrics shipped                                                                           | `roles/smc_node_exporter/`                     |
|   burringurrah — likely fleet-wide        |                                                                                                         |                                                |
| `smc_graylog` RISE defaults               | **FIXED 2026-06-30** — was actively crash-looping sidecar on tjuntjuntjara. Fix:                        | `inventories/rcp/group_vars/smc_bases.yml` ✓   |
|   (`graylog_sidecar_extra_tags`,          |   `inventories/rcp/group_vars/smc_bases.yml` — see ansible-authoring ref. **Deploy-lag gotcha (found**  |                                                |
|   `graylog_sidecar_extra_log_files`) lack |   **2026-07-14 on horn-island):** the group_vars fix landing doesn't retroactively fix already-deployed |                                                |
|   rcp override                            |   nodes — horn-island's on-disk sidecar config still had the old `rise` tag/paths and had been `failed` |                                                |
|                                           |   since 2026-07-03 until a normal `smc_bases.yml`+`smc_graylog.yml` redeploy regenerated it from the    |                                                |
|                                           |   (already-correct) current vars. If a node's sidecar is `failed` referencing `/var/log/rise`, check    |                                                |
|                                           |   whether it's simply never been redeployed since 2026-06-30 before assuming a new bug.                 |                                                |
| `apt_info.py` called `cache.update()`     | **FIXED 2026-07-15 — deployed fleet-wide, 12/12 nodes.** Was independent of and untouched by the        | `roles/smc_node_exporter/files/apt_info.py` —  |
|   unconditionally on every 5-min cron     |   `apt-daily.timer`/`apt-daily-upgrade.timer` fix (commit `0c51cb1`). Root cause traced one level       |   ansible-wifi commit `4889af8`, deployed      |
|   tick — a full `apt update` (network     |   deeper than first assumed: `cache.update()` is what fired `20apt-esm-hook.conf`'s                     |   12/12, not pushed to origin                  |
|   fetch + gpgv Release-signature          |   `APT::Update::Pre-Invoke` hook (`systemctl start --no-block apt-news.service esm-cache.service`) —    |                                                |
|   verification against every repo),       |   the downstream `apt-news.service`/`esm-cache.service` masking (see next row) is a belt-and-suspenders |                                                |
|   288×/day of apt.data.*/gpgv writes      |   cleanup, not the primary fix; masking those two alone would not have stopped the update-and-verify    |                                                |
|                                           |   cycle itself. Fix: removed `cache.update()` — the script already tolerated it failing and falling     |                                                |
|                                           |   back to the existing index, so this is functionally identical to that already-accepted path. Deployed |                                                |
|                                           |   via a scoped ansible ad-hoc `copy` targeting only `apt_info.py` (not the full `--tags node_exporter`  |                                                |
|                                           |   role, which would have bundled in the separate, not-yet-approved smartmon.py Part 1 rollout to 10     |                                                |
|                                           |   nodes lacking it — caught via dry-run showing `changed=2-4` instead of the expected 1 on several      |                                                |
|                                           |   hosts). Verified fleet-wide: `cache.update()`/`contextlib` import confirmed absent, script runs       |                                                |
|                                           |   clean, `apt_info.prom` still populates. Explained why the post-timer-fix re-baseline (2026-07-15      |                                                |
|                                           |   13:23) showed no measurable write-rate improvement on 11/12 nodes. See                                |                                                |
|                                           |   `smc-file-writing-analysis/ROADMAP.md` Completed milestones and `docs/log-audit-results.md`           |                                                |
|                                           |   2026-07-15 entries.                                                                                   |                                                |
| `apt-news.service` + `esm-cache.service`  | **FIXED 2026-07-15 — masked fleet-wide, 12/12 nodes.** Belt-and-suspenders cleanup, deployed same evening | `roles/smc_system/tasks/main.yml` —            |
|   fire as a side effect of the            |   as the row above. **Version-gated gotcha found live**: only shipped by `ubuntu-advantage-tools` ≥28.x |   ansible-wifi commit `97854ee`, deployed      |
|   `apt_info.py` issue above (row above),  |   (27.9~22.04.1 on tjuntjuntjara doesn't ship them; 28.1~22.04 on horn-island does) —                   |   12/12, not pushed                            |
|   not independently                       |   `systemd: masked: yes` fails hard (`Could not find the requested service`) on any node still on the   |                                                |
|                                           |   older version since it queries current state first. Fixed by masking via a direct `/dev/null` symlink |                                                |
|                                           |   instead (`file: state: link`, what `systemctl mask` does under the hood) — works regardless of unit   |                                                |
|                                           |   existence. Full detail: `08_ansible-authoring.md` "apt-news.service + esm-cache.service Mask".        |                                                |
| `my_node_network_device_info`             | `up{instance="<host>:9100"} == 1` and base kernel network metrics (`node_network_receive_bytes_total`   | `roles/smc_node_exporter/` — unconfirmed which |
|   (per-interface device/role/topology     |   etc.) are present and correct on all three — only this specific metric is absent, so `node_exporter`  |   collector/exporter path emits this metric;   |
|   registry metric) returns **zero series** on |   scraping health alone does not prove this metric is populated. Breaks any Grafana panel/query keyed   |   not yet traced to source                     |
|   old-looma, new-looma, and horn-island   |   on `role`/`device` labels for these three sites (e.g. the `${role}`/`${ethernet}` panels on the *SMC  |                                                |
|   (rcp) — confirmed 2026-07-29            |   Network* dashboard silently show nothing). **Not explained** — old-looma/new-looma are also the most  |                                                |
|                                           |   severely topology-stale sites in the 2026-07-29 routing investigation, which invites a "same root     |                                                |
|                                           |   cause as the dhclient-hook staleness" guess, but horn-island is healthy/unaffected by that issue, so  |                                                |
|                                           |   a single shared cause doesn't hold across all three. If picked up: check whether this metric is       |                                                |
|                                           |   populated by a textfile-collector script rendered per-site from `topology_vars` (like the dhclient    |                                                |
|                                           |   hook) — if so it would be a fourth topology-derived render that can silently drift, alongside the     |                                                |
|                                           |   hook, netplan, and the service-inventory table                                                        |                                                |
| Four units fail on every boot on `rcp`    | `isc-dhcp-server6.service` (DHCPv6 unused fleet-wide by policy — same root cause as the                 | `roles/smc_system/tasks/main.yml` —            |
|   hardware for structural,                |   separately-confirmed NBN Accelerate row below, but this fix is `rcp`-scoped, not shared with that     |   ansible-wifi commit `2dee86a8`,              |
|   non-configurable reasons — now masked,  |   fleet), `fwupd-refresh.service` (this hardware has no fwupd-manageable devices),                      |   pushed 2026-09-03                            |
|   `hotspot_flavor == 'rcp'` only (commit  |   `dhclient@eth0.service` (`eth0` is never a real interface under predictable naming on this hardware), |                                                |
|   `2dee86a8`, 2026-09-03)                 |   and the ASUS keyboard-backlight unit (no physical keyboard present). Fix masks all four via           |                                                |
|                                           |   `roles/smc_system/tasks/main.yml` plus a `systemctl reset-failed` pass to clear the stale failed      |                                                |
|                                           |   state masking alone leaves behind (`failed_when: false` there is deliberate — no failed state is the  |                                                |
|                                           |   desired outcome, not an error). Not assessed for other flavors — do not assume it applies to          |                                                |
|                                           |   `wh`/`nbn_wh`/`rct`/`nbn_accelerate` without separately confirming the same root causes hold          |                                                |

## Known Operational Bugs (NBN Accelerate cluster — full fleet sweep, 2026-08-03)

**Full-fleet live `tsh ssh` sweep, not a spot-check**: all 26 reachable `nbn_accelerate` sites plus both `nbn_wh` sites (`bungardi-smc01`, `darlngunaya-smc01`) — 28 hosts total, effectively the entire
NBN Accelerate cluster minus `aurukun-smc03` (in the static inventory but not visible in `tsh ls` at capture time) and the `cw`/central-infra nodes. Superseded the earlier same-day 2-host spot-check
(`warakurna-smc01`/`indulkana-smc01`). Collected via the new `scripts/collect-fleet-health.sh` + `scripts/fleet-health.justfile`. **`nbn_wh` is the `wh`-flavor equivalent on this cluster** (same RPi
hardware class as `rct`/`wh` on the APN cluster, operator-confirmed) — every `wh`-flavor expectation (RPi ARM64, Swissbit SD storage, overlayroot) is the baseline `nbn_wh` should be compared against,
not `nbn_accelerate`'s x86 baseline.

**Every code-inspection-only claim from the earlier gap-fill confirmed, 28/28 hosts**: Teleport domain (`teleport.communitywifi.net.au:443`), HTTPS-only portal with on-box TLS termination, mobile-app
backend + `apn-mqtt-client` + url_capture (v1 path) present on all 26 `nbn_accelerate` hosts (absent on both `nbn_wh` hosts — flavor-gated as documented), ClamAV+Lynis installed on all 26
`nbn_accelerate` hosts and absent on both `nbn_wh` hosts, Asterisk absent everywhere, non-`smc_ltp` DNS stack everywhere.

### Hardware inventory (new — no prior live chassis data existed for this cluster)

| Chassis                                    | Count | CPU                           | RAM   | Storage                     | Flavor           |
| ------------------------------------------ | ----- | ----------------------------- | ----- | --------------------------- | ---------------- |
| AAEON BOXER-6641                           | 11    | Intel Core i5-8500T @ 2.10GHz | 15Gi  | Transcend TS128GSSD420K SSD | `nbn_accelerate` |
| AAEON BOXER-6404                           | 15    | Intel Celeron J1900 @ 1.99GHz | 7.7Gi | Innodisk CFast 3ME3         | `nbn_accelerate` |
| Raspberry Pi (Cortex-A72, `-raspi` kernel) | 2     | ARM64, 4-core Cortex-A72      | 7.6Gi | Swissbit SB AFNI0 microSD   | `nbn_wh`         |

No dmidecode data on the 2 `nbn_wh` hosts (expected — RPi boards have no DMI/SMBIOS tables, same as `rct`/`wh`). Both `nbn_wh` hosts show `Swap: 0B` and no `zram0` device in `lsblk` — **contradicts**
`07_hardware-overlay.md`'s "RPi flavor → zram swap" row as a universal claim; either `nbn_wh` doesn't get zram unlike `rct`/`wh`, or zram provisioning is flavor-specific in a way not yet checked
against live `rct`/`wh` hosts either. Not resolved — flagged in `07_hardware-overlay.md`.

### Bugs and anomalies found

| Bug | Impact | Fix location |
|---|---|---|
| `clamav-freshclam.service` | Fleet runs `clamav 0.103.11+dfsg-0ubuntu0.22.04.1` | **Confirmed, not yet remediated.** Fix: upgrade `clamav`/`clamav-freshclam` fleet-wide to 1.4 LTS (current) or 1.0 LTS (older |
|   chronically failing — **ROOT** |   uniformly (one host, `warakurna-smc01`, on `0.103.12` — |   supported alternative) — no automated ClamAV-version-update pipeline exists for this cluster (consistent with the |
|   **CAUSE CONFIRMED** |   same EOL branch). **ClamAV's 0.103 branch reached** |   already-documented absence of an automated kernel-update pipeline, `01_overview.md`), so nothing will self-correct this |
|   **2026-08-03: ClamAV 0.103.x** |   **end-of-life for database updates on 2025-09-14** |   without a deliberate package-upgrade rollout via `roles/smc_bases.yml`. Confirmed on all 26 reachable `nbn_accelerate` |
|   **is past end-of-life for** |   ([ClamAV blog](https://blog.clamav.net/2025/03/advance-notice-end-of-life-for-clamav.html)); after that date the CDN actively rejects |   hosts (see `scripts/fleet-health.justfile`'s `freshclam-check` recipe). No comparison fleet exists on `apn`-cluster |
|   **database updates** |   `freshclam` requests from any 0.103.x client with HTTP |   (ClamAV isn't deployed there per the flavor gate). |
|  |   403 ("Forbidden; Blocked by CDN") — exactly the signature |  |
|  |   captured on all 26 `nbn_accelerate` hosts, exit code 17, |  |
|  |   `This is fatal. Retrying later won't help. Exiting now.`. |  |
|  |   **This explains the 10-month staggered failure-date spread** |  |
|  |   (2025-10-02 → 2026-07-30): a host only flips to `failed` |  |
|  |   the first time its `freshclam` timer runs *after* the |  |
|  |   2025-09-14 cutoff — hosts with different timer schedules |  |
|  |   or later provisioning dates would trip the block at |  |
|  |   different times, not simultaneously. The three hosts |  |
|  |   sharing 2025-10-02 exactly (`arreyonga`, `kowanyama`, |  |
|  |   `mindi-rardi`) are consistent with a shared timer |  |
|  |   schedule that first fired ~18 days post-cutoff. ClamAV |  |
|  |   0.103.4+ added a 24h cool-down for CDN-blocked clients |  |
|  |   specifically, but freshclam still treats the block as |  |
|  |   fatal — **no version of "wait and retry" fixes this; only** |  |
|  |   **upgrading ClamAV does.** `clamav-daemon` stays `active` on |  |
|  |   every host (still scanning) but with a virus database |  |
|  |   frozen at whatever it had before the block, degraded |  |
|  |   fleet-wide. Not cluster-specific, not a firewall/proxy |  |
|  |   issue, not `nbn_accelerate`-specific — this would affect |  |
|  |   any fleet anywhere still running 0.103.x past 2025-09-14. |  |
| `nbn_wh` overlayroot **not yet** | `smc_rise_deploy.yml` (`ansible-wifi` root playbook) | last in ['rct', 'wh', | grep | Tracked, not a bug — re-check `mount \| grep overlay` on `bungardi-smc01`/`darlngunaya-smc01` after the planned rollout |
|   **active** — planned rollout, |   explicitly targets `inventory_dir.split('/') |   'nbn_wh']` — `nbn_wh` is coded as a RISE/overlay-rollout target alongside `rct`/`wh`. Live on both `nbn_wh` hosts: `mount |   overlay` returns nothing — no overlayroot active yet. **Operator confirmed the plan is to enable overlay on these two `nbn_wh` sites in the near future** — this is pre-rollout current state, not an unexplained gap or a stalled/reverted deployment. `darlngunaya-smc01`'s |   lands to confirm it took; until then this row documents expected pre-rollout state. `roles/smc_rise_overlay/`, |
|   not a bug |  |  |   318-day uptime is consistent with it simply not having been reached by this specific rollout yet. |   `smc_rise_deploy.yml` line ~316. See `08_ansible-authoring.md` and `07_hardware-overlay.md` "NBN Accelerate / NBN WH |
|   (operator-confirmed |  |  |  |   Hardware Inventory" for the full picture. |
|   2026-08-03) |  |  |  |  |
| `koonibba-smc01` at **95% root** | Approaching full — worth an operator disk-usage check | Not investigated further — `koonibba-smc01` disk contents not examined (would need a live `du`/`df -h` breakdown by |
|   **disk usage**, fleet's |   before it becomes an outage. Same host also runs the |   directory, not run this sweep). |
|   highest by a wide margin |   fleet's oldest kernel (`5.15.0-79-generic` vs the fleet |  |
|   (next is `warakurna-smc01` |   norm of `-117`/`-119`; `warakurna-smc01` is the opposite |  |
|   at 65%) |   outlier at `-133`, newer than everyone else) — two |  |
|  |   independent signs this host hasn't been touched by a |  |
|  |   routine maintenance pass in a long time, consistent with |  |
|  |   the already-documented absence of an automated |  |
|  |   kernel-update pipeline for the cw-cluster |  |
|  |   (`01_overview.md` "APN Cluster vs NBN |  |
|  |   Accelerate Cluster"). |  |
| `fwupd-refresh.service` | Firmware-metadata refresh failing, not security-critical | Not investigated — `fwupd-refresh.service`, 3 hosts only, not fleet-wide. |
|   failed on 3/28 hosts |   like the ClamAV finding above, but same general class of |  |
|   (`bungardi-smc01`, |   "outbound CDN/metadata fetch quietly broken" — possibly |  |
|   `darlngunaya-smc01`, |   related to the same egress-path hypothesis being |  |
|   `warakurna-smc01`) — |   considered for the freshclam finding, possibly unrelated. |  |
|   minor, low-priority |   Not investigated. |  |
| `isc-dhcp-server6.service` | Every single host shows this in `systemctl --failed`. This | N/A — expected behavior, no fix needed. |
|   failed on **28/28 hosts** — |   fleet disables IPv6 at the kernel level by policy |  |
|   confirmed benign, not |   (`08_ansible-authoring.md` "IPv6 Disable Policy") — an |  |
|   a bug |   IPv6 DHCP server service failing to bind on an |  |
|  |   IPv6-disabled host is the expected, correct outcome, not |  |
|  |   a defect. Documented here explicitly so a future |  |
|  |   `systemctl --failed` audit doesn't waste time |  |
|  |   re-investigating it. |  |

### Evidence basis

Direct `tsh ssh root@<host>` read-only commands via `scripts/collect-fleet-health.sh`, this session, 28/28 targeted hosts successful (two-batch capture after a mid-run script edit corrupted the first
batch — see the script's own header note on why editing a running script file is unsafe). Raw evidence retained at
`local-knowledge-ansible/ansible-wifi/issues/nbn-accelerate/fleet-hardware-audit-20260803/` (relocated from `skill-smc/evidence/` per this pack's evidence-retention policy — see `scripts/README.md`).
Not covered: `cw` flavor itself (central-infra only, no site-level hosts to check), `aurukun-smc03` (not reachable via `tsh ls` at capture time).

## Known Site Issues (as of 2026-06-30)

| Site                      | Issue                                            | Status                                                                                                                |
| ------------------------- | ------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| kalumburu-smc01           | ~~graylog-sidecar inactive; cannot reach~~       | Resolved — see `smc-file-writing-analysis/docs/log-audit-results.md` 2026-07-10 09:18–09:31 UTC entry                 |
|                           |   ~~gl.aws.apn.au:443~~ — **RESOLVED 2026-07-10.** Live |                                                                                                                       |
|                           |   pre-deploy check found                         |                                                                                                                       |
|                           |   `graylog-sidecar.service` did not exist at all |                                                                                                                       |
|                           |   (never installed) — the 2026-06-30             |                                                                                                                       |
|                           |   "connectivity issue" framing was not           |                                                                                                                       |
|                           |   reproduced/sourced in ansible-wifi. Phase 3    |                                                                                                                       |
|                           |   deployed (`smc_bases.yml` + `smc_graylog.yml`, |                                                                                                                       |
|                           |   `--limit kalumburu-smc01`); sidecar installed  |                                                                                                                       |
|                           |   fresh, active, tailing                         |                                                                                                                       |
|                           |   syslog/squid/apache/apt/interfacecheck with no |                                                                                                                       |
|                           |   errors after a 15s settle check.               |                                                                                                                       |
| ~~horn-island-smc01~~     | ~~557MB/day syslog flood from 13 Cambium APs via~~ | **RESOLVED 2026-07-15** — rsyslog drop filter deployed fleet-wide 12/12 (commit `3032c2a`). Only covers the           |
|                           |   ~~UDP 514; AP11 alone = 14.6M nl80211~~        |   `nl80211:`-tagged lines specifically, not the AP's other verbose chatter — see `08_ansible-authoring.md` "nl80211   |
|                           |   ~~kernel lines~~                               |   rsyslog Drop Filter" for the full gotcha. **Severity understated by fatrace, found 2026-07-16**: a time-aligned live |
|                           |                                                  |   capture found horn-island writes ~16,400 actual syslog lines/5min (`nl80211:`/`mgmt:`/`WPA:`/hostapd chatter, 89%+  |
|                           |                                                  |   of volume) but only ~2,670 fatrace write-syscalls in the same window — rsyslog batches ~6 lines per syscall at this |
|                           |                                                  |   extreme volume vs ~1.2-1.3 on quieter nodes, so the fatrace `write_count` metric understates the true message flood |
|                           |                                                  |   ~6x here. See `smc-file-writing-analysis/docs/log-audit-results.md` 20260716_1300 and that project's                |
|                           |                                                  |   `.archcore/rules/RULE-011` addendum. **Confirmed not an SMC-side debug flag, found 2026-07-16**: ruled out identical |
|                           |                                                  |   rsyslog config (byte-diff against a quiet node), raw AP/device count (mornington has 2x horn-island's Cambium       |
|                           |                                                  |   device count but a tiny fraction of the chatter), and any ansible-wifi/SMC-side AP config (none exists at all for   |
|                           |                                                  |   any site — Cambium APs are managed entirely through cnMaestro, outside this project's Teleport/ansible-wifi         |
|                           |                                                  |   access). Fleet-wide grep of full retained syslog history: 10/12 nodes have **zero** `mgmt:`/`WPA:` lines ever; only |
|                           |                                                  |   horn-island and mornington have any, with horn-island ~80-410x mornington's volume depending on tag. Root cause is  |
|                           |                                                  |   AP-side (hostapd/wpa_supplicant debug verbosity, or a firmware/model difference specific to those 2 sites) — needs  |
|                           |                                                  |   whoever has cnMaestro/AP-admin access to compare horn-island's and mornington's AP hardware/firmware against the    |
|                           |                                                  |   other 10 sites. Not fixable from this project. **Per-AP breakdown added 2026-07-16**: horn-island's chatter is ~73% |
|                           |                                                  |   concentrated in 2 of its 13 APs (AP11 50%, AP9 23% — refines the original 2026-06-04 "AP11 alone" finding by        |
|                           |                                                  |   identifying AP9 as a second major contributor); mornington's is more evenly spread (top AP only 34% of its total)   |
|                           |                                                  |   but shows a distinct anomaly — exactly 5 of its 13 APs each log exactly 444 `WPA:` lines, the rest exactly 0,       |
|                           |                                                  |   suggesting a shared triggering event across those 5 specifically rather than organic traffic. See                   |
|                           |                                                  |   `smc-file-writing-analysis/docs/log-audit-results.md` 20260716_1420. **ROOT CAUSE CONFIRMED 2026-07-16 (operator, via** |
|                           |                                                  |   **cnMaestro)**: horn-island's and mornington's APs had Event Logging Severity set to `Debug`; every other site's APs |
|                           |                                                  |   are set to `Warning` — exactly the hypothesis this project raised. Fix in progress — correcting both sites'         |
|                           |                                                  |   severity to `Warning`, a cnMaestro AP-config change entirely outside ansible-wifi/SMC scope. Once applied, re-sweep |
|                           |                                                  |   both nodes and reassess whether the `00-drop-nl80211.conf` rsyslog filter is still needed. See                      |
|                           |                                                  |   `smc-file-writing-analysis/docs/log-audit-results.md` 20260716_1445. **POST-FIX VERIFICATION 2026-07-16 ~15:00**:   |
|                           |                                                  |   horn-island is **fully resolved** — live syslog sample shows zero `nl80211:`/`mgmt:`/`WPA:`, fatrace top5-sum dropped |
|                           |                                                  |   3,793-4,144→1,324, now indistinguishable from a normal fleet node. Mornington is **partially resolved** — `nl80211:` |
|                           |                                                  |   still the live #1 tag, traced by source-AP grep to exactly 2 of its 13 APs still on `Debug` (AP47                   |
|                           |                                                  |   `MOR_XV2-22H_AP47_IP3_227`, AP53 `MOR_XV2-22H_AP53_IP3_233`); the other 11 (including previously-worst AP19)        |
|                           |                                                  |   confirmed clean. Actionable: apply the severity fix to AP47/AP53 specifically. See                                  |
|                           |                                                  |   `smc-file-writing-analysis/docs/log-audit-results.md` 20260716_1500.                                                |
|                           |                                                  |   **RE-CHECKED 2026-07-16 ~16:05 — AP47/AP53 CONFIRMED FIXED, but pattern shifted to 2 different APs**: a larger      |
|                           |                                                  |   3,000-line window confirms zero `nl80211:` from AP47/AP53. But `MOR_XV2-22H_AP35_IP3_215` (207 lines — previously   |
|                           |                                                  |   mornington's *lowest*-volume AP, never flagged) and `MOR_XV2-22H_AP45_IP3_225` (2 lines, trace) now show the same   |
|                           |                                                  |   debug signature. Mornington remains not fully resolved — stragglers changed, didn't disappear. See                  |
|                           |                                                  |   `smc-file-writing-analysis/docs/log-audit-results.md` 20260716_1605. **HORN-ISLAND REGRESSED 2026-07-17 — a repeat** |
|                           |                                                  |   **fleet-wide sweep found `nl80211:` back at 1,071 lines in a 2,000-line window (was zero every check since**        |
|                           |                                                  |   **2026-07-16's post-fix verification)**, horn-island jumped from 3rd-busiest to fleet-busiest node (rsyslogd        |
|                           |                                                  |   1,287→2,134). Traced 100% to a **new** AP — `HRN_XV2_AP5_IP3_50` — not AP11/AP9, which stayed clean. Same whack-a-mole |
|                           |                                                  |   pattern as mornington's AP35/AP45 emergence — this is the **3rd recurrence across the 2 sites** (horn-island AP11/AP9 → |
|                           |                                                  |   mornington AP47/AP53 → mornington AP35/AP45 → horn-island AP5). **Horn-island can no longer be called "fully**      |
|                           |                                                  |   **resolved."** Recommend whoever has cnMaestro access audit Event Logging Severity across ALL APs at both sites in one |
|                           |                                                  |   pass, rather than continuing to chase individual stragglers reactively. See                                         |
|                           |                                                  |   `smc-file-writing-analysis/docs/log-audit-results.md` 20260717_1020. **THE `00-drop-nl80211.conf` RSYSLOG FILTER WAS** |
|                           |                                                  |   **FOUND TO HAVE NEVER WORKED, REMOVED FLEET-WIDE 2026-07-17** — `if $msg contains 'nl80211' then stop` checks `$msg`, |
|                           |                                                  |   but real AP-relayed lines carry `nl80211` as the syslog TAG/`$programname`, not inside `$msg` (rsyslog splits TAG   |
|                           |                                                  |   from MSG on ingest). Verified live on horn-island with paired `logger` probes: a tag-based test message (matching   |
|                           |                                                  |   real AP format) was NOT dropped, while a message with `nl80211` inside the body WAS dropped. **This filter never**  |
|                           |                                                  |   **blocked a single real AP-relayed line since deployment** — every past write-count improvement credited to it was  |
|                           |                                                  |   actually the AP-side severity fix, not this filter. Removed rather than patched (ansible-wifi commit `9d9b0b9`,     |
|                           |                                                  |   `roles/smc_rsyslog/tasks/main.yml`, deployed live to all 12/12, dry-run + live clean, verified via `tsh ssh`) since |
|                           |                                                  |   the AP-side fix is the real and only needed solution — **no local safety net now exists for this issue class**, see |
|                           |                                                  |   `08_ansible-authoring.md` "nl80211 rsyslog Drop Filter" (needs updating to reflect removal).                        |
|                           |                                                  |   **AP5 SEVERITY FIX CONFIRMED LIVE 2026-07-17 ~13:45** — verified rather than taken on report alone: `nl80211:`      |
|                           |                                                  |   dropped from 1,071/2,000 to 2/3,000 (residual = `localhost` boilerplate, not AP-relayed), fresh tag sample shows    |
|                           |                                                  |   normal DHCP-dominant baseline. **Horn-island is fully clean again** — this was the 4th AP fixed via this process across |
|                           |                                                  |   the 2 sites (AP11, AP9, AP47, AP53, AP35/AP45 partial, AP5). The "audit all APs at both sites in one pass"          |
|                           |                                                  |   recommendation remains open. See `smc-file-writing-analysis/docs/log-audit-results.md` 20260717_1330, 20260717_1345. |
| wujal-wujal-smc01         | syslog.2 = 222MB uncompressed (Jan file)         | Cleanup needed                                                                                                        |
| mornington-smc01          | `/var/lib/dhcp/dhcpd.leases` = 223MB             | Investigate lease cleanup                                                                                             |
| bidyadanga-smc01,         | **`dhcpd.leases.<unix-epoch>` orphaned snapshot** | Low priority (single-digit MB) — needs operator approval per destructive-command guard before cleanup; bundle with    |
|   wujal-wujal-smc01       |   **files — CONFIRMED FLEET-WIDE PATTERN**       |   the deferred DHCP-split item                                                                                        |
|                           |   **2026-07-17.** isc-dhcp-server's atomic       |                                                                                                                       |
|                           |   lease-rewrite temp file, usually self-cleaning |                                                                                                                       |
|                           |   (confirmed on horn-island — the same file      |                                                                                                                       |
|                           |   pattern appeared transiently in fatrace top-5  |                                                                                                                       |
|                           |   twice,                                         |                                                                                                                       |
|                           |   `smc-file-writing-analysis/docs/log-audit-\`   |                                                                                                                       |
|                           |   `results.md` 20260716_1500 and 20260717_1020,  |                                                                                                                       |
|                           |   gone both times when checked live immediately  |                                                                                                                       |
|                           |   after), but sometimes orphaned. bidyadanga: 2  |                                                                                                                       |
|                           |   files from April 2024 (68K+235K). wujal-wujal: |                                                                                                                       |
|                           |   4 files from May 2025–March 2026 (~1.1MB       |                                                                                                                       |
|                           |   total), newly found. Likely an                 |                                                                                                                       |
|                           |   interrupted/crashed rewrite. See               |                                                                                                                       |
|                           |   `smc-file-writing-analysis/docs/log-audit-\`   |                                                                                                                       |
|                           |   `results.md` 20260717_1020 "Finding 2".        |                                                                                                                       |
| guda-guda-smc01           | ~~graylog-sidecar `active` but writing to local~~ | Resolved — see `smc-file-writing-analysis/docs/log-audit-results.md` 20260714_0830 entry                              |
|                           |   ~~disk, not tmpfs~~ **RESOLVED 2026-07-14** — turned |                                                                                                                       |
|                           |   out a standard `smc_graylog.yml` redeploy      |                                                                                                                       |
|                           |   fixed it cleanly; the "investigate why the     |                                                                                                                       |
|                           |   config never took" concern didn't materialize  |                                                                                                                       |
|                           |   into a distinct root cause, it just needed the |                                                                                                                       |
|                           |   normal rollout like every other node.          |                                                                                                                       |
| bidyadanga-smc01          | ~~Graylog connectivity broken since 2026-05-18~~ | GELF drop-rate root-caused, fix pending decision (needs Graylog admin access + WAF/ALB owner); dhcpd                  |
|                           |   **CORRECTED 2026-07-16** — that framing was stale: |   churn unaddressed                                                                                                   |
|                           |   the May-June sidecar.log errors were the       |                                                                                                                       |
|                           |   sidecar's own self-health-check, unrelated to  |                                                                                                                       |
|                           |   actual log shipping, self-resolved by the      |                                                                                                                       |
|                           |   2026-07-14 Phase 3 redeploy, not reproduced    |                                                                                                                       |
|                           |   live. Real current issue: fleet-wide GELF-HTTP |                                                                                                                       |
|                           |   silent drop rate (0.2%-56.5% per node) from a  |                                                                                                                       |
|                           |   hard 64 KiB WAF/ALB body-size limit on         |                                                                                                                       |
|                           |   `gl.aws.apn.au`, confirmed via live curl       |                                                                                                                       |
|                           |   binary search — server-side, not               |                                                                                                                       |
|                           |   bidyadanga-specific. See                       |                                                                                                                       |
|                           |   `smc-file-writing-analysis/docs/log-audit-\`   |                                                                                                                       |
|                           |   `results.md` 20260716_1230. ~~graylog-sidecar~~ |                                                                                                                       |
|                           |   ~~`active` but writing to local disk~~ **RESOLVED** |                                                                                                                       |
|                           |   **2026-07-14** — same as guda-guda, standard   |                                                                                                                       |
|                           |   `smc_graylog.yml` redeploy fixed it, no        |                                                                                                                       |
|                           |   special investigation needed. dhcpd churn      |                                                                                                                       |
|                           |   (8,171 leases, old snapshots not cleaned)      |                                                                                                                       |
|                           |   still unaddressed.                             |                                                                                                                       |
| warburton-smc01           | Same `dhcpd`+`dhclient` lease-churn pattern as   | dhcpd churn unaddressed, same class as the 3 rows above                                                               |
|                           |   mornington/bidyadanga/wujal-wujal (confirmed   |                                                                                                                       |
|                           |   live 2026-07-16, see below)                    |                                                                                                                       |
| kalumburu-smc01           | **New 2026-07-16**: the only rcp node where      | Not investigated — flagged only                                                                                       |
|                           |   `auth.log` (129/300s) edges out `syslog`       |                                                                                                                       |
|                           |   (128/300s) in top writers — every other node   |                                                                                                                       |
|                           |   has syslog clearly #1. Also the fleet's worst  |                                                                                                                       |
|                           |   GELF-HTTP drop rate (56.5%, see bidyadanga row |                                                                                                                       |
|                           |   above) — two independent oddities on the same  |                                                                                                                       |
|                           |   node, not yet investigated together            |                                                                                                                       |
|                           |   or root-caused.                                |                                                                                                                       |
| jigalong-smc01            | `cnPilot`/`Could` top syslog tag, initially      | Not fixable from ansible-wifi/SMC side — needs cnMaestro access to claim the devices                                  |
|                           |   suspected to be the same raw-AP-relay-chatter  |                                                                                                                       |
|                           |   signature as horn-island's nl80211 flood.      |                                                                                                                       |
|                           |   **ROOT-CAUSED 2026-07-16 — confirmed NOT the** |                                                                                                                       |
|                           |   **same issue**: at least 5 distinct Cambium    |                                                                                                                       |
|                           |   devices (serial-number hostnames — likely      |                                                                                                                       |
|                           |   subscriber/CPE radios, not APs) stuck in an    |                                                                                                                       |
|                           |   infinite cnMaestro registration retry loop,    |                                                                                                                       |
|                           |   each rejected with `"Device Not Claimed"`      |                                                                                                                       |
|                           |   (error 1011) every ~5 minutes, 5 log           |                                                                                                                       |
|                           |   lines/cycle (17,500-17,900 lines/device in     |                                                                                                                       |
|                           |   retained history). A provisioning gap (devices |                                                                                                                       |
|                           |   never claimed in cnMaestro), not a             |                                                                                                                       |
|                           |   logging-severity setting. See                  |                                                                                                                       |
|                           |   `smc-file-writing-analysis/docs/log-audit-\`   |                                                                                                                       |
|                           |   `results.md` 20260716_1530.                    |                                                                                                                       |
| bungardi-smc01            | Multi-incident cluster, 2026-07-21→07-27 (master | Partially resolved (hostapd/netlink/kernel reboot); Teleport reverse-tunnel registration and eth0/WAN flakiness       |
|                           |   branch), each with a distinct root cause: (1)  |   remain open — needs field/WAN follow-up. Diagnostic pattern worth reusing: a driver hang can masquerade as lock     |
|                           |   `apt-get clean` exiting rc=100 traced to a     |   contention via D-state processes — check `ps` state column before assuming a lock-file/flock issue                  |
|                           |   **hostapd driver hang** (33 processes stuck    |                                                                                                                       |
|                           |   D-state on `genl_rcv`) — not lock contention   |                                                                                                                       |
|                           |   as first suspected, and explains a prior       |                                                                                                                       |
|                           |   14-day wedge dating to Jul-10; (2) a           |                                                                                                                       |
|                           |   system-wide nl80211 netlink wedge, resolved by |                                                                                                                       |
|                           |   a kernel `5.15.0-1064-raspi` reboot, after     |                                                                                                                       |
|                           |   which hostapd was disabled; (3) Teleport TLS   |                                                                                                                       |
|                           |   handshake failures traced to                   |                                                                                                                       |
|                           |   `upgrade_teleport.sh` purging node identity    |                                                                                                                       |
|                           |   across a major-version upgrade combined with   |                                                                                                                       |
|                           |   an ALPN routing change, plus `teleport.yaml`   |                                                                                                                       |
|                           |   alphanumeric-key validation contradictions;    |                                                                                                                       |
|                           |   (4) a persistent Teleport reverse-tunnel       |                                                                                                                       |
|                           |   registration failure ~50s post-join that       |                                                                                                                       |
|                           |   survived the cert fix; (5) eth0 flaky under    |                                                                                                                       |
|                           |   load, traced to simultaneous TCP resets from   |                                                                                                                       |
|                           |   both `teleport` and `autossh` to               |                                                                                                                       |
|                           |   `teleport.communitywifi.net.au` — pointing at  |                                                                                                                       |
|                           |   a WAN-level issue rather than a local NIC      |                                                                                                                       |
|                           |   fault (`ethtool`/`dmesg` both clean),          |                                                                                                                       |
|                           |   recurring after restart #31                    |                                                                                                                       |
| amata-smc01               | Root filesystem forced read-only by an active    | Open — see `06_failure-modes.md` "Disk Path Failure Forcing Root Read-Only"                                           |
|   (nbn_accelerate)        |   SATA/ATA disk-path fault since 2026-04-25      |                                                                                                                       |
|                           |   (`ata4.00` COMRESET failures,                  |                                                                                                                       |
|                           |   `DID_BAD_TARGET`) — **still open as of the last** |                                                                                                                       |
|                           |   **check (2026-04-30)**, not yet recovered via  |                                                                                                                       |
|                           |   reboot/failover; PIN/session enforcement chain |                                                                                                                       |
|                           |   (`ECLIPSE_*` marks + `netfilter-persistent`)   |                                                                                                                       |
|                           |   needs re-establishing once the box is          |                                                                                                                       |
|                           |   writable again                                 |                                                                                                                       |
| pandanus-park-smc01 (rcp) | `interfacecheckv2.sh`'s 5-minute cron restarted  | Not fully investigated — `enp2s0` restart cause open;                                                                 |
|                           |   `enp2s0`, `vlan531`, `vlan532`, `vlan621`,     |   `local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/docs/pandanus-park-interfacecheck-chronic-restart-\` |
|                           |   `vlan631` on **every single cycle**, continuously, |   `20260730_1140.md`                                                                                                  |
|                           |   for 24h+ (as of 2026-07-30).                   |                                                                                                                       |
|                           |   `vlan531`/`vlan532` are expected to clear once |                                                                                                                       |
|                           |   the corrected dhclient hook deploys            |                                                                                                                       |
|                           |   fleet-wide; `vlan621`/`vlan631` restarting is  |                                                                                                                       |
|                           |   expected/benign (cold-standby links with no    |                                                                                                                       |
|                           |   live cable); `enp2s0` restarting is a          |                                                                                                                       |
|                           |   genuinely separate, unexplained fault not yet  |                                                                                                                       |
|                           |   investigated. Worth checking as a general      |                                                                                                                       |
|                           |   diagnostic pattern (chronic per-cycle restart  |                                                                                                                       |
|                           |   = live evidence of the Problem-2-class         |                                                                                                                       |
|                           |   topology/hook mismatch) on other sites too,    |                                                                                                                       |
|                           |   not just this one                              |                                                                                                                       |
| old-looma-smc01 (rcp)     | `smc_iptables`-rendered config removes INPUT     | Open, unfixed                                                                                                         |
|                           |   ACCEPT rules for Asterisk/MQTT/Cambium-TFTP    |   — `local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/docs/problem2-live-root-cause-20260729_2112.md`    |
|                           |   that are actually present on the live deployed |                                                                                                                       |
|                           |   ruleset — a real ACL drift, unrelated to the   |                                                                                                                       |
|                           |   topology/routing investigation it was found    |                                                                                                                       |
|                           |   during, not yet fixed                          |                                                                                                                       |
| warburton-smc01 (rcp)     | `iptables.smp.j2`'s starlink `INPUT ... -j DROP` | Open, unresolved —                                                                                                    |
|                           |   rule on `vlan621` (the only site with a live   |   `local-knowledge-ansible/ansible-wifi/issues/apn/routing-issue/docs/starlink-backup-no-lease-l2-investigation-\`    |
|                           |   SMP-backup lease at check time) shows 1.68M    |   `20260730_1400.md`                                                                                                  |
|                           |   packets/3.3GB dropped over 2 weeks. Two        |                                                                                                                       |
|                           |   5-minute live `tcpdump` captures (Warburton +  |                                                                                                                       |
|                           |   Old Looma) found zero unsolicited third-party  |                                                                                                                       |
|                           |   inbound traffic — only the box's own           |                                                                                                                       |
|                           |   self-generated ARP/ICMP/DHCP. Ruled out:       |                                                                                                                       |
|                           |   self-generated traffic, public-internet        |                                                                                                                       |
|                           |   exposure (address is RFC1918 private, not      |                                                                                                                       |
|                           |   public — see the stale-comment note above).    |                                                                                                                       |
|                           |   Not confirmed: leading hypothesis is           |                                                                                                                       |
|                           |   shared-carrier L2 segment noise; would need an |                                                                                                                       |
|                           |   hours-long capture or a live `iptables LOG`    |                                                                                                                       |
|                           |   rule (a real ruleset change, separate          |                                                                                                                       |
|                           |   authorization) to pin down                     |                                                                                                                       |
| mercedes-cove-smc01 (rct) | Captive portal returns                           | Open, not investigated — `rcp-captive-portal-cache-perms-outage-20260728_1240.md` §10                                 |
|                           |   `Attempt to read property "result" on null` —  |                                                                                                                       |
|                           |   a distinct application bug surfaced during the |                                                                                                                       |
|                           |   2026-07-28 rcp portal-outage fleet sweep,      |                                                                                                                       |
|                           |   unrelated to the cache-perms issue that        |                                                                                                                       |
|                           |   prompted the sweep                             |                                                                                                                       |
| `inventories/rcp/prod`    | Declares `[horn-island_smc_bases]` twice (lines  | Open, cosmetic — `rcp-captive-portal-cache-perms-outage-20260728_1240.md` §10                                         |
|                           |   42 and 45) — cosmetic inventory duplication,   |                                                                                                                       |
|                           |   not observed to cause incorrect behavior, but  |                                                                                                                       |
|                           |   should be cleaned up                           |                                                                                                                       |
| tjuntjuntjara-smc01       | `netifd` top syslog tag (the only CFast node     | Needs field/hardware investigation — not a config change                                                              |
|                           |   where DHCP doesn't dominate), initially        |                                                                                                                       |
|                           |   suspected to be the same AP-relay-chatter      |                                                                                                                       |
|                           |   class. **ROOT-CAUSED 2026-07-16 — confirmed NOT** |                                                                                                                       |
|                           |   **the same issue**: at least 5 distinct devices |                                                                                                                       |
|                           |   with `eth0` links rapidly cycling down/up      |                                                                                                                       |
|                           |   (18,000-36,000 lines/device in retained        |                                                                                                                       |
|                           |   history, e.g. `TJN_F300SM_1065_IP_2_65`        |                                                                                                                       |
|                           |   down→up within 1-2 seconds repeatedly). Likely |                                                                                                                       |
|                           |   a physical-layer issue                         |                                                                                                                       |
|                           |   (power/cabling/interference), not confirmed.   |                                                                                                                       |
|                           |   See                                            |                                                                                                                       |
|                           |   `smc-file-writing-analysis/docs/log-audit-\`   |                                                                                                                       |
|                           |   `results.md` 20260716_1530.                    |                                                                                                                       |

**2026-07-16 synthesis — the fleet's 5 highest fatrace nodes generalize into two distinct causes, not one shared bug** (full detail: `smc-file-writing-analysis/docs/log-audit-results.md`
20260716_1118): (1) **mornington, warburton, bidyadanga, wujal-wujal** are high because they're currently the busiest public-WiFi sites — live `/var/log/syslog` tail on all 4 shows `dhcpd`+ `dhclient`
as the #1/#2 tag by volume, i.e. ordinary client connect/disconnect churn, not a defect — this ties together the previously separate per-node dhcpd/lease notes above into one fleet-wide pattern. (2)
**horn-island** is the one node with an actual unresolved defect layered on top of that same baseline traffic — the nl80211 filter above still only blocks that one tagged string, confirmed still 89%
of its fatrace top5 sum live today. Do not conflate the two: adding a dhcpd/DHCP-churn "fix" would not touch horn-island's issue, and vice versa.

## Out of Scope (permanent)

- Bugs that only appear on live hardware (require CI/test environment)
- CNMaestro / NBN API behaviour (external systems; no test access)
- WiFi RF performance (hardware/environment)
- Multi-engineer workflow coordination (process problem, not knowledge problem)

---

## 2026-07-28 — fleet fatrace sweep findings (all 16 rcp incl. new-looma)

Source: `smc-file-writing-analysis/docs/log-audit-results.md` `20260728_1033`; per-node trend rows in `docs/fatrace-sweep-history.csv`.

### GELF-HTTP 413 — the known 64 KiB limit also costs local SSD (new dimension)

The fleet-wide GELF drop issue in the bidyadanga row above (64 KiB WAF/ALB body-size limit on `gl.aws.apn.au`, root-caused 2026-07-16) surfaces on-box as `[error] [output:http:http.0]
gl.aws.apn.au:443, HTTP status=413` + `[ warn] ... chunk will not be retried`, continuously since **2026-07-14 07:38** on **all 16 rcp nodes**. Counts: mornington 184,573 / bidyadanga 57,989 /
horn-island 37,557 / tjuntjuntjara 35,802 / wujal-wujal 22,101 / remainder 375–4,375.

**The part not previously recorded: `/var/log/fluent-bit/fluent-bit.log` is not on tmpfs**, so this retry loop is a real-SSD writer — mornington 157M, wujal-wujal 81M, tjuntjuntjara 54M, bidyadanga
49M, burringurrah 36M, horn-island 16M. It is what puts `fluent-bit` back into the fatrace top-5 on tjuntjuntjara (160) and horn-island (163).

**Two traps when reading this signal:**
1. `fluent-bit` reappearing in a fatrace top-5 is **not** automatically a rise-gate (`68a08bfc`) regression. Check the log body first — if it is 413/flush errors, the rise-gate fix is still holding
   and this is the 413 loop.
2. Do not disposition the writes as STOP (RULE-008). The writes are the symptom; the dropped log shipping is the defect, and it is blocked on Graylog-admin/WAF access. The SMC-side half that *is*
   actionable without external access: relocate `/var/log/fluent-bit/` onto the smc-groups tmpfs. Not yet done.

### Fluent Bit squid/mosquitto tail inputs failing — it is a SQUID OUTAGE, and "check permissions" is a misleading message

On tjuntjuntjara (98,607 occurrences) and horn-island (35,365), vs a uniform ~4,245 baseline on the 13 healthy nodes: `[error] [input:tail:squid] read error, check permissions: /var/log/squid/*.log`
(and the mosquitto equivalent).

**RESOLVED 2026-07-28 — and the severity was understated when first written.** squid was not merely failing to log on these nodes, it was **failing to start** (`/var/log/squid/cache.log: No such file
or directory` → `FATAL` → restart-backoff), which is a **user-facing outage** because squid sits in the mandatory tcp/80 intercept path and is the captive-portal redirector. Root cause:
`/var/log/smc-groups` is an fstab tmpfs, so its subdirs die on every reboot, and the ansible tasks creating them are guarded on `stat.islnk` so an ansible re-run does not heal a rebooted node either.
Only the two nodes that had rebooted since the 2026-07-23 relocation were broken — **the other 13 were latent, not fixed**. Fixed by a `tmpfiles.d` rule in `smc_rsyslog`; see **RULE-016** in
`smc-file-writing-analysis/.archcore/rules/` for the full pattern and the safe way to verify it. **It is not a permission problem — Fluent Bit runs as root.** The glob matches nothing:
`/var/log/smc-groups/squid/` and `/var/log/smc-groups/mosquitto/` hold **zero files** on those two nodes, where the other 13 have 2 and 1. The symlinks are correct on all 16 (`/var/log/squid ->
/var/log/smc-groups/squid`, dated 2026-07-23), so this is **empty-target, not broken-link** — apparent fallout from the 2026-07-23 squid/mosquitto→tmpfs move on those two nodes. Diagnose why the
services emit no files under the tmpfs target rather than chasing ownership/modes.

### new-looma-smc01 — was in production missing the log-consolidation stack (REMEDIATED 2026-07-28)

new-looma is live and carrying traffic as of 2026-07-28 and is the **fleet's heaviest writer** (827 top-5 top_path events/300s, ~3.7× fleet median). The 2026-07-23 onboarding delivered
`smc_bases`/`smc_graylog`/`smc_prometheus`, but the same-day log-consolidation rollout (`594653b`) skipped it while it was DOWN. Verified live:

- `/etc/rsyslog.d/` holds **only stock Ubuntu configs** (`20-ufw`, `21-cloudinit`, `50-default`, `postfix`) — no `smc_rsyslog` files, no wifi/dhcp/system split.
- **No `/var/log/smc-groups`** — squid, interfacecheck and mosquitto all on real ext4. Top paths: `/var/log/syslog` 574, `/var/log/auth.log` 110, `mosquitto.log` 105.
- journald **is** correctly volatile (`99-smc-volatile.conf`, 200M in `/run/log/journal`), but **337M of stale archived journal** still sits on `/var/log/journal` from before the drop-in landed —
  reclaimable, not ongoing writes. A volatile journald drop-in does **not** clean up pre-existing `/var/log/journal` content; check for it on any node converted after it had been running persistent.
- `/var/lib/prometheus` tmpfs is **128M, not the 256M** the rest of the fleet was rebalanced to.
- `fatrace` was **not installed** — itself a reliable tell that a node was never reached by the ansible-wifi package pass. Per `smc-file-writing-analysis/AGENTS.md` standing policy, install it rather
  than substituting another tool, so write-rate numbers stay comparable across nodes.

**Remediated 2026-07-28** — and only two of the four items listed here were real. `smc_rsyslog` was deployed and verified (`ok=37 changed=23 failed=0`), and the orphaned journal was reclaimed
fleet-wide (see below). **The other two were never gaps:** `/var/lib/prometheus` at 128M *is* the fleet standard (the 128M→256M rebalance covered `/tmp` and `fbpos` only), and tmpfs monitoring was
already published on new-looma. Both had been asserted from a status doc's pending list without a live check. Also note `journalctl --vacuum-time` **cannot** reclaim the stale journal — see the
journal section below. new-looma is now at full 16/16 parity.

**Second confirmed outage, 2026-08-01 23:40 UTC → 2026-08-03 06:40 UTC (31h) — operator-reported "back online," confirmed via live Prometheus (`mcp-grafana-apn`).**
`up{instance="new-looma-smc01:9090",job="prometheus"}` and `up{instance="new-looma-smc01:9100",job="node_exporter"}` both dropped from the scrape at the same instant and returned at the same instant —
i.e. the whole host went unreachable (network/power/backhaul), not a single service crashing, since a service-level failure would leave `node_exporter` (or the self-scrape) reporting `up=1` while only
the failed service's own metric goes stale. **Root cause not established this session** — no live `tsh ssh` access was used, only read-only Prometheus history via Grafana MCP; this is a confirmed
timeline, not a diagnosed cause. A separate, earlier 18h gap in the same 7-day window (2026-07-29 11:10 UTC → 2026-07-30 05:10 UTC) lines up exactly with the already-documented topology cross-wiring
fix and "New Looma reconstruction" in `08_ansible-authoring.md` (§ backup-vlan-trunk-fixed-and-new-looma-online-20260730_1520.md) — that gap is explained, this new one is not. Two whole-host outages
in ~5 days is a recurrence pattern worth watching, not necessarily the same root cause as the cross-wiring bug (which was fixed and verified). If picked up: check whether this outage also correlates
with the still-open `my_node_network_device_info` zero-series gap on new-looma (topology-derived textfile collector, unresolved, see the Known Operational Bugs table above) — both are
new-looma-specific and topology/network-adjacent, but no shared mechanism has been established between them.

### guda-guda dhcpd lease churn — LOCAL-KEEP, not a new fault

guda-guda's +169% sweep-over-sweep rise is one path: `/var/lib/dhcp/dhcpd.leases.<epoch>` at 186 events — isc-dhcp-server's atomic lease-rewrite temp file (same class as the orphaned-snapshot row in
the table above). Server-side DHCP lease state must survive reboot, so it stays **LOCAL-KEEP** — distinct from the client-side `dhclient` leases withdrawn to disk on 2026-07-24.

## 2026-08-18 — `delye-smc01` 5-minute reboot loop: a 2.6 GiB Laravel log vs a 3.81 GiB overlay (RESOLVED)

**Symptom:** `delye-smc01` (rct, Pi 4, 7807 MiB RAM) rebooting roughly every 5 minutes.

**Culprit:** `/var/www/html/rct-tstik/storage/logs/laravel.log` at **2,755,411,645 bytes (2.63 GiB)**, actively appended, with **no logrotate stanza anywhere on the box** — `grep -rl
"rct-tstik\|laravel" /etc/logrotate.d/` returns nothing. Laravel's default `single` channel never rotates, and the tstik poller logs every Thuraya modem transaction at INFO
(`ProcessSystemConfigStatusRequest`, `ProcessChargerStatusRequest`, `ProcessThurayaProductRequest`).

**Why it killed the box:** the overlay budget is **3.81 GiB** — 50% of the box's 7.625 GiB of RAM. (Not 3.05 GiB: `overlay.size_ratio: 40` is inert, see `07_hardware-overlay.md` §8. An earlier
revision of this entry used the 40% figure and overstated the percentages by ~22%.) copy_up charges the file's *size at first write*, so laravel.log alone accounted for **69%** of the overlay the
instant anything appended to it. Add `fluent-bit.log` (273 MiB), `rise/healthcheck.log` + `.old` (~194 MiB), rotated (~55 MiB) and stale sidecar logs (~99 MiB) and the latent total reached ~85% before
any ordinary system write. See `07_hardware-overlay.md` §8 for the cost model.

**Triage notes that generalise:**

- **`rise_watchdog.py` issues the reboot**, not `rise_healthcheck.py`. The healthcheck only scores and applies penalties — it has no reboot path at all. Do not chase healthcheck when diagnosing a
  loop. The watchdog's two paths are `reboot_critical` (disk >= `DISK_THRESH`) and `reboot_after_cleanup` (overlay cleanup freed too little).
- `last -x reboot` may show a misleading history if the box has been running under overlayroot — `wtmp` lives in the overlay and is lost on every reboot.
- The fix is not "free up disk". `df` on the real filesystem looked fine (9.2G used of 57G, 17%). The exhausted resource is RAM, via the tmpfs upper layer.

**RESOLVED 2026-08-18.** The operator first disabled overlayroot to break the loop, then deployed `roles/smc_rise_logcaps` and re-enabled the overlay. Verified on-box afterwards:

| Check                | Before                     | After                                 |
| -------------------- | -------------------------- | ------------------------------------- |
| uptime               | rebooting every ~5 min     | 1 h 18 min, single boot at 11:33      |
| overlayroot          | disabled to stop the loop  | **active**                            |
| `laravel.log`        | 2,755,411,645 B (2.63 GiB) | **753,347 B**                         |
| `fluent-bit.log`     | 285,882,632 B              | 94,463 B                              |
| overlay used         | ~98% at failure            | 561 MB of 3.81 GiB — **15%**          |
| latent log exposure  | ~85% of budget             | **4%**                                |
| `rise-logcaps.timer` | absent                     | active + enabled, run takes 1.7 s CPU |
| `rise-watchdog`      | dead, `226/NAMESPACE`      | running normally                      |

The hourly scan now reports `managed=0 capped=0 ineligible=0 rotated=1 (55 MB) stale=10 (99 MB)` — `managed=0` because everything is now below the 8 MB watch threshold, which is the expected steady
state rather than a fault. The 10 stale graylog-sidecar dailies remain by design (`prune_stale` defaults false).

One failed unit remains on the host: `isc-dhcp-server6.service` — the **pre-existing fleet-wide bug from 2026-08-11**, unrelated to this incident. A fix exists in `roles/smc_dhcpd/tasks/ubuntu.yml`
and was deployed to four other rct hosts but not to delye.

## 2026-08-18 — `rise-watchdog.service` dead with `status=226/NAMESPACE` whenever overlay is off

**Fleet-class, previously undetected.** The unit's `ReadWritePaths=` listed `/media/root-rw` and `/media/root-ro` without systemd's `-` optional prefix. systemd requires every unprefixed
`ReadWritePaths` entry to exist, and those two paths exist **only while overlayroot is mounted**:

```
rise-watchdog.service: Failed to set up mount namespacing:
  /run/systemd/unit-root/media/root-ro: No such file or directory
rise-watchdog.service: Failed at step NAMESPACE spawning /usr/bin/python3
Main PID exited, code=exited, status=226/NAMESPACE
```

So the watchdog **cannot start on any host with overlayroot disabled** — precisely the state where its cleanup and reboot logic matters most — and `/boot/firmware` has the same problem on x86 hosts.

Also latent: `ProtectSystem=full` makes `/etc` read-only, so anything the watchdog writes under `/etc` fails **silently**.

Fix written (add `-` prefixes; grant `/etc/logrotate.d` and the scan roots), **not deployed**. Nobody has yet run a fleet-wide `systemctl --failed | grep rise-watchdog` sweep to establish how long the
watchdog has been non-functional, so do not assume it has been protecting anything.

## 2026-08-18 — Ubuntu's stock rsyslog logrotate has no size limit (fleet-wide)

`/etc/logrotate.d/rsyslog` ships as `rotate 4` + `weekly` with **no `size` directive**. Rotation works (verified: `/var/lib/logrotate/status` current, `syslog.1`/`syslog.2.gz`/`syslog.3.gz` on a clean
weekly cadence) — it is simply unbounded between rotations. Measured consequences:

| Host              | Live `auth.log` | `auth.log.1` | `syslog.1` |
| ----------------- | --------------- | ------------ | ---------- |
| mimbi-smc01       | 238 MB          | 537 MB       | 159 MB     |
| kiwirrkurra-smc01 | 71 MB           | 157 MB       | 184 MB     |
| hoppys-camp-smc01 | 10 MB           | 17 MB        | 177 MB     |

This is why `smc_rise_logcaps` caps **foreign** files even though it refuses to write a competing logrotate stanza for them: another config owning a file is no guarantee that the policy is sane.
Adding a `size` directive to the platform stanza (or shipping an override) is arguably the cleaner fix for this family and has **not** been done.

**Harness warning:** any ad-hoc `logrotate --debug` test must `include /etc/logrotate.conf`, not just `/etc/logrotate.d`. Omitting it drops the platform globals (`weekly`, `su root adm`, `rotate 4`,
`create`) and produces ~20 spurious "insecure permissions" skips that look exactly like fleet-wide rotation failure. Cross-check any such conclusion against observable state before believing it.

## 2026-08-18 — legacy `ozai` logger still writing post-RISE; graylog-sidecar logs accumulate forever

Both found by discovery scan, and neither would have been caught by an enumerated path list.

- **`/var/log/ozai/hc.log`** — 35–49 MB and **still actively written** on all three rct hosts checked (hoppys-camp, ilperle, black-hill-3). Zero references anywhere in `ansible-wifi`. Same family as
  the orphaned `ozai-hc-metrics.service` (2026-08-11) and the untested `ozai_overlay.prom` / `ozai_watchdog.prom` hypothesis. **No fleet sweep for ozai leftovers has ever been run.**
- **graylog-sidecar stdout logs** — `/var/log/graylog-sidecar/apn-gelf-http-<id>_stdout-<ISO>.log`, one file per day, each self-capped at exactly 10,485,746 bytes. Because they are already under any
  sane size threshold, **neither logrotate's size trigger nor a hard cap will ever fire on them** — they simply accumulate: 10 files/100 MB on delye, 10/99 MB on mimbi, 6/59 MB on kiwirrkurra. This
  file class is why `smc_rise_logcaps` has a `stale` bucket at all.
- **`/var/cache/apt/{pkg,srcpkg}cache.bin`** — ~68 MB each, survive `apt-get clean`. Now excluded from truncation and removed outright in overlay prep, since apt regenerates them for free.

**Fleet log exposure measured 2026-08-18** — percentages **corrected** against the real 3.81 GiB budget (an earlier revision divided by 3.05 GiB and overstated every figure by ~22%):

| Host                   | Flavor | Total log bytes | % of overlay budget |
| ---------------------- | ------ | --------------- | ------------------- |
| mimbi-smc01            | wh     | 1,239 MB        | **32%**             |
| kiwirrkurra-smc01      | wh     | 751 MB          | ~19%                |
| hoppys-camp-smc01      | rct    | 603 MB          | **15%**             |
| ilperle-smc01          | rct    | 498 MB          | ~13%                |
| black-hill-3-smc01     | rct    | 474 MB          | ~12%                |
| areyonga-smc01         | wh     | 456 MB          | ~12%                |
| delye-smc01 (post-fix) | rct    | 154 MB          | **4%**              |

None were looping — but mimbi is one large write away from trouble, and is surviving on the fact that nothing has touched its rotated files rather than on headroom. `nbn_wh` was **not** assessed: its
`teleport.communitywifi.net.au` profile was expired.

## 2026-08-18 — plaintext secrets in `group_vars`, and a copied Graylog config that shared them

**No `ansible-vault` exists anywhere in `ansible-wifi`** — `grep -rl ANSIBLE_VAULT inventories/ roles/` returns nothing. Live credentials sit in plaintext `group_vars` and are committed: teleport join
tokens (4+ files, including `cw/group_vars/teleport.yml`, `nbn_accelerate` and `nbn_wh` `smc_bases.yml`, `rcp/host_vars/mowanjum-smc01.yml`), the Graylog master `password_secret`, a root password
SHA-256 with its plaintext in a trailing comment, web/gelf/api tokens, and a Teams incoming webhook (6 files). This is a Bitbucket work repository, so a "my repos are private" assumption does not
apply.

Surfaced by investigating `inventories/cw/group_vars/graylog.yml`, which had been sitting **untracked since 2026-08-11**. It turned out to be a copy of the tracked `apn/group_vars/graylog.yml` with
only **five** values adapted — teleport fqdn, teleport token, teleport release, `mongodb_uri`, `graylog_server_url`. Everything else was byte-identical, including material that must not be shared
between two clusters:

| Value                                 | Why sharing it is wrong                                                                             |
| ------------------------------------- | --------------------------------------------------------------------------------------------------- |
| `graylog_cluster_uuid` / `cluster_id` | A cluster UUID *identifies* a Graylog cluster; two asserting the same one is a misconfiguration     |
| `graylog_password_secret`             | Master secret encrypting credentials in Mongo — either cluster's database could decrypt the other's |
| `graylog_root_password_sha2`          | Same admin password on both, plaintext disclosed in an adjacent comment                             |
| `graylog_web_token` / `gelf` / `api`  | Issued **by** a Graylog server, so APN's can never authenticate against a fresh instance            |
| `graylog_teams_webhook`               | Pointed at APN's channel; cw is getting its own                                                     |

The tokens are the instructive part: they *looked* configured, so the file read as "cw Graylog is set up" while being guaranteed non-functional. Note the asymmetry — the **client** side had already
been adapted for communitywifi (`nbn_wh`'s `smc_bases_graylog` uses `gl.communitywifi.net.au` plus `PLACEHOLDER_TOKEN_SET_ONCE_GRAYLOG_PROVISIONED`), while the **server** side had not. When a cluster
is cloned, check both halves.

Committed as `213c0e4a` with all seven replaced by `PLACEHOLDER_*` values carrying a generation hint, matching the `nbn_wh` convention. The genuinely cw-specific values were kept. Note the file is
inert today: `cw-graylog01` is not provisioned and `inventories/cw/prod` has no `graylog` group. Only `apn` and `cw` have a `group_vars/graylog.yml` at all — `rct`/`wh`/`rcp`/`nbn_accelerate`/`nbn_wh`
carry only the client-side `smc_bases_graylog` block.

Rotating the already-exposed material would mean every committed copy plus git history, and is tracked as its own roadmap item rather than something to fold into unrelated work.

## 2026-09-08 — upstream keepalived VIP config bug: `lb_algo rr` silently ignores the lweb03 drain intent (`202.171.100.138`)

**Not owned by `ansible-wifi`** — this is the APN keepalived/LVS director config behind `wifi-02.activ8me.net.au`, recorded here because it affects an endpoint every `nbn_accelerate` SMC talks to. See
`03_communication-flows.md` for the endpoint's architecture (it is APN's own VIP, not a third party).

| Item               | Finding                                                                                                                                                                         |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The bug            | The `virtual_server` uses `lb_algo rr`. **Plain `rr` does not honour `real_server` weights — only `wrr` does.**                                                                 |
| The ignored intent | The config sets `weight 65535` on `lweb04` with `lweb03` left at the default `1`, which reads as an intent to **drain `lweb03`**. Under `rr` that intent is silently discarded and |
|                    |   `lweb03` still takes roughly **50% of new connections**.                                                                                                                      |
| Was this           | **No.** Both backends were verified healthy on 2026-09-08 (HTTP 200 plain, and HTTP 200 with `Host: corellia`), so the mis-set algorithm was **not** the cause of that day's incident — |
|   the cause?       |   but the drain is genuinely not working and will not work whenever it is next relied upon.                                                                                     |
| Related setting    | `persistence_timeout 86400` pins each client source IP to one real server for 24 hours, so even a corrected `wrr` would take up to a day to fully drain existing                |
|                    |   client affinities.                                                                                                                                                            |
| Fix                | Change `lb_algo rr` to `lb_algo wrr` on the director pair (`202.171.100.132`/`.133`). Outside this repo — raise with whoever owns the keepalived config.                        |

**Investigation limit:** SSH to `202.171.100.132:22` is filtered from `cw-teleport01`, so the running config could not be re-read live from an SMC-side vantage point during the session.

## 2026-09-11 — portal-FQDN regression: two separate incidents, one still live on 2 sites

`smc_bases_portal_fqdn` controls the captive-portal redirect target. When it's wrong, it points captives at the Teleport proxy hostname instead of the real portal domain — the T&C page never loads, so
no pin ever gets issued. Full live-diagnosis methodology (two mechanisms, pitfalls, fleet audit tooling): `14_pin-activation-diagnosis.md`.

**Two independent regressions, confirmed via git archaeology, not just inference:**

| Inventory                                                        | Bad from           | Fixed in git       | Duration   | Fix commit                                                                 |
| ---------------------------------------------------------------- | ------------------ | ------------------ | ---------- | -------------------------------------------------------------------------- |
| `nbn_accelerate`                                                 | 2025-06-27         | 2025-07-28         | ~1 month   | Direct, deliberate revert                                                  |
|   (`inventories/nbn_accelerate/group_vars/smc_bases.yml`)        |   (`bdce3d05`)     |   (`9f395726`)     |            |                                                                            |
| `nbn_wh` (`inventories/nbn_wh/group_vars/smc_bases.yml`)         | 2025-07-01         | 2026-09-03         | **~14 months** | **Incidental** — bundled inside an unrelated squid-blocklist-transport     |
|                                                                  |   (`ec99f5d8`)     |   (`2dee86a8`)     |            |   refactor; the commit's headline never mentions the portal fix            |

**Git being fixed does not mean a box is fixed.** `squid.conf`/Apache vhosts/cron only regenerate when the relevant role actually re-runs on that box — a box provisioned (or whose `smc_squid` last
ran) inside the bad window keeps serving the broken redirect indefinitely afterward, however long ago git was corrected. Confirmed live 2026-09-11, full fleet sweep (26 reachable `nbn_accelerate` +
`nbn_wh` sites, config-side check = `deny_info` value + `squid.conf` mtime + enabled Apache vhosts + `sslcertcopy` cron):

- **RESOLVED 2026-09-11 — all 3 originally-broken sites fixed and recovery confirmed live.** `hope-vale-smc01` (`squid.conf` dated 2025-06-27, the exact regression-introduction moment — untouched for
  14+ months) and `kowanyama-smc01` (dated 2025-07-05, mid-window) were each showing only 1–2 successful `wifi/access` activations in a 15-day window pre-fix, against 57–893 at every
  comparable/control site (`14_pin-activation-diagnosis.md` §14.7). Operator re-ran `smc_squid` (tag `squid` only — `smc_dns` was already correct, `smc_application`'s stale vhost is inert; see the
  Failure mechanism note above) against both ~11:34; **first new activation confirmed on both within 3–9 minutes** (11:37:50), and both kept accumulating normally through the rest of the day
  (`kowanyama` 1→10, `hope-vale` 2→6, tracked live). `bungardi-smc01` (`nbn_wh`, `squid.conf` dated 2025-09-18) was fixed separately ~11:58 via the backdoor-SSH path (§Backdoor SSH Access in
  `03_communication-flows.md`) once its flapping Teleport agent — caused by uplink packet loss, not a hung box — allowed access; config re-verified correct, recovery-confirmation watch was still
  pending as of the last check in this investigation.
- **Fixed but with leftover cruft (3 sites, all also fixed above):** `hope-vale-smc01`/`kowanyama-smc01`/`bungardi-smc01`, plus `galiwinku-smc01` (fixed 2026-09-08), `doomadgee-smc01` (fixed
  2025-07-28, the day of the git revert), `darlngunaya-smc01` (never actually affected, see below, but carries an unrelated orphaned vhost). All still carry a stale
  `teleport.communitywifi.net.au.conf` Apache vhost and its `sslcertcopy` cron entry — the roles have no cleanup step for either, so removal is manual.
- **Correction (2026-09-11, same day as the finding below was first written): `kaltjiti-fergon-smc01` was never affected.** An earlier pass of this entry claimed it was fixed 2026-09-08 in the same
  batch as `galiwinku`. Re-verified live: single vhost (`communitywifi.net.au.conf` only, no `teleport.*`), `squid.conf` dated 2024-08-07 (the original fleet-wide baseline, predates the 2025-06-27
  regression entirely), correct `deny_info`. The original claim traced back to output-interleaving corruption in an early parallel sweep (multiple `tsh ssh` sessions appending to one shared file
  without per-host isolation) that a later "clean" rerun failed to fully purge before being written up. **Lesson: verify a fleet-sweep finding against a single, isolated, freshly-read capture for that
  exact host before writing it into this file — a table built from a batch run is not itself suffient evidence if the run's isolation was ever in question.**
- **`bungardi-smc01` (`nbn_wh`) — confirmed actively broken (2026-09-11, tunnel recovered).** The earlier "no tunnel connection found" failures were transient — a retry within the hour succeeded.
  `deny_info` still points at `teleport.communitywifi.net.au`; `squid.conf` mtime is **2025-09-18** (mid-regression, post-`nbn_accelerate`-fix-window but well before the `nbn_wh` fix landed
  2026-09-03). Pin-activation audit: 2 marks, 2 activations in the log window — same dead signature as `hope-vale`/`kowanyama`. Independently corroborated by the operator's Eclipse-side "PIN Last
  Issued" report, which showed `bungardi` last issuing 2026-09-01 (10 days stale) against every healthy site showing same-day — see the new evidence-source note below. **Third confirmed-broken site**,
  alongside `hope-vale-smc01` and `kowanyama-smc01`.
- **`darlngunaya-smc01` (`nbn_wh`) is currently correct** but its `squid.conf` mtime (2024-10) predates both the 2025-07-01 regression and the 2026-09-03 fix — `smc_squid` simply hasn't run on it
  since before the bug existed, so it never carried either value. It does have an orphaned `teleport.*` Apache vhost from Oct 2024, unrelated to this specific regression.
- **The remaining ~21 sites** have `squid.conf` predating 2025-06-27 entirely (fleet-wide `smc_squid` run of 2024-08-07) — never affected.

**Process lesson:** the `nbn_wh` fix landing inside an unrelated commit (headline: blocklist-feed transport, not portal FQDN) is exactly the kind of change where a targeted write-back audit misses
things — `git show --stat` on every commit that touches a shared vars file, not just commits whose headline names the file, should be part of any future sweep for this class of regression.

