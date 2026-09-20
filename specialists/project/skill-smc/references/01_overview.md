# SMC Overview

## Contents

- [1. What an SMC Box Is](#1-what-an-smc-box-is)

---

## 1. What an SMC Box Is

An SMC (Site Management Controller) box is a managed Linux appliance deployed as a WiFi hotspot and network gateway. It serves WiFi clients, manages local DHCP/DNS, routes traffic, collects metrics,
and optionally provides VoIP services.

### Hardware

| Platform               | CPU             | RAM (typical)                       | Storage                                   | Notes                 |
| ---------------------- | --------------- | ----------------------------------- | ----------------------------------------- | --------------------- |
| x86 PC                 | x86_64          | 4–16 GB (rcp/nbn_accelerate flavor) | SSD (Samsung monitored via SBDM/SMART)    | Standard production   |
| Raspberry Pi 4 Model B | ARM64 (aarch64) | 8 GB (rct/wh/nbn_wh flavor)         | SD card (always — USB reserved, not root) | RCT flavor; zram swap |

**OS:** Ubuntu 20.04+ (22.04 confirmed in production)

**Time zone:** All SMC boxes use Melbourne local time regardless of flavor, location, or operational state. Interpret local timestamps and day-boundary behavior as Australia/Melbourne time: AEST
(UTC+10) or AEDT (UTC+11) depending on daylight saving. The `smc_ntpd` role sets this timezone for all SMC flavors; services that depend on day boundaries should wait for NTP sync before acting on
local time.

### Remote Access

All remote access routes through **Teleport** via a persistent `autossh` reverse SSH tunnel:
- SSH port on Teleport server: `50000 + site_eclipse_siteid`
  - Example: `malik-rct01` → siteid `11001` → Teleport port `61001`
- `ansible_host = {{inventory_hostname}}.teleport.<project>.au` — **the Teleport cluster domain is not a single value fleet-wide; it splits by project into two clusters** (operator-confirmed
  2026-07-31, terminology corrected 2026-09-08 — the split is by project, not by flavor; each project has multiple flavors nested under it):

  | Project        | Flavors (incl. central-infra)                     | Teleport domain                 |
  | -------------- | ------------------------------------------------- | ------------------------------- |
  | APN            | `rcp`, `rct`, `wh` (+ `apn` central-infra)        | `teleport.apn.au`               |
  | nbn_accelerate | `nbn_accelerate`, `nbn_wh` (+ `cw` central-infra) | `teleport.communitywifi.net.au` |

All 7 inventory flavors are covered by this split. The operator runs `tsh login` manually against whichever cluster matches the project/site being worked on before any `tsh ssh` session — do not
hardcode a single domain in tooling or scripts; use this table to pick the right one instead.
- Direct SSH to port 22 is not reachable externally
- **SSH only** — Teleport DB/Kubernetes/app access features not in use
- **Access is exclusively `tsh ssh root@<hostname>` (Teleport CLI) — there is no SSH-wrapping MCP in use and no plain-`ssh` path to an SMC.** A `ssh root@<hostname>.teleport.<domain>` form only works
  if `tsh config` has already generated a `ProxyCommand`-wired `~/.ssh/config` entry for that specific cluster and `tsh login` is active; `tsh ssh` directly is the authoritative form.
- **Canonical local-port-forward tunnel to a device behind an SMC box** (operator-supplied form, 2026-09-17): `tsh ssh --proxy <teleport> -L <local_port>:<device_ip>:<device_port>
  root@<smc-hostname>`. The explicit `--proxy` flag matters — an earlier attempt without it (just `tsh ssh -L ... root@<host>`) was flaky in an agent-harness background-task context (intermittent
  "Unable to connect to ssh proxy" and shell-quoting errors); with `--proxy` named explicitly it connected reliably first try. Verified live 2026-09-17: `tsh ssh --proxy teleport.communitywifi.net.au
  -L 10000:10.255.3.1:443 root@hope-vale-smc01` tunnelled a real device's HTTPS web UI to `localhost:10000` (HTTP 200). Device port convention (see `skill-cambium` for the device side): `443` for
  current Cambium web UIs, `80` for older ones (operator-stated: ePMP 1000 uses HTTP not HTTPS).
- **`--cluster=` is NOT a substitute for `--proxy=` on `teleport.communitywifi.net.au`, for ANY command — not just `-L` tunnels — and getting this wrong produces an error that convincingly fakes a
  real outage (incident 2026-09-18).** Two independent agent sessions in `cambium-swap` ran `tsh ls --cluster=teleport.communitywifi.net.au` / `tsh ssh --cluster=teleport.communitywifi.net.au
  root@hope-vale-smc01` and got `ERROR: connection error: desc = "transport: authentication handshake failed: EOF"` on every attempt, while `tsh status` showed a fully valid cached session (hours
  left) and plain `curl https://teleport.communitywifi.net.au/webapi/ping` returned a clean 200. Both sessions concluded this meant a fleet-wide Teleport outage, and one further concluded
  `hope-vale-smc01` itself was missing/decommissioned (it isn't — it just couldn't be reached through the wrong flag). The operator reproduced and fixed it in under a minute: `tsh ls
  --proxy=teleport.communitywifi.net.au` lists the full node roster (including `hope-vale-smc01`) and `tsh ssh --proxy=teleport.communitywifi.net.au root@hope-vale-smc01` connects cleanly. **Root
  cause:** `teleport.communitywifi.net.au` is its own independently-logged-in root Teleport target (its own separate `tsh status` profile) — it is not subordinate to `teleport.apn.au`. `--cluster=`
  asks tsh to route to a target as a subordinate via a trust relationship from your current root context; that relationship doesn't exist here, so the gRPC handshake fails with EOF — a transport-layer
  error that gives no hint it's a flag-choice problem rather than a server problem. **Rule: always pass `--proxy=teleport.communitywifi.net.au` explicitly on every `tsh` command against this Teleport
  target** (`tsh ls`, `tsh ssh`, tunnels — not just the tunnel case documented above), never `--cluster=`. For a device tunnel specifically, prefer `scripts/teleport-tunnel.sh` over a hand-written
  `tsh` invocation — it already hardcodes `--proxy` correctly and resolves the right target from ansible-wifi's inventory automatically (its internal shell variable is still named `CLUSTER`; left
  as-is, a code rename is out of scope here), so this class of mistake can't happen through it. The 2026-09-18 incident happened because both agent sessions wrote raw `tsh ls`/`tsh ssh <cmd>` calls by
  hand instead of going through it — that path still needs `--proxy=` added by hand. Before ever concluding this Teleport target is down or a node is missing/decommissioned, re-run the same command
  with `--proxy=` explicit first — if that works, it was this flag, not an outage.

### APN Cluster vs NBN Accelerate Cluster — Structural Comparison (2026-08-03)

The 7 inventory flavors split into two independently-managed Ansible clusters, not just two Teleport domains (see "Remote Access" above). Roughly 95% of this pack's operational detail
(troubleshooting, known issues, live-validated fixes) was extracted from `rcp`/`rct`/`wh` work on the **APN cluster**. This section documents the **NBN Accelerate cluster** (`cw` / `nbn_accelerate` /
`nbn_wh`) by direct comparison, so the two are not conflated. Both clusters follow the same **1 central-infra inventory + N site-fleet inventories** topology, but NBN Accelerate is materially thinner
and has real functional differences beyond the SSH endpoint — do not assume "communitywifi.net.au = apn.au with a different domain" without checking this table.

|                         | APN cluster (`teleport.apn.au`)                                    | NBN Accelerate cluster (`teleport.communitywifi.net.au`)                                              |
| ----------------------- | ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------- |
| Central-infra inventory | `inventories/apn/` — jenkins, prometheus_aws,                      | `inventories/cw/` — jenkins, prometheus_aws, teleport_aws; **no graylog/opensearch host groups**      |
|                         |   teleport_aws, **graylog_servers, opensearch_servers**            |                                                                                                       |
| Site-fleet inventories  | `rcp` (x86, ~10 sites, VoIP), `rct` (RPi, ~300+ sites — largest    | `nbn_accelerate` (x86, ~20 sites), `nbn_wh` (x86, 2 real sites + 1 generic template)                  |
|                         |   fleet in repo), `wh` (x86, ~15 sites)                            |                                                                                                       |
| Kernel-update pipeline  | Full automated Jenkins kernel-update pipeline                      | **Absent** — `cw/group_vars/jenkins.yml` has no kernel-update keys or toggle at all                   |
|                         |   (`jenkins_update_kernel` batch/quarantine config) in             |                                                                                                       |
|                         |   `apn/group_vars/jenkins.yml`; per-flavor                         |                                                                                                       |
|                         |   `smc_update_kernel` toggle                                       |                                                                                                       |
| Mobile app backend      | Not present                                                        | `smc_bases_mobile_app` / `smc_bases_wifi_community_app_backend_git` — dedicated mobile-app backend    |
|                         |                                                                    |   deploy, `nbn_accelerate` only                                                                       |
| Kiosk mode              | Not present                                                        | `smc_dss_kiosk` toggle, `nbn_accelerate/group_vars/smc_bases.yml`                                     |
| Teleport alert routing  | Centralized in `prometheus.yml` only (noc/dev MS Teams webhooks)   | Same, **plus** a separate `group_vars/teleport_monitoring.yml` (dedicated MS Teams webhook) on        |
|                         |                                                                    |   `nbn_accelerate`/`nbn_wh` — no apn-side equivalent file                                             |
| Captive portal protocol | `smc_bases_portal_protocol: http` (rcp/rct/wh)                     | `smc_bases_portal_protocol: https` — cw-side portals are HTTPS-only                                   |
| Blocked-URL redirect    | `activ8me.net.au/blocked/wifi/`                                    | `blocked.communitywifi.net.au`                                                                        |
| VoIP (Asterisk)         | `rcp` only (`inventory_dir == 'rcp'` gate)                         | Not present on any cw-cluster flavor                                                                  |
| ClamAV +                | Not applied to `rcp`                                               | Applied to `nbn_accelerate` only (`inventory_dir == 'nbn_accelerate'` gate) — genuine cw-only         |
|   Lynis hardening       |                                                                    |   security-hardening difference, not hardware-driven. **Live-confirmed 2026-08-03: installed on 26/26** |
|                         |                                                                    |   **hosts, but `clamav-freshclam` failing on 26/26 — root cause confirmed: fleet-wide `clamav 0.103.x`** |
|                         |                                                                    |   **is past its 2025-09-14 database-update end-of-life, CDN now hard-blocks it (HTTP 403)**, fix is a |
|                         |                                                                    |   version upgrade to 1.0/1.4 LTS, not a retry. See `13_known-issues.md`.                              |
| `smc_ltp` sub-group     | `rcp`-only static group (`inventories/rcp/prod`), 7 sites (all     | Not present — no cw-cluster equivalent                                                                |
|                         |   "low touch"-onboarded) — dual purpose: (1) CNMaestro-managed     |                                                                                                       |
|                         |   Cambium ePMP/cnPilot wireless backhaul provisioning, (2)         |                                                                                                       |
|                         |   switches DNS resolver from unbound+stubby to bind9+RPZ. See      |                                                                                                       |
|                         |   `08_ansible-authoring.md` "smc_ltp Sub-Group"                    |                                                                                                       |
| Hardware                | `hotspot_flavor` groups `{rct, wh, nbn_wh}` as "big box"           | (same row — the split spans both clusters)                                                            |
|   form-factor split     |   (overlay+GPS+telemetry) and `{rcp, nbn_accelerate}` as "small    |                                                                                                       |
|                         |   box" — **this split is identical across both clusters**,         |                                                                                                       |
|                         |   not cluster-specific                                             |                                                                                                       |

**Genuinely identical across both clusters:** the `all.yml`/`teleport.yml`/`prometheus.yml`/ `smc_bases.yml` variable *vocabulary* (only values differ per site), the hardware form-factor branching
(`hotspot_flavor` "small box" vs "big box" applies the same way on both sides), and the hub-and-spoke inventory topology itself (a central-infra inventory with no `topology_vars/`, feeding N
site-fleet inventories that do have `topology_vars/`).

**Selector mechanism:** nothing in the codebase branches on the literal strings `cw`/`community`/ `communitywifi` — role-level conditionals key off `hotspot_flavor` (hardware class: small-box vs
big-box) or `inventory_dir.split('/')|last` (exact flavor name, e.g. `rcp`, `nbn_accelerate`), never off cluster identity directly. `cw` and `apn` as group names are only used for the central-infra
plays (jenkins/teleport/graylog/prometheus controllers) — no device-level role branches on them. When authoring a new cw-cluster-specific conditional, follow the same `inventory_dir.split('/')|last ==
'<flavor>'` pattern already used for the ClamAV/Lynis and Asterisk gates — see `08_ansible-authoring.md` "Flavor/Cluster Conditional Branching".

**Confidence / evidence basis:** structural findings from direct read of `inventories/{apn,cw,nbn_accelerate,nbn_wh,rcp,rct,wh}/group_vars/*.yml` and `inventories/*/prod` (2026-08-03 sweep);
behavioral/conditional findings from repo-wide grep across `roles/*/tasks/ main.yml`, `roles/*/templates/*.j2`, and `smc_bases.yml` (same sweep). **Live-validated at full fleet scale, 2026-08-03**:
`tsh ssh` to all 26 reachable `nbn_accelerate` hosts plus both `nbn_wh` hosts (28 total — not a spot-check) confirmed the Teleport domain, HTTPS-only portal, mobile-app backend, ClamAV+Lynis
presence/absence split, Asterisk absence, non-`smc_ltp` DNS stack, and a full hardware inventory (chassis models, CPU/RAM/storage, kernel/OS versions) — see `13_known-issues.md` "Known Operational
Bugs (NBN Accelerate cluster — full fleet sweep, 2026-08-03)" and `07_hardware-overlay.md` "NBN Accelerate / NBN WH Hardware Inventory". New findings from this sweep: ClamAV virus definitions
chronically stale fleet-wide (26/26, CDN-blocked, 10-month failure-date spread — an ongoing degradation, not a stabilized past incident), `nbn_wh` overlayroot not yet active (operator-confirmed as a
planned-but-not-yet-executed rollout, not a bug), kernel-version drift corroborating the no-automated-kernel-pipeline finding above, and one host (`koonibba-smc01`) at 95% disk usage with the fleet's
oldest kernel. `cw` flavor itself remains unvalidated (central-infra only, no site-level hosts to check) and `aurukun-smc03` was unreachable at capture time. Every troubleshooting/known-issue entry
elsewhere in this pack besides the NBN Accelerate bugs section is still an APN-cluster (`rcp`) site unless stated otherwise.

### Agentic Teleport Execution Pattern (Operational)

When using agent frameworks for SMC troubleshooting:
- Run Teleport commands (`tsh ssh`) from coordinator/main agent by default.
- Treat sub-agents as local analyzers of captured artifacts unless their own escalation/network approvals are explicitly in place.
- Persist raw outputs first (project artifact folder), then delegate parsing/summarization.
- This prevents false "stuck" states caused by sandbox DNS/approval mismatches in worker contexts.

### MCP + Skill Workflow (SMC Analysis Sessions)

For SMC disk-wear and node-audit work, use this minimum workflow:
- `skill-smc` for SMC topology/service context and disposition logic.
- `generator-and-derived-artifact-tracing` when updating generated artifacts (workbooks/scripts/docs) to keep source-of-truth aligned.
- `skill-slurp-chat` before handoff/closeout so decisions, commands, and artifacts are persisted.

MCP persistence discipline (mandatory):
- Read first, write second:
  - `memory-keeper`: `context_get(... sort=created_desc)` to find last savepoint.
  - `mcp-project-context`: `get_project_context(... section=notes, sort=created_desc)` to find latest note.
- Save only deltas/gaps (avoid duplicate notes), then checkpoint both backends.
- Channel convention for this repo: `ansible-wifi`.

Python environment for spreadsheet + workbook tasks:
- Python 3.14.4 project venv location (governed):
  - `/Volumes/Data/_ai/_project/project-working-cache/apn/smc-file-writing-analysis/.venv`
- Symlink retained for convenience at:
  - `/Volumes/Data/_ai/_project/project_stuff/apn/smc-file-writing-analysis/.venv`
- Required packages: `openpyxl`, `numpy`, `pandas`, `xlsxwriter`.

### Network Link — Satellite (Critical)

**All SMC boxes connect over satellite links:**
- Minimum RTT: ~600ms
- Average RTT: ~800ms

Operational implications:
- SSH session startup is slow — multiple Teleport handshake RTTs over satellite
- Ansible runs take significantly longer than LAN-connected hosts
- Batch commands into single SSH round-trips wherever possible (chain with `;` or `&&`)
- autossh keepalive tuning is critical — link drops are common on satellite
- Fluent Bit / Graylog log shipping subject to 800ms RTT per batch
- Prometheus remote_write and federation scrapes must tolerate high latency
- Any continuous disk writer (pcap, journal, large logs) has compounding impact since data cannot be quickly offloaded over the link

### WAN Uplink Topology Pattern — Direct-to-NTD and Switch-Trunked Access-VLANs Can Coexist on One Box

Confirmed at `galiwinku-smc01` (`nbn_accelerate`, multi-WAN NBN business site), 2026-09-08. Do not assume every `role: internet`/`role: starlink` interface on a multi-WAN site shares the same
deployment characteristics — two structurally different patterns can and do coexist on the same box:

- **Direct-to-NTD physical ports** — a NIC wired straight to its own NBN NTD, no switch in between (`eno1`, `enp3s0` on galiwinku).
- **Switch-trunked access-VLAN ports** — a single NIC (`enp1s0`/`enp2s0` on galiwinku) is an 802.1Q trunk into a dedicated on-site switch, and that one switch carries **multiple** separate NBN
  circuits as access-VLANs, one NTD per access port. Galiwinku's `enp2s0` ("switch01") trunks VLANs 521/523/525/527; `enp1s0` ("switch02") trunks VLANs 532/534/536/538. Starlink (`vlan621`/`vlan631`,
  `role: starlink`) rides the same two trunks but is a logically separate role from the `role: internet` VLANs sharing the switch.

**Why this matters for triage:** a shared-switch VLAN failure and an independent direct-NTD failure require different troubleshooting paths. On a switch-trunked circuit, the switch itself, its uplink
port, and the trunk NIC are all shared fate across every VLAN on that switch — a switch-level problem can look like several unrelated circuits failing together. A direct-to-NTD port has no such shared
blast radius; its failure is isolated to that one circuit. Before chasing a "why did N circuits fail at once" question, check whether those circuits share a switch trunk (`enp1s0`/`enp2s0`-style) or
are independent direct-to-NTD ports — the answer changes where to look first. This is a distinct pattern from the switch01/switch02 **active-standby failover for one circuit** design discussed in
`08_ansible-authoring.md` "Design Recommendation: Bond Doubled RCP/NBN-Accelerate Internet Circuits" — that one is two switches carrying the *same* circuit; this one is one switch carrying *several
different* circuits as access-VLANs.

### Inventory Flavors

| Flavor         | Platform    | Description                                |
| -------------- | ----------- | ------------------------------------------ |
| apn            | x86         | APN network hotspots                       |
| cw             | x86         | NBN Accelerate cluster — central infra hub |
| rcp            | x86         | RCP network                                |
| rct            | ARM64 (RPi) | Raspberry Pi-based                         |
| wh             | x86         | WH network                                 |
| nbn_accelerate | x86         | NBN Accelerate broadband                   |
| nbn_wh         | x86         | NBN WH                                     |

---

