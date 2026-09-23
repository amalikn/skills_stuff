# Device API & CLI Reference

## Contents

- [Scope](#scope)
- [Access — see 02, not duplicated here](#access--see-02-not-duplicated-here)
- [Enterprise Wi-Fi (XV2) — Adapter Data Points](#enterprise-wi-fi-xv2--adapter-data-points)
- [Config Backup — the SNMP Gap This Fills](#config-backup--the-snmp-gap-this-fills)
- [Write Operations — Exist, Not Documented Here](#write-operations--exist-not-documented-here)
- [Evidence and Version Scope](#evidence-and-version-scope)
- [ePMP AP / ePMP SM — Adapter Data Points](#epmp-ap--epmp-sm--adapter-data-points)
- [cnWave 60 GHz — SNMP Exists, on Its Own Arm, and Is Enabled Per Device](#cnwave-60-ghz--snmp-exists-on-its-own-arm-and-is-enabled-per-device)
- [Cross-Programme SNMP Comparison — Same Family, Both Teleport Targets](#cross-programme-snmp-comparison--same-family-both-teleport-targets)
- [Per-Device SNMP Enablement Survey — the actionable list](#per-device-snmp-enablement-survey--the-actionable-list)
- [SNMP Mechanics That Have Each Cost a Wrong Reading](#snmp-mechanics-that-have-each-cost-a-wrong-reading)
- [cnPilot R195P — Addressing Resolved via cnMaestro Cloud Export](#cnpilot-r195p--addressing-resolved-via-cnmaestro-cloud-export)
- [cnWave 60GHz — REST API, Not the SSH TUI, Is the Real Adapter Path](#cnwave-60ghz--rest-api-not-the-ssh-tui-is-the-real-adapter-path)
- [Monitoring Counter and Resource Surfaces — Probed Live 2026-09-21](#monitoring-counter-and-resource-surfaces--probed-live-2026-09-21)
- [Enterprise Wi-Fi Facts From the unified-network-controller Canary — 2026-09-21](#enterprise-wi-fi-facts-from-the-unified-network-controller-canary--2026-09-21)

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
|                              |                                   |                                               | `ETH1`); `port_status` is authoritative for link state **on XV2      |
|                              |                                   |                                               | only** — E-series returns neither field, see the model-split note    |
|                              |                                   |                                               | below.                                                               |
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

**Verified OIDs per device type, machine-readable: [snmp-oid-registry.yaml](snmp-oid-registry.yaml)** (read/write access, unit, date, method). The sections below keep the provenance and gotchas.

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

#### Model split in `device-summary` — `port_status` does not exist on E-series (2026-09-20)

The schema sweep found 14 of `device-summary`'s 45 fields splitting by model. An **E500 returns neither `port_stats` nor `port_status`**, along with `bootloader_version`, `channels`, `country`,
`kernel_version`, `max_ethernet_ports`, `max_num_scan_radios`, `max_radios`, `model`, `radio_sbs_mode`, `rca_enabled` and `reboot_count`. It returns `ap_info`, which XV2 does not.

Consequence for adapter code: reading `port_status` unconditionally works on XV2 and silently returns nothing on E-series — the same class of bug as the `port_stats.link` unreliability noted above,
but caused by absence rather than by a wrong value. Check the field exists before branching on it, and consult the generated contract in [schemas/enterprise-wifi](../schemas/enterprise-wifi) rather
than assuming parity across the family.

#### `client-summary` is truncated at 60,000 bytes on busy APs (2026-09-20)

**The device cuts the response at exactly 60,000 bytes and still returns HTTP 200**, leaving JSON that ends mid-record and will not parse. Confirmed live on `wandawuy` `10.255.3.10` with roughly 60
associated clients: `size_download=60000`, `HTTP=200`, `json.JSONDecodeError: Unterminated string starting at char 59998`. Repeated identically with `?limit=20`, `?limit=10&offset=0` and `?count=10` —
**no pagination parameter is honoured**, so there is no way to page a large client list out of this endpoint.

Consequences for anything built on this endpoint:

- A busy AP yields **nothing**, not partial data. The failure is all-or-nothing and looks like a malformed device rather than a capacity limit.
- The limit is on response *bytes*, not client count, so the threshold moves with how much per-client data the firmware emits. Roughly 60 clients on the observed firmware, but do not treat that as a
  fixed number.
- HTTP 200 means a naive collector records a parse error rather than a capacity problem, and an alert on "device returning bad JSON" will point at the wrong cause.

This qualifies the claim in the section below that REST dominates SNMP for Wi-Fi client detail: **it dominates on field richness and fails on the busiest APs**, which are exactly the ones an operator
most wants client detail for.

**SNMP is the proven fallback, tested head to head 2026-09-20.** On the same AP at the same time, REST returned unparseable truncated JSON while a walk of `cambiumClientTable` returned **63 complete
client rows from 1008 varbinds** against a reported count of 64 — a walk is many small PDUs and has no equivalent cap. Note what the fallback costs: SNMP carries 16 columns and has no per-client RSSI
or association timestamp, so above roughly 60 clients the record is thinner in exactly the fields REST was preferred for.

#### `ip6_ll` is normalised to a list in this pack's adapter (2026-09-20)

The field's JSON type differs by model: an `array` on XV2 (10 of 32 record-bearing fleet observations), a `string` on E500 (6), absent where the client has no link-local address (17).
`scripts/cambium_xv2_adapter.py`'s `get_clients()` now returns it as a list on every record, including records where the device omitted the key. A list is the lossless direction — wrapping the E500
string and mapping absent to empty keeps every value, whereas normalising to a string would truncate any XV2 client holding more than one address.

**Treat the value as identifying data.** An IPv6 link-local address is EUI-64 derived, so it encodes the client MAC: the observed `fe80::6885:b9ff:feac:bb89` resolves exactly to MAC
`6A-85-B9-AC-BB-89`. Redact it on the same footing as `mac`, never as ordinary telemetry.

### SNMP (cnPilotMIB) — Live Client and Radio Telemetry, Confirmed Live 2026-09-20

The same `cnPilotMIB` tree that carries identity data (previous section) also carries per-client and per-radio telemetry, walked live on 2026-09-20 against hope-vale XV2 units on firmware
`6.6.0.3-r9`. Evidence: `unified-network-controller` report `t1-t2-local-data-availability-test-20260920_1434.md`; runner `scripts/t1_t2_local_data_probe.sh` in that project.

| OID | Object | Contents confirmed live |
| --- | --- | --- |
| `.1.3.6.1.4.1.17713.22.1.1.1.14` | `cambiumAPTotalClients` | Scalar total associated clients |
| `.1.3.6.1.4.1.17713.22.1.2.1` | `cambiumRadioEntry` | Per radio: client count `.5`, channel `.6`, width `.7`, TX power `.8`, noise floor `.16`, interference `.17`, airtime `total/tx/rx/busy` `.18` |
| `.1.3.6.1.4.1.17713.22.1.3` | `cambiumClientTable` | Per client, 16 columns: MAC `.2`, IP `.3`, name `.4`, SSID `.5`, vendor `.6`, hwmode `.7`, radio index `.8`, WLAN `.9`, VLAN `.10`, SNR `.11`, TX rate `.12`, packet and byte counters `.13`–`.16` |

**Gotcha — an empty client table walks as `noSuchObject`, not as an empty table.** On an AP with zero associated clients, `snmpwalk` of `cambiumClientTable` returns "No Such Object available on this
agent at this OID", which is indistinguishable from an unimplemented subtree unless you also read `cambiumAPTotalClients`. A collector must treat that response as "zero clients", not as a MIB mismatch
or a device fault. This cost a wrong first reading on 2026-09-20 — the table was assumed unimplemented on Wi-Fi 6 firmware until the site was swept for an AP that actually had clients.

**Client MACs are randomized.** Observed client MACs carry the locally-administered bit (`06-…`, `DE-…`, `76-…`). MAC is not a stable per-client identifier on this estate. See `skill-smc`'s content
filtering reference for the same finding on the SMC side.

There is **no per-client RSSI** in `cnPilotMIB` — only SNR (`cambiumClientEntry.11`). Downlink RSSI per client is not available over SNMP on this family.

### REST `client-summary` Is the Real Wi-Fi Client Contract, Not the MIB — Confirmed Live 2026-09-20

For per-client Wi-Fi data the device's REST API strictly dominates SNMP, on both current and older firmware. Walked and queried live on 2026-09-20 against XV2 `6.6.0.3-r9` (hope-vale) and cnPilot E500
`4.2.3.1-r9` (Tjuntjuntjara).

| Aspect | SNMP `cambiumClientTable` | REST `GET /api/client-summary` |
| --- | --- | --- |
| Fields per client | 16 | 95 on XV2, 44 on E500 |
| SNR | Yes | Yes |
| RSSI | **Not in `cnPilotMIB` at all** | Yes (`rssi`, dBm) |
| Association timestamp | **Absent** | `assoc_time`, epoch seconds — a session start, per client, with no RADIUS |
| Empty state | `noSuchObject` (ambiguous) | `[]` (unambiguous) |

**No split between firmware generations.** Every load-bearing field is present on both: `snr`, `rssi`, `assoc_time`, `tx_bytes`, `rx_bytes`, `ssid`, `band`, `mode`, `vlan`, `authorized`, `data_rate`.
XV2's extra 52 fields are Wi-Fi 6 detail. One adapter and one field contract cover E500 through XV2.

**Credential note:** the E500 authenticates with the standard `<secret:keepassxc:cambium-devices/enterprise-wifi>` entry. The `enterprise-wifi-legacy` entry returns **403** on it — do not assume the
"legacy" entry belongs to legacy hardware. `GET /api/wlan-config` returns **404** on E500 firmware where it 500s on XV2; `wlan-summary` covers both.

**Field-level schema captures** (types plus example values, end-user identifiers redacted, infrastructure MACs kept) live in `cambium-swap/captures/device-queries/`:
`wifi-xv2-hope-vale-telemetry-schema-20260920_1530.json`, `wifi-e500-tjuntjuntjara-telemetry-schema-20260920_1531.json` and `epmp-3000l-hope-vale-snmp-sta-table-schema-20260920_1434.json`. Generated
by `unified-network-controller`'s `scripts/capture_telemetry_schema.py`. R195P and cnWave are not covered yet — different auth flows, each needs its own live run. The `events` endpoint is not JSON and
is excluded.

### Enterprise Wi-Fi E-series (`E500`, `E430`) — Same Adapter, Confirmed Live 2026-09-17

Older cnPilot E-series hardware, but the same Falcon-family REST API and CLI as XV2 above — no separate adapter needed. Confirmed live against real units: `E500` (`TJN_E500_AP4_IP3_40`, Tjuntjuntjara,
`10.255.3.40`, internal codename `Gambit`, firmware `4.2.3.1-r9`) and `E430H` (`Mowanjum_E430_AP13_IP3_130`, Mowanjum, `10.255.3.130`, internal codename `Sage`, firmware `4.2.3.1-r17` — the `H` in the
device's own `show version` output, "Dual Band Wall Plate Integrated", resolves E31's H-vs-W lifecycle ambiguity for this specific unit). Both `POST /api/login` + `GET /api/platform-info` and `show
version` over SSH worked identically to XV2's methods above — only tested `get_facts`, the rest of the table above is expected to apply but not yet individually re-confirmed on this hardware.

**`get_config()` (and the rest of `_cmd_getters()`) re-verified live 2026-09-18 (cambium-swap evidence E134)** against the same Hope Vale Tower 1 AP as the original 2026-09-17 test
(`HOP_XV2_AP1_IP3_1`, `10.255.3.1`, serial `WLYB0501N05R`), via a `tsh` local port-forward through `hope-vale-smc01`. Output unchanged in shape from the original test; 17 credential-shaped `config`
fields redacted, `wlans`/`clients` telemetry fields (which are not passed through `redact()` by design — they are narrow field-mapped summaries, not the raw API response) inspected and confirmed to
carry no real secret values, only mode names/VLANs/counters/BSSIDs.

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

**SM adapter re-verified fresh-live 2026-09-18** (superseding the earlier caveat that SM coverage was an offline replay only): the Hope Vale SM's own 5-session RW cap made a second live session there
unsafe to spend, so this run targeted a different real Force 300-25 SM instead — Doomadgee `DMG_F25_AP10_IP3_101` (`10.255.3.101`). `_cmd_getters()` (facts/interfaces/wireless_link/clients, no
`get_config`, one login/logout) ran clean end to end: serial `EBAE00B6JPM9` and MAC `00:04:56:4A:F1:D5` matched `device-inventory.csv` exactly, `wireless_link` returned a real uplink to AP MAC
`58:C1:7A:79:41:3E` at 5845 MHz. Confirms the adapter's SM code path generalises beyond the single Hope Vale unit it was originally built against, not just that one device's quirks.

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

**Working mode: which field says AP, SM or PTP master (2026-09-23, unified-network-controller Kalumburu discovery test).** In `act=status` `device_props`: `cambiumDeviceMode` is the role, observed `1` on `Tower1_Force 300_IP_0_11_master` (Force 300-16 as network master) and on `Tower1_Omni 1_IP_0_10` (ePMP 3000L AP), `2` on `Force300_EXT1002_IP2_2` (Force 300 SM); so 1 = AP, 2 = SM (`VERIFIED_PRIMARY` on three live units; the field appears in no archived MIB, it is REST-only). `cambiumSubModeType` is the protocol sub-mode and IS in CAMBIUM-PMP80211-MIB (`cambiumRFStatus` arm; enum: 1 = TDD, 2 = TDD PTP, 3 = Standard WiFi, 4 = ePTP Slave, 5 = ePTP Master, 6 = WLR): observed `5` on the Force 300 master and `1` on both the 3000L AP and the SM. Role derivation for a Nautobot record is therefore `cambiumDeviceMode` for AP-versus-SM and `cambiumSubModeType` for PTP-master-versus-PMP; the register's `_master`/`_slave` name suffixes agree on the units checked. The MIB is archived under cambium-swap `artifacts/mibs/`. Kalumburu's masters and its 3000L APs reject the primary `epmp-ap` entry and accept `epmp-ap-legacy`; its Force 300 SMs likewise take `epmp-sm-legacy`, and two of three SMs tried answered the first HTTPS request with a TLS EOF that a single retry did not clear.

**Enterprise Wi-Fi config layer facts (2026-09-23 evening, unified-network-controller canaries: `TJN_E500_AP1/2/4` at tjuntjuntjara, `HOP_XV2_AP25/26/27` at hope-vale):** `get_config()` returns six endpoint dicts (system, network, vlan, dhcp, firewall, service) — 132 flattened keys on an E500 (4.2.2.1-r3), 158 on an XV2-22H (6.6.0.3-r9); redaction clean (`snmp_read_community`, `snmp_write_community` and the RADIUS/PSK keys all `<REDACTED>`). Management-plane keys sit under `system.*` (`system_name`, `system_location`, `syslog_server` list, `snmp_trap_ip`, `ntp_server` list, `management_https/http/telnet/ssh`, `snmp_server`, `management_cns_url`, `country_code`, `tz_name`, `lldp`) and `vlan.*` (`default_gw`, `interface_vlan.<vid>.ip_addr`/`management_access`). **SNMP write is refused** (`sysLocation` SET rc 2 on eight units across both programmes) — read-only SNMP, as E34 said; tjuntjuntjara's E500s have SNMP off altogether while kalumburu's answer, so SNMP enablement is per device. `device_mac` from `device-summary` is what the register holds and what the collector writes to the record's `mgmt` interface (`HOP_XV2_AP25` had no serial, version or MAC in Nautobot until this run filled them).

**Kalumburu is on the `-legacy` entries for every family (2026-09-23, stage 3 identification of 13 SNMP-silent units from kalumburu-smc01):** ePMP APs and SMs took `epmp-ap-legacy` / `epmp-sm-legacy`, an XV2-2T0 and an E500 took `enterprise-wifi-legacy`, and the R195P SSH path read fine. Two adapter facts from the same pass: the R195P SSH snapshot reports `2.6.36` as firmware (the kernel version, `raw_uname`) and no serial, so the R-series identity over SSH is name and MAC only; an ePMP unit can fail the TLS handshake outright on every attempt (`Tower7_Omni 6_IP_0_50_New`, 10.255.0.50) while answering ping and sitting in ARP. **Lockout window:** the SM locked at ~21:45 accepted a login again at 22:55; treat the ePMP lockout as about an hour.

**ePMP SM confirmed for the same write and read paths as the AP (2026-09-23 evening, unified-network-controller three-device canary, mornington `MOR_F300-16SM_EXT1003/1004/1005`):** SNMP `sysLocation` test-write and revert with `apn-snmp-rw` succeeded on 3 of 3 (default value `undefined` on every SM, where a 3000L AP holds its own name); `get_config()` returns 793 keys on a Force 300-16 SM against 818 on a 3000L AP, redaction clean on both; the SM's `lan_mac_address` is written to Nautobot like the AP's. SMs at mornington send SNMP traps (`snmpTrapEnable` 1) where the APs do not (0), and `syslogServerIPFirst` is the SMC's management address on SMs but empty on two of three APs. **Login lockout:** the fourth HTTPS login to one SM inside about twenty minutes was refused as `auth_failed` with the correct password (EXT1003, 21:45); treat `auth_failed` after recent successful logins as a lockout, not a credential change, and wait before retrying.

**`get_config()` re-verified live 2026-09-18 (cambium-swap evidence E135)**, this time via the newly combined single-login `--include-config` path (see the R195P section below for why that change was
made), against Doomadgee `DMG_F25_AP10_IP3_101` (`10.255.3.101`) — a third real unit, after Hope Vale (2026-09-17 original) and the first Doomadgee re-verification (E132). 45 credential-shaped fields
redacted (`snmpReadWriteCommunity`, `snmpReadOnlyCommunity`, `snmpTrapCommunity`, `wirelessRadiusPassword` and the rest of the RADIUS VSA table, `networkWanPPPoEPassword`, `cambiumTR069Password`/
`cambiumTR069ACSPassword`, `vmsagentPassword`, among others); `facts.serial_number` (`EBAE00B6JPM9`) and `mac_address` (`00:04:56:4A:F1:D5`) matched `device-inventory.csv` and E132's own facts
exactly. Zero unredacted credential-shaped fields found on inspection.

### SNMP (CAMBIUM-PMP80211-MIB) — Per-SM Link Telemetry, Confirmed Live 2026-09-20

ePMP uses the `pmpMibTree` arm of the Cambium enterprise OID (`cambium 21`, `.1.3.6.1.4.1.17713.21`) — not the `cnPilotMIB` arm (`cambium 22`) used by Enterprise Wi-Fi, and not the `WHISP-*` MIBs,
which are the PMP450/Canopy tree (`enterprises 161.19`). Walked live 2026-09-20 against `HOP_3000L_T1_Omni0_20` (`10.255.0.20`, ePMP 3000L, firmware `4.7.0.1`) with 10 SMs registered.

| OID | Object | Contents confirmed live |
| --- | --- | --- |
| `.1.3.6.1.4.1.17713.21.1.2.10` | `cambiumAPNumberOfConnectedSTA` | Registered SM count |
| `.1.3.6.1.4.1.17713.21.1.2.30` | `cambiumAPConnectedSTATable` | Per SM: MAC `.1`, AID `.2`, channel `.3`, UL/DL RSSI `.4`/`.5`, UL/DL SNR `.6`/`.7`, UL/DL MCS `.8`/`.9`, IP `.10`, TX capacity `.19`, TX quality `.20`, session time `.27`, DL rate `.28`, distance in metres `.29` |
| `.1.3.6.1.4.1.17713.21.1.2.3` / `.18` | `cambiumSTADLRSSI` / `cambiumSTADLSNR` | SM-side scalars — return `noSuchObject` on an AP, as expected |

**The live agent exposes more columns than the MIB mirror documents.** `CAMBIUM-PMP80211-MIB` (in `cambium-swap`'s `artifacts/mibs/librenms/`) defines 29 columns for `cambiumAPConnectedSTAEntry`; the
live walk returned columns through `.43`, with `.43` carrying the SM's firmware string. Map adapter fields against live output, not the mirror alone.

**ePMP reports session time per SM directly** (`.27`, format `0001:22:51:32`), so ePMP link sessions do not need poll-based reconstruction the way Wi-Fi client sessions do.

## cnWave 60 GHz — SNMP Exists, on Its Own Arm, and Is Enabled Per Device

Walked live 2026-09-21 from `mornington-smc01` and `bidyadanga-smc01`. This section corrects an assumption that nearly entered the record as fact.

**cnWave uses `cambium 60` — `.1.3.6.1.4.1.17713.60` — not the ePMP arm (`21`) or the Enterprise Wi-Fi arm (`22`).** A walk of 21 or 22 against a cnWave returns nothing even on a unit where SNMP is
working perfectly, which is exactly how this was first mis-called.

| OID | Contents confirmed live |
| --- | --- |
| `.1.3.6.1.2.1.1.1.0` | `sysDescr`, e.g. `Cambium cnWave V5000 Distribution Node, Version 1.4` |
| `.1.3.6.1.4.1.17713.60.1.1.1` | Per-link entry. `.2` interface name (`terra0`, `terra16`), `.3` local MAC, `.4` peer MAC, `.7` signal in dBm (observed `-61`, `-63`). `.5` and `.6` have no documented meaning in any mirror held here and are deliberately left unread |

**Enablement splits by PROGRAMME, not by model or firmware.** This only became visible after sampling both Teleport targets; an `rcp`-only sample said "mostly off" and was wrong about the fleet.

| Site | Programme | cnWave reachable | SNMP answers |
| --- | --- | --- | --- |
| galiwinku | `nbn_accelerate` | 27 | **27** |
| doomadgee | `nbn_accelerate` | 5 | **5** |
| kowanyama | `nbn_accelerate` | 4 | **4** |
| pukatja | `nbn_accelerate` | 4 | **4** |
| mornington | `rcp` | 10 | 3 |
| bidyadanga | `rcp` | 2 | 2 |
| horn-island | `rcp` | 5 | 0 |
| wujal-wujal | `rcp` | 1 | 0 |

**`nbn_accelerate`: 40 of 40 reachable units answer. `rcp`: 5 of 19.** Same three models, same firmware `1.4`, both node roles on both sides — so this is a provisioning difference between the two
programmes, not a hardware or version one. On `rcp` it is worth treating as config drift; on `nbn_accelerate` SNMP is effectively already the collection path.

Every `rcp` non-responder was pingable. **A cnWave SNMP timeout means "not enabled on this unit", never "this family has no SNMP".**

**Two limits on the above, both load-bearing.**

1. **A single site cannot settle a family-wide question.** A first pass at hope-vale timed out on every cnWave and very nearly became "cnWave has no SNMP". Those units were simply down — no ICMP and
   no TCP on 443, 80 or 22 — while a control XV2 on the same hop answered normally. Sampling `rcp` sites reversed the conclusion.
2. **The address gap was closed by ARP, and it changed the answer.** `nbn_accelerate` holds 93 of the fleet's 117 cnWave, and five of its six cnWave sites carried no `management_ip` in
   `inventory/device-inventory.csv` at all. Addresses were derived 2026-09-21 by ping-sweeping `10.255.4.0/24` from each site's SMC box and joining `ip neigh` against the inventory's MAC column — 40
   cnWave resolved, against 12 recoverable from the stale 2026-09-18 ARP captures. **Two sites still yield nothing: `aurukun` and `hope-vale` return zero ARP entries for that subnet**, so the cnWave
   network is not reachable from their SMC boxes at all. That is a routing or VLAN question, not an SNMP one. Those addresses belong in the inventory. Until they are there, the derivation must be
   repeated: ping-sweep the cnWave subnet from the site SMC box, then join `ip neigh` on the inventory MAC column. The raw sweeps from this run are local evidence only and are not committed.

## Cross-Programme SNMP Comparison — Same Family, Both Teleport Targets

A family's contract must be checked on **both** programmes before it is called stable, because firmware and configuration track the programme, not the model. Walked 2026-09-21.

| Family | `nbn_accelerate` (`teleport.communitywifi.net.au`) | `rcp` (`teleport.apn.au`) | Variation |
| --- | --- | --- | --- |
| ePMP AP | hope-vale `10.255.0.20`: 10 SMs, 430 table rows | mornington `10.255.0.10`: 29 SMs, 1247 rows. horn-island `10.255.0.10`: 14 SMs, 602 rows | **None.** Exactly 43 columns per SM on every unit, both programmes |
| Enterprise Wi-Fi | hope-vale `10.255.3.26`, firmware `6.6.0.3-r9`: 36 `cambiumRadioEntry` rows | horn-island `10.255.3.10`, firmware **`7.1.1-r5`**: 36 rows | **None.** The radio contract survives the 6.6 → 7.1 firmware jump |
| Enterprise Wi-Fi | — | mornington `10.255.3.10`: no SNMP response at all | Per-device enablement varies *within* a programme, exactly as it does for cnWave |
| cnWave 60 GHz | unsampled — see the cnWave section above | 5 of 19 answer across four sites | Not comparable yet; the nbn side holds 93 of 117 units and has no addresses on record |

**What this buys:** the ePMP and Enterprise Wi-Fi OID contracts can be treated as programme-independent and firmware-stable across the versions in the fleet. **What it does not buy:** any assumption
that a given device has SNMP switched on. Reachability and enablement are per-device facts on every family, and must be probed, never inferred from a sibling at the same site.

## Per-Device SNMP Enablement Survey — the actionable list

Full per-device results: [snmp-enablement-survey-20260921.csv](snmp-enablement-survey-20260921.csv). 27 devices probed 2026-09-21 across five sites and three families.

**13 devices are pingable but silent on SNMP v2c — all of them `rcp`.** Every reachable `nbn_accelerate` device answered. Those are the actionable rows — a live device that does not answer is either
missing an SNMP config or answering only to a community other than the one tried. The CSV records `community_tried` per row precisely so that question can be settled without re-deriving which
credential was used where:

| Programme | Community tried | Sites |
| --- | --- | --- |
| `rcp` | `cambium-devices/apn-snmp-ro` | mornington, horn-island, bidyadanga, wujal-wujal |
| `nbn_accelerate` | `cambium-devices/nbn-snmp-ro` | hope-vale |

**Distinguish the three outcomes before concluding anything**, because they are not interchangeable:

| `icmp` | `snmp_v2c` | What it means |
| --- | --- | --- |
| `UP` | `OK` | SNMP enabled and the tried community is correct |
| `UP` | `TIMEOUT` | **Actionable.** Device healthy; SNMP not enabled, or a different community. Worth retrying with the other programme's community and with any site-local one |
| `DOWN` | `TIMEOUT` | **Carries no information about SNMP.** The device is unreachable. Do not count these as evidence either way — this is exactly the trap hope-vale set |

Three of the 13 silent units at mornington were confirmed healthy beyond ping (`10.255.4.111` answers on both tcp/443 and tcp/22), so for those the SNMP silence is definitely configuration rather than
device state.

**Not yet probed:** the remaining five hope-vale cnWave, and the 86 `nbn_accelerate` cnWave at aurukun, doomadgee, galiwinku, kowanyama and pukatja that carry no `management_ip` in the inventory.

## SNMP Mechanics That Have Each Cost a Wrong Reading

Three, all confirmed on the 2026-09-21 walks:

- **A table entry OID ends in `.1`, the Entry node**, and a row reads `<entry>.<column>.<index>`. Using the table OID instead shifts column and index by one, and every row then parses as a separate
  object carrying only its first field. This produced 420 "subscriber links" for an ePMP AP with 10 registered.
- **A scalar is instance `.0` of its object.** `cambiumAPNumberOfConnectedSTA` answers at `.1.3.6.1.4.1.17713.21.1.2.10.0`; an exact-match lookup on the bare OID returns nothing at all.
- **An empty table walks as `noSuchObject`, not as an empty table** — read the scalar count alongside it. Confirmed again on 2026-09-21: `HOP_XV2_AP26` returned `noSuchObject` for `cambiumClientTable`
  **and** `0` for `cambiumAPTotalClients`, i.e. genuinely zero clients rather than an unimplemented subtree.

**Undocumented column confirmed:** `cambiumAPConnectedSTAEntry.43` carries the subscriber's firmware string (`4.7.0.1` on all ten hope-vale SMs). The MIB mirror documents 29 columns; the live agent
returns 42.

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

**Monitoring path, 2026-09-22: `get_snapshot()`.** One SSH session returns `facts`, `interfaces` and `counters` (uptime, load average, core count, memory in bytes, `/proc/net/dev` per interface). Use
it for any recurring read: the per-getter path below costs about seven logins, and this dropbear throttles rapid logins. `;` chaining works on this shell; pipes do not. Live on six units (mowanjum,
horn-island, mornington). Observed there: 16 `imq*` QoS pseudo-interfaces per unit (not traffic), management address on `eth2.500` (for example `10.255.1.2/22`), and a load average of 9.75 on 4 cores
on `MOW-R195P-1002` while `/proc/stat` showed the CPU 2.1 % busy: use the snapshot's `cpu_percent` (two `/proc/stat` samples), never the load average, as the CPU measure.

Unlike XV2, the Enterprise Wi-Fi E-series, and cnWave, this family has no confirmed REST/HTTPS API — `device-family-matrix.csv` lists "Yes (web UI)" for R195P, but that is `USER_STATED` from vendor
docs only; no agent session has ever logged into its web UI. The only confirmed-live path is a plain SSH login dropping into a real BusyBox/Buildroot shell (MT7621 MIPS SoC) — not a vendor
"show"-style CLI. `scripts/cambium_r195p_adapter.py` implements `get_facts()` (`uname -a`, `/proc/cpuinfo`, LAN/WAN MAC via `ifconfig`) and `get_interfaces()` (`ip -o addr show`, regex-parsed to
tolerate this BusyBox's non-standard output — a line with no address to report is the LINK line itself, interleaved with real `inet` lines for the same interface, which a naive field-position parser
gets wrong). Verified live 2026-09-17 against two real Burringurrah units (`BUR-R195P-1047`, `BUR-R195P-1055`) — confirmed the WAN interface name is **not** consistent across units (`wan1` on one,
`eth2.500` on the other), so `get_facts()`'s `wan_mac_address` is best-effort only; `get_interfaces()`'s full dump is the reliable source.

**`get_config()` implemented 2026-09-18** under explicit operator authorization (the "real need" this section's prior text asked for — see `CHANGELOG.md`'s `20260918_1557` entry for the full context).
Source: `cat /etc/config/* 2>&1` over the same SSH path as every other getter (no `uci` binary confirmed present on this BusyBox/Buildroot platform). The raw UCI-style text is parsed into a nested
dict (`_parse_uci_text()`) and every `option`/`list` value is redacted via `REDACT_KEY_PATTERN`/`redact()` — copied verbatim from the other three adapters — before returning, keyed by option name
regardless of whether the value looks like ciphertext (this family's fleet-wide SNMP community is an encrypted blob in its own config, per the Ansible R195P provisioning template, but redacted
unconditionally anyway, same rule as the other three families after their two prior secret-exposure incidents — see [05_known-issues.md](05_known-issues.md) Security Incidents). Opt-in only via
`--include-config`, never part of the default `_cmd_getters()` output.

**Live-verified 2026-09-18 (cambium-swap evidence E137) — mechanism confirmed end to end, but the `/etc/config/*` source assumption is WRONG for this hardware.** Ran live against both real
Burringurrah units (`BUR-R195P-1047`, `10.255.11.47`; `BUR-R195P-1055`, `10.255.11.55`) through a `tsh` local port-forward via `burringurrah-smc01`. Real finding: **this platform has no `/etc/config/`
directory at all** — `cat /etc/config/* 2>&1` returns only `cat: can't open '/etc/config/*': No such file or directory`, correctly captured under `_unparsed` and passed through `redact()` cleanly (no
secret exposure — there was nothing there to expose). A live `ls /` walk found the real config surface instead: `/etc/cambium/` (includes a 122-byte `keystore` file — name alone strongly suggests a
real secret store, untested further), `/etc/provision/provision.conf` (877 bytes) plus `ssl_ca_cert`/`ssl_client_cert`/`ssl_client_key` stub files, `/etc/snmpd/snmpd.conf` (267 bytes — almost
certainly holds the SNMP community strings), `/etc/dnsmasq.conf` (23 bytes), and a much larger `/etc_ro/` tree (`CAMBIUM_default`, `CAMBIUM_normal_deny_param`, `hw_device_config_file`,
`TRANS_PRAM.conf`, `Wireless/`, `tr069/`, etc.) that looks like a param-file scheme, not UCI. This confirms the module docstring's own standing warning — "R195P is a different, older cnPilot Home
Router product line under the hood... built by a Flyingvoice/Actiontec-style OEM platform, not Cambium's own Falcon stack" — applies to config storage too, not just the shell/SSH access path. The
`_parse_uci_text()` parser itself is correctly implemented for UCI-style text (confirmed by its own offline unit test); it has simply never been given real UCI text to parse, because this device
doesn't produce any. **Open item, not yet resolved**: identify the real config source(s) among the files above and rebuild `get_config()`'s source command and parser around them — do not assume any of
those file contents are plaintext-safe to read/redact without care; treat `/etc/cambium/keystore` and `/etc/snmpd/snmpd.conf` in particular as likely-secret-bearing until characterized.

Three real code bugs surfaced and fixed by this first live run, all still governed by this family's own `REDACT_KEY_PATTERN`/`redact()` discipline:

1. `CambiumR195PAdapter.__init__`/`_run()` only ever built a bare `user@host` SSH target — `CAMBIUM_HOST=host:port` (the exact form the other 3 HTTPS adapters in this directory already accept, and the
   form a local Teleport port-forward naturally produces, e.g. `localhost:20104`) made `ssh` try to resolve the literal string `"host:port"` as one hostname and fail. Now parses a trailing `:<port>`
   and passes `-p <port>` to `ssh` instead.
2. **New secret-exposure incident, different root cause from E107/the ePMP incident**: an uncaught `subprocess.TimeoutExpired` on the first live attempt (nested-tunnel SSH handshake legitimately took
   longer than the old 8s `DEFAULT_SSH_TIMEOUT`) printed the full `sshpass -p <password> ssh ...` argv — **the real device password** — to this session's own stderr/transcript via Python's default
   exception formatting. Caught immediately (before it reached any persisted file beyond a since-deleted `/tmp` scratch file), the temp file was deleted at once, and `_run()` now catches
   `TimeoutExpired` explicitly and re-raises a sanitized `RuntimeError` with no argv embedded — `DEFAULT_SSH_TIMEOUT` also raised 8s→20s to match the nested-tunnel round trip actually observed live.
   Operator informed same session; no rotation authorized (see `cambium-swap` SCRATCHPAD.md), but the code path that leaked it is now closed.
3. `get_config()`'s own `cat /etc/config/* 2>&1` merges BusyBox `cat`'s stderr into stdout by design (so a missing file becomes parseable `_unparsed` text instead of silently vanishing — see
   `_parse_uci_text()`'s own docstring), but `_run()`'s blanket "raise on any non-zero exit" discarded that merged stdout before `get_config()` ever saw it, defeating the whole point of the `2>&1`.
   `_run()` gained an `allow_nonzero` parameter, set `True` only by `get_config()`'s own call — every other getter keeps the original strict behaviour.
4. `cambium_epmp_adapter.py`'s `--include-config` used to call `get_config()` alone in its own login/logout pair, separate from `_cmd_getters()`'s own — two full sessions for one combined request. It
   now runs `facts`/`interfaces`/`wireless_link`/`clients`/`config` under one login, matching `cambium_r195p_adapter.py`'s existing `--include-config` shape — this family has a real 5-session RW cap
   (see the ePMP section above), so halving session cost on this path matters.

A separate, low-severity observation from the same session: this device's dropbear sshd appeared to throttle/refuse new connections for roughly a minute after several rapid SSH attempts in quick
succession (multiple `Connection refused`/`Permission denied` results against a password confirmed correct moments earlier and again moments later) — not investigated further; treat rapid repeated
connection attempts against a live R195P unit as something to avoid, not just something to retry through.

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

**`get_config()` re-verified live 2026-09-18 (cambium-swap evidence E136)** against the same Doomadgee V5000 POP node used for the E133 stat-endpoint work (`DMG_T12_V5000_DN_IP4_100`, `10.255.4.100`),
via a `tsh` local port-forward through `doomadgee-smc01`. `facts` matched exactly (serial `VYZF00D10H12`, MAC `00:04:56:88:bb:25`, firmware `10.11.0.98`); 21 credential-shaped `config` fields
redacted; zero unredacted secret-shaped fields found anywhere in the output on inspection, including the `radio_stats`/`network_stats`/`key_performance_index`/`cn_agent_status` fields E133 added.

| Adapter method (target)     | Endpoint                                | Notes                                                                                                                        |
| --------------------------- | --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `get_facts`                 | `POST /local/getDeviceInfo`             | Confirmed live 2026-09-17 — name, MAC, serial, model, `swVer`/`fwVersion`, uptime, IPv4, `l2bridge` tunnel count, last       |
|                             |                                         |   reboot reason.                                                                                                             |
| `get_e2e_info`              | `POST /local/getE2eInfo`                | Confirmed live — `{"enabled":true,"available":true}` for this onboard-E2E device.                                            |
| `get_status`                | `POST /local/getStatusInfo`             | Confirmed live — `onboardStatus`, `e2eCtrlUrl` (the controller's own IPv6/tcp address).                                      |
| `get_capability`            | `POST /local/getSystemCapability`       | Confirmed live — `mode` (`KERNEL`), `build`, `safeboot`, VLAN-config support flag.                                           |
| `get_links` / `get_gps`     | `POST /local/getLinksCount`,            | Confirmed live — both returned real (empty, for this node's link count) responses, not errors.                               |
|                             |   `POST /local/getGpsBrief`             |                                                                                                                              |
| `get_topology`              | `POST /api/getTopology`                 | Confirmed live — full node/link topology, site names, MAC addresses, node status codes. Different base path (`/api/`, not    |
|                             |                                         |   `/local/`) but same bearer token.                                                                                          |
| `get_ctrl_status`           | `POST /api/getCtrlStatusDump`           | Confirmed live — per-node status including the underlying open-source Terragraph release string (`RELEASE_M60_20-...`) —     |
|                             |                                         |   cnWave is built on Meta's open-source Terragraph platform.                                                                 |
| `get_radio_stats`           | `POST /local/getRadioStats`             | Confirmed live 2026-09-18 against a real V5000 POP node (Doomadgee `DMG_T12_V5000_DN_IP4_100`, `10.255.4.100`). Body         |
|                             |                                         |   `{"macs": [<node_mac>]}` — per-radio RF/TDD stats (sync temps, tx/rx byte+packet rates, TDD slot ratio). See the "4 stat   |
|                             |                                         |   endpoints" note below — this and the next 3 rows were previously undocumented, not previously wrapped.                     |
| `get_network_stats`         | `POST /local/getNetworkStats`           | Confirmed live 2026-09-18. Body `{"macs": [<node_mac>], "ifaces": [<names>]}` (`ifaces` non-empty, e.g. `["nic1"]`) —        |
|                             |                                         |   per-interface Ethernet counters (rx/tx packets, bytes, errors, drops).                                                     |
| `get_key_performance_index` | `POST /local/getKeyPerformanceIndex`    | Confirmed live 2026-09-18. Body `{"mac": <node_mac>}` (singular, not a list) — node-level KPI summary (totalSectors,         |
|                             |                                         |   totalLinks, uptime, tx/rx byte rate) plus a per-sector link-count map.                                                     |
| `get_cn_agent_status`       | `POST /local/getCnAgentStatus`          | Confirmed live 2026-09-18. Body `{}` — genuinely takes no params; the connection status (code/status/message/ts) of this     |
|                             |                                         |   node's CN-agent to cnMaestro.                                                                                              |

### The 4 stat endpoints were a path bug, not a missing param (resolved 2026-09-18)

`getRadioStats`/`getNetworkStats`/`getKeyPerformanceIndex`/`getCnAgentStatus` were flagged 2026-09-17 as 400ing on an empty `{}` POST to `/api/<name>`, with the params assumed undiscovered. The real
cause: these four live under `/local/`, not `/api/` like `getTopology`/`getCtrlStatusDump` — confirmed by reading the served Angular JS bundle's own `http.post(...)` call sites (same
reverse-engineering technique as every other endpoint in this file), then verified live against a real V5000 POP node (`cambium-swap` evidence, `captures/device-queries/cnwave-stat-endpoints-\
doomadgee-live-20260918_1555.json`). All 4 param shapes are in the table rows above. `cambium_cnwave_adapter.py`'s `_cmd_getters()` now calls all four using `get_facts()`'s own `mac_address` as the
node MAC — passing a `wlan_mac_addrs` radio MAC instead (from `get_topology()`) returns an empty/nulled-out result with HTTP 200, not an error, so that mismatch fails silently rather than raising;
keep using the node MAC.

Not yet exercised: `getNetworkOverridesConfig`, `getControllerConfig`, `getTopologyMeta` (read-only, likely safe, just not called this session). **Never call** the write-shaped endpoints found in the
same bundle without explicit operator authorization: `cambiumConfigSet`, `cambiumConfigCommit`, `rebootNode`, `userUpdate`, `userLogout` (untested only because it's a needless write-shaped call, not
because it's risky).

## Monitoring Counter and Resource Surfaces — Probed Live 2026-09-21

Read-only probes run from `unified-network-controller` to find which fields can feed a monitoring platform's traffic, CPU and memory metrics (OpenWISP turns only interface byte/error counters,
wireless clients and `resources` into metrics). The getters above did not read any of these. Nothing here is wired into an adapter yet; the consuming project records that state in its CHANGELOG entry
`20260921_2008`.

- **ePMP AP and SM** (`MOW_3000L_E_IP_0-20` 3000L AP, `MOW_F300-16SM_1002_IP_2_2` Force 300-16 SM, mowanjum). `get_raw_param("status")["device_props"]` carries cumulative
  `rxEtherLanKbitCount`/`txEtherLanKbitCount`, `rxEtherLanErrorPacketCount`/`txEtherLanErrorPacketCount`, `dlWLanKbitCount`/`ulWLanKbitCount`,
  `dlWLanErrorDroppedPacketCount`/`ulWLanErrorDroppedPacketCount`, and `sysCPUUsage` (percent, e.g. `12.7`). Same keys on AP and SM. Counters are in **kbit**; whether one kbit is 1000 or 1024 bits is
  `UNVERIFIED` (a rate comparison against a known transfer would settle it). No memory figure found.
- **R195P** (`MOW-R195P-1002`). The BusyBox shell serves standard `/proc`: `/proc/net/dev` (per-interface byte, packet, error and drop counters), `/proc/loadavg`, `/proc/meminfo` (`MemTotal`,
  `MemFree`, `Buffers`, `Shmem` in kB) and `/proc/cpuinfo` (4 `processor` entries on MT7621). **Read each file with a plain `cat`:** a piped command (`cat ... | head`) exited 127 on this shell, and
  `which` does not exist.
- **cnWave** (`GAL_T2_V5000N_IP4_120`, V5000 POP, galiwinku). `get_network_stats(mac, ["nic1"])` answers `success: true` but every counter, including `speed`, read **0** with `link: 1` on this node.
  The fleet schema (`schemas/cnwave-60ghz/network_stats.schema.json`) likewise recorded only `message`/`success` at all 5 observed nodes, so its `message` payload was never characterised.
  `get_key_performance_index` and `get_radio_stats` return byte and packet **rates** (`tx_byte_rate`, `rx_packet_rate`), not cumulative counters. Whether `nic1` is the wrong interface name for this
  role is open.
- **Enterprise Wi-Fi mesh state.** `mesh_type` is `none` and `mesh_clients` is empty on every enterprise Wi-Fi device across all 36 sites (`schemas/_observations/enterprise-wifi/`), so no associated
  client on this estate is a WDS peer. `unified-network-controller` relies on this to send client `wds: false`; re-check if mesh is ever enabled.

## Enterprise Wi-Fi Facts From the unified-network-controller Canary — 2026-09-21

Found while taking enterprise Wi-Fi end to end into OpenWISP (mowanjum E500 and E430, hope-vale XV2), all read live and read-only:

- **`device_mac` arrives as `BC-E6-7C-EB-72-D6`:** dashes, upper case. Normalise before comparing with a colon-separated store.
- **`platform-info.model` is the marketing name:** `cnPilot E500` and `cnPilot E430H`, not the bare model code in the asset register.
- **No REST endpoint reports a CPU core count.** `device-summary.cpu` is a utilisation percentage. SSH to the CLI (`show system`, `show version`) failed from a non-interactive `sshpass` session
  through a Teleport forward (exit 255) even with port 22 open on the XV2, so the CLI's CPU details remain unread.
- **The management address is `device_ip`, also carried by the VLAN500 interface;** every other interface reports `0.0.0.0` (see [03_asset-register-conventions.md](03_asset-register-conventions.md)
  for the 10.255.0.0/18 rule).
- **An AP that is powered off answers nothing through its forward:** the TLS handshake ends in `UNEXPECTED_EOF`, which a caller should report as unreachable, not as a protocol fault. Nine of fourteen
  mowanjum APs were in that state at 23:30 AEST on 2026-09-21. **`UNEXPECTED_EOF` alone does not prove the device is off** (2026-09-23): ePMP 3000L `Tower3_Omni 4_IP_0_30` at kalumburu, firmware
  `4.7.0.1`, answered ping from the SMC and ended every HTTPS read in `UNEXPECTED_EOF` twice, while SNMP through the same SMC read it normally: 21 SMs, MCS 17-18, TX quality 100. Same model and
  firmware as three neighbours that read fine, so its HTTPS service had failed with the radio up. Tell the two apart with a second protocol before reporting: no ping and no SNMP is unreachable; ping
  and SNMP with a dead HTTPS is a management-plane fault on a live radio. The unified-network-controller collector reports this case as `pingable`.
- **The XV2 interface list varies, so metric counts vary** (hope-vale, 2026-09-22, firmware `6.6.0.3-r9`). `interface-summary` lists `PORT-CHANNEL1`, `VLAN500`, `ETH1`, `ETH2`, plus `ETH3` on the
  XV2-22H only (the XV2-2T0 has two Ethernet ports), plus `VLAN501` on four of five units. `HOP_XV2_AP26_IP3_26` listed no `VLAN501`, although its `HopeVale_WiFi` WLAN is on VLAN 501 like the others.
  It is not the client count at read time: AP27 and AP35 had no clients and still listed it. The cause is **unverified**; a restart about 7 hours earlier on AP26 is one lead. Callers must iterate the
  interfaces a device reports, never assume a fixed set.
