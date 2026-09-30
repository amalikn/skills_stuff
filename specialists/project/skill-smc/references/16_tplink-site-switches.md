# TP-Link Site Switches — Access, Quirks and Config Capture

The on-site TP-Link switches that sit on a site's management network behind the SMC box. They carry the SMC's VLAN trunks (management, client Wi-Fi, R195P provisioning and the `internetNN` WAN VLANs),
so they are the "switching layer" that `01_overview.md` refers to. First reached 2026-09-24 at kalumburu. Tooling: `scripts/tplink-switch.sh` and `scripts/tplink_cli_driver.py` (see
`scripts/README.md`).

## Contents

- [Where they are](#where-they-are)
- [Credentials](#credentials)
- [Access path and SSH quirks](#access-path-and-ssh-quirks)
- [Privilege: enable with and without a password](#privilege-enable-with-and-without-a-password)
- [Discovery: why ARP is not enough](#discovery-why-arp-is-not-enough)
- [Config capture](#config-capture)
- [SNMP](#snmp)
- [In Nautobot](#in-nautobot)
- [VLANs: parsing and drift against topology_vars](#vlans-parsing-and-drift-against-topology_vars)
- [Kalumburu as found (2026-09-24)](#kalumburu-as-found-2026-09-24)
- [Bidyadanga as found (2026-09-30)](#bidyadanga-as-found-2026-09-30)
- [Pitfalls](#pitfalls)

## Where they are

Candidates from unified-network-controller's discovery sweeps (`docs/reports/inventory/*-discovery-sweep-*.md`), by TP-Link OUI only; a TP-Link OUI is not proof of a switch until `--discover` shows
the `TPSSH` banner or a login confirms it:

| Site         | TP-Link addresses in the sweep           | Confirmed 2026-09-30 (`--discover` TPSSH, then a login)                  |
| ------------ | ---------------------------------------- | ------------------------------------------------------------------------ |
| kalumburu    | 10.255.0.2, 10.255.0.3                   | Both (first reached 2026-09-24)                                          |
| bidyadanga   | 10.255.0.2-4                             | 10.255.0.2 only; .3 and .4 are TP-Link OUIs but not switches             |
| burringurrah | 10.255.0.2-3                             | 10.255.0.3 only (named Switch2)                                          |
| hope-vale    | 10.255.0.2-4                             | All three                                                                |
| kowanyama    | 10.255.0.2-3                             | Both                                                                     |
| pukatja      | 10.255.0.2-3                             | Both                                                                     |
| aurukun      | 10.255.1.1-2, 10.255.2.1-2, 10.255.3.1-2 | None answered as TPSSH on the management subnet                          |
| doomadgee    | 10.255.0.2-3                             | None answered as TPSSH                                                   |
| galiwinku    | 10.255.0.2-4                             | None answered as TPSSH                                                   |

All 11 are SG2428P hardware 5.30; ten run firmware 5.30.1 Build 20240202, bidyadanga 5.30.5 Build 20250117. Every one enables with no password.

The pattern at most sites is `10.255.0.2` upward, directly after the SMC's own `bridge_500` address `10.255.0.1`. Galiwinku's WAN trunks name their switches `switch01`/`switch02` in topology_vars
(`01_overview.md` "WAN Uplink Topology Pattern").

## Credentials

KeePass entry `/Network/tplink switch`, user `admin`; its Notes list `10.255.0.2` and `10.255.0.3`. Read with the `kp` wrapper, never printed: the script pipes the password over stdin to the SMC, so
it never appears in a command line, process list or transcript. Verified on all 11 switches at six sites, both Teleport clusters (2026-09-30). Whether the same password holds at other sites is unknown
until each is tried; the script allows one password attempt per run (`NumberOfPasswordPrompts=1`) so a wrong entry cannot build up failures against a lockout. Override the entry with
`TPLINK_KP_ENTRY`, and name a separate enable password with `TPLINK_KP_ENABLE_ENTRY`.

## Access path and SSH quirks

Workstation -> `tsh ssh --proxy=<cluster> root@<site>-smc01` -> `ssh admin@<switch>` from the SMC. Found on SG2428P firmware 5.30.1 Build 20240202 (SSH server `TPSSH-1.0.0`):

| Quirk           | Symptom without the fix                                                                                                | Fix                                       |
| --------------- | ---------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| MAC list        | `Unable to negotiate ... no matching MAC found. Their offer: hmac-sha1-160,hmac-sha2-256,hmac-sha2-512,hmac-ripemd160` | `-o MACs=hmac-sha2-256`                   |
| Host key        | Session closes straight after `SSH2_MSG_SERVICE_ACCEPT`, before any auth method is offered                             | `-o HostKeyAlgorithms=+ssh-rsa`           |
| Pubkey          | Root's key is offered first (`sign_and_send_pubkey: no mutual signature supported`) and the switch drops the session   | `-o PubkeyAuthentication=no`              |
| No exec channel | `ssh switch "show ..."` and a piped stdin both log in and close at once (`ssh_tty_make_modes: no fd or tio`)           | A real pty: the driver uses `pty.fork()`  |
| Enter           | LF does nothing; commands run together (`show system-infoexit`)                                                        | Send CR (`\r`)                            |
| First keystroke | The first command after login is swallowed                                                                             | Send a blank CR first                     |
| Banner order    | The server sends its version banner only after the client's                                                            | Send `SSH-2.0-...\r\n` first when probing |

Kex and cipher are not an issue: `diffie-hellman-group16-sha512` and `aes128-ctr` negotiate by default. Telnet (tcp/23) is refused; HTTPS (tcp/443) is open for the web UI, reachable with
`scripts/teleport-tunnel.sh <site> <switch_ip> <port> 443`. Plain HTTP on 80 gave no answer.

## Privilege: enable with and without a password

After login the prompt is `>` (for example `Switch1>`), and `show system-info` returns `Error: Bad command` there, so `enable` comes first. Three cases, handled by the driver and reported on stderr as
`privilege: ...`:

- `enable-no-password`: `enable` goes straight to `#`. Both kalumburu switches.
- `enable-password`: `enable` asks for a password. The driver sends the `TPLINK_KP_ENABLE_ENTRY` password, or the login password when none is set; one attempt only, exit 6 on failure. Not yet seen
  live.
- `already-privileged`: the login lands on `#`, so no `enable` is sent. Not yet seen live.

The driver also answers an in-CLI `User:`/`Username:` prompt, in case a firmware asks for a CLI login after SSH. Not yet seen live.

## Discovery: why ARP is not enough

The SMC's ARP table cannot be used as the host list. Once a table holds more than `gc_thresh1` entries, the kernel purges any entry unused for
`gc_stale_time` (60 s); the SMCs hold 169-795 entries, above both their `gc_thresh1` of 1 and the kernel default of 128, and the switches rarely talk to the SMC, so they vanish between runs
(`13_known-issues.md`, neighbour table 2026-09-24). `--discover` therefore runs `fping -a` over the management subnet only (routes on `bridge_500` or in `10.255.x`) and probes each
live host's SSH banner for `TPSSH` (about 30 s at kalumburu's /19).

**Never sweep the client bridges.** A first version swept every connected `10.x` route, which included `bridge_501`, a /18 of public Wi-Fi clients: it pinged customer devices, took 4.5 minutes, and
flooded the neighbour table with thousands of `INCOMPLETE` entries. Without `fping` the script falls back to ARP and warns that quiet switches can be missed.

## Config capture

`scripts/tplink-switch.sh <site> <ip> --backup <dir>` runs `show system-info` and `show running-config`, redacts every `password`/`secret`/`community`/`key`/`passphrase`/`psk` value, refuses to write
if the known login or enable password survives, and writes `<dir>/<site>/<system-name>_<ip>_<YYYYMMDD_hhmm>.cfg` with the system-info as a `!` comment header. The paging prompt (`Press any key to
continue`) is answered automatically. Unified-network-controller keeps these as durable, git-tracked samples under `captures/tplink-switch-configs/` (operator, 2026-09-24): capture each switch's
config as each site is visited. The trap host's community name is redacted with the community line (2026-09-30).

## SNMP

Every switch has one v2c community, **read-write**, on the default view `viewDefault`, and one trap host, the SMC (`snmp-server host 10.255.0.1 162 "<community>" smode v2c`). The community is `SNMP-`
followed by the switch's `location` string (`show system-info` "System Location", sysLocation), typed by hand per site, so its case varies (`HopeVale`, `BURRINGURRAH`). Checked on six switches at six
sites (2026-09-30) by comparing in memory, never printed, then confirmed on all 11 by an SNMP read ([survey](tplink-snmp-enablement-survey-20260930.csv)). It is in no vault entry: not
`cambium-devices/*-snmp-*`, not the login password, not `public`/`private`. Two consequences:

- It is guessable from the site name and grants write. Changing it, and whether it goes into the vault, is the operator's decision.
- The trap host line carries it in the clear. `--backup` redacted only `snmp-server community` until 2026-09-30, so the 2026-09-24 kalumburu captures
  held it (committed in unified-network-controller `3b54e4c`); since then the trap host name is redacted too and every community value found is
  leak-checked before a file is written.

Query from the SMC, as for any device behind it (UNC `smc_snmp`), with `-t 5 -r 3`: the agent is slow after a large walk, and the default `-t 2 -r 1`
turned half the subtrees into timeouts that looked like missing MIBs. Which OIDs the project uses, and which are absent, is in
[snmp-oid-registry-tplink.yaml](snmp-oid-registry-tplink.yaml); one record per switch is in [tplink-site-switches.yaml](tplink-site-switches.yaml).

## In Nautobot

Unified-network-controller carries the model in its catalog (`vendors/tp-link/`: manufacturer TP-Link, device type SG2428P with its 28 ports named as ifName reports them, platform `TP-Link Omada
switch`, role `Switch`) and seeds a switch from its redacted capture with `wc-local/scripts/seed_switch_devices.py`: name `<site>-<sysName>`, Staged, serial, firmware, management VLAN interface with
its address as primary. Since 2026-09-30 switches are onboarded through UNC's sweep, identify and land stages like Cambium units: the sweep reads each pinged non-Cambium host's SSH banner from the SMC
(this script's `--discover` probe) and a `TPSSH` banner marks it a switch; identify runs `--backup` once per switch; land knows a switch by the base MAC on its management-only VLAN interface. Canary
on 2026-09-30, all Staged: nbn_accelerate `hope-vale-Switch1`, `kowanyama-Switch1`, `pukatja-Switch1`; rcp `bidyadanga-Switch1`, `burringurrah-Switch2`, `kalumburu-Switch1`. The management mask is per
site (37 sites /19, six /22 in topology_vars, 2026-09-30): the address takes its site's Prefix, which must equal topology_vars, and a switch configured otherwise (kalumburu and kowanyama Switch1, /22
on /19 sites) keeps the site's mask in Nautobot with the difference noted as drift.

## VLANs: parsing and drift against topology_vars

No FOSS project parses this config (unified-network-controller research, 2026-09-30). netutils' `linux` config parser nests it correctly (the Cisco
IOS parser fails on the bare `#` lines), and `netutils.vlan.vlanconfig_to_list` expands `500-501,503` and `vlan 621-626` ranges; UNC's
`seed_switch_devices.parse_config` maps the result. Ports run in general mode: tagged members, untagged members and a PVID; a port starts untagged in
VLAN 1 until `no switchport general allowed vlan 1`. A PVID outside a port's untagged members is a fault to report (bidyadanga 1/0/17 and 1/0/18:
untagged 623/624, PVID 621/622, both shut down).

topology_vars assigns VLANs per SMC port (`switch01`, `switch02`), so the switch that is `switch01` is found by exact MAC: an SMC port's MAC, or one
of its VLAN interfaces' own MACs, in the switch's MAC table (dot1qTpFdbPort). Drift found on 2026-09-30: hope-vale Switch1 defines 503, 522, 524,
526, 528 and trunks 521-528 to the SMC where topology_vars splits odd and even internets between two switches; bidyadanga Switch1 (`switch01`, SMC
enp2s0 on 1/0/1) defines 522, 524-528 and 622-626 beyond topology_vars.

## Kalumburu as found (2026-09-24)

|             | 10.255.0.2                                                 | 10.255.0.3        |
| ----------- | ---------------------------------------------------------- | ----------------- |
| System name | Switch1                                                    | Switch 2          |
| Model       | SG2428P 5.30 (Omada 28-port Gigabit Smart Switch, 24 PoE+) | SG2428P 5.30      |
| Firmware    | 5.30.1 Build 20240202 Rel.61907                            | same              |
| Serial      | 22480S0000948                                              | 22480S0000014     |
| MAC         | B0-19-21-EA-92-3B                                          | B0-19-21-EA-8E-95 |

Switch1's VLANs: 1 System-VLAN, 500 Management, 501 Public Wifi, 502 R195 Prov, 503 Private Wifi, 521-528 Internet 1-8 (each on its own access port, Gi1/0/9-16, and tagged on the Gi1/0/1 uplink).
Ports 25-28 are SFP, all down.

## Bidyadanga as found (2026-09-30)

`--discover` found one TPSSH host, 10.255.0.2; the sweep's 10.255.0.3-4 TP-Link OUIs did not answer as switches. Login with the same KeePass entry, `enable` with no password. Switch1, location
`Bidyadanga`, SG2428P 5.30, firmware 5.30.5 Build 20250117 Rel.60446 (newer than kalumburu's 5.30.1; the driver's quirk handling still worked), serial 225605X001920, MAC 8C-86-DD-33-A5-0F, up 232
days.

## Pitfalls

- On 2026-09-24 the login password was sent after an `enable` that asked for none; the CLI took it as a command (`Error: Event not found`), so it may sit in Switch1's CLI history. Never send a
  password unless a password prompt is on screen; the driver waits for one.
- Stale host keys: every connection uses `UserKnownHostsFile=/dev/null`, because multi-SMC sites and swapped units change keys (`01_overview.md`).
- Writes: the script is read-only by default (`show`, `ping`, `tracert` only). `--write` sends config commands to a production switch and needs the operator's explicit go-ahead.
