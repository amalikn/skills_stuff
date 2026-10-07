---
Title: RouterOS CLI reference for SMC-site MikroTiks
Category: reference
Status: current
Authority: local-supplement
Scope: Read-only RouterOS 7 commands used by this pack, what their fields mean, and gotchas
Last reviewed: 2026-10-07
Summary: Commands for identity, uptime, health, ports, link history, bridge/VLAN layout, logs and config export on RouterOS 7.8, with parsing notes.
---

# RouterOS CLI Reference (read-only)

All VERIFIED-OBSERVED on RouterOS 7.8 (RB450Gx4 and Metal 52 ac), 2026-10-07, unless marked.

Run any command with `without-paging` appended when the output is long.

| Command | Shows | Notes |
| --- | --- | --- |
| `/system identity print` | identity | Not unique per site (`450Gx4`, `AP1`); identify the site by its SMC |
| `/system resource print` | uptime, version, board, memory | Uptime vs SMC uptime reveals power-cycles |
| `/system routerboard print` | model, serial, firmware | RB450Gx4 r2 warns `cpu not running at default frequency` |
| `/system health print` | voltage, temperature | The DC input the board sees |
| `/interface print detail` | `link-downs=`, last down/up time | Counters reset when the device reboots |
| `/interface ethernet print stats` | FCS, alignment and other errors | Cable or port wear shows here first |
| `/interface ethernet monitor [find] once` | link status, rate, duplex, partner | delye ether4 runs 10 Mbps half duplex (phone UI), normal |
| `/interface bridge port print` | ports and VLAN sub-interfaces per bridge | One bridge per VLAN, no VLAN filtering |
| `/interface bridge vlan print` | empty here | Consistent with the bridge-per-VLAN layout |
| `/ip address print` | management address | Switch `10.255.0.5/24` on `bridge-vlan500` |
| `/log print` | in-memory log | 1,000-line buffer, lost on reboot; mostly link events |
| `/export terse` | config, one line per item | RouterOS 7 hides secrets by default; never add `show-sensitive` (`hide-sensitive` is the 6.x flag) |

Measured values: delye switch 26.7–26.9 V, amuroona 27.2 V, APs about 26 V (fleet ranges in `01_overview.md`).

## Parsing gotchas

- `name:` appears both as the identity and inside `architecture-name:`; anchor the match to the start of the line.
- Output uses `\r\n`; strip `\r` before parsing.
- `print detail` wraps long lines with indentation; parse per interface block, not per line.
- Log timestamps are the device's local clock with no year (`aug/17 12:25:57`); the clock source and timezone are not yet checked (see `05_known-issues.md`).
