# Device API & CLI Reference

## Contents

- [Scope](#scope)
- [Access — see 02, not duplicated here](#access--see-02-not-duplicated-here)
- [Enterprise Wi-Fi (XV2) — Adapter Data Points](#enterprise-wi-fi-xv2--adapter-data-points)
- [Config Backup — the SNMP Gap This Fills](#config-backup--the-snmp-gap-this-fills)
- [Write Operations — Exist, Not Documented Here](#write-operations--exist-not-documented-here)
- [Evidence and Version Scope](#evidence-and-version-scope)
- [ePMP AP / ePMP SM — Adapter Data Points](#epmp-ap--epmp-sm--adapter-data-points)
- [cnPilot R195P — Addressing Resolved via cnMaestro Cloud Export](#cnpilot-r195p--addressing-resolved-via-cnmaestro-cloud-export)
- [cnWave 60GHz — REST API, Not the SSH TUI, Is the Real Adapter Path](#cnwave-60ghz--rest-api-not-the-ssh-tui-is-the-real-adapter-path)

---

## Scope

What a Cambium device actually returns over its REST API and SSH CLI, keyed to the normalized adapter methods (`get_facts`, `get_interfaces`, `get_radios`, ...) that `scripts/cambium_xv2_adapter.py`
in this pack implements. This is deliberately **not** a full command dump — the device exposes 50+ REST endpoints and 250+ SSH CLI commands; most of that is either covered by the separate
LibreNMS/SNMP observability stack or isn't needed by any consuming project (RTLS/BLE tags, PPPoE, IPv6 tunnels). Only what maps to an adapter's normalized objects (`Device`, `Radio`, `WirelessLink`,
`ConfigIntent`) is listed. Raw reference guides, if a data point beyond this list is ever needed, are archived in `cambium-swap`'s `evidence/archived-docs/research/ewifi/`.

This file is the canonical technical record. Consuming projects (e.g. `cambium-swap`'s `docs/migration/controller-option3/`) may explain *why* they need a given data point and cite it by evidence ID,
but should link here rather than restate the table — see this pack's Standing Write-Back Contract in `SKILL.md`.

## Access — see 02, not duplicated here

Login mechanics (REST `POST /api/login` cookie/XSRF flow, `tsh` tunnel form, SSH nesting, credential vault entries) are fully documented in
[02_device-access-and-vault.md](02_device-access-and-vault.md) — read that first. This file assumes an authenticated session already exists.

## Enterprise Wi-Fi (XV2) — Adapter Data Points

| Adapter method (target)      | REST API (primary)                | SSH CLI (fallback)                            | Notes                                                                 |
| ---------------------------- | --------------------------------- | --------------------------------------------- | --------------------------------------------------------------------- |
| `get_facts`                  | `GET /api/platform-info`,         | `show version`, `show boot`                   | Model, serial, firmware/bootloader/kernel versions, uptime, MAC —     |
|                              | `GET /api/device-summary`         |                                               | confirmed live 2026-09-17. `device-summary` also returns live         |
|                              |                                   |                                               | cnMaestro connection state (`cns_status`).                            |
| `get_interfaces`             | `GET /api/interface-summary`,     | `show interface brief`,                       | Per-port link state, speed/duplex, RX/TX counters — confirmed live    |
|                              | `GET /api/ethports-config`        | `show config system interfaces`               | in `device-summary`'s `port_stats`/`port_status`. **Real bug found:** |
|                              |                                   |                                               | `port_stats.link` is unreliable (reported DOWN for a physically-up    |
|                              |                                   |                                               | `ETH1`); `port_status` is the authoritative field for link state.     |
| `get_radios` / RF state      | `GET /api/radio-summary`,         | `show wireless radios`,                       | Channel, power, Auto-RF state. Complements, does not replace,         |
|                              | `GET /api/radio-rf-summary`,      | `show wireless radios rfstatistics`,          | LibreNMS/SNMP RF telemetry — SNMP config is **unsupported** on this   |
|                              | `GET /api/radio-config`           | `show auto-rf channel-info`                   | family, so this is the only config-read path for radios. Confirmed    |
|                              |                                   |                                               | live 2026-09-17 — `radio-summary` and `radio-rf-summary` merged by    |
|                              |                                   |                                               | list position, since neither response carries a join key.             |
| `get_wlans` (SSID config)    | `GET /api/wlan-config`,           | `show config wireless`, `show wireless wlans` | WLAN/SSID definitions and per-WLAN stats. Confirmed live 2026-09-17   |
|                              | `GET /api/wlan-summary`,          |                                               | — `wlan-config` 500'd with no params on this firmware and is not      |
|                              | `GET /api/wlan-interface-summary` |                                               | used; `wlan-summary` merged with `wlan-interface-summary` by SSID     |
|                              |                                   |                                               | instead.                                                              |
| `get_clients` (associations) | `GET /api/client-summary`,        | `show wireless clients`,                      | Connected-station list — useful for capacity/health views, not just   |
|                              | `GET /api/client-failures`        | `show wireless clients statistics`            | SNMP client counts. Confirmed live 2026-09-17 — returned an empty     |
|                              |                                   |                                               | list at query time, a real state (no clients connected), not a bug.   |
| `get_config` (full backup)   | `GET /api/system-config`,         | `show config all`                             | See [Config backup](#config-backup--the-snmp-gap-this-fills) below —  |
|                              | `GET /api/network-config`,        |                                               | the Oxidized-equivalent data source for this family. Confirmed live   |
|                              | `GET /api/dhcp-config`,           |                                               | 2026-09-17 — credential fields redacted before storage (see           |
|                              | `GET /api/vlan-config`,           |                                               | [05_known-issues.md](05_known-issues.md) Security Incidents for why   |
|                              | `GET /api/firewall-config`        |                                               | this redaction matters).                                              |
| `get_events` (diagnostics)   | `GET /api/events`                 | `show events`                                 | Local event log — useful when Graylog/syslog forwarding is            |
|                              |                                   |                                               | unavailable or to correlate with a specific device session. Confirmed |
|                              |                                   |                                               | live 2026-09-17 — raw log observed at ~41KB; output capped via a      |
|                              |                                   |                                               | `limit` param.                                                        |
| Network health (routes/ARP)  | `GET /api/ip_route-summary`       | `show ip route`,                              | Lower priority — mostly redundant with LibreNMS, kept for CLI-only    |
|                              |                                   | `show arp`, `show ip neighbour`               | troubleshooting parity. Documented only, not yet queried live.        |

### SNMP (cnPilotMIB) — Read-Only Identity Data, Confirmed Live 2026-09-18

The gap noted in `cambium-swap`'s pass-08 research (no dedicated XV2/Wi-Fi 6 MIB in any public mirror) turned out not to block a real walk: the 2015-vintage `cnPilotMIB` mirror
(`artifacts/mibs/librenms/cnpilote/CAMBIUM-MIB` in `cambium-swap`, module `cnPilotMIB ::= { cambium 22 }`) still matches cleanly against live `XV2-22H` Wi-Fi 6 firmware `6.6.0.3-r9`. A live SNMPv2c
walk of `cambiumAccessPointEntry` — base OID `.1.3.6.1.4.1.17713.22.1.1.1` — against 4 hope-vale units (`HOP_XV2_AP26/27/28/29`) returned all 15 columns correctly: MAC (index `.1`, dash-separated —
convert to this project's colon-separated convention), name (`.2`), IP (`.3`), **serial number (`.4`)**, model (`.5`), CPU/memory (`.6`/`.7`), SW version (`.8`), uptime (`.9`), hardware type (`.10`,
e.g. "Two Radio Dual Band Wi-Fi 6 2x2 Wall Plate Indoor Access Point"), regulatory (`.11`), cnMaestro connection status/account ID (`.12`/`.13`), client count (`.14`), upgrade status (`.15`).

This is the only confirmed way to get `serial_msn` for a device that never appears in a cnMaestro Cloud export (REST `get_facts` needs an authenticated session on the device itself, which is fine when
reachable that way, but SNMP is lower-friction when only read-only community access is available). Evidence: `cambium-swap` evidence E130; automated by `cambium-swap`'s
`scripts/snmp_resolve_unknowns.py`.

**Do not assume this generalises** to `XV2-2T0`, `E500` or `E430` without testing one live unit of each first — `cnPilotMIB` matching `22H` firmware is not proof it matches other cnPilot E-series
firmware branches. `scripts/snmp_resolve_unknowns.py`'s `FAMILY_OID_MAP` is deliberately scoped to exactly what has been verified; extend it (and this note) only after a hands-on test, not by
inference.

### Enterprise Wi-Fi E-series (`E500`, `E430`) — Same Adapter, Confirmed Live 2026-09-17

Older cnPilot E-series hardware, but the same Falcon-family REST API and CLI as XV2 above — no separate adapter needed. Confirmed live against real units: `E500` (`TJN_E500_AP4_IP3_40`, Tjuntjuntjara,
`10.255.3.40`, internal codename `Gambit`, firmware `4.2.3.1-r9`) and `E430H` (`Mowanjum_E430_AP13_IP3_130`, Mowanjum, `10.255.3.130`, internal codename `Sage`, firmware `4.2.3.1-r17` — the `H` in the
device's own `show version` output, "Dual Band Wall Plate Integrated", resolves E31's H-vs-W lifecycle ambiguity for this specific unit). Both `POST /api/login` + `GET /api/platform-info` and `show
version` over SSH worked identically to XV2's methods above — only tested `get_facts`, the rest of the table above is expected to apply but not yet individually re-confirmed on this hardware.

## Config Backup — the SNMP Gap This Fills

`cambium-swap`'s `inventory/device-family-matrix.csv` flags this family's SNMP as "Monitoring only — config via SNMP unsupported". The project's accepted independent management toolset recommends
Oxidized for config backup, but Oxidized needs a way to pull a config for devices where SNMP can't do it — `GET /api/system-config` (+ the network/dhcp/vlan/firewall config endpoints above) or `show
config all` over SSH is that path for this family. Not yet wired into Oxidized or tested at scale — this file records the data source, not a finished integration.

## Write Operations — Exist, Not Documented Here

The API and CLI both expose write/destructive operations (`POST /api/create-wlan`/`delete-wlan`/`exec-command`/`reboot`; CLI `delete config`, `service boot backup-firmware`, `upgrade <url>`, `import
config ...`). These matter for a future "apply config" adapter path but are out of scope for this file and must never be called against a production device without explicit operator authorization and
a tested rollback plan.

## Evidence and Version Scope

Sourced from the exact firmware-version-matched CLI Reference Guide (Release 6.6.0.3 — matches the live-confirmed `6.6.0.3-r9` on this family, not the newer Release 7.2 guides) and the device's own
served REST API client bundle, both fetched 2026-09-17 and archived in `cambium-swap`'s `evidence/archived-docs/`. Live-confirmed by three authenticated sessions against three separate Hope Vale
units, all firmware `6.6.0.3-r9`: Tower 1 (`HOP_XV2_AP1_IP3_1`, first for `get_facts`/`get_interfaces`, then for the remaining five getters), Tower 5 (`HOP_XV2_AP5_IP3_5`), and Tower 6
(`HOP_XV2_AP6_IP3_6`) — the latter two run all seven getters in one pass each, confirming the adapter's output shape holds across multiple physical units, not just one (`cambium-swap`'s own evidence
register holds the full raw-session/capture/sha256 provenance chain for anyone who wants it, but the facts above stand on their own). Every row above is queried against a real device except the
route/ARP row, which is documented only. Field names for the confirmed rows come from live device responses, not just the reference guide.

A fourth Hope Vale unit, Tower 2 (`10.255.3.2`), was attempted during the same pass and found unreachable — see [05_known-issues.md](05_known-issues.md) Coverage Gaps.

## ePMP AP / ePMP SM — Adapter Data Points

`scripts/cambium_epmp_adapter.py` implements this. ePMP AP (`ePMP 3000L`) and ePMP SM (`Force 300-16`/`Force 300-25`) share one firmware/UI stack, confirmed against one Hope Vale unit of each
(`HOP_F25_AP5_IP4_5` / `10.255.4.5`, and `HOP_3000L_T1_Omni0_20` / `10.255.0.20`).

### Access

- **SSH CLI**: `ssh admin@<device_ip>` (per-family vault credential, see [02_device-access-and-vault.md](02_device-access-and-vault.md)), then `show dashboard` — returns ~170 `cambium*`-prefixed
  key/value pairs, not JSON. No `show version`; the CLI's other `show *` subcommands (`show ap`, `show sta`, `show wireless`, `show rssi [n]`, ...) are statistics/telemetry, not identity. See the
  archived `ePMP CLI User Guide pmp-0887_001v009.pdf` for the full list, but expect gaps — it's 2019/firmware-2.3-era against a 4.7.0.1-deployed fleet. The adapter does **not** use SSH — it uses the
  richer JSON API below exclusively.
- **HTTPS JSON API** (not documented anywhere in the vendor CLI/user guides — found live by reading the served web UI's own JS bundle, `cambui.<hash>.js`): a LuCI-derived web stack (`/cgi-bin/luci` —
  the literal LuCI 404 page confirms this), structurally nothing like XV2's Falcon `/api/*` REST layer:
  - **Login**: `POST /cgi-bin/luci` (plain path, no `stok` yet) with form-urlencoded `username`/`password`. Response is JSON: `{"clientIpAddr", "userRole", "stok", "certif_dir"}` on success, plus a
    `Set-Cookie: sysauth_<host>=<value>; SameSite=Strict; secure` header.
  - **Authenticated calls**: `POST /cgi-bin/luci/;stok=<stok>/admin/<method>` — **both** the `stok` in the URL path **and** the `sysauth_<host>` cookie from login are required together; either alone
    fails silently as `{"msg":"auth_failed","success":0}` with **HTTP 200**, not 401 — a real footgun, don't treat 200 as success without checking the body. A bare POST with no body 411s (`Length
    Required`) — always send `Content-Type: application/x-www-form-urlencoded` with an explicit (even empty) body.
  - **Real data comes from `get_param`** with a form field `act=<section>` — found by enumerating every literal string passed to the JS's `cambui.methods.ajax(...)` calls (46 real method names exist;
    see the adapter's docstring for the full list), then testing `act` values referenced elsewhere in the same JS (`"config_regular"`, `"status"`, `"dashboard"`). `act=status` and `act=config_regular`
    both work; `act=dashboard` returns almost nothing (`{"device_props":{},"success":"1"}`, despite the name).
  - **Concurrent-session limit, hit live**: the device caps read-write sessions (observed `{"users":{"ro":0,"rw":5}}`, i.e. 5). Untidy testing (logging in repeatedly without `logout()`) exhausted it
    mid-session — `login()` then failed with `{"msg":"max_user_number_reached",...}` until sessions aged out. **Always call `logout()`** (the adapter's `_cmd_getters` does, in a `finally` block) —
    this is a real device that other operators/cnMaestro may also need to reach.
- Neither access path was tested for write operations. Same rule as XV2: never call a write/config/reboot endpoint or CLI command against a production device without explicit operator authorization.

### Data points

| Adapter method (target)    | API (`get_param act=`)                                                                          | Notes                                                                 |
| -------------------------- | ----------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `get_facts`                | `status` → `device_props.cambiumEPMPMSN` (serial),                                              | Confirmed live on both AP and SM 2026-09-17. `cambiumCnsServConsStat` |
|                            |                                                                                                 |   matches XV2's                                                       |
|                            | `.cambiumCurrentuImageVersion` (firmware),                                                      | free-text-with-hostname cnMaestro-status pattern.                     |
|                            | `.cambiumWirelessMACAddress`, `.cambiumEffectiveDeviceName`,                                    |                                                                       |
|                            |   `.cambiumCnsServConsStat`, `.cambiumSystemUptime`                                             |                                                                       |
| `get_interfaces`           | `status` →                                                                                      | Confirmed live. One or two LAN ports depending on model; `LAN2` reads |
|                            |   `.cambiumLANStatus`/`.cambiumLANSpeedStatus`/`.cambiumLANModeStatus`/`.cambiumLANMACAddress`  |   all-zero on both units tested (unused).                             |
|                            |   (+ `LAN2` variants)                                                                           |                                                                       |
| `get_wireless_link`        | `status` → `.cambiumConnectedAPMACAddress`, `.cambiumSTAConnectedRFFrequency`,                  | **Real bug found and fixed**: `cambiumSTADLRSSI` exists (=0) on an AP |
|   (SM only)                |   `.cambiumSTADLRSSI`/`SNR`, `.cambiumSTADistanceKm`                                            |   too, so presence-checking it isn't a valid SM-vs-AP discriminator.  |
|                            |                                                                                                 |   `cambiumConnectedAPMACAddress` is: a SM reports a real MAC, an AP   |
|                            |                                                                                                 |   reports the literal string `"Not Associated"` — the adapter now     |
|                            |                                                                                                 |   checks that instead, returns `None` on an AP.                       |
| `get_clients` (AP only)    | `status` → `.cambiumAPConnectedSTATable` (array, one entry per associated SM)                   | Confirmed live: 12 real entries on the tested AP, each with hostname, |
|                            |                                                                                                 |   MAC, IP, firmware, RSSI/SNR both directions, distance, session      |
|                            |                                                                                                 |   time. `{}` (empty) on a SM, correctly returns `[]`.                 |
|                            |                                                                                                 |   **Cross-validation find**: entries' `connectedClickTHostName` match |
|                            |                                                                                                 |   `device-inventory.csv` naming exactly (e.g. `HOP_F25_AP8_IP4_8`) —  |
|                            |                                                                                                 |   this table is a live, authoritative cross-check for that file's     |
|                            |                                                                                                 |   Hope Vale ePMP rows, not yet exploited beyond noting it here.       |
| `get_config` (full backup) | `config_regular` → redacted via `REDACT_KEY_PATTERN`                                            | **Confirmed live with real secrets present** — SNMP RO/RW community   |
|                            |                                                                                                 |   strings, a RADIUS password, and a wireless encryption key were all  |
|                            |                                                                                                 |   non-empty on the tested SM. See Security Incidents in               |
|                            |                                                                                                 |   [05_known-issues.md](05_known-issues.md): checking these fields' *values* (not just names) |
|                            |                                                                                                 |   caused a second live secret-exposure incident this session.         |
|                            |                                                                                                 |   `get_raw_param('config_regular')` is the unredacted escape hatch —  |
|                            |                                                                                                 |   same warning as XV2's `get_raw()`, never call it without redacting  |
|                            |                                                                                                 |   before it leaves your hands.                                        |

`get_events`, `get_radios` (as a distinct concept from the single-uplink `get_wireless_link`), and write operations (`set_param`, `reboot`, `reset_to_def`, `disconnect_sta`, ...) are not wrapped —
`get_log` is a real, unexplored method name (see the adapter docstring's full `ajax()` method list) that likely covers events, similar shape to XV2's.

**Force 300-16 in an AP role, confirmed live 2026-09-17:** the table above was verified against Force 300-16/300-25 units in the SM (subscriber) role only. A Force 300-16 deployed as an AP (network
master) was first seen in `cambium-swap`'s Kalumburu reconciliation and confirmed live — `show dashboard` over SSH against `Tower1_Force 300_IP_0_11_master` (`10.255.0.11`) returned real data (serial
`E8XA0V6GZXHC`, firmware `4.7.0.1`, connected to `cloud.cambiumnetworks.com`) — same CLI, same data shape as the SM role. One real-world confirmation this session: **the primary `epmp-ap` vault
credential failed on this unit; only `epmp-ap-legacy` worked** — device-family-matrix.csv's "a minority of field units... still answer to the legacy default" note had never actually been hit before
this.

## cnPilot R195P — Addressing Resolved via cnMaestro Cloud Export

First attempted 2026-09-17 with live ARP alone (E110/E112 below) — inconclusive on the true address, though it correctly proved the `EXT10XX → 10.255.10.XX` derivation rule
([03_asset-register-conventions.md](03_asset-register-conventions.md)) was wrong. **Resolved same day (E113)** once the operator supplied a real cnMaestro Cloud export (`cambium-swap`'s
`inventory/asset-register/rcp/burringurrah_cnmaestro-inventory.csv`, 120 rows spanning every Burringurrah family, not just R195P):

- **Real subnet is `10.255.11.x`**, not `.10.x` — e.g. `BUR-R195P-1055` is `10.255.11.55`, `BUR-R195P-1047` is `10.255.11.47`. Both confirmed `VERIFIED-OBSERVED` by live SSH login (vault credential
  `cambium-devices/cnpilot-r-series`, user `admin`): real cnPilot R195P hardware, MT7621 MIPS SoC, Buildroot-based Linux, WAN-side MAC one higher than the LAN/`br0` MAC (e.g. `BC:A9:93:4E:63:C1` WAN
  vs `BC:A9:93:4E:63:C0` LAN on `BUR-R195P-1047`) — the WAN MAC is what appears in `bridge_500`'s ARP table.
- **Root cause of the E110/E112 duplicate-MAC anomaly, now fully diagnosed**: `device-inventory.csv`'s `EXT1055` row carries MAC `BC:A9:93:4D:5C:41`, but the cnMaestro export shows that MAC belongs to
  a different real device, `BUR-R195P-1059` (`10.255.11.59`) — a row-misalignment/off-by-one bug in the original 51-row asset-register extraction, not a fabricated field. `EXT1055`'s real MAC is
  `BC:A9:93:4D:5A:C9`.
- **Corrects E110/E112's working assumption that OUI `bc:a9:93` was XV2-exclusive at Burringurrah** — the export and the live logins both confirm R195P shares that OUI block with XV2, so `.11.x` is a
  *mixed* XV2+R195P cluster. Individual hosts there cannot be told apart by OUI alone, only by hostname/serial (this export) or a live per-host check.
- **Naming collision found**: `EXT1053`/`EXT1055`/`EXT1059` are reused identically across both the R195P family (`10.255.11.53/55/59`) and an unrelated ePMP Force 300-16 SM family
  (`10.255.21.53/55/59`, e.g. `BUR_F300-16SM_EXT1055_IP_21_55`) — the EXT number alone never disambiguates family or subnet at this site.
- **The export also reveals the original extract undercounted the fleet**: 53 real R195P devices (39 Online, 14 Offline, 1 partial), not 51.
- `device-inventory.csv` has since been fully reconciled against this export and eight further rcp-site exports (evidence E114–E117, E120) — all nine rcp sites the operator supplied are now
  represented, spanning 2,520 rows total. The `not yet corrected` state described when this section was first written no longer applies.

### Adapter — SSH Only, No REST API Confirmed

Unlike XV2, the Enterprise Wi-Fi E-series, and cnWave, this family has no confirmed REST/HTTPS API — `device-family-matrix.csv` lists "Yes (web UI)" for R195P, but that is `USER_STATED` from vendor
docs only; no agent session has ever logged into its web UI. The only confirmed-live path is a plain SSH login dropping into a real BusyBox/Buildroot shell (MT7621 MIPS SoC) — not a vendor
"show"-style CLI. `scripts/cambium_r195p_adapter.py` implements `get_facts()` (`uname -a`, `/proc/cpuinfo`, LAN/WAN MAC via `ifconfig`) and `get_interfaces()` (`ip -o addr show`, regex-parsed to
tolerate this BusyBox's non-standard output — a line with no address to report is the LINK line itself, interleaved with real `inet` lines for the same interface, which a naive field-position parser
gets wrong). Verified live 2026-09-17 against two real Burringurrah units (`BUR-R195P-1047`, `BUR-R195P-1055`) — confirmed the WAN interface name is **not** consistent across units (`wan1` on one,
`eth2.500` on the other), so `get_facts()`'s `wan_mac_address` is best-effort only; `get_interfaces()`'s full dump is the reliable source.

No `get_config()` — deliberately not implemented. This family's SNMP Get/Set community is configured fleet-wide (confirmed via the Ansible R195P provisioning template, encrypted there but real) and
this project already has two secret-exposure incidents from unscoped config dumps on other families (see [05_known-issues.md](05_known-issues.md) Security Incidents). Add it only with
REDACT_KEY_PATTERN applied and a real need, never as a blind `cat /etc/config` dump.

<details> <summary>Original inconclusive live-ARP attempt (E110/E112, superseded above)</summary>

Attempted once `teleport.apn.au` access was restored (was expired all session). All 51 `device-inventory.csv` R195P rows are Burringurrah, addressed `10.255.10.1`–`10.255.10.99` by the flawed
derivation rule. Found zero ARP entries at `10.255.10.x` on `burringurrah-smc01`'s `bridge_500` despite 96 total entries elsewhere on the same bridge; MAC-OUI cross-check found Burringurrah's XV2
fleet at `.11.x` and ePMP SM fleet at `.21.x`, but — before the cnMaestro export arrived — no way to confirm which `.11.x` hosts were XV2 vs R195P, since both families turned out to share the
`bc:a9:93` OUI block. A follow-up re-check (E112) confirmed zero R195P presence across all three of the SMC's bridges, and separately found the duplicate-MAC anomaly this section's root-cause finding
above resolves.

</details>

## cnWave 60GHz — REST API, Not the SSH TUI, Is the Real Adapter Path

First live access attempt 2026-09-17 (evidence E118) reached a real V5000 (`HOP_T1_V5K_IP4_100`, Hope Vale, `10.255.4.100`) over SSH with the `cnwave-60ghz` vault credential, but only as far as the
E2E controller's TUI banner — a full interactive ncurses-style UI, not a scriptable CLI (non-interactive and forced-pty exec both stalled on an unanswered `[6n` cursor-position query). Checked the
official documentation before going further (evidence E119): the vendor's own 60 GHz cnWave User Guide, Release 1.8 (`evidence/archived-docs/E44-cnwave-60ghz-user-guide-r1.8.pdf` in `cambium-swap`,
exact firmware match) has **zero mentions of SSH, CLI, command line, or console** across all 12,378 lines — this TUI is undocumented/internal, not the vendor-intended management interface. The onboard
E2E controller's **local web UI** is what the User Guide documents, and — same pattern as XV2 and ePMP — that web UI is an Angular SPA calling a real backend REST API, reverse-engineered from its own
JS bundle (`main.<hash>.js`) and confirmed fully live the same day.

**Auth:** `POST /local/userLogin` with JSON body `{"username": "...", "password": "..."}` returns `{"success":true,"message":"<JWT>"}`. The JWT (issuer `cambium.com`, carries a `roles` claim —
`tg_all_write` for the admin account) is sent as `Authorization: Bearer <JWT>` on every subsequent call. No cookies involved, unlike XV2's flow.

| Adapter method (target) | Endpoint                          | Notes                                                                                                                                  |
| ----------------------- | --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `get_facts`             | `POST /local/getDeviceInfo`       | Confirmed live 2026-09-17 — name, MAC, serial, model, `swVer`/`fwVersion`, uptime, IPv4, `l2bridge` tunnel count, last reboot reason.  |
| `get_e2e_info`          | `POST /local/getE2eInfo`          | Confirmed live — `{"enabled":true,"available":true}` for this onboard-E2E device.                                                      |
| `get_status`            | `POST /local/getStatusInfo`       | Confirmed live — `onboardStatus`, `e2eCtrlUrl` (the controller's own IPv6/tcp address).                                                |
| `get_capability`        | `POST /local/getSystemCapability` | Confirmed live — `mode` (`KERNEL`), `build`, `safeboot`, VLAN-config support flag.                                                     |
| `get_links` / `get_gps` | `POST /local/getLinksCount`,      | Confirmed live — both returned real (empty, for this node's link count) responses, not errors.                                         |
|                         |   `POST /local/getGpsBrief`       |                                                                                                                                        |
| `get_topology`          | `POST /api/getTopology`           | Confirmed live — full node/link topology, site names, MAC addresses, node status codes. Different base path (`/api/`, not `/local/`)   |
|                         |                                   |   but same bearer token.                                                                                                               |
| `get_ctrl_status`       | `POST /api/getCtrlStatusDump`     | Confirmed live — per-node status including the underlying open-source Terragraph release string (`RELEASE_M60_20-...`) — cnWave is     |
|                         |                                   |   built on Meta's open-source Terragraph platform.                                                                                     |

Not yet exercised: `getNetworkOverridesConfig`, `getControllerConfig`, `getTopologyMeta` (read-only, likely safe, just not called this session), `getCnAgentConfig`/`getCnAgentStatus`,
`getKeyPerformanceIndex`, `getNetworkStats`, `getRadioStats`, `minionConfigGet`. **Never call** the write-shaped endpoints found in the same bundle without explicit operator authorization:
`cambiumConfigSet`, `cambiumConfigCommit`, `rebootNode`, `userUpdate`, `userLogout` (untested only because it's a needless write-shaped call, not because it's risky).
